"""Check a lead-sources file (sources.json) before it is handed on.

Usage:
    python check_sources.py sources.json
    python check_sources.py sources.json --handoff icp-handoff.json

Errors mean the next skill would misread the file or the plan breaks a rule; the
script exits with 1. Warnings are things the plan must say plainly; they do not stop it.
Exit codes: 0 fine (warnings allowed), 1 errors, 2 the file could not be read.
"""
import json
import re
import sys

REQUIRED = ["sources_version", "client", "built_from", "review", "market_count",
            "hit_lines", "sources", "gaps", "search", "cannot_see"]
JOBS = {"market", "signal", "people", "tier2"}
RANKS = {"start", "add", "signal", "people", "open_by_hand", "not_used"}
ACCESS = {"free", "login", "paid", "blocked"}
FORMATS = {"html", "pdf", "csv", "xlsx", "api", "search_only"}
TERMS = {"allowed", "forbids_automated", "unclear"}
RELIABILITY = {"High", "Medium", "Low"}
SOURCE_FIELDS = ["id", "name", "url", "source_type", "jobs", "rank", "lists", "checked_on",
                 "access", "format", "terms", "reliability", "reliability_reason"]
# Signs that a URL is a saved database search rather than a page: this skill never writes those.
SEARCH_LINK = re.compile(r"(apollo\.io/#/(people|companies)\?|prospeo\.io/.*\?|clay\.com/.*\?|"
                         r"linkedin\.com/(sales|search)/)", re.I)


def blank(v):
    return v is None or v == "" or v == [] or v == {}


def rate(n, size):
    return n / size if size else 0.0


def check(s, handoff=None):
    errors, warns = [], []
    missing = [k for k in REQUIRED if k not in s]
    if missing:
        return [f"missing top-level keys: {', '.join(missing)}"], warns

    if s["review"].get("status") == "draft":
        warns.append("Draft: ICP not reviewed. The plan and every later output must carry that label")

    lines = {}
    for h in s["hit_lines"]:
        if blank(h.get("id")) or blank(h.get("line")):
            errors.append("a hit line has no id or no line")
            continue
        if h.get("job") not in JOBS:
            errors.append(f"hit line {h['id']}: job must be one of {', '.join(sorted(JOBS))}")
        lines[h["id"]] = h
    if not any(h.get("job") == "market" for h in s["hit_lines"]):
        errors.append("no market hit line: the plan has nothing to build the list from")

    ids, served, unclear = set(), set(), []
    market_count = s["market_count"].get("companies")
    for x in s["sources"]:
        sid = x.get("id", "?")
        gone = [f for f in SOURCE_FIELDS if blank(x.get(f))]
        if gone:
            errors.append(f"source {sid}: missing {', '.join(gone)}")
        if sid in ids:
            errors.append(f"source {sid}: id used twice")
        ids.add(sid)
        for f, allowed in (("rank", RANKS), ("access", ACCESS), ("format", FORMATS),
                           ("terms", TERMS), ("reliability", RELIABILITY)):
            if x.get(f) is not None and x.get(f) not in allowed:
                errors.append(f"source {sid}: {f} '{x.get(f)}' is not one of {', '.join(sorted(allowed))}")
        for j in x.get("jobs") or []:
            if j not in lines:
                errors.append(f"source {sid}: job {j} is not a hit line")
            elif x.get("rank") != "not_used":
                served.add(j)
        if SEARCH_LINK.search(x.get("url") or ""):
            errors.append(f"source {sid}: the url is a saved database search; name the database "
                          "and put the filters in filters_to_try instead")
        if x.get("terms") == "forbids_automated":
            warns.append(f"source {sid}: its terms forbid automated collection; manual or licensed use only")
        if x.get("terms") == "unclear":
            if x.get("rank") in ("start", "add"):
                warns.append(f"source {sid}: ranked {x.get('rank')} but its terms of use were not read; "
                             "read them before the list builder collects from it")
            else:
                unclear.append(sid)
        if x.get("access") == "blocked" and x.get("rank") not in ("open_by_hand", "not_used"):
            errors.append(f"source {sid}: blocked but ranked {x.get('rank')}; rank it open_by_hand")

        cov = x.get("coverage_pct")
        if cov is not None and not (0 <= cov <= 100):
            errors.append(f"source {sid}: coverage_pct must be between 0 and 100")
        if (cov is None and blank(x.get("coverage_note")) and x.get("rank") in ("start", "add")):
            errors.append(f"source {sid}: no coverage_pct and no coverage_note")
        if (cov is not None and x.get("records") is not None and isinstance(market_count, (int, float))
                and market_count > 0):
            expected = 100 * x["records"] / market_count
            if abs(expected - cov) > 1 and expected <= 100:
                warns.append(f"source {sid}: coverage_pct {cov} does not match records / market count "
                             f"({expected:.0f}%); say why in coverage_note")

        smp = x.get("sample")
        if x.get("rank") == "start" and blank(smp):
            errors.append(f"source {sid}: ranked start but not sample-checked")
        if not blank(smp):
            size = smp.get("size") or 0
            for f in ("exists", "fits_tier1", "fields_ok"):
                v = smp.get(f)
                if not isinstance(v, int) or v < 0 or v > size:
                    errors.append(f"source {sid}: sample.{f} must be a whole number from 0 to the sample size")
            if blank(smp.get("second_source")):
                errors.append(f"source {sid}: sample has no second_source")
            if size < 20:
                warns.append(f"source {sid}: sample of {size} is under 20; report the size, not a rate alone")
            elif rate(smp.get("exists") or 0, size) < 0.8 or rate(smp.get("fields_ok") or 0, size) < 0.8:
                warns.append(f"source {sid}: under 80% of the sample held up; use with care")
            if x.get("reliability") == "High" and size and rate(smp.get("exists") or 0, size) < 0.8:
                errors.append(f"source {sid}: rated High but under 80% of its sample exists")

    if unclear:
        warns.append(f"terms of use unclear for {len(unclear)} source(s) ({', '.join(unclear)}); "
                     "check each before collecting from it")

    for g in s["gaps"]:
        if g.get("job") not in lines:
            errors.append(f"gap for {g.get('job')}: not a hit line")
        elif blank(g.get("searched")):
            errors.append(f"gap for {g['job']}: say what was searched")
        else:
            served.add(g["job"])
    for hid in lines:
        if hid not in served:
            errors.append(f"hit line {hid}: no source and no gap entry")

    if not any(x.get("rank") == "start" for x in s["sources"]):
        warns.append("no source ranked start: the list builder has no complete list to begin from")

    sr = s["search"]
    if (sr.get("empty_rounds_at_end") or 0) < 2:
        warns.append("the search stopped before two empty rounds; coverage may be incomplete")
    if blank(s["cannot_see"]):
        errors.append("cannot_see is empty: say what the method could not see")

    if handoff is not None:
        names = {h.get("target") for h in s["hit_lines"] if h.get("job") == "signal"}
        for sig in handoff.get("signals", []):
            if sig.get("name") not in names:
                errors.append(f"handoff signal '{sig.get('name')}' has no signal hit line")
        hs = (handoff.get("review") or {}).get("status")
        if hs and hs != s["review"].get("status"):
            errors.append(f"review status '{s['review'].get('status')}' does not match the handoff ('{hs}')")
        hm = (handoff.get("market") or {}).get("companies")
        if hm != market_count:
            errors.append(f"market_count.companies {market_count} does not match the handoff ({hm})")
        if handoff.get("client", {}).get("client_type") == "local_consumer":
            if not any(h.get("job") == "market" for h in s["hit_lines"]):
                errors.append("local consumer client with no market hit line")
    return errors, warns


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    try:
        s = json.load(open(argv[1], encoding="utf-8"))
        handoff = None
        if "--handoff" in argv:
            handoff = json.load(open(argv[argv.index("--handoff") + 1], encoding="utf-8"))
    except (OSError, ValueError, IndexError) as e:
        print(f"could not read: {e}", file=sys.stderr)
        return 2
    errors, warns = check(s, handoff)
    for e in errors:
        print(f"error    {e}", file=sys.stderr)
    for w in warns:
        print(f"warning  {w}", file=sys.stderr)
    if errors:
        print(f"Sources file has {len(errors)} error(s): fix them before handing on.")
        return 1
    starts = sum(1 for x in s["sources"] if x.get("rank") == "start")
    print(f"Sources OK: {s['client'].get('name')}, {len(s['sources'])} source(s), {starts} to start from, "
          f"{len(s['gaps'])} gap(s), review {s['review'].get('status')}; {len(warns)} warning(s) to carry forward.")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv))
