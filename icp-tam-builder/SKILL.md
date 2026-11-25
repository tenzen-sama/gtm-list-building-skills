---
name: icp-tam-builder
description: Build an evidence-backed Ideal Customer Profile (ICP), buyer persona(s) and TAM/SAM/SOM market sizing for a client (or your own business) from their website, case studies, testimonials, call transcripts, customer interviews and CRM data. Interviews the user for gaps, sizes the market bottom-up and top-down with ranges, builds a 0-100 fit and readiness model that ranks a company list, checks copy against the ICP ("will this resonate?"), and writes list-building, messaging and client-summary packs. Works for software, services and local/consumer clients. Use when the user mentions ICP, ideal customer profile, "who should we sell to", buyer persona, firmographics, TAM, SAM, SOM or market sizing, asks to define or score target accounts for a client, or shares a client's website, transcripts or interviews to find their best customers, even without saying "ICP". Not for turning an existing ICP into a Clay or database search query (use clay-search-query), or for the user's own GTM career or job search.
---

# ICP & TAM Builder

Turn a client's website, documents and customer conversations into four things:

1. An evidence-backed Ideal Customer Profile (ICP)
2. Buyer persona(s)
3. TAM / SAM / SOM market sizing
4. A resonance check for anything written for that ICP

Built to be re-run for every new client, whatever they sell: B2B software, B2B services, or local and consumer businesses. The core workflow is the same; the client type changes the method (see Step 0).

## Ground rules

ICP work usually fails in one predictable way: a confident, generic profile built from a homepage. These rules exist to prevent that.

1. **Evidence has a hierarchy.** CRM data and call transcripts show who really buys and why. Case studies and testimonials show who the client chose to publicise. The homepage shows who the client *hopes* to sell to. Weight them in that order and say which tier each conclusion rests on.
2. **Label every claim.** Cite its source (URL, file name, transcript ID) or mark it `[Assumption]`. Give each ICP criterion and each market number a confidence rating (High / Medium / Low), with the reason whenever it is below High. Record the retrieval date next to anything taken from the web, and allow "unknown" as a value.
3. **Never invent.** No made-up customers, quotes, statistics, market sizes or dates. "I couldn't find this" is a valid result. A brief with honest gaps is more useful than a polished one with a fabricated number.
4. **State the evidence tier at the top of every output:**
   - **Hypothesis**: website and public research only. Vendor-selected case studies and testimonials count here.
   - **Grounded**: plus first-party customer evidence: call transcripts, a CRM export, survey data, or direct conversations with at least 5 customers
   - **Validated**: plus a test against real outcomes: a held-out backtest of the scoring model, a tier comparison on live pipeline, or a pilot against a control group (see "Validating the model" in `references/scoring-and-validation.md`). Customer conversations alone never make an ICP Validated.

   Separately, apply the customer-count test in `references/scoring-and-validation.md`: fewer than 8 comparable great customers is always an **Early Customer Profile**, not an ICP. From 8 upwards it is an ICP only once the count also meets the bar for the client's selling motion, or interviews or CRM outcomes back the pattern. State the count against the floor and the bar. Plan to revisit an Early Customer Profile quarterly.
5. **Ask on blockers, assume on the rest.** If something blocks a sound ICP (see `references/intake-questions.md`), ask before proceeding. For everything else, proceed with a stated default and mark it `[Assumption]` so the user can correct it. Never stall the whole job on a nice-to-have. A Full build has **two deliberate pauses**: the inputs checklist at the start (Step 0), and the ICP sign-off (Step 6). The second exists because every later output (scoring model, personas, market size, packs) inherits the ICP, and a wrong ICP is cheapest to fix before anything is built on it. Questions that come up between the two pauses, including conflicts between sources, wait for the sign-off with their defaults; do not stop for them one at a time.
6. **Be granular.** "SMEs in Africa" is not an ICP. If a company could not be checked against a criterion with a yes/no answer, sharpen the criterion.
7. **Small samples need honesty.** Always state n ("pain X appeared in 4 of 6 calls"). Do not present a pattern from 3 transcripts as a market truth.

## Modes

| Mode | Use when | What you do |
|---|---|---|
| **Full build** (default) | New client, real engagement | All steps below. Two pauses: the inputs checklist (Step 0), then the ICP sign-off (Step 6) |
| **Quick** | Pre-sales look, "is this client worth taking?" | Website only. Step 0: classify the client type; ask nothing unless the offer or client type is genuinely unclear. Step 1: read the site. Step 4, short version: the likely alternatives and the value only the client gives, stated as a thesis, and the pain a target would show from outside, labelled a pain hypothesis unless the site evidences it; no candidate offers. Step 5: the ICP table and disqualifiers only. No sign-off pause and no scoring model. Step 9: bottom-up TAM and SAM as a rough range, with the count basis stated; top-down only if a figure is to hand. Skip personas, use packs, the Goldilocks check and the inputs checklist; instead, end with one line naming the three inputs that would most improve this view. Say plainly at the top that the output is a Hypothesis-tier, directional view |
| **Resonance check** | User already has an ICP and wants an asset tested (email, landing copy, offer, pitch) | Jump to Step 10. No inputs checklist and no sign-off; if the ICP or the asset is missing, ask for it |
| **Refresh** | New data arrives for an existing ICP | Start with the inputs checklist for this round only: what has arrived and what is still missing. Read the previous brief, scoring model and `changelog.md` from the client folder first (ask for them only if there is no folder and they are not in the conversation). Re-run Steps 2 to 9 on the new data only. Stop for the ICP sign-off only if the new evidence changes a Tier 1 criterion or a disqualifier as written in the brief; otherwise say so in one line and carry on. Evidence that changes only a scoring weight (for example, a fit rule the new calls contradict) is applied in the new model version and listed under "What changed", without stopping. Update the evidence tier, bump the scoring model's version, and add a "What changed" section in the format in `references/output-template.md` |

## Client folder and context

**One place per client, so nothing is lost between conversations.** In a Full build or Refresh, everything the job produces is saved to a client folder, and every later job reads from it instead of asking the user to paste old work back in. Quick mode and a Resonance check stay in chat unless the user asks for a file.

- **Where.** If the user already keeps client work somewhere (for example a folder of files named `<client>-*`), use that layout and say where. Otherwise create `clients/<client-slug>/` in the working directory. Say the path in one line in the first reply.
- **What goes in it:** `brief.md` (the internal working brief), `client-summary.md`, `evidence/` (one record file per transcript or interview, plus the customer evidence table and the pages log), `scoring-model-v<N>.json` (a new file for each version, never overwritten), `sizing-inputs.json`, `icp-handoff.json` (what the next skills in the list-building chain read; Step 11), and `changelog.md` (one line per change: date, what changed, why, the evidence; plus who reviewed the ICP and when).
- **Save as you go.** Write the pages log, the evidence records and the ICP draft (`icp-draft.md`) to the folder at the end of the step that produces them, not only at delivery. Before the ICP sign-off, the draft is the only working document: do not write `brief.md` until the ICP is confirmed, or until the user has asked for the whole job in one go.
- **Context window.** A Full build with a website crawl, several transcripts and a CRM export fills a context window fast. Process each transcript in its own pass (Step 2). Once the window is about half full, write a short handover file to the client folder (`handover.md`: the step reached, the files written, the open questions and decisions so far) and carry on in a fresh window from it.
- **Lessons: two files.** `references/lessons.md` holds lessons about the skill itself, from its tests. It changes only when the skill is updated, so never write to it during a job. The **work lessons file** holds what users corrected on real jobs: `lessons.md` in the folder that holds the client folders (for example `project/clients/lessons.md`, or `clients/lessons.md` when you created `clients/`). It sits outside the skill, so a skill update never overwrites it. Read both in Step 0. Add a line to the work lessons file after each engagement and whenever the user corrects the ICP, in the format given in `references/lessons.md`; create the file if it does not exist, and say so in one line.

## Workflow

### Step 0: Inputs checklist, client type and blocking questions

**In a Full build or Refresh, the first reply is the inputs checklist, not analysis.** Most users do not know what to send beyond the website, so tell them before doing any work.

0. **Read both lessons files (`references/lessons.md` and the work lessons file; see "Client folder and context"), and look for the client folder** (search the working directory for the client's name). If earlier work exists, say what you found and build on it rather than starting again; a Full build on a client that already has a brief is usually a Refresh.
1. **Classify the client** by who pays: a business for software, a business for a service, or consumers. Use what the user said and the URL; do not crawl the site yet. If it is not obvious, make it one of the blocking questions. Read `references/client-types.md` and apply the matching variant for the rest of the workflow. Never apply the firmographic template to a consumer business.
2. **Build the inputs checklist** from `references/intake-questions.md` (Part 0) for that client type: every input, what it changes, and whether the user has already given it (Have / Missing / Not applicable). If the user has no access to the client (portfolio work, pre-sales), use the public-only list.
3. **Ask the blocking questions** that are still unanswered (Part B) in the same message: five or fewer, each with a suggested default. If the interface supports tappable choices, use them. Do not ask for anything the user already gave you. Add the optional question "In one or two lines, who do you think buys from this client, and why?", marked optional; if answered, the brief compares it with the evidence.
4. **Offer the client request message** (Part A) if the missing items have to come from the client: version A1 for a business that sells to businesses, A2 for a local or consumer business.
5. **Stop and wait.** Start Step 1 when the user sends what they can or says to go ahead with what they have. If their first message already said to start now, put the checklist at the top as "what would improve this later" and carry on in the same turn. Show the checklist once per job. "Go with what I have" answers this checklist only; it does not skip the ICP sign-off in Step 6.

### Step 1: Read the client's website properly

Do not skim; everything downstream depends on this. The full crawl checklist and extraction list are in `references/evidence-analysis.md` (section "Website crawl").

In short:
- Start at the URL the user gave, then follow the navigation. Also try `/sitemap.xml` for a page list.
- Prioritise: customers / case studies, testimonials, logo walls, industries / solutions / use-cases, services / products, pricing, about / careers, blog and resources, partners and integrations.
- Look beyond the site for third-party proof: review sites, press, LinkedIn page, webinars.
- Keep a list of pages read and pages you could not reach. If a page is blocked or rendered in a way you cannot read, say so and ask the user to paste it. Add short research notes as you go: what was hard to find, what you tried when a search failed, and how you checked facts. They go in the brief's appendix.
- If the client sells more than one offer, note which one has the most customer proof. The brief header says in one line why the chosen offer was picked over the others, and the others become separate ICPs.
- Treat the site as the client's **claim** about their market, not proof that those are the right customers.

### Step 2: Mine the customer evidence

Analyse every source the user supplied (transcripts, surveys, interviews, CRM export, decks) following `references/evidence-analysis.md`.

**First, tag every source by group**: best-fit customer, other customer, lost, or churned or struggling. Not every customer is good evidence, and pains voiced by bad-fit buyers would otherwise shape the ranking, the personas and the messages. If nobody has said which customers are best, use won-and-still-active, mark it `[Assumption]` and ask at the sign-off. For a CRM export, first check each account is a real company (Phase 0) and note current customers and open deals.

**Then process each transcript or interview in its own pass** (in a subagent if one is available), writing its record to the client folder (`evidence/T1.md`...). Build the counts and the quote bank from those files. Produce:

- **Customer evidence table**: one row per named customer or call, with its group and the attributes you can source (industry, size, location, role of buyer, who pushed for the purchase, problem, alternative considered, why they chose the client, outcome)
- **Pain-point frequency, ranked from the best-fit group**: each pain, how many best-fit sources mention it (n), the other groups in a separate contrast column, and the strongest short verbatim quote
- **Alternatives**: what each buyer used or considered instead, including doing nothing, how many sources name each (n), and why the buyer chose the client or the alternative. Step 4 is built on this.
- **Won versus lost patterns**, if both exist
- **Buyer language**: the exact words buyers use for the problem. Messaging should reuse these.
- **Role map**: who pushes for the purchase (the champion), who signs, who uses it, who could block it
- **Separators** (when CRM or win/loss data exists): the attributes that appear far more often in good customers than in lost, churned or struggling ones. Attributes that are about equal in both describe the market, not the ideal customer. Method in `references/scoring-and-validation.md`. Note that a CRM only records who found the client, so treat it as biased toward them.

**Check the quotes.** When the transcripts or interviews are files, run `scripts/check_quotes.py` on your draft (the quote bank, the sign-off message or the brief) against those files, and fix or remove any quote it cannot find word for word. A misquoted customer is an invented fact.

If there are **no** transcripts, surveys or interviews, say so and produce the **Top-5 customer conversation kit** from `references/intake-questions.md` (Part C): pick the client's five best customers and run a five-minute conversation with each. That is the fastest route from Hypothesis to Grounded.

### Step 3: Gaps and contradictions

Compare what the evidence says with what the ICP needs. List the gaps and contradictions (for example: the site claims fintech, but 5 of 6 case studies are retail). Draft targeted questions from the probing question bank in `references/intake-questions.md` (Part B): only those that change the answer, five or fewer, grouped, each with a default.

Do not stop here. Carry on with the defaults, marked `[Assumption]`, and put the questions in the ICP sign-off (Step 6), where the answers can still change the ICP before anything is built on it. When two sources disagree, keep both in view and ask which to trust at the sign-off; never average them or quietly choose. Stop earlier only for a true blocker (ground rule 5).

### Step 4: Why they buy

Firmographics say who *could* buy. They do not say why the best customers chose the client, so an ICP built on them alone returns lookalikes: companies that match on paper and have no reason to switch. Before defining the ICP, work out the reason to buy, in three parts. Method, tables and the client-type variants are in `references/why-they-buy.md`.

1. **Alternatives and what only the client gives.** List the alternatives buyers actually considered, including doing nothing, each with n and its sources. List what the client does that those alternatives do not, and the value that gives the buyer. Then ask which companies care most about that value: their traits are what belongs in Tier 1.
2. **The pain you can see from outside.** For each candidate Tier 1 segment, take its main pain (with n) and find two to five public data heuristics that would show that pain at a company nobody has spoken to yet, such as reviews, job posts, licences, filings or what is missing from its website. Name the source of each, say whether it carries a date, say why it suggests the company may be ready to talk to a vendor now, and rate its reliability (High / Medium / Low, with the reason; scale in `references/why-they-buy.md`). Look beyond LinkedIn and B2B databases: regulators, app stores, job boards, tenders and the other sources listed there. If none can be found, the segment is a **pain hypothesis**: say so in the brief. That label is separate from the evidence tier. State how many won accounts the heuristics rest on, against 20 to 30 where won-deal recordings exist.
3. **Candidate offers.** The offer in scope (Step 0) is what the client sells. The cold offer is what a Tier 1 company that has never heard of the client is offered first. Split the client's value into two to four candidate offers, each with its type of value (saves time, saves money or makes money), its frame, the segment it is for and the proof it rests on. The offer status is **untested** until an offer has been tried with real sends.

At Hypothesis tier much of this rests on the website: state the differentiated value as a thesis, label it, and carry the question that would confirm it into the sign-off and the validation plan. Never invent an alternative, a pain or a proof point to fill a row.

### Step 5: Define the ICP

Fill every row of the ICP table in `references/output-template.md`. The five core categories are:

- Company size
- Geography / location
- Industry / vertical
- Presence of specific roles
- Revenue range

Then add business model or stage, technology or operational characteristics, what they use today and the value only the client gives (from Step 4), ranked pain points (each tied to evidence), the pain visible from outside, trigger events, and **disqualifiers**. Give every Tier 1 criterion a one-line reason saying why accounts with that trait care more about the value from Step 4. A criterion with no reason describes the market, not the ideal customer.

Think in four layers: firmographic, technographic or operational, situational triggers, and behaviour. Firmographics set the boundary of who could buy. The reason to buy from Step 4 decides who belongs in Tier 1. Triggers and behaviour decide timing. Describe **negative ICP** too: accounts that look good but repeatedly fail, added as disqualifiers or gates.

Write the ICP sentence with the situation first (the pain or reason to buy), then the firmographic boundary. If the segment is a pain hypothesis, say so in the sentence.

Split the result into **Tier 1** (best fit: where the evidence is strongest) and **Tier 2** (adjacent: accounts where the evidence shows the same value from Step 4 matters, but with fewer proof points). Choose the direction Tier 2 widens in (a size band, a neighbouring sector, another region) from the evidence and say which evidence; never default to "one size-step above the best customers". Best fit means high win rate, healthy deal size, low churn and short sales cycle, not just the biggest logos. If the client has revenue or retention data, use it to choose. Case studies whose customer fails a disqualifier do not count towards Tier 1.

The ICP describes the *company*. Keep person-level detail for the persona. For consumer and local clients there are no firmographics: use the demographic, geographic (catchment) and behavioural variant in `references/client-types.md`, and treat the persona as the main output.

### Step 6: ICP sign-off

Everything after this step (the scoring model, personas, market size, packs and documents) is built on the ICP. A wrong ICP caught here costs one message; caught after delivery, it has already shaped the client's list and copy. So in a Full build, stop here and ask the user to confirm or correct it.

Send one message in the "ICP sign-off" format in `references/output-template.md`, containing:

- the evidence tier and label, and the ICP in one sentence
- the champion (who pushes for the purchase) and who signs, or that one person plays every role
- the why-they-buy summary from Step 4, including any pain hypothesis and the offer status
- Tier 1, Tier 2 (and the evidence that chose its direction) and the disqualifiers
- the evidence behind it: the pains ranked from the best-fit group with n, the other groups as a contrast column, and one verbatim quote each, with sources (checked with `scripts/check_quotes.py` when the sources are files)
- the gaps, contradictions and source conflicts from Step 3, each as a question with a default
- the three load-bearing assumptions: the ones that would change the ICP most if wrong, and what each would change

Then stop. Do not build the scoring model, personas, sizing, packs or any document yet, and say so in the message. When the user replies, apply their answers and corrections, record who reviewed the ICP and when (the brief header and `changelog.md` have a line for it), add any correction that would apply to other clients to the work lessons file, and continue with Step 7.

**When the user has asked for the whole job in one go** ("run it all the way through", "I won't be around to review"), do not stop. Put the sign-off contents at the top of the reply instead, carry on with the defaults, and label every output built after this point **"Draft: ICP not reviewed"**: the brief header, the scoring model, the sizing and every pack. Mark the client-facing summary "Draft: not for the client until the ICP is reviewed". Phrases about the inputs, such as "go with what I have" or "go ahead with what's here", answer the Step 0 checklist only; they do not skip this sign-off.

There is no sign-off in Quick mode or a Resonance check. In Refresh, stop here only if the new evidence changes Tier 1 or the disqualifiers; otherwise say in one line that they are unchanged and carry on.

### Step 7: Scoring model and Goldilocks check

Turn the ICP into a **scoring model** so it can rank a real list: a 0-100 **fit** score and a separate **readiness** score, with gates, disqualifiers and tier bands. Gates may carry points (the vertical is often both the gate and the heaviest weight), but never enough to reach the Tier 1 floor on their own, or every company that passes them is Tier 1. If gate points reach the Tier 2 floor, say in the brief that Tier 3 then holds only gate failures. Follow `references/scoring-and-validation.md` and run `scripts/score_accounts.py` when the user has a company list (start from `examples/scoring-model.json`).

- **Hold out 20% first.** Where accounts with known outcomes exist, set 20% aside before the separator test, test the finished model on them, and drop any rule that fails. Report it on the "Backtest result" line every time, or say why it could not be run. Scoring the customers the model was built from is a consistency check, not a backtest.
- **Readiness from evidence, not a stock menu.** Build readiness rules from the look-back on won and lost accounts where close dates exist, otherwise from the dated pain heuristics in Step 4, and say which. Score a pain as a counted, dated field (for example 2+ complaint reviews in 90 days), never as `truthy` on a free-text note. Label the readiness weights untested.
- **What the actions mean.** Readiness decides which message an account gets, not whether it is contacted: Tier 1 and visibly hurting gets "Prioritise now: pain-specific message"; Tier 1 with no signal gets "Contact now with the no-signal offer"; Tier 2 gets "Test after Tier 1"; an unknown gate gets "Confirm the gate before contact". High fit means Tier 1 only unless Tier 2 rests on the same evidence and the client can work both.
- **Exclude current customers and open deals** with a disqualifier on the client's CRM status.
- **Keep the citation trail in the model file:** `built_from`, `evidence_tier`, and an `evidence` line on every rule and disqualifier. The script warns when any is missing.

The scorer also writes two separate columns: **priority** (how much the account is wanted now, from the action) and **confidence** (how sure the score is, from the data behind it). Report them side by side and never merge them: a high-priority account can rest on thin data.

Report the script's flags (unknown-heavy fields, unreadable values, gate near misses, missing evidence, rows in `needs_review`) as data to fix before the tiers are trusted.

Then run the **Goldilocks check** from the same file: is this ICP the right size for the client's stage and selling motion? Report every check as **Pass / Fail / Unknown** with the actual figure next to the threshold (for example "4 reference customers against a bar of 5: Fail"). A near miss is a Fail, never a Pass.

### Step 8: Build the persona(s)

Use the persona template in `references/output-template.md`. A persona is semi-fictional but built from real data: every attribute must trace to a source or be marked `[Assumption]`, and its pains come from the best-fit group. **Always name the champion**, the person who pushes for the purchase and recommends it to whoever signs, separately from the user. When one person plays every role (for example a founder), say so. Add the **economic buyer** and any **blocker** when the evidence shows a buying committee. Include job title variants and seniority, goals, pains in the buyer's own words, objections, and what triggers them to look for a solution.

### Step 9: Size the market (TAM / SAM / SOM)

Read `references/frameworks.md` for definitions, both methods, SAM filters and SOM approaches.

- Compute **both** bottom-up and top-down when the data allows. Bottom-up is the primary method; top-down is the sanity check.
- Do the arithmetic with `scripts/tam_calc.py`, not in your head. Copy the closest file in `examples/` (`sizing-single.json`, `sizing-segments.json`, `sizing-services.json`, `sizing-ranges.json`), edit it and run it. It prints the TAM of each method, the SAM funnel, the SOM, and flags when the two methods disagree by more than 3x.
- **Say where the company count comes from** with `count_basis`: `counted` (a real list, register or database search) or `derived` (a share of a bigger total, such as 17,000 SaaS companies x 15%). A derived count is not a true bottom-up figure, and its agreement with top-down proves little; say so in the brief. The script flags it.
- Several segments or price tiers: use the `segments` list so each has its own count, ACV, filters and SOM, and the script adds them up. A top-level `top_down` is checked against the segment total.
- **Give uncertain inputs as ranges** (`{"low": ..., "base": ..., "high": ...}`). The script then reports low / base / high and a sensitivity table showing which input moves the answer most. Base the sensitivity note on that table.
- **SOM needs exactly one sales basis**: stated deals per year, sales capacity, or a share of SAM. If the client's sales capacity is unknown, any deals figure is an `[Assumption]` and must be called one everywhere it appears, including the client-facing summary.
- B2C clients: use `customers` and `annual_value`. Services and local clients: add a `delivery` cap to SOM (see `references/client-types.md`); the script takes the smaller of what sales and delivery allow and says which one binds.
- Source and date every count and market figure. A number without a source is an `[Assumption]`. Put each source in the input file (`acv_source`, `count_source`, a `source` on each filter, on the top-down figure and on the SOM basis); the script prints an "Unsourced inputs" list, and everything on it is an `[Assumption]` in the brief.
- **Say what kind of source the count came from** (`count_source_type`: register, directory, maps, aggregator or other) and estimate its coverage. A register count and an aggregator count are not equally reliable; where one source is thin, combine sources and remove duplicates.
- **Reachable contacts:** give `contacts_per_company` (the roles to reach from Pack 1) and report SAM companies times that number, with one line on what it means for how hard and how often the market can be followed up.

### Step 10: Resonance check

Run this on the finished ICP and on any asset the user wants tested. Process and output format are in `references/output-template.md` (section "Resonance check"). Be specific: quote the line that lands or misses, link it to a documented pain point, and suggest a rewrite.

- **Read it as the champion** unless the user names another persona. If the asset is addressed to someone else (for example a CRO), say whether that person is the champion or only the one who signs, and what that means for who should receive it.
- **For any outreach message, run the cold-message checks**, each Pass / Fail: the name-swap test (could it go to another company by changing only the name?), useful without a reply, the offer plain in the first lines, the word count against roughly 100, an easy ask aimed at a reply (a demo or meeting in a first cold message is a big ask: flag it and suggest a smaller one), and personal touches tied to a documented pain.

Be honest about the limits: this is a structured critique grounded in the ICP evidence, not real buyer feedback. If the ICP is Hypothesis-tier, say the verdict is weak for that reason. Recommend a read-through with 3 to 5 real prospects or customers as a sense check before sending, and the offer test with real sends as the real test.

### Step 11: Deliver

Lead with the answer: the ICP in one sentence, the champion and who signs, the headline TAM / SAM / SOM, the evidence tier and the top three risks or unknowns. Detail follows. Use the structure in `references/output-template.md`. The brief is the **internal working brief** and says so at the top; its header records the offer status and whether the ICP was reviewed (by whom and when) or is a draft. If the user answered the optional Step 0 question, the summary shows where the evidence agrees with their view and where it does not.

**What the client sees is a separate file.** The **client-facing summary** is always produced, as its own file (`client-summary.md` or a separate document), never only as a section of the brief. It leads with what the client can realistically win this year, in plain words with no TAM / SAM / SOM or ICP jargon; gives who to target first and who to avoid, the first offer (described as not yet tested), what is surprising or "Nothing yet", what happens next (the next deliverable and who produces it, plus at most two things only the client can do), and the evidence tier in plain words at the end. Every headline number that rests on an `[Assumption]` keeps a one-line basis ("about 40 new customers a year, assuming the sales team can close that many; we do not yet know its capacity"). Say in one line which file goes to the client.

**Check the links before delivering.** Run `scripts/check_links.py` on every file that carries links (the brief, the packs, the evidence pages log). Fix or remove every BROKEN link, and list the CHECK BY HAND links (LinkedIn blocks automated checks) for the user to open. The script says whether a page opens, not whether it shows what the file claims.

**Use packs.** Blocking question B5 ("What will the ICP be used for?") decides which of these are produced; if B5 was never answered, produce both. Offer any pack not produced in one line. The table is in `references/output-template.md` ("Delivery format"). Named prospects are not part of this skill: if the user asks for them, say so in one line and hand over the handoff file for the list builder. Each pack starts with a line giving the evidence tier, label, scoring-model version, the brief it was built from and the offer status, so the caveats travel with it.

1. **List-building spec and handoff file:** write `icp-handoff.json` to the client folder in the format in `references/handoff-format.md`: the filters with their reasons and evidence, titles (the champion's first), exclusions (always including current customers and open deals), triggers with their reliability, the rule for when Tier 2 work starts, the scoring model, the market size and sales capacity (for B2C: catchment, ad audiences and local channels instead). Check it with `python scripts/check_handoff.py icp-handoff.json --markdown`: fix every error, carry every warning into the brief, and deliver the printed text as Pack 1. Edit the JSON, never the printed Pack 1, so the two cannot disagree. The handoff file is where this skill's job ends; the next skills in the list-building chain read it
2. **Messaging inputs:** the candidate offers and their status; one hand-written example message per Tier 1 segment with the exact conditions that justify sending it (Pack 1's triggers come from these); the pain-to-angle table from the best-fit group; buyer language; proof points; objections grouped by the persona who raises them

**Format.** Unless the user names a format, decide with this rule. An explicit request for a format always wins, and applies for the rest of the conversation:

| Situation | Deliver |
|---|---|
| Quick mode, Resonance check, or a small Refresh | Chat only |
| Full build | Chat summary, **plus** the internal working brief as a shareable document (use the platform's editable document tool if there is one, otherwise a Word or PDF file), **plus** the client-facing summary as its own file. Only the client-facing summary goes to the client |
| Full build with a TAM / SAM / SOM model or a target-list spec | **Also** a spreadsheet with the ICP table, the evidence table, an assumptions tab (each with source and confidence), the sizing model with live formulas, and the list-building filters, so the client can change inputs and see the result |

Use whatever document and spreadsheet tools the environment offers, and load their instructions first. Do not stall asking about format; state what you chose in one line and offer to switch. Save every output to the client folder as well.

End with a **validation plan**: the next two to four actions that would raise the evidence tier, split into what the user (the contractor) will do and at most two things only the client can do. Include the real-send tests in `references/scoring-and-validation.md` ("Real-send tests of the offer and the message"): first the offer test (each candidate offer in one plain template to a Tier 1 list picked on firmographics, replies per email sent against a benchmark agreed in advance), then a weekly test of one pain-qualified segment with a small hand-checked list and hand-written messages. Other examples: the five customer calls, a short survey, a test list of 100 companies, the held-out test of the scoring model, a four-to-six-week pilot that changes the list or the message, not both at once. Also give the refresh cadence and name an owner for the profile. Finally, add a line to `changelog.md`, and to the work lessons file for anything the user corrected that would apply to other clients.

## Files in this skill

| File | Read it when |
|---|---|
| `references/lessons.md` | Step 0 of every job (read only: lessons about the skill itself, plus the line format). Lessons from real jobs go in the work lessons file beside the client folders |
| `references/intake-questions.md` | Steps 0, 3 and 6: inputs checklist, client request messages (business and local/consumer), blocking and probing questions, customer interview guides |
| `references/evidence-analysis.md` | Steps 1 and 2: website crawl, transcripts, surveys, CRM |
| `references/client-types.md` | Step 0: software, services, or local/consumer variants |
| `references/why-they-buy.md` | Step 4: alternatives and differentiated value, pain visible from outside, candidate offers |
| `references/frameworks.md` | Steps 5 to 9: definitions, ICP categories, TAM / SAM / SOM methods |
| `references/scoring-and-validation.md` | Steps 7 and 11: fit and readiness scoring, separators, validation, market list, upkeep |
| `references/output-template.md` | Steps 4 to 11: brief structure, tables, ICP sign-off, persona, use packs, client-facing summary, resonance check, delivery format |
| `scripts/check_quotes.py` | Steps 2 and 6, and before delivering: check that every customer quote appears word for word in the transcripts |
| `references/handoff-format.md` | Step 11: the handoff file's fields, when to write it, and what stays out of it |
| `scripts/check_handoff.py` | Step 11: check the handoff file and print it as Pack 1 |
| `scripts/check_links.py` | Before delivering: check that every link in the brief, the packs and the evidence log opens; LinkedIn links are listed for checking by hand |
| `scripts/tam_calc.py` | Step 9: TAM / SAM / SOM arithmetic, single or multi-segment |
| `scripts/score_accounts.py` | Step 7: score a company CSV against the ICP model; writes each account's action, priority and confidence, and a review queue for low-confidence research |
| `scripts/flatten_research.py` | Steps 7 and 11: turn per-account research JSON into a CSV the scorer reads |
| `examples/` | Steps 7, 9 and 11: runnable sizing inputs, a scoring model, a handoff file, a messy accounts CSV and sample research output to copy from |
| `tests/run_tests.py` | After changing any script: `python tests/run_tests.py` must pass |
| `evals/` | When testing changes to this skill (for example with skill-creator): `evals.json` plus one folder per newer test case |

## Handing off

This skill defines *who* to target and *how big* the market is; its job ends with the handoff file (`icp-handoff.json`). The next steps are separate skills, each with one job: where to find the companies and people (lead sources), the searches to run in each tool (search queries), and pulling, cleaning and scoring the list (list building). Hand them the handoff file, not the brief. Until those skills exist, hand Pack 1 to the `clay-search-query` skill if it is available to turn it into a Clay search; never write a search link for a tool from memory. If the user then needs the wider outbound engine (data sources, reachability, buying signals, how long the market lasts against a daily quota) and a skill for that is available, suggest it and pass the ICP across as its starting segment.
