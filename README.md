# airunner-common

Shared, dependency-light foundation for
[Capsize-Games/airunner](https://github.com/Capsize-Games/airunner)
(AI Runner)'s distributions: the desktop GUI (`airunner`), the headless
service daemon (`airunner-services`), and the native launcher
(`airunner-native`). Extracted into its own repository (issue
[#2197](https://github.com/Capsize-Games/airunner/issues/2197), part of
the repository-split tracker
[#2185](https://github.com/Capsize-Games/airunner/issues/2185)) because
it's the foundation of that dependency graph: every other distribution
depends on this one, and this one depends on none of them.

## What this package owns

- `settings` — environment-derived runtime constants
- `startup_env` — process-startup environment configuration
- `dev_build_token` — stale-daemon detection token
- `linux_bundle_layout` — relocatable Linux bundle path helpers
- `contract_enums` — cross-process and cross-layer contracts (enums that
  cross a package boundary belong here, not duplicated in a consumer)
- `contract_version` — the desktop/daemon wire contract's own version,
  independent of any single distribution's package version
- `llm_response` — the `LLMResponse` payload streamed across the
  desktop/daemon boundary (issue #2188 in the source repository)
- `logging_utils` / `get_logger` — shared logging configuration and the
  one `Logger` implementation both the GUI and services layers use

Nothing here imports from `airunner`, `airunner_services` or
`airunner_native`, so all three can depend on it without a cycle.

## Optional legacy Shield compatibility

The default package installation does not require FacehuggerShield. Consumers
that explicitly need the historical dependency can request the
`legacy-shield` extra, which pins `facehuggershield==1.0.0`. That distribution
is currently paused or yanked on the configured public indexes, so this extra
requires a reviewed source that provides the pinned version. The extra only
installs the dependency; it does not activate it. AIRunner-specific activation
remains the consuming application's responsibility.

## Versioning

The [`airunner-common`](https://pypi.org/project/airunner-common/) project is
registered on PyPI. As of 2026-11-01, its published files are yanked and
distribution is paused. This source change does not resume publication.

This repository continues the version series first published from the source
repository's `shared/` directory, starting at 6.1.4. It does not restart at
0.1.0 because existing consumers already pin `airunner-common~=6.1`.

## Provenance

Extracted from `Capsize-Games/airunner` (issue #2197). History for the
moved files is preserved (`git filter-repo`).

## Licensing

GPL-3.0-only, matching the applications that depend on it. See
[`LICENSE`](LICENSE).
