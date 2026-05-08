# Upstream candidates

Findings from this project that may belong in the shared rules.
See `.roo/rules/00-agent-workflow.md` §Upstream feedback loop for the
format and lifecycle.

---

## 2026-05-08: Agent-workflow rules reference Ansible-specific file names

**Status:** open

**Target file:** .roo/rules/00-agent-workflow.md (upstream)

**Type:** rule change

**Proposed rule text:**
> When something surfaces during work that is not a project-local
> finding but a gap, error, or ambiguity in the **shared rules
> themselves** (this file, `01-coding.md`, language-specific rules
> files, `ARCHITECTURE.md`), record it as an upstream candidate.

**Why this generalises:**
The current upstream text names `01-ansible.md`, `02-molecule.md`,
and `03-testing.md` in a rule that is supposed to apply to all
projects regardless of stack. Any non-Ansible project using this
rule set will encounter file names that do not exist, and the
examples will mislead rather than illustrate. Replacing the
Ansible-specific names with the generic equivalents makes the rule
apply correctly to all project types.

**Originating context (drop on promotion):**
Surfaced when creating the coding-conventions template repository.
The rule was copied from the Ansible template and the Ansible file
names were carried over verbatim. Fixed in this project by replacing
`01-ansible.md`, `02-molecule.md`, `03-testing.md` with `01-coding.md`
and "language-specific rules files".
