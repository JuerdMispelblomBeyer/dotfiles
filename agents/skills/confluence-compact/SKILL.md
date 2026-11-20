---
name: confluence-compact
description: Reduce token use for Atlassian Confluence retrieval with search-first routing, bounded programmatic batches, and projected page evidence. Use when searching Confluence, reading or comparing multiple pages, inspecting a page hierarchy or space, extracting known sections, or fetching current bodies before an authorized update. Do not use for Jira-only work.
---

# Confluence Compact

Retrieve the smallest evidence set that can answer the task. Keep raw page bodies inside the tool runtime when deterministic extraction can reduce them safely.

## Route the task

1. If one known page is sufficient, fetch it directly.
2. If the relevant pages are unknown, search first. Return at most 10 candidates with only ID/ARI, title, URL, and a short snippet.
3. If 2–8 known pages can be read independently and the task needs metadata, named sections, exact terms, links, dates, or other deterministic fields, use one programmatic batch.
4. If more than 8 pages are plausible, process batches of 4–6 and stop as soon as the evidence is sufficient. Never fetch an entire space by default.
5. If each page requires fresh semantic judgment, use direct staged reads. Batching alone does not justify returning every full body.

Prefer natural-language Atlassian search for discovery unless the user explicitly supplies CQL or the task needs an exact CQL filter. Use page descendants or pages-in-space only for structural questions, always with explicit `depth` and `limit`.

## Batched read stage

On Codex or another runtime with Programmatic Tool Calling, use it only for the bounded read-and-reduce stage. Read [references/programmatic-confluence.md](references/programmatic-confluence.md) before composing it.

If the agent has only native parallel tool calls, apply the same concurrency and stopping limits but request the narrowest connector fields available. Native batching reduces round trips, not necessarily input tokens, because raw results may still enter context. Prefer a local `cf pack` command when available because it can reduce bodies before returning them.

Required limits:

- Concurrency: at most 6 page reads.
- Retries: at most 1 retry for a transient read failure.
- Emitted content: at most 4,000 characters per page and 16,000 characters total unless the task clearly requires more.
- Output: `pages[]` with `id`, `title`, `url`, `version`, `updated`, `section`, `excerpt`, `sourceChars`, and `truncated`; plus `errors[]`.

Project connector results before calling `text(...)`. Do not emit the original connector envelope, author/account identifiers, ADF, or full bodies unless they are required evidence. Preserve page ID and URL so a final direct validation remains possible.

Use direct calls instead when the result changes which tool should run next, an approval is needed, a write is involved, or native citations/artifacts must be preserved.

## Read and write discipline

- Request Markdown for reading unless storage format or ADF is specifically required.
- Extract a named heading, matching paragraphs, metadata, or a bounded excerpt before returning a page body.
- Deduplicate page IDs before fetching and do not refetch unchanged pages in the same task.
- For quotes, citations, or high-stakes wording, directly refetch only the selected final pages and verify the exact passage.
- Before an authorized update, fetch the current page once and preserve its complete body.
- Perform writes directly and sequentially. Never hide writes inside a programmatic batch.
- Set `includeBody: false` on `updateConfluencePage` unless the returned body is immediately needed.
- After a write, verify only the changed page or returned version; do not reload the space.

## Repository helper

When a repository provides `bin/cf`, prefer `cf overview --brief` for orientation and `cf pack <id>...` for bounded parallel page reads. Ask `cf help` for exact options. Use full `overview`, `tree`, `body`, or `export` only when the smaller commands cannot answer the task.
