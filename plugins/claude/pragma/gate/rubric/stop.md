Moment: the agent ended its turn with the final response `F`, which the user
has already seen.

Revise only when the evidence shows one of these:

- `delegated_work`: a part the user asked for and authorized was left as an
  offer, or as a command for the user to run, although the agent could have
  done it.
- `missing_verification`: a verification the task called for (asked by the
  user, or needed to support a claim in `F`) has no result, nothing concrete
  prevented it, and it can still be run.
- `unproven_success`: a test or attempt that was only started, or that ended
  inconclusive, is presented as passed or done.
- `unanswered_question`: a question the user asked is not answered in `F` or
  in an earlier `assistant` item, or `F` claims it was answered when no
  `assistant` item shows the answer.
- `false_completion`: `F` declares the work complete while a known failure
  inside the requested scope remains.
- `stale_pending`: `F` presents something as still pending although the
  evidence shows it resolved, discarded or never confirmed, or presents an
  unconfirmed state as confirmed.
- `temporary_resources`: `F` reports temporary resources the agent created
  that remain, without resolving what happens to them or naming a concrete
  need to keep them. The action is to identify their origin and dependencies
  before deciding; never to delete shared or pre-existing resources.
- `unintelligible`: `F` can only be understood through internal test codes or
  through terms the conversation shows the user did not understand.

Let these through: the requested work is done and `F` reports it faithfully;
a required environment was unavailable and `F` explains the observed failure
and its impact; a test is still running and `F` says so without claiming
success; the user only asked for an explanation; something outside the scope
is merely mentioned as a possible improvement; `F` disputes the user with
evidence.
