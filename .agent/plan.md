# Plan: build coding-conventions template

## Status
Complete

## Steps
- [x] Present plan to user and receive approval
- [x] Create directory structure
- [x] Create .agent/plan.md (this file)
- [x] Create .roo/rules/00-agent-workflow.md
- [x] Create .roo/rules/01-coding.md
- [x] Create docs/conventions/README.md
- [x] Create docs/conventions/agent-workflow.md
- [x] Create docs/conventions/coding.md
- [x] Create .agent/README.md
- [x] Create CLAUDE.md
- [x] Create .rooignore
- [x] Create README.md
- [x] Create .agent/upstream-candidates.md

## Decisions
- 2026-05-08: Generalised Ansible-specific file names (`01-ansible.md`, `02-molecule.md`,
  `03-testing.md`) in the upstream-feedback-loop section of 00-agent-workflow.md to
  `01-coding.md` and "language-specific rules files". Upstream candidate recorded.
- 2026-05-08: "English in repositories and online services" kept only in 00-agent-workflow.md;
  not duplicated in 01-coding.md.
- 2026-05-08: Each .roo/rules/ file gets a brief note pointing to its docs/conventions/ companion.
- 2026-05-08: CLAUDE.md uses @-import syntax to inline both rules files.
