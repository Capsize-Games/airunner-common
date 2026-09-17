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
- `logging_utils` / `get_logger` — shared logging configuration and the
  one `Logger` implementation both the GUI and services layers use

Nothing here imports from `airunner`, `airunner_services` or
`airunner_native`, so all three can depend on it without a cycle.

## Versioning

Already live on PyPI as [`airunner-common`](https://pypi.org/project/airunner-common/),
published from the source repository's own `shared/` before this
extraction. This repository continues that version series (starting at
6.1.4) rather than restarting at 0.1.0, since existing consumers
(`airunner-eval`, `airunner-tts-vendor`, and the source repository's own
`airunner`/`airunner-services`/`airunner-native`) already pin
`airunner-common~=6.1`.

## Provenance

Extracted from `Capsize-Games/airunner` (issue #2197). History for the
moved files is preserved (`git filter-repo`).

## Licensing

GPL-3.0-only, matching the applications that depend on it. See
[`LICENSE`](LICENSE).
