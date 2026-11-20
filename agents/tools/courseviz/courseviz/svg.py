"""Small, escaped SVG primitives; geometry lives in the semantic renderers."""
import html
import math
import textwrap

def esc(value):
    return html.escape(str(value), quote=True)

def require(condition, message):
    if not condition:
        raise ValueError(message)

def finite(value, name):
    require(isinstance(value, (int, float)) and not isinstance(value, bool), f'{name} must be a number')
    try:
        number = float(value)
    except (OverflowError, ValueError):
        raise ValueError(f'{name} must fit a finite floating-point number') from None
    require(math.isfinite(number), f'{name} must be finite')
    return number

def wrap(value, width=30):
    return [part for paragraph in str(value).split('\n') for part in (textwrap.wrap(paragraph, width=max(1, int(width)), break_long_words=True, break_on_hyphens=False) or [''])]

def text(x, y, value, theme, size=17, fill=None, anchor='start', weight='normal'):
    return f'<text x="{x:g}" y="{y:g}" fill="{esc(fill or theme["ink"])}" font-family="{esc(theme["font"])}" font-size="{size}" text-anchor="{esc(anchor)}" font-weight="{esc(weight)}">{esc(value)}</text>'

def lines(x, y, value, theme, width=30, size=17, leading=24, fill=None, anchor='start', weight='normal'):
    content = ''.join(f'<tspan x="{x:g}" dy="{0 if i == 0 else leading}">{esc(v)}</tspan>' for i, v in enumerate(wrap(value, width)))
    return f'<text x="{x:g}" y="{y:g}" fill="{esc(fill or theme["ink"])}" font-family="{esc(theme["font"])}" font-size="{size}" text-anchor="{esc(anchor)}" font-weight="{esc(weight)}">{content}</text>'

def rect(x,y,w,h,fill,stroke='none',rx=12):
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{rx:g}" fill="{esc(fill)}" stroke="{esc(stroke)}"/>'

def line(x1,y1,x2,y2,stroke,width=2,dash=None):
    return f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" stroke="{esc(stroke)}" stroke-width="{width:g}"' + (f' stroke-dasharray="{esc(dash)}"' if dash else '') + '/>'
