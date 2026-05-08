# coding-conventions

A NETWAYS template repository for starting new coding projects. It provides
a language-agnostic set of rules and conventions that work out of the box for
both AI coding agents and human contributors.

## What this is

This template defines:

- **Agent workflow rules** — how AI agents plan work, maintain session state,
  handle mistakes, and feed findings back to the shared rules.
- **Coding conventions** — code organization, versioning, testing, CI, and
  repository hygiene practices that apply regardless of language or stack.

It is intentionally language-agnostic. Language-specific rules (e.g. Python,
Go) are added as separate files when a concrete project needs them.

A parallel template exists for Ansible projects. The two are independently
maintained siblings: the same overall shape, independently evolved content.

## How to use this template

1. Copy the repository contents into your new project (or use it as a GitHub
   template).
2. Open `CLAUDE.md` and fill in the four `PROJECT-SPECIFIC` placeholder
   sections.
3. If your project uses a language with specific conventions, add
   `.roo/rules/02-<language>.md` and a matching
   `docs/conventions/<language>.md`.
4. Delete this section of `README.md` and replace it with a description of
   your actual project.

## Where things live

    .roo/rules/               Authoritative rules — short, imperative.
                              Read by Claude Code and RooCode every session.

      00-agent-workflow.md    Agent working-session rules.
      01-coding.md            Coding conventions.

    docs/conventions/         Long-form companions to the rules.
                              Read when the short rules need context.

      agent-workflow.md       Rationale behind 00-agent-workflow.md.
      coding.md               Rationale behind 01-coding.md.

    .agent/                   Plans, checklists, and notes from agent
                              sessions. Committed to the repository.

    CLAUDE.md                 Entry point for Claude Code. Imports the
                              rules and adds project-specific overrides.

## For AI agents

Read `CLAUDE.md` first. It imports the rules in `.roo/rules/` and carries
any project-specific overrides. Read `.roo/rules/00-agent-workflow.md`
before doing anything else — it covers how to maintain session state,
when to plan, and how to handle findings.
