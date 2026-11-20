# Dotfiles overlay

This file extends the user-level policy at `~/.codex/AGENTS.md`, which Codex loads automatically. Do not reread or duplicate it.

- This repository is the canonical source for linked user configuration.
- Patch the narrow source file under this repository; do not edit a generated backup or replace an unrelated dirty setting.
- Preserve existing user changes and inspect `git diff` before modifying shared shell, SSH, Codex, or Claude configuration.
- Add home-directory links through `tools/link_configs.sh`; keep it idempotent and backup-preserving.
- Validate JSON/TOML and shell syntax before running the linker.
- Agent policies, adapters, skills, and bounded helper commands live under `agents/`.
- Codex profiles live next to `codex/config.toml` and are selected with `codex --profile <name>`.
