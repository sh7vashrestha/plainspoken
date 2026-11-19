#!/usr/bin/env python3
"""List lines that may sound machine-made.

Usage: check.py FILE [FILE...]     or pipe text on stdin.

Every line printed is a candidate to review. Some hits are fine in context
(a technical term, a quotation). A single em dash is allowed; lines with
several, and files with many, are listed. Fenced code blocks, inline code and YAML
front matter are skipped. Exit code is 1 if anything was found.
"""
import re
import sys

I = re.IGNORECASE

RULES = [
    ("placeholder",
     r"\[[^\]\n]*\b(your|insert|needed|placeholder|tbd|to be added)\b[^\]\n]*\](?!\()|"
     r"\[(company|name|date|title|address|recipient|position|city|phone|email)\b[^\]\n]*\](?!\()|"
     r"\{\{[^}\n]+\}\}|\blorem ipsum\b", I,
     "fill it in or ask the user"),
    ("placeholder", r"\b(TBD|TODO|XXX+)\b", 0,
     "fill it in or ask the user"),
    ("chat leftover",
     r"\bas an? (AI|large language model)\b|\bas of my (last|knowledge)\b|\bcertainly! here\b|"
     r"\bhere(['’]s| is) (a|an|the|your) (revised|rewritten|updated|polished|improved)\b|"
     r"\blet me know if you(['’]d| would) like\b", I,
     "delete the line"),
    ("tool mark",
     r"【[^】\n]*】|\[oaicite[^\]\n]*\]|:contentReference|\bturn\d+(search|view|news)\d+\b|"
     r"utm_source=(chatgpt|openai)[\w.]*", I,
     "delete, or replace with a checked citation"),
    ("hidden character", r"[\u200b\u2060\ufeff\u00ad]", 0,
     "remove"),
    ("contrast flourish", r"\bnot only\b|\bnot just\b|\brather than\b|, not\b", I,
     "state the point; give the other side its own sentence"),
    ("inflated verb",
     r"\b(utili[sz]|leverag|harness|delv|facilitat|empower|foster|elevat|unlock|showcas|underscor)\w*", I,
     "use a plain verb"),
    ("hype word",
     r"\b(robust(ness)?|seamless(ly)?|comprehensive|cutting[- ]edge|state[- ]of[- ]the[- ]art|"
     r"game[- ]chang\w*|groundbreaking|revolutionary|transformative|unprecedented|"
     r"pivotal|crucial(ly)?|paramount|novel)\b", I,
     "say what it actually does"),
    ("metaphor filler",
     r"\b(landscape|realm|tapestry|journey|ecosystem|myriad|plethora|testament|beacon|cornerstone|"
     r"treasure trove|paradigm shift|dawn of time)\b", I,
     "name the thing"),
    ("stock opener",
     r"(^|[.!?]\s+)(Notably|Importantly|Crucially|Interestingly|Indeed|Moreover|Furthermore|"
     r"Additionally|Ultimately|Essentially)\b", 0,
     "delete the word"),
    ("filler phrase",
     r"\bit(['’]s| is) (worth noting|important to note)\b|\bin order to\b|\bdue to the fact\b|"
     r"\bplays? an? (crucial|key|vital|pivotal|significant) role\b|\bwhen it comes to\b|"
     r"\bproven track record\b|\bperfect fit\b", I,
     "cut to the verb"),
    ("stock framing",
     r"\bin today['’]s\b|\bever-(evolving|changing)\b|\bfast-paced\b|\bwhether you['’]re\b|"
     r"\bi hope this (email|message) finds you\b|\bthis (essay|paper|article) will explore\b", I,
     "start with the point"),
    ("stock closing",
     r"\bin conclusion\b|\bin summary\b|\bto sum up\b|\bhope this helps\b|\bgreat question\b", I,
     "end on the last real point"),
    ("it's not X, it's Y",
     r"\b(it|this|that)(['’]s| is) not (just |only |merely )?[^.;!?]{1,40}[,;] (it|this|that)(['’]s| is)\b", I,
     "say Y"),
    ("hedge stack",
     r"\b(may|might|could|can) (potentially|possibly|perhaps)\b|\b(potentially|possibly) (may|might|could)\b", I,
     "one hedge, or none"),
    ("vague pointer", r"\bthe (former|latter)\b", I,
     "name the thing again"),
    ("question lead-in",
     r"(^|[.!?]\s+)(The|Our|My|Its|And the|But the)(\s+[\w'’-]+){1,3}\?(?=\s+[A-Z])", 0,
     "make it a statement"),
    ("question heading", r"^#+ .*\?\s*$", 0,
     "name what the section contains"),
    ("emoji", r"[\U0001F300-\U0001FAFF\u2600-\u26FF\u2B50\u2B06]", 0,
     "remove"),
]
COMPILED = [(name, re.compile(rx, flags), hint) for name, rx, flags, hint in RULES]

DASH = re.compile(r"—| – | -- |(?<=\w)---?(?=\s)|(?<=\s)---(?=\w)")
DASH_HINT = "keep a dash only where nothing else works"

FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE = re.compile(r"`[^`]*`")
PREFIX = re.compile(r"^\s*(>\s*)*([-*+]\s+|\d+[.)]\s+)?(\*\*|__)?")


def check_lines(lines):
    """Yield (line_number, rule_name, matched_text, hint) for each hit."""
    in_fence = False
    in_front_matter = False
    dashes = words = 0
    for number, raw in enumerate(lines, 1):
        line = raw.rstrip("\n")
        if number == 1:
            line = line.lstrip("\ufeff")
        if number == 1 and line.strip() == "---":
            in_front_matter = True
            continue
        if in_front_matter:
            if line.strip() == "---":
                in_front_matter = False
            continue
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        text = INLINE_CODE.sub(" ", line)
        heading = text.lstrip().startswith("#")
        if not heading:
            text = PREFIX.sub("", text, count=1)
        for name, rx, hint in COMPILED:
            for m in rx.finditer(text):
                found = m.group(0)
                if name == "hidden character":
                    found = "U+%04X" % ord(found)
                yield number, name, found.strip(), hint
        found = DASH.findall(text)
        dashes += len(found)
        words += len(text.split())
        if len(found) > 1:
            yield number, "dash pile-up", f"{len(found)} dashes in one line", DASH_HINT
    if dashes > max(2, words // 300):
        yield 0, "dash overuse", f"{dashes} dashes in {words} words", DASH_HINT


def main(argv):
    if len(argv) > 1 and argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0
    sources = argv[1:] or ["-"]
    total = 0
    for path in sources:
        if path == "-":
            label, lines = "stdin", sys.stdin.readlines()
        else:
            label = path
            try:
                with open(path, encoding="utf-8") as f:
                    lines = f.readlines()
            except OSError as e:
                print(f"{path}: {e.strerror}", file=sys.stderr)
                return 2
        for number, name, found, hint in check_lines(lines):
            where = f"{label}:{number}" if number else label
            print(f'{where}: {name}: "{found}" ({hint})')
            total += 1
    print(f"{total} place(s) to review.", file=sys.stderr)
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
