# Verification

Tested on 2 November 2026 using official Goose 1.57.0 CLI and Desktop releases on macOS arm64.

| Check | Result |
|---|---|
| Custom provider parsing and Desktop discovery | Passed |
| Live streamed chat and visible reasoning | Passed in CLI and Desktop |
| Live shell tool and matching result | Passed in CLI and Desktop |
| Synthetic PNG recognition and continuation after tool results | Passed in CLI and Desktop |
| Endpoint, authentication, headers and session ID | Passed against a local mock |
| Static model list without network model discovery | Passed against a local mock |
| Thinking replay in assistant `reasoning_content` | Passed against a local mock |

Live checks used a synthetic prompt, a harmless `printf` command and a generated red PNG. Tests used a separate Goose profile. No API keys or production logs are included in this repository.

The final JSON adds zero cache-write pricing to the live-tested configuration. This metadata change passed the local wire test. Prices and model limits were checked against the public Fortytwo documentation.

Run the local test with:

```sh
python3 tests/test_wire.py /absolute/path/to/goose
```

It uses a dummy key and a loopback server, including a tool round trip. It does not call the live API.

## Limits

- Client-side header delivery is verified. Agreement on attribution names and server-side recording remains unverified; the headers are provisional.
- The CLI's interactive `goose configure` could not run in the test PTY. Explicit CLI provider selection and Desktop provider selection were verified.
- This self-serve configuration is not a bundled upstream listing. Goose requires a human-written issue and Ready board status before an upstream implementation or pull request. See [CONTRIBUTING](https://github.com/aaif-goose/goose/blob/main/CONTRIBUTING.md).
