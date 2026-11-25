# Scoring, validation and upkeep

Turns an ICP from a description into something that can rank a list of real companies, be tested, and be kept current.

Contents:
- Fit versus readiness
- The four evidence layers
- Finding what separates winners from losers
- Building the 0-100 fit model
- Readiness scoring
- Negative ICP
- When is it an ICP, and when is it an early customer profile?
- Goldilocks check
- Validating the model (including real-send tests of the offer and the message)
- From ICP to working market list
- Per-account research prompt
- Ownership and refresh cadence
- Sources, and how to treat their numbers

---

## Fit versus readiness

Keep two separate scores. One number hides the answer.

- **Fit:** should this company buy from the client and succeed with it? Built from durable traits.
- **Readiness:** is something happening now that makes this the moment? Built from triggers and recent behaviour.

Readiness decides **which message an account gets and how soon**, not whether it is contacted. Most of a list shows no trigger at any given time, so a high-fit account with no signal is contacted now with the no-signal offer from Step 4, not left to wait.

| Fit | Readiness | Action (the label `score_accounts.py` writes) |
|---|---|---|
| High (Tier 1) | High: visibly hurting now | **Prioritise now: pain-specific message** |
| High (Tier 1) | Low: no visible pain or trigger | **Contact now with the no-signal offer** |
| Tier 2 | Any | **Test after Tier 1** |
| Gate unknown (capped at Tier 2) | Any | **Confirm the gate before contact**. Never "Prioritise now" |
| Low (Tier 3) | High | Verify fit before spending sales time; light nurture at most |
| Low (Tier 3) | Low | Deprioritise |

This stops three common mistakes: chasing an excited but poor-fit lead, ignoring a perfect-fit company that has not yet made a sound, and treating an unconfirmed gate as confirmed.

"Readiness high" means "visibly hurting" only when the readiness rules are the dated pain heuristics from Step 4 or events that survived the look-back below. Built from a stock list of signals, it means only "something happened". Say which in the brief.

**High fit means Tier 1 by default** (`high_fit_tiers: ["T1"]` in the model). Add Tier 2 only when Tier 2 rests on the same evidence as Tier 1 (not an Early Customer Profile) and the client can work both this quarter; then Tier 2 gets the Tier 1 actions.

**When Tier 2 work starts (one rule, used everywhere):** once every Tier 1 account has been contacted at least once (with the pain-specific message or the no-signal offer), add as much of Tier 2 as the client can work this quarter. Pack 1 and the market-list steps both use this rule.

**Choosing Tier 2.** Tier 2 holds accounts where the evidence shows the same differentiated value matters (Step 4), but with fewer proof points. Choose its direction (a size band, a neighbouring sector, another region) from the evidence, and say which evidence. Do not default to "one size-step above the best customers": a company in a different size band may value something different.

---

## The four evidence layers

| Layer | Question it answers | Examples | How fast it goes stale |
|---|---|---|---|
| Firmographic | Could they buy? | Industry, size, location, revenue, business model | Slowly: verify when new evidence appears, review yearly |
| Technographic / operational | Does it fit, and is switching plausible? | Tools in use, integrations needed, incumbent supplier, how they run today | Quarterly |
| Situational triggers | Why now? | Funding, expansion, new leader, hiring for a relevant role, regulation, migration, a new branch | Weeks; recheck on a schedule |
| First-party behaviour | Are they engaging with the client? | Pricing-page visits, trial activity, replies, event attendance, bookings | Days; apply time decay |

Rules:
- **Firmographics set the boundary** (who could be a fit). The **reason to buy** from Step 4 of SKILL.md (the value only the client gives, and a pain visible from outside; method in `why-they-buy.md`) decides who belongs in Tier 1. Triggers and behaviour set **timing**.
- Firmographics are proxies, not proof. Company size matters only if it predicts something real: budget, complexity, volume.
- For consumer and local clients, translate the layers: location and demographics (boundary), behaviours and occasions (fit), life events or seasons (triggers), bookings and messages (behaviour).

---

## Finding what separates winners from losers

Do not start by writing down what sounds like a good customer. Start from outcomes.

0. **Phase 0: check the accounts are real.** Before any account goes into a comparison group, confirm it is a real, operating company (a working website, a company page or a register entry). Drop test records, duplicates and personal sign-ups, and say how many were dropped.
1. **Hold out 20% first.** Where accounts with known outcomes exist, set aside 20% of them at random, before looking at their attributes. Build everything below on the other 80%. The held-out group is scored once the model exists (see "Validating the model", check 1). State how many accounts the held-out group has; a group of a handful of accounts gives an indicative result only.
2. **Define "ideal".** Pick the outcome that matters: retention, expansion, time to value, margin or cost to serve, sales cycle, referenceability. Revenue alone is not enough. A big account that needs constant custom work can be worse than a small one that adopts quickly and renews.
3. **Build comparison groups.** Recent customers that did well, customers that churned or struggled, lost deals, and deals that stalled. Use a defined period (for example the last 12 months).
4. **Check the same attributes for every account** in every group.
5. **Compare how often each attribute appears** in the good group versus the weak groups.
6. **Sort the attributes:**
   - Big gap between groups: a **discriminator**. It earns points in the fit model.
   - About equal in both groups: it **describes the market**, not the ideal customer. Use it to define the universe, not to rank within it.
7. **Check stability.** Promote an attribute only if the gap holds in two time periods or two segments.
8. **Respect small numbers.** With few accounts, read patterns qualitatively and state n. Do not report percentages from 12 customers as if they were facts.
9. **Test on the held-out 20%.** Score the held-out accounts with the finished model. A rule fails if, on those accounts, its attribute is not more common in the good group than in the weak groups. Drop every rule that fails before the list ships, even if it improved the results on the build accounts, and drop a rule that improves scores but has no link to a documented pain or the value from Step 4. Report the result on the model's "Backtest result" line every time, or say why it could not be run (for example: no accounts with known outcomes).

**Survivorship warning.** A CRM records whoever found the client: inbound, referrals, an event scan. It is not a sample of the market. An ICP built only from it inherits that bias. Where possible, also test against companies that never contacted the client (a sample from the market list below).

---

## Building the 0-100 fit model

The blunt test of an ICP: can you score any company from data alone, without a meeting? If not, you have an opinion.

1. **Scorecard the best customers.** Take about 20 accounts and rate each 1 to 5 on revenue quality, speed of sale, time to value, depth of use, and ease of working together. **Multiply** the five ratings instead of averaging them, because multiplying separates accounts that averaging hides. The top 20% is the working definition of ideal. With fewer accounts, start with 10.
2. **Keep 5 to 8 discriminating attributes** from the separator test, grouped by layer.
3. **Weight them out of 100.** The most predictive attributes (often industry or the presence of a specific role) get the most points. Treat the weights as hypotheses to be corrected later.
4. **Mark gates.** A gate is something that must be true (for example the vertical). A company that fails a gate is placed in Tier 3, however well it scores elsewhere. A company whose gate field is unknown is capped at Tier 2, because an unconfirmed gate cannot earn the top tier. Gates may carry points, since the vertical is often both the gate and the strongest predictor. Watch the total: once gate points reach the Tier 1 floor, every company that passes the gates is Tier 1 and the model ranks nothing (the script warns). Once they reach the Tier 2 floor, every company that passes starts in Tier 2, so Tier 3 holds only gate failures and the remaining rules decide Tier 1 versus Tier 2. That is a valid design, but say so in the brief (the script notes it).
5. **Set bands.** A common starting point: Tier 1 at 80 and above, Tier 2 at 50 to 79, Tier 3 below 50. Adjust once real data arrives.
6. **Add disqualifiers** for anything that rules a company out (see negative ICP).
7. **Exclude current customers and open deals.** Add a disqualifier on the client's CRM status (for example `crm_status` in `customer` / `open deal`) so no current customer or live deal is prospected as if it were new. Get the list from the client's CRM export; if there is none, say in Pack 1 that the list must be checked against the client's customers before any outreach.
8. **Record the citation trail in the model file.** Give the model `built_from` (the brief's file name and date) and `evidence_tier`, and give every rule and disqualifier an `evidence` line (the separator test, transcript IDs, the Step 4 heuristic, or `[Assumption]`). The script warns when any is missing, because the file that ranks accounts, and is handed on to list-building, must point back to what justified it.

Design rules:
- **Scoreable from findable data.** Anything that needs a discovery call belongs in qualification, not in the fit score.
- **One model per segment.** A trait that predicts buying in one segment can mean nothing in another. Give distinct customer types separate weights.
- **Transparent.** Show which rules fired for every account, so anyone can see why it ranked where it did. Record the model's version and date.
- **Unknown is allowed.** A blank earns nothing and is reported. Never fill blanks with guesses.
- **What counts as unknown.** A blank, a marker such as "unknown", "n/a" or "tbc", a value that cannot be read as a number, and a range that straddles a rule's boundary ("11-50" against "20 or more") are all unknown. They earn nothing, never trigger a disqualifier, and are reported.
- **Controlled vocabulary.** Category rules match exactly, so build a clean column first (for example `vertical_group` = `dental_clinic`) rather than scoring raw descriptions. The script reports near misses such as "dental clinics" against `dental_clinic`; fix the column before trusting Tier 3.
- **Keep Tier 1 narrow.** If Tier 1 covers a large share of the list (more than about 30%), the model describes the market instead of discriminating within it. For an early-stage client, 50 Tier 1 accounts is more useful than 5,000.

Run it: copy `examples/scoring-model.json`, edit it, and run `scripts/score_accounts.py` on a CSV of companies (`examples/accounts.csv` shows the messy inputs it handles, including a current customer that is excluded). The script produces fit score, tier, readiness score, recommended action, the reasons, the data issues and a `needs_review` column for each row. It flags a wide Tier 1, unknown-heavy fields, unreadable values, gate near misses, gate points that reach the Tier 1 or Tier 2 floor, rules with no `evidence`, and rows whose gate or heaviest rule rests on low-confidence research. The header comment in the script lists the full model format.

---

## Readiness scoring

Readiness rules come from evidence, not from a stock menu of signals. There are two sources, strongest first:

1. **The look-back on won and lost accounts** (below), when accounts with close dates exist.
2. **The dated visible-pain heuristics from Step 4** (`why-they-buy.md`), when they do not. Say in the model which rules came from there.

Generic signals such as funding, a leadership change or general hiring are candidates to test in the look-back, never defaults. Keep one only where it survives the comparison, or where the evidence ties it to the pain.

### Look-back: what happened before the won deals

1. Take every won and lost account that has a close date.
2. Choose a fixed window before the close (for example the six months before it) and state it. Use the same window for every account.
3. For each pain in the transcripts, search the public sources tied to it (reviews, job boards, registers, filings, news, the company's own site, archived copies of it) for **dated** events inside that window.
4. Count how often each event type appears before won deals and before lost deals:

   | Event type | Source | Won accounts with it (n of N) | Lost accounts with it (n of N) | Keep? |
   |---|---|---|---|---|

5. Keep an event type only if it appears clearly more often before wins than before losses. Those become the readiness rules and the trigger fields in the research prompts below. State n; with few accounts, call the table indicative.

### Rules for every readiness signal

- **It carries a date.** Give the rule a `date_field` and `max_age_days`: points fall in a straight line from full on the day of the signal to zero at `max_age_days`. A signal with no usable date earns nothing and is reported.
- **A pain is counted, not just present.** Use a counted, dated field (for example `booking_complaint_reviews_90d` with `gte 2`), not `truthy` on a free-text note: `truthy` checks only that some text is there, so "Reviews praise easy booking" would score.
- **The pain heuristic carries the most weight** when the evidence ties it to the top pain.
- **Record where each signal is detected** (careers page, news, reviews, registry filings), so it can be re-checked.
- **The weights are untested** until the three-campaign test (see "Validating the model") has run. Say so in the model (`readiness_status`) and the brief. Keep a signal's points only if campaigns triggered by it beat the no-signal campaign.
- **Never let readiness raise a poor-fit company's tier.** The two scores stay separate.

---

## Negative ICP

Describe the accounts that look attractive but repeatedly fail: unsupported technical or regulatory requirements, an uneconomic service burden, a business model the offer was not built for, chronic late payment, a buyer type that never signs.

- Source them from lost-deal reasons and churn reviews, with evidence.
- Add them as **disqualifiers or gates**. Do not rely on positive points to outweigh them.

---

## When is it an ICP, and when is it an early customer profile?

An **early customer profile (ECP)** reflects first customers and tells you what works. An **ICP** reflects repeatable best-fit customers and can steer targeting at scale.

Use two tests, in order:

1. **Floor.** Fewer than **8 comparable great customers** is always an early customer profile, whatever the selling motion.
2. **Bar for the selling motion.** From 8 upwards, patterns become trustworthy only once the count reaches the rough figure for the client's motion below. Lighter selling gives less signal per customer, so it needs more customers. Between the floor and the bar, call it an ICP only if interviews or CRM outcomes back the pattern, and state the count against the bar.

| Selling motion | Rough customer count to trust patterns |
|---|---|
| Self-serve, no sales contact | About 160 |
| Short, single-stage sale | About 80 |
| Two-stage sale | About 40 |
| High-touch or field sales | About 27 |
| Named accounts | About 20 (use an ideal account profile: organisation traits, not personas) |

These are heuristics, not statistical laws. In a small market they may never be reached. In that case lean harder on interviews, and say so.

Below the floor, or between the floor and the bar without that backing, **label the output "Early customer profile"** and plan to revisit it quarterly. Do not call a hypothesis an ICP.

---

## Goldilocks check

Before finalising, check that the ICP suits the client's stage and the way they sell. Report each check as **Pass / Fail / Unknown**, with the actual figure next to the threshold (table format in `output-template.md`). A near miss is a Fail, not a Pass.

1. Is the contract value enough to support the cost of selling it?
2. Do deals close within a cycle the client can live with? A cycle much longer than the client can fund means the ICP is probably too big for their stage.
3. Does the client have, or can it quickly get, at least 5 reference customers in this ICP?
4. Is the cost to serve in proportion to the contract value? If serving a customer eats a large share of what they pay (a common warning level is around 30%), the ICP is probably too small.
5. Can you count at least 100 reachable targets? Fewer means the market is too small to build on.

Any dollar thresholds quoted in practitioner guides come from US software businesses. **Scale them to the client's market, currency and price points, and say you did.** For a client with little traction, aiming slightly smaller (shorter cycles, more deals, faster learning) is often wiser than aiming at the biggest logos.

---

## Validating the model

1. **Held-out test.** Score the 20% set aside before the separator test (see "Finding what separates winners from losers"). Do high-fit accounts do better on conversion, time to value, retention, expansion and cost to serve? Drop every rule that fails on them. If the model rates churned or difficult customers as ideal, find which attributes caused it, remove ones that merely sound plausible, and strengthen the disqualifiers.
2. **Tier comparison.** Compare Tier 1 and Tier 2 at each stage of the customer journey (speed and conversion from lead to meeting, meeting to win, win to live, time to first result). Tier 1 should come out ahead at every stage. If it loses one, change one weight, wait a quarter and measure again. Never adjust on one reading.
3. **Pilot.** Four to six weeks, with success thresholds agreed in advance. Measure meeting or opportunity rate, win rate, cycle length, deal size and reply rate. **Change one thing per comparison**, so the effect of the list and the effect of the message can be told apart:
   - List effect: the same plain message to accounts in ICP priority order against a control group handled as usual.
   - Message effect: tailored messaging against the plain message, on the same list.

   Tailor the copy only after a message has shown it works (see the offer test below).
4. **Small-client version.** Pull a test list of about 100 companies, check by hand how many truly fit, and record the fit rate before scaling.

Only checks 1 to 3 move an ICP to the **Validated** tier. Check 4 tests the quality of the list, not whether the ICP predicts outcomes. Scoring the accounts the model was built from is a consistency check, not a held-out test, and validates nothing.

### Real-send tests of the offer and the message

The checks above test the list. None of them tests the offer, so a brief can reach Validated with an offer nobody has sent. Run these in order:

1. **Offer test first.** Send each candidate offer from Step 4 in one plain template to a Tier 1 list picked on firmographics only, so the offer is the only thing that changes. Count replies per email sent against a benchmark agreed with the client **in advance**. If you borrow a practitioner's benchmark, name whose rule it is and say it is their operating figure, not an independent finding. Build tailored copy and workflows only for an offer that passes. The offer status in the brief changes from "untested" to "tested" with what was sent, to how many, the replies per send and the date.
2. **Then a weekly pain-segment test.** Each week, pick one pain-qualified segment (Step 4), check a small list of it by hand, and write the messages by hand. Keep or drop the segment the following week on its replies. Expect most tests to fail; that is the point of running them weekly.
3. **Three-campaign test of the readiness signals.** Run three campaigns side by side: the whole firmographic list with no signals; focused segments with one signal per campaign; and trigger-based campaigns on real-time events. Keep a readiness signal's points only if its campaign beats the no-signal campaign.

Weekly tests and the quarterly cycle do not clash: the weekly tests act on segments and messages, the quarterly cycle on the fit model's weights.

A resonance check (Step 10) or a read-through with 3 to 5 prospects is a **sense check before sending**, not a test.

---

## From ICP to working market list

An ICP that only filters existing leads ranks whoever happened to show up. A market list covers the companies that never contacted the client.

1. **Define the universe** using only industry, size and geography. Pick the source where the buyers are actually visible: professional-network search for office-based buyers; maps, chambers of commerce, registries and trade directories for local businesses. Add a second source only while each new one adds a meaningful number of new names.
2. **Make a raw first export in an hour.** No enrichment, no scoring. This is list v1.
3. **Enrich in bulk:** domains, phone and email, and a simple website-quality check (a real, maintained site behaves differently from none). Sample-check 20 to 30 records for accuracy before trusting any database in this market.
4. **Remove current customers and open deals**, using the client's CRM (the `crm_status` disqualifier). If there is no CRM export, say so and have the client check the list before any outreach.
5. **Score everything** with the fit model before anyone contacts anyone.
6. **Activate by capacity:** every Tier 1 account first (pain-specific message or the no-signal offer). Once every Tier 1 account has been contacted at least once, add as much of Tier 2 as the client can work this quarter.
7. **Validate by tier** (see above).
8. **Keep it alive quarterly:** re-enrich (contacts go stale), re-score on new signals, add newly qualifying companies, remove dead ones.

Sanity check on shape: a universe should narrow steadily to reachable companies, then to a small Tier 1. A Tier 1 that is a large share of the universe means the model needs sharper attributes.

---

## Per-account research prompt

Use in any tool that lets an LLM or research agent read a company's public pages (for example a row-by-row enrichment in a spreadsheet or table tool). Run it on both won and lost accounts to look for separators, then on the market list to score it.

It is **two prompts, one job each**: extraction gathers evidence, classification turns it into the model's values. One run that researches, writes a judgement and classifies at once does each job worse.

### Prompt 1: extraction

```
Research the company at {domain}. Use only evidence you can see on its own public pages
and the sources listed in this request. Do not infer anything from the company name alone.

Return JSON with these fields. Each field is an object with "value", "source_url",
"retrieved_on" and "confidence" (high / medium / low). Use "unknown" for "value" when you
cannot find evidence.

- what_they_sell
- who_they_sell_to
- business_model
- size_signals            (team page, branches, headcount hints)
- locations
- tools_or_systems_mentioned
[one line per readiness signal in the model, each with the date of the event, for example:
 hiring_front_desk: is there a current job post for front-desk or reception staff? Give its posting date.
 booking_complaint_reviews_90d: how many reviews in the last 90 days say calls or bookings go unanswered? Give the latest one's date.]

Do not state certifications, customer names or numbers unless the page states them explicitly.
```

### Prompt 2: classification

```
Below is the extracted evidence for {domain}. Classify it into the scoring model's fields.
For each field, return one of the listed values exactly as written, or "unknown". Use the
object shape {"value", "source_url", "retrieved_on", "confidence"}, carrying the source of
the evidence you used.

Fields:
[one line per model field, for example:
 vertical_group: dental_clinic | other_healthcare | other
 employees: a number or a range such as 11-50]
Readiness signals: for each, return the signal as yes / no, and its date in a separate field
whose name matches the model's date_field exactly, for example:
 hiring_front_desk: yes | no      hiring_front_desk_date: YYYY-MM-DD or unknown

Examples (hand-picked, with the answers you should give):
- Good fit: [2 or 3 Tier 1 accounts with their evidence and correct values]
- Bad fit: [2 or 3 accounts that fail a disqualifier or the negative ICP, with why]
- Thin data: [1 account with too little evidence, where most values are "unknown"]

Evidence:
{extraction output}
```

The `fit_note` sentence ("why this company does or does not fit") is not part of either prompt. If you want one, run it as a separate third step on the classified output, and never score on it.

Rules for using the output:
- Keep the source link, retrieval date and confidence next to every value.
- Allow "unknown"; do not turn uncertain web evidence into a confident fact.
- Send high-impact, low-confidence results to a person for review: `score_accounts.py` lists rows whose gate or heaviest rule rests on a "low" value in its `needs_review` column.
- Automate only after the fields are defined and each one has proved it affects a decision. Until then, start by hand.
- The research fields are for scoring and grouping accounts, **not for first lines** of messages. A first line built from a company description says nothing about the buyer's problem.
- Run `scripts/flatten_research.py` on the classified JSON to get a CSV for the scorer. Each field becomes a value column plus `<field>__source`, `<field>__retrieved_on` and `<field>__confidence`. The classified field and date-field names must match the model's `field` and `date_field` names exactly; "unknown" values are scored as unknown. A readiness rule whose date column is missing scores 0, so check the date columns are there before trusting readiness.

---

## Ownership and refresh cadence

Assign one owner who manages field definitions, scoring changes, source quality and review dates. For a small client this can be the account lead. The owner coordinates; the profile still needs input from sales, marketing, delivery and customer success.

| What | Review |
|---|---|
| Industry, business model, geography | When new evidence appears; yearly otherwise |
| Company size, leadership, funding | Quarterly, or when a trigger is detected |
| Tools and operational traits | Quarterly, and before specific outreach |
| Behavioural signals | Continuously, with time decay |
| Triggers | Weekly for priority accounts |
| One pain-qualified segment and its messages | Weekly test: kept or dropped the following week |
| Weights, gates, disqualifiers | Quarterly, against actual outcomes |
| Whole profile | Rebuild yearly from fresh data, and after any major change to product, pricing, target market or sales motion |

Keep a change log: what changed, why, and what happened to the results. It lives in the client folder as `changelog.md` (see "Client folder" in SKILL.md), next to each version of the scoring model.

---

## Sources, and how to treat their numbers

The methods in this file draw on four practitioner guides:
- context.dev: ICP template and scoring (https://www.context.dev/blog/ideal-customer-profile-template)
- gtmskills.com: ICP builder skill and operational reference (https://www.gtmskills.com/skill/icp-builder)
- Clay: guide to ICP (https://www.clay.com/guides/ideal-customer-profile)
- sparkco.ai: ICP framework and GTM playbook (https://sparkco.ai/blog/build-ideal-customer-profile-icp-framework)

Treat the **methods** as useful and the **numbers** with care. Customer-count thresholds, tier bands, conversion rates, win-rate targets and market sizes in those guides come mostly from US and European software businesses, and many are rules of thumb or unsourced illustrations. Use them as starting points, recalibrate against the client's own data and market, and never present them as local benchmarks.

**Verification status:** the four URLs above, and which figure came from which of them (the 8-customer floor, the 160 / 80 / 40 / 27 / 20 customer counts, the 30% cost-to-serve warning level, the 80 / 50 tier bands, the 30% wide-Tier-1 warning), have not been re-checked against the pages. Treat every one as an unverified rule of thumb. When you use one in a brief, call it a practitioner heuristic, not a measured benchmark, and do not attribute a figure to a named source unless you have just read it there.
