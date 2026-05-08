# Coding conventions

This is the narrative companion to `.roo/rules/01-coding.md`.
The two documents share section headings in the same order. When they
conflict in content, the imperative version wins.

## Code organization

### Public interface vs. internal state

Make the boundary between the public interface and internal state
explicit. Different languages have different mechanisms — Python
underscore prefixes, Go capitalization, explicit `__all__`, `internal/`
packages, public `pkg/` directories — but the principle is the same: a
reader (or an agent) must be able to tell at a glance whether a name is
part of the contract or an implementation detail.

If a name moves from internal to public, treat it as a deliberate
interface decision, not a refactoring side-effect. Interface decisions
have consequences: external code may depend on the name, and changing
it later is a breaking change.

### Naming consistency

Apply naming conventions uniformly within a project. Drift creates
ambiguity: when one part of the codebase uses one convention and another
part uses a different one, every contributor has to remember which is
which.

When you find naming drift in an existing codebase, note it in
`.agent/findings.md`. Fix it as a deliberate cleanup pass, not as a
side effect of unrelated work. Mixing a naming cleanup with a behavior
change makes both harder to review.

### Scope discipline

A module, package, or repository does one thing. The boundary of "what
this is" is explicit in the README and is enforced when reviewing pull
requests.

Excess configurability is friction, not flexibility. A value becomes
configurable only when it genuinely varies between deployments, when it
is sensitive, or when an external standard requires it. Hardcoded values
are not automatically wrong.

### Workarounds are explicit and documented

Workarounds are opt-in where possible. They live behind an explicit
flag, configuration option, or feature gate that defaults to off. They
have an inline comment explaining the target environment and the failure
mode they address.

When a workaround becomes obsolete, deprecate the flag in one release
and remove it in a later release. Workarounds without an exit strategy
become permanent.

## Versioning and releases

### Semantic versioning

Public projects follow semantic versioning. The major version reflects
breaking changes; the minor version, additions; the patch version,
fixes.

Pre-1.0 versions are explicitly less stable. Use `0.x` for projects
that are not yet committing to API stability.

### Quoted version numbers in YAML

Always quote version numbers as strings in any YAML file: `"3.10"`, not
`3.10`. YAML's native parser converts `3.10` to the float `3.1`, which
is silent and load-bearing wrong. This applies to CI matrix files,
package manifests, language version pins, and any other YAML field
where a version appears.

### Changelog

Every public project has a changelog. The format is the project's
choice (Keep-a-Changelog, towncrier, antsibull-changelog,
auto-generated from commits) but the principle is fixed: every release
adds an entry, the entry describes user-visible changes, and the entry
is written in the same pull request that makes the change — not
retroactively.

### Pinned dependencies

External dependencies are pinned with a version constraint that
expresses the actual tested range. Unbounded dependency declarations
(`*`, `latest`, no upper bound) are a reproducibility risk.

When a pin has a reason ("this version triggers bug X on platform Y"),
the reason is recorded in a comment in the same file as the pin. Pins
without a recorded reason rot — the next contributor cannot tell
whether the pin is still load-bearing.

### Reproducible builds

A fresh checkout plus a documented setup command produces a working
environment. The setup command is in the README. The setup command
works without manual intervention.

If the setup is complex enough that it cannot fit in a few README
lines, it lives in a `Makefile`, `justfile`, `scripts/setup`, or
similar — referenced from the README.

## Testing

### Real assertions

Tests assert what the test was created to verify. Placeholder tests
(`assert True`, "service is enabled" without checking what the service
does, file existence checks for files whose content matters) are worse
than no test — they create false confidence.

A test must fail when the thing it claims to verify breaks. If a test
cannot fail, it is not a test.

### Idempotency, where it applies

For code that mutates state (infrastructure, configuration, file
generation), idempotency is part of the contract. Run twice; the second
run is a no-op. Test it.

For pure code (libraries, calculations), this principle does not apply.

### Test what changes, not just what is

For lifecycle code paths (upgrade, migration, cleanup, retry, recovery),
write tests that exercise the lifecycle event, not just the steady
state. The hard part of operations code is the transitions, not the end
states.

### Coverage is a tool, not a goal

A coverage number alone does not say anything useful. High coverage
with shallow assertions is worse than lower coverage with deep
assertions.

When a coverage target is set (e.g., 80%), it is a floor below which
something is clearly missing — not a ceiling beyond which nothing is
worth testing.

## CI conventions

### Pin the testing toolchain

CI matrices pin tool versions explicitly: language version, framework
version, linter version. Pinning catches regressions caused by tool
updates and keeps test results reproducible.

Use bounded ranges (`>=X.Y,<X.Z`) where possible, exact pins where
necessary, version specifiers that match the project's actual support
contract.

### Quote version numbers in CI matrices

Same rule as elsewhere: `"3.11"` not `3.11`. CI matrix files are YAML;
the float trap applies.

### Scheduled runs need alerting

A scheduled CI run (nightly, weekly) without failure alerting is
silent. Failures pile up unnoticed and the run becomes worse than no
run at all because it creates false confidence.

Either configure alerting (email, Slack, issue auto-creation) or
remove the schedule. Pull-request CI catches most regressions; the
case for additional scheduled runs must be specific.

## Documentation conventions

### README is the entry point

Every project's README answers, in this order:

1. What this is
2. Who it is for
3. Minimum example to use it
4. How to install or build
5. Where to read further

Move detail beyond that into separate documents (`docs/`,
`ARCHITECTURE.md`, per-module READMEs). The top-level README is
optimized for someone who has never seen the project before.

### Document what is out of scope

Explicitly state what the project does *not* do. Users save time when
they know not to look for something. This applies at every level —
project, package, module, function.

### Examples in documentation must work

Code examples in documentation are tested or otherwise verified to
match the current API. Examples that drift from the code create
worse-than-no-documentation: confidently wrong information.

### Architecture documents

For non-trivial projects, maintain an `ARCHITECTURE.md` that explains
the design — not the API, but the *why*. Why the project is structured
this way. What the design principles are. What trade-offs were made
deliberately. This document outlives any specific contributor and
orients new ones.

## Repository hygiene

### Branch naming

Use prefixes that signal intent: `fix/`, `feature/`, `doc/`, `chore/`,
`refactor/`. The exact set is the project's choice; consistency is what
matters. The prefix is part of code review — a reviewer approaches a
`fix/` branch differently from a `feature/` branch.

### Commit messages

Commit messages explain *why*, not *what*. The diff already shows what.
The commit message records the reasoning that the diff alone cannot
convey.

For breaking changes, the message says so explicitly. The exact
convention (Conventional Commits, plain prose) is the project's choice;
the principle is that someone reading `git log` six months from now
should be able to follow the project's history.

### Secrets are never in repositories

No secrets in committed files. No secrets in CI configuration files
visible to forks. No secrets in error messages, logs, or test fixtures.

When credentials must appear in code paths (passing them to a
subprocess, an API client, etc.), they are passed via environment
variables or secret-management mechanisms — never via positional
arguments to processes whose command line appears in `ps` output.
