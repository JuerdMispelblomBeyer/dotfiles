---
name: token-audit
description: Measure local Codex session input, cached input, output, reasoning, compaction, and tool-result sizes without exposing prompt contents. Use when the user explicitly asks for token telemetry, context-cost diagnosis, or before/after optimization evidence.
---

# Token audit

1. Run `codex-usage report --since 30d` for the baseline.
2. Add `--json <path>` when a machine-readable comparison is needed.
3. Report calls, sessions, input, uncached input, cache rate, output, reasoning, compactions, and largest tool-result categories.
4. Explain that retained session counters are operational telemetry, not billing records.
5. Compare equivalent time windows and task mixes. Do not claim savings from cached-input ratios alone.
6. Treat increased retries, failures, or rediscovery as regressions even if raw input falls.

The tool reads sizes and counters by default. Do not extract prompt bodies, source code, secrets, or command output into the report.
