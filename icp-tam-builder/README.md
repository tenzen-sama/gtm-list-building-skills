# icp-tam-builder

**Bottom line:** give it a client's website (and, ideally, their call recordings, customer list and prices). It tells you who the client should sell to, how big that market is, and how to find and talk to those buyers. Every claim it makes is either sourced or labelled as an assumption.

This README is for people. Claude reads `SKILL.md` and the files it points to, never this one, so editing the README changes nothing about how the skill behaves.

Running example throughout: **Sketch Labs**, a London office-search agency, built on 17 November 2026 from its website alone. Its client files are not included in this repository.

---

## What it produces

| Output | What it is | Sketch Labs example |
|---|---|---|
| ICP | The kind of *company* most worth targeting, written as criteria you can check yes or no | London office-based companies, 10 to 49 staff, growing, in flexible space |
| Persona(s) | The *people* inside those companies: who decides, who champions, who blocks | "The founder with a real job" |
| TAM / SAM / SOM | The market size in three layers (definitions below) | £107M / £45.5M / £286k a year |
| Scoring model | A 0-100 formula that ranks any list of companies | `sketchlabs-scoring-model.json` |
| Handoff file | One JSON file holding the targeting the next skills need (filters, roles, signals, exclusions, market size, scoring model). This skill's job ends here | `examples/icp-handoff.json` (illustrative; Sketch Labs was built before v4.3) |
| Use packs | A list-building spec (printed from the handoff file) and messaging inputs | Sections 7.1 and 7.2 of the brief |
| Client-facing summary | One page in plain words for the client, as its own file | Section 7.3 of the brief (built before v4 made it a separate file) |
| Resonance check | A verdict on whether a piece of copy will land with the buyer | The Sketch Labs homepage headline: Mixed |

**Delivery** is a chat summary, plus the brief document (marked internal), plus the client-facing summary as its own file, plus a spreadsheet with live formulas. Only the client-facing summary goes to the client.

**Where it keeps things.** Everything for one client goes in one place: the brief, the client summary, one record per call, each version of the scoring model, the sizing inputs and a change log. If you already keep client files somewhere (for example `project/clients/`, with files named `<client>-*`), it uses that. A later job, such as a Refresh, reads from there instead of asking you to paste the old brief.

---

## How to use it

Ask in plain words: "build an ICP for [url]", "who should this client sell to?", "size the market for X", "will this email land?". You don't need to say "ICP".

### Modes

| Mode | Use when | What you get |
|---|---|---|
| **Full build** (default) | A real client engagement | Everything above. The first reply is an inputs checklist, with an optional question asking who *you* think buys and why. Work starts once you send files or say "go with what I have". It pauses once more, at the ICP sign-off, before building anything on the ICP |
| **Quick** | A pre-sales look: "is this client worth taking?" | Website only. A rough ICP table and a market-size range, with no personas, scoring model or packs |
| **Resonance check** | You have an ICP and want an asset tested (an email, landing page, pitch) | A verdict and a rewrite only |
| **Refresh** | New data has arrived for an existing ICP | The ICP re-run on the new data, plus a "What changed" section |

### What to send

The Full build opens with this list. Here it is in short, most useful first:

1. **Must have:**
   - The website.
   - The one offer the ICP is for.
   - The price, or the typical deal size.
   - Where the client can serve customers.
2. **Biggest jump in quality:**
   - Sales call recordings: at least 5 to start; 20 to 30 recordings of won deals is ideal where they exist.
   - A customer list or CRM export, including which are current customers and open deals (so they are left off prospect lists).
   - The client's five best customers.
3. **Needed for a real SOM:**
   - Sales capacity (salespeople, meetings, close rate).
   - For a services firm, delivery hours too.
4. **Helpful:**
   - Reasons deals were lost, and competitors.
   - Case studies and testimonials.
   - The sales deck.
   - A list of target companies to score.

With no access to the client, it uses a public-only list instead: review sites, LinkedIn, job posts, press, and a database count of matching companies.

**Asking the client.** It can draft the request message for you, in one of two versions: one for businesses that sell to businesses, one for local and consumer businesses (a salon is never asked for "sales call recordings"). Both open with what the client gets and by when, give a "10 minutes" minimum (or a call instead), mark everything else optional, include the five questions their best customers would be asked, and have a line you must fill in on how you will handle their data.

---

## The workflow, step by step

| Step | What happens |
|---|---|
| 0. Inputs checklist | Reads both lessons files and looks for the client's folder. Works out who pays (a business buying software, a business buying a service, or consumers). Lists what to send, asks up to five blocking questions, each with a default, plus your optional view of who buys, then waits |
| 1. Read the website | Crawls case studies, testimonials, logos, pricing, team and blog. Keeps a log of pages read and pages unreachable |
| 2. Mine customer evidence | Tags every source (best-fit customer, other customer, lost, churned). Reads each call in its own pass and saves a record of it. Ranks pains from the best-fit customers only, with the others shown alongside. Finds who pushed for each purchase. Checks every quote with `check_quotes.py` |
| 3. Gaps and contradictions | Lists contradictions (for example, the website shows a team of brokers but the accounts show 1 employee) and drafts targeted questions, which wait for the sign-off |
| 4. Why they buy | The alternatives buyers compared the client with and what only the client gives them; the pain you can see from outside; two to four candidate offers, marked untested |
| 5. Define the ICP | The ICP table, with a reason for every Tier 1 criterion, Tier 1 and Tier 2, and disqualifiers |
| 6. ICP sign-off | Stops and asks you to confirm or correct the ICP before anything is built on it. If you asked for one go, it carries on and labels everything "Draft: ICP not reviewed" |
| 7. Scoring model | The 0-100 fit and readiness model and the Goldilocks check. Holds back 20% of known outcomes to test it. Builds readiness from what actually happened before won deals, not a stock list. Excludes current customers and open deals |
| 8. Personas | Always names the champion. One persona per buying role, every attribute sourced or marked as an assumption |
| 9. Market size | TAM, SAM and SOM, calculated by `tam_calc.py` rather than mental arithmetic. Lists every input with no source, and how many contacts can actually be reached |
| 10. Resonance check | Tests copy against the documented pains and buyer language, read as the champion. For cold messages, adds the name-swap test, length, the offer and the ask |
| 11. Deliver | Summary first, then detail, the packs that the use (blocking question 5) calls for, the client summary as its own file, and a validation plan split into your actions and at most two of the client's |

---

## Glossary: every term the skill uses

### The basics

- **ICP (Ideal Customer Profile).** The kind of company the client wins most often, keeps longest and serves most profitably. It is written as checkable criteria: "London, 10 to 49 staff", never "growing SMEs".
- **Persona.** A semi-fictional profile of one *person* inside an ICP company: title, goals, pains in their own words, objections, and what makes them start looking.
- **Firmographics.** Company facts used to group companies: industry, size, location, revenue.
- **Tier 1 / Tier 2.**
  - Tier 1 is the best fit, where the evidence is strongest.
  - Tier 2 is adjacent: accounts where the evidence shows the same value matters, but with fewer proof points. Which way it widens (size, sector or region) is chosen from the evidence, not fixed in advance.
  - Tier 2 work starts once every Tier 1 account has been contacted at least once.
- **Champion.** The person inside the buying company who pushes for the purchase and recommends it to whoever signs. The skill always names the champion separately from the person who signs, because that is who the outreach and copy are written for.
- **Best-fit group.** The client's best customers. Pains are ranked from this group only, so buyers who were never a good fit do not shape the messages.
- **Disqualifier.** Anything that rules a company out, however good it looks otherwise. Sketch example: under 5 staff, because a 3-desk placement earns about £2,000.
- **Negative ICP.** Companies that look attractive but repeatedly fail. They are turned into disqualifiers.

### Why they buy (Step 4)

- **Alternative.** What a buyer compared the client with: a competitor, an in-house hire, a spreadsheet, or doing nothing. Only alternatives a buyer actually named are counted.
- **Differentiated value.** What the client does that those alternatives don't, turned into what the buyer gains. Tier 1 is the set of companies that care most about it. On website-only work it is stated as a **thesis** to confirm.
- **Pain visible from outside.** Public data that would show a company has the pain before anyone speaks to it: reviews, job posts, a new branch, a licence renewal. Each one has a source and, ideally, a date.
- **Pain hypothesis.** A segment where no such public data could be found. It is a separate label from the evidence tier.
- **Candidate offer.** What a Tier 1 company that has never heard of the client is offered first, with the kind of value it gives (saves time, saves money or makes money) and the proof behind it. **Offer status** stays "untested" until offers are tried with real sends.

### How much to trust the result

- **Evidence tier.** Stated at the top of every output. There are three levels:
  - **Hypothesis:** website and public research only. Sketch Labs was here.
  - **Grounded:** adds first-party evidence: transcripts, a CRM export, a survey, or conversations with 5 or more customers.
  - **Validated:** the scoring model has been tested against real outcomes (see "Validation" below). Customer conversations alone never make an ICP Validated.
- **ICP versus Early Customer Profile (ECP).** It is called an ECP, not an ICP, in two cases:
  - **Below the floor:** fewer than **8 comparable great customers**. This rule always applies.
  - **Between the floor and the bar:** 8 or more, but not yet the bar for the client's selling style, without interviews or CRM data backing the pattern.

  The bar is about 27 customers for a high-touch sale, 40 for a two-stage sale, 80 for a short sale and 160 for self-serve. Sketch had 7, so it is an ECP. Revisit an ECP quarterly.
- **[Assumption].** A label on any number or claim without a source. "I couldn't find this" is an allowed answer; an invented figure is not.
- **Confidence (High / Medium / Low).** Given for each ICP criterion and market number, with a reason whenever it is below High.

### Market size

- **TAM (total addressable market).** The whole market if every fitting company bought.

  > TAM = number of fitting companies × annual contract value

- **SAM (serviceable addressable market).** The part of the TAM the client can actually reach and serve. It is the TAM with filters applied one after another: geography, channels, ability to pay.
- **SOM (serviceable obtainable market).** What the client can realistically win in 12 months. It is limited by sales capacity, or by delivery capacity for a services firm, whichever is smaller.
- **ACV (annual contract value).** What one customer pays a year. For Sketch, it is the fee per placement:

  > Fee = staff × desks per person × desk rate × months × 10%

- **Bottom-up versus top-down.**
  - Bottom-up counts companies and multiplies by ACV. It is the main method.
  - Top-down takes a published market figure and cuts it down. It is only a sanity check.
- **Triangulation.** Comparing the two methods.
  - Within 3x of each other is acceptable.
  - Further apart means something is wrong.
  - Agreement only counts as confirmation if the two methods are independent.
- **Count basis: counted or derived.**
  - **Counted** means a list you can open: a register, a database search, a directory.
  - **Derived** means a share of a bigger total, such as "17,000 companies × 15%". That is really a top-down number in disguise.

  Sketch's base count was counted (ONS), but turning it into "contracts per year" used an assumed rate, so the result is derived.
- **Ranges and sensitivity.**
  - Any uncertain input can be given as low / base / high.
  - The script then shows three scenarios.
  - It also produces a sensitivity table showing which single input moves the answer most. For Sketch, that was the share of companies moving office each year.
- **Delivery cap.** For services and local businesses: the most clients the team can actually serve. SOM is never higher than this.

### Scoring model

- **Fit score (0 to 100).** Should this company buy and succeed? Built from durable traits: size, sector, location.
- **Readiness score (0 to 100).** Is now the moment? Built from dated signals that the evidence links to the pain: for example two or more reviews in 90 days saying calls go unanswered. Where won and lost deals have close dates, the skill checks which public events actually happened before the wins (the **look-back**). Funding or hiring count only if they survive that check. The weights stay "untested" until real sends show a signal beats sending with no signal.
- **Signal decay.** Readiness points shrink in a straight line as a signal ages, reaching zero at a set age (for example 90 days for a hiring spike).
- **Gate.** A rule that must be true.
  - If the gate fails, the company goes to Tier 3.
  - If the gate is unknown, the company is capped at Tier 2.
  - Gates can carry points, but never enough to reach Tier 1 on their own.
- **Bands.** The score cut-offs for each tier. Sketch used Tier 1 at 70 or more, Tier 2 at 45 to 69, and Tier 3 below 45.
- **Action matrix.** Readiness decides which message an account gets, not whether it is contacted:
  - **Tier 1, visibly hurting now:** prioritise now, with a message about that pain.
  - **Tier 1, no signal:** contact now with the no-signal offer.
  - **Tier 2:** test after Tier 1.
  - **Gate unknown:** confirm the gate before contact. Never "prioritise now".
  - **Tier 3, high readiness:** check fit first.
  - **Tier 3, low readiness:** deprioritise.

  Worked example (`examples/accounts.csv`): Example Clinic 8 scores 100 for fit but shows no current signal. Before v4 it was told to "monitor for triggers", meaning wait. Now it gets "Contact now with the no-signal offer".
- **Unknown.** A blank, "n/a", or a range that straddles a rule's boundary (for example "1-50" against a 10-to-49 rule). It earns nothing and is reported, never guessed.
- **Near miss.** A value that almost matches a rule, such as "dental clinics" against `dental_clinic`. Fix the data before trusting the tiers.
- **Separator (discriminator).** An attribute far more common in good customers than in lost or churned ones. Only separators earn points. An attribute equally common in both just describes the market.
- **Holdout.** 20% of the accounts with known outcomes, set aside before the model is built and used to test it afterwards. Any rule that fails on them is dropped.
- **Review queue.** When per-company research says it has low confidence in a value that decides the tier, the scorer lists that company in a `needs_review` column for a person to check.

### Checks and tests

- **ICP sign-off.** The pause after the ICP is defined. It shows the ICP, why they buy, the tiers, the evidence with quotes, open questions and the three load-bearing assumptions, then waits for you. If you asked for the whole job in one go, everything built afterwards says **"Draft: ICP not reviewed"**, and the client-facing summary is marked not for the client.
- **Load-bearing assumption.** An assumption that would change the ICP if it turned out wrong.
- **Goldilocks check.** *Is this ICP the right size for this client right now?* It is not too big for the client to afford to sell to, and not too small to be worth it. Five tests, each reported as **Pass / Fail / Unknown** with the actual figure next to the threshold. A near miss counts as a Fail.

  | Test | Threshold | Sketch result |
  |---|---|---|
  | Does the contract value cover the cost of selling? | No fixed figure | Unknown |
  | Is the sales cycle short enough for the client to fund? | The client's runway | Unknown |
  | Are there at least 5 reference customers in this ICP? | 5 | **Fail** (1 confirmed) |
  | Is the cost to serve about 30% of contract value or less? | About 30% | Unknown |
  | Are there at least 100 reachable targets? | 100 | Pass (about 2,160 a year) |

  The thresholds come from US software rules of thumb, so they are scaled to the client's market and flagged as unverified.
- **Consistency check versus backtest.**
  - Scoring the customers the model was built from is only a **consistency check**. It proves nothing.
  - A **backtest** scores customers held back from building the model. It is one of the routes to Validated.
- **Validation.** The routes to the Validated tier:
  - A held-out backtest.
  - A Tier 1 versus Tier 2 comparison on live pipeline.
  - A 4 to 6 week pilot against a control group.

  A hand-checked 100-company test list checks list quality, not the ICP.
- **Resonance check.** Reads a piece of copy as the champion would. It quotes what lands and what misses, ties each to a documented pain, and suggests a rewrite. For a cold message it also runs:
  - the **name-swap test**: could the same message go to another company by changing only the name? If yes, it fails;
  - **useful without a reply**: does it give the reader something even if they never answer?;
  - the offer in the first lines, length against about 100 words, and an easy ask aimed at a reply ("Want a demo?" is a big ask).

  Confidence is low while the ICP is at Hypothesis tier. A read-through with 3 to 5 prospects is only a sense check.
- **Real-send tests.** The real test of an offer: send each candidate offer in one plain template to a Tier 1 list, and count replies per email against a benchmark agreed with the client in advance. After that, test one pain-qualified segment each week with hand-written messages.
- **Top-5 customer conversation kit.** Five 5-minute calls with the client's best customers, five fixed questions each. It is the fastest route from Hypothesis to Grounded.

### Use packs and the client summary

Which packs you get depends on your answer to blocking question 5 ("What will the ICP be used for?"); with no answer you get both. Each pack opens with the evidence tier, model version and offer status, so the caveats travel with it.

1. **List-building spec.** The filters, job titles (the champion's first), exclusions (always current customers and open deals) and trigger signals needed to build a target list. Since v4.3 it is printed from the handoff file, `icp-handoff.json`, by `scripts/check_handoff.py`, so the readable spec and the file the next skills read always agree. The next skills (lead sources, search queries, list building) are planned, not built; until then, hand it to the `clay-search-query` skill.
2. **Messaging inputs.** The candidate offers, one hand-written example message per Tier 1 segment with the conditions for sending it, a pain-to-angle table, the buyer's own words, objections grouped by who raises them, and a do-not-say list of claims the evidence can't back.

Named prospects are not part of this skill. Ask for them and it hands over the handoff file for the list builder (planned).

The **client-facing summary** is always produced, as its own file. It leads with what the client can realistically win this year in plain words (no TAM / SAM / SOM jargon), says what happens next and who does it, asks the client for at most two things, and allows "Nothing yet" under surprises. Every number that rests on an assumption keeps a one-line reason.

---

## Files

| File | What it does |
|---|---|
| `SKILL.md` | The instructions Claude follows |
| `references/lessons.md` | Lessons about the skill itself, from its tests, plus the line format. Claude reads it at the start of every job but never writes to it. Lessons from real client work go in a separate file, `lessons.md` in your clients folder (for example `project/clients/lessons.md`), which Claude reads at the start of every job and adds to after each one. Keeping it outside the skill means a skill update can never overwrite it |
| `references/intake-questions.md` | Inputs checklist, the two client request messages, blocking and probing questions, interview guides |
| `references/evidence-analysis.md` | How to crawl a website and analyse transcripts, surveys and CRM data |
| `references/client-types.md` | Method differences for software, services and consumer/local clients |
| `references/why-they-buy.md` | Step 4: alternatives and differentiated value, pain visible from outside, candidate offers |
| `references/frameworks.md` | ICP categories; TAM / SAM / SOM methods, mistakes and a worked example |
| `references/scoring-and-validation.md` | Fit and readiness scoring, ECP rule, Goldilocks check, validation, market list, upkeep |
| `references/output-template.md` | The brief layout, tables, persona template, packs and resonance format |
| `references/handoff-format.md` | The handoff file: what each field holds, when to write it, how to check it, and what stays out |
| `scripts/tam_calc.py` | Market-size calculator: segments, ranges, sensitivity, SOM caps, unsourced inputs, count source types, reachable contacts |
| `scripts/score_accounts.py` | Scores a company CSV against a scoring model; writes each company's action, priority, confidence and a review queue |
| `scripts/flatten_research.py` | Turns per-company research JSON into a CSV the scorer reads, keeping each value's source, date and confidence |
| `scripts/check_quotes.py` | Checks that every quote cited to a transcript appears in it word for word |
| `scripts/check_handoff.py` | Checks the handoff file (errors stop the handoff; warnings travel with it) and prints it as Pack 1 |
| `scripts/check_links.py` | Checks that every link in the brief, the packs or the evidence log opens; lists LinkedIn links for you to open by hand |
| `examples/` | Copy-and-edit inputs: 4 sizing files, a scoring model, a handoff file that matches them, a messy accounts CSV with a current customer planted in it, sample research output (all illustrative) |
| `tests/run_tests.py` | 61 tests; run after changing any script |
| `evals/` | Test prompts with expected behaviour, for checking changes to the skill: the original 4 in `evals.json`, plus one folder per newer test (a folder with the same name as an `evals.json` test replaces it) |

### Running the scripts yourself

Run these from the skill folder:

```bash
python scripts/tam_calc.py examples/sizing-ranges.json
```

```bash
python scripts/score_accounts.py examples/scoring-model.json examples/accounts.csv
```

```bash
python scripts/check_quotes.py brief.md transcripts/
```

```bash
python scripts/check_handoff.py examples/icp-handoff.json --markdown
```

```bash
python tests/run_tests.py
```

---

## Rules it will not break

- **No invented numbers, customers, quotes or dates.** Gaps are reported as gaps.
- **Every claim is sourced or marked [Assumption].** Web facts carry the retrieval date.
- **Sample sizes are stated** ("4 of 6 calls"); a pattern from 3 sources is never presented as a market truth.
- **When sources disagree, both are reported** and you are asked which to trust. It never quietly picks one.
- **Nothing is built on an unreviewed ICP without saying so.** It stops for the ICP sign-off, or labels the result a draft.

## Known limits

- **The benchmark figures are unverified rules of thumb.** That covers the 8-customer floor, the 27 / 40 / 80 / 160 bars, the 30% cost-to-serve line, the 80 / 50 tier bands and the 3x triangulation rule. They come from practitioner guides drawn mostly from US and European software businesses, and have not been re-checked against those guides.
- **Database counts outside the US and Europe are often overstated.** Sample-check 20 to 30 records before trusting one.
- **The evals have been run once (19 November 2026), on v3 and v2, one run per version.** v3 passed 62 of 67 assertions and v2 passed 42 of 67, across 7 tests. With one run each, a single pass or fail can be chance. Results: `icp-tam-builder-workspace/iteration-1/` (benchmark.md, review.html). v4 was tested lightly on 20 November 2026: the three tests most changed by v4, one run each. Full build 16 of 17 (one Tier 1 row had no "Why it matters" reason), resonance check 10 of 10, Quick mode 7 of 7. Results: `icp-tam-builder-workspace/iteration-2/benchmark-v4-light.md`. The other four tests have not been run on v4. The script tests (37) pass on v4, 44 pass on v4.2 and 59 on v4.3 and 61 on v4.5. **v4.2 (signal reliability, priority and confidence, the link checker) has not been run against the evals.** **v4.3's handoff file has not been run against the evals either.** It has been tried once by hand, on Example Co (20 November 2026): the file passed with 3 warnings, and the first printed Pack 1 dropped four items the file held (fixed, with a test).
- **The test companies and people are fictional.** The 19 November resonance run used a MaxIQ brief kept outside this repository; from v4 the resonance test carries its own fictional ICP (`files/icp-brief.md`, "Northwind Revenue") so it needs no outside files.
- **Watch:** in the 19 November Quick-mode run, v3 gave no URLs for its sources. The v4 re-run on 20 November gave a URL for every page, so it did not repeat, but that is one run. Both are recorded in `references/lessons.md`.
- **The next skills in the chain are not built.** Lead sources, search queries and list building are planned; the handoff format may need changes once they read it. The format carries a version number (`handoff_version`) for that reason.
- **New in v4 and untried on a real client:** the client folder, the lessons file, the look-back on won and lost deals, the 20% holdout and the real-send tests are instructions only. They have not been used on a live engagement yet.
- **The data-handling line in the client request is a placeholder you fill in.** Whether your wording is adequate depends on the data-protection law that applies; the template is not legal advice.
- **`check_links.py` checks that a page opens, not what it says.** It cannot confirm that a LinkedIn profile is the right person, or that a job post still shows the date claimed. LinkedIn links always come back as "check by hand".
- **Confidence is a rule of thumb.** The scorer's High / Medium / Low confidence comes from how much of the data behind a score is missing or rated low; the cut-offs are a design choice, not a measured standard.
- **`check_quotes.py` matches text, not meaning.** It catches a quote whose words are not in the source. It cannot tell whether a real quote is used out of context, and it skips quotes of fewer than four words and quotes with no source ID unless run with `--all`.

---

## Version

- **v4.5.2 (22 November 2026):** wording only. `references/handoff-format.md` now says the handoff file takes the client prefix when the client folder uses one (`exampleco-icp-handoff.json`), matching what the skill already did and what lead-sources v0.3 looks for.
- **v4.5.1 (22 November 2026):** test fixes only; the skill itself is unchanged. In the sign-off test, seven checks no longer depend on the run stopping (check 1 tests that on its own), so a run that does not stop loses one check instead of up to eight. The inputs-checklist test now gives the website as pasted homepage text instead of the dead address `example-agency.test`, which no run could open. Neither test has been rerun since the change.
- **v4.5 (20 November 2026):** fixes from the first full run of all 7 tests on v4.4 (75 of 79 checks passed; after the fixes the two failed tests were rerun and passed 13 of 13 and 10 of 10; results in `icp-tam-builder-workspace/iteration-3/`). The ICP draft is now named (`icp-draft.md`) and `brief.md` waits for the sign-off. In a Refresh, evidence that changes only a scoring weight no longer stops for the sign-off. `check_handoff.py` prints a local or consumer Pack 1 in terms of people and audiences, and accepts `count_basis: none` with a warning. The Refresh test's sample brief now matches its own answer key (its Tier 1 role read "dedicated practice manager" while the key expected "practice or operations manager"). 2 new tests (61 in all).
- **v4.4 (20 November 2026):** scope closed at the handoff file. Pack 3 (the named-prospect list) moved out, to become the starting spec for the list builder; asked for named prospects, the skill now hands over the handoff file instead. The extra-sources list (Step 4) and `check_links.py` stay: one feeds each signal's `where` field, the other checks the brief's own evidence links.
- **v4.3 (20 November 2026):** the skill's job now ends with a handoff file. New `references/handoff-format.md`, `scripts/check_handoff.py` and `examples/icp-handoff.json`. Step 11 writes `icp-handoff.json` to the client folder; Pack 1 is printed from it, so the two cannot disagree. The checker stops on errors a later skill would misread (no current-customer exclusion, a Tier 1 filter with no reason or evidence, an ICP label below 8 customers, the champion not first) and lists warnings that travel with the file (draft ICP, Low-reliability signals, assumptions, derived counts, signals the scoring model does not count). First step of a modular list-building chain: lead sources, search queries and list building will be separate skills that read this file. 15 new tests (59 in all). Pack 3 moved out in v4.4.
- **v4.2 (20 November 2026):** ideas from a lead-generation exercise. New Pack 3, a prospect list: each account kept only with a dated, sourced signal, a decision-maker with a verifiable source or "not verified", and a top-five ranking. Every visible-pain signal now gets "why it suggests ready now" and a High / Medium / Low reliability rating, plus a list of sources beyond LinkedIn and databases. The scorer writes separate priority and confidence columns. New `scripts/check_links.py` to run before delivery. A one-line "why this offer" when the client sells several, and research notes in the evidence appendix. `check_quotes.py --all` no longer flags the skill's own action labels. 7 new tests (44 in all).
- **v4.1 (20 November 2026):** lessons split in two. `references/lessons.md` keeps lessons about the skill and is changed only with the skill; lessons from real jobs go in `lessons.md` in the clients folder, outside the skill, so updates never overwrite them. The Sketch Labs lesson moved there.
- **v4 (20 November 2026):** fixes 4 to 21 from the 19 November 2026 review panel, applying the decisions recorded in that report.
  - **Actions (fix 4):** a Tier 1 account with no signal is contacted now with the no-signal offer; Tier 2 is "Test after Tier 1"; an unknown gate is never "Prioritise now"; high fit means Tier 1 by default; one rule for when Tier 2 starts; Tier 2's direction comes from the evidence.
  - **Readiness (fixes 5 and 7):** built from a look-back on won and lost deals or from Step 4's dated pain heuristics, not a stock list; the example complaints rule is now a counted, dated field; weights labelled untested.
  - **Research prompt (fix 6):** split into extraction and classification, with good-fit, bad-fit and thin-data examples, a date column per signal and a confidence rating that feeds a review queue.
  - **Client-facing work (fixes 8 and 9):** two client request messages with a 10-minute minimum; the client summary is always its own file, in plain words; the brief is marked internal; blocking question 5 picks the packs.
  - **Evidence (fixes 10, 12, 19):** sources tagged by group and pains ranked from the best-fit group; real-company check on CRM accounts; 20% holdout built in; 20 to 30 won-deal recordings asked for where they exist.
  - **Lists and copy (fixes 11, 13, 14):** current customers and open deals excluded; the champion always named; cold-message checks in the resonance check; one example message per Tier 1 segment in Pack 2.
  - **Validation (fix 15):** offer test first, then weekly pain-segment tests, the three-campaign test of signals, and a pilot that changes one thing at a time.
  - **Memory and traceability (fixes 16, 17, 18):** client folder, `references/lessons.md`, one pass per transcript and a handover file when the context window is half full; evidence lines in the scoring model; sources and unsourced-input list in the calculator; count source type and coverage.
  - **Smaller ones (fixes 20, 21):** an optional question asking for your own view of who buys, compared with the evidence in the brief; reachable contacts in the sizing.
  - Also: plain errors in `flatten_research.py`; blocking question 6 is now asked only when the checklist leaves it unclear, so no more than five are asked; 9 new script tests (37 in all); new eval checks for the no-signal action, the separate client summary, Pack 1's champion-first titles and the cold-message checks; a fictional ICP for the resonance test.
- **v3 (19 November 2026):** the top three fixes from a review panel on 19 November 2026.
  - Added Step 4, "Why they buy", and `references/why-they-buy.md`. It covers alternatives and differentiated value, the pain visible from outside, and candidate offers. The three parts follow principles the review panel's Dunford, Crawford and Nowoslawski auditors applied, as recorded in that panel's source files.
  - Added Step 6, the ICP sign-off, as the second deliberate pause, with a draft label when you ask for one go. The gap questions from Step 3 now wait for it.
  - Renumbered the later steps (scoring is now Step 7, personas 8, sizing 9, resonance 10, delivery 11).
  - Added `scripts/check_quotes.py` and 3 tests for it. The first eval run showed it missed source IDs written as "(call-1)" or placed before the quote ("call-4 lost: ..."); both are now read, with tests.
  - Added 5 new test cases under `evals/`: a stop at the ICP sign-off, a local/consumer client, a Refresh, and new versions of the full-build and resonance tests. Ran all 7 tests for the first time (see Known limits).
- **v2 (17 November 2026):**
  - Audit fixes:
    - Rebuilt the scripts with ranges, sensitivity, segments, SOM caps, unknown handling and signal decay.
    - Clarified the gate rules.
    - Added count basis, the ECP floor and bar, and the Goldilocks Pass / Fail / Unknown format.
  - Added the inputs checklist at the start of a Full build.
  - Added this README.
- **v1:** original version, backed up as `icp-tam-builder-v1-backup.skill`.
