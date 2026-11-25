"""Build Prospeo search links from a spec, and read Prospeo links back.

A Prospeo search link is the filter set as compact JSON, base64url-encoded
with no padding, after https://app.prospeo.io/search/people/ (worked out from
the user's own captured links, 17 Nov 2026). The model writes the spec; this
script writes every link. Filter keys and allowed values come from Prospeo's
official filters documentation and value lists (references/prospeo-keys.json,
references/prospeo-values.json). Anything else the spec asks for is reported
as "not applied", never guessed.

Usage:
    python prospeo_links.py build <spec.json> [--markdown] [--out <file.md>]
    python prospeo_links.py parse "<prospeo link>"
    python prospeo_links.py compare "<link a>" "<link b>"
    python prospeo_links.py confirm-key <prospeo_key> "<link from the user's dashboard>"
    python prospeo_links.py values industries|seniorities|departments|employee_ranges [<search text>]
"""
import base64
import copy
import difflib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
KEYS_FILE = os.path.join(ROOT, "references", "prospeo-keys.json")
VALUES_FILE = os.path.join(ROOT, "references", "prospeo-values.json")
BASE = "https://app.prospeo.io/search/people/"

# Spec keys that are recorded and reported, never written into a link.
NOT_APPLIED = {
    "technologies": ("company_technology", None),
    "exclude_technologies": ("company_technology", None),
    "job_postings": ("company_job_posting_hiring_for", None),
    "funding": ("company_funding", None),
    "revenue": ("company_revenue", None),
    "job_change": ("person_job_change", None),
    "key_exec_changes": ("company_key_execs", None),
    "buying_intent": (None, "Prospeo's Free plan includes 3 intent topics, but this script doesn't write the intent filter yet"),
    "exclude_companies": (None, "Company include/exclude lists aren't written by this script yet"),
}

APPLIED = {"titles", "exclude_titles", "title_match", "similar_intensity",
           "person_locations", "exclude_person_locations", "company_locations", "exclude_company_locations",
           "headcount", "headcount_ranges", "industries", "exclude_industries",
           "keywords", "exclude_keywords", "keywords_match_all",
           "seniority", "exclude_seniority", "departments", "exclude_departments",
           "department_headcount", "months_in_current_role"}
LABELS = {"person_job_title": "job title", "person_location_search": "person location",
          "company_location_search": "company HQ location", "company_headcount_custom": "headcount",
          "company_headcount_range": "headcount bands", "company_industry": "industry", "company_keywords": "keywords",
          "person_seniority": "seniority", "person_department": "department",
          "company_headcount_by_department": "department headcount", "person_time_in_current_role": "time in current role"}
# Filters that always narrow by inclusion (no exclude form).
POSITIVE_ALWAYS = {"company_headcount_custom", "company_headcount_range", "company_headcount_by_department",
                   "person_time_in_current_role"}
SEARCH_KEYS = APPLIED | set(NOT_APPLIED) | {"page_type", "days_in_current_role"}


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def encode(filters):
    raw = json.dumps(filters, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def decode(token):
    token = token.strip().split("?")[0].split("#")[0].rstrip("/")
    return json.loads(base64.urlsafe_b64decode(token + "=" * (-len(token) % 4)).decode("utf-8"))


def expand(spec):
    base = spec.get("base", {})
    out = []
    for s in spec.get("searches") or [{"name": spec.get("name", "Search")}]:
        f = copy.deepcopy(base)
        for k in s.get("drop", []):
            f.pop(k, None)
        f.update(copy.deepcopy(s.get("set", {})))
        out.append((s.get("name", "Search"), f))
    return out


def check_enum(values, allowed, label, errors):
    good = []
    lower = {a.lower(): a for a in allowed}
    for v in values:
        if v in allowed:
            good.append(v)
        elif v.lower() in lower:
            good.append(lower[v.lower()])
        else:
            near = difflib.get_close_matches(v, allowed, n=3, cutoff=0.5)
            errors.append(f"{label} {v!r} isn't one of Prospeo's values" + (f". Closest: {', '.join(near)}" if near else
                          f". Run: values {label.lower()}s <search text>"))
    return good


def build_one(name, f, keys, values):
    errors, warnings, contains, not_applied = [], [], [], []
    st = keys["keys"]
    plan = keys.get("user_plan", "Free")
    if f.get("page_type", "people") != "people":
        errors.append("Only people search is supported for Prospeo: the company search link format hasn't been captured")
    for k in f:
        if k not in SEARCH_KEYS:
            errors.append(f"Unknown spec key {k!r}. Use one of: {', '.join(sorted(SEARCH_KEYS))}")
    if f.get("days_in_current_role"):
        errors.append("Prospeo counts time in role in months: use months_in_current_role, for example {\"min\": 0, \"max\": 3}")
    for k, (pkey, reason) in NOT_APPLIED.items():
        if f.get(k):
            if pkey:
                reason = f"Needs Prospeo's {st[pkey]['min_plan']} plan; your plan is {plan}"
            not_applied.append({"filter": k, "value": f[k], "reason": reason})

    out, used = {}, []

    def lst(k):
        v = f.get(k) or []
        if isinstance(v, str):
            errors.append(f"{k} must be a list, not a single string")
            return []
        return v

    # Job titles: mirrors the user's captured dashboard links (include, exclude, match_mode, smart_intensity).
    inc, exc = lst("titles"), lst("exclude_titles")
    if inc or exc:
        if not inc:
            errors.append("exclude_titles needs at least one title to include")
        mode = str(f.get("title_match", "contains")).upper()
        if mode not in {"CONTAINS", "EXACT", "SIMILAR"}:
            errors.append("title_match must be contains, exact or similar")
        for t in inc + exc:
            if not 2 <= len(t.strip()) <= 100:
                errors.append(f"Title {t!r} must be 2 to 100 characters")
        if len(inc) > 100 or len(exc) > 100:
            errors.append("Prospeo allows at most 100 titles to include and 100 to exclude")
        out["person_job_title"] = {"include": [t.strip().lower() for t in inc], "exclude": [t.strip().lower() for t in exc],
                                   "match_mode": mode, "smart_intensity": str(f.get("similar_intensity", "loose")).upper()}
        used.append("person_job_title")
        contains.append(f"Titles ({mode.lower()}): " + ", ".join(t.strip().lower() for t in inc)
                        + (f"; excluding {', '.join(exc)}" if exc else ""))

    def inc_exc(key, inc_k, exc_k, label, allowed=None, both_ok=True, enum_label=None):
        i, e = lst(inc_k), lst(exc_k)
        if not (i or e):
            return
        if allowed is not None:
            i, e = check_enum(i, allowed, enum_label, errors), check_enum(e, allowed, enum_label, errors)
        if not both_ok and i and e:
            errors.append(f"Prospeo doesn't allow include and exclude together for {label.lower()}: use one")
        body = {}
        if i:
            body["include"] = i
        if e:
            body["exclude"] = e
        out[key] = body
        used.append(key)
        contains.append(f"{label}: " + (", ".join(i) if i else "any") + (f"; excluding {', '.join(e)}" if e else ""))

    inc_exc("person_location_search", "person_locations", "exclude_person_locations", "Person location")
    inc_exc("company_location_search", "company_locations", "exclude_company_locations", "Company HQ location")
    for loc in lst("person_locations") + lst("exclude_person_locations") + lst("company_locations") + lst("exclude_company_locations"):
        if not 1 <= len(loc) <= 200:
            errors.append(f"Location {loc!r} must be 1 to 200 characters")

    hc, hr = lst("headcount"), lst("headcount_ranges")
    if hc and hr:
        errors.append("Use headcount (a custom range) or headcount_ranges (Prospeo's presets), not both")
    if hc:
        if len(hc) > 1:
            errors.append("Prospeo takes one custom headcount range; for several bands use headcount_ranges")
        r = hc[0]
        if not isinstance(r, dict) or r.get("min") is None or r.get("max") is None:
            errors.append("headcount needs a min and a max, for example {\"min\": 100, \"max\": 5000}")
        elif not (1 <= r["min"] <= r["max"] <= 999999):
            errors.append("headcount must satisfy 1 <= min <= max <= 999,999")
        else:
            out["company_headcount_custom"] = {"min": r["min"], "max": r["max"]}
            used.append("company_headcount_custom")
            contains.append(f"Headcount: {r['min']} to {r['max']}")
    if hr:
        good = check_enum(hr, values["employee_ranges"], "Headcount range", errors)
        out["company_headcount_range"] = good
        used.append("company_headcount_range")
        contains.append("Headcount bands: " + ", ".join(good))

    inc_exc("company_industry", "industries", "exclude_industries", "Industries", values["industries"], enum_label="Industry")

    ki, ke = lst("keywords"), lst("exclude_keywords")
    if ki or ke:
        if not ki:
            errors.append("exclude_keywords needs at least one keyword to include (Prospeo rule)")
        if len(ki) > 20 or len(ke) > 20:
            errors.append("Prospeo allows at most 20 keywords to include and 20 to exclude")
        for k in ki + ke:
            if not 3 <= len(k.strip()) <= 100:
                errors.append(f"Keyword {k!r} must be 3 to 100 characters")
        body = {"include": [k.strip() for k in ki]}
        if ke:
            body["exclude"] = [k.strip() for k in ke]
        body["include_all"] = bool(f.get("keywords_match_all", False))
        body["search_everywhere"] = True
        out["company_keywords"] = body
        used.append("company_keywords")
        contains.append(f"Company keywords ({'all' if body['include_all'] else 'any'}): " + ", ".join(body["include"])
                        + (f"; excluding {', '.join(ke)}" if ke else ""))

    inc_exc("person_seniority", "seniority", "exclude_seniority", "Seniority", values["seniorities"], both_ok=False,
            enum_label="Seniority")
    dept_names = [d["name"] for d in values["departments"]]
    inc_exc("person_department", "departments", "exclude_departments", "Departments", dept_names, both_ok=False,
            enum_label="Department")

    dh = lst("department_headcount")
    if dh:
        rows = []
        if len(dh) > 10:
            errors.append("Prospeo allows at most 10 department headcount rows")
        for r in dh:
            dname = check_enum([r.get("department", "")], dept_names, "Department", errors)
            lo, hi = r.get("min"), r.get("max")
            if lo is None and hi is None:
                errors.append("Each department_headcount row needs a min or a max")
            elif hi is not None and lo is not None and lo > hi:
                errors.append(f"department_headcount min {lo} is above max {hi}")
            elif dname:
                rows.append({"department": dname[0], "min": lo, "max": hi})
        if rows:
            out["company_headcount_by_department"] = rows
            used.append("company_headcount_by_department")
            contains.append("Department headcount: " + "; ".join(
                f"{r['department']}: " + (f"{r['min']} to {r['max']}" if r['min'] is not None and r['max'] is not None
                                       else f"at least {r['min']}" if r['min'] is not None else f"at most {r['max']}") for r in rows))

    m = f.get("months_in_current_role")
    if m:
        lo, hi = m.get("min", 0), m.get("max")
        if hi is None or not (0 <= lo <= hi <= 600):
            errors.append("months_in_current_role needs 0 <= min <= max <= 600")
        else:
            out["person_time_in_current_role"] = {"min": lo, "max": hi}
            used.append("person_time_in_current_role")
            contains.append(f"Time in current role: {lo} to {hi} months")

    unseen = [LABELS.get(k, k) for k in used if st.get(k, {}).get("status") == "documented"]
    if unseen:
        warnings.append("Taken from Prospeo's documentation, not yet seen in a link from your account: " + ", ".join(unseen)
                        + ". Check a chip appears for each. If one is missing, open '...' > Search API in Prospeo to see "
                        "what it kept, then tell me")
    if any(k in used for k in ("person_location_search", "company_location_search")):
        warnings.append("Places must use Prospeo's own wording (from its location suggestions). If a location chip is "
                        "missing, re-add the place in the dashboard and paste me the link")
    for k in used:
        if st.get(k, {}).get("status") == "locked":
            errors.append(f"Filter {k} needs Prospeo's {st[k]['min_plan']} plan")
    if not out:
        errors.append("This search has no filters")
    elif not any((isinstance(v, dict) and v.get("include")) or k in POSITIVE_ALWAYS for k, v in out.items()):
        errors.append("Prospeo needs at least one positive filter, not only exclusions")
    url = "" if errors else BASE + encode(out)
    return {"name": name, "url": url, "filters": out, "contains": contains, "warnings": warnings,
            "errors": errors, "not_applied": not_applied}


def build(spec, keys, values):
    results = [build_one(n, f, keys, values) for n, f in expand(spec)]
    seen = {}
    for r in results:
        if not r["url"]:
            continue
        if r["url"] in seen:
            r["warnings"].append(f"Same link as '{seen[r['url']]}': the filters that make this search different couldn't be "
                                 "applied (see below), so running it adds nothing")
        else:
            seen[r["url"]] = r["name"]
    return results


def fmt(v):
    if isinstance(v, list):
        return "; ".join(fmt(x) for x in v)
    if isinstance(v, dict):
        return ", ".join(f"{k.replace('_', ' ')} {x}" for k, x in v.items())
    return str(v)


def to_markdown(spec, results):
    lines = [f"# Prospeo searches: {spec.get('name', 'untitled')}", ""]
    if spec.get("built_from"):
        lines += [f"Built from: {spec['built_from']}. Every link was written by `prospeo_links.py`, not by hand.", ""]
    lines += ["Open each link while logged in to Prospeo. Check that the filter chips match \"Contains\" and note the "
              "result count. Browsing results is free; credits are spent only when you reveal contact details.", ""]
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


def token_of(url):
    url = url.strip()
    if not url.startswith(BASE):
        raise ValueError("Not a Prospeo people-search link (expected it to start with " + BASE + ")")
    return url[len(BASE):]


def parse(url, keys=None):
    notes = []
    try:
        filters = decode(token_of(url))
    except Exception as e:  # noqa: BLE001
        return {"filters": None, "notes": [f"This link doesn't carry readable filters ({e}). If you set filters before "
                                           "copying it, Prospeo may have changed its link format: then this skill can't "
                                           "build Prospeo links until the new format is worked out"]}
    st = (keys or {}).get("keys", {})
    status = {k: st.get(k, {}).get("status", "unknown to this skill") for k in filters}
    unknown = [k for k, s in status.items() if s == "unknown to this skill"]
    if unknown:
        notes.append("Keys this skill doesn't write yet: " + ", ".join(unknown))
    return {"filters": filters, "key_status": status, "notes": notes}


def compare(a, b):
    fa, fb = decode(token_of(a)), decode(token_of(b))
    return {"same": fa == fb, "only_in_a": sorted(set(fa) - set(fb)), "only_in_b": sorted(set(fb) - set(fa)),
            "different_values": sorted(k for k in set(fa) & set(fb) if fa[k] != fb[k])}


def confirm_key(key, url, path=KEYS_FILE, today=None):
    filters = decode(token_of(url))
    d = load(path)
    if key not in d["keys"]:
        raise ValueError(f"{key!r} isn't a key this skill writes")
    if key not in filters:
        raise ValueError(f"The link doesn't contain {key}; apply only that filter in the dashboard and copy the link again")
    d["keys"][key].update({"status": "seen", "source": f"User's captured link{', ' + today if today else ''}",
                           "seen_value": filters[key]})
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(d, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return f"{key} marked as seen in the user's account"


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if not argv:
        print(__doc__)
        return 2
    keys, values = load(KEYS_FILE), load(VALUES_FILE)
    cmd = argv[0]
    if cmd == "build":
        spec = load(argv[1])
        results = build(spec, keys, values)
        text = to_markdown(spec, results)
        if "--out" in argv:
            out = argv[argv.index("--out") + 1]
            with open(out, "w", encoding="utf-8") as fh:
                fh.write(text)
            print(f"Wrote {out}")
        if "--markdown" in argv or "--out" not in argv:
            print(text)
        bad = [r["name"] for r in results if r["errors"]]
        if bad:
            print("NOT BUILT: " + "; ".join(bad))
            return 1
        print(f"{len(results)} link(s) built")
        return 0
    if cmd == "parse":
        print(json.dumps(parse(argv[1], keys), indent=2, ensure_ascii=False))
        return 0
    if cmd == "compare":
        r = compare(argv[1], argv[2])
        print(json.dumps(r, indent=2))
        return 0 if r["same"] else 1
    if cmd == "confirm-key":
        print(confirm_key(argv[1], argv[2]))
        return 0
    if cmd == "values":
        kind = argv[1]
        items = values[kind] if kind != "departments" else [
            (d["name"] if not d["parent"] else f"  {d['name']}  (under {d['parent']})") for d in values["departments"]]
        q = argv[2].lower() if len(argv) > 2 else None
        for i in items:
            if q is None or q in i.lower():
                print(i)
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
