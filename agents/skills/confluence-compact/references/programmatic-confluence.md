# Programmatic Confluence retrieval

Use this reference only after discovery has produced known page IDs and a deterministic reduction target such as a heading, term set, metadata comparison, or bounded excerpt.

## Connector shape

`getConfluencePage` returns a `CallToolResult`. Its first text block contains JSON with page fields such as `id`, `title`, `version`, `body`, and `webUrl`. Parse that JSON inside the V8 program; return only the projected result.

## Bounded batch pattern

Adapt this pattern to the current tool name and task. The program runtime has no Node.js, filesystem, direct network, or console.

```javascript
const ids = [...new Set(PAGE_IDS)].slice(0, 8);
const perPage = 4000;
const totalLimit = 16000;

function unwrap(result) {
  if (result?.isError) throw new Error("connector returned an error");
  const block = result?.content?.find(x => x.type === "text");
  if (!block?.text) throw new Error("missing text result");
  return JSON.parse(block.text);
}

function project(page) {
  const source = String(page.body || "");
  const selected = REDUCE_BODY(source, page); // heading, terms, or bounded excerpt
  const excerpt = selected.slice(0, perPage);
  return {
    id: String(page.id),
    title: page.title,
    url: page.webUrl,
    version: page.version?.number,
    updated: page.version?.createdAt,
    section: SECTION_OR_NULL,
    excerpt,
    sourceChars: source.length,
    truncated: selected.length > excerpt.length
  };
}

const pages = [];
const errors = [];
let emitted = 0;
for (let start = 0; start < ids.length; start += 6) {
  const chunk = ids.slice(start, start + 6);
  const settled = await Promise.allSettled(chunk.map(pageId =>
    tools.mcp__codex_apps__atlassian_rovo_getconfluencepage({
      cloudId: CLOUD_ID,
      pageId,
      contentFormat: "markdown"
    })
  ));
  for (let i = 0; i < settled.length; i++) {
    const item = settled[i];
    if (item.status === "rejected") {
      errors.push({id: chunk[i], error: String(item.reason).slice(0, 300)});
      continue;
    }
    try {
      const page = project(unwrap(item.value));
      const room = Math.max(0, totalLimit - emitted);
      page.excerpt = page.excerpt.slice(0, room);
      page.truncated = page.truncated || room === 0;
      emitted += page.excerpt.length;
      pages.push(page);
    } catch (error) {
      errors.push({id: chunk[i], error: String(error).slice(0, 300)});
    }
  }
}
text(JSON.stringify({pages, errors}));
```

Replace `REDUCE_BODY` with a deterministic reducer. Good reducers select an exact Markdown heading and its subsections, keep paragraphs containing explicit search terms, or take a short prefix when only orientation is needed. If no deterministic reducer is faithful to the task, do not use this pattern.

## Stop and validation rules

- Do not run a second discovery query after the needed IDs are known.
- Do not repeat successful page reads after a partial batch failure.
- Retry only failed IDs, once, and only for transient errors.
- Do not call create, update, comment, move, archive, or delete tools from the program.
- If the answer needs native citations or exact quotations, direct-fetch the final selected page after reduction.
