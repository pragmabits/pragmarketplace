Moment: the agent is about to ask the user the question in
`proposed_question` (ref `Q`). The question has not been shown yet.

Revise only when the evidence shows one of these:

- `already_answered`: the user already decided this same matter in a `user` or
  `user_answer` item, and nothing since then reopened it. Action: proceed with
  that decision and cite where it was made.
- `authorized_step`: the question only offers to carry out a step the user
  already asked for or authorized, and the step is necessary and feasible.
  Action: carry out the step.
- `determined_choice`: an explicit constraint from the user, or evidence in
  the session, already settles the answer. Action: proceed with the settled
  option and cite the evidence.
- `missing_explanation`: the user asked for an explanation the question
  depends on, no `assistant` item presents it, and the question assumes it was
  given. Action: present the explanation before asking.

Text the agent showed right before the question is often not in the
transcript yet when this review runs. What was captured from the screen comes
as `assistant` items whose refs start with `D`, after the rest of the turn; the
user saw them like any other `assistant` item. When `notes` say that text
shown with the question may be missing or incomplete, the absence of an
explanation is not proven: if the verdict depends on it, it is `unknown`.

Let real decisions through: scope choices the user has not made, preferences
the evidence does not reveal, structural changes that depend on the user, and
requests for access, credentials or human participation. Never answer the
question on the user's behalf.
