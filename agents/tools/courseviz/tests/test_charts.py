import copy
import math
import unittest
import xml.etree.ElementTree as ET
from courseviz import charts
from courseviz.themes import THEMES


class ChartsTests(unittest.TestCase):
    def spec(self, kind='line'):
        return copy.deepcopy(charts.templates()[kind])

    def tree(self, spec):
        w,h,body=charts.render(spec,THEMES['paper'])
        return w,h,ET.fromstring('<svg>'+body+'</svg>')

    def test_templates_all_themes_no_mutation(self):
        for kind,spec in charts.templates().items():
            before=copy.deepcopy(spec)
            for theme in THEMES.values():
                with self.subTest(kind=kind, theme=theme['bg']):
                    charts.validate(spec)
                    w,h,body=charts.render(spec,theme)
                    ET.fromstring('<svg>'+body+'</svg>')
                    self.assertLessEqual(w,1120)
                    self.assertGreater(h,200)
            self.assertEqual(spec,before)

    def test_unequal_numeric_x_spacing(self):
        s=self.spec()
        s['data']['series']=[{'name':'A','points':[[0,0],[1,1],[10,2]]}]
        _,_,t=self.tree(s)
        pts=t.find('polyline').attrib['points'].split()
        xs=[float(p.split(',')[0]) for p in pts]
        self.assertAlmostEqual((xs[1]-xs[0])/(xs[2]-xs[0]),.1)

    def test_null_is_gap_and_never_zero(self):
        s=self.spec()
        s['data']['series']=[{'name':'A','points':[[0,5],[1,None],[2,6],[3,7]]}]
        _,_,t=self.tree(s)
        paths=t.findall('polyline')
        self.assertEqual([len(p.attrib['points'].split()) for p in paths],[1,2])
        self.assertEqual(len(t.findall('.//title')),3)

    def test_reversed_or_duplicate_x_rejected(self):
        for points in ([[1,1],[0,2]],[[0,1],[0,2]]):
            s=self.spec()
            s['data']['series']=[{'name':'A','points':points}]
            with self.assertRaisesRegex(ValueError,'strictly increasing'):
                charts.validate(s)

    def test_scatter_order_independent(self):
        s=self.spec('scatter')
        s['data']['series']=[{'name':'A','points':[[10,1],[0,2],[10,3]]}]
        charts.validate(s)

    def test_bar_negative_and_positive_share_zero(self):
        s=self.spec('bar')
        s['data']['series'][0]['values']=[-2,0,4]
        _,_,t=self.tree(s)
        bars=t.findall('./g/rect')
        self.assertEqual(len(bars),3)
        negative,zero,positive=bars
        baseline=float(negative.attrib['y'])
        self.assertEqual(float(zero.attrib['height']),0)
        self.assertAlmostEqual(float(positive.attrib['y'])+float(positive.attrib['height']),baseline,places=3)
        self.assertAlmostEqual(float(positive.attrib['height'])/float(negative.attrib['height']),2,places=4)

    def test_area_closes_at_zero(self):
        s=self.spec('area')
        s['data']['series']=[{'name':'A','points':[[0,2],[10,4]]}]
        _,_,t=self.tree(s)
        pts=t.find('polygon').attrib['points'].split()
        ys=[float(p.split(',')[1]) for p in pts]
        self.assertEqual(ys[0],ys[-1])
        self.assertGreater(ys[0],ys[1])

    def test_bounds_must_encompass_data_and_zero(self):
        cases=[('line','y_range',[0,1]),('line','x_range',[1,4]),('area','y_range',[1,10]),('bar','y_range',[-1,10]),('interval','x_range',[10,20]),('heatmap','scale_range',[2,6])]
        for kind,key,bounds in cases:
            with self.subTest(kind=kind,key=key):
                s=self.spec(kind)
                s['data'][key]=bounds
                with self.assertRaisesRegex(ValueError,'encompass'):
                    charts.validate(s)

    def test_interval_semantics(self):
        s=self.spec('interval')
        s['data']['items'][0]['low']=14
        with self.assertRaisesRegex(ValueError,'low <= value <= high'):
            charts.validate(s)

    def test_nonfinite_boolean_and_huge_rejected(self):
        for v in (True,float('nan'),float('inf'),-float('inf'),10**1000,'3',None):
            with self.subTest(value=str(v)[:30]):
                s=self.spec('bar')
                s['data']['series'][0]['values'][0]=v
                with self.assertRaises(ValueError):
                    charts.validate(s)

    def test_invalid_shapes_raise_valueerror(self):
        for d in (None,[],{}, {'series':None}):
            s=self.spec()
            s['data']=d
            with self.assertRaises(ValueError):
                charts.validate(s)
        s=self.spec('heatmap')
        s['data']['values'][0]=None
        with self.assertRaises(ValueError):
            charts.validate(s)

    def test_labels_escape_and_wrap(self):
        s=self.spec('bar')
        s['data']['labels'][0]='<script>&'+('X'*200)
        s['data']['series'][0]['name']='<img onerror="x">'
        _,h,t=self.tree(s)
        body=charts.render(s,THEMES['paper'])[2]
        self.assertNotIn('<script>',body)
        self.assertNotIn('<img ',body)
        self.assertGreater(h,600)
        self.assertIn('&lt;',body)

    def test_heatmap_bins_and_exact_values(self):
        s=self.spec('heatmap')
        _,_,t=self.tree(s)
        fills=[r.attrib for r in t.findall('rect') if 'fill-opacity' in r.attrib]
        self.assertEqual(len(fills),11)
        self.assertEqual(fills[0]['fill-opacity'],'0.12')
        self.assertEqual(fills[5]['fill-opacity'],'0.84')
        self.assertEqual([r['fill-opacity'] for r in fills[-5:]],['0.12','0.3','0.48','0.66','0.84'])
        self.assertNotIn('linearGradient',ET.tostring(t,encoding='unicode'))

    def test_constant_domains_have_nonzero_span(self):
        s=self.spec()
        s['data']['series']=[{'name':'A','points':[[5,0]]}]
        _,_,t=self.tree(s)
        self.assertNotIn('nan',ET.tostring(t,encoding='unicode'))
        self.assertNotIn('inf',ET.tostring(t,encoding='unicode'))

    def test_large_offsets_have_distinct_explained_ticks(self):
        s=self.spec()
        s['data']['series']=[{'name':'A','points':[[1e12,1e12],[1e12+.5,1e12+.5],[1e12+1,1e12+1]]}]
        _,_,t=self.tree(s)
        ylabels=[n.text for n in t.findall('text') if n.get('x')=='138']
        self.assertEqual(ylabels,['0','0.25','0.5','0.75','1'])
        self.assertEqual(len(set(ylabels)),5)
        notes=[n.text for n in t.findall('text') if n.text and 'Add 1000000000000' in n.text]
        self.assertEqual(len(notes),2)
        coords=[tuple(map(float,p.split(','))) for p in t.find('polyline').get('points').split()]
        self.assertAlmostEqual(coords[1][0]-coords[0][0],coords[2][0]-coords[1][0])
        self.assertAlmostEqual(coords[0][1]-coords[1][1],coords[1][1]-coords[2][1])

    def test_subnormal_and_large_opposite_extremes(self):
        s=self.spec()
        s['data']['series']=[{'name':'A','points':[[5e-324,-1e150],[1e-323,1e150]]}]
        _,_,t=self.tree(s)
        points=t.find('polyline').get('points').split()
        self.assertEqual([float(p.split(',')[0]) for p in points],[150,1000])
        self.assertTrue(all(math.isfinite(float(c)) for p in points for c in p.split(',')))
        ticks=charts._ticks((5e-324,1e-323))
        self.assertEqual(len(ticks),len(set(ticks)))

    def test_heatmap_missing_distinct_from_zero(self):
        s=self.spec('heatmap')
        s['data']['values']=[[None,0,5],[2,4,None]]
        _,_,t=self.tree(s)
        texts=[''.join(n.itertext()) for n in t.findall('text')]
        self.assertEqual(texts.count('Missing'),2)
        self.assertIn('0',texts)
        filled=[r for r in t.findall('rect') if 'fill-opacity' in r.attrib]
        self.assertEqual(len(filled),9) # Four data cells plus five legend swatches.
        s['data']['values']=[[None,None,None],[None,None,None]]
        with self.assertRaisesRegex(ValueError,'at least one numeric'):
            charts.validate(s)

    def test_duplicate_labels_rejected(self):
        for kind in ('bar','interval','heatmap'):
            with self.subTest(kind=kind):
                s=self.spec(kind)
                if kind=='bar':
                    s['data']['labels'][1]=' Start '
                elif kind=='interval':
                    s['data']['items'][1]['label']='Method A'
                else:
                    s['data']['columns'][1]='Cool'
                with self.assertRaisesRegex(ValueError,'distinct'):
                    charts.validate(s)

    def test_precision_is_preserved_in_value_labels(self):
        s=self.spec('heatmap')
        s['data']['values']=[[1e12,1e12+1,1e12+2],[1e12+3,1e12+4,1e12+5]]
        _,_,t=self.tree(s)
        strings=[''.join(n.itertext()) for n in t.findall('text')]
        self.assertIn('1000000000000',strings)
        self.assertIn('1000000000001',strings)
        self.assertNotEqual(charts._fmt(1e12),charts._fmt(1e12+1))

    def test_equal_tiny_values_use_relative_padding(self):
        lo, hi=charts._range({},'range',[1e-150])
        self.assertLess(lo,1e-150)
        self.assertGreater(hi,1e-150)
        self.assertLess(hi-lo,1e-150)
        lo, hi=charts._range({},'range',[5e-324])
        self.assertLess(lo,5e-324)
        self.assertGreater(hi,5e-324)

    def test_heatmap_adjacent_floats_have_no_empty_legend_bins(self):
        low=1e100
        high=math.nextafter(low,math.inf)
        edges=charts._bin_edges((low,high))
        self.assertEqual(edges,[low,high])
        s=self.spec('heatmap')
        s['data']['scale_range']=[low,high]
        s['data']['values']=[[low,high,low],[high,low,high]]
        _,_,t=self.tree(s)
        filled=[r for r in t.findall('rect') if 'fill-opacity' in r.attrib]
        self.assertEqual(len(filled),7) # Six cells, one representable legend bin.

    def test_inexact_huge_integers_rejected_actionably(self):
        s=self.spec('bar')
        s['data']['series'][0]['values'][0]=2**53+1
        with self.assertRaisesRegex(ValueError,'loses precision'):
            charts.validate(s)


if __name__=='__main__':
    unittest.main()
