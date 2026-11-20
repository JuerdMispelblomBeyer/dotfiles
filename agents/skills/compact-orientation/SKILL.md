---
name: compact-orientation
description: Orient in an unfamiliar repository or workspace with bounded context using instruction-chain, Git, manifest, and targeted-search summaries. Use for repository mapping and finding likely files; do not use when the exact file is already known.
---

# Compact orientation

1. Run `repo-snapshot [path]` once.
2. Use `agentctl chain <path>` if instruction precedence needs more detail.
3. Search with `rgpack <pattern> [paths...]`; narrow by directory or file type before expanding limits.
4. Read only required Markdown sections with `mdslice <file> <heading>`.
5. Inspect candidate files in targeted ranges. Do not dump the repository tree or every manifest.
6. Stop once entry points, relevant rules, and the smallest verification command are known.

If a bounded tool reports omitted results, expand one limit deliberately and explain why.
