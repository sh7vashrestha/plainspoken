import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "skills", "plainspoken")
sys.path.insert(0, os.path.join(SKILL, "scripts"))

import check  # noqa: E402


def rules_hit(text):
    return {name for _, name, _, _ in check.check_lines(text.splitlines(True))}


class RuleTests(unittest.TestCase):
    CASES = {
        "placeholder": "Dear [Hiring Manager's Name], see {{link}}. TODO",
        "chat leftover": "Certainly! Here is your email.",
        "tool mark": "It grew 4% [oaicite:0].",
        "hidden character": "A zero\u200bwidth space.",
        "contrast flourish": "It is a tool, not a toy.",
        "inflated verb": "We leverage the cache.",
        "hype word": "A seamless and robust system.",
        "metaphor filler": "The landscape of testing is wide.",
        "stock opener": "It works. Notably, it is fast.",
        "filler phrase": "It's worth noting that it runs.",
        "stock framing": "In today's world, code matters.",
        "stock closing": "In conclusion, it works.",
        "it's not X, it's Y": "It's not just a model, it's a shift.",
        "hedge stack": "This may potentially help.",
        "vague pointer": "We prefer the latter.",
        "question lead-in": "The result? Faster code.",
        "question heading": "## Why does this matter?",
        "emoji": "Launch day \U0001F680",
    }

    def test_each_rule_fires(self):
        for name, text in self.CASES.items():
            with self.subTest(rule=name):
                self.assertIn(name, rules_hit(text))

    def test_dashes(self):
        self.assertEqual(rules_hit("One dash is fine — like this one.\n"), set())
        self.assertIn("dash pile-up", rules_hit("The tool — a small one — works.\n"))
        many = "This line has a dash — here.\n\n" * 4
        self.assertEqual(rules_hit(many), {"dash overuse"})

    def test_links_are_not_placeholders(self):
        self.assertEqual(rules_hit("See [your account page](https://example.com) and [1].\n"), set())

    def test_every_rule_has_a_case(self):
        self.assertEqual({r[0] for r in check.RULES}, set(self.CASES))

    def test_clean_text_passes(self):
        text = (
            "Hi Sam, the project will be about two weeks late.\n"
            "Did the sensors arrive? I have not seen them.\n"
            "The range is 3–5 volts and the script is in `tools/`.\n"
            "1. Not all devices support it.\n"
        )
        self.assertEqual(rules_hit(text), set())

    def test_code_and_front_matter_are_skipped(self):
        text = "---\nname: leverage — robust\n---\n```\nwe delve\n```\nUse `leverage` here.\n"
        self.assertEqual(rules_hit(text), set())

    def test_list_and_quote_prefixes_are_ignored(self):
        self.assertIn("stock opener", rules_hit("> Notably, it is fast."))
        self.assertIn("stock opener", rules_hit("- Moreover, it is small."))


class RepoTextTests(unittest.TestCase):
    def read(self, *parts):
        with open(os.path.join(*parts), encoding="utf-8") as f:
            return f.read()

    def test_examples_before_fails_and_after_passes(self):
        text = self.read(SKILL, "references", "examples.md")
        blocks = re.findall(r"^(Before|After):\n((?:>.*\n?)+)", text, re.M)
        self.assertGreaterEqual(len(blocks), 20)
        for kind, body in blocks:
            with self.subTest(kind=kind, body=body[:40]):
                hits = rules_hit(body)
                if kind == "Before":
                    self.assertTrue(hits, "a Before example should trip the checker")
                else:
                    self.assertEqual(hits, set())

    def test_own_prose_passes(self):
        for parts in [(ROOT, "README.md"), (SKILL, "references", "formats.md")]:
            with self.subTest(file=parts[-1]):
                text = re.sub(r"^Before:\n\n?(?:>.*\n?)+", "", self.read(*parts), flags=re.M)
                self.assertEqual(rules_hit(text), set())

    def test_skill_front_matter(self):
        text = self.read(SKILL, "SKILL.md")
        m = re.match(r"---\nname: (.+)\ndescription: (.+)\n---\n", text)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), "plainspoken")
        self.assertLessEqual(len(m.group(2)), 1024)


if __name__ == "__main__":
    unittest.main()
