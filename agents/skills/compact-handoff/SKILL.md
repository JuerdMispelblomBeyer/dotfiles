---
name: compact-handoff
description: Create a compact, evidence-based checkpoint for continuing work in a fresh task or agent without carrying the full transcript. Use when the user asks for a handoff, continuation note, or context reset.
---

# Compact handoff

1. Run `handoff-pack [path]` to capture repository, branch, dirty files, diff statistics, and active guidance.
2. Add only task facts that cannot be reconstructed cheaply: objective, completed work, verification, blockers, and next action.
3. Link exact files or logs instead of pasting their contents.
4. Exclude conversation history, abandoned speculation, verbose command output, and already-resolved alternatives.
5. Verify the checkpoint against current Git status and test evidence.

Keep the checkpoint below 1,500 words unless the task has multiple independent workstreams that genuinely require more.
