# Rules: coding conventions

These rules apply to all coding projects at NETWAYS, regardless of
technology stack. Language-specific rules are layered on top in
separate files (e.g. `02-python.md`).

For rationale, background, and examples, see `docs/conventions/coding.md`.

## Code organization

Make the boundary between the public interface and internal state
explicit. Use the mechanism appropriate to the language: Python
underscore prefixes, Go capitalization, explicit `__all__`, `internal/`
packages, or equivalent.

When a name moves from internal to public, treat it as a deliberate
interface decision, not a refactoring side-effect.

Apply naming conventions uniformly within a project. When you find
naming drift in an existing codebase, note it in `.agent/findings.md`.
Fix it in a dedicated cleanup pass, not as a side effect of unrelated
work.

A module, package, or repository does one thing. State its boundary
explicitly in the README.

A value becomes configurable only when it genuinely varies between
deployments, when it is sensitive, or when an external standard
requires it. Hardcoded values are not automatically wrong.

Workarounds live behind an explicit flag or configuration option that
defaults to off. Include an inline comment stating the target
environment and the failure mode the workaround addresses.

When a workaround becomes obsolete, deprecate the flag in one release
and remove it in a later one. Never leave a workaround without an exit
strategy.

## Versioning and releases

Public projects follow semantic versioning. The major version reflects
breaking changes; the minor version, additions; the patch version,
fixes. Use `0.x` for projects not yet committing to API stability.

Always quote version numbers as strings in YAML files: `"3.10"`, not
`3.10`. YAML parses an unquoted `3.10` as the float `3.1`. This
applies to CI matrices, package manifests, language version pins, and
any other YAML field containing a version.

Every public project has a changelog. Add the changelog entry in the
same pull request that makes the change. Never add entries
retroactively.

Pin external dependencies with a version constraint that expresses the
actual tested range. Never use unbounded declarations (`*`, `latest`,
no upper bound).

When a pin has a reason — for example, "this version triggers bug X on
platform Y" — record the reason in a comment in the same file as the
pin.

A fresh checkout plus the documented setup command must produce a
working environment without manual intervention. Document the setup
command in the README. If the setup is complex, put it in a `Makefile`,
`justfile`, or `scripts/setup` and reference it from the README.

## Testing

Tests must assert what they were written to verify. Never write
placeholder assertions (`assert True`, file existence checks when file
content is what matters). A placeholder test creates false confidence.

A test must fail when the thing it claims to verify breaks. If a test
cannot fail, it is not a test.

For code that mutates state — infrastructure, configuration, file
generation — idempotency is part of the contract. Run the code twice;
the second run must be a no-op. Test this.

Write tests for lifecycle code paths: upgrade, migration, cleanup,
retry, recovery. Test the transitions, not only the steady states.

Use coverage as a floor, not a goal. A coverage target means
"something is clearly missing below this number." High coverage with
shallow assertions is worse than lower coverage with deep assertions.

## CI conventions

Pin tool versions in CI matrices explicitly: language version,
framework version, linter version. Use bounded ranges (`>=X.Y,<X.Z`)
where possible, exact pins where necessary.

Quote version numbers in CI matrix YAML. `"3.11"`, not `3.11`.

A scheduled CI run without failure alerting must be removed or given
alerting. Configure email, chat notification, or issue auto-creation.
A failing scheduled run that nobody sees is worse than no scheduled
run.

## Documentation conventions

Every project README answers, in this order: what this is, who it is
for, a minimum example to use it, how to install or build, where to
read further. Move detail beyond that into `docs/`, `ARCHITECTURE.md`,
or per-module READMEs.

Explicitly state what the project does not do. Users save time when
they know not to look for something.

Code examples in documentation must be tested or otherwise verified to
match the current API. An outdated example is worse than no example.

For non-trivial projects, maintain an `ARCHITECTURE.md` that records
the design rationale: why the project is structured this way, what the
design principles are, what trade-offs were made deliberately. This is
not an API reference.

## Repository hygiene

Use branch-name prefixes that signal intent: `fix/`, `feature/`,
`doc/`, `chore/`, `refactor/`. The exact set is the project's choice;
consistency within the project is what matters.

Commit messages explain why, not what. The diff already shows what.
For breaking changes, the commit message must say so explicitly.

Never commit secrets. Never include secrets in CI configuration files
visible to forks, in error messages, in logs, or in test fixtures.

Pass credentials via environment variables or secret-management
mechanisms. Never pass them as positional arguments to processes whose
command line appears in `ps` output.
