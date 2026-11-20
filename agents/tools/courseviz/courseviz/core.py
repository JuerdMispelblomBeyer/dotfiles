import copy
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from . import __version__, graphs, layouts, charts
from .svg import esc, lines, rect, wrap, require
from .themes import THEMES

ET.register_namespace('', 'http://www.w3.org/2000/svg')

BACKENDS = (graphs, layouts, charts)
REGISTRY = {kind: backend for backend in BACKENDS for kind in backend.KINDS}
STATUSES = ('conceptual', 'illustrative', 'measured', 'modelled')
COMMON = {'version','kind','title','description','status','source','caption','theme','data'}

def templates():
    result = {k:v for backend in BACKENDS for k,v in backend.templates().items()}
    result['steps'] = dict(version=1,kind='steps',title='From evidence to a decision',description='Read the panels in order. Each adds a different kind of claim.',status='conceptual',data={'frames':[{'label':'Observe','spec':copy.deepcopy(result['flow'])},{'label':'Assess','spec':copy.deepcopy(result['cards'])}]})
    return result

def _bounded(value, depth=0):
    require(depth <= 24, 'Input nesting exceeds 24 levels')
    if isinstance(value, str):
        require(len(value) <= 12000, 'A text field exceeds 12000 characters; split the visual')
        require(not any((ord(c)<32 and c not in '\n\t\r') or 0xD800<=ord(c)<=0xDFFF or ord(c) in (0xFFFE,0xFFFF) for c in value), 'Text contains unsupported control characters')
    elif isinstance(value, dict):
        require(len(value)<=500, 'Too many object fields')
        for k,v in value.items():
            _bounded(k,depth+1); _bounded(v,depth+1)
    elif isinstance(value,list):
        require(len(value)<=10000, 'Too many values; aggregate the data explicitly')
        for v in value: _bounded(v,depth+1)

def validate(spec, child=False):
    require(isinstance(spec,dict), 'Specification must be a JSON object')
    _bounded(spec)
    require(not set(spec)-COMMON, 'Unknown top-level fields: '+', '.join(sorted(set(spec)-COMMON)))
    require(spec.get('version') == 1 and not isinstance(spec.get('version'),bool), 'version must be 1')
    for key in ('title','description','status','kind'):
        require(isinstance(spec.get(key),str) and bool(spec[key].strip()), f'{key} must be a nonempty string')
    require(spec['status'] in STATUSES, 'status must be conceptual, illustrative, measured, or modelled')
    require(spec.get('theme','paper') in THEMES, 'Unknown theme; use courseviz catalog')
    for key in ('source','caption'):
        require(key not in spec or isinstance(spec[key],str), f'{key} must be a string')
    require(spec['status'] != 'measured' or bool(spec.get('source','').strip()), 'Measured data requires source provenance')
    require(isinstance(spec.get('data'),dict), 'data must be an object')
    if spec['kind']=='steps':
        require(not child, 'Nested steps are unsupported')
        require(set(spec['data'])=={'frames'}, 'steps data requires only frames')
        frames=spec['data']['frames']
        require(isinstance(frames,list) and 2<=len(frames)<=12, 'steps requires 2–12 frames')
        for i,frame in enumerate(frames):
            require(isinstance(frame,dict) and set(frame)=={'label','spec'}, f'Frame {i} requires label and spec')
            require(isinstance(frame['label'],str) and 0<len(frame['label'])<=120, 'Frame label must contain 1–120 characters')
            validate(frame['spec'],child=True)
    else:
        require(spec['kind'] in REGISTRY, 'Unknown kind; use courseviz catalog')
        REGISTRY[spec['kind']].validate(spec)

def load(path):
    def pairs(items):
        out={}
        for key,value in items:
            require(key not in out, f'Duplicate JSON key: {key}')
            out[key]=value
        return out
    raw=path.read_bytes()
    require(len(raw)<=2_000_000, 'Input exceeds 2 MB; aggregate before rendering')
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda v: (_ for _ in ()).throw(ValueError(f'Invalid number {v}')))

def _safe_svg(svg):
    root=ET.fromstring(svg)
    for element in root.iter():
        tag=element.tag.split('}')[-1]
        require(tag not in {'script','foreignObject','image','a','iframe'}, f'Unsafe SVG element: {tag}')
        for attr,value in element.attrib.items():
            require(not attr.lower().startswith('on'), 'Unsafe SVG event handler')
            if attr.split('}')[-1]=='href': require(value.startswith('#'), 'External SVG resource rejected')
            if 'url(' in value: require(re.fullmatch(r'url\(#[\w.-]+\)',value) is not None,'External SVG URL rejected')
    return ET.tostring(root, encoding='unicode')

def _scope_svg(rendered, prefix):
    """Keep repeated frames' accessibility and marker IDs independent."""
    root = ET.fromstring(rendered)
    ids = {e.attrib['id']: prefix + e.attrib['id'] for e in root.iter() if 'id' in e.attrib}
    for element in root.iter():
        for key, value in list(element.attrib.items()):
            if key == 'id': element.set(key, ids[value])
            elif key in ('aria-labelledby', 'aria-describedby'):
                element.set(key, ' '.join(ids.get(v, v) for v in value.split()))
            elif key.split('}')[-1] == 'href' and value.startswith('#'):
                element.set(key, '#' + ids.get(value[1:], value[1:]))
            elif value.startswith('url(#') and value.endswith(')'):
                element.set(key, 'url(#' + ids.get(value[5:-1], value[5:-1]) + ')')
    return ET.tostring(root, encoding='unicode')

def svg(spec):
    validate(spec)
    theme=THEMES[spec.get('theme','paper')]
    if spec['kind']=='steps':
        parts=[]; offset=0; width=1120
        for i,frame in enumerate(spec['data']['frames']):
            child=copy.deepcopy(frame['spec']); child['theme']=spec.get('theme','paper')
            child_svg=_scope_svg(svg(child), f'frame-{i}-')
            root=ET.fromstring(child_svg)
            cw,ch=map(float,root.attrib['viewBox'].split()[2:])
            scale=min(1,1120/cw)
            parts.append(lines(24,offset+28,f'{i+1}. {frame["label"]}',theme,width=75,weight='bold'))
            offset+=max(48,24*len(wrap(frame['label'],75))+20)
            parts.append(f'<svg x="0" y="{offset}" width="{cw*scale}" height="{ch*scale}" viewBox="0 0 {cw} {ch}">'+''.join(ET.tostring(e,encoding='unicode') for e in root if e.tag.split('}')[-1] not in ('title','desc'))+'</svg>')
            offset+=ch*scale+30
        body=''.join(parts); height=offset
    else:
        width,height,body=REGISTRY[spec['kind']].render(spec,theme)
    require(0<width<=20000 and 0<height<=100000, 'Rendered dimensions exceed safe bounds; split the visual')
    # Reserve top and bottom space according to actual wrapped text length.
    width=max(560,width+64)
    chars=max(8,int((width-64)/31))
    heading=wrap(spec['title'],chars)
    header=52+len(heading)*36
    footer_items=[spec['status'].upper()+(' · '+spec['caption'] if spec.get('caption') else '')]
    if spec.get('source'): footer_items.append('Source: '+spec['source'])
    footer_text='\n'.join(footer_items)
    footer_lines=wrap(footer_text,max(10,int((width-64)/13)))
    total=header+height+48+len(footer_lines)*21
    ident='cv-'+hashlib.sha256(json.dumps(spec,sort_keys=True).encode()).hexdigest()[:12]
    result=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:g} {total:g}" width="{width:g}" height="{total:g}" role="img" aria-labelledby="{ident}-title {ident}-desc">'
    result+=f'<title id="{ident}-title">{esc(spec["title"])}</title><desc id="{ident}-desc">{esc(spec["description"])}</desc>'
    result+=rect(0,0,width,total,theme['bg'],rx=0)
    result+=rect(32,23,40,5,theme['accent'],rx=2)
    result+=lines(32,64,spec['title'],theme,width=chars,size=28,leading=36,weight='bold')
    result+=f'<g transform="translate(32 {header})">{body}</g>'
    result+=lines(32,header+height+28,footer_text,theme,width=max(10,int((width-64)/13)),size=13,leading=21,fill=theme['muted'])+'</svg>'
    return _safe_svg(result)

def data_html(value):
    if isinstance(value,dict):
        return '<dl>'+''.join(f'<dt>{esc(k)}</dt><dd>{data_html(v)}</dd>' for k,v in value.items())+'</dl>'
    if isinstance(value,list):
        if value and all(isinstance(row,dict) for row in value) and all(not isinstance(v,(dict,list)) for row in value for v in row.values()):
            keys=list(dict.fromkeys(k for row in value for k in row))
            return '<div class="scroll"><table><thead><tr>'+''.join(f'<th scope="col">{esc(k)}</th>' for k in keys)+'</tr></thead><tbody>'+''.join('<tr>'+''.join(f'<td>{esc(row.get(k,"—"))}</td>' for k in keys)+'</tr>' for row in value)+'</tbody></table></div>'
        return '<ol>'+''.join('<li>'+data_html(v)+'</li>' for v in value)+'</ol>'
    return esc(value)

def html_page(spec, rendered):
    theme=THEMES[spec.get('theme','paper')]
    panels=''
    if spec['kind']=='steps':
        for i,frame in enumerate(spec['data']['frames']):
            child=copy.deepcopy(frame['spec']); child['theme']=spec.get('theme','paper')
            panels+=f'<section class="frame" id="frame-{i}"><h2>{i+1}. {esc(frame["label"])}</h2>'+_scope_svg(svg(child), f'frame-{i}-')+f'<p>{esc(child["description"])}</p></section>'
        controls='<nav aria-label="Diagram steps"><button id="prev">Previous</button><output id="position" aria-live="polite"></output><button id="next">Next</button><button id="all">Show all steps</button></nav>'
    else:
        panels=rendered; controls=''
    return f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(spec['title'])}</title>
<style>:root{{color-scheme:{'dark' if spec.get('theme') in ('midnight','blueprint') else 'light'}}}*{{box-sizing:border-box}}body{{margin:0;background:{theme['bg']};color:{theme['ink']};font:17px/1.65 {theme['font']}}}main{{max-width:1240px;margin:auto;padding:28px}}h1{{font-size:clamp(24px,4vw,40px);line-height:1.2}}.lead{{max-width:80ch;color:{theme['muted']}}}svg{{display:block;max-width:100%;height:auto;margin:auto}}button,a{{color:inherit}}button{{border:1px solid {theme['line']};border-radius:8px;background:{theme['surface']};padding:8px 14px;font:inherit;cursor:pointer}}button:focus-visible,a:focus-visible,summary:focus-visible{{outline:3px solid {theme['accent']};outline-offset:3px}}nav{{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin:20px 0}}details{{border-top:1px solid {theme['line']};padding:16px 0}}summary{{cursor:pointer;font-weight:bold}}.scroll,.viewport{{overflow:auto}}.viewport.zoom svg{{max-width:none}}table{{border-collapse:collapse;width:100%;margin:12px 0}}td,th{{text-align:left;border-bottom:1px solid {theme['line']};padding:8px;vertical-align:top}}dt{{font-weight:bold}}dd{{margin:0 0 12px 20px}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;font-size:13px}}.frame[hidden]{{display:none}}@media print{{nav,button,details{{display:none}}.frame[hidden]{{display:block}}main{{padding:0}}.frame{{break-inside:avoid}}}}</style>
<main><h1>{esc(spec['title'])}</h1><p class="lead">{esc(spec['description'])}</p>{controls}<nav aria-label="View controls"><button id="zoom" aria-pressed="false">Actual size / fit</button><button id="print">Print / save PDF</button></nav><div class="viewport" tabindex="0" aria-label="Visual, scrollable at actual size">{panels}</div><p>{esc(spec.get('caption',''))}</p><details><summary>Text and data alternative</summary>{data_html(spec['data'])}</details><details><summary>Reusable specification</summary><pre>{esc(json.dumps(spec,indent=2,ensure_ascii=False))}</pre></details><p class="lead">{esc(spec['status'].capitalize())} visual. {esc('Source: '+spec['source'] if spec.get('source') else 'No measured data is claimed.')}</p></main>
<script>const frames=[...document.querySelectorAll('.frame')];let index=0,showAll=false;function update(){{frames.forEach((f,i)=>f.hidden=!showAll&&i!==index);document.querySelector('#position').textContent=showAll?'All steps':`${{index+1}} / ${{frames.length}}`;document.querySelector('#prev').disabled=showAll||index===0;document.querySelector('#next').disabled=showAll||index===frames.length-1;document.querySelector('#all').textContent=showAll?'Show one step':'Show all steps';}}if(frames.length){{document.querySelector('#prev').onclick=()=>{{index--;update()}};document.querySelector('#next').onclick=()=>{{index++;update()}};document.querySelector('#all').onclick=()=>{{showAll=!showAll;update()}};update()}}document.querySelector('#zoom').onclick=e=>{{let on=document.querySelector('.viewport').classList.toggle('zoom');e.currentTarget.setAttribute('aria-pressed',on)}};document.querySelector('#print').onclick=()=>window.print();</script></html>'''
