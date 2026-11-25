#!/usr/bin/env python3
"""Score a list of companies against an ICP fit-and-readiness model.

Usage:
    python score_accounts.py model.json accounts.csv [-o out.csv] [--as-of YYYY-MM-DD]

Writes <accounts>_scored.csv beside the input (or to the -o path) and prints a summary.
Runnable examples: ../examples/scoring-model.json and ../examples/accounts.csv.
Copy the example model and edit it rather than writing one from scratch.

Model JSON keys
---------------
name, version, date       label the model; printed with every run
built_from                the brief (file name and date) the model was built from
evidence_tier             Hypothesis / Grounded / Validated, copied from that brief
                          (the script warns when either is missing, because the scored list
                          could not then be traced back to its evidence)
as_of                     date used to age readiness signals (default: today; --as-of wins)
bands                     {"T1": 80, "T2": 50}: fit-score floors; below T2 is T3
readiness_high            readiness score that counts as "high" (default 50)
high_fit_tiers            tiers treated as "high fit" in the action matrix (default ["T1"]).
                          Add "T2" only when Tier 2 rests on the same evidence as Tier 1
                          and the client can work both this quarter
disqualifiers             list of {"field", "op", "value", "reason", "evidence"}; a match
                          excludes the account. Current customers and open deals go here too
rules                     list of {"pillar": "fit" | "readiness", "field", "op", "value",
                          "points", "label", "evidence"}, plus optional:
                            "required": true        the rule is a gate
                            "date_field": "col"     column holding the signal's date
                            "max_age_days": 90      points fall in a straight line to 0 at this age
                          "evidence" says what justified the rule (separator test, transcript
                          IDs, Step 4 heuristic); the script warns when it is missing.

Actions (fit tier x readiness)
------------------------------
High fit (a tier in high_fit_tiers), readiness high   Prioritise now: pain-specific message
High fit, readiness low                               Contact now with the no-signal offer
Tier 2 when not in high_fit_tiers                     Test after Tier 1
Gate unknown (capped at Tier 2)                       Confirm the gate before contact
Tier 3, readiness high                                Verify fit before spending sales time;
                                                      light nurture
Tier 3, readiness low                                 Deprioritise
Readiness decides which message an account gets and how soon, not whether it is contacted.
An account whose gate is unknown is never "Prioritise now".

Research confidence
-------------------
If the CSV came from flatten_research.py, a column <field>__confidence may hold high /
medium / low. A row whose gate, heaviest fit rule or heaviest readiness rule rests on a
"low" value is listed in the needs_review column, for a person to check by hand.

Priority and confidence (two separate columns)
----------------------------------------------
priority     how much the account is wanted now, from the action:
               High    Prioritise now: pain-specific message
               Medium  Contact now with the no-signal offer; Confirm the gate before contact
               Low     Test after Tier 1; Verify fit...; Deprioritise
confidence   how sure the score is, from the data behind it (not how good the account is):
               Low     a gate is unknown, a gate or heaviest rule rests on "low" research,
                       or half or more of the rule fields are unknown
               Medium  any rule field is unknown or unreadable, a dated signal has no usable
                       date, or a gate or heaviest rule rests on "medium" research
               High    none of the above
A disqualified row gets neither.

Operators
---------
eq, in, not_in   exact match after lower-casing and trimming spaces. Score on a controlled
                 vocabulary (for example vertical_group = "dental_clinic") built before
                 scoring, not on raw descriptions. Gate near misses ("dental clinics"
                 against "dental clinic") are reported.
contains         substring match; value may be a string or a list of strings
yes              yes / y / true / 1 is a match; no / n / false / 0, or text that starts
                 with no / not / never / none, is a clear no; anything else is unknown
truthy           any text that is not a clear no ("Not hiring" is a no). It checks that a
                 value is present, NOT that a pain exists: "Reviews praise easy booking"
                 passes. To score a pain, use a counted field with gte and a date_field
                 (for example booking_complaint_reviews_90d gte 2)
between [lo, hi], gte, lte
                 numbers. Reads "1,000", "2.5M", "500k", "$2M", "N50m", ranges such as
                 "11-50" and open ranges such as "10,000+". A range that straddles the
                 rule's boundary ("11-50" against gte 20) is unknown, never guessed.

Unknown values
--------------
A blank cell, a marker such as unknown / n/a / tbc / not found, a value that cannot be read,
or a straddling range is unknown. Unknown earns nothing, never triggers a disqualifier, and
is reported per row (unknown_fields, data_issues) and per field in the summary.

Gates
-----
Known and not matching: the account is placed in Tier 3. Unknown: capped at Tier 2, because
an unconfirmed gate cannot earn the top tier. Gates may carry points (the vertical is often
both the gate and the heaviest weight). The script warns when gate points reach the Tier 1
floor, because every account that passes the gates would then land in Tier 1, and notes when
they reach the Tier 2 floor, because Tier 3 then holds only gate failures.

Positive points in each pillar should add up to 100; the script warns if not.
Only score on fields that can be found without a sales conversation; anything that needs a
discovery call belongs in qualification, not in the fit score.
"""

import csv
import json
import re
import sys
from datetime import date, datetime

TIER1_TOO_WIDE = 30  # warn if Tier 1 is more than this % of the scored list
UNKNOWN_WARN = 30    # warn if a model field is unknown for more than this % of rows

BLANKS = {"", "unknown", "unk", "n/a", "na", "-", "--", "?", "not found", "not stated",
          "null", "tbc", "tbd"}
YES = {"yes", "y", "true", "1"}
NEGATIVE = re.compile(r"^(?:no|n|false|0|none|nil|never|zero|not|nothing)$"
                      r"|^(?:no|not|never|none)\b")
OPS = {"eq", "in", "not_in", "contains", "yes", "truthy", "between", "gte", "lte"}
UNITS = {"k": 1e3, "thousand": 1e3, "m": 1e6, "mm": 1e6, "mn": 1e6, "million": 1e6,
         "b": 1e9, "bn": 1e9, "billion": 1e9}
NUM_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(thousand|million|billion|mm|mn|bn|k|m|b)?(?![a-z])")
DATE_FORMATS = ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%Y-%m")


def die(msg):
    raise SystemExit(f"error: {msg}")


def norm(v):
    return " ".join(str("" if v is None else v).split()).lower()


def is_unknown(v):
    return norm(v) in BLANKS


def parse_range(raw):
    """Return (low, high) for a number, a range or an open range; None if unreadable."""
    s = norm(raw).replace(",", "")
    found = NUM_RE.findall(s)
    if not found or len(found) > 2:
        return None
    if len(found) == 2 and not found[0][1] and found[1][1]:
        found[0] = (found[0][0], found[1][1])  # "2-5m" means 2m to 5m
    vals = [float(n) * UNITS.get(u, 1) for n, u in found]
    if len(vals) == 2:
        return (min(vals), max(vals))
    v = vals[0]
    if "+" in s or ">" in s or re.search(r"\b(over|above|more than|at least)\b", s):
        return (v, float("inf"))
    if "<" in s or re.search(r"\b(under|below|less than|fewer than|up to)\b", s):
        return (0.0, v)
    return (v, v)


def parse_date(raw):
    s = str(raw or "").strip()[:10]
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


def evaluate(rule, raw):
    """Return (True | False | None, note). None means unknown."""
    op, val = rule["op"], rule.get("value")
    s = norm(raw)
    if op == "yes":
        if s in YES:
            return True, None
        if NEGATIVE.search(s):
            return False, None
        return None, f"not a clear yes/no: {raw!r}"
    if op == "truthy":
        return (not NEGATIVE.search(s)), None
    if op == "eq":
        return s == norm(val), None
    if op == "in":
        return s in {norm(x) for x in val}, None
    if op == "not_in":
        return s not in {norm(x) for x in val}, None
    if op == "contains":
        items = val if isinstance(val, list) else [val]
        return any(norm(i) in s for i in items), None
    rng = parse_range(raw)
    if rng is None:
        return None, f"not a number: {raw!r}"
    lo, hi = rng
    if op == "between":
        a, b = val
        if lo >= a and hi <= b:
            return True, None
        if hi < a or lo > b:
            return False, None
    elif op == "gte":
        if lo >= val:
            return True, None
        if hi < val:
            return False, None
    elif op == "lte":
        if hi <= val:
            return True, None
        if lo > val:
            return False, None
    return None, f"range {raw!r} straddles the rule's boundary"


def loose(v):
    """Lower-case, treat _ and - as spaces, drop a plural s: for near-miss checks only."""
    words = re.sub(r"[_\-/]+", " ", norm(v)).split()
    return " ".join(w[:-1] if len(w) > 3 and w.endswith("s") else w for w in words)


def near_miss(rule, raw):
    if rule["op"] not in ("eq", "in"):
        return None
    s = loose(raw)
    targets = rule["value"] if isinstance(rule["value"], list) else [rule["value"]]
    for t in targets:
        lt = loose(t)
        if s and lt and (lt in s or s in lt):
            return norm(t)
    return None


def decayed_points(rule, row, as_of):
    raw = row.get(rule["date_field"], "")
    d = None if is_unknown(raw) else parse_date(raw)
    if d is None:
        return 0.0, f"no usable date in '{rule['date_field']}' ({raw!r}), so 0 points"
    age = (as_of - d).days
    max_age = rule.get("max_age_days")
    if not max_age or age <= 0:
        return float(rule["points"]), None
    factor = max(0.0, 1 - age / max_age)
    if factor == 0:
        return 0.0, f"signal is {age} days old, past {max_age}, so 0 points"
    return rule["points"] * factor, None


def score_row(model, row, as_of):
    unknown, issues, why, near = set(), [], [], []
    for d in model.get("disqualifiers", []):
        raw = row.get(d["field"], "")
        if is_unknown(raw):
            unknown.add(d["field"])
            continue
        hit, note = evaluate(d, raw)
        if hit is None:
            unknown.add(d["field"])
            issues.append(f"{d['field']}: {note}")
            continue
        if hit:
            return {"dq": d.get("reason", "disqualified"), "fit": 0, "readiness": 0, "cap": None,
                    "why": [f"Disqualified: {d.get('reason', d['field'])}"],
                    "unknown": sorted(unknown), "issues": issues, "near": near}

    totals = {"fit": 0.0, "readiness": 0.0}
    cap = None
    for r in model["rules"]:
        pillar = r.get("pillar", "fit")
        label = r.get("label", r["field"])
        raw = row.get(r["field"], "")
        hit = None
        if is_unknown(raw):
            unknown.add(r["field"])
        else:
            hit, note = evaluate(r, raw)
            if hit is None:
                unknown.add(r["field"])
                issues.append(f"{r['field']}: {note}")
        if hit is None:
            if r.get("required"):
                if cap != "T3":
                    cap = "T2"
                why.append(f"Gate unconfirmed: {label} (capped at T2)")
            continue
        if hit:
            pts = float(r["points"])
            if r.get("date_field"):
                pts, note = decayed_points(r, row, as_of)
                if note:
                    issues.append(f"{label}: {note}")
                    if "no usable date" in note:
                        unknown.add(r["date_field"])
            totals[pillar] += pts
            if pts:
                why.append(f"{label} ({round(pts, 1):+g})")
        elif r.get("required"):
            cap = "T3"
            miss = near_miss(r, raw)
            if miss:
                near.append((label, str(raw).strip(), miss))
                why.append(f"Gate failed: {label} (Tier 3; near miss: {str(raw).strip()!r} "
                           f"against {miss!r}, check the vocabulary)")
            else:
                why.append(f"Gate failed: {label} (Tier 3)")

    clamp = lambda x: max(0, min(100, round(x)))
    return {"dq": None, "fit": clamp(totals["fit"]), "readiness": clamp(totals["readiness"]),
            "cap": cap, "why": why, "unknown": sorted(unknown), "issues": issues, "near": near}


def tier_of(model, fit, cap=None):
    b = model["bands"]
    tier = "T1" if fit >= b["T1"] else "T2" if fit >= b["T2"] else "T3"
    order = {"T1": 1, "T2": 2, "T3": 3}
    if cap and order[cap] > order[tier]:
        tier = cap
    return tier


ACT_PRIORITISE = "Prioritise now: pain-specific message"
ACT_NO_SIGNAL = "Contact now with the no-signal offer"
ACT_TIER2 = "Test after Tier 1"
ACT_GATE = "Confirm the gate before contact"
ACT_VERIFY = "Verify fit before spending sales time; light nurture"
ACT_DEPRIORITISE = "Deprioritise"


def action_of(tier, readiness, high, high_fit_tiers, gate_unknown=False):
    """Readiness picks the message and the timing; it never decides alone whether to contact."""
    ready = readiness >= high
    if tier == "T3":
        return ACT_VERIFY if ready else ACT_DEPRIORITISE
    if gate_unknown:
        return ACT_GATE
    if tier in high_fit_tiers:
        return ACT_PRIORITISE if ready else ACT_NO_SIGNAL
    return ACT_TIER2


PRIORITY = {ACT_PRIORITISE: "High", ACT_NO_SIGNAL: "Medium", ACT_GATE: "Medium",
            ACT_TIER2: "Low", ACT_VERIFY: "Low", ACT_DEPRIORITISE: "Low"}


def priority_of(action):
    return PRIORITY.get(action, "")


def confidence_of(model, row, result, check_fields):
    """How sure the score is, from the data behind it: High, Medium or Low."""
    if result["dq"]:
        return ""
    rule_fields = {r["field"] for r in model["rules"]}
    unknown = set(result["unknown"])
    unknown_rules = unknown & rule_fields
    levels = {f: norm(row.get(f"{f}__confidence", "")) for f in check_fields}
    if (result["cap"] == "T2" or "low" in levels.values()
            or (rule_fields and len(unknown_rules) * 2 >= len(rule_fields))):
        return "Low"
    if unknown_rules or (unknown - rule_fields) or "medium" in levels.values():
        return "Medium"
    return "High"


def review_fields(model):
    """Fields whose low-confidence research should send a row to a person: the gates and the
    heaviest fit and readiness rules."""
    fields = {r["field"] for r in model["rules"] if r.get("required")}
    for pillar in ("fit", "readiness"):
        rules = [r for r in model["rules"] if r.get("pillar", "fit") == pillar and r["points"] > 0]
        if rules:
            top = max(r["points"] for r in rules)
            fields |= {r["field"] for r in rules if r["points"] == top}
    return fields


def low_confidence(row, fields):
    return sorted(f for f in fields if norm(row.get(f"{f}__confidence", "")) == "low")


def check_model(model):
    """Validate the model; return a list of warnings. Stops on errors."""
    if not isinstance(model.get("rules"), list) or not model["rules"]:
        die("the model needs a non-empty 'rules' list")
    model.setdefault("bands", {"T1": 80, "T2": 50})
    if not {"T1", "T2"} <= set(model["bands"]) or model["bands"]["T1"] <= model["bands"]["T2"]:
        die("'bands' needs T1 and T2, with T1 above T2")
    for kind, items in (("rule", model["rules"]), ("disqualifier", model.get("disqualifiers", []))):
        for i, r in enumerate(items, 1):
            where = f"{kind} {i} ({r.get('label', r.get('field', '?'))})"
            if "field" not in r or "op" not in r:
                die(f"{where} needs 'field' and 'op'")
            op = r["op"]
            if op not in OPS:
                die(f"{where}: unknown operator '{op}'. Use one of: {', '.join(sorted(OPS))}")
            if op in ("in", "not_in") and not isinstance(r.get("value"), list):
                die(f"{where}: '{op}' needs a list as 'value'")
            if op == "between" and not (isinstance(r.get("value"), list) and len(r["value"]) == 2):
                die(f"{where}: 'between' needs [low, high]")
            if op in ("eq", "contains", "gte", "lte") and "value" not in r:
                die(f"{where}: '{op}' needs a 'value'")
            if kind == "rule":
                if isinstance(r.get("points"), bool) or not isinstance(r.get("points"), (int, float)):
                    die(f"{where} needs numeric 'points'")
                if r.get("pillar", "fit") not in ("fit", "readiness"):
                    die(f"{where}: pillar must be 'fit' or 'readiness'")
                if r.get("max_age_days") and not r.get("date_field"):
                    die(f"{where}: 'max_age_days' needs a 'date_field'")

    warnings = []
    missing_meta = [k for k in ("built_from", "evidence_tier") if not model.get(k)]
    if missing_meta:
        warnings.append(f"the model has no {' or '.join(repr(k) for k in missing_meta)}, so the "
                        "scored list cannot be traced back to the brief and its evidence tier")
    unsourced = [r.get("label", r["field"]) for r in model["rules"] if not r.get("evidence")]
    unsourced += [f"disqualifier: {d.get('reason', d['field'])}"
                  for d in model.get("disqualifiers", []) if not d.get("evidence")]
    if unsourced:
        warnings.append(f"{len(unsourced)} rule(s) or disqualifier(s) have no 'evidence' saying what "
                        f"justified them: {'; '.join(unsourced)}")
    for pillar in ("fit", "readiness"):
        pts = sum(r["points"] for r in model["rules"]
                  if r.get("pillar", "fit") == pillar and r["points"] > 0)
        if pts and abs(pts - 100) > 1e-9:
            warnings.append(f"positive {pillar} points add up to {pts:g}, not 100")
    gate_pts = sum(r["points"] for r in model["rules"]
                   if r.get("required") and r.get("pillar", "fit") == "fit" and r["points"] > 0)
    if gate_pts and gate_pts >= model["bands"]["T1"]:
        warnings.append(
            f"gates carry {gate_pts:g} fit points, at or above the Tier 1 floor "
            f"({model['bands']['T1']}). Every account that passes the gates lands in Tier 1, so "
            "the model does not rank anything. Move points from the gates to the other fit rules.")
    elif gate_pts and gate_pts >= model["bands"]["T2"]:
        warnings.append(
            f"note: gates carry {gate_pts:g} fit points, at or above the Tier 2 floor "
            f"({model['bands']['T2']}). Every account that passes the gates starts in Tier 2, so "
            "Tier 3 holds only gate failures and the other rules decide Tier 1 versus Tier 2. "
            "Fine if intended; say so in the brief.")
    return warnings


def load_json(path):
    with open(path, encoding="utf-8-sig") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            die(f"{path} is not valid JSON ({e}). Comments are not allowed in JSON; "
                "copy a file from examples/ instead.")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    args = sys.argv[1:]
    opts = {}
    for flag in ("-o", "--as-of"):
        if flag in args:
            i = args.index(flag)
            if i + 1 >= len(args):
                die(f"{flag} needs a value")
            opts[flag] = args[i + 1]
            del args[i:i + 2]
    if len(args) != 2:
        raise SystemExit(__doc__)

    model = load_json(args[0])
    warnings = check_model(model)
    as_of_raw = opts.get("--as-of") or model.get("as_of")
    as_of = parse_date(as_of_raw) if as_of_raw else date.today()
    if as_of is None:
        die(f"cannot read the as-of date {as_of_raw!r}; use YYYY-MM-DD")

    with open(args[1], newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        cols = reader.fieldnames or []

    model_fields = ({r["field"] for r in model["rules"]}
                    | {r["date_field"] for r in model["rules"] if r.get("date_field")}
                    | {d["field"] for d in model.get("disqualifiers", [])})
    missing_cols = sorted(model_fields - set(cols))
    if missing_cols:
        warnings.append(f"columns not in the CSV (treated as unknown): {', '.join(missing_cols)}")
    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)

    high = model.get("readiness_high", 50)
    high_fit = model.get("high_fit_tiers", ["T1"])
    check_fields = review_fields(model)
    has_confidence = any(f"{f}__confidence" in cols for f in check_fields)
    scored = []
    unknown_count = {f: 0 for f in model_fields}
    unreadable = {}
    near_misses = []
    for row in rows:
        r = score_row(model, row, as_of)
        for f in r["unknown"]:
            unknown_count[f] = unknown_count.get(f, 0) + 1
        for issue in r["issues"]:
            field, _, note = issue.partition(": ")
            if note.startswith(("not a number", "not a clear", "range")):
                unreadable.setdefault(field, []).append(note)
        near_misses += r["near"]
        if r["dq"]:
            tier, act = "DQ", f"Excluded: {r['dq']}"
        else:
            tier = tier_of(model, r["fit"], r["cap"])
            act = action_of(tier, r["readiness"], high, high_fit, gate_unknown=r["cap"] == "T2")
        review = [] if r["dq"] else low_confidence(row, check_fields)
        scored.append({**row, "fit_score": r["fit"], "fit_tier": tier,
                       "readiness_score": r["readiness"], "action": act,
                       "priority": "" if r["dq"] else priority_of(act),
                       "confidence": confidence_of(model, row, r, check_fields),
                       "why": "; ".join(r["why"]), "unknown_fields": ", ".join(r["unknown"]),
                       "data_issues": "; ".join(r["issues"]),
                       "needs_review": ", ".join(f"{f} (low confidence)" for f in review)})

    out_path = opts.get("-o") or args[1].rsplit(".", 1)[0] + "_scored.csv"
    extra = ["fit_score", "fit_tier", "readiness_score", "action", "priority", "confidence",
             "why", "unknown_fields", "data_issues", "needs_review"]
    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(cols) + extra)
        w.writeheader()
        w.writerows(scored)

    n = len(scored) or 1
    print(f"Model: {model.get('name', '?')} v{model.get('version', '?')} "
          f"({model.get('date', 'undated')}); signals aged as of {as_of.isoformat()}")
    print(f"Evidence tier: {model.get('evidence_tier', 'not stated')}; "
          f"built from: {model.get('built_from', 'not stated')}")
    print(f"Scored {len(scored)} accounts -> {out_path}\n")
    print("| Tier | Accounts | Share |")
    print("|---|---|---|")
    shares = {}
    for t in ("T1", "T2", "T3", "DQ"):
        c = sum(1 for s in scored if s["fit_tier"] == t)
        shares[t] = c / n * 100
        print(f"| {t} | {c} | {shares[t]:.0f}% |")
    acts = {}
    for s in scored:
        acts[s["action"]] = acts.get(s["action"], 0) + 1
    print("\nActions:")
    for a, c in sorted(acts.items(), key=lambda x: -x[1]):
        print(f"- {a}: {c}")
    conf = [s["confidence"] for s in scored if s["confidence"]]
    if conf:
        print("\nConfidence (how sure each score is): " + ", ".join(
            f"{k} {conf.count(k)}" for k in ("High", "Medium", "Low")))

    flags = []
    if shares["T1"] > TIER1_TOO_WIDE:
        flags.append(f"Tier 1 is {shares['T1']:.0f}% of the list. The model may be describing the "
                     "market rather than discriminating within it. Find sharper attributes or "
                     "raise the T1 floor.")
    for f in sorted(unknown_count):
        c = unknown_count[f]
        if c / n * 100 > UNKNOWN_WARN:
            flags.append(f"Field '{f}' is unknown for {c / n * 100:.0f}% of accounts, so scores "
                         "that depend on it are unreliable.")
    for f, notes in sorted(unreadable.items()):
        flags.append(f"Field '{f}': {len(notes)} value(s) could not be scored, e.g. {notes[0]}.")
    if has_confidence:
        queue = [s.get("company") or s.get("domain") or "?" for s in scored if s["needs_review"]]
        if queue:
            more = "..." if len(queue) > 5 else ""
            flags.append(f"{len(queue)} account(s) rest on low-confidence research for a gate or "
                         f"the heaviest rule ({', '.join(queue[:5])}{more}). Check them by hand "
                         "before acting; see the needs_review column.")
    if near_misses:
        eg = near_misses[0]
        flags.append(f"{len(near_misses)} gate failure(s) look like vocabulary mismatches, e.g. "
                     f"{eg[1]!r} against {eg[2]!r} on '{eg[0]}'. Clean the column before trusting "
                     "Tier 3.")
    if flags:
        print("\nFlags:")
        for x in flags:
            print(f"- {x}")


if __name__ == "__main__":
    main()
