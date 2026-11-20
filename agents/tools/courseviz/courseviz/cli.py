"""Bounded authoring commands with content-addressed incremental builds."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from . import __version__
from . import core
from .svg import esc, require
from .themes import THEMES

def atomic(path, content):
    path.parent.mkdir(parents=True,exist_ok=True)
    raw=content.encode('utf-8')
    if path.exists() and path.read_bytes()==raw: return
    with tempfile.NamedTemporaryFile(dir=path.parent,delete=False) as f:
        temporary=Path(f.name); f.write(raw)
    try: temporary.replace(path)
    finally: temporary.unlink(missing_ok=True)

def digest(raw): return hashlib.sha256(raw).hexdigest()

def engine_hash():
    sources=b''.join(p.read_bytes() for p in sorted(Path(__file__).parent.glob('*.py')))
    dot=shutil.which('dot')
    if dot:
        p=subprocess.run([dot,'-V'],capture_output=True,timeout=10)
        sources+=p.stdout+p.stderr
    return digest(sources)

def render_files(spec, out, name, engine, force=False):
    require(re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_.-]{0,100}',name) is not None,'Output name must be a simple filename stem (max 101 characters)')
    require(name != 'index', 'Output name index is reserved for the gallery')
    core.validate(spec) # Do not let caching hide invalid input.
    canonical=json.dumps(spec,sort_keys=True,ensure_ascii=False,indent=2)+'\n'
    fingerprint=digest((engine+canonical).encode())
    paths={ext:out/(name+'.'+ext) for ext in ('svg','html','spec.json')}
    cache=out/(name+'.build.json')
    if cache.exists() and not force:
        try:
            previous=json.loads(cache.read_text())
            if previous['fingerprint']==fingerprint and all(p.exists() and digest(p.read_bytes())==previous['outputs'][ext] for ext,p in paths.items()):
                return 'cached'
        except (ValueError,KeyError,OSError): pass
    rendered=core.svg(spec)
    contents={'svg':rendered+'\n','html':core.html_page(spec,rendered),'spec.json':canonical}
    for ext,path in paths.items(): atomic(path,contents[ext])
    atomic(cache,json.dumps({'version':1,'engine':engine,'fingerprint':fingerprint,'outputs':{k:digest(v.encode()) for k,v in contents.items()}},indent=2)+'\n')
    return 'built'

def gallery(out,entries,title):
    cards=''.join(f'<a class="card" data-search="{esc((s["title"]+" "+s["kind"]).lower())}" href="{esc(n)}.html"><div class="preview"><img loading="lazy" src="{esc(n)}.svg" alt="{esc(s["description"])}"></div><div class="label"><small>{esc(s["kind"])}</small><h2>{esc(s["title"])}</h2><p>{esc(s.get("caption",s["description"]))}</p></div></a>' for n,s in entries)
    page=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title><style>*{{box-sizing:border-box}}body{{margin:0;background:#edf1f7;color:#14253d;font:16px/1.55 system-ui,sans-serif}}main{{max-width:1400px;padding:48px 28px;margin:auto}}header{{max-width:850px;margin-bottom:32px}}h1{{font-size:clamp(32px,5vw,58px);line-height:1.1;margin:16px 0}}header p{{color:#4a5c73}}input{{font:inherit;border:1px solid #b7c4d6;border-radius:9px;padding:12px;width:100%;max-width:520px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,370px),1fr));gap:24px}}a.card{{color:inherit;text-decoration:none;border:1px solid #c6d0df;border-radius:18px;background:white;overflow:hidden;box-shadow:0 8px 24px #1b35520a}}.card:focus-visible,input:focus-visible{{outline:3px solid #195caf;outline-offset:4px}}.card:hover{{border-color:#195caf}}.preview{{height:280px;padding:12px;background:#e5ebf3;display:flex;align-items:center;justify-content:center}}img{{max-width:100%;max-height:100%;object-fit:contain}}.label{{padding:20px}}h2{{font-size:22px;line-height:1.3;margin:6px 0}}small{{text-transform:uppercase;letter-spacing:2px;color:#195caf}}p{{margin:8px 0}}[hidden]{{display:none!important}}</style><main><header><small>COURSEVIZ · LEARN THROUGH STRUCTURE</small><h1>{esc(title)}</h1><p>Inspect a visual, explore its steps, and reuse its specification. Every visual includes a text alternative and identifies whether its content is conceptual, illustrative, measured, or modelled.</p><label for="filter">Find a visual</label><br><input id="filter" type="search" placeholder="Search title or diagram type"><p id="count" aria-live="polite">{len(entries)} visuals</p></header><div class="grid">{cards}</div></main><script>document.querySelector('#filter').addEventListener('input',e=>{{let n=0;document.querySelectorAll('.card').forEach(c=>{{c.hidden=!c.dataset.search.includes(e.target.value.toLowerCase());if(!c.hidden)n++}});document.querySelector('#count').textContent=n+' visuals'}})</script></html>'''
    atomic(out/'index.html',page)

def parser():
    p=argparse.ArgumentParser(prog='courseviz',description='Small specifications → validated SVG + offline HTML teaching visuals.')
    p.add_argument('--version',action='version',version=__version__)
    sub=p.add_subparsers(dest='command',required=True)
    c=sub.add_parser('catalog',help='List kinds and themes; no large templates loaded into output')
    c.add_argument('--json',action='store_true')
    t=sub.add_parser('template',help='Print one editable JSON example'); t.add_argument('kind',choices=sorted(core.REGISTRY)+['steps']); t.add_argument('--theme',choices=THEMES,default='paper')
    v=sub.add_parser('validate',help='Check one or more specifications without rendering'); v.add_argument('files',nargs='+',type=Path)
    r=sub.add_parser('render',help='Render one specification'); r.add_argument('file',type=Path); r.add_argument('--out',type=Path,required=True); r.add_argument('--name'); r.add_argument('--theme',choices=THEMES); r.add_argument('--force',action='store_true')
    b=sub.add_parser('build',help='Build an explicit manifest and searchable gallery'); b.add_argument('manifest',type=Path); b.add_argument('--out',type=Path,required=True); b.add_argument('--force',action='store_true')
    e=sub.add_parser('examples',help='Generate every template and gallery'); e.add_argument('--out',type=Path,required=True); e.add_argument('--theme',choices=THEMES,default='paper'); e.add_argument('--all-themes',action='store_true')
    sub.add_parser('doctor',help='Report runtime dependencies')
    x=sub.add_parser('export',help='Export an existing local HTML visual using optional Playwright'); x.add_argument('file',type=Path); x.add_argument('--out',type=Path,required=True); x.add_argument('--width',type=int,default=1440); x.add_argument('--scale',type=float,default=2)
    return p

def run(args):
    if args.command=='catalog':
        kinds={k:('progressive sequence of complete visuals' if k=='steps' else core.REGISTRY[k].__name__.split('.')[-1]) for k in sorted(core.REGISTRY)+['steps']}
        print(json.dumps({'kinds':kinds,'themes':list(THEMES)},indent=2) if args.json else '\n'.join(f'{k:14} {v}' for k,v in kinds.items())+'\nThemes: '+', '.join(THEMES)); return
    if args.command=='doctor':
        print(json.dumps({'python':sys.version.split()[0],'graphviz':shutil.which('dot'),'node_optional_export':shutil.which('node'),'playwright':'optional; install Node playwright and its Chromium browser, or supply NODE_PATH'},indent=2)); return
    if args.command=='template':
        spec=core.templates()[args.kind]; spec['theme']=args.theme; print(json.dumps(spec,indent=2,ensure_ascii=False)); return
    if args.command=='validate':
        for path in args.files: core.validate(core.load(path)); print(f'valid {path}')
        return
    if args.command=='export':
        require(args.file.is_file() and args.file.suffix.lower()=='.html','Export input must be an existing local HTML file')
        require(args.out.suffix.lower() in ('.png','.pdf'),'Export output must end in .png or .pdf')
        require(320<=args.width<=4000 and 0.5<=args.scale<=4,'Export width must be 320–4000 and scale 0.5–4')
        require(shutil.which('node') is not None,'PNG/PDF export requires Node.js and Playwright with Chromium')
        args.out.parent.mkdir(parents=True,exist_ok=True)
        result=subprocess.run(['node',str(Path(__file__).with_name('export.cjs')),str(args.file.resolve()),str(args.out.resolve()),str(args.width),str(args.scale)],capture_output=True,text=True,timeout=90)
        require(result.returncode==0,'Export failed: '+result.stderr[-1500:])
        print(f'exported {args.out}'); return
    engine=engine_hash()
    if args.command=='render':
        spec=core.load(args.file)
        if args.theme: spec['theme']=args.theme
        name=args.name or args.file.stem
        status=render_files(spec,args.out,name,engine,args.force)
        print(f'{status} {args.out/name}.svg + .html'); return
    entries=[]; counts={'built':0,'cached':0}
    if args.command=='build':
        manifest=core.load(args.manifest)
        require(isinstance(manifest,dict) and not set(manifest)-{'version','title','theme','visuals'},'Manifest fields: version, title, theme, visuals')
        require(manifest.get('version')==1,'Manifest version must be 1')
        title=manifest.get('title','Course visuals'); require(isinstance(title,str),'Manifest title must be text')
        rows=manifest.get('visuals'); require(isinstance(rows,list) and 1<=len(rows)<=500,'Manifest requires 1–500 visuals')
        for row in rows:
            require(isinstance(row,dict) and set(row)<= {'file','name','theme'} and isinstance(row.get('file'),str),'Each visual requires file; name and theme optional')
            path=(args.manifest.parent/row['file']).resolve()
            spec=core.load(path)
            if 'theme' in row or 'theme' in manifest: spec['theme']=row.get('theme',manifest.get('theme'))
            entries.append((row.get('name',path.stem),spec))
    else:
        title='Courseviz visual library'
        for theme in (THEMES if args.all_themes else [args.theme]):
            for kind,spec in core.templates().items():
                spec['theme']=theme; entries.append((kind+'-'+theme if args.all_themes else kind,spec))
    names=[n for n,s in entries]
    require(len(set(names))==len(names),'Output names must be unique')
    # Validate every item before changing any outputs.
    for name,spec in entries:
        require(isinstance(name,str) and re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_.-]{0,100}',name) is not None,'Invalid output name')
        require(name != 'index', 'Output name index is reserved for the gallery')
        core.validate(spec)
    for name,spec in entries: counts[render_files(spec,args.out,name,engine,getattr(args,'force',False))]+=1
    gallery(args.out,entries,title)
    print(f'{counts["built"]} built, {counts["cached"]} cached; {args.out/"index.html"}')

def main():
    try: run(parser().parse_args()); return 0
    except (ValueError,TypeError,KeyError,OSError,OverflowError,RecursionError,subprocess.SubprocessError) as e:
        print(f'courseviz: {e}',file=sys.stderr); return 2
