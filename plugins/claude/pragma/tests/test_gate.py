#!/usr/bin/env python3
"""Deterministic tests for the pragma review gate.

Usage: python3 -B -I plugins/claude/pragma/tests/test_gate.py [-v]

Each test runs the real hook script against fictitious transcripts in a
temporary directory, with a fake reviewer (fake_claude.py) in place of
`claude -p`, so no model is called. Covered: budgets per request and per
moment, concurrency, cache, isolation between sessions and from subagents,
reviewer failures and timeouts, invalid replies, malformed input, the
reviewer's isolation flags, non-recursion, cleanup, retention, the
evidence package itself, narration, and the text shown on screen that the
transcript does not hold yet when a question is reviewed.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
HOOK = PLUGIN / "gate" / "hook.py"
FAKE = Path(__file__).resolve().parent / "fake_claude.py"
sys.path.insert(0, str(PLUGIN))

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fixture import Transcript  # noqa: E402
from gate import display, evaluator, evidence, state, transcript  # noqa: E402


class GateCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="pragma-gate-test-"))
        self.state_dir = self.tmp / "state"
        self.fake_log = self.tmp / "fake"
        self.fake_log.mkdir()
        self.config = self.tmp / "gate.json"
        self.write_config({"timeout_s": 5, "lock_wait_s": 20})
        self.plan([{"verdict": "pass"}])
        wrapper = self.tmp / "claude"
        wrapper.write_text(f"#!/bin/sh\nexec {sys.executable} -I {FAKE} \"$@\"\n")
        wrapper.chmod(0o755)
        self.wrapper = wrapper
        self.tr = Transcript(self.tmp / "session.jsonl")
        self.session = "sess-1"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write_config(self, cfg):
        self.config.write_text(json.dumps(cfg))

    def plan(self, steps):
        (self.tmp / "plan.json").write_text(json.dumps(steps))

    def env(self, **extra):
        env = {k: v for k, v in os.environ.items()
               if not k.startswith("PRAGMA_GATE") and k not in ("CLAUDE_PROJECT_DIR",)}
        env.update({"PRAGMA_GATE_STATE_DIR": str(self.state_dir), "PRAGMA_GATE_CONFIG": str(self.config),
                    "PRAGMA_GATE_CLAUDE_BIN": str(self.wrapper), "FAKE_PLAN": str(self.tmp / "plan.json"),
                    "FAKE_LOG": str(self.fake_log), "CLAUDE_PROJECT_DIR": str(self.tmp / "project"),
                    "CLAUDE_CODE_SESSION_ID": "parent-session"})
        env.update(extra)
        return env

    def hook(self, event, payload, timeout=60, **env):
        proc = subprocess.run([sys.executable, "-B", "-I", str(HOOK), event], input=json.dumps(payload)
                              if not isinstance(payload, str) else payload, capture_output=True, text=True,
                              env=self.env(**env), timeout=timeout)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out = proc.stdout.strip()
        return json.loads(out) if out else None

    def base(self, prompt_id, session=None):
        return {"session_id": session or self.session, "transcript_path": str(self.tr.path),
                "cwd": str(self.tmp), "prompt_id": prompt_id}

    def submit(self, text, prompt_id, session=None):
        self.hook("user-prompt-submit", dict(self.base(prompt_id, session), hook_event_name="UserPromptSubmit",
                                             prompt=text))
        self.tr.user(text, prompt_id)

    def stop(self, prompt_id, final, session=None, **kw):
        self.tr.assistant(final)
        payload = dict(self.base(prompt_id, session), hook_event_name="Stop", stop_hook_active=False,
                       last_assistant_message=final, background_tasks=[])
        payload.update(kw)
        return self.hook("stop", payload)

    def ask(self, prompt_id, question, session=None, agent_id=None, tool_name="AskUserQuestion"):
        payload = dict(self.base(prompt_id, session), hook_event_name="PreToolUse", tool_name=tool_name,
                       tool_use_id="toolu_q", agent_id=agent_id,
                       tool_input={"questions": [{"question": question, "header": "Q",
                                                  "options": [{"label": "A", "description": "a"},
                                                              {"label": "B", "description": "b"}],
                                                  "multiSelect": False}]})
        return self.hook("pre-tool-use", payload)

    def answer(self, prompt_id, n, question, choice):
        self.tr.answer(prompt_id, n, question, choice)

    def display(self, prompt_id, delta, message_id="m1", index=0, final=True, session=None, **kw):
        """One MessageDisplay batch, as Claude Code sends it while a message is shown."""
        payload = dict(self.base(prompt_id, session), hook_event_name="MessageDisplay", turn_id="turn-1",
                       message_id=message_id, index=index, final=final, delta=delta)
        payload.update(kw)
        return self.hook("message-display", payload)

    def shown(self, session=None):
        path = self.state_dir / "sessions" / (session or self.session) / "shown.json"
        return json.loads(path.read_text()) if path.exists() else None

    def package(self, n=-1):
        return json.loads((self.fake_log / f"package-{self.calls()[n]['n']}.json").read_text())

    def calls(self):
        return sorted((json.loads(p.read_text()) for p in self.fake_log.glob("call-*.json")), key=lambda c: c["n"])

    def log(self, session=None):
        path = self.state_dir / "sessions" / (session or self.session) / "log.jsonl"
        return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


class Budgets(GateCase):
    def test_regression_two_questions_then_stop_return_and_resolution(self):
        """The case that motivated separate budgets."""
        self.submit("Crie o relatório e rode os testes.", "p1")
        self.plan([{"verdict": "pass"}, {"verdict": "pass"},
                   {"verdict": "revise", "category": "missing_verification"}, {"verdict": "pass"}])
        self.assertIsNone(self.ask("p1", "Formato do relatório?"))
        self.answer("p1", 1, "Formato do relatório?", "Markdown")
        self.assertIsNone(self.ask("p1", "Incluir gráficos?"))
        self.answer("p1", 2, "Incluir gráficos?", "Não")
        out = self.stop("p1", "Relatório criado. Quer que eu rode os testes?")
        self.assertEqual(out["decision"], "block")
        self.assertIn("missing_verification", out["reason"])
        self.tr.stop_feedback(out["reason"], "p1")
        self.tr.tool("toolu_t1", "Bash", {"command": "make test"}, "12 passed", "p1")
        self.assertIsNone(self.stop("p1", "Relatório criado; make test: 12 passed."))
        self.assertEqual(len(self.calls()), 4)
        st = json.loads((self.state_dir / "sessions" / "sess-1" / "state.json").read_text())
        budgets = st["requests"]["p1"]["budgets"]
        self.assertEqual(budgets["question"], {"evaluations": 2, "returns": 0})
        self.assertEqual(budgets["stop"], {"evaluations": 2, "returns": 1})

    def test_two_stop_returns_leave_a_third_evaluation(self):
        self.submit("Faça a tarefa.", "p1")
        self.plan([{"verdict": "revise"}, {"verdict": "revise"}, {"verdict": "pass"}])
        self.assertEqual(self.stop("p1", "parcial 1")["decision"], "block")
        self.assertEqual(self.stop("p1", "parcial 2")["decision"], "block")
        self.assertIsNone(self.stop("p1", "feito"))
        self.assertEqual([r["outcome"] for r in self.log()], ["returned", "returned", "pass"])

    def test_third_revise_is_released_with_one_diagnostic_and_no_approval(self):
        self.submit("Faça a tarefa.", "p1")
        self.plan([{"verdict": "revise"}])
        self.stop("p1", "a")
        self.stop("p1", "b")
        out = self.stop("p1", "c")
        self.assertNotIn("decision", out)
        self.assertIn("correction budget", out["systemMessage"])
        out4 = self.stop("p1", "d")
        self.assertIsNone(out4)  # diagnostic only once per request
        outcomes = [r["outcome"] for r in self.log()]
        self.assertEqual(outcomes, ["returned", "returned", "returns_exhausted", "evaluations_exhausted"])
        self.assertNotIn("pass", outcomes)
        self.assertEqual(len(self.calls()), 3)

    def test_budgets_are_independent(self):
        self.submit("Decida comigo.", "p1")
        for n in range(3):
            self.assertIsNone(self.ask("p1", f"pergunta {n}?"))
        out = self.ask("p1", "pergunta 3?")
        self.assertIn("evaluation budget", out["systemMessage"])
        self.assertEqual(len(self.calls()), 3)
        self.assertIsNone(self.stop("p1", "pronto"))
        self.assertEqual(len(self.calls()), 4)  # the stop budget was untouched

    def test_exhausting_stop_leaves_question_counter_alone(self):
        self.submit("Faça.", "p1")
        self.plan([{"verdict": "revise"}, {"verdict": "revise"}, {"verdict": "revise"}, {"verdict": "pass"}])
        for final in ("a", "b", "c", "d"):
            self.stop("p1", final)
        self.assertIsNone(self.ask("p1", "nova decisão?"))
        st = json.loads((self.state_dir / "sessions" / "sess-1" / "state.json").read_text())
        self.assertEqual(st["requests"]["p1"]["budgets"]["question"], {"evaluations": 1, "returns": 0})

    def test_answers_tools_and_continuations_do_not_reset(self):
        self.submit("Faça.", "p1")
        self.plan([{"verdict": "revise"}])
        self.stop("p1", "a")
        self.answer("p1", 1, "x?", "y")
        self.tr.tool("toolu_b", "Bash", {"command": "ls"}, "ok", "p1")
        self.stop("p1", "b", stop_hook_active=True)
        self.stop("p1", "c", stop_hook_active=True)
        self.assertEqual(self.log()[-1]["outcome"], "returns_exhausted")

    def test_new_request_starts_new_budgets(self):
        self.submit("Primeiro.", "p1")
        self.plan([{"verdict": "revise"}])
        for final in ("a", "b", "c", "d"):
            self.stop("p1", final)
        self.submit("Segundo.", "p2")
        out = self.stop("p2", "e")
        self.assertEqual(out["decision"], "block")
        self.assertEqual(self.log()[-1]["evaluations"], 1)

    def test_failures_consume_attempts(self):
        self.submit("Faça.", "p1")
        self.plan([{"exit": 1}])
        out = self.stop("p1", "a")
        self.assertIn("unavailable", out["systemMessage"])
        self.assertIsNone(self.stop("p1", "b"))
        self.assertIsNone(self.stop("p1", "c"))
        self.assertIsNone(self.stop("p1", "d"))
        self.assertEqual(len(self.calls()), 3)
        self.assertEqual([r["outcome"] for r in self.log()], ["error", "error", "error", "evaluations_exhausted"])


class Cache(GateCase):
    def test_identical_input_reuses_verdict(self):
        self.submit("Faça.", "p1")
        payload = dict(self.base("p1"), hook_event_name="Stop", last_assistant_message="feito", background_tasks=[])
        self.tr.assistant("feito")
        self.assertIsNone(self.hook("stop", payload))
        self.assertIsNone(self.hook("stop", payload))
        self.assertEqual(len(self.calls()), 1)
        self.assertEqual([r["cache"] for r in self.log()], [False, True])

    def test_changed_evidence_needs_new_evaluation(self):
        self.submit("Faça.", "p1")
        payload = dict(self.base("p1"), hook_event_name="Stop", last_assistant_message="feito", background_tasks=[])
        self.tr.assistant("feito")
        self.hook("stop", payload)
        self.tr.tool("toolu_x", "Bash", {"command": "pytest"}, "1 failed", "p1", is_error=True)
        self.hook("stop", payload)  # same final text, different evidence
        self.assertEqual(len(self.calls()), 2)


class Failures(GateCase):
    def test_timeout_kills_reviewer_and_releases(self):
        self.write_config({"timeout_s": 1})
        self.plan([{"sleep": 30}])
        self.submit("Faça.", "p1")
        started = time.monotonic()
        out = self.stop("p1", "feito")
        self.assertLess(time.monotonic() - started, 10)
        self.assertIn("unavailable", out["systemMessage"])
        call = self.calls()[0]
        self.assertNotIn("end", call)
        with self.assertRaises(ProcessLookupError):
            os.kill(call["pid"], 0)
        self.assertEqual(self.log()[-1]["outcome"], "timeout")

    def test_non_json_reply_is_invalid(self):
        self.plan([{"raw": "not json"}])
        self.submit("Faça.", "p1")
        out = self.stop("p1", "feito")
        self.assertIn("inconclusive", out["systemMessage"])
        self.assertEqual(self.log()[-1]["outcome"], "invalid")

    def test_reference_absent_from_package_is_invalid(self):
        self.plan([{"verdict": "revise", "refs": ["U999"]}])
        self.submit("Faça.", "p1")
        out = self.stop("p1", "feito")
        self.assertNotIn("decision", out)
        self.assertIn("absent from the package", out["systemMessage"])

    def test_unknown_verdict_releases_with_diagnostic(self):
        self.plan([{"verdict": "unknown"}])
        self.submit("Faça.", "p1")
        out = self.stop("p1", "feito")
        self.assertIn("inconclusive: missing fake missing item", out["systemMessage"])

    def test_malformed_hook_input(self):
        self.assertIsNone(self.hook("stop", "{not json"))
        self.assertIsNone(self.hook("stop", json.dumps(["no", "session"])))
        self.assertIsNone(self.hook("bogus-event", self.base("p1")))
        self.assertEqual(self.calls(), [])

    def test_request_not_in_the_transcript_yet_skips_the_call(self):
        """A lagging transcript must not get the turn judged against the previous request."""
        self.write_config({"timeout_s": 5, "lock_wait_s": 20, "stop_wait_s": 0.2})
        self.submit("Pedido anterior.", "p0")
        self.tr.assistant("Feito.")
        self.hook("user-prompt-submit", dict(self.base("p1"), hook_event_name="UserPromptSubmit", prompt="Novo."))
        out = self.hook("stop", dict(self.base("p1"), last_assistant_message="pronto", background_tasks=[]))
        self.assertIn("current request is not in the transcript yet", out["systemMessage"])
        self.assertIsNone(self.ask("p1", "Qual?"))  # once per request
        self.assertEqual(self.calls(), [])
        self.assertEqual([r["outcome"] for r in self.log()], ["no_request", "no_request"])

    def test_request_found_through_any_item_of_its_turn(self):
        self.submit("Rode os testes.", "p1")
        self.tr._write({"type": "user", "promptId": "p2", "origin": {"kind": "task-notification"},
                        "message": {"role": "user", "content": "<task-notification>tests done</task-notification>"}})
        self.assertIsNone(self.stop("p2", "Os testes terminaram."))
        self.assertEqual(len(self.calls()), 1)
        self.assertEqual(self.package()["request"]["text"], "Rode os testes.")

    def test_transcript_without_prompt_ids_falls_back_to_the_last_user_message(self):
        self.tr._write({"type": "user", "origin": {"kind": "human"}, "message": {"role": "user", "content": "Faça."}})
        self.assertIsNone(self.stop("p1", "feito"))
        self.assertEqual(len(self.calls()), 1)
        self.assertTrue(any("last user message" in n for n in self.package()["notes"]))

    def test_missing_transcript_skips_the_call(self):
        payload = {"session_id": self.session, "transcript_path": str(self.tmp / "nope.jsonl"),
                   "prompt_id": "p1", "last_assistant_message": "x"}
        out = self.hook("stop", payload)
        self.assertIn("transcript is not available", out["systemMessage"])
        self.assertIsNone(self.hook("stop", payload))  # once per request
        self.assertEqual(self.calls(), [])
        self.assertEqual(self.log()[-1]["outcome"], "no_transcript")


class Isolation(GateCase):
    def test_reviewer_flags_env_and_workdir(self):
        self.submit("Faça.", "p1")
        self.stop("p1", "feito")
        call = self.calls()[0]
        argv = call["argv"]
        for flag in ("-p", "--safe-mode", "--strict-mcp-config", "--no-session-persistence"):
            self.assertIn(flag, argv)
        self.assertEqual(argv[argv.index("--tools") + 1], "")
        self.assertEqual(argv[argv.index("--disallowedTools") + 1], "mcp__*")
        self.assertEqual(argv[argv.index("--output-format") + 1], "json")
        self.assertIn("--json-schema", argv)
        self.assertEqual(argv[argv.index("--model") + 1], "claude-test-model")  # the session's model
        self.assertEqual(argv[argv.index("--effort") + 1], "low")
        self.assertEqual(call["env"]["PRAGMA_GATE_EVALUATOR"], "1")
        self.assertIsNone(call["env"]["CLAUDE_PROJECT_DIR"])
        self.assertIsNone(call["env"]["CLAUDE_CODE_SESSION_ID"])
        self.assertTrue(call["cwd"].startswith(str(self.state_dir / "evalbox")))
        self.assertFalse(Path(call["cwd"]).exists())
        self.assertEqual(list((self.state_dir / "evalbox").iterdir()), [])

    def test_configured_model_wins(self):
        self.write_config({"model": "claude-other", "effort": "medium"})
        self.submit("Faça.", "p1")
        self.stop("p1", "feito")
        argv = self.calls()[0]["argv"]
        self.assertEqual(argv[argv.index("--model") + 1], "claude-other")
        self.assertEqual(argv[argv.index("--effort") + 1], "medium")

    def test_no_recursion_inside_reviewer(self):
        self.submit("Faça.", "p1")
        out = self.hook("stop", dict(self.base("p1"), last_assistant_message="x"), PRAGMA_GATE_EVALUATOR="1")
        self.assertIsNone(out)
        self.assertEqual(self.calls(), [])

    def test_sessions_do_not_share_counters(self):
        self.plan([{"verdict": "revise"}])
        self.submit("Faça.", "p1", session="sess-A")
        self.submit("Faça.", "p1", session="sess-B")
        self.stop("p1", "a", session="sess-A")
        self.stop("p1", "b", session="sess-A")
        self.assertEqual(self.stop("p1", "c", session="sess-B")["decision"], "block")
        self.assertEqual(self.log("sess-B")[-1]["returns"], 1)

    def test_subagents_and_other_tools_are_skipped(self):
        self.submit("Faça.", "p1")
        self.assertIsNone(self.ask("p1", "q?", agent_id="agent-7"))
        self.assertIsNone(self.ask("p1", "q?", tool_name="Bash"))
        self.assertEqual(self.calls(), [])

    def test_disabled_by_config_or_env(self):
        self.submit("Faça.", "p1")
        self.write_config({"enabled": False})
        self.assertIsNone(self.stop("p1", "a"))
        self.write_config({})
        self.assertIsNone(self.hook("stop", dict(self.base("p1"), last_assistant_message="a"), PRAGMA_GATE="off"))
        self.assertEqual(self.calls(), [])


class Concurrency(GateCase):
    def test_one_evaluation_at_a_time_per_session(self):
        self.plan([{"verdict": "pass", "sleep": 1.0}])
        self.submit("Faça.", "p1")
        self.tr.assistant("feito")
        payloads = [dict(self.base("p1"), last_assistant_message=f"feito {n}", background_tasks=[]) for n in range(3)]
        errors = []

        def run(p):
            try:
                self.hook("stop", p)
            except Exception as exc:  # surfaced below
                errors.append(exc)

        threads = [threading.Thread(target=run, args=(p,)) for p in payloads]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(errors, [])
        spans = sorted((c["start"], c["end"]) for c in self.calls())
        self.assertEqual(len(spans), 3)
        for (_, end), (start, _) in zip(spans, spans[1:]):
            self.assertLessEqual(end, start + 0.05)
        self.assertEqual(self.log()[-1]["evaluations"], 3)

    def test_lock_timeout_releases_without_evaluating(self):
        self.write_config({"lock_wait_s": 0.5})
        self.submit("Faça.", "p1")
        sdir = state.session_dir(self.state_dir, self.session)
        with state.locked(sdir, 1) as got:
            self.assertTrue(got)
            out = self.stop("p1", "feito")
        self.assertIn("still running", out["systemMessage"])
        self.assertEqual(self.calls(), [])


class Retention(GateCase):
    def test_prune_removes_old_sessions_only(self):
        old = state.session_dir(self.state_dir, "old")
        (old / "state.json").write_text("{}")
        past = time.time() - 30 * 86400
        os.utime(old / "state.json", (past, past))
        os.utime(old / "lock", (past, past)) if (old / "lock").exists() else None
        os.utime(old, (past, past))
        new = state.session_dir(self.state_dir, "new")
        (new / "state.json").write_text("{}")
        self.hook("session-start", {"session_id": "new", "source": "startup"})
        self.assertFalse(old.exists())
        self.assertTrue(new.exists())


class Package(GateCase):
    def build(self, event="stop", prompt_id="p1", limit=64 * 1024, **extras):
        idx = transcript.update_index(self.tmp / "index.json", str(self.tr.path))
        with transcript.Loader(idx["path"]) as loader:
            return evidence.build(event, idx["items"], loader, prompt_id, extras, limit)

    def test_kinds_and_exclusions(self):
        self.tr.user("Primeiro pedido", "p0")
        self.tr.reasoning()
        self.tr.assistant("Resposta antiga")
        self.tr.user("Pedido atual", "p1")
        self.answer("p1", 1, "Formato?", "JSON")
        self.tr.stop_feedback("pragma stop review: algo", "p1")
        self.tr._write({"type": "user", "isMeta": True, "message": {"content": "skill text"}})
        self.tr._write({"type": "assistant", "isSidechain": True,
                        "message": {"content": [{"type": "text", "text": "SUBAGENTE"}]}})
        pkg, refs, _ = self.build(final_response="fim")
        dump = json.dumps(pkg, ensure_ascii=False)
        self.assertNotIn("SUBAGENTE", dump)
        self.assertNotIn("skill text", dump)
        self.assertEqual(pkg["request"]["text"], "Pedido atual")
        kinds = [i["kind"] for i in pkg["turn"]]
        self.assertIn("hook_feedback", kinds)
        self.assertEqual([i["kind"] for i in pkg["history"]], ["user", "assistant"])
        answer = next(i for i in pkg["turn"] if i["kind"] == "tool")
        self.assertIn("JSON", answer["result"]["text"])
        self.assertIn(answer["result"]["ref"], refs)

    def test_narration_is_assistant_text_marked_summarized(self):
        self.tr.user("Pedido antigo", "p0")
        self.tr.narration("Resumo antigo: o primeiro arquivo está certo.")
        self.tr.user("Pedido atual", "p1")
        self.tr.reasoning(display="updates")
        self.tr.narration("Resumo: li os dois arquivos, e o segundo tem o erro.", display="updates")
        pkg, refs, _ = self.build(final_response="fim")
        self.assertEqual(len(pkg["turn"]), 1)  # the reasoning block adds nothing
        item = pkg["turn"][0]
        self.assertEqual((item["kind"], item["summarized"]), ("assistant", True))
        self.assertIn("o segundo tem o erro", item["text"])
        self.assertTrue(item["ref"].startswith("G"))
        self.assertIn(item["ref"], refs)
        self.assertEqual([(i["kind"], i.get("summarized")) for i in pkg["history"]],
                         [("user", None), ("assistant", True)])

    def test_attached_files_and_harness_context(self):
        self.tr.context("Git user: someone\nCurrent branch: main", email="private@example.com")
        self.tr.user("Leia @spec.md e implemente", "p1")
        self.tr.attach_file("spec.md", "ESPECIFICACAO: faça X e Y")
        self.tr.assistant("Feito.")
        pkg, refs, _ = self.build(final_response="Feito.")
        files = pkg["request"]["attached_files"]
        self.assertEqual(files[0]["file"], "spec.md")
        self.assertIn("ESPECIFICACAO", files[0]["text"])
        self.assertIn(files[0]["ref"], refs)
        self.assertIn("Git user: someone", pkg["context"][0]["text"])
        self.assertIn(pkg["context"][0]["ref"], refs)
        self.assertNotIn("private@example.com", json.dumps(pkg))

    def test_refused_question_is_not_an_answer(self):
        self.tr.user("Pedido", "p1")
        self.tr.refused_question("p1", 1, [{"question": "x?"}], "pragma question review: já respondido")
        self.answer("p1", 2, "y?", "sim")
        idx = transcript.update_index(self.tmp / "index.json", str(self.tr.path))
        self.assertEqual([i["kind"] for i in idx["items"]], ["U", "T", "R", "T", "N"])

    def test_size_limit_records_omissions_and_keeps_tails(self):
        self.tr.user("Pedido", "p1")
        for n in range(80):
            self.tr.tool(f"toolu_{n}", "Bash", {"command": f"step {n}"}, "x" * 5000 + f" EXIT STATUS {n}", "p1")
        pkg, refs, stats = self.build(final_response="fim")
        self.assertLessEqual(stats["bytes"], 64 * 1024)
        self.assertGreater(stats["omitted"], 0)
        turn_omit = next(o for o in pkg["omitted"] if o["section"] == "turn")
        self.assertEqual(turn_omit["reason"], "package size limit")
        newest = pkg["turn"][-1]
        self.assertIn("EXIT STATUS 79", newest["result"]["text"])
        self.assertIn("characters cut here", newest["result"]["text"])
        self.assertEqual(pkg["request"]["ref"] in refs, True)

    def test_final_response_not_duplicated(self):
        self.tr.user("Pedido", "p1")
        self.tr.tool("toolu_1", "Bash", {"command": "ls"}, "a b", "p1")
        self.tr.assistant("Pronto: a e b.")
        pkg, refs, _ = self.build(final_response="Pronto: a e b.")
        self.assertEqual(pkg["turn"][-1]["kind"], "tool")
        self.assertEqual(len(pkg["final_response"]["same_as"]), 1)
        self.assertIn(pkg["final_response"]["same_as"][0], refs)

    def test_request_located_by_prompt_id(self):
        self.tr.user("um", "p1")
        self.tr.user("dois", "p2")
        pkg, _, _ = self.build(prompt_id="p1", final_response="x")
        self.assertEqual(pkg["request"]["text"], "um")
        pkg, _, _ = self.build(prompt_id="nope", final_response="x")
        self.assertEqual(pkg["request"]["text"], "dois")
        self.assertTrue(any("last user message" in n for n in pkg["notes"]))

    def test_index_is_incremental(self):
        self.tr.user("um", "p1")
        idx = transcript.update_index(self.tmp / "index.json", str(self.tr.path))
        first = idx["parsed_bytes"]
        with open(self.tr.path, "a") as fh:
            fh.write('{"type": "assistant", "message": {"content": [{"type": "text", "text": "parcial"')
        idx = transcript.update_index(self.tmp / "index.json", str(self.tr.path))
        self.assertEqual(idx["parsed_bytes"], first)  # a partial line waits
        with open(self.tr.path, "a") as fh:
            fh.write('}]}}\n')
        idx = transcript.update_index(self.tmp / "index.json", str(self.tr.path))
        self.assertEqual([i["kind"] for i in idx["items"]], ["U", "A"])
        stored = (self.tmp / "index.json").read_text()
        self.assertNotIn("parcial", stored)  # references only, no text


class Display(GateCase):
    """Text shown on screen before the transcript holds it."""

    REQUEST = "Explique as duas opções de migração e depois me pergunte qual eu prefiro."

    def setUp(self):
        super().setUp()
        self.write_config({"timeout_s": 5, "lock_wait_s": 20, "display_wait_s": 0.5})

    def base_turn(self):
        self.submit(self.REQUEST, "p1")
        self.tr.tool("toolu_r", "Read", {"file_path": "docs/migration.md"}, "## in-place\n## blue-green", "p1")

    def shown_items(self, pkg):
        return [i for i in pkg["turn"] if i["ref"].startswith("D")]

    def test_explanation_shown_with_the_question_reaches_the_package(self):
        """The measured case: neither the explanation nor the question is in the transcript yet."""
        self.base_turn()
        self.display("p1", "In-place: para a aplicação por 20 minutos.\n", index=0, final=False)
        self.display("p1", "Blue-green: quase sem parada, mas o dobro de disco.", index=1, final=True)
        self.assertIsNone(self.ask("p1", "Qual opção você prefere?"))
        pkg = self.package()
        items = self.shown_items(pkg)
        self.assertEqual([(i["ref"], i["kind"]) for i in items], [("D1", "assistant")])
        self.assertIn("In-place: para a aplicação", items[0]["text"])
        self.assertIn("Blue-green: quase sem parada", items[0]["text"])
        self.assertEqual(pkg["turn"][-1]["ref"], "D1")  # the newest of the turn
        self.assertEqual(pkg["notes"], [])
        record = self.log()[-1]["display"]
        self.assertEqual((record["gap"], record["shown"]), (True, 1))

    def test_missing_explanation_is_still_returned(self):
        self.base_turn()
        self.display("p1", "Li o documento de migração.")
        self.plan([{"verdict": "revise", "category": "missing_explanation"}])
        out = self.ask("p1", "Com base na explicação acima, qual opção você prefere?")
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertIn("missing_explanation", out["hookSpecificOutput"]["permissionDecisionReason"])
        pkg = self.package()
        self.assertEqual([i["text"] for i in self.shown_items(pkg)], ["Li o documento de migração."])
        self.assertEqual(pkg["notes"], [])  # nothing in the package excuses the missing explanation

    def test_question_without_text_on_an_installation_that_captures(self):
        self.display("p0", "texto de outra sessão", session="other")
        self.base_turn()
        self.ask("p1", "Qual opção você prefere?")
        pkg = self.package()
        self.assertEqual(self.shown_items(pkg), [])
        self.assertEqual(pkg["notes"], [])

    def test_waits_for_the_last_batch(self):
        self.write_config({"timeout_s": 5, "lock_wait_s": 20, "display_wait_s": 5})
        self.base_turn()
        self.display("p1", "Primeira parte da explicação.\n", final=False)
        thread = threading.Thread(target=self.ask, args=("p1", "Qual opção você prefere?"))
        thread.start()
        time.sleep(0.4)
        self.display("p1", "Última parte, com a recomendação.", index=1, final=True)
        thread.join()
        pkg = self.package()
        text = self.shown_items(pkg)[0]["text"]
        self.assertIn("Primeira parte", text)
        self.assertIn("com a recomendação", text)
        self.assertEqual(pkg["notes"], [])
        waited = self.log()[-1]["display"]["waited_ms"]
        self.assertGreater(waited, 150)
        self.assertLess(waited, 4000)  # ended by the last batch, not by the limit

    def test_unfinished_text_is_declared(self):
        self.base_turn()
        self.display("p1", "Começo da explicação\n", final=False)
        self.ask("p1", "Qual opção você prefere?")
        pkg = self.package()
        self.assertEqual(len(self.shown_items(pkg)), 1)
        self.assertEqual(pkg["notes"], [display.INCOMPLETE])

    def test_gap_without_capture_is_declared(self):
        self.base_turn()
        self.ask("p1", "Qual opção você prefere?")
        pkg = self.package()
        self.assertEqual(pkg["notes"], [display.NOT_CAPTURED])
        self.assertEqual(self.log()[-1]["display"], {"gap": True, "waited_ms": 0, "shown": 0})

    def test_narration_session_declares_that_shown_text_may_be_missing(self):
        """The first refusal measured: the answers went into narration the transcript does not hold yet."""
        self.display("p0", "texto de outra sessão", session="other")  # this installation delivers MessageDisplay
        self.submit(self.REQUEST, "p1")
        self.tr.narration("Vou ler o documento de migração.")
        self.tr.tool("toolu_r", "Read", {"file_path": "docs/migration.md"}, "## in-place\n## blue-green", "p1")
        self.answer("p1", 1, "Qual opção?", "Antes: dá para migrar sem parar? Quanto disco? Por que não blue-green?")
        self.ask("p1", "Com isso respondido, qual opção você prefere?")
        pkg = self.package()
        self.assertEqual(self.shown_items(pkg), [])
        self.assertEqual(pkg["notes"], [display.NARRATION_MISSING])

    def test_narration_of_the_question_message_reaches_the_package(self):
        """The second refusal measured: the narration is written, the call is not yet."""
        self.display("p0", "texto de outra sessão", session="other")
        self.base_turn()
        self.tr.reasoning(display="updates")
        self.tr.narration("In-place para 20 minutos; blue-green quase não para, mas usa o dobro de disco.",
                          display="updates")
        self.ask("p1", "Qual opção você prefere?")
        pkg = self.package()
        item = pkg["turn"][-1]
        self.assertEqual((item["kind"], item.get("summarized")), ("assistant", True))
        self.assertIn("blue-green quase não para", item["text"])
        self.assertEqual(pkg["notes"], [display.NARRATION_MISSING])

    def test_narration_note_needs_a_gap_and_no_other_note(self):
        self.base_turn()
        self.tr.narration("Resumo da explicação.")
        self.ask("p1", "Qual opção você prefere?")
        self.assertEqual(self.package()["notes"], [display.NOT_CAPTURED])  # no MessageDisplay: one note
        self.display("p0", "texto de outra sessão", session="other")
        self.tr._assistant({"type": "tool_use", "id": "toolu_q", "name": "AskUserQuestion", "input": {}})
        self.ask("p1", "Qual opção você prefere?")
        self.assertEqual(self.package()["notes"], [])  # the transcript holds the call: nothing is missing

    def test_transcript_holding_the_question_needs_no_capture(self):
        self.base_turn()
        self.display("p1", "In-place para 20 minutos;   blue-green quase não para.\n")
        self.tr.assistant("In-place para 20 minutos; blue-green quase não para.")
        self.tr._assistant({"type": "tool_use", "id": "toolu_q", "name": "AskUserQuestion", "input": {}})
        self.ask("p1", "Qual opção você prefere?")
        pkg = self.package()
        self.assertEqual(self.shown_items(pkg), [])
        self.assertEqual(self.log()[-1]["display"], {"gap": False, "waited_ms": 0, "shown": 0})
        self.assertIsNone(self.shown())  # the transcript holds it: the copy is gone

    def test_a_new_request_or_session_start_empties_it(self):
        self.display("p1", "texto do pedido 1")
        self.assertIsNotNone(self.shown())
        self.submit("Novo pedido.", "p2")
        self.assertIsNone(self.shown())
        self.display("p2", "texto do pedido 2")
        self.display("p3", "texto de um pedido sem prompt registrado", message_id="m9")
        self.assertEqual([m["id"] for m in self.shown()["messages"]], ["m9"])
        self.hook("session-start", {"session_id": self.session, "source": "resume"})
        self.assertIsNone(self.shown())

    def test_reviews_drop_what_the_transcript_holds(self):
        self.submit("Faça.", "p1")
        self.display("p1", "Vou rodar os testes.", message_id="m1")
        self.display("p1", "Texto que o transcript não tem.", message_id="m2")
        self.tr.tool("toolu_t", "Bash", {"command": "make test"}, "ok", "p1")
        self.tr.assistant("Vou rodar os testes.")
        self.stop("p1", "feito")
        self.assertEqual([m["id"] for m in self.shown()["messages"]], ["m2"])

    def test_capture_is_bounded(self):
        for n in range(10):
            self.display("p1", f"mensagem {n}", message_id=f"m{n}")
        self.assertEqual([m["id"] for m in self.shown()["messages"]], [f"m{n}" for n in range(4, 10)])
        big = "".join(f"{n:05d}\n" for n in range(5000))
        chunks = [big[k:k + 3000] for k in range(0, len(big), 3000)]
        for k, chunk in enumerate(chunks):
            self.display("p1", chunk, message_id="big", index=k, final=k == len(chunks) - 1)
        msgs = self.shown()["messages"]
        self.assertEqual(len(msgs), display.MAX_MESSAGES)
        msg = msgs[-1]
        self.assertEqual(len(msg["head"]) + len(msg["tail"]), display.KEEP_CHARS)
        self.assertEqual(len(msg["head"]) + msg["dropped"] + len(msg["tail"]), len(big))
        self.assertTrue(big.startswith(msg["head"]) and big.endswith(msg["tail"]))
        self.assertEqual(evidence.cut_parts(msg["head"], msg["dropped"], msg["tail"], evidence.CAP_ASSISTANT),
                         evidence.cut(big, evidence.CAP_ASSISTANT))
        size = (self.state_dir / "sessions" / self.session / "shown.json").stat().st_size
        self.assertLess(size, display.MAX_MESSAGES * display.KEEP_CHARS * 1.2)

    def test_capture_skips_subagents_and_a_disabled_gate_and_prints_nothing(self):
        self.assertIsNone(self.display("p1", "texto de subagente", agent_id="agent-1"))
        self.assertIsNone(self.shown())
        self.write_config({"enabled": False})
        self.assertIsNone(self.display("p1", "texto"))
        self.assertIsNone(self.shown())
        self.write_config({})
        self.assertIsNone(self.display("p1", "texto"))  # no displayContent: the screen keeps the original
        self.assertEqual(self.shown()["messages"][0]["head"], "texto")


class TranscriptLag(GateCase):
    """The turn's last steps reach the transcript with the final response, after Stop has started."""

    def test_stop_waits_for_the_final_response(self):
        """The measured case: the last tool calls arrive together with the final response."""
        self.submit("Grave as duas notas.", "p1")
        final = "Gravei as duas notas."

        def late():
            time.sleep(0.4)
            self.tr.tool("toolu_w1", "Write", {"file_path": "a.md"}, "File created successfully", "p1")
            self.tr.tool("toolu_w2", "Write", {"file_path": "b.md"}, "File created successfully", "p1")
            self.tr.assistant(final)

        writer = threading.Thread(target=late)
        writer.start()
        out = self.hook("stop", dict(self.base("p1"), last_assistant_message=final, background_tasks=[]))
        writer.join()
        self.assertIsNone(out)
        pkg = self.package()
        self.assertEqual([i["tool"] for i in pkg["turn"] if i["kind"] == "tool"], ["Write", "Write"])
        self.assertEqual(len(pkg["final_response"]["same_as"]), 1)
        self.assertEqual(pkg["notes"], [])
        wait = self.log()[-1]["final_wait"]
        self.assertTrue(wait["held"])
        self.assertGreater(wait["waited_ms"], 200)
        self.assertLess(wait["waited_ms"], 1900)  # ended by the write, not by the limit

    def test_final_response_that_never_arrives_is_declared(self):
        self.write_config({"timeout_s": 5, "lock_wait_s": 20, "stop_wait_s": 0.3})
        self.submit("Faça.", "p1")
        self.hook("stop", dict(self.base("p1"), last_assistant_message="feito", background_tasks=[]))
        self.assertEqual(self.package()["notes"], [transcript.FINAL_MISSING])
        wait = self.log()[-1]["final_wait"]
        self.assertFalse(wait["held"])
        self.assertGreaterEqual(wait["waited_ms"], 300)

    def test_no_wait_when_the_transcript_already_holds_it(self):
        self.submit("Faça.", "p1")
        self.stop("p1", "feito")
        wait = self.log()[-1]["final_wait"]
        self.assertTrue(wait["held"])
        self.assertLess(wait["waited_ms"], 50)


class Validation(unittest.TestCase):
    refs = {"U1", "F", "T2"}

    def check(self, reply, event="stop"):
        return evaluator.validate(event, reply, self.refs)

    def finding(self, **kw):
        f = {"category": "delegated_work", "refs": ["U1"], "description": "d", "action": "a"}
        f.update(kw)
        return f

    def test_valid(self):
        verdict, problem = self.check({"verdict": "revise", "findings": [self.finding()], "missing": []})
        self.assertIsNone(problem)
        self.assertEqual(verdict["findings"][0]["category"], "delegated_work")

    def test_rejections(self):
        cases = [
            ({"verdict": "ok", "findings": [], "missing": []}, "verdict"),
            ({"verdict": "revise", "findings": [], "missing": []}, "revise without findings"),
            ({"verdict": "pass", "findings": [self.finding()], "missing": []}, "pass with findings"),
            ({"verdict": "unknown", "findings": [], "missing": []}, "unknown without"),
            ({"verdict": "revise", "findings": [self.finding(refs=["Z9"])], "missing": []}, "absent"),
            ({"verdict": "revise", "findings": [self.finding(refs=[])], "missing": []}, "no references"),
            ({"verdict": "revise", "findings": [self.finding(category="already_answered")], "missing": []}, "category"),
            ({"verdict": "revise", "findings": [self.finding(action=" ")], "missing": []}, "empty action"),
            ("text", "not an object"),
        ]
        for reply, expected in cases:
            _, problem = self.check(reply)
            self.assertIsNotNone(problem, reply)
            self.assertIn(expected, problem)

    def test_question_categories(self):
        _, problem = evaluator.validate("question", {"verdict": "revise", "missing": [], "findings": [
            self.finding(category="already_answered", refs=["Q"])]}, {"Q"})
        self.assertIsNone(problem)


if __name__ == "__main__":
    unittest.main()
