# Economical agent orchestration

Read once before delegation. Current tool contracts and higher-priority instructions govern.

## Dispatch

- Reuse the live model catalog supplied in tool documentation, or query it once if absent. Refresh only on availability failure, a changed catalog, or a new session. Verify a successor's role and supported effort; newer is not automatically better. Consult official docs if unclear. Preserve user model choices and disclose fallback. Static defaults are not an automatic updater.
- Prefer `gpt-6.1-sol`: low for extraction, medium for routine work, high for complex work; justify higher effort. Pass model and effort explicitly. Prefer `fork_turns="none"` for independent workers; full-history forks currently inherit the parent's model and cannot override it.
- Give each worker an objective, relevant facts and policies, exact file ownership, constraints, acceptance check, and result budget. Workers discover their applicable directory instructions. Avoid copied chat history, overlapping edits, duplicated research, and agents created merely to poll others.
- Ask for prompt blocker reports and one final result, normally at most 200–400 words: outcome, paths, verification, risks, and decisions needed. Store detailed evidence in files. Do not request routine progress reports. Retain parent integration and judgment.

## Wait and integrate

1. Dispatch bounded independent work, then do useful parent work without duplicating it.
2. Consume automatic completion notifications. When blocked, use `collaboration.wait_agent` for subagents, or cursor-based `wait_threads` for separately authorized chats. Do not create user-owned chats solely as workers.
3. Use the longest wait allowed by current responsiveness rules and deadlines (currently at most 60 seconds per blocking call). After an unchanged timeout, re-wait with minimal reasoning. Avoid list/status/history polling and narration of unchanged polls; still honor required user progress updates.
4. Inspect status only for an actionable ambiguity, error, deadline, or missing result. Read the relevant result once. A timeout is not worker failure; do not restart work solely because no result arrived. Wait for required results, integrate, and run the narrow relevant check.

## External jobs and measurement

Do not schedule an LLM turn merely to check worker status. A quiet scheduled chat still runs a model. Native waits suspend active reasoning, but repeated wake-ups can cost inference; do not promise zero tokens or billing savings. Measure parent tokens, total tokens, latency, and correctness separately. More workers can increase total usage.

For an authorized external workflow, prefer a deterministic supervisor waiting on process exit, webhook, or a documented completion event. Persist IDs, deduplicate/batch events, and wake a model only for a decision or synthesis. Cron polling of machine-readable external state is a fallback when events are unavailable. Do not install a timer, scrape private session databases, or assume an interface can wake an existing desktop chat. Instructions cannot fix the client's wait implementation.

Research, sources, and integration limits: `~/work/tools/agent-workflows/docs/orchestration-research.md`. Read only when evaluating the design or building an external supervisor.
