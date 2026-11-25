"""Build Apollo search links from a spec, and read Apollo links back.

The model writes the spec; this script writes every link. It only uses URL
parameters that have been seen in a working link from the user's own Apollo
account (see references/apollo-parameters.md). Anything else the spec asks
for is reported as "not applied", never guessed.

Usage:
    python apollo_links.py build <spec.json> [--markdown] [--out <file.md>]
    python apollo_links.py parse "<apollo link>"
    python apollo_links.py compare "<link a>" "<link b>"
    python apollo_links.py learn-industry "<single-industry link>" "<Industry name>"
    python apollo_links.py industries [--status confirmed|probable|unverified|conflict]

Options:
    --dict <file>   industry list to use (default: references/apollo-industries.json)
"""
import copy
import json
import os
import re
import sys
from urllib.parse import quote, unquote

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEFAULT_DICT = os.path.join(ROOT, "references", "apollo-industries.json")

BASE = {"people": "https://app.apollo.io/#/people",
        "companies": "https://app.apollo.io/#/companies"}

# Location strings seen in a working link from the user's account.
CONFIRMED_LOCATIONS = {"united states"}

# Spec keys this script can apply. "pages" = the search pages the parameter
# has been seen on in a working link; on another allowed page it is applied
# with a warning; on a page not listed in "allowed" it is an error.
APPLIED = {
    "titles": {"param": "personTitles[]", "allowed": {"people"}, "seen": {"people"}},
    "person_locations": {"param": "personLocations[]", "allowed": {"people"}, "seen": {"people"}},
    "company_locations": {"param": "organizationLocations[]", "allowed": {"people", "companies"}, "seen": {"people"}},
    "headcount": {"param": "organizationNumEmployeesRanges[]", "allowed": {"people", "companies"}, "seen": {"people"}},
    "industries": {"param": "organizationIndustryTagIds[]", "allowed": {"people", "companies"}, "seen": {"people", "companies"}},
    "keywords": {"param": "qOrganizationKeywordTags[]", "allowed": {"people", "companies"}, "seen": {"people"}},
    "days_in_current_role": {"param": "personDaysInCurrentTitleRange", "allowed": {"people"}, "seen": {"people"}},
}

# Filters Apollo has but this script will not write, with the reason.
NOT_APPLIED = {
    "technologies": "Locked on the user's Free Apollo plan (user's account, 22 Nov 2026), and its link parameter has not been captured",
    "job_postings": "Locked on the user's Free Apollo plan, and its link parameter has not been captured",
    "funding": "Locked on the user's Free Apollo plan, and its link parameter has not been captured",
    "department_headcount": "Locked on the user's Free Apollo plan (# of employees by department), and its link parameter has not been captured",
    "revenue": "Marked as a plan filter in Apollo's article; its link parameter has not been captured",
    "buying_intent": "Marked as a plan filter in Apollo's article; its link parameter has not been captured",
    "seniority": "Management level is not available as a filter on the user's plan (user's account); use titles instead",
    "job_change": "Apollo's Job change filter only finds contacts who changed jobs since you saved them (Apollo's article); use days_in_current_role as the proxy",
    "exclude_companies": "No exclusion parameter has been captured from a working link yet",
    "exclude_titles": "No exclusion parameter has been captured from a working link yet",
    "exclude_industries": "No exclusion parameter has been captured from a working link yet",
    "exclude_keywords": "No exclusion parameter has been captured from a working link yet",
    "exclude_technologies": "Locked on the user's Free plan, and no exclusion parameter has been captured",
}

SEARCH_KEYS = set(APPLIED) | set(NOT_APPLIED) | {"page_type", "sort", "page"}

# Parameters this script recognises when reading a link back.
KNOWN_PARAMS = {"personTitles[]", "personLocations[]", "organizationLocations[]",
                "organizationNumEmployeesRanges[]", "organizationIndustryTagIds[]",
                "qOrganizationKeywordTags[]", "personDaysInCurrentTitleRange[min]",
                "personDaysInCurrentTitleRange[max]", "includedOrganizationKeywordFields[]",
                "sortByField", "sortAscending", "page", "recommendationConfigId"}
FILTER_PARAMS = KNOWN_PARAMS - {"includedOrganizationKeywordFields[]", "sortByField",
                                "sortAscending", "page", "recommendationConfigId"}

ID_RE = re.compile(r"^[0-9a-f]{24}$")


def enc(value):
    """Encode a value as Apollo's links do: spaces %20, commas %2C, brackets %5B %5D."""
    return quote(str(value), safe="")


# ---------------------------------------------------------------- industries

def load_dict(path=DEFAULT_DICT):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def find_industry(d, name):
    key = name.strip().lower()
    for e in d["industries"]:
        names = [e["name"]] + e.get("aliases", [])
        if key in (n.lower() for n in names):
            return e
    return None


def industry_by_id(d, iid):
    return [e for e in d["industries"] if e["id"] == iid]


# ---------------------------------------------------------------- spec

def expand(spec):
    """Turn base + searches into a list of (name, filters) pairs."""
    base = spec.get("base", {})
    searches = spec.get("searches") or [{"name": spec.get("name", "Search")}]
    out = []
    for s in searches:
        f = copy.deepcopy(base)
        for k in s.get("drop", []):
            f.pop(k, None)
        f.update(copy.deepcopy(s.get("set", {})))
        out.append((s.get("name", "Search"), f))
    return out


def build_one(name, f, d):
    """Build one link. Returns dict with url, contains, warnings, errors, not_applied."""
    errors, warnings, contains, not_applied = [], [], [], []
    page_type = f.get("page_type", "people")
    if page_type not in BASE:
        errors.append(f"page_type must be 'people' or 'companies', not {page_type!r}")
        return {"name": name, "url": "", "contains": contains, "warnings": warnings,
                "errors": errors, "not_applied": not_applied}

    for k in f:
        if k not in SEARCH_KEYS:
            errors.append(f"Unknown spec key {k!r}. Use one of: {', '.join(sorted(SEARCH_KEYS))}")
    for k in NOT_APPLIED:
        if f.get(k):
            not_applied.append({"filter": k, "value": f[k], "reason": NOT_APPLIED[k]})

    for k, rule in APPLIED.items():
        if f.get(k) in (None, [], {}):
            continue
        if page_type not in rule["allowed"]:
            errors.append(f"{k} is a person filter and can't be used on the {page_type} search page")
        elif page_type not in rule["seen"]:
            warnings.append(f"{k} has only been seen on {'/'.join(sorted(rule['seen']))} search in a working link; "
                            f"check its chip appears on the {page_type} page")

    p = []  # (param, encoded value) in Apollo's observed order

    def lst(key):
        v = f.get(key) or []
        if isinstance(v, str):
            errors.append(f"{key} must be a list, not a single string")
            return []
        return v

    if page_type == "people":
        for t in lst("titles"):
            p.append(("personTitles[]", enc(t.strip().lower())))
        if lst("titles"):
            contains.append("Titles: " + ", ".join(t.strip().lower() for t in lst("titles")))
        for loc in lst("person_locations"):
            p.append(("personLocations[]", enc(loc.strip().lower())))
        if lst("person_locations"):
            contains.append("Person location: " + ", ".join(lst("person_locations")))

    for loc in lst("company_locations"):
        p.append(("organizationLocations[]", enc(loc.strip().lower())))
    if lst("company_locations"):
        contains.append("Company HQ location: " + ", ".join(lst("company_locations")))
    for loc in lst("person_locations") + lst("company_locations"):
        if loc.strip().lower() not in CONFIRMED_LOCATIONS:
            warnings.append(f"Location {loc!r} hasn't been seen in a working link yet; check its chip shows up")

    for r in lst("headcount"):
        if not isinstance(r, dict) or r.get("min") is None or r.get("max") is None:
            errors.append("Each headcount range needs a min and a max, for example {\"min\": 100, \"max\": 5000}. "
                          "An open-ended range's link format hasn't been captured")
            continue
        if r["min"] > r["max"]:
            errors.append(f"Headcount min {r['min']} is above max {r['max']}")
            continue
        p.append(("organizationNumEmployeesRanges[]", enc(f"{r['min']},{r['max']}")))
        contains.append(f"Headcount: {r['min']} to {r['max']}")

    ind_names = []
    for n in lst("industries"):
        e = find_industry(d, n)
        if e is None:
            errors.append(f"Industry {n!r} has no Apollo ID yet. In Apollo, tick only that industry, copy the link, "
                          f"and run: learn-industry \"<link>\" \"{n}\"")
            continue
        if e["status"] == "conflict":
            errors.append(f"Industry {e['name']!r} has a disputed ID ({e.get('note', 'see the industry list')}). "
                          f"Capture a single-industry link first")
            continue
        if e["status"] == "probable":
            warnings.append(f"Industry {e['name']!r} ID is probable, not confirmed; check the chip reads {e['name']}")
        elif e["status"] == "unverified":
            warnings.append(f"Industry {e['name']!r} ID comes from an outside list and is unverified; "
                            f"check the chip reads {e['name']}")
        p.append(("organizationIndustryTagIds[]", e["id"]))
        ind_names.append(e["name"])
    if ind_names:
        contains.append("Industries: " + ", ".join(ind_names))

    kws = lst("keywords")
    for k in kws:
        p.append(("qOrganizationKeywordTags[]", enc(k.strip())))
    if kws:
        contains.append("Company keywords (any): " + ", ".join(kws))

    if page_type == "companies":
        p.append(("includedOrganizationKeywordFields[]", "tags"))
        p.append(("includedOrganizationKeywordFields[]", "name"))
        p.append(("sortAscending", "false"))
        p.append(("sortByField", enc(f.get("sort", "recommendations_score"))))
        p.append(("page", str(f.get("page", 1))))
    else:
        p.append(("sortByField", enc(f.get("sort", "recommendations_score"))))
        p.append(("sortAscending", "false"))
        p.append(("page", str(f.get("page", 1))))
        days = f.get("days_in_current_role")
        if days:
            lo, hi = days.get("min", 0), days.get("max")
            if hi is None:
                errors.append("days_in_current_role needs a max (in days)")
            elif lo > hi:
                errors.append(f"days_in_current_role min {lo} is above max {hi}")
            else:
                p.append(("personDaysInCurrentTitleRange[max]", str(hi)))
                p.append(("personDaysInCurrentTitleRange[min]", str(lo)))
                contains.append(f"Time in current role: {lo} to {hi} days")
    p.append(("recommendationConfigId", "score"))

    if not contains:
        errors.append("This search has no filters, so it would return all of Apollo")
    url = "" if errors else BASE[page_type] + "?" + "&".join(f"{k}={v}" for k, v in p)
    return {"name": name, "page_type": page_type, "url": url, "contains": contains,
            "warnings": warnings, "errors": errors, "not_applied": not_applied}


def build(spec, d):
    return [build_one(n, f, d) for n, f in expand(spec)]


def to_markdown(spec, results):
    lines = [f"# Apollo searches: {spec.get('name', 'untitled')}", ""]
    if spec.get("built_from"):
        lines += [f"Built from: {spec['built_from']}. Every link was written by `apollo_links.py`, not by hand.", ""]
    lines += ["Open each link while logged in to Apollo. Check that the filter chips match \"Contains\", "
              "and note the result count.", ""]
    for r in results:
        lines += [f"## {r['name']}", ""]
        if r["errors"]:
            lines += ["**Not built:**", ""] + [f"- {e}" for e in r["errors"]] + [""]
            continue
        lines += [r["url"], "", "**Contains:**", ""] + [f"- {c}" for c in r["contains"]] + [""]
        if r["warnings"]:
            lines += ["**Check when you open it:**", ""] + [f"- {w}" for w in r["warnings"]] + [""]
        if r["not_applied"]:
            lines += ["**Asked for but not applied:**", ""]
            lines += [f"- {n['filter']} ({fmt(n['value'])}): {n['reason']}" for n in r["not_applied"]] + [""]
    return "\n".join(lines).rstrip() + "\n"


def fmt(v):
    """Show a spec value in plain words: {"department": "Sales", "min": 20} -> "department Sales, min 20"."""
    if isinstance(v, list):
        return "; ".join(fmt(x) for x in v)
    if isinstance(v, dict):
        return ", ".join(f"{k.replace('_', ' ')} {x}" for k, x in v.items())
    return str(v)


# ---------------------------------------------------------------- reading links

def split_link(url):
    url = url.strip().replace("\\[", "[").replace("\\]", "]").replace("\\&", "&")
    if "?" not in url:
        return url, []
    base, q = url.split("?", 1)
    return base, [tuple(x.split("=", 1)) if "=" in x else (x, "") for x in q.split("&") if x]


def parse(url, d=None):
    """Read an Apollo link back into a spec-like dict, plus anything unrecognised."""
    base, params = split_link(url)
    page_type = "companies" if base.endswith("#/companies") else "people" if base.endswith("#/people") else None
    f, unknown, notes = {"page_type": page_type}, [], []
    days = {}
    for k, v in params:
        val = unquote(v)
        if k == "personTitles[]":
            f.setdefault("titles", []).append(val)
        elif k == "personLocations[]":
            f.setdefault("person_locations", []).append(val)
        elif k == "organizationLocations[]":
            f.setdefault("company_locations", []).append(val)
        elif k == "organizationNumEmployeesRanges[]":
            lo, _, hi = val.partition(",")
            f.setdefault("headcount", []).append({"min": int(lo), "max": int(hi) if hi else None})
        elif k == "organizationIndustryTagIds[]":
            hits = industry_by_id(d, val) if d else []
            label = f"{hits[0]['name']} ({hits[0]['status']})" if len(hits) == 1 else "unknown industry" if not hits \
                else "disputed: " + " / ".join(h["name"] for h in hits)
            f.setdefault("industry_ids", []).append({"id": val, "industry": label})
        elif k == "qOrganizationKeywordTags[]":
            f.setdefault("keywords", []).append(val)
        elif k == "personDaysInCurrentTitleRange[min]":
            days["min"] = int(val)
        elif k == "personDaysInCurrentTitleRange[max]":
            days["max"] = int(val)
        elif k == "sortByField":
            f["sort"] = val
        elif k == "page":
            f["page"] = int(val) if val.isdigit() else val
        elif k not in KNOWN_PARAMS:
            unknown.append({"param": k, "value": val})
    if days:
        f["days_in_current_role"] = days
    if page_type is None:
        notes.append("Not an Apollo people or companies search link")
    if not any(k in FILTER_PARAMS for k, _ in params):
        notes.append("This link carries no filters this script can read. If you set filters before copying it, "
                     "your account may be on Apollo's 'Filters 2.0', where links no longer hold the filters: "
                     "then this skill can't build Apollo links for you")
    if unknown:
        notes.append("Unrecognised parameters: work out which filter each one is before adding it to the skill")
    return {"filters": f, "unknown_params": unknown, "notes": notes}


def compare(a, b):
    """Compare two links as sets of parameters, ignoring order."""
    from collections import Counter
    ba, pa = split_link(a)
    bb, pb = split_link(b)
    ca = Counter((k, unquote(v)) for k, v in pa)
    cb = Counter((k, unquote(v)) for k, v in pb)
    return {"same_page": ba == bb, "only_in_a": sorted((ca - cb).elements()),
            "only_in_b": sorted((cb - ca).elements()), "same": ba == bb and ca == cb}


def learn_industry(url, name, path=DEFAULT_DICT, today=None):
    """Record an industry ID from a link with exactly one industry ticked."""
    _, params = split_link(url)
    ids = [unquote(v) for k, v in params if k == "organizationIndustryTagIds[]"]
    if len(ids) != 1:
        raise ValueError(f"The link holds {len(ids)} industry IDs; it needs exactly one, so the match is certain")
    iid = ids[0]
    if not ID_RE.match(iid):
        raise ValueError(f"{iid!r} doesn't look like an Apollo industry ID (24 hex characters)")
    d = load_dict(path)
    source = f"User's single-industry Apollo link{', ' + today if today else ''}"
    e = find_industry(d, name)
    clash = [x for x in industry_by_id(d, iid) if x is not e]
    if e:
        old = (e["id"], e["status"])
        e.update({"id": iid, "status": "confirmed", "source": source})
        e.pop("note", None)
        msg = f"Updated {e['name']}: {old[0]} ({old[1]}) -> {iid} (confirmed)"
    else:
        d["industries"].append({"name": name.strip(), "id": iid, "status": "confirmed", "source": source})
        msg = f"Added {name.strip()}: {iid} (confirmed)"
    for x in clash:
        if x["status"] != "confirmed":
            x["status"] = "conflict"
            x["note"] = f"Shares ID {iid} with the confirmed industry {name.strip()}"
            msg += f"\nMarked {x['name']} as conflict: it listed the same ID"
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(d, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return msg


# ---------------------------------------------------------------- CLI

def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = list(argv)
    path = DEFAULT_DICT
    if "--dict" in args:
        i = args.index("--dict")
        path = args[i + 1]
        del args[i:i + 2]
    if not args:
        print(__doc__)
        return 2
    cmd = args[0]
    d = load_dict(path)
    if cmd == "build":
        spec = json.load(open(args[1], encoding="utf-8"))
        results = build(spec, d)
        text = to_markdown(spec, results)
        if "--out" in args:
            out = args[args.index("--out") + 1]
            with open(out, "w", encoding="utf-8") as fh:
                fh.write(text)
            print(f"Wrote {out}")
        if "--markdown" in args or "--out" not in args:
            print(text)
        bad = [r["name"] for r in results if r["errors"]]
        if bad:
            print("NOT BUILT: " + "; ".join(bad))
            return 1
        print(f"{len(results)} link(s) built")
        return 0
    if cmd == "parse":
        print(json.dumps(parse(args[1], d), indent=2, ensure_ascii=False))
        return 0
    if cmd == "compare":
        r = compare(args[1], args[2])
        print(json.dumps(r, indent=2, ensure_ascii=False))
        return 0 if r["same"] else 1
    if cmd == "learn-industry":
        print(learn_industry(args[1], args[2], path))
        return 0
    if cmd == "industries":
        status = args[args.index("--status") + 1] if "--status" in args else None
        for e in sorted(d["industries"], key=lambda x: x["name"].lower()):
            if status is None or e["status"] == status:
                print(f"{e['status']:<11} {e['id']}  {e['name']}")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
