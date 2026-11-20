"""Faithful, linear quantitative charts with explicit axes and bounded input."""
import math
from bisect import bisect_right
from .svg import esc, text, wrap, lines, rect, line, finite, require

KINDS = ('bar', 'line', 'scatter', 'area', 'heatmap', 'interval')
_DASH = (None, '8 4', '2 4', '10 3 2 3', '5 3', '1 3')


def _label(v, name):
    require(isinstance(v, str) and bool(v.strip()) and len(v) <= 240,
            f'{name} must be nonempty text of at most 240 characters')
    return v


def _num(v, name):
    try:
        n = finite(v, name)
    except OverflowError:
        raise ValueError(f'{name} is too large; rescale your units') from None
    require(abs(n) <= 1e150, f'{name} must have magnitude at most 1e150; rescale your units')
    require(not isinstance(v, int) or int(n) == v,
            f'{name} integer loses precision in floating-point coordinates; rescale your units')
    return n


def _keys(d, allowed, name='data'):
    require(isinstance(d, dict), f'{name} must be an object')
    require(not (set(d) - set(allowed)), f'{name} has unknown fields: {", ".join(sorted(str(k) for k in set(d) - set(allowed)))}')


def _array(v, name, lo=1, hi=24):
    require(isinstance(v, list) and lo <= len(v) <= hi, f'{name} must be a list with {lo}–{hi} entries')
    return v


def _range(d, key, values, zero=False):
    vals = list(values) + ([0.] if zero else [])
    low, high = min(vals), max(vals)
    if key in d:
        b = _array(d[key], key, 2, 2)
        a, z = (_num(b[0], key), _num(b[1], key))
        require(a < z, f'{key} must be strictly increasing')
        require(a <= low and z >= high, f'{key} must encompass all values' + (' and zero' if zero else ''))
        return a, z
    if low == high:
        if low == 0:
            return -1., 1.
        pad = abs(low) * .1
        # Relative padding preserves tiny-unit scales; adjacent floats cover
        # subnormals when ten percent rounds to zero.
        return min(low-pad, math.nextafter(low, -math.inf)), max(high+pad, math.nextafter(high, math.inf))
    return low, high


def validate(spec):
    require(isinstance(spec, dict), 'spec must be an object')
    k = spec.get('kind')
    require(k in KINDS, 'unsupported chart kind')
    d = spec.get('data')
    if k == 'heatmap':
        _keys(d, ('rows', 'columns', 'values', 'scale_label', 'scale_range'))
        rows = _array(d.get('rows'), 'rows', hi=30)
        cols = _array(d.get('columns'), 'columns', hi=14)
        for label in rows + cols:
            _label(label, 'heatmap label')
        require(len({' '.join(v.split()) for v in rows}) == len(rows) and len({' '.join(v.split()) for v in cols}) == len(cols), 'heatmap row and column labels must be distinct within each axis')
        _label(d.get('scale_label'), 'scale_label (include units)')
        values = _array(d.get('values'), 'values', len(rows), len(rows))
        for row in values:
            for v in _array(row, 'matrix row', len(cols), len(cols)):
                if v is not None:
                    _num(v, 'heatmap value')
        nums = [v for row in values for v in row if v is not None]
        require(bool(nums), 'heatmap must contain at least one numeric value')
        _range(d, 'scale_range', nums)
        return
    if k == 'interval':
        _keys(d, ('items', 'x_label', 'x_range'))
        _label(d.get('x_label'), 'x_label (include units)')
        for item in _array(d.get('items'), 'items', hi=30):
            _keys(item, ('label', 'value', 'low', 'high'), 'interval item')
            _label(item.get('label'), 'item label')
            a, b, c = [_num(item.get(f), f) for f in ('low', 'value', 'high')]
            require(a <= b <= c, 'interval must satisfy low <= value <= high')
        require(len({' '.join(i['label'].split()) for i in d['items']}) == len(d['items']), 'interval labels must be distinct')
        _range(d, 'x_range', [i[f] for i in d['items'] for f in ('low', 'high')])
        return
    _keys(d, ('labels', 'series', 'x_label', 'y_label', 'x_range', 'y_range') if k == 'bar'
          else ('series', 'x_label', 'y_label', 'x_range', 'y_range'))
    _label(d.get('x_label'), 'x_label (include units or category)')
    _label(d.get('y_label'), 'y_label (include units)')
    series = _array(d.get('series'), 'series', hi=6)
    names = []
    xs, ys = [], []
    if k == 'bar':
        require('x_range' not in d, 'bar has a categorical x axis; use y_range only')
        labels = _array(d.get('labels'), 'labels', hi=24)
        for label in labels:
            _label(label, 'category label')
        require(len({' '.join(v.split()) for v in labels}) == len(labels), 'category labels must be distinct')
    for s in series:
        _keys(s, ('name', 'values') if k == 'bar' else ('name', 'points'), 'series')
        names.append(_label(s.get('name'), 'series name'))
        if k == 'bar':
            ys.extend(_num(v, 'bar value') for v in _array(s.get('values'), 'values', len(labels), len(labels)))
        else:
            px = []
            for p in _array(s.get('points'), 'points', hi=100):
                _array(p, 'point [x, y]', 2, 2)
                x = _num(p[0], 'x')
                px.append(x)
                xs.append(x)
                if p[1] is None:
                    require(k in ('line', 'area'), 'scatter y must be numeric')
                else:
                    ys.append(_num(p[1], 'y'))
            if k in ('line', 'area'):
                require(all(a < b for a, b in zip(px, px[1:])), 'line/area x coordinates must be strictly increasing; sort points and remove duplicate x values')
    require(len({' '.join(v.split()) for v in names}) == len(names), 'series names must be distinct')
    require(bool(ys), 'chart must contain at least one numeric y value')
    _range(d, 'y_range', ys, k in ('bar', 'area'))
    if xs:
        _range(d, 'x_range', xs)


def _fmt(n):
    if n == 0:
        return '0'
    value = str(float(n))
    return value[:-2] if value.endswith('.0') else value


def _map(v, domain, start, end):
    return start + (v - domain[0]) / (domain[1] - domain[0]) * (end - start)


def _ticks(domain):
    # At subnormal spans or one-ULP domains fewer than five distinct ticks exist.
    values = [domain[0] + (domain[1] - domain[0]) * (i / 4) for i in range(4)] + [domain[1]]
    return list(dict.fromkeys(values))


def _tick_layout(domain):
    ticks = _ticks(domain)
    span = domain[1] - domain[0]
    offset = domain[0] if span < max(abs(domain[0]), abs(domain[1])) * 1e-4 else 0.
    values = [t-offset for t in ticks]
    for precision in range(5,18):
        labels = [format(v, f'.{precision}g') if v else '0' for v in values]
        if len({' '.join(v.split()) for v in labels}) == len(labels):
            break
    note = f'Add {_fmt(offset)} to tick labels' if offset else ''
    return ticks, labels, note


def _bin_edges(domain):
    for count in range(5,0,-1):
        edges = [domain[0]+(domain[1]-domain[0])*(i/count) for i in range(count)] + [domain[1]]
        if all(a < b for a,b in zip(edges,edges[1:])):
            return edges


def _marker(x, y, color, index):
    if index % 6 == 0:
        return f'<circle cx="{x:g}" cy="{y:g}" r="5" fill="{color}" stroke="{color}"/>'
    if index % 6 == 1:
        return rect(x-5, y-5, 10, 10, color, rx=0)
    if index % 6 == 3:
        return f'<path d="M{x:g},{y-7:g} L{x+6:g},{y:g} L{x:g},{y+7:g} L{x-6:g},{y:g} Z" fill="{color}"/>'
    if index % 6 == 4:
        return line(x-6,y,x+6,y,color,3) + line(x,y-6,x,y+6,color,3)
    if index % 6 == 5:
        return line(x-5,y-5,x+5,y+5,color,3) + line(x-5,y+5,x+5,y-5,color,3)
    return f'<path d="M{x:g},{y-6:g} L{x+6:g},{y+5:g} L{x-6:g},{y+5:g} Z" fill="{color}"/>'


def _legend(series, theme, y):
    out = []
    for i, s in enumerate(series):
        color = theme['palette'][i]
        out += [line(150, y+5, 187, y+5, color, 3, _DASH[i]), _marker(168, y+5, color, i),
                lines(202, y, s['name'], theme, width=53, size=15, leading=21)]
        y += max(30, len(wrap(s['name'], 53))*21 + 8)
    return ''.join(out), y


def _axes(theme, yd, ymap, bottom, xd=None, xmap=None, top=65):
    out = []
    yticks, ylabels, _ = _tick_layout(yd)
    for v, label in zip(yticks, ylabels):
        y = ymap(v)
        out += [line(150, y, 1000, y, theme['line'], 1), text(138, y+5, label, theme, 14, anchor='end')]
    if yd[0] <= 0 <= yd[1]:
        out.append(line(150, ymap(0), 1000, ymap(0), theme['ink'], 1.5))
    out += [line(150, top, 150, bottom, theme['ink'], 1), line(150, bottom, 1000, bottom, theme['ink'], 1)]
    if xd is not None:
        xticks, xlabels, _ = _tick_layout(xd)
        for v, label in zip(xticks, xlabels):
            x = xmap(v)
            out += [line(x, bottom, x, bottom+6, theme['ink'], 1), text(x, bottom+25, label, theme, 14, anchor='middle')]
    return out


def render(spec, theme):
    validate(spec)
    k, d = spec['kind'], spec['data']
    if k == 'heatmap':
        return _heatmap(d, theme)
    if k == 'interval':
        return _interval(d, theme)
    ss = d['series']
    vals = [v for s in ss for v in (s['values'] if k == 'bar' else [p[1] for p in s['points'] if p[1] is not None])]
    yd = _range(d, 'y_range', vals, k in ('bar', 'area'))
    bottom = 445
    ym = lambda v: _map(v, yd, bottom, 65)
    out = [lines(150, 22, d['y_label'], theme, width=50, size=16, leading=21)]
    # Expand plot top to accommodate arbitrarily wrapped axis titles.
    top = 22 + len(wrap(d['y_label'], 50))*21 + 22
    y_note = _tick_layout(yd)[2]
    if y_note:
        out.append(text(150, top, 'Y axis: ' + y_note, theme, 14, fill=theme['muted']))
        top += 26
    bottom = top + 380
    ym = lambda v: _map(v, yd, bottom, top)
    if k == 'bar':
        out.extend(_axes(theme, yd, ym, bottom, top=top))
        n = len(d['labels'])
        group = 850/n
        bw = group*.8/len(ss)
        maxrows = 1
        for j, label in enumerate(d['labels']):
            x = 150 + group*(j+.5)
            chars = max(1, int(group/14)-1)
            maxrows = max(maxrows, len(wrap(label, chars)))
            out.append(lines(x, bottom+25, label, theme, width=chars, size=14, leading=19, anchor='middle'))
            for i, s in enumerate(ss):
                v = s['values'][j]
                yy = ym(v)
                bx = 150+j*group+group*.1+i*bw
                # Rectangles encode zero-to-value distances, including negatives.
                out.append(f'<g><title>{esc(s["name"])} · {esc(label)}: {_fmt(v)}</title>' + rect(bx, min(yy, ym(0)), bw*.94, abs(yy-ym(0)), theme['palette'][i], rx=0) + '</g>')
                if len(ss) > 1:
                    # Symbols provide series identity independently of color.
                    out.append(_marker(bx+bw*.47, yy, theme['ink'], i))
        foot = bottom + maxrows*19 + 30
    else:
        xs = [p[0] for s in ss for p in s['points']]
        xd = _range(d, 'x_range', xs)
        xm = lambda v: _map(v, xd, 150, 1000)
        out.extend(_axes(theme, yd, ym, bottom, xd, xm, top=top))
        for i, s in enumerate(ss):
            color = theme['palette'][i]
            segments, seg = [], []
            for x, y in s['points']:
                if y is None:
                    if seg:
                        segments.append(seg)
                    seg = []
                else:
                    seg.append((xm(x), ym(y), x, y))
            if seg:
                segments.append(seg)
            for seg in segments:
                coords = ' '.join(f'{x:g},{y:g}' for x,y,_,_ in seg)
                if k == 'area':
                    z = ym(0)
                    out.append(f'<polygon points="{seg[0][0]:g},{z:g} {coords} {seg[-1][0]:g},{z:g}" fill="{color}" fill-opacity="0.18"/>')
                if k in ('line', 'area'):
                    dash = f' stroke-dasharray="{_DASH[i]}"' if _DASH[i] else ''
                    out.append(f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="2.5"{dash}/>')
                for x, y, rawx, rawy in seg:
                    out.append(f'<g><title>{esc(s["name"])}: x={_fmt(rawx)}, y={_fmt(rawy)}</title>{_marker(x,y,color,i)}</g>')
        foot = bottom + 55
        x_note = _tick_layout(xd)[2]
        if x_note:
            out.append(text(150, foot, 'X axis: ' + x_note, theme, 14, fill=theme['muted']))
            foot += 28
    out.append(lines(575, foot, d['x_label'], theme, width=50, size=16, leading=21, anchor='middle'))
    foot += len(wrap(d['x_label'], 50))*21 + 30
    legend, end = _legend(ss, theme, foot)
    out.append(legend)
    return 1080, int(end+20), ''.join(out)


def _interval(d, theme):
    domain = _range(d, 'x_range', [i[f] for i in d['items'] for f in ('low','high')])
    xm = lambda v: _map(v, domain, 350, 990)
    out, y = [], 35
    for item in d['items']:
        rows = len(wrap(item['label'], 19))
        h = max(58, rows*22+18)
        cy = y+h/2
        out += [lines(22, y+22, item['label'], theme, width=19, size=16, leading=22),
                line(xm(item['low']), cy, xm(item['high']), cy, theme['accent'], 3),
                line(xm(item['low']), cy-9, xm(item['low']), cy+9, theme['accent'], 2),
                line(xm(item['high']), cy-9, xm(item['high']), cy+9, theme['accent'], 2),
                _marker(xm(item['value']), cy, theme['accent'], 0),
                text(350, cy+27, f'{_fmt(item["value"])} [{_fmt(item["low"])}, {_fmt(item["high"])}]', theme, 13, fill=theme['muted'])]
        y += h
    out.append(line(350,y,990,y,theme['ink'],1))
    ticks, labels, note = _tick_layout(domain)
    for v, label in zip(ticks, labels):
        x=xm(v)
        out += [line(x,y,x,y+6,theme['ink'],1),text(x,y+26,label,theme,14,anchor='middle')]
    if note:
        out.append(text(350,y+53,note,theme,14,fill=theme['muted']))
        y+=28
    out.append(lines(670,y+60,d['x_label'],theme,width=40,size=16,leading=22,anchor='middle'))
    end=y+60+len(wrap(d['x_label'],40))*22
    out.append(text(350,end+25,'Dot: value · whiskers: supplied low–high range',theme,14,fill=theme['muted']))
    return 1080,int(end+50),''.join(out)


def _heatmap(d, theme):
    rows, cols = d['rows'], d['columns']
    domain = _range(d,'scale_range',[v for row in d['values'] for v in row if v is not None])
    edges = _bin_edges(domain)
    count = len(edges)-1
    cw=760/len(cols)
    chars=max(1,int(cw/14)-1)
    head=max(len(wrap(c,chars)) for c in cols)*20+25
    out=[]
    for j,c in enumerate(cols):
        out.append(lines(285+(j+.5)*cw,22,c,theme,width=chars,size=14,leading=20,anchor='middle'))
    y=head
    for i,r in enumerate(rows):
        value_chars=max(1,int(cw/13)-1)
        value_rows=max(len(wrap(_fmt(v) if v is not None else 'Missing',value_chars)) for v in d['values'][i])
        h=max(55,len(wrap(r,16))*22+16,value_rows*16+20)
        out.append(lines(20,y+27,r,theme,width=16,size=16,leading=22))
        for j,v in enumerate(d['values'][i]):
            if v is None:
                label = 'Missing'
                out += [rect(285+j*cw,y,cw,h,theme['surface'],theme['muted'],rx=0),
                        lines(285+(j+.5)*cw,y+h/2+5-(len(wrap(label,value_chars))-1)*8,label,theme,width=value_chars,size=13,leading=16,anchor='middle',fill=theme['muted'])]
                continue
            # Match the displayed boundary intervals exactly, including ties.
            b=min(count-1,max(0,bisect_right(edges,v)-1))
            fill=theme['palette'][0]
            out += [rect(285+j*cw,y,cw,h,theme['surface'],theme['line'],rx=0),
                    f'<rect x="{285+j*cw:g}" y="{y:g}" width="{cw:g}" height="{h:g}" fill="{fill}" fill-opacity="{.12+.72*b/max(1,count-1):g}"/>',
                    lines(285+(j+.5)*cw,y+h/2+5-(len(wrap(_fmt(v),value_chars))-1)*8,_fmt(v),theme,width=value_chars,size=13,leading=16,anchor='middle')]
        y+=h
    y+=35
    out.append(lines(285,y,d['scale_label'],theme,width=46,size=16,leading=22))
    y+=len(wrap(d['scale_label'],46))*22+15
    for b in range(count):
        a,z=edges[b:b+2]
        out += [rect(285,y,75,25,theme['surface'],theme['line'],rx=0),
                f'<rect x="285" y="{y}" width="75" height="25" fill="{theme["palette"][0]}" fill-opacity="{.12+.72*b/max(1,count-1):g}"/>',
                text(378,y+19,f'[{_fmt(a)}, {_fmt(z)}'+(']' if b==count-1 else ')'),theme,14)]
        y+=36
    out.append(lines(285,y+24,f'{count} discrete equal-width bins; neutral outlines indicate missing values.',theme,width=58,size=14,leading=20,fill=theme['muted']))
    return 1080,int(y+70),''.join(out)


def templates():
    base={'version':1,'status':'illustrative','theme':'paper'}
    out={}
    for k in ('bar','line','scatter','area'):
        d={'x_label':'Elapsed time (min)','y_label':'Change in temperature (°C)',
           'series':[{'name':'Sample A', 'values':[-2,3,5]}]}
        if k=='bar':
            d['labels']=['Start','Middle','End']
            d['x_label']='Observation stage'
        else:
            d['series']=[{'name':'Sample A','points':[[0,-2],[1,3],[4,5]]},
                         {'name':'Sample B','points':[[0,1],[2,2],[4,4]]}]
        out[k]={**base,'kind':k,'title':f'{k.title()} example','description':'Invented measurements show how supplied values map to linear axes. Numbers are illustrative.', 'data':d}
    out['interval']={**base,'kind':'interval','title':'Estimate and uncertainty','description':'Illustrative estimates with supplied low and high bounds. Bounds are not assigned a statistical confidence level.', 'data':{'x_label':'Estimated response (ms)','items':[{'label':'Method A','value':12,'low':8,'high':18},{'label':'Method B','value':17,'low':14,'high':23}]}}
    out['heatmap']={**base,'kind':'heatmap','title':'Measurements by condition','description':'Invented values are printed in each cell; fill encodes five equal-width discrete bins. Missing cells have a neutral outline.', 'data':{'rows':['Sample A','Sample B'],'columns':['Cool','Warm','Hot'],'values':[[1,3,5],[2,4,6]],'scale_label':'Response (arbitrary units)'}}
    return out
