# Fortytwo for Goose

[![Discord](https://img.shields.io/badge/discord-join-7289da)](https://discord.gg/fortytwo)
[![X Fortytwo](https://img.shields.io/twitter/follow/fortytwo?style=social)](https://x.com/fortytwo)

Adds [Fortytwo](https://fortytwo.network) as a model provider to [Goose](https://github.com/aaif-goose/goose). After install, Fortytwo appears in the provider list, with streaming, tool calls, image input and reasoning.

API reference: [OpenAI compatibility](https://docs.fortytwo.network/docs/openai-compatibility) in the Fortytwo docs.

Tested with Goose CLI and Desktop 1.57.0.

Fortytwo is installed as a custom provider; it is not bundled with Goose.

## Install

Install Goose first, then download the provider definition.

macOS / Linux:

```sh
mkdir -p ~/.config/goose/custom_providers
curl -fsSL https://raw.githubusercontent.com/Fortytwo-Network/fortytwo-goose/main/fortytwo.json \
  -o ~/.config/goose/custom_providers/fortytwo.json
```

Windows PowerShell:

```powershell
$providerDir = Join-Path $env:APPDATA 'Block\goose\config\custom_providers'
New-Item -ItemType Directory -Force $providerDir | Out-Null
Invoke-WebRequest 'https://raw.githubusercontent.com/Fortytwo-Network/fortytwo-goose/main/fortytwo.json' `
  -OutFile (Join-Path $providerDir 'fortytwo.json')
```

Restart Goose Desktop after copying the file. To remove the provider, delete `fortytwo.json` from that directory.

## Add your API key

Create a key on the [API keys](https://platform.fortytwo.network/api-keys) page of the Fortytwo Platform, then use one of these:

- In Goose Desktop, select **Fortytwo** in the provider list and enter your key in its configuration form.
- Or set an environment variable before you start Goose:

  ```sh
  export FORTYTWO_API_KEY="your-api-key"
  ```

  In Windows PowerShell:

  ```powershell
  $env:FORTYTWO_API_KEY = 'your-api-key'
  ```

Desktop launched from Finder does not inherit a terminal's environment variables. Do not put your key in `fortytwo.json`.

## Select the model

In Goose Desktop, choose **Fortytwo** and `qwen/qwen3.8-27b`. From the command line:

```sh
goose run --provider fortytwo --model qwen/qwen3.8-27b --text 'Say hello.'
```

For interactive configuration, run `goose configure`, select **Configure Providers**, then **Fortytwo** and `qwen/qwen3.8-27b`.

## Models

| Model ID | Name | Context (tokens) | Max output (tokens) | Input | Input price (USD / 1M tokens) | Output price (USD / 1M tokens) | Cached input price (USD / 1M tokens) |
|---|---|---|---|---|---|---|---|
| `qwen/qwen3.8-27b` | Qwen3.8 27B | 262,144 | 235,929 | text, image | 0.425 | 2.55 | 0.085 |

Current models: [Models](https://docs.fortytwo.network/docs/models). Current prices: [Pricing](https://docs.fortytwo.network/docs/pricing).

The JSON declares prices per token and uses a static model list. PNG and JPEG are documented image formats.

## Reasoning

Goose displays Fortytwo reasoning separately from the answer. Reasoning tokens count against the output limit.

With `preserves_thinking: true`, Goose replays thinking as `reasoning_content`. Fortytwo accepts that field but does not use it to restore reasoning state.

## Environment variables

| Variable | Meaning |
|---|---|
| `FORTYTWO_API_KEY` | API key, sent as the Bearer token. Not needed if you configured credentials in Goose |
| `GOOSE_PATH_ROOT` | Optional absolute directory for an isolated Goose profile. Install the JSON under its `config/custom_providers/` directory |

## Attribution

The definition sends `http-referer: https://goose-docs.ai` and `x-title: goose`; Goose also adds `agent-session-id`. These attribution names remain provisional. Local wire tests confirm delivery, but backend agreement and server-side recording are still unverified.

## Troubleshooting

- **Fortytwo is not in the provider list.** Check the installation path and restart Goose. If `GOOSE_PATH_ROOT` is set, use that profile's `config/custom_providers/` directory.
- **Authentication fails.** Check that the key is available to the process running Goose, or enter it in Desktop's provider configuration.
- **Other problems.** See [Common problems](https://docs.fortytwo.network/docs/support-common-problems) or ask on [Discord](https://discord.gg/fortytwo).

## Development

Run the wire test with an installed Goose binary:

```sh
python3 tests/test_wire.py /absolute/path/to/goose
```

It uses a local mock and a dummy key; it makes no paid requests. Live checks call the production API and need a test key and an isolated Goose profile. See [verification.md](verification.md) for results and remaining upstream listing gates.

## License

[MIT](LICENSE)
