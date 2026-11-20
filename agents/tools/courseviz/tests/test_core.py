import copy
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
from courseviz import core
from courseviz.cli import render_files
from courseviz.themes import THEMES

class CoreTests(unittest.TestCase):
    def spec(self): return copy.deepcopy(core.templates()['bar'])
    def test_every_template_and_theme(self):
        for name,spec in core.templates().items():
            for theme in THEMES:
                with self.subTest(kind=name,theme=theme):
                    spec=copy.deepcopy(spec); spec['theme']=theme
                    before=copy.deepcopy(spec)
                    root=ET.fromstring(core.svg(spec))
                    self.assertEqual(root.attrib['role'],'img')
                    self.assertEqual(spec,before)
    def test_escape_and_alternative(self):
        s=self.spec(); s['title']='</script><img src=x onerror=alert(1)> & "'
        rendered=core.svg(s); page=core.html_page(s,rendered)
        self.assertNotIn('<img src=x',page)
        self.assertIn('&lt;img',page)
        self.assertIn('Text and data alternative',page)
        ET.fromstring(rendered)
    def test_measured_provenance(self):
        s=self.spec(); s['status']='measured'; s.pop('source',None)
        with self.assertRaisesRegex(ValueError,'source'): core.validate(s)
    def test_strict_common(self):
        for key,value in [('version',True),('surprise',3),('theme','unknown'),('description','')]:
            s=self.spec(); s[key]=value
            with self.assertRaises(ValueError): core.validate(s)
    def test_duplicate_json_keys(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.json'; p.write_text('{"a":1,"a":2}')
            with self.assertRaisesRegex(ValueError,'Duplicate'): core.load(p)
    def test_cache_and_corruption_repair(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d); s=self.spec()
            self.assertEqual(render_files(s,out,'test','engine'),'built')
            self.assertEqual(render_files(s,out,'test','engine'),'cached')
            p=out/'test.svg'; original=p.read_bytes(); p.write_text('corrupt')
            self.assertEqual(render_files(s,out,'test','engine'),'built')
            self.assertEqual(p.read_bytes(),original)
            self.assertEqual(render_files(s,out,'test','new-engine'),'built')
    def test_bad_name_does_not_escape_output(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError): render_files(self.spec(),Path(d),'../escape','x')
    def test_reserved_name(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,'reserved'): render_files(self.spec(),Path(d),'index','x')
    def test_invalid_xml_text(self):
        for value in ['bad\ufffe', 'bad\ud800']:
            s=self.spec(); s['title']=value
            with self.assertRaises(ValueError): core.validate(s)
    def test_wide_title_wraps(self):
        s=core.templates()['flow']; s['title']='W'*80
        result=core.svg(s)
        self.assertNotIn('W'*80,result.split('</desc>')[1])
    def test_repeated_frames_have_unique_ids(self):
        s=core.templates()['steps']
        s['data']['frames'][1]['spec']=copy.deepcopy(s['data']['frames'][0]['spec'])
        root=ET.fromstring(core.svg(s))
        ids=[e.attrib['id'] for e in root.iter() if 'id' in e.attrib]
        self.assertEqual(len(ids),len(set(ids)))
    def test_inline_graph_uses_real_svg_tags(self):
        result=core.svg(core.templates()['architecture'])
        self.assertNotIn('<ns0:',result)
        self.assertIn('<text',result)
    def test_nested_steps_rejected(self):
        s=core.templates()['steps']; s['data']['frames'][0]['spec']=copy.deepcopy(s)
        with self.assertRaisesRegex(ValueError,'Nested'): core.validate(s)
    def test_svg_resource_guard(self):
        for bad in ['<script/>','<image href="https://x"/>','<rect onclick="x"/>','<rect fill="url(https://x)"/>']:
            with self.assertRaises(ValueError): core._safe_svg('<svg>'+bad+'</svg>')

if __name__=='__main__': unittest.main()
