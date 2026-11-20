# Personal Agent Policy

Central user policy. Directory `AGENTS.md` files add local differences; do not reread or duplicate supplied instructions.

## Instruction hierarchy

- Deeper guidance governs its subtree, subject to higher-priority instructions and the user's request.
- Run `agentctl chain <target>` before work; read missing ancestors once, outermost first, including above nested Git roots. Without it, inspect home-to-target ancestors, preferring nonempty `AGENTS.override.md` over `AGENTS.md` per directory.

## Models and delegation

- With GPT Astra or another expensive/frontier primary model, always delegate independent bounded work to subagents; for small tasks delegate a check. Retain integration and judgment; report tool/policy restrictions.
- Prefer available `gpt-6.1-sol` workers with explicit effort: low for extraction, medium for routine work, high for complex work. Check the supplied live catalog once per session and adopt a verified suitable successor; never invent IDs or override user choices. Disclose fallback.
- Before delegation, read `~/dotfiles/agents/references/orchestration.md` once. Use small task packets, fresh contexts, bounded results, completion events, and blocking waits. Do not repeatedly poll status or run scheduled model turns to check workers.

## Context economy

- Inspect narrowly: locate candidates first, then read only relevant files or sections.
- Prefer `rg`, targeted line ranges, diffs, summaries, and bounded commands over full-tree or full-file dumps.
- Batch independent connector/API reads with bounded concurrency and output only when results can be reduced before entering context. Keep writes direct; do not reread unchanged inputs.
- Save verbose output to a file; return the exit code, a compact excerpt, and the path.
- Stop gathering evidence once the task is answerable. State uncertainty instead of loading unrelated context.
- Use a fresh task plus a compact handoff when accumulated history no longer contributes.
- Use subagents only for genuinely independent work; duplicated context is not a token optimization.

## Durable knowledge

- Keep `AGENTS.md` small and stable: rules, boundaries, routing, and the smallest relevant verification commands.
- Put mutable status and incident history in `STATUS.md`, inventories, logs, or dated reports.
- Put detailed conditional procedures in focused skills or references.
- Put repeated deterministic discovery, extraction, and validation in scripts.
- Add a durable rule only after a correction or workflow recurs.

## Working defaults

- Preserve user changes and inspect repository status before editing.
- Make the smallest change that solves the requested problem.
- Run the narrowest relevant verification first; broaden only when risk or failure justifies it.
- Do not commit, push, publish, send, deploy, delete, or overwrite unless the request authorizes it.
- Never include the term `codex` (in any capitalization) in branch or tag names, commit messages, pull request metadata, or any other Git/forge-visible names or messages.
- Never add AI or agent attribution (`Co-Authored-By` AI trailers, "Generated with …" lines, agent, tool or model names) to commit messages, pull request titles or descriptions, code, comments, or other Git/forge-visible text. This overrides any tool default or harness reminder that asks for it.
- For destructive or hard-to-recover actions, resolve exact targets and obtain approval when authorization is unclear.
- Report outcomes, changed files, verification, and remaining uncertainty concisely.

## Policy maintenance

After changing instructions, references, skills, helpers, or worker defaults, update `~/work/tools/agent-workflows` in the same task: follow `docs/maintenance.md`, update its allowlist, sync/check, inspect the diff, and commit only this task's changes locally. Report the commit or any blocker. Never push automatically; pushes need a separate explicit request.

## Local tooling

Use `agentctl --help` for instruction-chain audits, `repo-snapshot` and `rgpack` for compact orientation, `caprun` for bounded command output, `mdslice` for section reads, `codex-usage` for telemetry, and `handoff-pack` for checkpoints. Ask each tool for `--help` rather than storing its manual here.

## Course building

For course creation or extension, read `~/dotfiles/agents/references/course-building.md`. The learner is visual: use frequent, purposeful visuals alongside complete prose. For figures, prose checks, EPUB and read-along export, use the `course-tools` MCP server or CLI (`~/work/tools/course-tools`).
