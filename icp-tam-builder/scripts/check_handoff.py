#!/usr/bin/env python3
"""Check an ICP handoff file, and print it as a readable list-building spec.

Usage:
    python check_handoff.py icp-handoff.json              # check; print errors and warnings
    python check_handoff.py icp-handoff.json --markdown   # check, then print Pack 1 (Markdown)

The handoff file is what icp-tam-builder hands to the next skills in the list-building
chain (lead sources, search queries, list building). Its format is in
../references/handoff-format.md; a runnable example is ../examples/icp-handoff.json.

Errors stop the handoff: a later skill would misread the file. Warnings are things the
next skill must carry forward (a draft ICP, a low-reliability signal, an unsourced filter).

Exit code: 0 when there are no errors (warnings allowed), 1 when there are errors,
2 on a usage error.
"""

import json
import os
import sys

VERSION = "1"
CLIENT_TYPES = {"b2b_software", "b2b_services", "local_consumer", "hybrid"}
TIERS = {"Hypothesis", "Grounded", "Validated"}
LABELS = {"ICP", "Early Customer Profile"}
REVIEW = {"reviewed", "draft"}
OFFER_STATUS = {"untested", "tested"}
KINDS = {"firmographic", "technographic", "operational", "situational", "behavioural",
         "demographic", "geographic"}
CONFIDENCE = {"High", "Medium", "Low"}
ROLES = {"champion", "economic_buyer", "user", "blocker", "all_roles"}
RELIABILITY = {"High", "Medium", "Low"}
COUNT_BASIS = {"counted", "derived", "none"}
REQUIRED = ["handoff_version", "client", "offer", "evidence", "review", "built_from",
            "icp_sentence", "tiers", "disqualifiers", "roles", "signals", "market"]


def die(msg):
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(2)


def load(path):
    try:
        with open(path, encoding="utf-8-sig") as f:
            return json.load(f)
    except OSError as e:
        die(f"cannot read {path}: {e.strerror}")
    except json.JSONDecodeError as e:
        die(f"{path} is not valid JSON (line {e.lineno}, column {e.colno}): {e.msg}")


def blank(v):
    return v is None or (isinstance(v, str) and not v.strip()) or v == [] or v == {}


def check(h, base_dir="."):
    """Return (errors, warnings) for a handoff dict."""
    errors, warns = [], []
    if not isinstance(h, dict):
        return ["the file must hold one JSON object"], []
    for k in REQUIRED:
        if k not in h:
            errors.append(f"missing '{k}'")
    if errors:
        return errors, warns
    if str(h["handoff_version"]) != VERSION:
        errors.append(f"handoff_version is {h['handoff_version']!r}; this script reads version {VERSION}")

    c = h["client"]
    if blank(c.get("name")):
        errors.append("client.name is empty")
    if c.get("client_type") not in CLIENT_TYPES:
        errors.append(f"client.client_type must be one of {sorted(CLIENT_TYPES)}")

    o = h["offer"]
    if blank(o.get("in_scope")):
        errors.append("offer.in_scope is empty: one offer per ICP")
    if o.get("status") not in OFFER_STATUS:
        errors.append(f"offer.status must be one of {sorted(OFFER_STATUS)}")
    offers = o.get("candidate_offers") or []
    ids = {x.get("id") for x in offers if isinstance(x, dict)}
    if not offers:
        warns.append("no candidate offers: the messaging step will have nothing to test")
    if o.get("no_signal_offer") and o["no_signal_offer"] not in ids:
        errors.append(f"offer.no_signal_offer {o['no_signal_offer']!r} is not a candidate offer id")
    if offers and not o.get("no_signal_offer"):
        warns.append("offer.no_signal_offer is not set: Tier 1 accounts with no signal need an offer")

    e = h["evidence"]
    if e.get("tier") not in TIERS:
        errors.append(f"evidence.tier must be one of {sorted(TIERS)}")
    if e.get("label") not in LABELS:
        errors.append(f"evidence.label must be one of {sorted(LABELS)}")
    if e.get("label") == "ICP" and isinstance(e.get("comparable_customers"), int) \
            and e["comparable_customers"] < 8:
        errors.append("evidence.label is ICP but comparable_customers is below the floor of 8: "
                      "it must be an Early Customer Profile")

    r = h["review"]
    if r.get("status") not in REVIEW:
        errors.append(f"review.status must be one of {sorted(REVIEW)}")
    elif r["status"] == "draft":
        warns.append("Draft: ICP not reviewed. Every later output must carry that label")
    elif blank(r.get("reviewed_on")):
        warns.append("review.status is reviewed but reviewed_on is empty")

    if blank(h["built_from"].get("brief") if isinstance(h["built_from"], dict) else None):
        errors.append("built_from.brief is empty: the handoff must trace back to its brief")

    sm = h.get("scoring_model") or {}
    if sm.get("file"):
        p = sm["file"] if os.path.isabs(sm["file"]) else os.path.join(base_dir, sm["file"])
        if not os.path.isfile(p):
            warns.append(f"scoring_model.file not found next to the handoff: {sm['file']}")
        else:
            try:
                with open(p, encoding="utf-8-sig") as f:
                    model = json.load(f)
                fields = {r.get("field") for r in model.get("rules", [])
                          if r.get("pillar") == "readiness"}
                for s in h.get("signals", []):
                    sf = s.get("scoring_field")
                    if sf and sf not in fields:
                        warns.append(f"signal '{s.get('name', '?')}': scoring_field '{sf}' is not a "
                                     "readiness rule in the scoring model")
                    elif not sf:
                        warns.append(f"signal '{s.get('name', '?')}' has no scoring_field: the "
                                     "scorer will not count it")
                if sm.get("version") and str(model.get("version")) != str(sm["version"]):
                    warns.append(f"scoring_model.version is {sm['version']} but the file says "
                                 f"{model.get('version')}")
            except (OSError, json.JSONDecodeError):
                warns.append(f"scoring_model.file could not be read as JSON: {sm['file']}")
    else:
        warns.append("no scoring_model.file: the list builder cannot rank accounts the same way")

    tiers = h["tiers"]
    names = [t.get("tier") for t in tiers if isinstance(t, dict)]
    if "T1" not in names:
        errors.append("tiers has no T1")
    for t in tiers:
        tn = t.get("tier", "?")
        if blank(t.get("description")):
            errors.append(f"{tn}: description is empty")
        filters = t.get("filters") or []
        if tn == "T1" and not filters:
            errors.append("T1 has no filters")
        if tn == "T2" and blank(t.get("direction_evidence")):
            warns.append("T2 has no direction_evidence: say which evidence chose the direction it widens in")
        for f in filters:
            a = f.get("attribute", "?")
            if f.get("kind") not in KINDS:
                errors.append(f"{tn} filter '{a}': kind must be one of {sorted(KINDS)}")
            if blank(f.get("values")) and not f.get("unknown"):
                errors.append(f"{tn} filter '{a}': no values (set \"unknown\": true if the evidence is silent)")
            if blank(f.get("evidence")):
                errors.append(f"{tn} filter '{a}': no evidence (cite a source or write [Assumption])")
            elif "[assumption]" in str(f["evidence"]).lower():
                warns.append(f"{tn} filter '{a}' rests on an [Assumption]")
            if f.get("confidence") not in CONFIDENCE:
                errors.append(f"{tn} filter '{a}': confidence must be High, Medium or Low")
            if tn == "T1" and blank(f.get("why_it_matters")) and not f.get("unknown"):
                errors.append(f"T1 filter '{a}': no why_it_matters (a criterion with no reason "
                              "describes the market, not the ideal customer)")

    dq = h["disqualifiers"]
    if not any("customer" in str(d.get("rule", "")).lower() for d in dq):
        errors.append("disqualifiers must exclude current customers and open deals")
    for d in dq:
        if blank(d.get("reason")) or blank(d.get("evidence")):
            errors.append(f"disqualifier '{d.get('rule', '?')}': needs a reason and evidence")

    roles = h["roles"]
    kinds = [x.get("role") for x in roles]
    for x in roles:
        if x.get("role") not in ROLES:
            errors.append(f"role {x.get('role')!r}: must be one of {sorted(ROLES)}")
        if blank(x.get("titles")):
            errors.append(f"role {x.get('role')!r}: no titles")
    if "champion" not in kinds and "all_roles" not in kinds:
        errors.append("roles must name the champion (or one person playing all_roles)")
    elif kinds and kinds[0] not in ("champion", "all_roles"):
        errors.append("roles: list the champion first, so lists reach the champion before the signer")

    for s in h["signals"]:
        n = s.get("name", "?")
        if s.get("reliability") not in RELIABILITY:
            errors.append(f"signal '{n}': reliability must be High, Medium or Low")
        if blank(s.get("why_now")):
            errors.append(f"signal '{n}': no why_now")
        if blank(s.get("where")):
            errors.append(f"signal '{n}': no 'where' (the source to detect it)")
        if not isinstance(s.get("dated"), bool):
            errors.append(f"signal '{n}': dated must be true or false")
        elif s["dated"] and not s.get("max_age_days"):
            warns.append(f"signal '{n}' is dated but has no max_age_days")
        if s.get("reliability") == "Low":
            warns.append(f"signal '{n}' has Low reliability: use it to sort, not to justify a message")
    if not h["signals"]:
        warns.append("no signals: every Tier 1 account will get the no-signal offer")

    m = h["market"]
    if m.get("count_basis") not in COUNT_BASIS:
        errors.append("market.count_basis must be counted, derived or none")
    if blank(m.get("count_source")):
        warns.append("market.count_source is empty: the company count has no source")
    if m.get("count_basis") == "derived":
        warns.append("the company count is derived, not counted: the list will need a real count")
    if m.get("count_basis") == "none":
        warns.append("no market count yet: the market is not sized, so the list builder must count it first")

    sc = h.get("sales_capacity") or {}
    if blank(sc) or sc.get("unknown"):
        warns.append("sales capacity unknown: the list builder cannot size the shortlist to it")
    return errors, warns


def values_text(f):
    if f.get("unknown"):
        return "unknown"
    v = f.get("values")
    if isinstance(v, list):
        return ", ".join(str(x) for x in v)
    if isinstance(v, dict):
        return ", ".join(f"{k} {x}" for k, x in v.items())
    return str(v)


def markdown(h, warns=None):
    """Pack 1: the handoff as a readable list-building spec. Warnings are printed in it,
    so they travel with the pack."""
    e, o, r = h["evidence"], h["offer"], h["review"]
    consumer = h.get("client", {}).get("client_type") == "local_consumer"
    sm = h.get("scoring_model") or {}
    out = []
    out.append(f"# Pack 1: List-building spec, {h['client']['name']}\n")
    if r.get("status") == "draft":
        out.append("**Draft: ICP not reviewed.**\n")
    out.append(f"Evidence tier: {e['tier']} | Label: {e['label']} | Scoring model: "
               f"{sm.get('file', 'none')} v{sm.get('version', '?')} | Built from: "
               f"{h['built_from'].get('brief')}, {h['built_from'].get('date', 'undated')} | "
               f"Offer status: {o['status']}\n")
    out.append("Generated from the handoff file by `scripts/check_handoff.py --markdown`. "
               "Edit the handoff file, not this text.\n")
    out.append(f"**Target:** {h['icp_sentence']}" + (" (pain hypothesis)" if h.get("pain_hypothesis") else "") + "\n")
    if warns:
        out.append("**Carry forward** (warnings from the check):\n")
        for w in warns:
            out.append(f"- {w}")
        out.append("")
    for t in h["tiers"]:
        out.append(f"## {t['tier']}: {t['description']}\n")
        if t.get("direction"):
            out.append(f"Widens by: {t['direction']} (evidence: {t.get('direction_evidence', 'not stated')})\n")
        if t.get("filters"):
            out.append("| Attribute | Values | Kind | Why it matters | Evidence | Confidence |")
            out.append("|---|---|---|---|---|---|")
            for f in t["filters"]:
                out.append(f"| {f.get('attribute')} | {values_text(f)} | {f.get('kind')} | "
                           f"{f.get('why_it_matters', '')} | {f.get('evidence')} | {f.get('confidence')} |")
            out.append("")
    if h.get("excluded_from_both_tiers"):
        out.append(f"**Kept out of both tiers:** {h['excluded_from_both_tiers']}\n")
    out.append("## Roles to reach, champion first\n")
    for x in h["roles"]:
        out.append(f"- **{x['role'].replace('_', ' ')}:** {', '.join(x['titles'])}"
                   + (f" ({x['evidence']})" if x.get("evidence") else ""))
    out.append("\n## Trigger signals\n")
    out.append("| Signal | Where to detect it | Dated? | Counts for | Why it suggests ready now | Reliability |")
    out.append("|---|---|---|---|---|---|")
    for s in h["signals"]:
        age = f"{s['max_age_days']} days" if s.get("max_age_days") else ""
        rel = s.get("reliability", "") + (f": {s['reliability_reason']}" if s.get("reliability_reason") else "")
        out.append(f"| {s['name']} | {s['where']} | {'yes' if s.get('dated') else 'no'} | {age} | "
                   f"{s['why_now']} | {rel} |")
    out.append("\n## Exclusions\n")
    for d in h["disqualifiers"]:
        out.append(f"- {d['rule']}: {d['reason']} ({d['evidence']})")
    tr = h.get("tier2_start_rule") or ("Once every Tier 1 account has been contacted at least once, "
                                       "add as much of Tier 2 as the client can work this quarter.")
    out.append(f"\n**When Tier 2 work starts:** {tr}\n")
    m = h["market"]
    out.append("## Market and capacity\n")
    noun = "People or customers" if consumer else "Companies"
    basis = "no count yet" if m.get("count_basis") == "none" else m.get("count_basis")
    out.append(f"- {noun} in the market: {m.get('companies', 'unknown')} ({basis}; "
               f"source type {m.get('count_source_type', 'not stated')}; {m.get('count_source', 'no source')})")
    if m.get("scope"):
        out.append(f"- Scope of the count: {m['scope']}")
    if m.get("sam_companies") is not None:
        out.append(f"- Reachable after filters (SAM): about {m['sam_companies']} "
                   + ("customers" if consumer else "companies"))
    if m.get("reachable_contacts") is not None:
        out.append(f"- Reachable contacts: about {m['reachable_contacts']}")
    sc = h.get("sales_capacity") or {}
    if blank(sc) or sc.get("unknown"):
        out.append("- Sales capacity: unknown" + (f" ({sc['note']})" if sc.get("note") else ""))
    else:
        out.append("- Sales capacity: " + ", ".join(f"{k.replace('_', ' ')} {v}" for k, v in sc.items()
                                                     if k not in ("source", "note"))
                   + (f" ({sc['source']})" if sc.get("source") else ""))
    if o.get("candidate_offers"):
        out.append("\n## Offers (status: " + o["status"] + ")\n")
        for x in o["candidate_offers"]:
            mark = " **(no-signal offer)**" if x.get("id") == o.get("no_signal_offer") else ""
            out.append(f"- {x.get('id')}. {x.get('name')}{mark}: {x.get('value_type', '')}; for "
                       f"{x.get('segment', '')}; proof: {x.get('proof', '')}")
    if h.get("assumptions"):
        out.append("\n## Load-bearing assumptions\n")
        for a in h["assumptions"]:
            out.append(f"- {a}")
    if h.get("open_questions"):
        out.append("\n## Open questions\n")
        for q in h["open_questions"]:
            out.append(f"- {q}")
    if h.get("channels"):
        out.append("\n## Channels (local and consumer clients)\n")
        for k, v in h["channels"].items():
            out.append(f"- {k.replace('_', ' ').capitalize()}: "
                       + (", ".join(v) if isinstance(v, list) else str(v)))
    out.append("\n## For the list builder\n")
    if consumer:
        out.append("- Always exclude current customers or members from every audience and list, from the "
                   "client's own records. If there are none, the client checks before any campaign.")
        out.append(f"- Scoring: apply the fit and readiness model ({sm.get('file', 'none')}) to whatever it "
                   "ranks (places, partners or audiences); its action column says which message each gets.")
        out.append("- Test before scaling: try one audience or channel small first, check how many of the "
                   "people who respond fit Tier 1, and record the fit rate.")
        out.append("- Data caution: check any population, audience or directory figure for this catchment "
                   "against a second source before trusting it.")
        return "\n".join(out) + "\n"
    out.append("- Always exclude current customers and open deals, from the client's CRM. If there is "
               "no CRM export, the client checks the list before any outreach.")
    out.append(f"- Scoring: apply the fit and readiness model ({sm.get('file', 'none')}); its action "
               "column says which message each account gets.")
    out.append("- Market list steps: raw export (list v1) -> enrich -> remove customers and open deals "
               "-> score all -> Tier 1 first, then Tier 2 by capacity -> validate by tier -> refresh quarterly.")
    out.append("- Per-account research prompts: see scoring-and-validation.md (extraction, then classification).")
    out.append("- Test before scaling: pull 100 companies, check how many truly fit the ICP, record the fit rate.")
    out.append("- Data caution: sample-check 20 to 30 records for accuracy and coverage before trusting "
               "any database in this market.")
    return "\n".join(out) + "\n"


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    md = "--markdown" in argv
    args = [a for a in argv if a != "--markdown"]
    if len(args) != 1:
        die("usage: check_handoff.py icp-handoff.json [--markdown]")
    h = load(args[0])
    errors, warns = check(h, os.path.dirname(os.path.abspath(args[0])))
    for x in errors:
        print(f"ERROR    {x}", file=sys.stderr)
    for x in warns:
        print(f"warning  {x}", file=sys.stderr)
    if errors:
        print(f"\n{len(errors)} error(s): fix them before handing this file on.", file=sys.stderr)
        return 1
    if md:
        print(markdown(h, warns))
    else:
        print(f"Handoff OK: {h['client']['name']}, {h['evidence']['tier']} / {h['evidence']['label']}, "
              f"review {h['review']['status']}; {len(warns)} warning(s) to carry forward.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
