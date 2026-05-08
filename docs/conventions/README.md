# docs/conventions

This directory contains the human-readable rationale behind the project's
rules.

## Authoritative source

The authoritative rules are in `.roo/rules/`. Those files are imperative,
concise, and consumed directly by AI coding agents (Claude Code, RooCode)
on every session.

The documents here are long-form companions. They explain the *why* behind
each rule, provide examples, and discuss trade-offs. They are written for
human contributors and for agents that need more context than the short
rules provide.

**When the two conflict in content, `.roo/rules/` wins.**

## Documents

- [agent-workflow.md](agent-workflow.md) — Rationale and background for the
  agent working-session rules in `.roo/rules/00-agent-workflow.md`. Covers
  session state, planning, documentation discipline, the upstream feedback
  loop, and related topics.

- [coding.md](coding.md) — Rationale and background for the coding
  conventions in `.roo/rules/01-coding.md`. Covers code organization,
  versioning, testing, CI, documentation conventions, and repository
  hygiene.
