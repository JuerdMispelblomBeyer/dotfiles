---
name: agent-infrastructure
description: Maintain or audit the machine's central AGENTS.md hierarchy, agent adapters, skills, helper scripts, profiles, or instruction budgets. Use for explicit agent-configuration and context-efficiency changes; do not use for ordinary repository work.
---

# Agent infrastructure

1. Run `agentctl chain <target>` and `agentctl lint <target>` before changing guidance.
2. Keep the user-level policy tool-neutral, stable, and compact; use the existing 5 KB central-policy warning budget.
3. Keep overlays limited to local boundaries, routing, and verification. Never import the central policy in Codex overlays because Codex already concatenates it.
4. Move mutable state to `STATUS.md`, detailed conditional procedures to references or focused skills, and deterministic work to scripts.
5. Preserve dirty worktrees and existing settings. Patch specific keys rather than replacing configuration files.
6. Validate with `agentctl lint`, skill validation, config parsing, and a fresh instruction-discovery run.
7. For material tuning, compare `codex-usage` on comparable workloads when available; distinguish expensive-parent usage from total tokens and do not claim unmeasured savings.
8. Follow `~/work/tools/agent-workflows/docs/maintenance.md` to synchronize changed instructions, skills, helpers, and workflow defaults into the portable mirror and verify its diff. Automatically commit only the verified task changes in that mirror; this does not authorize commits in source repositories. Never push automatically; a push needs a separate explicit user request.

Do not raise instruction size limits to accommodate avoidable prose. Treat 12 KB effective guidance as a warning and 16 KB as a failure unless a measured exception is documented.
