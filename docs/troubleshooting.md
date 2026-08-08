# Troubleshooting

- **Missing command**: activate the virtual environment and install the project editable.
- **Whisper or FFprobe unavailable**: install the optional transcription dependency and FFmpeg/FFprobe;
  do not claim transcription or media validation passed without a real run.
- **Non-empty input directory**: choose a new workspace; the collector refuses to overwrite existing
  input files.
- **Login, CAPTCHA or expired page**: complete the authorized action manually in the isolated browser;
  the CLI does not bypass it.
- **Validation failure**: inspect the reported metadata, headers, media streams and transcript segments;
  do not replace them with placeholders.
- **Secret or license finding**: stop, rotate/remediate or obtain authorization, then rerun the complete
  pre-publish audit.
