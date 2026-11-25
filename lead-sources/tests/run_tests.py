"""Tests for lead-sources' scripts. Run: python tests/run_tests.py"""
import copy
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TESTS = []


def test(name):
    def wrap(fn):
        TESTS.append((name, fn))
        return fn
    return wrap


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, "scripts", f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cs = load("check_sources")
EXAMPLE = json.load(open(os.path.join(ROOT, "examples", "sources.json"), encoding="utf-8"))
HANDOFF_PATH = os.path.join(ROOT, "..", "icp-tam-builder", "examples", "icp-handoff.json")
HANDOFF = json.load(open(HANDOFF_PATH, encoding="utf-8")) if os.path.exists(HANDOFF_PATH) else None


def src():
    return copy.deepcopy(EXAMPLE)


def by_id(s, sid):
    return next(x for x in s["sources"] if x["id"] == sid)


@test("example passes with no errors, against the example handoff when it is present")
def _():
    errors, warns = cs.check(src(), copy.deepcopy(HANDOFF) if HANDOFF else None)
    assert errors == [], errors
    assert any("S2" in w and "forbid" in w for w in warns), warns
    assert any("S2" in w and "use with care" in w for w in warns), warns


@test("a missing top-level key is an error")
def _():
    s = src(); del s["gaps"]
    errors, _ = cs.check(s)
    assert errors and "gaps" in errors[0]


@test("a start source with no sample check is an error")
def _():
    s = src(); by_id(s, "S1")["sample"] = None
    errors, _ = cs.check(s)
    assert any("S1" in e and "not sample-checked" in e for e in errors), errors


@test("a sample count above the sample size is an error")
def _():
    s = src(); by_id(s, "S1")["sample"]["exists"] = 31
    errors, _ = cs.check(s)
    assert any("sample.exists" in e for e in errors), errors


@test("a sample under 20 gives a warning, not a rate")
def _():
    s = src(); by_id(s, "S1")["sample"].update(size=12, exists=11, fits_tier1=9, fields_ok=11)
    errors, warns = cs.check(s)
    assert errors == [] and any("under 20" in w for w in warns), (errors, warns)


@test("rated High with under 80% of the sample existing is an error")
def _():
    s = src(); by_id(s, "S1")["sample"]["exists"] = 20
    errors, _ = cs.check(s)
    assert any("rated High" in e for e in errors), errors


@test("a saved database search link is an error")
def _():
    s = src(); by_id(s, "S5")["url"] = "https://app.apollo.io/#/people?personTitles[]=practice%20manager"
    errors, _ = cs.check(s)
    assert any("saved database search" in e for e in errors), errors


@test("a blocked source must be ranked open_by_hand")
def _():
    s = src(); by_id(s, "S4")["access"] = "blocked"
    errors, _ = cs.check(s)
    assert any("S4" in e and "open_by_hand" in e for e in errors), errors


@test("a hit line with no source and no gap is an error; a gap entry fixes it")
def _():
    s = src(); s["sources"] = [x for x in s["sources"] if x["id"] != "S4"]
    errors, _ = cs.check(s)
    assert any("H3" in e and "no source and no gap" in e for e in errors), errors
    s["gaps"].append({"job": "H3", "what": "no job board lists clinic posts", "searched": "3 boards, 4 phrasings"})
    errors, _ = cs.check(s)
    assert errors == [], errors


@test("a gap must say what was searched")
def _():
    s = src(); s["gaps"].append({"job": "H4", "what": "none", "searched": ""})
    errors, _ = cs.check(s)
    assert any("say what was searched" in e for e in errors), errors


@test("a source pointing at an unknown hit line is an error")
def _():
    s = src(); by_id(s, "S2")["jobs"] = ["H9"]
    errors, _ = cs.check(s)
    assert any("H9" in e for e in errors), errors


@test("bad enum values are errors")
def _():
    s = src(); by_id(s, "S1")["reliability"] = "Very high"; by_id(s, "S1")["format"] = "word"
    errors, _ = cs.check(s)
    assert any("reliability" in e for e in errors) and any("format" in e for e in errors), errors


@test("a coverage figure that does not match records / market count gives a warning")
def _():
    s = src(); by_id(s, "S1")["coverage_pct"] = 50
    errors, warns = cs.check(s)
    assert errors == [] and any("does not match" in w for w in warns), (errors, warns)


@test("stopping before two empty rounds gives a warning")
def _():
    s = src(); s["search"]["empty_rounds_at_end"] = 1
    _, warns = cs.check(s)
    assert any("two empty rounds" in w for w in warns), warns


@test("an empty cannot_see is an error")
def _():
    s = src(); s["cannot_see"] = []
    errors, _ = cs.check(s)
    assert any("cannot_see" in e for e in errors), errors


@test("a draft review gives the draft warning")
def _():
    s = src(); s["review"]["status"] = "draft"
    _, warns = cs.check(s)
    assert any(w.startswith("Draft: ICP not reviewed") for w in warns), warns


@test("handoff: a signal with no signal hit line is an error")
def _():
    if HANDOFF is None:
        return
    s = src(); s["hit_lines"] = [h for h in s["hit_lines"] if h["id"] != "H4"]
    by_id(s, "S3")["jobs"] = ["H2"]
    errors, _ = cs.check(s, copy.deepcopy(HANDOFF))
    assert any("Opened a new branch" in e for e in errors), errors


@test("handoff: review status and market count must match the handoff")
def _():
    if HANDOFF is None:
        return
    s = src(); s["review"]["status"] = "draft"; s["market_count"]["companies"] = 999
    errors, _ = cs.check(s, copy.deepcopy(HANDOFF))
    assert any("review status" in e for e in errors) and any("market_count" in e for e in errors), errors


@test("unclear terms are grouped into one warning")
def _():
    s = src()
    for x in s["sources"]:
        x["terms"] = "unclear"
    _, warns = cs.check(s)
    u = [w for w in warns if "unclear for" in w]
    assert len(u) == 1 and "3 source(s)" in u[0], warns
    assert sum("terms of use were not read" in w for w in warns) == 2, warns


@test("main: exit codes 0, 1 and 2")
def _():
    import tempfile
    d = tempfile.mkdtemp()
    good = os.path.join(d, "good.json"); bad = os.path.join(d, "bad.json")
    json.dump(src(), open(good, "w", encoding="utf-8"))
    b = src(); b["cannot_see"] = []
    json.dump(b, open(bad, "w", encoding="utf-8"))
    devnull = open(os.devnull, "w")
    old = sys.stdout, sys.stderr
    sys.stdout = sys.stderr = devnull
    try:
        codes = (cs.main(["x", good]), cs.main(["x", bad]), cs.main(["x", os.path.join(d, "none.json")]))
    finally:
        sys.stdout, sys.stderr = old
        devnull.close()
    assert codes == (0, 1, 2), codes


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    passed = 0
    for name, fn in TESTS:
        try:
            fn()
            print(f"PASS  {name}")
            passed += 1
        except Exception as e:  # noqa: BLE001
            print(f"FAIL  {name}: {e!r}")
    print(f"\n{passed} of {len(TESTS)} passed")
    sys.exit(0 if passed == len(TESTS) else 1)
