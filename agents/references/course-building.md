# Building courses for a visual learner

Apply this guide when creating or extending courses. Preserve the particular course's learning contract, sequencing, exercise policy and distinction between delivered content and demonstrated understanding.

## Write so the learner can follow on first reading

The learner wants substantial knowledge that is easy to absorb. Both very long lectures and compressed, telegraphic ones have failed them. Set the scene first: who observes what, and what question we are answering. Then write out each reasoning step: what we check, what each explanation predicts, what we see, and what that rules out. Use plain verbs and concrete names instead of abstract nouns ("messages carrying the controller's identifier", not "source-attributed frames"). Use connecting words such as *because*, *so* and *for example*. Introduce at most a few new terms per section, each defined with an example, and keep one running example. Say once that examples are fictional; give an extra caveat only where a reader would otherwise draw a wrong conclusion. Say why each point matters. Keep courses short enough to finish: about 1,000–1,200 words and three ideas per lecture, and a few hours for a whole course (for example, two lectures per module). Shorten by selecting fewer ideas, never by compressing the explanation of an idea you keep, and review short outlines (question, scene, three ideas, figures, what is cut) before writing prose. Check changed lectures with the course-tools prose checker (`check_prose`, or `course-tools prose COURSE --details`; pass `--words 1000-1250` for this length) and reread flagged passages aloud.

## Teach through prose and visuals together

The learner explicitly prefers visual explanations. Use them frequently and deliberately: plan several meaningful visuals through a substantial lecture when its concepts support them, rather than one decorative overview. Show relationships, boundaries, sequences, alternatives, time behavior and uncertainty near the prose that explains them. Select the number by learning value and complexity; do not pad a lecture to satisfy a quota.

The learner reads the lectures rather than listening to them, so a visual may carry content: introduce the question it answers in one line, add at most one sentence on what to notice, and do not repeat in prose what it already shows. Give it an alt text that states its point in one sentence. Use progressive frames or an interactive comparison when revealing successive states aids understanding. Include a static SVG alternative so readers can print, review or read offline.

## Default reusable tooling

Use course-tools (`~/work/tools/course-tools`: MCP server `course-tools`, or `bin/course-tools`) wherever it applies. Lay out the course folder as its `course-layout` guide says, read its `figures` guide once per session, render with `render_figures`, and for a multi-lecture figure pass start `start_figure_pipeline` once instead of per-lecture agents. Without it, draw figures as short text sources in an auto-layout language (D2 or Graphviz for structure and flow, D2 or Mermaid for sequences and states, WaveDrom for signals and bit layouts) or as freehand SVG with a shared stylesheet for timelines, proportions and physical layouts. Keep one house vocabulary of colours and shapes per course, and put meaning in geometry rather than in sentences inside boxes. Comparisons and vocabularies belong in Markdown tables, not figures.

Keep sources beside the course (`visuals/src/`) and generated SVG separate. Edit the source, not the SVG. Check layout from text output where the tooling reports it, and look at rendered images once per lecture through a low-resolution contact sheet rather than per figure. Embed SVG with meaningful alt text beside the relevant paragraph.

Select the representation for the question: directed graphs for flow/dependence, trees for actual hierarchies, state transitions for permitted changes, sequences for message order, numeric timelines for elapsed time, layers for responsibilities, comparisons/matrices for alternatives, charts for real numerical relationships, and steps for a developing explanation. Do not imply causality from placement or chronology. Use standard scientific plotting or specialized domain tools when the figure tooling cannot faithfully express the material.

## Review meaning before beauty

State whether a visual is conceptual, illustrative, measured or modelled. Cite measured evidence and explain model assumptions. An illustrative robot, timeout, dataset or architecture must not appear verified by rendering it professionally. Match arrows and boundaries to the prose; distinguish observations, hypotheses, assessments and decisions. Label units, time origins, scales and missing data. Describe what uncertainty intervals mean. Keep quantitative geometry faithful; never shorten an axis or smooth data merely to create a stronger story.

Inspect for omitted data, wrong direction, ambiguous ownership, accidental deployment claims, illegible labels, clipping and misleading color semantics. Use labels, shapes, markers or line patterns alongside color. Check text/data alternatives and static fallbacks. Structural validation catches input mistakes; it does not establish factual truth or certify accessibility.

If a visual is too dense, divide the teaching into several coherent views with explicit links between them. Preserve the source specification and rebuild after conceptual corrections so prose and diagrams stay aligned.

## Exports

The learner reads on a Kobo: export books with `build_epub` and `kobo`, and narrated pages with `build_read_along` when asked to listen. A routine export only runs the export. It does not reread or rewrite lectures, regenerate existing figures, redraw an existing cover, or update learning progress. Draw a cover once for a course that has none, following the cover style in the course-tools `epub` guide.
