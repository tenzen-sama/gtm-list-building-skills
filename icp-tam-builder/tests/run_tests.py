#!/usr/bin/env python3
"""Regression tests for the icp-tam-builder scripts.

Run from anywhere:  python tests/run_tests.py
Every test prints PASS or FAIL; the exit code is the number of failures.
Each test pins a bug found in the November 2026 audit, so a failure means it is back.
"""

import csv
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCRIPTS = os.path.join(ROOT, "scripts")
EXAMPLES = os.path.join(ROOT, "examples")


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(SCRIPTS, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


tam = load("tam_calc")
sc = load("score_accounts")
cl = load("check_links")
ch = load("check_handoff")
results = []


def test(name):
    def wrap(fn):
        try:
            fn()
            results.append((name, None))
        except Exception as e:  # noqa: BLE001 - report every failure, keep going
            results.append((name, f"{type(e).__name__}: {e}"))
        return fn
    return wrap


def example(name):
    with open(os.path.join(EXAMPLES, name), encoding="utf-8-sig") as f:
        return json.load(f)


def close(a, b, tol=0.01):
    assert abs(a - b) <= tol, f"{a} != {b}"


def exits(fn):
    try:
        fn()
    except SystemExit:
        return
    raise AssertionError("expected an error exit")


# --- tam_calc ---------------------------------------------------------------

@test("worked example in frameworks.md reproduces exactly")
def _():
    h = tam.calc(example("sizing-single.json"))["headline"]
    close(h["tam_bottom_up"], 15_360_000)
    close(h["tam_top_down"], 24_000_000)
    close(h["triangulation_ratio"], 1.5625, 0.001)
    close(h["sam_count"], 1344)
    close(h["sam"], 6_451_200)
    close(h["som_deals"], 24)
    close(h["som"], 115_200)


@test("percentages written as fractions are flagged")
def _():
    r = tam.calc({"acv": 10, "bottom_up": {"companies": 1000, "count_basis": "counted"},
                  "sam_filters": [{"name": "Lagos", "pct": 0.6}]})
    assert any("not fractions" in f for f in r["flags"]), r["flags"]


@test("percentages above 100 are an error")
def _():
    exits(lambda: tam.calc({"acv": 10, "bottom_up": {"companies": 10},
                            "sam_filters": [{"name": "x", "pct": 160}]}))


@test("SOM with two sales bases is an error, not a silent pick")
def _():
    exits(lambda: tam.calc({"acv": 100, "bottom_up": {"companies": 1000},
                            "som": {"deals_per_year": 5, "share_pct": 1}}))


@test("subsegment_pct accepts a single number")
def _():
    h = tam.calc({"top_down": {"market_size": 1000, "subsegment_pct": 30}})["headline"]
    close(h["tam_top_down"], 300)


@test("segments: total SOM is n/a when no segment has SOM inputs")
def _():
    h = tam.calc({"segments": [{"name": "A", "companies": 100, "acv": 10,
                                "count_basis": "counted"}]})["headline"]
    assert h["som"] is None, h["som"]


@test("segments: partial SOM is flagged")
def _():
    r = tam.calc({"segments": [
        {"name": "A", "companies": 100, "acv": 10, "count_basis": "counted", "deals_per_year": 2},
        {"name": "B", "companies": 100, "acv": 10, "count_basis": "counted"}]})
    assert any("No SOM inputs for B" in f for f in r["flags"]), r["flags"]


@test("segments: top_down and capacity SOM are used, not ignored")
def _():
    r = tam.calc(example("sizing-segments.json"))
    h = r["headline"]
    assert h["tam_top_down"] is not None and h["triangulation_ratio"] is not None
    large = r["units"][1]["som"]
    close(large["deals_per_year"], 4.8)


@test("delivery capacity caps SOM and says it binds")
def _():
    r = tam.calc(example("sizing-services.json"))
    s = r["units"][0]["som"]
    close(s["sales_deals"], 72)
    close(s["delivery_cap"], 15)
    close(s["deals_per_year"], 15)
    assert s["binding"] == "delivery capacity"


@test("derived company count makes triangulation non-independent")
def _():
    r = tam.calc({"acv": 10, "bottom_up": {"companies": 100, "count_basis": "derived"},
                  "top_down": {"market_size": 1000}})
    assert any("not independent" in f for f in r["flags"]), r["flags"]


@test("ranges give a low/base/high scenario and a sorted sensitivity table")
def _():
    base, scen, sens = tam.run(example("sizing-ranges.json"))
    assert scen["low"]["sam"] < scen["base"]["sam"] < scen["high"]["sam"]
    swings = [round(abs(s["at_high"] - s["at_low"]), 2) for s in sens]
    assert swings == sorted(swings, reverse=True), swings
    close(scen["base"]["sam"], 6_451_200)


@test("every example sizing file runs from the command line")
def _():
    for name in ("sizing-single.json", "sizing-ranges.json", "sizing-segments.json",
                 "sizing-services.json"):
        p = subprocess.run([sys.executable, "-I", os.path.join(SCRIPTS, "tam_calc.py"),
                            os.path.join(EXAMPLES, name)], capture_output=True)
        assert p.returncode == 0, (name, p.stderr.decode("utf-8", "replace"))


@test("UTF-8 names and currency symbols load on Windows")
def _():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "u.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"currency": "₦", "segments": [
                {"name": "Ōyọ clinics", "companies": 5, "acv": 10,
                 "count_basis": "counted"}]}, f, ensure_ascii=False)
        p = subprocess.run([sys.executable, "-I", os.path.join(SCRIPTS, "tam_calc.py"), path],
                           capture_output=True)
        assert p.returncode == 0, p.stderr.decode("utf-8", "replace")
        assert "Ōyọ" in p.stdout.decode("utf-8")


@test("unsourced inputs are listed; the fully sourced example lists none")
def _():
    base, _, _ = tam.run(example("sizing-single.json"))
    assert base["unsourced"] == [], base["unsourced"]
    base, _, _ = tam.run(example("sizing-services.json"))
    assert "Market: ACV" in base["unsourced"], base["unsourced"]
    assert any("SAM filter" in x for x in base["unsourced"]), base["unsourced"]
    ranged = {"acv": {"low": 1, "base": 2, "high": 3, "source": "price list"},
              "bottom_up": {"companies": 10, "count_basis": "counted", "count_source": "register"}}
    assert tam.run(ranged)[0]["unsourced"] == []


@test("count source type: aggregator-only count is flagged; a bad type is an error")
def _():
    r = tam.calc({"acv": 10, "bottom_up": {"companies": 100, "count_basis": "counted",
                                           "count_source_type": "aggregator"}})
    assert any("aggregator only" in f for f in r["flags"]), r["flags"]
    exits(lambda: tam.calc({"acv": 10, "bottom_up": {"companies": 100, "count_basis": "counted",
                                                     "count_source_type": "apollo"}}))


@test("reachable contacts = SAM companies x roles to reach")
def _():
    h = tam.calc(example("sizing-single.json"))["headline"]
    close(h["contacts"], 1344 * 2)
    assert tam.calc({"acv": 1, "bottom_up": {"companies": 5}})["headline"]["contacts"] is None


@test("invalid JSON gives a plain error, not a traceback")
def _():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "bad.json")
        with open(path, "w", encoding="utf-8") as f:
            f.write('{"acv": 10,  # a comment\n}')
        p = subprocess.run([sys.executable, "-I", os.path.join(SCRIPTS, "tam_calc.py"), path],
                           capture_output=True)
        err = p.stderr.decode("utf-8", "replace")
        assert p.returncode != 0 and "Traceback" not in err and "not valid JSON" in err, err


# --- score_accounts ---------------------------------------------------------

AS_OF = date(2026, 11, 17)
DQ_MODEL = {"bands": {"T1": 80, "T2": 50},
            "disqualifiers": [{"field": "country", "op": "not_in", "value": ["Nigeria"], "reason": "x"}],
            "rules": [{"field": "sector", "op": "in", "value": ["dental clinic"], "points": 0,
                       "required": True, "label": "Vertical"},
                      {"field": "employees", "op": "between", "value": [10, 50], "points": 100}]}


def score(row, model=DQ_MODEL):
    return sc.score_row(model, row, AS_OF)


@test("'unknown' never triggers a disqualifier")
def _():
    r = score({"country": "unknown", "sector": "dental clinic", "employees": "20"})
    assert r["dq"] is None and "country" in r["unknown"], r


@test("'unknown' on a gate caps at T2, not T3")
def _():
    r = score({"country": "Nigeria", "sector": "unknown", "employees": "20"})
    assert r["cap"] == "T2", r


@test("'Not hiring' is a no for truthy and yes operators")
def _():
    for op in ("truthy", "yes"):
        hit, _ = sc.evaluate({"op": op}, "Not hiring")
        assert hit is False, op
    assert sc.evaluate({"op": "truthy"}, "Northwind hiring")[0] is True


@test("headcount ranges and money suffixes are read")
def _():
    assert sc.parse_range("11-50") == (11, 50)
    assert sc.parse_range("10,000+") == (10000, float("inf"))
    assert sc.parse_range("$2M") == (2e6, 2e6)
    assert sc.parse_range("N50m") == (5e7, 5e7)
    assert sc.parse_range("2-5m") == (2e6, 5e6)
    assert sc.evaluate({"op": "between", "value": [10, 50]}, "11-50")[0] is True


@test("a range straddling the boundary is unknown, not a silent no")
def _():
    hit, note = sc.evaluate({"op": "gte", "value": 20}, "11-50")
    assert hit is None and "straddles" in note
    r = score({"country": "Nigeria", "sector": "dental clinic", "employees": "5-20"})
    assert "employees" in r["unknown"], r


@test("gate near miss is reported")
def _():
    r = score({"country": "Nigeria", "sector": "dental clinics", "employees": "20"})
    assert r["cap"] == "T3" and r["near"], r


@test("readiness decays with age and needs a date")
def _():
    rule = {"pillar": "readiness", "field": "hiring", "op": "yes", "points": 40,
            "date_field": "hiring_date", "max_age_days": 90}
    pts, _ = sc.decayed_points(rule, {"hiring_date": "2026-10-03"}, AS_OF)  # 45 days old
    close(pts, 20)
    pts, note = sc.decayed_points(rule, {"hiring_date": ""}, AS_OF)
    assert pts == 0 and "no usable date" in note


@test("gate points: warning at the Tier 1 floor, note at the Tier 2 floor")
def _():
    def model(a, b):
        return {"bands": {"T1": 80, "T2": 50}, "rules": [
            {"field": "v", "op": "eq", "value": "x", "points": a, "required": True},
            {"field": "c", "op": "eq", "value": "y", "points": b, "required": True},
            {"field": "e", "op": "gte", "value": 50, "points": 100 - a - b}]}
    w = sc.check_model(model(35, 25))
    assert any(x.startswith("note: gates carry 60") for x in w), w
    w = sc.check_model(model(50, 35))
    assert any(x.startswith("gates carry 85") and "Tier 1" in x for x in w), w
    assert not any("gates carry" in x for x in sc.check_model(model(20, 10)))


@test("action matrix: readiness picks the message, never whether to contact")
def _():
    t1 = ["T1"]
    assert sc.action_of("T1", 80, 50, t1) == sc.ACT_PRIORITISE
    assert sc.action_of("T1", 0, 50, t1) == sc.ACT_NO_SIGNAL
    assert sc.action_of("T2", 80, 50, t1) == sc.ACT_TIER2
    assert sc.action_of("T2", 80, 50, ["T1", "T2"]) == sc.ACT_PRIORITISE
    assert sc.action_of("T3", 80, 50, t1) == sc.ACT_VERIFY
    assert sc.action_of("T3", 0, 50, t1) == sc.ACT_DEPRIORITISE


@test("an unknown gate is never 'Prioritise now'")
def _():
    for tiers in (["T1"], ["T1", "T2"]):
        assert sc.action_of("T2", 100, 50, tiers, gate_unknown=True) == sc.ACT_GATE


@test("a counted pain field does not score praise or 'zero complaints'")
def _():
    rule = {"pillar": "readiness", "field": "booking_complaint_reviews_90d", "op": "gte",
            "value": 2, "points": 45}
    assert sc.evaluate(rule, "Reviews praise easy booking")[0] is None
    assert sc.evaluate(rule, "0")[0] is False
    assert sc.evaluate(rule, "3")[0] is True
    m = {"bands": {"T1": 80, "T2": 50}, "rules": [rule]}
    assert sc.score_row(m, {"booking_complaint_reviews_90d": "Zero complaints"}, AS_OF)["readiness"] == 0


@test("model warns when rules lack evidence or the model lacks built_from and evidence_tier")
def _():
    w = sc.check_model({"rules": [{"field": "a", "op": "eq", "value": 1, "points": 100}]})
    assert any("built_from" in x for x in w) and any("no 'evidence'" in x for x in w), w
    w = sc.check_model(example("scoring-model.json"))
    assert not any("evidence" in x or "built_from" in x for x in w), w


@test("low-confidence research on a gate or heaviest rule goes to the review queue")
def _():
    model = example("scoring-model.json")
    fields = sc.review_fields(model)
    assert {"vertical_group", "employees", "has_practice_manager",
            "booking_complaint_reviews_90d"} <= fields, fields
    row = {"vertical_group": "dental_clinic", "vertical_group__confidence": "Low",
           "employees__confidence": "high"}
    assert sc.low_confidence(row, fields) == ["vertical_group"]


@test("unknown operator is an error at load")
def _():
    exits(lambda: sc.check_model({"rules": [{"field": "a", "op": "equals", "value": 1, "points": 1}]}))


@test("example model and accounts score as expected end to end")
def _():
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "scored.csv")
        p = subprocess.run([sys.executable, "-I", os.path.join(SCRIPTS, "score_accounts.py"),
                            os.path.join(EXAMPLES, "scoring-model.json"),
                            os.path.join(EXAMPLES, "accounts.csv"), "-o", out],
                           capture_output=True)
        assert p.returncode == 0, p.stderr.decode("utf-8", "replace")
        with open(out, encoding="utf-8-sig", newline="") as f:
            rows = {r["company"]: r for r in csv.DictReader(f)}
    want = {"Example Clinic 1": ("T1", sc.ACT_PRIORITISE),
            "Example Clinic 2": ("T2", sc.ACT_TIER2),
            "Example Clinic 3": ("T2", sc.ACT_GATE),
            "Example Clinic 4": ("T3", sc.ACT_DEPRIORITISE),
            "Example Clinic 5": ("T3", sc.ACT_DEPRIORITISE),
            "Example Clinic 6": ("DQ", "Excluded: outside the cities served"),
            "Example Clinic 7": ("DQ", "Excluded: public procurement not supported"),
            "Example Clinic 8": ("T1", sc.ACT_NO_SIGNAL),
            "Example Clinic 9": ("DQ", "Excluded: current customer or open deal: do not prospect")}
    for company, (tier, action) in want.items():
        got = (rows[company]["fit_tier"], rows[company]["action"])
        assert got == (tier, action), (company, got)
    assert "near miss" in rows["Example Clinic 4"]["why"], rows["Example Clinic 4"]["why"]
    assert "vocabulary mismatches" in p.stdout.decode("utf-8"), "near-miss flag missing"


@test("flatten_research output feeds the scorer")
def _():
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "flat.csv")
        p = subprocess.run([sys.executable, "-I", os.path.join(SCRIPTS, "flatten_research.py"),
                            os.path.join(EXAMPLES, "research-output.json"), "-o", out],
                           capture_output=True)
        assert p.returncode == 0, p.stderr.decode("utf-8", "replace")
        with open(out, encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
    assert rows[0]["employees"] == "11-50" and rows[0]["employees__source"].endswith("/team")
    assert rows[0]["locations"] == "Lekki; Ikeja"
    assert sc.is_unknown(rows[1]["vertical_group"])
    assert rows[0]["hiring_front_desk_date"] == "2026-11-01"
    assert rows[1]["vertical_group__confidence"] == "low"


@test("flatten_research gives plain errors for bad JSON and a missing -o value")
def _():
    with tempfile.TemporaryDirectory() as d:
        bad = os.path.join(d, "bad.json")
        with open(bad, "w", encoding="utf-8") as f:
            f.write('[{"domain": "x.test",}]')
        for args in ([bad], [os.path.join(EXAMPLES, "research-output.json"), "-o"]):
            p = subprocess.run([sys.executable, "-I", os.path.join(SCRIPTS, "flatten_research.py"),
                                *args], capture_output=True)
            err = p.stderr.decode("utf-8", "replace")
            assert p.returncode != 0 and "Traceback" not in err and "error:" in err, err


# --- check_quotes -----------------------------------------------------------

def run_quotes(draft_text, sources, *extra):
    with tempfile.TemporaryDirectory() as d:
        draft = os.path.join(d, "draft.md")
        with open(draft, "w", encoding="utf-8") as f:
            f.write(draft_text)
        src = os.path.join(d, "transcripts")
        os.mkdir(src)
        for name, text in sources.items():
            with open(os.path.join(src, name), "w", encoding="utf-8") as f:
                f.write(text)
        p = subprocess.run([sys.executable, "-I", os.path.join(SCRIPTS, "check_quotes.py"),
                            draft, src, *extra], capture_output=True)
    return p.returncode, p.stdout.decode("utf-8", "replace")


CALL = {"call-1.md": "Practice manager: After four o'clock nobody picks up, and patients "
                     "just call the next clinic. We tried a paper diary first."}


@test("check_quotes finds a cited quote despite curly quotes and case")
def _():
    code, out = run_quotes("Top pain: “after four o’clock nobody picks up” (T1)", CALL)
    assert code == 0 and "1 of 1" in out, out


@test("check_quotes flags an altered quote and exits 1")
def _():
    code, out = run_quotes('Top pain: "after five o\'clock nobody picks up" (T1)', CALL)
    assert code == 1 and "NOT FOUND" in out, out


@test("check_quotes checks cut quotes in order and skips uncited ones unless --all")
def _():
    good = '"nobody picks up ... call the next clinic" (T1)'
    bad = '"call the next clinic ... nobody picks up" (T1)'
    assert run_quotes(good, CALL)[0] == 0
    assert run_quotes(bad, CALL)[0] == 1
    for cited in ('Pain: "nobody picks up, and patients" (call-1)',
                  'call-1 won: "we tried a paper diary first"',
                  '| Unanswered calls | 3 | "patients just call the next clinic" | call-1 |'):
        code, out = run_quotes(cited, CALL)
        assert code == 0 and "1 of 1" in out, (cited, out)
    uncited = 'The site says "booking software for every clinic".'
    assert run_quotes(uncited, CALL)[1].strip().startswith("0 of 0"), run_quotes(uncited, CALL)[1]
    assert run_quotes(uncited, CALL, "--all")[0] == 1


@test("check_quotes --all skips the skill's own action labels")
def _():
    draft = ('Action: "Contact now with the no-signal offer" and "Test after Tier 1". '
             'Header: "Draft: ICP not reviewed".')
    code, out = run_quotes(draft, CALL, "--all")
    assert code == 0 and out.strip().startswith("0 of 0"), out


# --- priority and confidence ------------------------------------------------

CONF_MODEL = {"bands": {"T1": 80, "T2": 50}, "readiness_high": 50, "high_fit_tiers": ["T1"],
              "rules": [
                  {"pillar": "fit", "field": "vertical", "op": "in", "value": ["mfb"],
                   "points": 40, "required": True},
                  {"pillar": "fit", "field": "agents", "op": "yes", "points": 60},
                  {"pillar": "readiness", "field": "hiring", "op": "yes", "points": 100,
                   "date_field": "hiring_date", "max_age_days": 90}]}


def conf(row):
    r = sc.score_row(CONF_MODEL, row, date(2026, 11, 20))
    return sc.confidence_of(CONF_MODEL, row, r, sc.review_fields(CONF_MODEL))


@test("priority follows the action; disqualified rows get none")
def _():
    assert sc.priority_of(sc.ACT_PRIORITISE) == "High"
    assert sc.priority_of(sc.ACT_NO_SIGNAL) == "Medium"
    assert sc.priority_of(sc.ACT_GATE) == "Medium"
    assert sc.priority_of(sc.ACT_TIER2) == "Low"
    assert sc.priority_of(sc.ACT_DEPRIORITISE) == "Low"
    assert sc.priority_of("Excluded: outside EMEA") == ""


@test("confidence is High with full data, Medium with a gap, Low with an unknown gate")
def _():
    full = {"vertical": "mfb", "agents": "yes", "hiring": "yes", "hiring_date": "2026-11-01"}
    assert conf(full) == "High", conf(full)
    assert conf({**full, "hiring_date": ""}) == "Medium"
    assert conf({**full, "agents": ""}) == "Medium"
    assert conf({**full, "vertical": ""}) == "Low"
    assert conf({**full, "agents": "", "hiring": ""}) == "Low"
    assert conf({**full, "vertical__confidence": "low"}) == "Low"
    assert conf({**full, "agents__confidence": "medium"}) == "Medium"


@test("scored CSV carries priority and confidence columns")
def _():
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "scored.csv")
        p = subprocess.run([sys.executable, "-I", os.path.join(SCRIPTS, "score_accounts.py"),
                            os.path.join(EXAMPLES, "scoring-model.json"),
                            os.path.join(EXAMPLES, "accounts.csv"), "-o", out],
                           capture_output=True)
        assert p.returncode == 0, p.stderr.decode("utf-8", "replace")
        with open(out, encoding="utf-8-sig", newline="") as f:
            rows = {r["company"]: r for r in csv.DictReader(f)}
    assert rows["Example Clinic 1"]["priority"] == "High"
    assert rows["Example Clinic 3"]["confidence"] == "Low"
    assert rows["Example Clinic 6"]["priority"] == "" and rows["Example Clinic 6"]["confidence"] == ""
    assert "Confidence (how sure each score is)" in p.stdout.decode("utf-8")


# --- check_links ------------------------------------------------------------

@test("check_links finds each link once and trims trailing punctuation")
def _():
    text = ("See https://a.test/x. Also (https://a.test/x) and | https://b.test/y |\n"
            "[job](https://c.test/jobs?id=1), https://a.test/x")
    assert cl.extract_urls(text) == ["https://a.test/x", "https://b.test/y",
                                     "https://c.test/jobs?id=1"], cl.extract_urls(text)


@test("check_links classifies statuses, and LinkedIn blocks as check by hand")
def _():
    assert cl.classify("https://a.test", 200) == "OK"
    assert cl.classify("https://a.test", 404) == "BROKEN"
    assert cl.classify("https://a.test", 500) == "ERROR"
    assert cl.classify("https://a.test", 0, "timed out") == "ERROR"
    assert cl.classify("https://www.linkedin.com/in/x", 999) == "CHECK BY HAND"
    assert cl.classify("https://ng.linkedin.com/in/x", 403) == "CHECK BY HAND"
    assert cl.classify("https://www.linkedin.com/in/x", 200) == "CHECK BY HAND"
    assert cl.classify("https://www.linkedin.com/in/x", 404) == "BROKEN"


@test("check_links reports OK and BROKEN against a local server, exit 1 on a broken link")
def _():
    import threading
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class H(BaseHTTPRequestHandler):
        def do_HEAD(self):
            self.send_response(200 if self.path == "/ok" else 404)
            self.end_headers()

        do_GET = do_HEAD

        def log_message(self, *a):
            pass

    srv = HTTPServer(("127.0.0.1", 0), H)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        with tempfile.TemporaryDirectory() as d:
            f = os.path.join(d, "list.md")
            with open(f, "w", encoding="utf-8") as fh:
                fh.write(f"| A | http://127.0.0.1:{port}/ok |\n| B | http://127.0.0.1:{port}/gone |\n")
            p = subprocess.run([sys.executable, "-I", os.path.join(SCRIPTS, "check_links.py"), f,
                                "--timeout", "5"], capture_output=True)
        out = p.stdout.decode("utf-8", "replace")
        assert p.returncode == 1, out
        assert f"OK" in out and "BROKEN" in out and "/gone" in out, out
    finally:
        srv.shutdown()


# --- check_handoff ----------------------------------------------------------

def handoff():
    return example("icp-handoff.json")


def hcheck(h):
    return ch.check(h, EXAMPLES)


@test("handoff: the example passes with no errors and no warnings")
def _():
    errors, warns = hcheck(handoff())
    assert errors == [] and warns == [], (errors, warns)


@test("handoff: example signals match the example scoring model's readiness rules")
def _():
    model = example("scoring-model.json")
    fields = {r["field"] for r in model["rules"] if r["pillar"] == "readiness"}
    assert {s["scoring_field"] for s in handoff()["signals"]} == fields


@test("handoff: example market figures match tam_calc on sizing-single.json")
def _():
    m = handoff()["market"]
    p = subprocess.run([sys.executable, "-I", os.path.join(SCRIPTS, "tam_calc.py"),
                        os.path.join(EXAMPLES, "sizing-single.json")], capture_output=True)
    text = p.stdout.decode("utf-8", "replace")
    for n in (m["tam"], m["sam"], m["sam_companies"], m["reachable_contacts"]):
        assert f"{n:,}" in text, f"{n:,} not in tam_calc output"


@test("handoff: a missing required section is an error")
def _():
    h = handoff(); del h["signals"]
    errors, _ = hcheck(h)
    assert any("signals" in e for e in errors), errors


@test("handoff: an ICP label below the floor of 8 customers is an error")
def _():
    h = handoff(); h["evidence"]["label"] = "ICP"
    errors, _ = hcheck(h)
    assert any("floor of 8" in e for e in errors), errors


@test("handoff: no current-customer exclusion is an error")
def _():
    h = handoff(); h["disqualifiers"] = [d for d in h["disqualifiers"] if "customer" not in d["rule"]]
    errors, _ = hcheck(h)
    assert any("current customers" in e for e in errors), errors


@test("handoff: a Tier 1 filter with no reason, or no evidence, is an error")
def _():
    h = handoff(); h["tiers"][0]["filters"][0]["why_it_matters"] = ""
    h["tiers"][0]["filters"][1]["evidence"] = ""
    errors, _ = hcheck(h)
    assert any("why_it_matters" in e for e in errors) and any("no evidence" in e for e in errors), errors


@test("handoff: an unknown filter needs no values; a blank one does")
def _():
    h = handoff(); f = h["tiers"][0]["filters"][2]
    f["values"] = None
    errors, _ = hcheck(h)
    assert any("no values" in e for e in errors), errors
    f["unknown"] = True
    errors, _ = hcheck(h)
    assert not any("no values" in e for e in errors), errors


@test("handoff: the champion must come first")
def _():
    h = handoff(); h["roles"].reverse()
    errors, _ = hcheck(h)
    assert any("champion first" in e for e in errors), errors


@test("handoff: draft review, Low signal, assumption and derived count are warnings, not errors")
def _():
    h = handoff()
    h["review"]["status"] = "draft"
    h["signals"][1]["reliability"] = "Low"
    h["tiers"][0]["filters"][2]["evidence"] = "[Assumption] typical clinic size"
    h["market"]["count_basis"] = "derived"
    errors, warns = hcheck(h)
    assert errors == [], errors
    for bit in ("Draft: ICP not reviewed", "Low reliability", "[Assumption]", "derived"):
        assert any(bit in w for w in warns), (bit, warns)


@test("handoff: a scoring_field missing from the scoring model is a warning")
def _():
    h = handoff(); h["signals"][0]["scoring_field"] = "not_a_field"
    _, warns = hcheck(h)
    assert any("not_a_field" in w for w in warns), warns


@test("handoff: --markdown prints Pack 1 with the header line and every Pack 1 item")
def _():
    p = subprocess.run([sys.executable, "-I", os.path.join(SCRIPTS, "check_handoff.py"),
                        os.path.join(EXAMPLES, "icp-handoff.json"), "--markdown"], capture_output=True)
    out = p.stdout.decode("utf-8", "replace")
    assert p.returncode == 0, p.stderr
    for bit in ("Evidence tier: Grounded | Label: Early Customer Profile | Scoring model:",
                "Roles to reach, champion first", "Trigger signals", "Reliability",
                "current customers and open deals", "When Tier 2 work starts",
                "Market list steps", "Per-account research prompts", "Test before scaling",
                "Data caution", "no-signal offer"):
        assert bit in out, bit


@test("handoff: a draft prints the draft label at the top of Pack 1")
def _():
    h = handoff(); h["review"]["status"] = "draft"
    assert "Draft: ICP not reviewed" in ch.markdown(h).split("\n## ")[0]


@test("handoff: a file with errors exits 1 and prints no Pack 1")
def _():
    h = handoff(); h["roles"] = []
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "bad.json")
        with open(f, "w", encoding="utf-8") as fh:
            json.dump(h, fh)
        p = subprocess.run([sys.executable, "-I", os.path.join(SCRIPTS, "check_handoff.py"), f,
                            "--markdown"], capture_output=True)
    assert p.returncode == 1 and b"# Pack 1" not in p.stdout, p.stdout


@test("handoff: warnings, open questions and the capacity note are printed in Pack 1")
def _():
    h = handoff(); h["sales_capacity"] = {"unknown": True, "note": "capacity not given"}
    _, warns = hcheck(h)
    out = ch.markdown(h, warns)
    assert "Carry forward" in out and "sales capacity unknown" in out, out[:400]
    assert "capacity not given" in out and "Open questions" in out


@test("handoff: count_basis none is allowed with a warning; anything else unknown is an error")
def _():
    h = handoff(); h["market"]["count_basis"] = "none"
    errors, warns = hcheck(h)
    assert errors == [] and any("no market count yet" in w for w in warns), (errors, warns)
    h["market"]["count_basis"] = "guessed"
    errors, _ = hcheck(h)
    assert any("counted, derived or none" in e for e in errors), errors


@test("handoff: a local consumer Pack 1 talks about people and audiences, not companies and CRMs")
def _():
    h = handoff(); h["client"]["client_type"] = "local_consumer"
    h["channels"] = {"catchment": ["within 10 minutes"], "ad_audiences": ["Instagram, ages 25 to 44"]}
    out = ch.markdown(h, [])
    tail = out.split("## For the list builder")[1]
    assert "members" in tail and "CRM" not in tail and "pull 100 companies" not in tail, tail
    assert "People or customers in the market" in out and "## Channels" in out


if __name__ == "__main__":
    fails = 0
    for name, err in results:
        print(f"{'PASS' if err is None else 'FAIL'}  {name}" + (f"\n      {err}" if err else ""))
        fails += err is not None
    print(f"\n{len(results) - fails} of {len(results)} passed")
    sys.exit(fails)
