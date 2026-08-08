# Changelog

All notable changes are documented here. This project follows Semantic Versioning.

## 1.0.0 - 2026-07-31

### Release

- Promoted the validated RC2 workflow to the stable 1.0.0 release.
- Added UTF-8 BOM compatibility for Windows-authored metadata and transcript JSON.
- Verified the complete local narration transcription path with a real spoken-audio smoke test.

## 1.0.0-rc2 - 2026-07-31

### Added

- One-command `package --transcribe-video` workflow for full-video local Whisper
  transcription before packaging.
- `完整文案` in transcript JSON for direct access to the complete spoken transcript.

### Changed

- Transcript TXT, JSON and SRT files are included only when real transcript segments
  exist.
- Packages without a transcript now state clearly that complete video narration was
  not extracted.
- Whisper process failures are reported as controlled CLI errors.

## 1.0.0-rc1 - 2026-07-31

### Added

- Workspace `validate` and archive `verify` commands.
- FFprobe media validation and metadata/comment schema checks.
- Optional comment identity anonymization and explicit raw-comment inclusion.
- Schema, tool, environment and collection provenance in the manifest.
- Coverage, lint, type, dependency and package-build CI checks.

### Security

- Treat metadata and transcript strings as Excel text to prevent formula execution.
- Build ZIP archives through verified temporary files before publishing them.
- Refuse to overwrite existing transcript files unless `--force` is supplied.

### Changed

- Raw comment workbooks are excluded by default and clearly marked when included.
- The minimum supported Python versions are now tested on Windows and Ubuntu.
