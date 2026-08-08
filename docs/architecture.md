# Architecture

The package is a Python CLI installed from `src/social_content_data_packager`.

- `cli.py` parses commands and delegates work.
- `workspace.py` manages the standard Chinese input/output directories.
- `validation.py` checks metadata, comments and media streams.
- `transcript.py` optionally runs local Whisper and writes transcript artifacts.
- `packager.py` creates the verified Excel/ZIP data package.
- `verification.py` independently checks package contents and SHA-256 values.
- The in-progress `collector.py` can connect to a user-authorized Edge/CDP session and copy DATATOOL
  downloads into a new workspace. It is excluded from the current release candidate and must not be
  described as a stable command or used to bypass authentication or platform controls.

The CLI is deterministic and local-first. External platform access is user-authorized browser state,
not a server-side credential or repository secret.
