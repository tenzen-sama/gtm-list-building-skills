#!/usr/bin/env python3
"""TAM / SAM / SOM calculator.

Usage:
    python tam_calc.py inputs.json           # markdown summary
    python tam_calc.py inputs.json --json    # machine-readable JSON
    python tam_calc.py - < inputs.json       # read from stdin

Runnable inputs are in ../examples/: sizing-single.json (one market, matches the worked
example in references/frameworks.md), sizing-segments.json, sizing-services.json (delivery
cap) and sizing-ranges.json (low / base / high). Copy the closest one and edit it.
Files must be plain JSON: no comments.

Input keys (every section optional; supply what you have)
---------------------------------------------------------
currency       "USD", "NGN", "GBP"... a label only; never mix currencies in one file
acv            annual contract value per customer ("annual_value" for B2C)
acv_source     where the ACV comes from ("annual_value_source" for B2C)
bottom_up      {"companies": n, "count_basis": "counted" | "derived", "count_source": "...",
                "count_source_type": "register" | "directory" | "maps" | "aggregator" | "other",
                "count_coverage_pct": p}
               B2C: "customers" instead of "companies".
               counted = a real list, register or database search count
               derived = a share of a bigger total (for example 17,000 x 15%)
               count_source_type: a government or regulator register is the strongest;
               an aggregator (a B2B database search) is directional only
               count_coverage_pct: your estimate of how much of the real market the source
               holds, with its basis in count_source
top_down       {"market_size": n, "relevance_pct": p, "subsegment_pct": p or [p, p, ...],
                "source": "..."}
sam_filters    [{"name": "...", "pct": p, "source": "..."}, ...], applied one after another
contacts_per_company
               optional: the number of roles to reach at each company (from Pack 1). The
               script then reports reachable contacts = SAM companies x this number
som            exactly ONE sales basis:
                 "deals_per_year": n
                 "capacity": {"reps": n, "meetings_per_rep_per_month": n, "close_rate_pct": p}
                 "share_pct": p                      (share of SAM)
               plus, for services and local businesses, an optional delivery cap:
                 "delivery": {"max_clients": n}
                   or {"hours_available_per_year": n, "hours_per_client_per_year": n}
                 "existing_clients": n               (default 0; subtracted from the cap)
               SOM deals = the smaller of the sales basis and the delivery cap.

Percentages are 0-100, not fractions. A value between 0 and 1 is flagged, because
0.6 means 0.6%, not 60%.

Segments: give a "segments" list instead of bottom_up / sam_filters / som. Each segment
takes "name", "companies" (or "customers"), "acv", "count_basis", "sam_filters" and "som"
(or the shorthand "deals_per_year"). A top-level "top_down" is compared with the total
bottom-up TAM.

Ranges: any number may be written as {"low": a, "base": b, "high": c}. Write "low" as the
value that gives the SMALLER market (for hours per client, the larger number of hours).
The script then adds a low / base / high scenario and a one-at-a-time sensitivity table.

Sources: every input should carry its source and date ("source" inside a range, or the
keys above). The script prints an "Unsourced inputs" list of every ACV, company count,
SAM filter, top-down market figure and SOM basis that has none. Each of those is an
[Assumption] in the brief until it is sourced. The script only does the arithmetic and
flags inconsistencies; it cannot check that a source is real.
"""

import json
import sys

DISAGREE_RATIO = 3.0    # flag if the two TAM methods differ by more than this
AGGRESSIVE_SHARE = 10.0  # flag if year-1 SOM exceeds this % of SAM
SOM_KEYS = ("deals_per_year", "capacity", "share_pct")
RANGE_KEYS = {"low", "base", "high", "source", "note"}
SOURCE_TYPES = ("register", "directory", "maps", "aggregator", "other")


def die(msg):
    raise SystemExit(f"error: {msg}")


# --- ranges -----------------------------------------------------------------

def is_range(v):
    return isinstance(v, dict) and "base" in v and set(v) <= RANGE_KEYS


def walk_ranges(node, path=()):
    if is_range(node):
        yield path, node
    elif isinstance(node, dict):
        for k, v in node.items():
            yield from walk_ranges(v, path + (k,))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk_ranges(v, path + (i,))


def resolve(node, pick="base", override=None, path=()):
    if is_range(node):
        which = (override or {}).get(path, pick)
        return node.get(which, node["base"])
    if isinstance(node, dict):
        return {k: resolve(v, pick, override, path + (k,)) for k, v in node.items()}
    if isinstance(node, list):
        return [resolve(v, pick, override, path + (i,)) for i, v in enumerate(node)]
    return node


def path_label(data, path):
    parts, node = [], data
    for p in path:
        if isinstance(p, int):
            node = node[p]
            name = node.get("name") if isinstance(node, dict) else None
            parts[-1] += f"[{name or p + 1}]"
        else:
            parts.append(str(p))
            node = node[p]
    return ".".join(parts)


# --- arithmetic -------------------------------------------------------------

def num(v, label):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        die(f"{label} must be a number, got {v!r}")
    return v


def pct(v, label, flags):
    v = num(v, label)
    if v < 0 or v > 100:
        die(f"{label} is {v:g}; percentages are 0-100")
    if 0 < v <= 1:
        flags.append(f"{label} is {v:g}%. Percentages are 0-100, not fractions; "
                     f"if you meant {v * 100:g}%, write {v * 100:g}.")
    return v / 100


def calc_som(som, sam_count, sam_value, acv, label, unit, flags):
    if not som:
        return None
    given = [k for k in SOM_KEYS if k in som]
    if len(given) != 1:
        die(f"{label}: 'som' needs exactly one sales basis ({', '.join(SOM_KEYS)}); "
            f"got {', '.join(given) or 'none'}")
    basis = given[0]
    out = {"basis": basis}
    if basis == "capacity":
        c = som["capacity"]
        for k in ("reps", "meetings_per_rep_per_month", "close_rate_pct"):
            if k not in c:
                die(f"{label}: som.capacity needs '{k}'")
        sales = (num(c["reps"], f"{label}: reps")
                 * num(c["meetings_per_rep_per_month"], f"{label}: meetings_per_rep_per_month")
                 * 12 * pct(c["close_rate_pct"], f"{label}: close_rate_pct", flags))
    elif basis == "deals_per_year":
        sales = num(som["deals_per_year"], f"{label}: deals_per_year")
    else:
        share = pct(som["share_pct"], f"{label}: som.share_pct", flags)
        if sam_count is not None:
            sales = sam_count * share
        elif sam_value is not None:
            if "delivery" in som:
                die(f"{label}: a delivery cap needs a company count; a value-only SAM cannot be capped")
            return {"basis": basis, "value": sam_value * share, "deals_per_year": None,
                    "share_of_sam_pct": som["share_pct"], "binding": "sales"}
        else:
            die(f"{label}: som.share_pct needs a SAM (sam_filters on a bottom-up or top-down TAM)")
    out["sales_deals"] = sales

    cap = None
    d = som.get("delivery")
    if d:
        if "max_clients" in d:
            max_clients = num(d["max_clients"], f"{label}: delivery.max_clients")
        elif "hours_available_per_year" in d and "hours_per_client_per_year" in d:
            hpc = num(d["hours_per_client_per_year"], f"{label}: hours_per_client_per_year")
            if hpc <= 0:
                die(f"{label}: hours_per_client_per_year must be above 0")
            max_clients = num(d["hours_available_per_year"], f"{label}: hours_available_per_year") / hpc
        else:
            die(f"{label}: som.delivery needs 'max_clients', or 'hours_available_per_year' "
                "and 'hours_per_client_per_year'")
        existing = num(som.get("existing_clients", d.get("existing_clients", 0)),
                       f"{label}: existing_clients")
        cap = max(0.0, max_clients - existing)
        out["delivery_cap"] = cap
    deals = sales if cap is None else min(sales, cap)
    out["binding"] = "delivery capacity" if cap is not None and cap < sales else "sales"

    if acv is None:
        die(f"{label}: 'acv' (or 'annual_value') is required to value SOM")
    out["deals_per_year"] = deals
    out["value"] = deals * acv
    if sam_count is not None:
        if deals > sam_count:
            flags.append(f"{label}: SOM deals ({deals:,.0f}) exceed the SAM {unit} count "
                         f"({sam_count:,.0f}), which is impossible.")
        if sam_count > 0:
            share = deals / sam_count * 100
            out["share_of_sam_pct"] = share
            if deals <= sam_count and share > AGGRESSIVE_SHARE:
                flags.append(f"{label}: year-1 SOM is {share:.1f}% of SAM {unit}, which is "
                             "aggressive. Check the sales inputs.")
    elif sam_value:
        out["share_of_sam_pct"] = out["value"] / sam_value * 100
    return out


def size_unit(u, label, acv, unit, flags):
    count = u.get("companies", u.get("customers"))
    if count is None:
        die(f"{label}: needs 'companies' (B2B) or 'customers' (B2C)")
    count = num(count, f"{label}: count")
    if acv is None:
        die(f"{label}: needs 'acv' (or 'annual_value')")
    acv = num(acv, f"{label}: acv")
    basis = u.get("count_basis")
    if basis is None:
        flags.append(f"{label}: count_basis not stated. Say 'counted' (a real list or database "
                     "count) or 'derived' (a share of a bigger total); until then treat it as derived.")
        basis = "unstated"
    elif basis not in ("counted", "derived"):
        die(f"{label}: count_basis must be 'counted' or 'derived', not {basis!r}")
    stype = u.get("count_source_type")
    if stype is not None and stype not in SOURCE_TYPES:
        die(f"{label}: count_source_type must be one of {', '.join(SOURCE_TYPES)}, not {stype!r}")
    if stype is None:
        flags.append(f"{label}: count_source_type not stated (register, directory, maps, "
                     "aggregator or other). A register count and an aggregator count are not "
                     "equally reliable.")
    elif stype == "aggregator":
        flags.append(f"{label}: the company count comes from an aggregator only. Treat it as "
                     "directional, sample-check 20 to 30 records, and where you can, combine it "
                     "with a register or directory and remove duplicates.")
    coverage = u.get("count_coverage_pct")
    if coverage is not None:
        pct(coverage, f"{label}: count_coverage_pct", flags)

    n = count
    funnel = [{"step": f"ICP-fit {unit} (TAM)", "pct": None, "count": n}]
    for i, f in enumerate(u.get("sam_filters", [])):
        fname = f.get("name", f"filter {i + 1}")
        if "pct" not in f:
            die(f"{label}: SAM filter '{fname}' needs 'pct'")
        n *= pct(f["pct"], f"{label}: SAM filter '{fname}'", flags)
        funnel.append({"step": fname, "pct": f["pct"], "count": n})

    som = u.get("som")
    if "deals_per_year" in u:
        if som is not None:
            die(f"{label}: give 'som' or the shorthand 'deals_per_year', not both")
        som = {"deals_per_year": u["deals_per_year"]}
    cpc = u.get("contacts_per_company")
    contacts = None
    if cpc is not None:
        contacts = n * num(cpc, f"{label}: contacts_per_company")
    return {"name": label, "count": count, "count_basis": basis, "acv": acv,
            "count_source_type": stype, "count_coverage_pct": coverage,
            "tam": count * acv, "sam_count": n, "sam": n * acv, "funnel": funnel,
            "contacts_per_company": cpc, "contacts": contacts,
            "som": calc_som(som, n, n * acv, acv, label, unit, flags)}


def calc(d):
    flags = []
    acv_top = d.get("acv", d.get("annual_value"))
    out = {"currency": d.get("currency", ""), "flags": flags, "units": []}

    if "segments" in d:
        for k in ("bottom_up", "som", "sam_filters"):
            if k in d:
                die(f"'{k}' goes inside each segment when 'segments' is used")
        segs = d["segments"]
        unit = "customers" if any("customers" in s for s in segs) else "companies"
        for i, s in enumerate(segs):
            acv = s.get("acv", s.get("annual_value", acv_top))
            if "contacts_per_company" not in s and "contacts_per_company" in d:
                s = {**s, "contacts_per_company": d["contacts_per_company"]}
            out["units"].append(size_unit(s, s.get("name", f"Segment {i + 1}"), acv, unit, flags))
        out["mode"] = "segments"
    elif "bottom_up" in d:
        bu = d["bottom_up"]
        unit = "customers" if "customers" in bu else "companies"
        u = {k: bu[k] for k in ("companies", "customers", "count_basis", "count_source_type",
                                "count_coverage_pct") if k in bu}
        if "contacts_per_company" in d:
            u["contacts_per_company"] = d["contacts_per_company"]
        u["sam_filters"] = d.get("sam_filters", [])
        if "som" in d:
            u["som"] = d["som"]
        out["units"].append(size_unit(u, "Market", acv_top, unit, flags))
        out["mode"] = "single"
    else:
        unit = "companies"
        out["mode"] = "top_down_only"
    out["unit"] = unit

    units = out["units"]
    h = {"tam_bottom_up": None, "tam_top_down": None, "triangulation_ratio": None,
         "count": None, "sam_count": None, "sam": None, "som": None, "som_deals": None,
         "contacts": None}
    if units:
        h["tam_bottom_up"] = sum(x["tam"] for x in units)
        h["count"] = sum(x["count"] for x in units)
        h["sam_count"] = sum(x["sam_count"] for x in units)
        h["sam"] = sum(x["sam"] for x in units)
        if any(x["contacts"] is not None for x in units):
            h["contacts"] = sum(x["contacts"] or 0 for x in units)
        with_som = [x for x in units if x["som"]]
        if with_som:
            h["som"] = sum(x["som"]["value"] for x in with_som)
            h["som_deals"] = sum(x["som"]["deals_per_year"] or 0 for x in with_som)
            missing = [x["name"] for x in units if not x["som"]]
            if missing:
                flags.append(f"No SOM inputs for {', '.join(missing)}; the total SOM covers the "
                             "other segments only.")

    td = d.get("top_down")
    if td:
        if "market_size" not in td:
            die("top_down needs 'market_size'")
        v = num(td["market_size"], "top_down.market_size")
        v *= pct(td.get("relevance_pct", 100), "top_down.relevance_pct", flags)
        subs = td.get("subsegment_pct", [])
        subs = subs if isinstance(subs, list) else [subs]
        for i, p in enumerate(subs, 1):
            v *= pct(p, f"top_down.subsegment_pct[{i}]", flags)
        h["tam_top_down"] = v
        if not units:
            filters = d.get("sam_filters", [])
            sv, funnel = v, [{"step": "TAM (top-down value)", "pct": None, "value": v}]
            for i, f in enumerate(filters):
                fname = f.get("name", f"filter {i + 1}")
                sv *= pct(f["pct"], f"SAM filter '{fname}'", flags)
                funnel.append({"step": fname, "pct": f["pct"], "value": sv})
            if filters:
                h["sam"] = sv
                out["value_funnel"] = funnel
            s = calc_som(d.get("som"), None, h["sam"], acv_top, "Market", unit, flags)
            if s:
                out["value_som"] = s
                h["som"], h["som_deals"] = s["value"], s.get("deals_per_year")

    if h["tam_bottom_up"] and h["tam_top_down"]:
        a, b = h["tam_bottom_up"], h["tam_top_down"]
        ratio = max(a, b) / min(a, b)
        h["triangulation_ratio"] = ratio
        if ratio > DISAGREE_RATIO:
            flags.append(f"The two TAM methods differ by {ratio:.1f}x (more than "
                         f"{DISAGREE_RATIO:g}x). Re-check the company count, ACV and the "
                         "relevance / subsegment percentages before trusting either.")
        derived = [x["name"] for x in units if x["count_basis"] != "counted"]
        if derived:
            flags.append(f"The company count for {', '.join(derived)} is derived or unstated, so "
                         "bottom-up and top-down are not independent: agreement between them "
                         "proves little.")
    out["headline"] = h
    return out


def has_source(v, sibling=None):
    """A value is sourced if it is a range carrying "source", or a sibling key holds one."""
    if is_range(v) and v.get("source"):
        return True
    return bool(sibling)


def unsourced_inputs(d):
    """List every input with no source, from the raw file (before ranges are resolved)."""
    missing = []

    def check_unit(u, name, acv_val, acv_src):
        if acv_val is not None and not has_source(acv_val, acv_src):
            missing.append(f"{name}: ACV")
        cnt = u.get("companies", u.get("customers"))
        if cnt is not None and not has_source(cnt, u.get("count_source")):
            missing.append(f"{name}: company count")
        for i, f in enumerate(u.get("sam_filters", []) or []):
            if not has_source(f.get("pct"), f.get("source")):
                missing.append(f"{name}: SAM filter '{f.get('name', i + 1)}'")
        som = u.get("som")
        if isinstance(som, dict) and not som.get("source"):
            if any(k in som for k in SOM_KEYS):
                missing.append(f"{name}: SOM sales basis")
        if "deals_per_year" in u and not has_source(u["deals_per_year"], u.get("som_source")):
            missing.append(f"{name}: deals per year")

    top_acv = d.get("acv", d.get("annual_value"))
    top_src = d.get("acv_source", d.get("annual_value_source"))
    if "segments" in d:
        for i, sg in enumerate(d["segments"]):
            name = sg.get("name", f"Segment {i + 1}")
            if "acv" in sg or "annual_value" in sg:
                acv_val = sg.get("acv", sg.get("annual_value"))
                acv_src = sg.get("acv_source", sg.get("annual_value_source"))
            else:
                acv_val, acv_src = top_acv, top_src
            check_unit(sg, name, acv_val, acv_src)
    elif "bottom_up" in d:
        bu = d["bottom_up"]
        u = {**bu, "sam_filters": d.get("sam_filters", [])}
        if "som" in d:
            u["som"] = d["som"]
        check_unit(u, "Market", top_acv, top_src)
    td = d.get("top_down")
    if td and not (td.get("source") or has_source(td.get("market_size"))):
        missing.append("top-down market size")
    return missing


def run(data):
    base = calc(resolve(data))
    base["unsourced"] = unsourced_inputs(data)
    ranges = list(walk_ranges(data))
    if not ranges:
        return base, None, None
    scen = {"low": calc(resolve(data, "low"))["headline"], "base": base["headline"],
            "high": calc(resolve(data, "high"))["headline"]}
    metric = next((k for k in ("sam", "tam_bottom_up", "tam_top_down")
                   if base["headline"][k] is not None), None)
    sens = []
    for path, rng in ranges:
        lo = calc(resolve(data, "base", {path: "low"}))["headline"]
        hi = calc(resolve(data, "base", {path: "high"}))["headline"]
        sens.append({"input": path_label(data, path), "low": rng.get("low", rng["base"]),
                     "base": rng["base"], "high": rng.get("high", rng["base"]),
                     "metric": metric, "at_low": lo[metric] if metric else None,
                     "at_high": hi[metric] if metric else None,
                     "som_at_low": lo["som"], "som_at_high": hi["som"]})
    sens.sort(key=lambda s: (-round(abs((s["at_high"] or 0) - (s["at_low"] or 0)), 2),
                             -round(abs((s["som_at_high"] or 0) - (s["som_at_low"] or 0)), 2)))
    return base, scen, sens


# --- output -----------------------------------------------------------------

def money(n, cur):
    if n is None:
        return "n/a"
    pre = f"{cur} " if cur else ""
    return f"{pre}{n:,.0f}" if abs(n) >= 100 else f"{pre}{n:,.2f}"


def count(n):
    if n is None:
        return "n/a"
    return f"{n:,.0f}" if abs(n) >= 10 else f"{n:,.1f}"


def som_cell(s, cur):
    if not s:
        return "n/a"
    bits = []
    if s.get("deals_per_year") is not None:
        bits.append(f"{s['deals_per_year']:,.1f}".rstrip("0").rstrip(".") + " deals")
    if s.get("binding") == "delivery capacity":
        bits.append("delivery-capped")
    return money(s["value"], cur) + (f" ({', '.join(bits)})" if bits else "")


METRIC_NAMES = {"sam": "SAM", "tam_bottom_up": "TAM (bottom-up)", "tam_top_down": "TAM (top-down)"}


def to_markdown(r, scen=None, sens=None):
    cur, unit, h, units = r["currency"], r["unit"], r["headline"], r["units"]
    L = []
    if r["mode"] == "segments":
        L += ["| Segment | Count | Count basis | ACV | TAM | SAM count | SAM | SOM (yr 1) |",
              "|---|---|---|---|---|---|---|---|"]
        for u in units:
            L.append(f"| {u['name']} | {count(u['count'])} | {u['count_basis']} | "
                     f"{money(u['acv'], cur)} | {money(u['tam'], cur)} | {count(u['sam_count'])} | "
                     f"{money(u['sam'], cur)} | {som_cell(u['som'], cur)} |")
        deals = f" ({count(h['som_deals'])} deals)" if h["som_deals"] else ""
        L.append(f"| **Total** | {count(h['count'])} | | | {money(h['tam_bottom_up'], cur)} | "
                 f"{count(h['sam_count'])} | {money(h['sam'], cur)} | {money(h['som'], cur)}{deals} |")
        L.append("")

    L += ["| Measure | Value | Notes |", "|---|---|---|"]
    if h["tam_bottom_up"] is not None:
        if r["mode"] == "single":
            u = units[0]
            note = (f"{count(u['count'])} {unit} x {money(u['acv'], cur)} per year "
                    f"({u['count_basis']} count)")
        else:
            note = f"{count(h['count'])} {unit} across {len(units)} segments"
        L.append(f"| TAM, bottom-up | {money(h['tam_bottom_up'], cur)} | {note} |")
    if h["tam_top_down"] is not None:
        L.append(f"| TAM, top-down | {money(h['tam_top_down'], cur)} | market x relevance x subsegments |")
    if h["triangulation_ratio"] is not None:
        L.append(f"| Triangulation | {h['triangulation_ratio']:.2f}x apart | over "
                 f"{DISAGREE_RATIO:g}x needs a re-check |")
    if h["sam"] is not None:
        note = f"{count(h['sam_count'])} {unit}" if h["sam_count"] is not None else "value-based"
        L.append(f"| SAM | {money(h['sam'], cur)} | {note} |")
    if h["contacts"] is not None:
        L.append(f"| Reachable contacts | {count(h['contacts'])} | SAM {unit} x roles to reach per "
                 "company; a small pool means fewer, slower follow-ups (pace is set in the "
                 "outbound hand-off) |")
    if h["som"] is not None:
        bits = []
        if h["som_deals"]:
            bits.append(f"{count(h['som_deals'])} new customers/yr")
        som1 = units[0]["som"] if r["mode"] == "single" else r.get("value_som")
        if som1:
            if som1.get("share_of_sam_pct") is not None:
                bits.append(f"{som1['share_of_sam_pct']:.2f}% of SAM")
            bits.append(f"basis: {som1['basis'].replace('_', ' ')}")
            if som1.get("delivery_cap") is not None:
                bits.append(f"delivery cap {count(som1['delivery_cap'])}, binding: {som1['binding']}")
        elif h["sam_count"]:
            bits.append(f"{h['som_deals'] / h['sam_count'] * 100:.2f}% of SAM {unit}")
        L.append(f"| SOM (year 1) | {money(h['som'], cur)} | {', '.join(bits)} |")

    if r["mode"] == "single" and len(units[0]["funnel"]) > 1:
        L += ["", "SAM funnel:", "", "| Step | Filter % | Count |", "|---|---|---|"]
        for f in units[0]["funnel"]:
            L.append(f"| {f['step']} | {'' if f['pct'] is None else f['pct']} | {count(f['count'])} |")
    if r.get("value_funnel"):
        L += ["", "SAM funnel (value):", "", "| Step | Filter % | Value |", "|---|---|---|"]
        for f in r["value_funnel"]:
            L.append(f"| {f['step']} | {'' if f['pct'] is None else f['pct']} | {money(f['value'], cur)} |")

    if scen:
        L += ["", "Scenarios (every ranged input at its low, base or high value at once):", "",
              "| Measure | Low | Base | High |", "|---|---|---|---|"]
        for key, name in (("tam_bottom_up", "TAM, bottom-up"), ("tam_top_down", "TAM, top-down"),
                          ("sam", "SAM"), ("som", "SOM (year 1)")):
            if scen["base"][key] is not None:
                L.append(f"| {name} | {money(scen['low'][key], cur)} | {money(scen['base'][key], cur)} | "
                         f"{money(scen['high'][key], cur)} |")
    if sens and sens[0]["metric"]:
        m = METRIC_NAMES[sens[0]["metric"]]
        has_som = scen and scen["base"]["som"] is not None
        som_head = " SOM at low | SOM at high |" if has_som else ""
        L += ["", f"Sensitivity (one input at a time, the rest at base; sorted by how much it moves {m}):",
              "", f"| Input | Low | Base | High | {m} at low | {m} at high |{som_head}",
              "|---|---|---|---|---|---|" + ("---|---|" if has_som else "")]
        for s in sens:
            som_cells = (f" {money(s['som_at_low'], cur)} | {money(s['som_at_high'], cur)} |"
                         if has_som else "")
            L.append(f"| {s['input']} | {s['low']:,} | {s['base']:,} | {s['high']:,} | "
                     f"{money(s['at_low'], cur)} | {money(s['at_high'], cur)} |{som_cells}")

    if units:
        L += ["", "Company counts:"]
        for u in units:
            cov = (f", estimated coverage {u['count_coverage_pct']}%"
                   if u.get("count_coverage_pct") is not None else ", coverage not estimated")
            L.append(f"- {u['name']}: {u['count_basis']} count, source type "
                     f"{u.get('count_source_type') or 'not stated'}{cov}")
    if r.get("unsourced"):
        L += ["", "Unsourced inputs (each is an [Assumption] until sourced):"]
        L += [f"- {x}" for x in r["unsourced"]]
    if r["flags"]:
        L += ["", "Flags:"] + [f"- {x}" for x in r["flags"]]
    return "\n".join(L)


def load(path):
    if path == "-":
        raw = sys.stdin.buffer.read().decode("utf-8-sig")
    else:
        with open(path, encoding="utf-8-sig") as f:
            raw = f.read()
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        die(f"{path} is not valid JSON ({e}). Comments are not allowed in JSON; "
            "copy a file from examples/ instead.")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    args = [a for a in sys.argv[1:] if a != "--json"]
    if not args:
        raise SystemExit(__doc__)
    base, scen, sens = run(load(args[0]))
    if "--json" in sys.argv:
        print(json.dumps({"result": base, "scenarios": scen, "sensitivity": sens}, indent=2,
                         ensure_ascii=False))
    else:
        print(to_markdown(base, scen, sens))


if __name__ == "__main__":
    main()
