import copy
import shutil
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch

from courseviz import graphs
from courseviz.themes import THEMES

SVG = "http://www.w3.org/2000/svg"


class GraphValidationTests(unittest.TestCase):
    def setUp(self):
        self.spec = graphs.templates()["flow"]

    def assertInvalid(self, spec, message):
        with self.assertRaisesRegex(ValueError, message):
            graphs.validate(spec)

    def test_complete_templates_validate_without_mutation(self):
        examples = graphs.templates()
        self.assertEqual(set(examples), set(graphs.KINDS))
        original = copy.deepcopy(examples)
        for spec in examples.values():
            graphs.validate(spec)
            self.assertTrue(spec["description"])
            self.assertEqual(spec["status"], "conceptual")
        self.assertEqual(examples, original)
        examples["flow"]["data"]["nodes"][0]["label"] = "Changed"
        self.assertNotEqual(graphs.templates()["flow"]["data"]["nodes"][0]["label"], "Changed")

    def test_wrong_json_types_raise_value_error(self):
        for bad in [None, [], "flow", {"kind": []}, {"kind": "flow", "data": []}]:
            with self.subTest(bad=bad):
                self.assertInvalid(bad, ".")
        for field, bad in [("nodes", {}), ("nodes", [None]), ("edges", [None]), ("groups", [None])]:
            spec = copy.deepcopy(self.spec)
            spec["data"][field] = bad
            self.assertInvalid(spec, ".")

    def test_ids_duplicates_and_endpoints(self):
        self.spec["data"]["nodes"][0]["id"] = 'a\"]; URL="https://example.com"'
        self.assertInvalid(self.spec, "must start with a letter")
        spec = graphs.templates()["flow"]
        spec["data"]["nodes"].append(copy.deepcopy(spec["data"]["nodes"][0]))
        self.assertInvalid(spec, "duplicate node")
        spec = graphs.templates()["flow"]
        spec["data"]["edges"][0]["to"] = "missing"
        self.assertInvalid(spec, "unknown node")
        spec = graphs.templates()["flow"]
        spec["data"]["edges"].append(copy.deepcopy(spec["data"]["edges"][0]))
        self.assertInvalid(spec, "duplicate edge")

    def test_only_explicit_attributes_and_role_styles(self):
        for target, key, value in [("data", "dot", "digraph {}"), ("node", "URL", "https://example.com"),
                                   ("edge", "style", "bold; URL=evil"), ("node", "role", "ellipse")]:
            spec = graphs.templates()["flow"]
            obj = spec["data"] if target == "data" else spec["data"]["nodes" if target == "node" else "edges"][0]
            obj[key] = value
            self.assertInvalid(spec, "unsupported|must be")

    def test_text_limits_and_xml_controls(self):
        for label in ["", "a" * 601, "abc\x00def", "surrogate\ud800"]:
            spec = graphs.templates()["flow"]
            spec["data"]["nodes"][0]["label"] = label
            self.assertInvalid(spec, "text|long|XML")

    def test_group_membership_and_uniqueness(self):
        spec = graphs.templates()["architecture"]
        spec["data"]["groups"].append(copy.deepcopy(spec["data"]["groups"][0]))
        self.assertInvalid(spec, "duplicate group")
        spec = graphs.templates()["architecture"]
        spec["data"]["nodes"][0]["group"] = "missing"
        self.assertInvalid(spec, "declared group")
        spec = graphs.templates()["architecture"]
        spec["data"]["groups"].append({"id": "unused", "label": "Empty"})
        self.assertInvalid(spec, "at least one node")

    def test_tree_invariants_for_both_tree_kinds(self):
        for kind in ("tree", "mindmap"):
            def spec(edges):
                return {"kind": kind, "data": {"nodes": [{"id": n, "label": n} for n in "abcd"],
                        "edges": [{"from": a, "to": b} for a, b in edges]}}
            for edges, message in [([("a", "b")], "exactly one root"),
                                   ([("a", "c"), ("b", "c"), ("c", "d")], "one parent"),
                                   ([("a", "b"), ("b", "c"), ("c", "a")], "reachable|cycles"),
                                   ([("a", "b"), ("c", "d"), ("d", "c")], "connected")]:
                with self.subTest(kind=kind, edges=edges):
                    self.assertInvalid(spec(edges), message)
            graphs.validate(spec([("a", "b"), ("a", "c"), ("c", "d")]))

    def test_single_node_is_a_valid_tree(self):
        graphs.validate({"kind": "tree", "data": {"nodes": [{"id": "root", "label": "Root"}], "edges": []}})

    def test_initial_state_and_final_state_consistency(self):
        spec = graphs.templates()["state"]
        spec["data"]["initial"] = "collect"
        self.assertInvalid(spec, "agree")
        spec = graphs.templates()["state"]
        spec["data"]["initial"] = "missing"
        self.assertInvalid(spec, "existing state")
        spec = graphs.templates()["state"]
        del spec["data"]["initial"]
        graphs.validate(spec)
        spec["data"]["nodes"][0]["role"] = "state"
        self.assertInvalid(spec, "requires data.initial")
        spec = graphs.templates()["state"]
        spec["data"]["edges"].append({"from": "complete", "to": "ready"})
        self.assertInvalid(spec, "final state")
        self.spec["data"]["initial"] = "start"
        self.assertInvalid(self.spec, "only for state")

    def test_missing_graphviz_is_actionable(self):
        with patch("courseviz.graphs.shutil.which", return_value=None):
            with self.assertRaisesRegex(ValueError, "install Graphviz"):
                graphs.render(self.spec, THEMES["paper"])


@unittest.skipUnless(shutil.which("dot"), "Graphviz is unavailable")
class GraphRenderingTests(unittest.TestCase):
    def svg(self, spec, theme="paper"):
        width, height, body = graphs.render(spec, THEMES[theme])
        self.assertGreater(width, 0)
        self.assertLessEqual(width, 1080)
        self.assertGreater(height, 0)
        root = ET.fromstring(f'<svg xmlns="{SVG}" width="{width}" height="{height}">{body}</svg>')
        return root, body

    def test_every_complete_template_renders_every_theme(self):
        for kind, spec in graphs.templates().items():
            original = copy.deepcopy(spec)
            for theme in THEMES:
                with self.subTest(kind=kind, theme=theme):
                    root, _ = self.svg(spec, theme)
                    texts = root.findall(f".//{{{SVG}}}text")
                    self.assertTrue(texts)
                    self.assertTrue(all(text.attrib["fill"] == THEMES[theme]["ink"] for text in texts))
                    # The top-level graph canvas polygon is removed, preserving parent theme.
                    graph = next(g for g in root.iter(f"{{{SVG}}}g") if g.attrib.get("class") == "graph")
                    self.assertFalse(graph.findall(f"{{{SVG}}}polygon"))
            self.assertEqual(spec, original)

    def test_hostile_labels_remain_literal_text_and_cannot_add_resources(self):
        hostile = '<script>alert("x")</script> \\N \\n ]; URL="https://example.com" <IMG SRC="/etc/passwd">'
        spec = {"kind": "flow", "data": {"nodes": [{"id": "safe", "label": hostile}], "edges": []}}
        root, body = self.svg(spec)
        labels = " ".join(t.text or "" for t in root.iter(f"{{{SVG}}}text"))
        self.assertIn("<script>", labels)
        self.assertIn("\\N", labels)
        self.assertIn("\\n", labels)
        self.assertNotIn("<script>", body)
        self.assertFalse(any(element.tag.rsplit("}", 1)[-1] in {"image", "script", "a", "foreignObject"} for element in root.iter()))
        self.assertFalse(any("href" in attribute for element in root.iter() for attribute in element.attrib))

    def test_long_labels_wrap_without_losing_content(self):
        label = "This is a deliberately long label with supercalifragilisticexpialidocious and a final word"
        spec = {"kind": "flow", "data": {"nodes": [{"id": "safe", "label": label}], "edges": []}}
        root, _ = self.svg(spec)
        texts = [t.text or "" for t in root.iter(f"{{{SVG}}}text")]
        self.assertGreater(len(texts), 2)
        self.assertEqual("".join("".join(texts).split()), "".join(label.split()))

    def test_dash_patterns_and_role_shapes_survive_rendering(self):
        spec = graphs.templates()["flow"]
        spec["data"]["edges"][0]["style"] = "dotted"
        root, body = self.svg(spec)
        self.assertIn("stroke-dasharray", body)
        self.assertTrue(root.findall(f".//{{{SVG}}}ellipse"))
        self.assertTrue(root.findall(f".//{{{SVG}}}polygon"))

    def test_extremely_wide_layout_is_rejected_with_readability_guidance(self):
        spec = {"kind": "dependency", "data": {"direction": "LR",
                "nodes": [{"id": f"n{i}", "label": "A deliberately wide component label"} for i in range(12)],
                "edges": [{"from": f"n{i}", "to": f"n{i+1}"} for i in range(11)]}}
        with self.assertRaisesRegex(ValueError, "too wide.*direction TB"):
            graphs.render(spec, THEMES["paper"])
        spec["data"]["direction"] = "TB"
        self.svg(spec)


if __name__ == "__main__":
    unittest.main()
