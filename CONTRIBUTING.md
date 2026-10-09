# Contributing to TwitchMiner

Thanks for helping out. TwitchMiner is a fork of Twitch Channel Points Miner v2 (see [Credits and license](README.md#credits-and-license)), and contributions are welcome: bug reports, fixes, documentation and new features.

By contributing you agree that your changes are released under the project's license, the **GNU General Public License v3.0** (see [LICENSE](LICENSE)).

## Before you start
- Look through the existing [issues](https://github.com/Poag/TwitchMiner/issues) and [pull requests](https://github.com/Poag/TwitchMiner/pulls) to see whether someone is already on it.
- For anything bigger than a small fix, open an issue first to agree on the approach.
- Keep changes focused: one fix or feature per pull request.

## Project layout
```
TwitchChannelPointsMiner/
  __main__.py, config.py     start-up: builds the miner from TCPM_* environment variables
  paths.py                   the single data folder (TCPM_DATA_DIR) and its subfolders
  TwitchChannelPointsMiner.py  the miner (sessions, websockets, drops/minute-watched threads)
  classes/                   Twitch API client, websockets, notifiers, analytics server, drops database
  classes/entities/          Streamer, Stream, Drop, Campaign, ...
assets/                      analytics web page (charts.html, style.css, script.js) and icon
compose.yaml, Dockerfile     container build and example stack
.env.example                 every setting with its default
```
Configuration is **environment variables only** (prefix `TCPM_`). If you add or change a setting, update `config.py`, `.env.example` and the README settings tables together. Everything the miner writes goes under `TCPM_DATA_DIR` (`cookies/`, `database/`, `logs/`, `analytics/`); use `paths.subdir()` instead of building paths yourself.

## Development setup
TwitchMiner is only supported as a Docker container. Running it from source below is for development; please reproduce bugs in Docker before reporting them.

1. Fork the repository and clone your fork.
2. Create a virtualenv and install the requirements (Python 3.12 is what the Docker image uses):
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Configure and run it:
   ```sh
   cp .env.example .env      # set TCPM_USERNAME and TCPM_STREAMERS at least
   set -a; . ./.env; set +a
   python -m TwitchChannelPointsMiner
   ```
   Use a throw-away data folder while developing, for example `export TCPM_DATA_DIR=/tmp/tcpm-dev`, so you don't touch a real login.
4. To work on the analytics page, set `TCPM_ENABLE_ANALYTICS=true` and open <http://127.0.0.1:5000/>. The assets in `assets/` are served as they are, so reload the browser (Flask caches the HTML template, so restart the miner after editing `charts.html`).

### Docker
```sh
docker build -t twitchminer .
docker run -it --env-file .env -v $(pwd)/data:/data -p 5000:5000 twitchminer
```
Images are built and published by [.github/workflows/docker-publish.yml](.github/workflows/docker-publish.yml) on every push to `main` (`amd64` and `arm64`, rebuilt monthly). The Dockerfile has no compilers: if you add a dependency, make sure it ships wheels for both architectures.

## Code style and checks
- Formatting and linting are set up with [pre-commit](https://pre-commit.com/) (`isort`, `black`, `flake8`, trailing whitespace). Run it on the files you change:
  ```sh
  pip install pre-commit
  pre-commit install
  ```
- There is no automated test suite yet. Before opening a pull request, at least:
  - `python -m py_compile` the Python files you changed, and start the miner against your own account to exercise the code path you touched;
  - for settings, check that bad values stop start-up with a clear message (see `config.py`);
  - for the analytics page, check light and dark mode and that it still works with no data.
- Tests for new logic are very welcome.
- Don't commit secrets, cookies, logs or anything from a data folder (`data/` and `.env` are gitignored).

## Pull requests
1. Create a branch from `main` in your fork.
2. Commit with clear messages that say what changed and why.
3. Open the pull request against `main` and fill in the [pull request template](.github/PULL_REQUEST_TEMPLATE.md): what changed, how you tested it, and whether it breaks existing setups.
4. Review your own diff first, and update the README and `.env.example` if behaviour or settings changed.
5. Expect review comments. Push follow-up commits to the same branch, and resolve conversations as you address them.

## Reporting bugs
Open an issue using the bug report template. Please include the version (shown on the first log line), how you run it (Docker, compose, Unraid, plain Python), the relevant log lines, and your `TCPM_*` settings **without passwords or tokens**.

## Questions about Twitch behaviour
The miner uses Twitch's unofficial web endpoints, which change without notice. If something that used to work stops (a drop, a bonus, a whole feature), say what you saw in the logs; removing support for features Twitch has retired is a welcome contribution.
