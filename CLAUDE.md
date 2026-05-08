# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

This repository is the NETWAYS language-agnostic rules template. It provides
a starting point for new coding projects. The rules here apply regardless of
technology stack. Language-specific rules are added as separate files when a
concrete project needs them (e.g. `.roo/rules/02-python.md`).

The short, imperative rules are in `.roo/rules/` and are imported below.
For the rationale and background behind each rule, see `docs/conventions/`.
Read those files when the short rules leave something unclear — agents should
not ingest them every session, only when needed.

<!-- PROJECT-SPECIFIC: Replace this comment with a brief description of what
     this project is, who it is for, and its primary technology stack. -->

## Rules

@.roo/rules/00-agent-workflow.md
@.roo/rules/01-coding.md

## Project-specific conventions

<!-- PROJECT-SPECIFIC: Add any conventions specific to this project that are
     not covered by the general rules above. Examples: preferred test
     framework, release process, configuration layout decisions, commit
     message format enforced by CI. -->

## Things to never do without approval

<!-- PROJECT-SPECIFIC: List actions that require explicit human approval
     before proceeding. Examples: pushing to main, running database
     migrations, changing public APIs, modifying CI secrets, bumping the
     major version of a dependency, deploying to production. -->

## Known gotchas

<!-- PROJECT-SPECIFIC: Document environment quirks, non-obvious behaviors,
     or traps that have caused problems before. Examples: a dependency that
     breaks on a specific platform, a test that requires a running external
     service, a configuration value that is easy to set incorrectly. -->
