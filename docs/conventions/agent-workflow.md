# Agent workflow conventions

This is the narrative companion to `.roo/rules/00-agent-workflow.md`.
The two documents share section headings in the same order. When they
conflict in content, the imperative version wins.

## Reading order

The rules in `.roo/rules/` are short by design: they are meant to be
read in full at the start of every session. The order matters.
`00-agent-workflow.md` establishes the working contract before any
project-specific rules are applied. `ARCHITECTURE.md` gives the design
context an agent needs before making changes that affect behavior. The
project's `CLAUDE.md` customizes the general rules for the specific
repository.

Reading in a different order leads to avoidable mistakes: an agent that
applies project-specific overrides before understanding the general
contract will misapply those overrides.

## Session state lives in `.agent/`

The `.agent/` directory exists to solve a specific problem: AI agents do
not have persistent memory across sessions. Without a committed record,
every new session starts from scratch, re-discovering decisions that
were already made, re-asking questions that were already answered, and
duplicating work that was already done.

Committing `.agent/` to the repository treats agent work products as
first-class project knowledge. A human reviewer can read
`.agent/plan.md` and see what the agent was trying to do and why. The
next agent session — whether it is the same agent, a different agent,
or a human picking up where the agent left off — has a reliable
starting point.

The consequence of not committing `.agent/` is not just inconvenience.
It means every session is an island, and the project cannot benefit
from the continuity that written records provide.

## File format

Markdown task lists are used for plans because they are both
human-readable and machine-parseable. A checked checkbox signals to
both a human reviewer and the next agent session that a step is
complete. An unchecked checkbox signals where to resume.

The example plan format in the rules file is a minimum, not a rigid
template. A plan file can and should grow to include whatever is needed:
open questions, links to relevant commits, warnings about known
obstacles. The requirement is that the file remains useful to someone
reading it without access to the original conversation.

Date-stamping significant entries matters for the same reason. A
decision recorded without a date becomes hard to evaluate once the
project's state has changed.

## Resumability

The rule "mark a plan stale rather than deleting it" reflects a
principle about incomplete information. When an agent starts a new
session and finds a plan that looks inconsistent with recent commits,
it does not know with certainty that the plan is wrong — it knows only
that something has changed. Marking a plan stale preserves the record
while preventing it from being acted on blindly. Deleting it destroys
the history of what was decided and why.

Moving completed plans to `.agent/done/` rather than deleting them has
the same rationale. Completed work is a reference. If the same design
question comes up again later, the completed plan documents what was
tried, what worked, and what was discarded.

## Plan before code

The plan-before-code rule reflects an asymmetry in the cost of errors.
A plan that turns out to be wrong is cheap to correct before a line of
code is written. A plan that turns out to be wrong after the code is
written requires reversing the code, understanding the side effects,
and re-communicating the change to reviewers.

The plan covers what will change, why, what will not change, how the
change will be verified, and what risks exist. The "what will not
change" section is often the most valuable part: an explicit statement
of scope boundaries prevents the plan from expanding during execution.

The exception for small, obvious changes — a typo correction, a
one-line bug fix — is a practical concession. Requiring a formal plan
for every trivial change adds friction without reducing risk.

## Documentation first

Updating documentation before changing behavior prevents documentation
debt. When behavior is changed first and documentation is updated
"later," that later update is more likely to be skipped, abbreviated,
or inconsistent with the actual change. The change is also harder to
review: a reviewer reading a pull request that modifies behavior without
updating documentation cannot tell whether the omission was intentional
or accidental.

The principle that "if a change does not justify a documentation update,
it is either too small to need a plan or it is hiding behavior changes
from review" captures the underlying logic. Documentation is a forcing
function: it requires the author to articulate what changed and why in
terms a reader unfamiliar with the change can follow.

For projects with architecture documents, the documentation-first rule
applies to design changes as well. An `ARCHITECTURE.md` updated before
or alongside the code change serves as a reviewable proposal before the
implementation is committed.

When adding a new public-facing element — a function, a CLI flag, a
configuration option, an environment variable — add it to the
user-facing documentation in the same commit.

## English in repositories and online services

Projects on public platforms are globally discoverable. A user searching
for an error message or a configuration option will not find
documentation or community discussion written in a language other than
the one they are searching in. Non-English repositories effectively
exclude the majority of potential users and contributors.

English in repositories is therefore not a stylistic preference. It is
a structural requirement for any project with external visibility. It is
what makes error messages searchable, documentation findable, and
contributions possible from outside the immediate team.

## Communication follows the user's language

The English-in-repositories rule governs persistent artifacts that live
in the repository and are visible to external parties. It does not
govern the working conversation between a user and an agent.

Requiring a German-speaking user to write prompts in English adds
friction without benefit. The agent's job is to assist the user
effectively, which means meeting the user in their language. The code,
commits, and pull request descriptions that result from the conversation
are still in English because those are repository artifacts subject to
the rule above.

## Asking is cheap

The rule reflects an asymmetry in the cost of errors. A clarifying
question takes seconds. Implementing the wrong thing, discovering it is
wrong during review, reverting, and reimplementing can take hours.

The list of situations that require asking — renaming, support matrix
changes, external dependencies, cross-repository changes — is a minimum,
not an exhaustive enumeration. These are the categories of change where
the cost of being wrong is highest, because they affect external users,
cross role boundaries, or introduce dependencies that are hard to
remove.

The underlying principle is that when an agent is uncertain about scope
or intent, it should surface that uncertainty rather than resolve it
silently with a guess.

## Scope discipline

Inline scope creep is a pull request problem. When a pull request mixes
a focused fix with unrelated improvements, reviewers cannot efficiently
validate the focused fix without also evaluating the improvements. The
improvements may be good; the problem is that they are mixed in with
something else, making the pull request harder to read, harder to
revert, and harder to bisect if something goes wrong later.

Noting unrelated findings in `.agent/findings.md` is not a way of
ignoring them. It is a way of making them visible without mixing them
into the current change. A finding in `.agent/findings.md` can become
the basis for a follow-up task.

## Upstream feedback loop

### Why this exists

Shared rules are written upfront based on what is known at the time of
writing. Real projects reveal gaps, ambiguities, and errors that were
not anticipated. Without a feedback path, those revelations stay buried
in individual projects and the shared rules never improve. The same gap
gets re-discovered in the next project, and the project after that, and
the project after that.

The upstream candidates mechanism is the feedback path.

### The generalisation test

Not every finding belongs in the shared rules. Most findings are
project-specific. Apply this test:

> Would this same issue plausibly appear in another project with a
> similar structure but different domain or stack?

If yes, it is a candidate for the shared rules. If no, it is a
project-local note and goes in `.agent/findings.md`.

The generalisation test is intentionally permissive. If unsure, write
the candidate down. Rejecting a candidate is cheap; missing one means
the gap persists.

### Separation between proposing and deciding

The agent proposes candidates. The agent does not promote them. A human
decides whether each candidate becomes a shared rule, gets deferred, or
is rejected.

This separation is deliberate. An agent that could promote its own
candidates would create a self-reinforcing loop: the shared rules would
gradually reflect agent preferences rather than deliberate human
decisions about project conventions.

### Format requirements and why they matter

The format requires that the proposed rule text be self-contained: it
can be lifted out of the project's `.agent/upstream-candidates.md` and
pasted into the upstream rules file without further editing. The
"Originating context" block is explicitly marked for removal on
promotion so it is clear what survives the move.

A candidate that requires reading the originating project's context to
make sense cannot be evaluated on its own merits. The format enforces
portability.

### Lifecycle of a candidate

A candidate is open until a human promotes, defers, or rejects it.
Promoted candidates update the upstream rules and are archived in
`.agent/upstream-candidates/done/`. Rejected candidates remain in place
rather than being deleted — they prevent the same topic from being
re-evaluated from scratch in six months.

### Cross-project visibility

Promoting a candidate updates the shared rules. The shared rules are
not automatically connected to the projects that consume them. A human
is responsible for carrying a promoted change into the projects that
should adopt it.

To stay on top of open candidates across many projects, do periodic
reviews: walk through every active project's
`.agent/upstream-candidates.md`, evaluate the open entries, and
promote, defer, or reject. Quarterly is a reasonable cadence; the
right frequency depends on how often projects produce candidates.

A future option, if manual review becomes too time-consuming, is to
build a small aggregation tool that collects open candidates from all
repositories into a single overview. The manual approach is enough
until the volume justifies tooling.

## Mistake handling

Mistakes are expected. The rule is not that mistakes must not happen —
it is that mistakes must not be concealed.

Silently producing a new plan that contradicts the old one without
acknowledging the contradiction creates confusion for anyone who later
reads the `.agent/` files. The record appears internally consistent but
is not. A future agent session or human reviewer has no way to know
that the first plan was wrong and why.

Owning a mistake directly and updating the `.agent/` file with what was
learned keeps the project record accurate and useful.
