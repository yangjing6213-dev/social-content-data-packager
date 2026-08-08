# Installation

## Runtime

Use Python 3.10 or newer. Python 3.10–3.12 is the supported range for local Whisper transcription.
Install FFmpeg/FFprobe when validating or transcribing video.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e "."
```

For development checks:

```powershell
python -m pip install -e ".[dev]"
```

The in-progress browser collector is excluded from the current release candidate. If developing it locally,
install `.[browser]` and use a user-created isolated Edge/CDP profile. Complete login, CAPTCHA and
authorization yourself; never commit the profile or cookies.
