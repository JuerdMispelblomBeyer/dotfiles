# Specification reference

A visual is one JSON object. Obtain a complete editable example with
`courseviz template KIND > example.json`; run `courseviz validate example.json`
before rendering. This reference describes the fields inside those examples.
Unknown fields are rejected, including fields inside nodes, rows and series.
All kind-specific fields belong under `data`.

## Shared fields

| Field | Required | Meaning |
| --- | --- | --- |
| `version` | Yes | `1`. |
| `kind` | Yes | One of the 20 kinds documented below. |
| `title` | Yes | Nonempty visible heading and accessible SVG title. |
| `description` | Yes | Nonempty plain-text explanation of how to read the visual and what its relationships/numbers mean; included in SVG accessibility metadata and visible HTML. |
| `status` | Yes | `conceptual`, `illustrative`, `measured`, or `modelled`. |
| `data` | Yes | Object with the schema for the selected kind. |
| `theme` | No | `paper` (default), `midnight`, `blueprint`, `warm`, or `mono`. |
| `source` | For measured data | String identifying provenance; must be nonempty when `status` is `measured`. |
| `caption` | No | String appended to the visible status footer. |

`conceptual` describes relationships or ideas; `illustrative` identifies invented
example values; `measured` claims observations with provenance; `modelled`
identifies calculated or simulated results. These declarations do not verify
scientific truth. Explain uncertainty, arrow meanings and units in the description.

Text is literal, escaped text, not HTML, DOT, Markdown, or executable code.
Newlines are supported. Labels wrap; large examples grow vertically or fail with
an instruction to split them. General input limits are 2,000,000 bytes per JSON
file, 24 nesting levels, 12,000 characters per string, 500 fields per object and
10,000 entries per array; kind-specific limits below are usually tighter.
Duplicate JSON object keys and JSON `NaN`/`Infinity` constants are rejected.
Numbers must be finite JSON numbers; booleans and numeric strings are not numbers.

Minimal complete example:

```json
{
  "version": 1,
  "kind": "cards",
  "title": "Preserve evidence",
  "description": "One independent diagnostic habit; card size has no numerical meaning.",
  "status": "conceptual",
  "data": {
    "cards": [{"label": "Observe first", "detail": "Capture the symptom before changing the system."}]
  }
}
```

## Graph kinds

`flow`, `architecture`, `dependency`, `tree`, `mindmap`, and `state` use the
same node/edge schema and require the local Graphviz `dot` executable to render.
Validation itself does not require Graphviz.

| `data` field | Required | Shape and limits |
| --- | --- | --- |
| `nodes` | Yes | Array of 1–36 node objects. |
| `edges` | Yes | Array of 0–72 edge objects. |
| `groups` | No | Array of 0–8 group objects; default `[]`. |
| `direction` | No | `TB` (top to bottom) or `LR` (left to right). Defaults to `TB` for flow/tree/state and `LR` otherwise. |
| `initial` | For some states | Node ID, supported only by `state`; see below. |

Node object: required `id` and `label`; optional `role` and `group`.
IDs start with an ASCII letter, then contain ASCII letters, digits, `_` or `-`,
up to 64 characters total. Node IDs must be unique. Labels contain 1–600
characters of nonblank text. `group` must name a declared group.

Group object: exactly `id` and `label`; labels contain 1–160 characters of
nonblank text. Group IDs must be unique among groups, and every group must have
at least one node. Groups are flat visual boundaries, not nested containers.

Edge object: required `from` and `to` node IDs; optional nonblank `label`
(1–240 characters) and `style` (`solid`, `dashed`, or `dotted`; default `solid`).
Both endpoints must exist. Repeating the same `from`, `to` and label is rejected;
parallel edges with different labels are allowed where the kind's rules permit.
Describe what arrows mean; direction alone does not establish causation.

| Kind | Allowed node roles | Default role | Additional meaning or validation |
| --- | --- | --- | --- |
| `flow` | `process`, `decision`, `start`, `end`, `input` | `process` | Directed process links; decisions use diamonds. No automatic branch semantics or required start/end nodes. |
| `architecture` | `service`, `store`, `external` | `service` | Directed relationships between system elements; groups can show boundaries. |
| `dependency` | `component`, `external` | `component` | Directed links; choose and explain “requires” or another convention. Cycles are permitted. |
| `tree` | `topic` | `topic` | Exactly one root, at most one parent per node, all nodes reachable, no cycles. Edges point parent → child. |
| `mindmap` | `topic` | `topic` | Same rooted-tree validation; links render without arrowheads. Root is inferred from edge direction. |
| `state` | `state`, `initial`, `final` | `state` | Explicit initial state and directed transitions. Final nodes cannot have outgoing edges. |

For `state`, either set `data.initial` or give exactly one node role `initial`.
If both are provided they must select the same node. An initial node cannot also
be final; at most one role `initial` is allowed. The renderer adds an entry arrow.
Other graph kinds reject `data.initial`. Flow and state graphs may contain loops.
A transition label is supplied text; guards and actions have no executable syntax.

Graph `data` fragment:

```json
{
  "direction": "LR",
  "nodes": [{"id": "observe", "label": "Observe"}, {"id": "test", "label": "Test"}],
  "edges": [{"from": "observe", "to": "test", "label": "Form a prediction"}]
}
```

Rendering is bounded to 15 seconds and 2 MB of Graphviz output. Layouts that
would reduce 17-unit graph text below 13 units are rejected: try `TB`, shorter
labels, or separate views. Nodes are positioned by Graphviz, not input coordinates.

## Teaching layouts

These layouts require all fields listed below. `interaction` additionally allows
an optional message `style`; the other teaching layouts have no optional fields. A **teaching item** is exactly
`{"label": "…", "detail": "…"}`: nonblank strings with at most 180 label
characters and 1,200 detail characters. Colors do not encode quantities.

| Kind | `data` fields | Meaning and limits |
| --- | --- | --- |
| `interaction` | `participants`, `messages` | Participant lifelines and ordered directed messages; details below. |
| `sequence` | `steps` | Array of 2–12 teaching items. Supplied order is numbered, linked and marked START/END; spacing does not encode duration. |
| `timeline` | `unit`, `start`, `end`, `events` | Numeric time positions on a proportional linear axis; details below. |
| `layers` | `order`, `layers` | `order`: nonblank explanation of the vertical order, up to 240 characters. `layers`: 2–12 teaching items, top first. Bands show boundaries; heights do not encode size, duration or containment. |
| `comparison` | `columns`, `rows` | 2–4 unique column labels; 1–16 criterion rows. Complete qualitative comparison; details below. |
| `matrix` | `columns`, `rows`, `values`, `row_axis`, `column_axis` | Complete text matrix with explicit axes; details below. |
| `cards` | `cards` | 1–12 teaching items. Independent ideas, one column for a single card and two columns otherwise. Placement does not imply rank. |

### Interaction

`participants` contains 1–6 objects, each exactly `{"id": "…", "label": "…"}`.
IDs are unique nonblank strings of at most 64 characters; labels are nonblank
strings of at most 180 characters. Participants appear left to right in input
order, each with a named header and a dashed vertical lifeline.

`messages` contains 1–16 objects with required `from`, `to`, `label`; optional
`style` is `solid` (default) or `dashed`. Both endpoints must reference participant
IDs. Message labels are nonblank strings of at most 240 characters. Self-messages
are supported by giving the same sender and receiver. Numbered messages appear
in input order from top to bottom; arrowheads point to receivers. Vertical
spacing conveys order only, never elapsed time. Explain the meaning of dashed
messages in the description; no response semantics are inferred from style.

Example message: `{"from": "client", "to": "service", "label": "Request findings"}`.
Use `sequence` for ordered process steps and `interaction` for exchanges among
participants.

### Timeline

`unit` is nonblank text of at most 60 characters. `start` and `end` are finite
numbers with `start < end`; their difference must also be finite. Units are
literal text, with no automatic date parsing or conversion.

`events` contains 1–16 objects, each with exactly `at`, `label`, `detail`.
Label/detail limits are those of teaching items. `at` must be finite and within
`[start, end]`. Events must already be in ascending `at` order; equal times are
allowed and retain equal positions. One row per event avoids collisions without
moving close events apart. The shared axis shows numeric endpoints; intermediate
guides are equally spaced in the same numeric domain.

```json
{"unit": "min", "start": 0, "end": 60, "events": [
  {"at": 0, "label": "Symptom", "detail": "The first observation."},
  {"at": 45, "label": "Verified", "detail": "The original scenario succeeds."}
]}
```

### Comparison and matrix

`comparison.columns` contains 2–4 distinct nonblank strings, each at most 180
characters. Each `rows` entry is exactly `{"label": "…", "values": ["…", "…"]}`.
Row labels are distinct, nonblank and at most 180 characters. Every row must
contain exactly one value per column. Values are nonblank strings of at most
900 characters; missing values, numeric values and `null` are rejected.

`matrix.columns` contains 1–4 distinct labels; `matrix.rows` contains 1–16
distinct labels. These labels and both axis titles are nonblank strings of at
most 180 characters. `values` is a row-major array: exactly one array per row,
with exactly one nonblank string per column, at most 900 characters per cell.
Use `heatmap` for numerical cells. Write “Unknown” explicitly when that is the
meaning, rather than leaving a blank intersection.

## Quantitative charts

`bar`, `line`, `scatter`, `area`, `heatmap`, and `interval` accept only supplied
values and linear scales. There are no log scales, automatic aggregation,
interpolation models, smoothing, stacking, date parsing, or unit conversion.
Chart numeric magnitudes must be at most `1e150`; rescale units for larger data.
Integer values that cannot be represented exactly as a floating-point number
are rejected. Categorical labels and series names must be distinct after
whitespace normalization (trim and collapse runs of whitespace).
Chart labels (axis titles, series names, categories and item labels) are nonblank
strings of at most 240 characters.

**Ranges:** optional `x_range`, `y_range`, and `scale_range` are two-number arrays
`[minimum, maximum]` with strictly increasing endpoints. They must encompass all
corresponding values; values are never silently clipped. Bar/area `y_range`
must additionally encompass zero. Automatic ranges use the minimum and maximum
of the supplied values, including zero for bar/area. A nonzero constant domain expands by 10% on each side, using adjacent
representable floats when necessary; an all-zero domain becomes `[-1, 1]`. Axes propose five equally spaced ticks; coincident intermediate floating-point
ticks are removed.

**Display precision:** supplied values in tooltips, interval annotations and
heatmap cells use shortest round-trip floating-point text. Tick labels use
adaptive precision so distinct tick values remain distinguishable. For a tiny
range relative to a large offset, an explicit note such as “X axis: Add … to tick
labels” identifies an offset; displayed ticks then show residuals. The mapping
still uses the original numeric values. The HTML text/data alternative and
`.spec.json` retain supplied values. Floating-point resolution still limits
representable differences; rescale units when necessary.

### Bar

Required `data`: `labels`, `series`, `x_label`, `y_label`.
Optional: `y_range`. `x_range` is rejected because x is categorical.

`labels`: 1–24 category strings, in display order. `series`: 1–6 objects, each
exactly `{"name": "…", "values": [number, …]}`. Names must be distinct.
Every series has exactly one numeric value per category. Bars are grouped by
series and encode zero-to-value distance, including negative values. Equal
category spacing does not assert equal numeric distances between categories.

### Line, scatter and area

Required `data`: `series`, `x_label`, `y_label`.
Optional: `x_range`, `y_range`.

`series`: 1–6 objects, each exactly
`{"name": "…", "points": [[x, y], …]}`. Names are distinct; each series has
1–100 points. x is always numeric, so unequal x intervals produce unequal
spacing. At least one numeric y value is required across the chart.

- `line`: x values must be strictly increasing within each series. Points are
  connected with straight segments; `null` y creates a visible gap.
- `area`: same point rules and gaps, with fill between each segment and zero.
  Series overlap transparently; they are not stacked. The y domain includes zero.
- `scatter`: both coordinates must be numeric; points need not be ordered,
  duplicate x positions are allowed, and no connecting lines are drawn.

Example series: `{"name": "Sample A", "points": [[0, 2], [1, null], [4, 5]]}`
is valid for line/area. Include the gap's x coordinate; there is no inferred gap
from absent input rows. Use `bar` for categories rather than inventing numeric x
positions for an ordered category list.

### Heatmap

Required `data`: `rows`, `columns`, `values`, `scale_label`.
Optional: `scale_range`.

`rows`: 1–30 category labels; `columns`: 1–14 category labels.
`values`: row-major numeric matrix with exactly one array per row and exactly
one number or `null` per column. At least one numeric cell is required.
`null` denotes missing data, is excluded from the color domain, and displays
a neutral outlined “Missing” cell; it is distinct from zero. Ragged rows and
omitted cell positions are rejected. `scale_label` names the
quantity and should include units. Both axes are categorical, equally spaced.

Each numeric value is printed and mapped into **five discrete equal-width color
bins** over the numeric scale range. If floating-point boundaries coincide,
fewer bins (1–4) are used and the legend states the actual count. Bins are `[low, high)` except the final bin, which
includes its upper endpoint. There is no between-cell interpolation. A legend
shows all resulting numeric intervals. Numeric cell labels retain round-trip precision.
Use `matrix` for qualitative or mixed textual intersections.

### Interval

Required `data`: `items`, `x_label`. Optional: `x_range`.
`items` contains 1–30 objects, each exactly
`{"label": "…", "value": number, "low": number, "high": number}`.
All three numbers are required, with `low <= value <= high`; equal bounds are
allowed. A dot shows `value`, with whiskers spanning `low` to `high` on a linear
numeric x axis. The item order is categorical. No confidence level, error model,
or distribution is inferred: explain what the supplied bounds mean.

## Steps: progressive teaching panels

`kind: "steps"` requires `data` containing only `frames`, an array of 2–12 objects.
Each frame is exactly `{"label": "…", "spec": {complete visual specification}}`.
Labels have 1–120 characters. Each `spec` includes its own common fields and data;
it can use any kind above but cannot itself be `steps`.

Frames preserve supplied order. HTML provides Previous/Next and Show all controls;
SVG includes all panels in order, and printing shows every panel. The parent's
`theme` overrides each child theme. Child titles, descriptions, status and source
remain meaningful independently; measured children still require provenance.
Use `sequence` for a single diagram of process steps and `steps` for a sequence
of complete diagrams with independently authored content.

## Batch manifest

A manifest is separate from a visual specification. Required fields: `version: 1`
and `visuals` (1–500 entries). Optional fields: `title` (default `Course visuals`)
and `theme`. Each visual entry requires `file`; optional fields are `name` and
`theme`. Paths resolve relative to the manifest. Theme precedence is entry →
manifest → visual specification → `paper`.

`name` defaults to the input file's stem. Names must be unique, contain 1–101
ASCII letters/digits/`_`/`.`/`-`, and start with a letter or digit. Each output
receives `.svg`, `.html`, `.spec.json` and `.build.json`; the batch adds `index.html`.
