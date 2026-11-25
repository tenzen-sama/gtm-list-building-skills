#!/usr/bin/env python3
"""Check that the customer quotes in a draft appear word for word in the source files.

Usage:
    python check_quotes.py draft.md transcripts/ [more files or folders] [--all]

The draft is any text file: the quote bank, the ICP sign-off message or the brief.
After it, list the transcript, interview or review files (or folders of them) that
the quotes should come from. Folders are searched for .md and .txt files.

A quote is text between double quotation marks, straight or curly, of four words or
more. By default only quotes with a source ID are checked, because those are the ones
the draft presents as a customer's own words: an ID right after the quote, such as
(T3), [T3], (call-2) or a table cell | call-2 |, or just before it and ending in a
colon or dash, such as T3: "..." or call-4 lost: "...". --all checks every quote of
four words or more, except the skill's own fixed labels (the scorer's action names and
"Draft: ICP not reviewed"), which are wording, not quotes.

Matching ignores case, curly versus straight quotes, dashes and runs of spaces.
"..." or an ellipsis character inside a quote marks a cut: each piece must appear, in
order, in the same file.

Exit code: 0 when every checked quote is found, 1 when any is not, 2 on a usage error.
"""

import os
import re
import sys
import unicodedata

MIN_WORDS = 4
QUOTE = re.compile(r'["“”]([^"“”\n]*)["“”]')
# A source ID: T3, I-4, R12, call-2, Call 2, transcript 5, interview 3, review 12
ID = (r"(?:[A-Za-z]{1,3}-?\d{1,3}"
      r"|(?:call|transcript|interview|review|survey)[\s#_-]*\d{1,3})\b")
# ...right after the closing quote: (T3), [T3], T3:, | call-2 |
SOURCE_AFTER = re.compile(r"^[\s,;:.|\-–—]{0,4}[(\[]?\s*" + ID, re.IGNORECASE)
# ...or just before the opening quote, ending in a colon or dash: T3: "...", call-4 lost: "..."
SOURCE_BEFORE = re.compile(r"\b" + ID + r"[^\"“”\n]{0,15}[:\-–—]\s*$",
                           re.IGNORECASE)


def die(msg):
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(2)


def norm(text):
    text = unicodedata.normalize("NFKC", text)
    for a, b in (("‘", "'"), ("’", "'"), ("“", '"'), ("”", '"'),
                 ("–", "-"), ("—", "-"), ("…", "...")):
        text = text.replace(a, b)
    return re.sub(r"\s+", " ", text).strip().lower()


def pieces(quote):
    parts = re.split(r"\s*(?:\.\.\.|\[\.\.\.\])\s*", norm(quote))
    return [p.strip(" .,;:!?'\"") for p in parts if p.strip(" .,;:!?'\"")]


def read(path):
    try:
        with open(path, encoding="utf-8-sig") as f:
            return f.read()
    except (OSError, UnicodeDecodeError) as e:
        die(f"cannot read {path}: {e}")


def source_files(paths):
    files = []
    for p in paths:
        if os.path.isdir(p):
            for root, _, names in os.walk(p):
                files += [os.path.join(root, n) for n in sorted(names)
                          if n.lower().endswith((".md", ".txt"))]
        elif os.path.isfile(p):
            files.append(p)
        else:
            die(f"not found: {p}")
    if not files:
        die("no source files to check against")
    return files


# The skill's own fixed wording, which drafts quote but no source contains.
OWN_LABELS = {
    "prioritise now: pain-specific message",
    "contact now with the no-signal offer",
    "test after tier 1",
    "confirm the gate before contact",
    "verify fit before spending sales time; light nurture",
    "draft: icp not reviewed",
    "draft: not for the client until the icp is reviewed",
    "what would improve this later",
}


def quotes_in(text, check_all):
    """Yield (quote, has_source_id) for every quote of MIN_WORDS words or more."""
    for line in text.splitlines():
        for m in QUOTE.finditer(line):
            q = m.group(1).strip()
            if len(q.split()) < MIN_WORDS:
                continue
            if norm(q).strip(" .") in OWN_LABELS:
                continue
            cited = bool(SOURCE_AFTER.match(line[m.end():]) or
                         SOURCE_BEFORE.search(line[:m.start()]))
            if cited or check_all:
                yield q, cited


def find(quote, sources):
    """Return the first source path containing every piece of the quote in order."""
    want = pieces(quote)
    for path, text in sources:
        pos = 0
        for piece in want:
            i = text.find(piece, pos)
            if i < 0:
                break
            pos = i + len(piece)
        else:
            return path
    return None


def main(argv):
    check_all = "--all" in argv
    args = [a for a in argv if a != "--all"]
    if len(args) < 2:
        die("usage: check_quotes.py draft.md source-file-or-folder [...] [--all]")
    draft = read(args[0])
    sources = [(p, norm(read(p))) for p in source_files(args[1:])]

    found, missing, seen = [], [], set()
    for q, cited in quotes_in(draft, check_all):
        if q in seen:
            continue
        seen.add(q)
        where = find(q, sources)
        (found if where else missing).append((q, where, cited))

    for q, where, _ in found:
        print(f"FOUND      \"{q}\"  ->  {os.path.basename(where)}")
    for q, _, cited in missing:
        note = "" if cited else "  (no source ID)"
        print(f"NOT FOUND  \"{q}\"{note}")
    print(f"\n{len(found)} of {len(found) + len(missing)} quotes found word for word"
          f" in {len(sources)} source file(s).")
    if missing:
        print("Fix or remove every NOT FOUND quote: a quote that is not in the source is"
              " an invented fact.")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
