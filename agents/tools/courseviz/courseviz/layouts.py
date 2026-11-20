"""Teaching layouts with explicit order, complete tables, and honest time axes."""
from .svg import esc, text, wrap, lines, rect, line, finite, require

KINDS = ("sequence", "timeline", "layers", "comparison", "matrix", "cards", "interaction")
WIDTH = 1080


def _object(value, name, allowed, required=()):
    require(isinstance(value, dict), f"{name} must be an object")
    require(all(isinstance(k, str) for k in value), f"{name} keys must be strings")
    unknown = set(value) - set(allowed)
    require(not unknown, f"{name} has unknown fields: {', '.join(sorted(unknown))}")
    for key in required:
        require(key in value, f"{name}.{key} is required")


def _string(value, name, maximum=1200):
    require(isinstance(value, str) and bool(value.strip()), f"{name} must be a nonempty string")
    require(len(value) <= maximum, f"{name} exceeds {maximum} characters; split this visual")
    require(all((ord(c) >= 32 and not 0xD800 <= ord(c) <= 0xDFFF and ord(c) not in (0xFFFE, 0xFFFF)) or c in '\n\t\r' for c in value), f"{name} contains an invalid control character")


def _array(value, name, minimum=1, maximum=12):
    require(isinstance(value, list), f"{name} must be an array")
    require(minimum <= len(value) <= maximum, f"{name} must contain {minimum}–{maximum} items; split larger visuals")


def _labels(value, name, minimum=1, maximum=6):
    _array(value, name, minimum, maximum)
    for i, item in enumerate(value):
        _string(item, f"{name}[{i}]", 180)
    require(len(set(value)) == len(value), f"{name} labels must be unique")


def _items(value, name, minimum=1, maximum=12, extra=()):
    _array(value, name, minimum, maximum)
    for i, item in enumerate(value):
        p = f"{name}[{i}]"
        _object(item, p, ("label", "detail", *extra), ("label", "detail"))
        _string(item["label"], p + ".label", 180)
        _string(item["detail"], p + ".detail")


def _finite(value, name):
    try:
        return finite(value, name)
    except (OverflowError, TypeError):
        raise ValueError(f"{name} must be a finite number that fits a float") from None


def validate(spec):
    """Validate all kind-specific fields without mutating input."""
    require(isinstance(spec, dict), "spec must be an object")
    kind = spec.get("kind")
    require(isinstance(kind, str) and kind in KINDS, "unsupported teaching layout kind")
    data = spec.get("data")
    if kind == "interaction":
        _object(data, "data", ("participants", "messages"), ("participants", "messages"))
        _array(data["participants"], "data.participants", 1, 6)
        ids = []
        for i, participant in enumerate(data["participants"]):
            p = f"data.participants[{i}]"
            _object(participant, p, ("id", "label"), ("id", "label"))
            _string(participant["id"], p + ".id", 64)
            _string(participant["label"], p + ".label", 180)
            ids.append(participant["id"])
        require(len(set(ids)) == len(ids), "participant ids must be unique")
        _array(data["messages"], "data.messages", 1, 16)
        for i, message in enumerate(data["messages"]):
            p = f"data.messages[{i}]"
            _object(message, p, ("from", "to", "label", "style"), ("from", "to", "label"))
            for field in ("from", "to"):
                _string(message[field], p + "." + field, 64)
                require(message[field] in ids, p + "." + field + " refers to an unknown participant")
            _string(message["label"], p + ".label", 240)
            require(message.get("style", "solid") in ("solid", "dashed"), p + ".style must be solid or dashed")
    elif kind == "sequence":
        _object(data, "data", ("steps",), ("steps",))
        _items(data["steps"], "data.steps", 2)
    elif kind == "timeline":
        _object(data, "data", ("events", "unit", "start", "end"), ("events", "unit", "start", "end"))
        _string(data["unit"], "data.unit", 60)
        start = _finite(data["start"], "data.start")
        end = _finite(data["end"], "data.end")
        require(start < end, "data.start must be smaller than data.end")
        require(end - start < float('inf'), "timeline axis span must be finite; rescale the positions")
        _items(data["events"], "data.events", 1, 16, ("at",))
        previous = start
        for i, event in enumerate(data["events"]):
            require("at" in event, f"data.events[{i}].at is required")
            at = _finite(event["at"], f"data.events[{i}].at")
            require(start <= at <= end, f"data.events[{i}].at is outside the axis range")
            require(at >= previous, "data.events must be ordered by ascending at; equal times are allowed")
            previous = at
    elif kind == "layers":
        _object(data, "data", ("layers", "order"), ("layers", "order"))
        _string(data["order"], "data.order", 240)
        _items(data["layers"], "data.layers", 2)
    elif kind in ("comparison", "matrix"):
        fields = ("columns", "rows") if kind == "comparison" else ("columns", "rows", "values", "row_axis", "column_axis")
        _object(data, "data", fields, fields)
        _labels(data["columns"], "data.columns", 2 if kind == "comparison" else 1, 4)
        if kind == "comparison":
            _array(data["rows"], "data.rows", 1, 16)
            labels = []
            for i, row in enumerate(data["rows"]):
                _object(row, f"data.rows[{i}]", ("label", "values"), ("label", "values"))
                _string(row["label"], f"data.rows[{i}].label", 180)
                labels.append(row["label"])
                _cells(row["values"], len(data["columns"]), f"data.rows[{i}].values")
            require(len(set(labels)) == len(labels), "data.rows labels must be unique")
        else:
            _labels(data["rows"], "data.rows", 1, 16)
            _string(data["row_axis"], "data.row_axis", 180)
            _string(data["column_axis"], "data.column_axis", 180)
            _array(data["values"], "data.values", len(data["rows"]), len(data["rows"]))
            for i, row in enumerate(data["values"]):
                _cells(row, len(data["columns"]), f"data.values[{i}]")
    else:
        _object(data, "data", ("cards",), ("cards",))
        _items(data["cards"], "data.cards", 1)


def _cells(values, count, name):
    _array(values, name, count, count)
    for i, value in enumerate(values):
        _string(value, f"{name}[{i}]", 900)


def _safe_width(width):
    # Reserve enough horizontal space for unusually wide glyphs and long tokens.
    return max(1, int(width * .60))


def _height(value, width, size=17, leading=24):
    return len(wrap(value, _safe_width(width))) * leading


def _label(x, y, value, theme, width, size=17, weight="normal", fill=None):
    return lines(x, y, value, theme, width=_safe_width(width), size=size, leading=24,
                 fill=fill, weight=weight)


def _number(value):
    return repr(float(value)).removesuffix('.0')


def _dot(x, y, radius, fill, stroke=None):
    return f'<circle cx="{x:g}" cy="{y:g}" r="{radius:g}" fill="{esc(fill)}" stroke="{esc(stroke or fill)}"/>'


def _sequence(data, theme):
    out = []
    y = 28
    steps = data["steps"]
    for i, step in enumerate(steps):
        lh = _height(step["label"], 62)
        dh = _height(step["detail"], 88)
        h = 32 + lh + 10 + dh + 22
        center = y + 36
        if i < len(steps) - 1:
            out.append(line(56, center + 22, 56, y + h + 28, theme["line"], 3))
            out.append(f'<path d="M 50 {y+h+18} L 56 {y+h+26} L 62 {y+h+18}" fill="none" stroke="{esc(theme["accent"])}" stroke-width="2"/>')
        out.append(rect(96, y, 956, h, theme["surface"], theme["line"]))
        out.append(_dot(56, center, 22, theme["accent"]))
        out.append(text(56, center + 6, str(i + 1), theme, size=17, anchor="middle", fill=theme["bg"], weight="bold"))
        out.append(_label(122, y + 30, step["label"], theme, 62, weight="bold"))
        out.append(_label(122, y + 30 + lh + 10, step["detail"], theme, 88, fill=theme["muted"]))
        endpoint = "START" if i == 0 else "END" if i == len(steps) - 1 else ""
        if endpoint:
            out.append(text(1026, y + 26, endpoint, theme, size=13, anchor="end", fill=theme["muted"], weight="bold"))
        y += h + 30
    return WIDTH, int(y), ''.join(out)


def _timeline(data, theme):
    # A shared proportional axis with one event per row prevents close events
    # from being moved apart, hidden, or mislabeled as equally spaced.
    left, right = 52, 500
    heading = "Time · " + data["unit"]
    note_y = 28 + _height(heading, 52) + 12
    axis_y = note_y + 40
    y = axis_y + 26
    start, end = float(data["start"]), float(data["end"])
    out = [_label(52, 28, heading, theme, 52, weight="bold"),
           text(552, 28, "EVENTS · EARLIEST FIRST", theme, size=13, fill=theme["muted"], weight="bold"),
           text(52, note_y, "Proportional linear axis", theme, size=13, fill=theme["muted"]),
           line(left, axis_y, right, axis_y, theme["ink"], 2)]
    for i in range(5):
        tick = start if i == 0 else end
        x = left + (right - left) * i / 4
        out.append(line(x, axis_y-6, x, axis_y+6, theme["ink"], 2))
        if i in (0, 4):
            out.append(text(x, axis_y-13, _number(tick), theme, size=13, anchor="start" if i == 0 else "end"))
    for i, event in enumerate(data["events"]):
        lh, dh = _height(event["label"], 42), _height(event["detail"], 48)
        time_label = _number(float(event["at"])) + " " + data["unit"]
        th = _height(time_label, 48)
        h = 40 + th + lh + dh
        cy = y + 32
        color = theme["palette"][i % len(theme["palette"])]
        out.append(rect(532, y, 520, h, theme["surface"], theme["line"]))
        for j in range(5):
            gx = left + (right-left) * j / 4
            out.append(line(gx, y, gx, y+h, theme["line"], 1, dash="3 6"))
        x = left + (float(event["at"]) - start) / (end - start) * (right - left)
        out.append(line(left, cy, right, cy, theme["line"], 2))
        out.append(_dot(x, cy, 7, color, theme["ink"]))
        out.append(_label(552, y+25, time_label, theme, 48, size=13, fill=theme["muted"]))
        out.append(_label(552, y+25+th+6, event["label"], theme, 42, weight="bold"))
        out.append(_label(552, y+25+th+lh+14, event["detail"], theme, 48, fill=theme["muted"]))
        y += h + 20
    return WIDTH, int(y + 8), ''.join(out)


def _layers(data, theme):
    out = [_label(32, 30, data["order"], theme, 94, weight="bold")]
    y = 34 + _height(data["order"], 94) + 24
    for i, layer in enumerate(data["layers"]):
        lh, dh = _height(layer["label"], 27), _height(layer["detail"], 65)
        h = max(lh, dh) + 44
        out.append(rect(32, y, 1020, h, theme["surface"], theme["line"], rx=4))
        out.append(rect(32, y, 7, h, theme["palette"][i % len(theme["palette"])], rx=0))
        out.append(_label(58, y+31, layer["label"], theme, 27, weight="bold"))
        out.append(line(350, y+20, 350, y+h-20, theme["line"], 1))
        out.append(_label(374, y+31, layer["detail"], theme, 65, fill=theme["muted"]))
        y += h + 18
    out.append(text(32, y+10, "Separate bands show boundaries; band height carries no quantitative meaning.", theme, size=13, fill=theme["muted"]))
    return WIDTH, int(y+40), ''.join(out)


def _table(data, theme, matrix=False):
    columns = data["columns"]
    n = len(columns)
    label_w = 224
    cell_w = (1020-label_w)/n
    # Conservative text width even for wide glyphs; generous cell padding.
    cell_chars = max(10, int((cell_w-36)/10))
    label_chars = 18
    out = []
    y = 24
    if matrix:
        heading = data["column_axis"] + " →"
        out.append(_label(32+label_w+18, y+20, heading, theme, 74, weight="bold"))
        y += _height(heading, 74) + 20
    header_h = max([_height(c, cell_chars) for c in columns] + [_height(data["row_axis"] + " ↓", label_chars) if matrix else 24]) + 40
    out.append(rect(32, y, 1020, header_h, theme["surface"], theme["line"], rx=4))
    out.append(_label(50, y+29, data["row_axis"] + " ↓" if matrix else "Criterion", theme, label_chars, weight="bold"))
    for j, col in enumerate(columns):
        x = 32+label_w+j*cell_w
        out.append(line(x, y, x, y+header_h, theme["line"], 1))
        out.append(_label(x+18, y+29, col, theme, cell_chars, weight="bold"))
    y += header_h
    rows = list(zip(data["rows"], data["values"])) if matrix else [(r["label"], r["values"]) for r in data["rows"]]
    for i, (label, values) in enumerate(rows):
        h = max([_height(label, label_chars)] + [_height(v, cell_chars) for v in values]) + 40
        out.append(rect(32, y, 1020, h, theme["bg"] if i%2 else theme["surface"], theme["line"], rx=0))
        out.append(_label(50, y+29, label, theme, label_chars, weight="bold"))
        for j, value in enumerate(values):
            x = 32+label_w+j*cell_w
            out.append(line(x, y, x, y+h, theme["line"], 1))
            out.append(_label(x+18, y+29, value, theme, cell_chars))
        y += h
    return WIDTH, int(y + 28), ''.join(out)


def _cards(data, theme):
    cards = data["cards"]
    ncols = 1 if len(cards) == 1 else 2
    card_w = (1020 - 24*(ncols-1))/ncols
    chars = int((card_w-48)/10)
    out = []
    y = 24
    for first in range(0, len(cards), ncols):
        row = cards[first:first+ncols]
        h = max(64 + _height(c["label"], chars) + _height(c["detail"], chars) for c in row)
        for j, card in enumerate(row):
            x = 32+j*(card_w+24)
            out.append(rect(x, y, card_w, h, theme["surface"], theme["line"]))
            out.append(rect(x+24, y+22, 34, 4, theme["palette"][(first+j)%len(theme["palette"])], rx=2))
            out.append(_label(x+24, y+53, card["label"], theme, chars, weight="bold"))
            out.append(_label(x+24, y+53+_height(card["label"], chars)+12, card["detail"], theme, chars, fill=theme["muted"]))
        y += h+24
    return WIDTH, int(y+4), ''.join(out)


def _interaction(data, theme):
    participants = data["participants"]
    count = len(participants)
    positions = {p["id"]: 540 if count == 1 else 80 + 900*i/(count-1)
                 for i, p in enumerate(participants)}
    header_h = max(_height(p["label"], 12) for p in participants) + 32
    y = header_h + 64
    messages = []
    for i, message in enumerate(data["messages"]):
        x1, x2 = positions[message["from"]], positions[message["to"]]
        self_message = x1 == x2
        chars = 18 if self_message else max(4, int((abs(x2-x1)-30)/18))
        label_h = len(wrap(message["label"], chars))*24
        arrow_y = y + label_h + 8
        label_x = max(48, min(x1-130, WIDTH-348)) if self_message else (x1+x2)/2
        messages.append(lines(label_x, y, message["label"], theme, width=chars,
                              anchor="start" if self_message else "middle", leading=24))
        messages.append(text(26, arrow_y+5, str(i+1), theme, size=13, fill=theme["muted"]))
        dash = "7 5" if message.get("style", "solid") == "dashed" else None
        tip_x, tip_y = x2, arrow_y
        if self_message:
            # A return to the same lifeline is explicit and takes its own row.
            messages.extend((line(x1, arrow_y, x1+42, arrow_y, theme["ink"], 2, dash),
                             line(x1+42, arrow_y, x1+42, arrow_y+24, theme["ink"], 2, dash),
                             line(x1+42, arrow_y+24, x1, arrow_y+24, theme["ink"], 2, dash)))
            tip_y += 24
            behind = x2+9
        else:
            messages.append(line(x1, arrow_y, x2, arrow_y, theme["ink"], 2, dash))
            behind = x2-9 if x2 > x1 else x2+9
        messages.append(f'<path d="M {behind:g} {tip_y-5:g} L {tip_x:g} {tip_y:g} L {behind:g} {tip_y+5:g}" fill="none" stroke="{esc(theme["ink"])}" stroke-width="2"/>')
        y = tip_y + 58
    out = [text(32, 20, "MESSAGE ORDER · TOP TO BOTTOM · SPACING DOES NOT ENCODE ELAPSED TIME", theme, size=13, fill=theme["muted"])]
    for p in participants:
        x = positions[p["id"]]
        out.extend((line(x, 40+header_h, x, y-22, theme["line"], 2, "5 6"),
                    rect(x-75, 40, 150, header_h, theme["surface"], theme["line"]),
                    lines(x, 68, p["label"], theme, width=_safe_width(12), anchor="middle", weight="bold", leading=24)))
    out.extend(messages)
    return WIDTH, int(y+10), ''.join(out)


def render(spec, theme):
    validate(spec)
    kind, data = spec["kind"], spec["data"]
    if kind == "comparison":
        return _table(data, theme)
    if kind == "matrix":
        return _table(data, theme, matrix=True)
    return {"sequence": _sequence, "timeline": _timeline, "layers": _layers, "cards": _cards, "interaction": _interaction}[kind](data, theme)


def templates():
    """Return fresh complete examples; all invented quantities are illustrative."""
    examples = {
        "interaction": ("A request and its response", "Participants run left to right. Read numbered messages from top to bottom; arrowheads identify receivers. Dashed lines denote the labelled response in this example. A self-message returns to the same participant. Vertical spacing encodes order only, not elapsed time.", {"participants": [
            {"id": "client", "label": "Client"}, {"id": "service", "label": "Service"}, {"id": "store", "label": "Store"}], "messages": [
            {"from": "client", "to": "service", "label": "Request findings"},
            {"from": "service", "to": "store", "label": "Read observations"},
            {"from": "store", "to": "service", "label": "Return observations", "style": "dashed"},
            {"from": "service", "to": "service", "label": "Assess evidence"},
            {"from": "service", "to": "client", "label": "Return findings", "style": "dashed"}]}),
        "sequence": ("From observation to verified fix", "Follow the numbered steps from START to END. Each arrow means proceed to the next step; the order is conceptual, with no duration implied.", {"steps": [
            {"label": "Capture the symptom", "detail": "Record what failed, when it failed, and the expected behavior."},
            {"label": "Test a focused hypothesis", "detail": "Choose an observation that distinguishes competing explanations."},
            {"label": "Verify the change", "detail": "Repeat the original scenario and check for regressions."}]}),
        "timeline": ("Illustrative incident timeline", "Event positions use a proportional linear axis in minutes since the first observation. Equal positions represent simultaneous events. These invented times illustrate the layout, not measured incident data.", {"unit": "min", "start": 0, "end": 60, "events": [
            {"at": 0, "label": "First symptom", "detail": "A request exceeds the expected response time."},
            {"at": 10, "label": "Evidence captured", "detail": "Logs and metrics preserve the state before intervention."},
            {"at": 45, "label": "Recovery verified", "detail": "The original scenario succeeds after the change."}]}),
        "layers": ("A diagnostic stack", "Read from highest abstraction at the top to lowest at the bottom. Separate bands indicate conceptual boundaries, not containment, scale, dependency direction, or measured size.", {"order": "Highest abstraction at top → lowest at bottom", "layers": [
            {"label": "User experience", "detail": "What the person observes and expects."},
            {"label": "Application", "detail": "Requests, state, and decisions in the program."},
            {"label": "Operating system", "detail": "Processes, files, memory, and network interfaces."},
            {"label": "Hardware", "detail": "Physical resources and device behavior."}]}),
        "comparison": ("Two ways to collect evidence", "Compare each approach against the same explicit criteria. Every cell is a qualitative teaching example; no approach is assigned a numerical score.", {"columns": ["Logs", "Metrics"], "rows": [
            {"label": "Best question", "values": ["What happened in this event?", "How does behavior change over time?"]},
            {"label": "Typical detail", "values": ["A contextual record of one event", "A numerical summary across events"]},
            {"label": "Limitation", "values": ["Volume can hide relevant events", "Aggregation can hide individual events"]}]}),
        "matrix": ("Which evidence answers which question?", "Rows are diagnostic questions; columns are evidence sources. Each intersection states the source's qualitative usefulness for that question. This is an illustrative teaching matrix, not measured coverage.", {"row_axis": "Question", "column_axis": "Evidence source", "columns": ["Logs", "Metrics", "Trace"], "rows": ["What failed?", "How widespread?", "Where was time spent?"], "values": [["Detailed events", "Failure counts", "Failing span"], ["Sampled context", "Population trend", "Sampled requests"], ["Timestamps", "Latency distribution", "Span duration"]]}),
        "cards": ("Three habits of diagnosis", "These cards present three independent habits. Their placement and color group the ideas visually; neither encodes a rank or numerical quantity.", {"cards": [
            {"label": "Observe before changing", "detail": "Preserve the evidence that a change could erase."},
            {"label": "Make predictions", "detail": "State what would be different if the hypothesis were true."},
            {"label": "Close the loop", "detail": "Check the original symptom after applying the fix."}]})
    }
    return {kind: {"version": 1, "kind": kind, "title": title, "description": description,
                   "status": "illustrative" if kind in ("timeline", "matrix") else "conceptual",
                   "theme": "paper", "data": data}
            for kind, (title, description, data) in examples.items()}
