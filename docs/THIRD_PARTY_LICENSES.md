# Third-party license inventory

Audit date: 2026-08-08
Project license: MIT (`LICENSE`)
Scope: direct runtime, optional, development, and audit dependencies in the stable Release Candidate,
plus the separately audited `playwright` dependency used only by the excluded dirty-worktree `browser`
development branch. The review also covers dependency metadata and package contents that enter the
wheel/sdist. This is a reasonable technical license audit, not legal advice.

## Direct runtime and optional dependencies

| Package | Version / range | Purpose | Official source | Declared license | SPDX | MIT compatibility | Attribution / redistribution | Bundled in package | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `openpyxl` | `>=3.1,<4` (audited 3.1.5) | XLSX read/write | [openpyxl](https://openpyxl.readthedocs.io/) | Upstream licence and installed metadata identify MIT | `MIT` | Compatible | Preserve the MIT notice if its code is redistributed | No | `VERIFIED` |
| `openai-whisper` | `>=20250625` (audited 20250625) | Optional local transcription | [openai/whisper](https://github.com/openai/whisper) | Upstream `LICENSE` and installed metadata identify MIT | `MIT` | Compatible | Preserve the MIT notice if its code is redistributed | No | `VERIFIED` |

## Excluded dirty-worktree optional dependency

| Package | Version / range | Purpose | Official source | Declared license | SPDX | Candidate relation | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `playwright` | `>=1.50,<2` (audited 1.62.0) | Browser/CDP integration for unfinished `collect` development | [microsoft/playwright-python](https://github.com/microsoft/playwright-python) | Upstream `LICENSE` is Apache License 2.0 | `Apache-2.0` | Not declared, bundled, or required by the stable Release Candidate | `VERIFIED / EXCLUDED` |

## Development and audit dependencies

| Package | Version / range | Purpose | Official source | Declared license | SPDX | MIT compatibility | Attribution / redistribution | Bundled in package | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `build` | `>=1.2,<2` (audited 1.5.0) | Build wheel/sdist | [pypa/build](https://github.com/pypa/build) | Upstream `LICENSE` contains the MIT grant | `MIT` | Compatible | Preserve the MIT notice if its code is redistributed | No | `VERIFIED` |
| `mypy` | `>=1.11,<2` (audited 1.20.2) | Static type checking | [python/mypy](https://github.com/python/mypy) | Upstream `LICENSE` identifies MIT | `MIT` | Compatible | Preserve the MIT notice if its code is redistributed | No | `VERIFIED` |
| `pip-audit` | `>=2.7,<3` (audited 2.10.1) | Dependency vulnerability audit | [pypa/pip-audit](https://github.com/pypa/pip-audit) | Upstream `LICENSE` and installed classifier identify Apache License 2.0 | `Apache-2.0` | Compatible as a separately installed tool | Preserve the Apache-2.0 license and applicable notices if its code is redistributed | No | `VERIFIED` |
| `pytest` | `>=8,<10` (audited 9.1.1) | Test runner | [pytest-dev/pytest](https://github.com/pytest-dev/pytest) | Upstream `LICENSE` identifies MIT | `MIT` | Compatible | Preserve the MIT notice if its code is redistributed | No | `VERIFIED` |
| `pytest-cov` | `>=5,<8` (audited 7.1.0) | Coverage reporting | [pytest-dev/pytest-cov](https://github.com/pytest-dev/pytest-cov) | Upstream `LICENSE` and installed classifier identify MIT | `MIT` | Compatible | Preserve the MIT notice if its code is redistributed | No | `VERIFIED` |
| `ruff` | `>=0.8,<1` (audited 0.16.1 locally; resolver selected 0.16.2) | Lint checks | [astral-sh/ruff](https://github.com/astral-sh/ruff) | Upstream `LICENSE` identifies MIT | `MIT` | Compatible | Preserve the MIT notice if its code is redistributed | No | `VERIFIED` |

The official upstream licence files above were retrieved read-only on 2026-08-08. Installed distribution
metadata was also checked where available. Empty legacy `License:` fields were not treated as proof of an
unknown licence when the package's official upstream `LICENSE` supplied clear evidence.

## Transitive dependency snapshot

The read-only dependency resolution includes packages such as `torch`, `numpy`, `numba`, `requests`,
`pyee`, `greenlet`, `tiktoken`, `regex`, `Jinja2`, `networkx`, and `sympy`. They are installed by the
end user as transitive dependencies; their source, licence texts, and notices are not vendored, copied,
or bundled into this project's wheel/sdist.

`TRANSITIVE_LICENSE_METADATA = PASS_WITH_NOTES`

This status means that incomplete transitive metadata remains a documentation note, not a publication
blocker for the current non-vendored package. It must be reassessed if a future release bundles dependency
code, native binaries, model files, fonts, datasets, or other third-party assets.

## Distribution boundary

- The project wheel/sdist contains project source, project metadata, and the MIT `LICENSE`; dependency code
  is not embedded.
- `pyproject.toml` records dependency requirements instead of redistributing their packages.
- The stable candidate metadata declares `openpyxl`, `openai-whisper`, and development/audit tools; it does
  not declare the dirty-worktree-only `browser`/`playwright` extra.
- No vendored dependency directory or copied third-party source tree was identified in the repository audit.
- No additional `THIRD_PARTY_NOTICES.md` is required for the current distribution boundary.

`LICENSE_READY = YES`

No visual asset enters the stable Release Candidate. The tracked legacy cover remains excluded because its
redistribution rights are unverified; under the v1.2 project policy, no replacement visual is required.
