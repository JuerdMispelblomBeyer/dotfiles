import copy
import math
import unittest
import xml.etree.ElementTree as ET

from courseviz import layouts
from courseviz.themes import THEMES


class LayoutTests(unittest.TestCase):
    def setUp(self):
        self.examples = layouts.templates()
        self.theme = THEMES['paper']

    def svg(self, spec):
        width, height, body = layouts.render(spec, self.theme)
        return width, height, ET.fromstring('<svg>' + body + '</svg>')

    def test_all_examples_validate_render_and_do_not_mutate(self):
        self.assertEqual(set(layouts.KINDS), set(self.examples))
        original = copy.deepcopy(self.examples)
        for kind, spec in self.examples.items():
            layouts.validate(spec)
            for name, theme in THEMES.items():
                with self.subTest(kind=kind, theme=name):
                    width, height, body = layouts.render(spec, theme)
                    self.assertLessEqual(width, 1120)
                    self.assertGreater(height, 100)
                    ET.fromstring('<svg>' + body + '</svg>')
        self.assertEqual(original, self.examples)

    def test_examples_are_fresh(self):
        self.examples['sequence']['data']['steps'][0]['label'] = 'Changed'
        self.assertNotEqual(self.examples, layouts.templates())

    def test_text_is_escaped(self):
        for kind, spec in self.examples.items():
            if kind in ('sequence', 'layers', 'cards', 'timeline'):
                key = {'sequence': 'steps', 'timeline': 'events'}.get(kind, kind)
                spec['data'][key][0]['label'] = '<script>alert("x") & bad</script>'
            elif kind == 'interaction':
                spec['data']['messages'][0]['label'] = '<script> & "'
            else:
                spec['data']['columns'][0] = '<script> & "'
            _, _, root = self.svg(spec)
            self.assertFalse(list(root.iter('script')))
            self.assertIn('<script>', ''.join(root.itertext()))

    def test_sequence_has_order_and_both_endpoints(self):
        _, _, root = self.svg(self.examples['sequence'])
        texts = list(root.itertext())
        for term in ('1', '2', '3', 'START', 'END'):
            self.assertIn(term, texts)
        content = "".join(root.itertext()).replace(" ", "")
        self.assertLess(content.index("Capturethesymptom"), content.index("Testafocusedhypothesis"))

    def test_proportional_time_positions_and_coincident_events(self):
        spec = self.examples['timeline']
        spec['data'].update(start=0, end=100, events=[
            {'at': at, 'label': str(at), 'detail': 'A diagnostic event'} for at in [0, 10, 10, 100]])
        _, _, root = self.svg(spec)
        xs = [float(c.attrib['cx']) for c in root.iter('circle')]
        self.assertAlmostEqual((xs[1]-xs[0])/(xs[-1]-xs[0]), .1)
        self.assertEqual(xs[1], xs[2])
        self.assertEqual(xs[0], 52)
        self.assertEqual(xs[-1], 500)
        self.assertIn('Proportional linear axis', ''.join(root.itertext()))

    def test_timeline_close_large_numbers_are_distinct(self):
        spec = self.examples['timeline']
        spec['data'].update(start=10**15, end=10**15+1, events=[
            {'at': 10**15, 'label': 'A', 'detail': 'First'},
            {'at': 10**15+1, 'label': 'B', 'detail': 'Last'}])
        _, _, root = self.svg(spec)
        text = ''.join(root.itertext())
        self.assertIn('1000000000000000', text)
        self.assertIn('1000000000000001', text)

    def test_invalid_timeline_numbers_ranges_and_order(self):
        for field, bad in [('start', True), ('start', '0'), ('end', math.inf), ('end', math.nan), ('end', 10**1000), ('end', 0)]:
            spec = copy.deepcopy(self.examples['timeline'])
            spec['data'][field] = bad
            with self.subTest(field=field, bad_type=type(bad).__name__), self.assertRaises(ValueError):
                layouts.validate(spec)
        for ats in [[20, 10], [-1, 10], [10, 61], [False, 10], [10, math.nan]]:
            spec = copy.deepcopy(self.examples['timeline'])
            spec['data']['events'] = [{'at': a, 'label': 'A', 'detail': 'D'} for a in ats]
            with self.subTest(ats=ats), self.assertRaises(ValueError):
                layouts.validate(spec)

    def test_tables_require_complete_explicit_cells(self):
        for kind in ('matrix', 'comparison'):
            for bad in [None, [], ['only one'], ['x']*5, [1, 2, 3]]:
                spec = copy.deepcopy(self.examples[kind])
                if kind == 'matrix':
                    spec['data']['values'][0] = bad
                else:
                    spec['data']['rows'][0]['values'] = bad
                with self.subTest(kind=kind, bad=bad), self.assertRaises(ValueError):
                    layouts.validate(spec)

    def test_matrix_axes_and_each_cell_are_rendered(self):
        spec = self.examples['matrix']
        _, _, root = self.svg(spec)
        content = ''.join(root.itertext())
        for value in [spec['data']['row_axis'], spec['data']['column_axis']]:
            self.assertIn(value, content)
        for row in spec['data']['values']:
            for value in row:
                self.assertIn(value.replace(' ', ''), content.replace(' ', ''))

    def test_layers_render_order_and_boundary_note(self):
        _, _, root = self.svg(self.examples['layers'])
        content = ''.join(root.itertext())
        self.assertLess(content.index('User experience'), content.index('Hardware'))
        self.assertIn('height carries no quantitative meaning', content)

    def test_bad_shapes_and_unknown_fields_are_value_errors(self):
        for bad in [None, [], '', 1, {'kind': []}, {'kind': 'invalid'}]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                layouts.validate(bad)
        for kind, original in self.examples.items():
            for bad_data in [None, [], '', 1, {**original['data'], 'surprise': 1}]:
                spec = {**original, 'data': bad_data}
                with self.subTest(kind=kind, data=bad_data), self.assertRaises(ValueError):
                    layouts.validate(spec)

    def test_long_labels_increase_height_and_stay_inside_canvas(self):
        for kind in ('sequence', 'timeline', 'layers', 'cards', 'matrix', 'comparison'):
            spec = self.examples[kind]
            _, initial_height, _ = self.svg(spec)
            key = {'sequence': 'steps', 'timeline': 'events'}.get(kind, kind)
            if kind in ('matrix', 'comparison'):
                spec['data']['columns'][0] = 'W'*180
            else:
                spec['data'][key][0]['label'] = 'W'*180
                spec['data'][key][0]['detail'] = 'Evidence and interpretation. '*35
            width, height, root = self.svg(spec)
            self.assertGreater(height, initial_height)
            for node in root:
                if node.tag == 'rect':
                    self.assertLessEqual(float(node.attrib['x'])+float(node.attrib['width']), width)
                    self.assertLessEqual(float(node.attrib['y'])+float(node.attrib['height']), height)
                if node.tag == 'text':
                    bottom = float(node.attrib['y']) + sum(float(t.attrib.get('dy', 0)) for t in node)
                    self.assertLessEqual(bottom+8, height)

    def test_long_unit_header_precedes_axis(self):
        spec = self.examples['timeline']
        spec['data']['unit'] = 'W'*60
        _, _, root = self.svg(spec)
        heading = next(root.iter('text'))
        heading_bottom = float(heading.attrib['y']) + sum(float(t.attrib.get('dy', 0)) for t in heading)
        axis = next(root.iter('line'))
        self.assertGreater(float(axis.attrib['y1']), heading_bottom + 30)

    def test_invalid_xml_characters_are_rejected(self):
        for bad in ['bad\x00', 'bad\ud800', 'bad\ufffe']:
            spec = self.examples['cards']
            spec['data']['cards'][0]['label'] = bad
            with self.assertRaises(ValueError):
                layouts.validate(spec)

    def test_interaction_order_directions_and_self_message(self):
        spec = self.examples['interaction']
        _, _, root = self.svg(spec)
        content = ''.join(root.itertext())
        self.assertIn('SPACING DOES NOT ENCODE ELAPSED TIME', content)
        paths = list(root.iter('path'))
        self.assertEqual(len(paths), len(spec['data']['messages']))
        self.assertIn('L 530', paths[0].attrib['d'])
        self.assertIn('L 530', paths[2].attrib['d'])
        self.assertIn('L 530', paths[3].attrib['d'])
        self.assertEqual(len([l for l in root.iter('line') if l.attrib.get('stroke-dasharray') == '7 5']), 2)
        labels = [next(t for t in root.iter('text') if ''.join(t.itertext()) == m['label'])
                  for m in spec['data']['messages']]
        self.assertEqual(sorted(float(t.attrib['y']) for t in labels), [float(t.attrib['y']) for t in labels])

    def test_interaction_rejects_duplicate_and_unknown_participants(self):
        mutations = [
            lambda d: d['participants'].append(d['participants'][0]),
            lambda d: d['messages'][0].update({'to': 'absent'}),
            lambda d: d['messages'][0].update({'style': 'dotted'}),
            lambda d: d.update({'messages': []}),
            lambda d: d.update({'participants': []}),
            lambda d: d['messages'][0].update({'from': True})]
        for mutate in mutations:
            spec = copy.deepcopy(self.examples['interaction'])
            mutate(spec['data'])
            with self.assertRaises(ValueError):
                layouts.validate(spec)

    def test_interaction_single_participant_and_long_labels(self):
        spec = self.examples['interaction']
        spec['data'] = {'participants': [{'id': 'one', 'label': 'W'*180}],
                        'messages': [{'from': 'one', 'to': 'one', 'label': 'W'*240}]}
        _, height, root = self.svg(spec)
        self.assertGreater(height, 1000)
        for node in root.iter('text'):
            bottom = float(node.attrib['y']) + sum(float(t.attrib.get('dy', 0)) for t in node)
            self.assertLess(bottom, height)

    def test_item_limits_and_duplicate_axis_labels(self):
        spec = self.examples['cards']
        spec['data']['cards'] *= 13
        with self.assertRaisesRegex(ValueError, 'split larger'):
            layouts.validate(spec)
        spec = self.examples['matrix']
        spec['data']['columns'][1] = spec['data']['columns'][0]
        with self.assertRaisesRegex(ValueError, 'unique'):
            layouts.validate(spec)


if __name__ == '__main__':
    unittest.main()
