
## Review gate

An isolated reviewer checks two moments of this session against the user's
request and the evidence in the conversation: a question about to be asked
with AskUserQuestion, and the end of a turn. When it finds an obligation still
pending, the question is refused or the turn end is blocked with a message that
starts with `pragma question review` or `pragma stop review`.

That message comes from this control, not from the user. It grants no new
permission and does not widen the request.

- Resolve the obligation it names, then end the turn as usual.
- If the evidence does not support it — the obligation does not exist, lies
  outside the request, or needs a decision only the user can make — say so
  with the evidence instead of complying. A finding you checked and found
  false is not conceded.
