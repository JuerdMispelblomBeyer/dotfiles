# Courseviz

Small, reviewable JSON specifications become consistent SVG diagrams and offline HTML learning aids. A specification owns the meaning; renderers own geometry; themes own appearance. Reuse a template and edit labels/data rather than generating drawing code or loading a visualization framework into every teaching conversation.

## Quick start

```sh
courseviz catalog
courseviz template flow > evidence.json
# Edit the JSON, including its description and epistemic status.
courseviz validate evidence.json
courseviz render evidence.json --out visuals
courseviz render evidence.json --out visuals --name evidence-dark --theme midnight
courseviz examples --all-themes --out /tmp/courseviz-gallery
```

Open the resulting HTML in a browser, embed the SVG in a lecture, and retain the source JSON. HTML includes an expandable text/data alternative, specification, actual-size view and print control. A `steps` visual adds keyboard-accessible previous/next buttons; its SVG presents every frame in order. No server, network, CDN, telemetry, build service or Python package dependency is needed. Graph diagrams use the local Graphviz `dot` executable. Optional raster/PDF export uses Node + Playwright + its Chromium browser.

```sh
courseviz doctor
courseviz export visuals/evidence.html --out visuals/evidence.png
courseviz export visuals/evidence.html --out visuals/evidence.pdf
```

Export only trusted generated HTML. The exporter blocks remote requests but is not a sandbox for arbitrary local HTML. For large diagrams, SVG is the preferred master; PDF pagination uses browser print layout. Export is optional and reports missing dependencies rather than installing anything. `NODE_PATH` may point to an existing Playwright installation; `COURSEVIZ_CHROMIUM` may select an existing compatible browser executable. No machine-specific runtime paths are baked into the tool.

## Choose a visual for the question

| Question | Kind | Essential meaning |
|---|---|---|
| What depends on what? | `dependency`, `tree`, `mindmap` | Explicit directed edges; tree/mindmap enforce one rooted tree |
| Where are the responsibilities and interfaces? | `architecture`, `layers` | Grouping and boundaries, not accidental physical deployment claims |
| What can happen next? | `flow`, `state` | Branches or transitions with labels and state entry |
| Who exchanges what, in which order? | `interaction` | Ordered participants and messages; no elapsed-time claim |
| What are the successive stages? | `sequence` | Explicit ordered steps, not a time axis |
| When did it happen? | `timeline` | Proportional numeric time axis and explicit unit |
| How do alternatives differ? | `comparison`, `matrix`, `cards` | Explicit categories/criteria; no implied numerical score |
| How large are values? | `bar` | Zero baseline, signed values, named series |
| How does a quantity change? | `line`, `area` | Numeric x positions; gaps remain gaps; area includes zero |
| How are two quantities related? | `scatter` | Independent point positions; no automatic causal claim or fitted trend |
| What is uncertain? | `interval` | Named intervals with low ≤ estimate ≤ high; define what the interval represents |
| How does a grid of values vary? | `heatmap` | Numeric scale, visible values, missing cells distinguished |
| How can the reader build understanding gradually? | `steps` | 2–12 complete visual frames; offline HTML controls and full static SVG |

Use `courseviz template KIND` for the exact schema and a working example; [formats.md](formats.md) explains fields and constraints. There are five themes: paper, midnight, blueprint, warm and mono. Themes change colors and surfaces only. Use consistent themes within a course and labels/line styles as well as color. Templates contain illustrative values, never evidence from a deployed system.

## Batch builds and reproducibility

Keep authored specifications separate from generated assets:

```text
visuals/
  specs/claim-chain.json
  specs/information-roles.json
  manifest.json
  generated/
```

```json
{
  "version": 1,
  "title": "Module 1 visual companion",
  "theme": "paper",
  "visuals": [
    {"file": "specs/claim-chain.json"},
    {"file": "specs/information-roles.json", "name": "roles", "theme": "warm"}
  ]
}
```

`courseviz build visuals/manifest.json --out visuals/generated` validates the batch, renders only changed items, and writes a searchable `index.html`. Cache keys include normalized input, renderer source and Graphviz version. Output checksums detect manual changes or corruption. `--force` bypasses reuse. The per-visual `.build.json` is derived cache metadata; it can be ignored in version control. No timestamps enter generated output. Graphviz/font differences can change layout across machines, so pin their versions when byte-identical cross-machine output is required. Validation runs even on a cache hit. Existing unrelated files are never cleaned; remove obsolete assets deliberately. A failed renderer may leave earlier successful outputs from the batch, but it does not replace the gallery until every visual succeeds.

## Correctness contract

The tool checks schemas, types, IDs/references, graph/tree invariants, finite numbers, interval bounds, chart domains and baselines. It escapes text, checks generated SVG for external resources/scripts, limits input sizes, and refuses diagrams too dense for readable graph layout. Long labels wrap. Some chart/layout fields have explicit limits; split an overloaded visual rather than defeating those checks. See the format guide for limits.

It **cannot prove** that a claim, arrow, unit, assumed independence, measurement, model or source is true. Authors must review these against the lesson and evidence. A graph edge may represent data flow, control, dependence or causality: explain which. A timestamp needs an origin/clock interpretation. An interval needs its statistical or engineering meaning. Geometry must never lend certainty to a hypothesis or make an architectural sketch look like an audited deployment.

Every spec requires a descriptive text alternative and `status`: `conceptual`, `illustrative`, `measured` or `modelled`. Measured data also requires a source. Give model assumptions and provenance in description/caption/source. The tool does not infer or invent them. Text alternatives expose original data, not pixel coordinates. Screen-reader usability still deserves human testing; automated validation is not an accessibility certification.

## Efficient authoring loop

1. State the learning question and the one relationship the reader should see.
2. Ask for one template, not the entire toolkit source. Edit semantic fields only.
3. Validate, render, and inspect at the intended reading size. Check every edge/direction and label, units, ordering, missing data, bounds and caption.
4. Embed the SVG beside the relevant prose; link the HTML when interaction adds value. Keep enough prose that the lesson still works aloud.
5. Rebuild after a spec change; use a theme override for appearance. Reuse vocabulary and templates across lectures.

For publication-grade scientific plots, geospatial maps, 3-D geometry, mathematical typesetting or specialized domain notation, use a suitable standard plotting/domain tool and keep its reproducible source beside the result. Do not approximate those semantics with a visually similar Courseviz type. Courseviz deliberately accepts no arbitrary code, expressions, raw DOT or remote images in its specifications.

## Development and extension

Python 3.11+. Run from this directory with `python3 -m courseviz`; run `python3 -m unittest discover -s tests`. The shared command resolves its installation through its own real path. Modules:

- `svg.py`, `themes.py`: escaped primitives and presentation tokens.
- `graphs.py`, `layouts.py`, `charts.py`: type-specific validation and rendering.
- `core.py`: shared contract, accessible SVG/HTML and progressive frames.
- `cli.py`: templates, explicit manifests, deterministic caching and atomic file writes.
- `export.cjs`: optional browser export, isolated from the core.

To add a kind, implement `validate(spec)`, `render(spec, theme) -> (width, height, svg_body)` and `templates()` in a backend; register its `KINDS`. A new backend also joins `core.BACKENDS`. Add semantic tests, hostile-input tests, a working template and format documentation. Test all five themes and visually inspect small/large/long-label cases. No renderer may silently drop data, change units, invent precision, truncate labels, or apply a transformation without exposing it in the specification.

The general authoring policy is [course-building.md](../../references/course-building.md) in the live installation.

Design references: [Graphviz layered directed layout](https://graphviz.org/docs/layouts/dot/) and [W3C guidance on text alternatives for complex images](https://www.w3.org/WAI/tutorials/images/complex/).
