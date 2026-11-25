"""Tests for search-query's script. Run: python tests/run_tests.py"""
import copy
import importlib.util
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TESTS = []


def test(name):
    def wrap(fn):
        TESTS.append((name, fn))
        return fn
    return wrap


spec_ = importlib.util.spec_from_file_location("apollo_links", os.path.join(ROOT, "scripts", "apollo_links.py"))
al = importlib.util.module_from_spec(spec_)
spec_.loader.exec_module(al)
D = al.load_dict()
EXAMPLE = json.load(open(os.path.join(ROOT, "examples", "apollo-spec.json"), encoding="utf-8"))

# ---- Links captured by the user from their own Apollo account (search-links.md, section 4)
TITLES = ("personTitles[]=chief%20revenue%20officer&personTitles[]=vice%20president%20of%20sales&personTitles[]=vice%20president%20of%20revenue%20operations"
          "&personTitles[]=head%20of%20revenue%20operations&personTitles[]=vice%20president%20of%20sales%20operations&personTitles[]=head%20of%20sales%20operations"
          "&personTitles[]=revenue%20operations%20manager&personTitles[]=vice%20president%20of%20customer%20success")
REST = ("personLocations[]=united%20states&organizationLocations[]=united%20states&organizationNumEmployeesRanges[]=100%2C5000"
        "&organizationIndustryTagIds[]=5567cd4e7369643b70010000&organizationIndustryTagIds[]=5567cd4773696439b10b0000"
        "&organizationIndustryTagIds[]=5567cd877369644cf94b0000&organizationIndustryTagIds[]=5567e0d47369641233eb0600"
        "&qOrganizationKeywordTags[]=data%20infrastructure&qOrganizationKeywordTags[]=data%20platform&qOrganizationKeywordTags[]=data%20engineering%20infrastructure"
        "&qOrganizationKeywordTags[]=cloud&qOrganizationKeywordTags[]=cloud%20infrastructure&qOrganizationKeywordTags[]=cloud%20computing"
        "&qOrganizationKeywordTags[]=storage&qOrganizationKeywordTags[]=data%20storage&qOrganizationKeywordTags[]=storage%20systems"
        "&qOrganizationKeywordTags[]=cybersecurity&qOrganizationKeywordTags[]=cyber%20security&qOrganizationKeywordTags[]=information%20security"
        "&qOrganizationKeywordTags[]=AI%20infrastructure&qOrganizationKeywordTags[]=artificial%20intelligence%20infrastructure"
        "&qOrganizationKeywordTags[]=machine%20learning%20infrastructure&qOrganizationKeywordTags[]=developer%20tools"
        "&qOrganizationKeywordTags[]=developer%20tooling&qOrganizationKeywordTags[]=software%20development%20tools")
LINK1 = ("https://app.apollo.io/#/people?page=1&" + TITLES + "&" + REST +
         "&recommendationConfigId=score&sortByField=%5Bnone%5D&sortAscending=false")
LINK2 = ("https://app.apollo.io/#/people?" + TITLES + "&" + REST +
         "&sortByField=recommendations_score&sortAscending=false&page=1"
         "&personDaysInCurrentTitleRange[max]=90&personDaysInCurrentTitleRange[min]=0&recommendationConfigId=score")
TAIL = "includedOrganizationKeywordFields[]=tags&includedOrganizationKeywordFields[]=name&sortAscending=false&sortByField=recommendations_score&page=1"
BOTH = ("https://app.apollo.io/#/companies?organizationIndustryTagIds[]=5567cd4773696439dd350000"
        "&organizationIndustryTagIds[]=5567cd477369645401010000&" + TAIL + "&recommendationConfigId=score")
CONSTRUCTION = ("https://app.apollo.io/#/companies?organizationIndustryTagIds[]=5567cd4773696439dd350000&" + TAIL
                + "&recommendationConfigId=score")
REAL_ESTATE = ("https://app.apollo.io/#/companies?" + TAIL
               + "&organizationIndustryTagIds[]=5567cd477369645401010000&recommendationConfigId=score")

BASE = {
    "page_type": "people",
    "titles": ["chief revenue officer", "vice president of sales", "vice president of revenue operations",
               "head of revenue operations", "vice president of sales operations", "head of sales operations",
               "revenue operations manager", "vice president of customer success"],
    "person_locations": ["united states"], "company_locations": ["united states"],
    "headcount": [{"min": 100, "max": 5000}],
    "industries": ["Computer Software", "Information Technology & Services", "Computer & Network Security", "Computer Hardware"],
    "keywords": EXAMPLE["base"]["keywords"],
}


def one(filters):
    return al.build_one("t", copy.deepcopy(filters), D)


# ---------------------------------------------------------------- captured links

@test("captured link 2 (time in role, 409 results) is rebuilt character for character")
def _():
    r = one({**BASE, "days_in_current_role": {"min": 0, "max": 90}})
    assert r["errors"] == [], r["errors"]
    assert r["url"] == LINK2, r["url"]
    assert len(LINK2) == 1801


@test("captured link 1 is rebuilt with the same parameters (Apollo's order differs)")
def _():
    r = one({**BASE, "sort": "[none]"})
    c = al.compare(r["url"], LINK1)
    assert c["same"], c
    assert len(LINK1) == 1715  # the length the earlier chat reported for the user's link


@test("Construction-only company link is rebuilt character for character")
def _():
    assert one({"page_type": "companies", "industries": ["Construction"]})["url"] == CONSTRUCTION


@test("Real Estate-only company link is rebuilt with the same parameters")
def _():
    r = one({"page_type": "companies", "industries": ["real estate"]})
    assert al.compare(r["url"], REAL_ESTATE)["same"]


@test("two-industry company link is rebuilt character for character")
def _():
    assert one({"page_type": "companies", "industries": ["Construction", "Real Estate"]})["url"] == BOTH


@test("parse then build reproduces captured link 2 exactly")
def _():
    f = al.parse(LINK2, D)["filters"]
    f["industries"] = [x["industry"].rsplit(" (", 1)[0] for x in f.pop("industry_ids")]
    assert one(f)["url"] == LINK2


# ---------------------------------------------------------------- industries

@test("confirmed industry gives no warning; probable gives a chip check")
def _():
    r = one({"page_type": "companies", "industries": ["Construction"]})
    assert r["warnings"] == []
    r = one({"page_type": "companies", "industries": ["Computer Software"]})
    assert any("probable" in w for w in r["warnings"])


@test("aliases resolve (Software, Cybersecurity, the seed list's 'Consumer & Network Security' label)")
def _():
    for a in ["Software", "cybersecurity", "Consumer & Network Security", "IT Services"]:
        assert al.find_industry(D, a) is not None, a


@test("unknown industry stops the search and says how to capture its ID")
def _():
    r = one({"page_type": "companies", "industries": ["Dental Clinics"]})
    assert r["url"] == "" and "learn-industry" in r["errors"][0]


@test("disputed industry (Animation / Industrial Automation) is never used")
def _():
    r = one({"page_type": "companies", "industries": ["Animation"]})
    assert r["url"] == "" and "disputed" in r["errors"][0]


@test("industry list: IDs are 24 hex characters, statuses valid, shared IDs only as conflict")
def _():
    from collections import Counter
    for e in D["industries"]:
        assert al.ID_RE.match(e["id"]), e
        assert e["status"] in {"confirmed", "probable", "unverified", "conflict"}, e
        assert e.get("source"), e
    counts = Counter(e["id"] for e in D["industries"])
    for e in D["industries"]:
        if counts[e["id"]] > 1:
            assert e["status"] == "conflict", e


@test("learn-industry records a single-industry link as confirmed")
def _():
    tmp = tempfile.mkdtemp()
    try:
        p = os.path.join(tmp, "d.json")
        shutil.copy(al.DEFAULT_DICT, p)
        msg = al.learn_industry(CONSTRUCTION.replace("5567cd4773696439dd350000", "5567cd4773696439dd350001"), "Civil Engineering", p)
        assert "Added Civil Engineering" in msg
        e = al.find_industry(al.load_dict(p), "civil engineering")
        assert e["status"] == "confirmed" and e["id"] == "5567cd4773696439dd350001"
    finally:
        shutil.rmtree(tmp)


@test("learn-industry confirms a probable entry and refuses a two-industry link")
def _():
    tmp = tempfile.mkdtemp()
    try:
        p = os.path.join(tmp, "d.json")
        shutil.copy(al.DEFAULT_DICT, p)
        al.learn_industry("https://app.apollo.io/#/people?organizationIndustryTagIds[]=5567cd4e7369643b70010000", "Computer Software", p)
        assert al.find_industry(al.load_dict(p), "Computer Software")["status"] == "confirmed"
        try:
            al.learn_industry(BOTH, "Construction", p)
            raise AssertionError("accepted a two-industry link")
        except ValueError:
            pass
    finally:
        shutil.rmtree(tmp)


@test("learn-industry resolves a disputed pair: the confirmed name wins, the other stays disputed")
def _():
    tmp = tempfile.mkdtemp()
    try:
        p = os.path.join(tmp, "d.json")
        shutil.copy(al.DEFAULT_DICT, p)
        al.learn_industry("https://app.apollo.io/#/companies?organizationIndustryTagIds[]=5567e1337369641ad2970000", "Animation", p)
        d = al.load_dict(p)
        assert al.find_industry(d, "Animation")["status"] == "confirmed"
        assert al.find_industry(d, "Industrial Automation")["status"] == "conflict"
    finally:
        shutil.rmtree(tmp)


# ---------------------------------------------------------------- spec rules

@test("locked filters are reported as not applied and never appear in the link")
def _():
    r = one({**BASE, "technologies": ["Salesforce"], "funding": {"within_days": 365}})
    assert {n["filter"] for n in r["not_applied"]} == {"technologies", "funding"}
    assert "salesforce" not in r["url"].lower() and "funding" not in r["url"].lower()


@test("an unknown spec key is an error (catches typos)")
def _():
    r = one({**BASE, "titels": ["cro"]})
    assert r["url"] == "" and "Unknown spec key 'titels'" in r["errors"][0]


@test("person filters are refused on the companies page")
def _():
    r = one({"page_type": "companies", "industries": ["Construction"], "titles": ["ceo"]})
    assert r["url"] == "" and "person filter" in r["errors"][0]


@test("company filters only seen on the people page get a chip warning on the companies page")
def _():
    r = one({"page_type": "companies", "industries": ["Construction"], "headcount": [{"min": 10, "max": 50}]})
    assert r["url"] and any("headcount has only been seen" in w for w in r["warnings"])


@test("an unconfirmed location string gets a chip warning; united states doesn't")
def _():
    assert not any("Location" in w for w in one(BASE)["warnings"])
    r = one({**BASE, "person_locations": ["united kingdom"]})
    assert any("'united kingdom'" in w for w in r["warnings"])


@test("headcount needs both ends; min above max is an error")
def _():
    assert one({**BASE, "headcount": [{"min": 100}]})["url"] == ""
    assert one({**BASE, "headcount": [{"min": 500, "max": 100}]})["url"] == ""


@test("days in role: min above max is an error")
def _():
    assert one({**BASE, "days_in_current_role": {"min": 100, "max": 10}})["url"] == ""


@test("a search with no filters is refused")
def _():
    assert one({"page_type": "people"})["url"] == ""


@test("values are encoded as Apollo does: spaces, commas, brackets and parentheses")
def _():
    assert al.enc("chief revenue officer (cro)") == "chief%20revenue%20officer%20%28cro%29"
    assert al.enc("100,5000") == "100%2C5000" and al.enc("[none]") == "%5Bnone%5D"


@test("titles and locations are written lowercase; keyword case is kept")
def _():
    r = one({"page_type": "people", "titles": ["VP of Sales"], "person_locations": ["United States"], "keywords": ["AI infrastructure"]})
    assert "personTitles[]=vp%20of%20sales" in r["url"] and "personLocations[]=united%20states" in r["url"]
    assert "AI%20infrastructure" in r["url"]


@test("base plus searches: set adds, drop removes")
def _():
    spec = {"base": {**BASE}, "searches": [{"name": "a"}, {"name": "b", "drop": ["keywords"]},
                                            {"name": "c", "set": {"days_in_current_role": {"min": 0, "max": 30}}}]}
    a, b, c = al.build(spec, D)
    assert "qOrganizationKeywordTags" in a["url"] and "qOrganizationKeywordTags" not in b["url"]
    assert "personDaysInCurrentTitleRange[max]=30" in c["url"]


@test("the example spec builds: 6 searches, the locked signals reported, the UK flagged")
def _():
    rs = al.build(EXAMPLE, D)
    assert len(rs) == 6 and all(not r["errors"] for r in rs), [r["errors"] for r in rs]
    names = {r["name"]: r for r in rs}
    assert any(n["filter"] == "job_postings" for n in names["US, signal B: hiring for RevOps or Sales Ops"]["not_applied"])
    assert any("united kingdom" in w for w in names["UK base (about 30% of the list)"]["warnings"])
    assert al.compare(names["US, signal C: new in role in the last 90 days"]["url"], LINK2)["same"]
    md = al.to_markdown(EXAMPLE, rs)
    assert "Asked for but not applied" in md and "not by hand" in md


# ---------------------------------------------------------------- reading links

@test("parse names industries and flags unknown parameters")
def _():
    r = al.parse(BOTH + "&organizationTechnologyUids[]=salesforce", D)
    labels = [x["industry"] for x in r["filters"]["industry_ids"]]
    assert labels == ["Construction (confirmed)", "Real Estate (confirmed)"]
    assert r["unknown_params"] == [{"param": "organizationTechnologyUids[]", "value": "salesforce"}]


@test("parse warns when a link carries no readable filters (Filters 2.0)")
def _():
    r = al.parse("https://app.apollo.io/#/people?filterSetId=abc123&page=1", D)
    assert any("Filters 2.0" in n for n in r["notes"])


@test("parse copes with Markdown-escaped links pasted from chat")
def _():
    esc = LINK2.replace("[", "\\[").replace("]", "\\]").replace("&", "\\&")
    assert al.compare(esc, LINK2)["same"]


@test("compare reports what differs, ignoring order")
def _():
    c = al.compare(CONSTRUCTION, BOTH)
    assert not c["same"] and c["only_in_b"] == [("organizationIndustryTagIds[]", "5567cd477369645401010000")]


# ================================================================ Prospeo

_ps = importlib.util.spec_from_file_location("prospeo_links", os.path.join(ROOT, "scripts", "prospeo_links.py"))
pl = importlib.util.module_from_spec(_ps)
_ps.loader.exec_module(pl)
PK, PV = pl.load(pl.KEYS_FILE), pl.load(pl.VALUES_FILE)
P_EXAMPLE = json.load(open(os.path.join(ROOT, "examples", "prospeo-spec.json"), encoding="utf-8"))
# The user's two captured Prospeo links (search-links.md, section 4)
P1 = ("https://app.prospeo.io/search/people/eyJwZXJzb25fam9iX3RpdGxlIjp7ImluY2x1ZGUiOlsiY2hpZWYgcmV2ZW51ZSBvZmZpY2VyIiwiY2hpZWYg"
      "cmV2ZW51ZSBvZmZpY2VyIChjcm8pIl0sImV4Y2x1ZGUiOltdLCJtYXRjaF9tb2RlIjoiQ09OVEFJTlMiLCJzbWFydF9pbnRlbnNpdHkiOiJMT09TRSJ9fQ")
P2 = ("https://app.prospeo.io/search/people/eyJwZXJzb25fam9iX3RpdGxlIjp7ImluY2x1ZGUiOlsiY2hpZWYgcmV2ZW51ZSBvZmZpY2VyIiwiY2hpZWYg"
      "cmV2ZW51ZSBvZmZpY2VyIChjcm8pIiwiY2hpZWYgcmV2ZW51ZSBvZmZpY2VyIGNybyIsInZwIHNhbGVzIl0sImV4Y2x1ZGUiOltdLCJtYXRjaF9tb2RlIjoiQ09O"
      "VEFJTlMiLCJzbWFydF9pbnRlbnNpdHkiOiJMT09TRSJ9fQ")


def pone(filters):
    return pl.build_one("t", copy.deepcopy(filters), PK, PV)


P_BASE = {"titles": ["chief revenue officer"], "industries": ["Software Development"]}


@test("Prospeo: captured title link 1 is rebuilt character for character")
def _():
    assert pone({"titles": ["chief revenue officer", "chief revenue officer (cro)"]})["url"] == P1


@test("Prospeo: captured title link 2 is rebuilt character for character")
def _():
    assert pone({"titles": ["chief revenue officer", "chief revenue officer (cro)", "chief revenue officer cro", "vp sales"]})["url"] == P2


@test("Prospeo: decode then encode gives back both captured links")
def _():
    for u in (P1, P2):
        assert pl.BASE + pl.encode(pl.decode(pl.token_of(u))) == u


@test("Prospeo: captured links match the verified notes file")
def _():
    path = os.path.join(ROOT, "..", "_plans", "list-building-pipeline", "tool-docs", "search-links.md")
    if not os.path.exists(path):  # the installed copy has no _plans folder beside it
        return
    lines = [l.strip() for l in open(path, encoding="utf-8").read().splitlines()]
    assert P1 in lines and P2 in lines


@test("Prospeo: value lists are complete (256 industries, 10 seniorities, 11 bands, 14 top-level departments)")
def _():
    assert len(PV["industries"]) == len(set(PV["industries"])) == 256
    assert len(PV["seniorities"]) == 10 and len(PV["employee_ranges"]) == 11
    assert sum(1 for d in PV["departments"] if d["parent"] is None) == 14
    for n in ["Software Development", "IT Services and IT Consulting", "Computer and Network Security", "Computer Hardware"]:
        assert n in PV["industries"], n


@test("Prospeo: industry names are checked; wrong case is fixed, Apollo's names are refused with suggestions")
def _():
    r = pone({**P_BASE, "industries": ["software development"]})
    assert r["filters"]["company_industry"]["include"] == ["Software Development"]
    r = pone({**P_BASE, "industries": ["Computer Software"]})
    assert r["url"] == "" and "Closest" in r["errors"][0]


@test("Prospeo: locked filters are reported with the plan they need and kept out of the link")
def _():
    r = pone({**P_BASE, "technologies": ["Salesforce"], "job_postings": ["revops"], "funding": {"within_days": 365},
              "job_change": {"days": 90}})
    reasons = {n["filter"]: n["reason"] for n in r["not_applied"]}
    assert "Starter" in reasons["technologies"] and "Growth" in reasons["job_change"]
    assert set(r["filters"]) == {"person_job_title", "company_industry"}


@test("Prospeo: filters seen in your account get no warning; documented-only filters get a chip check")
def _():
    assert pone({"titles": ["cro"]})["warnings"] == []
    r = pone(P_BASE)
    assert any("not yet seen" in w and "industry" in w for w in r["warnings"])


@test("Prospeo: confirm-key marks a filter seen, and refuses a link that lacks it")
def _():
    tmp = tempfile.mkdtemp()
    try:
        path = os.path.join(tmp, "k.json")
        shutil.copy(pl.KEYS_FILE, path)
        link = pone({"industries": ["Construction"]})["url"]
        pl.confirm_key("company_industry", link, path)
        assert pl.load(path)["keys"]["company_industry"]["status"] == "seen"
        try:
            pl.confirm_key("company_keywords", link, path)
            raise AssertionError("accepted a link without the key")
        except ValueError:
            pass
    finally:
        shutil.rmtree(tmp)


@test("Prospeo: headcount rules (custom or bands, not both; min <= max; bands must be Prospeo's)")
def _():
    assert pone({**P_BASE, "headcount": [{"min": 100, "max": 50}]})["url"] == ""
    assert pone({**P_BASE, "headcount": [{"min": 1, "max": 5}], "headcount_ranges": ["1-10"]})["url"] == ""
    assert pone({**P_BASE, "headcount_ranges": ["11-50"]})["url"] == ""
    assert pone({**P_BASE, "headcount_ranges": ["11-20", "21-50"]})["filters"]["company_headcount_range"] == ["11-20", "21-50"]


@test("Prospeo: keyword rules (at most 20, 3+ characters, exclusions need an include)")
def _():
    assert pone({**P_BASE, "keywords": [f"kw{i:02}" for i in range(21)]})["url"] == ""
    assert pone({**P_BASE, "keywords": ["ai"]})["url"] == ""
    assert pone({**P_BASE, "exclude_keywords": ["consumer"]})["url"] == ""


@test("Prospeo: seniority and department can't include and exclude at once; values are checked")
def _():
    assert pone({**P_BASE, "seniority": ["Vice President"], "exclude_seniority": ["Intern"]})["url"] == ""
    assert pone({**P_BASE, "seniority": ["VP"]})["url"] == ""
    assert pone({**P_BASE, "departments": ["Revenue Operations"]})["url"]


@test("Prospeo: department headcount writes an open-ended max as null, as the docs show")
def _():
    r = pone({**P_BASE, "department_headcount": [{"department": "Sales", "min": 20}]})
    assert r["filters"]["company_headcount_by_department"] == [{"department": "Sales", "min": 20, "max": None}]


@test("Prospeo: time in role is in months; a days value is refused with the fix")
def _():
    r = pone({**P_BASE, "months_in_current_role": {"min": 0, "max": 3}})
    assert r["filters"]["person_time_in_current_role"] == {"min": 0, "max": 3}
    r = pone({**P_BASE, "days_in_current_role": {"min": 0, "max": 90}})
    assert r["url"] == "" and "months" in r["errors"][0]


@test("Prospeo: refuses no filters, only exclusions, company search, and typos")
def _():
    assert pone({})["url"] == ""
    assert pone({"exclude_industries": ["Construction"]})["url"] == ""
    assert pone({**P_BASE, "page_type": "companies"})["url"] == ""
    assert "Unknown spec key" in pone({**P_BASE, "industry": ["Construction"]})["errors"][0]


@test("Prospeo: parse reads a link, flags keys this skill doesn't write, and flags unreadable links")
def _():
    r = pl.parse(pl.BASE + pl.encode({"person_job_title": {"include": ["cro"]}, "company_type": "Private"}), PK)
    assert r["key_status"]["person_job_title"] == "seen" and "company_type" in r["notes"][0]
    assert pl.parse(pl.BASE + "not-a-real-token!", PK)["filters"] is None


@test("Prospeo: compare names the filters that differ")
def _():
    c = pl.compare(P1, P2)
    assert not c["same"] and c["different_values"] == ["person_job_title"]


@test("Prospeo: the example spec builds 6 links and flags the two that collapse into the US base")
def _():
    rs = pl.build(P_EXAMPLE, PK, PV)
    assert len(rs) == 6 and all(not r["errors"] for r in rs), [r["errors"] for r in rs]
    dup = [r["name"] for r in rs if any("Same link as" in w for w in r["warnings"])]
    assert dup == ["US, signal B: hiring for RevOps or Sales Ops", "US, signal D: recent funding"], dup
    assert "not by hand" in pl.to_markdown(P_EXAMPLE, rs)


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
