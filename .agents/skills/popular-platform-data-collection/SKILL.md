---
name: popular-platform-data-collection
description: Use when Codex needs to process DATATOOL exports from public or authorized social-video content, validate and package videos, covers, copy, and comments, or transcribe video speech with the social-content-packager CLI.
---

# Popular Platform Data Collection

Use the repository CLI to validate exported inputs, optionally transcribe complete
video audio locally with Whisper, and generate a verifiable Chinese ZIP data package.

## Safety Boundaries

- Process only public, user-owned, or explicitly authorized content.
- Require the user to export files manually with DATATOOL. Do not operate the extension,
  automate login, bypass verification, or access cookies, browser profiles, or credentials.
- Exclude raw comments by default. Use `--anonymize-comments` for shareable packages and
  include raw comments only after explicit user confirmation.

## Run the CLI

1. Resolve the repository root with `git rev-parse --show-toplevel`.
2. Prefer `.venv-whisper\\Scripts\\python.exe`; otherwise use `.venv\\Scripts\\python.exe`.
3. Run `doctor` before any transcription request.
4. Run the requested command with `python -m social_content_data_packager`.

## Workflow

```powershell
python -m social_content_data_packager init "<workspace>"
python -m social_content_data_packager validate "<workspace>"
python -m social_content_data_packager package "<workspace>" --transcribe-video --model small --language zh --anonymize-comments
python -m social_content_data_packager verify "<workspace>\\output\\<archive>.zip"
```

Use the required input filenames documented in `README.md`. Treat comments and cover
files as optional. Do not overwrite an existing transcript unless the user explicitly
requests `--force-transcript`.

## Command Choice

| Request | Command |
| --- | --- |
| Check dependencies | `doctor` |
| Create task layout | `init <workspace>` |
| Check exported files | `validate <workspace>` |
| Extract spoken video copy only | `transcribe <workspace> --model small --language zh` |
| Create the package | `package <workspace>` |
| Verify an existing ZIP | `verify <zip>` |
