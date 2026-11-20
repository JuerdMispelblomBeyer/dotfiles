"""Constrained graph specifications rendered by the local Graphviz executable.

No caller-supplied DOT, attributes, markup, paths, or links are accepted.
"""
from __future__ import annotations

import copy
import math
import re
import shutil
import subprocess
import textwrap
import xml.etree.ElementTree as ET

KINDS = ("flow", "architecture", "dependency", "tree", "mindmap", "state")
_ROLES = {
    "flow": {"process", "decision", "start", "end", "input"},
    "architecture": {"service", "store", "external"},
    "dependency": {"component", "external"},
    "tree": {"topic"}, "mindmap": {"topic"},
    "state": {"state", "initial", "final"},
}
_DEFAULT_ROLE = dict(zip(KINDS, ("process", "service", "component", "topic", "topic", "state")))
_SHAPES = {"process": "box", "decision": "diamond", "start": "oval", "end": "oval",
           "input": "parallelogram", "service": "box", "store": "cylinder",
           "external": "hexagon", "component": "box", "topic": "box",
           "state": "box", "initial": "box", "final": "box"}
_SVG = "http://www.w3.org/2000/svg"
_ID = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,63}\Z")


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _text(value, name, limit=600):
    _require(isinstance(value, str) and bool(value.strip()), f"{name} must be nonempty text")
    _require(len(value) <= limit, f"{name} is too long; use at most {limit} characters")
    _require(all(c in "\t\n\r" or 0x20 <= ord(c) <= 0xD7FF or 0xE000 <= ord(c) <= 0xFFFD
                 or 0x10000 <= ord(c) <= 0x10FFFF for c in value),
             f"{name} contains characters XML cannot display")


def _identifier(value, name):
    _require(isinstance(value, str) and _ID.fullmatch(value),
             f"{name} must start with a letter and contain only letters, digits, _ or - (64 characters maximum)")


def _fields(value, allowed, name):
    _require(isinstance(value, dict), f"{name} must be an object")
    unknown = set(value) - set(allowed)
    _require(not unknown, f"{name} has unsupported fields: {', '.join(sorted(map(str, unknown)))}")


def validate(spec):
    _require(isinstance(spec, dict), "graph specification must be an object")
    kind = spec.get("kind")
    _require(isinstance(kind, str) and kind in KINDS, "unsupported graph kind")
    data = spec.get("data")
    _fields(data, {"nodes", "edges", "groups", "direction", "initial"}, "data")
    _require(data.get("direction", "TB" if kind in {"tree", "flow", "state"} else "LR") in ("LR", "TB"),
             "data.direction must be LR or TB")
    nodes, edges, groups = data.get("nodes"), data.get("edges"), data.get("groups", [])
    _require(isinstance(nodes, list) and 1 <= len(nodes) <= 36,
             "data.nodes must contain 1–36 nodes; split larger graphs into separate views")
    _require(isinstance(edges, list) and len(edges) <= 72,
             "data.edges must be a list with at most 72 edges")
    _require(isinstance(groups, list) and len(groups) <= 8, "data.groups must be a list with at most 8 groups")
    group_ids = set()
    for index, group in enumerate(groups):
        name = f"data.groups[{index}]"
        _fields(group, {"id", "label"}, name)
        _identifier(group.get("id"), name + ".id")
        _text(group.get("label"), name + ".label", 160)
        _require(group["id"] not in group_ids, f"duplicate group id: {group['id']}")
        group_ids.add(group["id"])
    node_ids, initial_roles, used_groups = set(), [], set()
    for index, node in enumerate(nodes):
        name = f"data.nodes[{index}]"
        _fields(node, {"id", "label", "role", "group"}, name)
        _identifier(node.get("id"), name + ".id")
        _text(node.get("label"), name + ".label")
        _require(node["id"] not in node_ids, f"duplicate node id: {node['id']}")
        role = node.get("role", _DEFAULT_ROLE[kind])
        _require(isinstance(role, str) and role in _ROLES[kind],
                 f"{name}.role must be one of {', '.join(sorted(_ROLES[kind]))}")
        if role == "initial":
            initial_roles.append(node["id"])
        if "group" in node:
            _identifier(node["group"], name + ".group")
            _require(node["group"] in group_ids, f"{name}.group does not name a declared group")
            used_groups.add(node["group"])
        node_ids.add(node["id"])
    _require(used_groups == group_ids, "every declared group must contain at least one node")
    seen_edges, children, parents = set(), {n: [] for n in node_ids}, {n: [] for n in node_ids}
    for index, edge in enumerate(edges):
        name = f"data.edges[{index}]"
        _fields(edge, {"from", "to", "label", "style"}, name)
        for endpoint in ("from", "to"):
            _identifier(edge.get(endpoint), name + "." + endpoint)
            _require(edge[endpoint] in node_ids, f"{name}.{endpoint} refers to an unknown node: {edge[endpoint]}")
        if "label" in edge:
            _text(edge["label"], name + ".label", 240)
        _require(edge.get("style", "solid") in ("solid", "dashed", "dotted"),
                 f"{name}.style must be solid, dashed or dotted")
        key = (edge["from"], edge["to"], edge.get("label", ""))
        _require(key not in seen_edges, f"duplicate edge from {key[0]} to {key[1]} with the same label")
        seen_edges.add(key)
        children[edge["from"]].append(edge["to"])
        parents[edge["to"]].append(edge["from"])
    if kind in {"tree", "mindmap"}:
        _require(all(len(p) <= 1 for p in parents.values()), f"{kind} nodes may have only one parent")
        roots = [n for n in node_ids if not parents[n]]
        _require(len(roots) == 1, f"{kind} requires exactly one root and no cycles")
        visited, active = set(), set()

        def visit(node):
            _require(node not in active, f"{kind} must not contain cycles")
            if node in visited:
                return
            active.add(node)
            for child in children[node]:
                visit(child)
            active.remove(node)
            visited.add(node)

        visit(roots[0])
        _require(visited == node_ids, f"{kind} must be connected, reachable from its root, and contain no cycles")
    if kind == "state":
        _require(len(initial_roles) <= 1, "state may have only one node with role initial")
        if "initial" in data:
            _identifier(data["initial"], "data.initial")
            _require(data["initial"] in node_ids, "data.initial must name an existing state")
            _require(not initial_roles or initial_roles == [data["initial"]],
                     "data.initial must agree with the node whose role is initial")
            selected = next(n for n in nodes if n["id"] == data["initial"])
            _require(selected.get("role") != "final", "the initial state cannot also have role final")
        else:
            _require(len(initial_roles) == 1, "state requires data.initial or one node with role initial")
        final_ids = {n["id"] for n in nodes if n.get("role") == "final"}
        _require(not any(edge["from"] in final_ids for edge in edges),
                 "a final state cannot have outgoing transitions")
    else:
        _require("initial" not in data, "data.initial is supported only for state diagrams")


def _quote(value):
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"').replace("\r", " ").replace("\n", "\\n") + '"'


def _label(value, width=22):
    return "\n".join(line for paragraph in value.splitlines() or [value]
                     for line in textwrap.wrap(paragraph, width=width, break_long_words=True, break_on_hyphens=False) or [""])


def _dot(spec, theme):
    data, kind = spec["data"], spec["kind"]
    identifiers = {node["id"]: f"n{i}" for i, node in enumerate(data["nodes"])}
    direction = data.get("direction", "TB" if kind in {"tree", "flow", "state"} else "LR")
    attrs = lambda fields: ",".join(f"{key}={_quote(value)}" for key, value in fields.items())
    output = ["digraph diagram {", "graph [" + attrs({"rankdir": direction, "bgcolor": "transparent", "pad": "0.2",
              "nodesep": "0.35", "ranksep": "0.55", "fontname": theme["font"], "fontsize": "17",
              "fontcolor": theme["ink"], "compound": "true"}) + "];",
              "node [" + attrs({"fontname": theme["font"], "fontsize": "17", "fontcolor": theme["ink"],
              "fillcolor": theme["surface"], "color": theme["ink"], "penwidth": "1.5", "margin": "0.16,0.12"}) + "];",
              "edge [" + attrs({"fontname": theme["font"], "fontsize": "17", "fontcolor": theme["ink"],
              "color": theme["ink"], "penwidth": "1.5", "arrowsize": "0.8"}) + "];"]

    def node_line(node):
        role = node.get("role", _DEFAULT_ROLE[kind])
        label = _label(node["label"], 18 if role == "decision" else 22)
        fields = {"label": label, "shape": _SHAPES[role], "style": "rounded,filled" if _SHAPES[role] == "box" else "filled"}
        if role == "final":
            fields["peripheries"] = "2"
        return identifiers[node["id"]] + " [" + attrs(fields) + "];"

    for index, group in enumerate(data.get("groups", [])):
        output += [f"subgraph cluster_{index} {{", "graph [" + attrs({"label": _label(group["label"], 30),
                   "color": theme["muted"], "style": "dashed", "margin": "18"}) + "];"]
        output += [node_line(n) for n in data["nodes"] if n.get("group") == group["id"]]
        output.append("}")
    output += [node_line(n) for n in data["nodes"] if "group" not in n]
    if kind == "state":
        initial = data.get("initial") or next(n["id"] for n in data["nodes"] if n.get("role") == "initial")
        output += ["entry [shape=point,label=\"\",width=0.12,fillcolor=" + _quote(theme["ink"]) + "];",
                   "entry -> " + identifiers[initial] + ";"]
    for edge in data["edges"]:
        fields = {"style": edge.get("style", "solid")}
        if "label" in edge:
            fields["label"] = _label(edge["label"], 22)
        if kind == "mindmap":
            fields["arrowhead"] = "none"
        output.append(f"{identifiers[edge['from']]} -> {identifiers[edge['to']]} [" + attrs(fields) + "];")
    return "\n".join(output + ["}"])


def render(spec, theme):
    validate(spec)
    executable = shutil.which("dot")
    _require(executable is not None, "Graphviz 'dot' is required for graph diagrams; install Graphviz and retry")
    try:
        result = subprocess.run([executable, "-Tsvg"], input=_dot(spec, theme), text=True,
                                capture_output=True, timeout=15, check=False)
    except subprocess.TimeoutExpired as error:
        raise ValueError("graph layout exceeded 15 seconds; reduce its nodes or edges") from error
    _require(result.returncode == 0, "Graphviz could not lay out this graph; simplify the graph and retry")
    _require(len(result.stdout) <= 2_000_000, "graph output is too large; split the graph into smaller views")
    try:
        root = ET.fromstring(result.stdout)
        x, y, width, height = map(float, root.attrib["viewBox"].split())
    except (ET.ParseError, KeyError, ValueError) as error:
        raise ValueError("Graphviz returned invalid SVG") from error
    _require(all(math.isfinite(v) for v in (x, y, width, height)) and width > 0 and height > 0,
             "Graphviz returned invalid layout bounds")
    scale = min(1, 1080 / width)
    _require(scale >= 13 / 17,
             "graph is too wide for readable text; try direction TB, shorter labels, or split it into smaller views")
    for graph in root.findall(f"{{{_SVG}}}g"):
        for child in list(graph):
            if child.tag == f"{{{_SVG}}}polygon":
                graph.remove(child)
                break
    # ElementTree escapes all text and keeps namespace declarations self-contained.
    body = "".join(ET.tostring(child, encoding="unicode") for child in root)
    transform = f"translate({-x * scale:.6f},{-y * scale:.6f}) scale({scale:.6f})"
    return math.ceil(width * scale), math.ceil(height * scale), f'<g transform="{transform}">{body}</g>'


def templates():
    examples = {
        "flow": ("Diagnostic decision flow", "A conceptual sequence for gathering evidence before choosing a diagnostic action.",
                 {"direction": "TB", "nodes": [{"id": "start", "label": "Observe the symptom", "role": "start"},
                  {"id": "check", "label": "Evidence sufficient?", "role": "decision"},
                  {"id": "measure", "label": "Gather another measurement", "role": "input"},
                  {"id": "act", "label": "Choose the next action", "role": "end"}],
                  "edges": [{"from": "start", "to": "check"}, {"from": "check", "to": "measure", "label": "No"},
                            {"from": "measure", "to": "check", "label": "New evidence", "style": "dashed"},
                            {"from": "check", "to": "act", "label": "Yes"}]}),
        "architecture": ("Diagnostic system architecture", "A conceptual architecture showing information moving from a sensor through a service to stored results.",
                         {"direction": "LR", "groups": [{"id": "platform", "label": "Diagnostic platform"}],
                          "nodes": [{"id": "sensor", "label": "Sensor", "role": "external"},
                                    {"id": "service", "label": "Analysis service", "role": "service", "group": "platform"},
                                    {"id": "store", "label": "Results store", "role": "store", "group": "platform"}],
                          "edges": [{"from": "sensor", "to": "service", "label": "Measurements"},
                                    {"from": "service", "to": "store", "label": "Findings"}]}),
        "dependency": ("Course module dependencies", "Arrows mean requires: fault isolation requires measurement and a system model; both require observation.",
                       {"direction": "TB", "nodes": [{"id": "isolation", "label": "Fault isolation"},
                        {"id": "measurement", "label": "Measurement"}, {"id": "model", "label": "System model"},
                        {"id": "observation", "label": "Observation"}],
                        "edges": [{"from": "isolation", "to": "measurement", "label": "Requires"},
                                  {"from": "isolation", "to": "model", "label": "Requires"},
                                  {"from": "measurement", "to": "observation"}, {"from": "model", "to": "observation"}]}),
        "tree": ("Diagnostic evidence hierarchy", "A conceptual rooted hierarchy partitions evidence into observations and measurements.",
                 {"direction": "TB", "nodes": [{"id": "evidence", "label": "Evidence"}, {"id": "observe", "label": "Observations"},
                  {"id": "measure", "label": "Measurements"}, {"id": "voltage", "label": "Voltage"}, {"id": "current", "label": "Current"}],
                  "edges": [{"from": "evidence", "to": "observe"}, {"from": "evidence", "to": "measure"},
                            {"from": "measure", "to": "voltage"}, {"from": "measure", "to": "current"}]}),
        "mindmap": ("Planning a diagnostic investigation", "A conceptual mind map links the central investigation to questions about symptoms, hypotheses, and evidence.",
                    {"direction": "LR", "nodes": [{"id": "investigation", "label": "Investigation"},
                     {"id": "symptoms", "label": "What are the symptoms?"}, {"id": "hypotheses", "label": "What could explain them?"},
                     {"id": "evidence", "label": "What evidence distinguishes causes?"}],
                     "edges": [{"from": "investigation", "to": "symptoms"}, {"from": "investigation", "to": "hypotheses"},
                               {"from": "investigation", "to": "evidence"}]}),
        "state": ("Diagnostic session states", "A conceptual state machine starts ready, collects evidence, and completes when the findings are accepted. Insufficient evidence returns the session to collection.",
                  {"direction": "TB", "initial": "ready", "nodes": [{"id": "ready", "label": "Ready", "role": "initial"},
                   {"id": "collect", "label": "Collecting evidence"}, {"id": "review", "label": "Reviewing findings"},
                   {"id": "complete", "label": "Complete", "role": "final"}],
                   "edges": [{"from": "ready", "to": "collect", "label": "Begin"},
                             {"from": "collect", "to": "review", "label": "Evidence available"},
                             {"from": "review", "to": "collect", "label": "Insufficient evidence", "style": "dashed"},
                             {"from": "review", "to": "complete", "label": "Accept findings"}]}),
    }
    return {kind: {"version": 1, "kind": kind, "title": title, "description": description,
                   "status": "conceptual", "theme": "paper", "data": copy.deepcopy(data)}
            for kind, (title, description, data) in examples.items()}
