# The ICP handoff file

## What it is and why it exists

**Bottom line:** the handoff file is where this skill's job ends. It is one JSON file, written after the ICP sign-off, that holds everything the next skills in the list-building chain need, and nothing they don't.

The chain is modular. Each skill does one job and reads the file the step before it wrote:

1. **icp-tam-builder** (this skill): works out who to target and how big the market is. Writes `icp-handoff.json`.
2. **Lead sources** (planned): reads the handoff and says where to find those companies and people, with coverage, cost and a sample check.
3. **Search queries** (planned): reads the handoff and turns it into searches for Apollo, Prospeo and Clay.
4. **List builder** (planned): pulls, cleans, scores and checks the list.

A JSON file is used, not prose, so the next skill reads the exact filter values instead of re-interpreting a paragraph. A script, `scripts/check_handoff.py`, checks it and prints it as a readable list-building spec (Pack 1), so a person never has to read JSON.

**Running example:** `examples/icp-handoff.json`, the illustrative dental-clinic client used throughout this skill. It matches `examples/scoring-model.json` and `examples/sizing-single.json`.

## When to write it

- **Full build:** at Step 11, after the sign-off, whenever Pack 1 would be produced (blocking question B5; see `output-template.md`, "Delivery format"). Pack 1 is now printed from the handoff file, so the two never disagree.
- **Refresh:** write a new one whenever the ICP, the scoring model or the market size changes. Keep the old file; name the new one with the date or the scoring-model version.
- **Quick mode and Resonance check:** do not write one. A Quick view has no sign-off and no scoring model, so it is not fit to build a list from.
- **Not reviewed:** if the user skipped the sign-off, write the file with `"review": {"status": "draft"}`. Every later skill must carry the label "Draft: ICP not reviewed".

Save it in the client folder as `icp-handoff.json`, next to the scoring model it names. Where the client folder names files after the client (see "Client folder and context" in `SKILL.md`), it is `<client>-icp-handoff.json`, for example `exampleco-icp-handoff.json`; the next skills look for either name.

## How to check it

```
python scripts/check_handoff.py icp-handoff.json              # check only
python scripts/check_handoff.py icp-handoff.json --markdown   # check, then print Pack 1
```

- **Errors** mean a later skill would misread the file. Fix them before handing it on. The script exits with 1.
- **Warnings** are things the next skill must carry forward, such as a draft ICP, a Low-reliability signal, an `[Assumption]` behind a filter, a derived company count or unknown sales capacity. They do not stop the handoff.

Run it before delivery, and paste the `--markdown` output as Pack 1. The warnings are printed at the top of Pack 1 under "Carry forward", so they travel with it. Edit the JSON, never the printed text.

## The fields

Every value comes from the signed-off brief. Nothing new is invented here: if the brief does not have it, the field says so (`"unknown": true`, an empty list, or `[Assumption]`).

### Header

| Field | What it holds |
|---|---|
| `handoff_version` | `"1"`. The format version, so a later skill can tell if it is reading an older file |
| `client` | `name`, `website`, `client_type` (`b2b_software`, `b2b_services`, `local_consumer` or `hybrid`, from Step 0) |
| `built_from` | `brief` (the file it came from) and `date` |
| `review` | `status` (`reviewed` or `draft`), `reviewed_by`, `reviewed_on`. Copy from the changelog |
| `evidence` | `tier` (Hypothesis, Grounded or Validated), `label` (ICP or Early Customer Profile), `comparable_customers`, `floor` (8), `bar` (for the selling motion) |
| `scoring_model` | `file` and `version` of the scoring model. The list builder ranks accounts with it |

### Offer

| Field | What it holds |
|---|---|
| `offer.in_scope` | The one offer this ICP is for (blocking question B1) |
| `offer.why_this_offer` | The one-line reason (the "Why this offer" line in the brief) |
| `offer.status` | `untested` or `tested` |
| `offer.candidate_offers` | The candidate offers from Step 4: `id`, `name`, `value_type`, `frame`, `segment`, `proof`, `status` |
| `offer.no_signal_offer` | The `id` of the offer for Tier 1 accounts with no visible signal |

### Who to target

| Field | What it holds |
|---|---|
| `icp_sentence` | The ICP sentence, situation first |
| `pain_hypothesis` | `true` if the main segment is a pain hypothesis (Step 4) |
| `tiers` | One entry per tier, `T1` first. Each has a `description` and `filters`. Tier 2 also has `direction` (what it widens by) and `direction_evidence` |
| `tiers[].filters[]` | One filter per ICP criterion: `attribute`, `values`, `kind`, `why_it_matters`, `evidence`, `confidence` (High, Medium or Low). `kind` is one of firmographic, technographic, operational, situational, behavioural, demographic, geographic |
| `disqualifiers` | `rule`, `reason`, `evidence`. Must include current customers and open deals |
| `excluded_from_both_tiers` | Optional. Work the client does that needs its own ICP (for example a different outcome), so the list builder does not pull it in |
| `roles` | People to reach, **champion first**: `role` (`champion`, `economic_buyer`, `user`, `blocker`, or `all_roles` when one person does everything), `titles`, `evidence` |
| `channels` | Local and consumer clients only: `catchment`, `ad_audiences`, `local_partners`, `community_or_referral`. Replaces company filters, as in Pack 1's consumer version |

**Filter values.** A list for categories (`["Lagos", "Abuja"]`), or `{"min": .., "max": ..}` for a range. Use the client's own words or the brief's values; the search-query skill translates them into each tool's filter values. If the evidence is silent, set `"unknown": true` instead of guessing, and the list builder leaves that filter open.

**Why a reason on every Tier 1 filter.** A criterion with no reason describes the market, not the ideal customer (SKILL.md Step 5). The script errors on a Tier 1 filter without `why_it_matters`.

### When to reach them

| Field | What it holds |
|---|---|
| `signals[]` | One per trigger signal: `name`, `where` (the source to detect it), `dated` (true or false), `max_age_days`, `why_now`, `reliability` (High, Medium or Low, on the scale in `why-they-buy.md`), `reliability_reason`, `link_to_pain`, `scoring_field` (the readiness field in the scoring model) |
| `tier2_start_rule` | When Tier 2 work starts. Default: once every Tier 1 account has been contacted at least once, add as much of Tier 2 as the client can work this quarter |

If the scoring model file is found, the script warns when a signal's `scoring_field` is not one of its readiness rules, or when the version numbers differ.

### How big, and how fast

| Field | What it holds |
|---|---|
| `market` | From the sizing output: `companies`, `count_basis` (counted, derived, or none when nothing has been counted yet; none prints a warning), `count_source`, `count_source_type`, `sam_companies`, `reachable_contacts`, `currency`, `tam`, `sam`, `sizing_file`, and optionally `scope` (what the count covers, for example one country or one institution type) |
| `sales_capacity` | `reps`, `meetings_per_rep_per_month`, `close_rate_pct`, `source`; or `{"unknown": true, "note": "..."}`. The list builder sizes the shortlist to it |

### Loose ends

| Field | What it holds |
|---|---|
| `assumptions` | The load-bearing `[Assumption]`s, one line each |
| `open_questions` | Questions still open after the sign-off |

## What stays out

The handoff carries targeting, not research or copy:

- No named prospects, contact details or prospect research. Those belong to the list builder.
- No search links or tool-specific filter values. Those belong to the search-query skill, which works from each tool's current documentation.
- No example messages. Pack 2 stays a separate file for now.
- No quotes or evidence records. The `evidence` fields point back to the brief; they do not copy it.
