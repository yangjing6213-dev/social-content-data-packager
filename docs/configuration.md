# Configuration

The core CLI accepts workspace paths and command-line options; it does not require committed secrets.
Use `.env.example` only as a documented placeholder reference. Never copy real values into it or commit
`.env` files.

Key options include `--model`, `--language`, `--initial-prompt`, `--anonymize-comments` and
`--include-raw-comments`. Inspect `social-content-packager <command> --help` for the installed version.
The in-progress browser collector requires an already authorized local CDP endpoint and is excluded from
the current release candidate. It must remain within the target platform's terms and the user's authorization.
