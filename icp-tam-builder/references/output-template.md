# Output template

Contents:
- Brief structure (the internal working brief)
- ICP table
- Why they buy
- ICP sign-off (Step 6)
- Fit and readiness model
- Customer evidence table
- Persona template
- Market sizing section
- Use packs (list-building spec, messaging inputs)
- Client-facing summary (its own file)
- Resonance check
- Delivery format
- Validation plan
- What changed (Refresh mode)

Lead with the answer. Put detail below it. Keep lists one item per line.

---

## Brief structure

The full brief is the **internal working brief**: for the user, not the client. What the client sees is the client-facing summary, a separate file (see below).

```
# ICP & TAM brief: [Client]
INTERNAL WORKING BRIEF: not for the client. The client gets client-summary.md.
Offer in scope: [one product/service]
Why this offer: [one line: why it was picked over the client's other offers, which become separate ICPs]  (only when the client sells more than one)
Offer status: untested / tested ([what was sent, to how many, replies per send, date])
Date: [date]
Evidence tier: Hypothesis / Grounded / Validated  ([n] transcripts, [n] customers in CRM, [n] interviews)
Label: ICP / Early Customer Profile  ([n] comparable great customers against a floor of 8 and a bar of [n] for this selling motion)
ICP review: reviewed by [name] on [date] / Draft: ICP not reviewed
Client folder: [path]

## 1. Summary
- ICP in one sentence (the situation first, then the firmographic boundary)
- Champion in one sentence (the person who pushes for the purchase), and who signs
- TAM / SAM / SOM headline numbers (with currency, year, confidence; as a range when inputs were ranged)
- Top 3 risks or unknowns
- Your view against the evidence (only if you gave one in Step 0): where the evidence agrees, and where it does not

## 2. Evidence used
Pages read, files analysed, what was NOT available. (See table below.)

## 3. ICP
(ICP table, Tier 1 and Tier 2, disqualifiers)

## 4. Why they buy
(Alternatives and what only the client gives, the pain visible from outside, candidate offers)

## 5. What the customers say
(Pain frequency from the best-fit group, with the other groups as a contrast column; buyer language; won vs lost; quote bank)

## 6. Persona(s)

## 7. Market size: TAM, SAM, SOM

## 8. Use packs: the ones produced (see "Delivery format"), plus where the client summary is

## 9. Resonance check  (include when messaging or an asset was provided)

## 10. Validation plan and open questions

## 11. What changed  (Refresh mode only)

## Appendix: pages log, research notes, customer evidence table, assumptions list
```

When the user asked for the whole job in one go and the ICP was not reviewed (SKILL.md Step 6), the "ICP review" line reads "Draft: ICP not reviewed", and the same words go at the top of the scoring model, the sizing section, every pack and the client summary.

**Your view against the evidence.** If the user answered the optional Step 0 question ("who do you think buys and why?"), quote their answer in one line, then give, one line each, the points the evidence supports and the points it contradicts, with sources. This is a comparison, not a verdict on the user.

### Evidence used table

| Source | Type | What it gave | Limits |
|---|---|---|---|
| [URL or file] | Website / transcript / CRM / survey | One line | One line |

---

## ICP table

State the ICP in one sentence first, with the situation (the pain or reason to buy) before the firmographic boundary, for example: "Private dental clinics in Lagos, Abuja and Port Harcourt that are losing bookings to unanswered phone calls, with 3 to 15 chairs and a dedicated practice manager." If no public data shows the pain, add "(pain hypothesis)".

| Criterion | Tier 1 (best fit) | Tier 2 (adjacent) | Why it matters | Evidence | Confidence |
|---|---|---|---|---|---|
| Industry / vertical | | | | | |
| Company size | | | | | |
| Revenue range | | | | | |
| Geography | | | | | |
| Presence of specific roles | | | | | |
| Business model / stage | | | | | |
| Technology / operational traits | | | | | |
| What they use today (the alternative) | | | | | |
| Value they get that the alternative can't give | | | | | |
| Top pain points (ranked, best-fit group) | | | | | |
| Pain visible from outside (heuristic, source, dated?) | | | | | |
| Trigger events | | | | | |
| **Disqualifiers** | | | | | |

Rules:
- "Why it matters" says, in one line, why accounts with this trait care more about the value only the client gives (from Step 4). Required for every Tier 1 criterion; a criterion with no reason describes the market, not the ideal customer
- "Evidence" cites a source (T3, case study URL, CRM segment) or says `[Assumption]`
- "Confidence" is High / Medium / Low, and below High needs the reason
- Tier 1 needs real evidence; if there is none, it is not Tier 1
- Tier 2 holds accounts where the evidence shows the same value matters, with fewer proof points. Say which direction it widens in (size, sector or region) and which evidence chose it; never default to "one size-step above"
- Case studies for customers that fail a disqualifier do not count towards Tier 1
- "Pain visible from outside" says "pain hypothesis" when no public data heuristic was found

---

## Why they buy

Method in `why-they-buy.md`. Three short tables, each row sourced or marked `[Assumption]`:

```
Alternatives buyers considered
| Alternative | n (sources) | What the client does that it doesn't | Value to the buyer | Evidence | Confidence |
Named by the client, not by buyers: [list, or "none"]
Differentiated value, in one sentence: [statement]  (at Hypothesis tier: "Thesis: ... To confirm: ...")

Pain visible from outside
| Segment | Pain (n) | Heuristic | Source | Dated? | Why it suggests ready now | Reliability (High / Medium / Low, why) | Link to the pain (evidence or [Assumption]) |
Pain hypothesis: [segments with no heuristic found, or "none"]
Won accounts these heuristics rest on: [n], against 20 to 30 where won-deal recordings exist

Candidate offers  (Offer status: untested)
| Candidate offer | Value type | Frame | Segment | Proof it rests on | Status |
Offer for Tier 1 companies with no visible trigger: [which]
```

---

## ICP sign-off (Step 6)

One message, sent after the ICP is defined and before anything is built on it. In a one-go run (SKILL.md Step 6), the same contents go at the top of the reply instead, headed "ICP not reviewed: here is what everything below rests on".

```
ICP sign-off: please confirm or correct this before I build on it.
Nothing has been built on it yet: no scoring model, personas, market size or packs.

Evidence tier: [tier]   Label: [ICP / Early Customer Profile, n against the floor of 8 and the bar of n]
ICP in one sentence: [situation first, then the firmographic boundary]
Champion: [role] (signs: [role])  /  one person plays every role: [role]

Why they buy
- Alternatives buyers considered: [alternative (n, sources)], ...
- What only the client gives: [value] ([source] / [Assumption] / thesis)
- Pain visible from outside: [pain (n)] shown by [heuristic, source, dated?] / pain hypothesis
- Candidate offers: [offer: value type, proof], ...  Status: untested

Tier 1: [one line]
Tier 2: [one line, and the evidence that chose its direction]
Disqualifiers: [one per line]

Evidence behind it (best-fit group: [which accounts], n = [n])
| Pain | n in best-fit group (sources) | Other groups: lost / churned / other (n) | Strongest verbatim quote (source) |

Questions (answer any you like; the default applies otherwise)
1. [Gap, contradiction or source conflict from Step 3, as a question] (Default: [...])

Load-bearing assumptions (if one is wrong, the ICP changes)
1. [Assumption]: [what it would change]
2. ...
3. ...

Reply "confirmed", or correct anything above.
```

Rules:
- Three load-bearing assumptions: the ones that would change the ICP most if wrong. Give fewer only if there are fewer, and say so
- Pains are ranked by the best-fit group's count; the other groups sit in the contrast column, never merged into the ranking
- Every quote is verbatim and carries its source ID; when the sources are files, run `scripts/check_quotes.py` on this message first
- Do not add analysis here that the user has to wade through. This is a checkpoint, not the brief

---

## Fit and readiness model

Include when the ICP will be used to rank a list. Method and rules in `scoring-and-validation.md`. The model file carries the same citation trail: `built_from`, `evidence_tier`, and an `evidence` line on every rule and disqualifier.

```
Model: [name] v[version], effective [date], owner [name]
Built from: [brief file and date]   Evidence tier / ICP or Early Customer Profile: [label]
ICP review: reviewed by [name] on [date] / Draft: ICP not reviewed

Gates (must be true, with points): [list]. Gate points total: [n], against bands of [T1] / [T2]; if at or above the Tier 2 floor, say that Tier 3 holds only gate failures
Disqualifiers: [list, each with reason and evidence; always including current customers and open deals]
Fit rules (positive points add to 100):
| Layer | Attribute | Rule | Points | Evidence | Source of the data |
Readiness rules (positive points add to 100, decaying with age; weights untested until the three-campaign test):
| Signal | Rule | Points | Where it came from (look-back / Step 4 heuristic) | Where detected | Typical age before it stops counting |
Bands: Tier 1 at [n]+, Tier 2 at [n] to [n-1], Tier 3 below
High fit: Tier 1 only / Tier 1 and Tier 2 (with the reason)
Action matrix: fit x readiness (see scoring-and-validation.md)
Backtest result: [held-out n, what was checked, which rules were dropped] / not run: [why]. Scoring the accounts that built the model is a consistency check
Data issues from the scoring run: [unknown-heavy fields, unreadable values, gate near misses, rules without evidence, rows in needs_review]
```

Tell the user the weights are hypotheses and will be corrected quarterly, and that the readiness weights are untested until real sends have compared them with the no-signal offer.

### Goldilocks check

| Check | Threshold | Actual | Result |
|---|---|---|---|
| Contract value supports the cost of selling | [scaled to this market] | | Pass / Fail / Unknown |
| Sales cycle the client can fund | [client's runway] | | |
| Reference customers in this ICP | 5 | | |
| Cost to serve as a share of contract value | about 30% or less | | |
| Reachable targets | 100 or more | | |

A near miss is a Fail. Say which thresholds were scaled from US software figures.

---

## Customer evidence table

| Customer / call | Group | Industry | Size | Location | Buyer role | Who pushed for the purchase | Problem (short quote) | Alternative considered | Why they chose the client (or the alternative) | Outcome | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|

"Group" is one of: best-fit customer, other customer, lost, churned or struggling (`evidence-analysis.md`, "Tag every source"). Leave fields blank rather than guess.

---

## Persona template

Always name the **champion** (the person who pushes for the purchase inside the account and recommends it to whoever signs), separately from the user and the economic buyer. When one person plays every role (for example a founder who finds, chooses, signs and uses), say so in one line instead. Add one persona per other distinct buying role (economic buyer, user, blocker) when the evidence shows them. Build every persona's pains from the best-fit group's evidence.

```
### [Persona name, a label, e.g. "The Overstretched Practice Manager"]
Role in the deal: champion / economic buyer / user / blocker
Typical titles: [variants]
Seniority and reporting line:
Buying power: [budget scope, who they recommend to, who signs]
Goals:
KPIs they are measured on:
Pains, in their own words: ["quote" (T2)] ...
What they have tried before:
Objections:
How they evaluate and decide (criteria, must-have versus nice-to-have):
Who else is involved (economic buyer, technical influencer, champion, blocker):
What triggers them to look:
Where they get information:
Success after buying (what they will measure):
Evidence behind this persona: [sources] / Assumptions: [list]
```

---

## Market sizing section

| Measure | Value | Inputs and source | Confidence |
|---|---|---|---|
| TAM, bottom-up | | companies x ACV, sourced and dated | |
| Count basis and source type | | counted or derived; register / directory / maps / aggregator; estimated coverage | |
| TAM, top-down | | market x relevance x subsegments, sourced and dated | |
| Triangulation | | ratio and which one is trusted | |
| SAM | | funnel filters, each sourced | |
| SOM (12 months) | | capacity or share basis | |
| Reachable contacts | | SAM companies x roles to reach (from Pack 1) | |

Then:
- SAM funnel table (from `tam_calc.py` output)
- The script's "Unsourced inputs" list, each carried into the assumptions list as `[Assumption]`
- Assumptions list, each with a source or `[Assumption]`
- Low / base / high scenario and the sensitivity table, when inputs were given as ranges
- Sensitivity: the one input that moves the answer most (the top row of the script's sensitivity table)
- If the count is derived, one line saying the bottom-up and top-down figures are not independent
- If the count comes from one aggregator alone, one line saying it is directional; where one source is thin, combine sources and remove duplicates
- Reachable contacts: one line on what the number means for follow-up. A small pool cannot be emailed hard or for long, so follow-ups are fewer and slower; the outbound hand-off (SKILL.md "Handing off") sets the actual pace

---

## Use packs

Each pack is built from the ICP and persona already in the brief, so nothing new is invented here. Which packs are produced depends on blocking question B5 (see "Delivery format"). If the ICP was not reviewed (SKILL.md Step 6), each pack starts with "Draft: ICP not reviewed".

Every pack starts with this line, so the caveats travel with it when it is handed on:

```
Evidence tier: [tier] | Label: [ICP / Early Customer Profile] | Scoring model: [name] v[n] | Built from: [brief file, date] | Offer status: [untested / tested]
```

### Pack 1: List-building spec

Written tool-neutral, so it can be translated into any database, search tool or directory. **Pack 1 is printed from the handoff file** (`icp-handoff.json`, format in `handoff-format.md`) with `python scripts/check_handoff.py icp-handoff.json --markdown`, so fill the handoff file, not this outline. The outline below shows what it must cover.

```
Target: [Tier 1 one-liner]
Must-have filters:
- Industry / vertical: [specific values]
- Company size: [employees range]
- Geography: [places]
- Revenue range: [range, if used]
- Technology or operational traits: [values]
Roles to reach, champion first:
- Champion: [title variants, seniority]
- Then: [economic buyer and other roles, one per line]
Role that must exist at the company: [if relevant]
Trigger signals (boost priority): [list, one per line, with where to detect each and its reliability. Build them from the sending conditions of the example messages in Pack 2 and from the dated visible-pain heuristics in "Why they buy"]
Exclusions / disqualifiers: [list, one per line]
- Always: current customers and open deals, from the client's CRM (if there is no CRM export, the client checks the list before any outreach)
Tier 2: [one-liner, the differences, and the evidence that chose its direction]
When Tier 2 work starts: once every Tier 1 account has been contacted at least once, add as much of Tier 2 as the client can work this quarter
Scoring: apply the fit and readiness model; the action column says which message each account gets
Market list steps: raw export (list v1) -> enrich -> remove customers and open deals -> score all -> Tier 1 first, then Tier 2 by capacity -> validate by tier -> refresh quarterly
Per-account research prompts: see scoring-and-validation.md (extraction, then classification)
Test before scaling: pull 100 companies, check how many truly fit the ICP, record the fit rate
Data caution: sample-check 20 to 30 records for accuracy and coverage before trusting any database in this market
```

For B2C and local clients, replace the filters with: catchment area, ad-audience definitions (location, age band, interests, behaviours), local partnership targets, and community or referral channels.

### Pack 2: Messaging inputs

Start with the offer, because the message angles below only matter once there is something worth replying to.

```
Offer inputs   (Offer status: untested)
| Candidate offer | Value type (saves time / saves money / makes money) | Frame | Segment | Proof it rests on |
Offer for Tier 1 companies with no visible trigger: [which]
```

Then **one hand-written example message per Tier 1 segment**, written for one real or illustrative account in that segment:

```
Segment: [which]
Send this when: [the exact conditions that justify it, e.g. "2+ reviews in the last 90 days say calls go unanswered"]
Found in the prospect's own public data: [what, with source]
Message: [the full message, under about 100 words, offer plain in the first lines, an easy ask aimed at a reply]
Name-swap test: Pass (it would not make sense sent to another company)
```

Pack 1's trigger signals are built from these "Send this when" conditions.

Then, from the best-fit group's evidence:

| Pain (ranked) | Evidence (n, best-fit group) | Message angle | Proof point available | Buyer's own words |
|---|---|---|---|---|

Then, a buying-stage table:

| Stage | What the buyer needs | Proof or content that helps | Where they look |
|---|---|---|---|
| Realising the problem | Recognise the business case | Short insight, benchmark, a story like theirs | |
| Comparing options | See whether this approach fits | Comparison, demo, plain explanation | |
| Deciding | Reduce the risk of choosing | Reference from a similar customer, case study, clear terms, a small first step | |
| Getting started | Know how it will go live | Simple plan, timeline, who does what | |

Fill the last column from evidence, otherwise `[Assumption]`.

Then:
- **Objections and how to answer them**, grouped by the persona who raises them (champion, economic buyer, user, blocker), with the evidence each answer rests on. Write each answer so the champion can pass it on to the others
- **Do-not-say list:** claims the client cannot back up with the evidence they actually have
- **Channel notes:** where this persona pays attention (from the evidence, otherwise `[Assumption]`)
- **Research fields are for scoring, not first lines.** `what_they_sell` and `who_they_sell_to` rank and group accounts; restating them in a first line says nothing about the buyer's problem. Without a specific pain or signal for an account, lead with the offer

---

## Client-facing summary (its own file)

Always produced in a Full build, as **its own file** (`client-summary.md`, or a separate document), never a section buried in the brief. One page, plain language, no internal jargon. Leave out TAM, SAM, SOM, ICP, "evidence tier" and "Early Customer Profile" as terms; say what they mean instead.

```
# Who to target first: [Client]
[Date]

What you can realistically win this year
[One or two sentences: about [n] new customers a year, worth about [amount], limited by [sales capacity / how many your team can deliver / a stated assumption]. Then, as context only: the wider market we could find is about [amount] a year, of which about [amount] is within reach of how you sell today.]

Who your best customers are
[One paragraph]

Who to target first, and who to avoid
[Tier 1 in plain words; the disqualifiers as "who to avoid", each with the reason]

What to offer them first
[The suggested first offer, and that it has not yet been tested with real prospects]

What we found that is surprising
[One to three points, or: "Nothing yet: this view comes from [your public pages / the material you sent]."]

What happens next
- We will: [the next deliverable and who produces it, e.g. "pull and rank the first 100 companies by [date]"]
- We need from you (at most two things): [1] [2]

How sure we are
[One or two plain sentences, e.g. "This is our starting view from your public information. It gets sharper once we have spoken to five of your customers."]
```

Rules:
- Every headline number that rests on an `[Assumption]` keeps a one-line basis in plain words ("about 40 new customers a year, assuming the sales team can close that many; we do not yet know its capacity"). Never imply that the client's capacity, prices or results are known when they are not
- The confidence table and the full assumptions list stay in the internal brief
- If the ICP was not reviewed (SKILL.md Step 6), mark the whole summary "Draft: not for the client until the ICP is reviewed"
- "How sure we are" turns the evidence tier into plain words: Hypothesis = "our starting view from public information"; Grounded = "built from your customers' own words and records"; Validated = "tested against real results"

---

## Resonance check

Use on the finished ICP or on any asset the user supplies (email, landing page copy, offer, pitch script, ad). **Read it as the champion** unless the user names another persona; if the asset is addressed to someone else (for example a CRO), say whether that person is the champion or only the one who signs, and what that means for who should receive it.

**Process**
1. Re-read the relevant persona and the pain points with their evidence.
2. Read the asset as that buyer would: what do they see in the first five seconds, what do they understand, what do they doubt?
3. Check it against the buyer's own language from the quote bank.
4. Check claims against the evidence the client actually has (no promise the case studies cannot back up).
5. For any outreach message (cold email, LinkedIn message, cold-call opener), also run the cold-message checks below.

**Cold-message checks** (each Pass / Fail, with the line it rests on)
- **Name-swap test:** could the same message go to another company by changing only the name? If yes: Fail. It is about the sender, not the reader.
- **Useful without a reply:** does it give the reader something useful even if they never reply, sign up or book a demo?
- **Offer stated plainly** in the first lines.
- **Length:** the word count, against roughly 100 words.
- **The ask:** an easy ask aimed at a reply. Asking a stranger for a demo or a meeting in the first message is a big ask; flag it and suggest a smaller one.
- **Personal touches tie to a pain:** each personal line connects to a documented pain or signal, not a restatement of the company's own description.

**Output**

```
Asset: [what was tested]   Persona: [champion / which]   Evidence tier of ICP: [tier]
Verdict: Strong / Mixed / Weak, with one-line reason

Lands:   [line from the asset] -> [documented pain it hits] ([source])
Misses:  [line] -> [why it misses: wrong seniority, jargon, no proof, solves a pain nobody mentioned]
Red flags: [unsupported claims, wrong tone, wrong channel]
Cold-message checks (outreach only):
  Name-swap test: Pass / Fail. [line]
  Useful without a reply: Pass / Fail. [why]
  Offer plain in the first lines: Pass / Fail
  Length: [n] words against about 100: Pass / Fail
  Ask aimed at a reply: Pass / Fail. [the ask, and a smaller one if it fails]
  Personal touches tied to a pain: Pass / Fail / None used
Suggested rewrite: [specific line-level changes using buyer language]
Confidence in this verdict: [High/Med/Low]. [Reason, e.g. "ICP is Hypothesis-tier"]
```

Limit: this is a structured critique grounded in the evidence, not real buyer feedback. A read-through with 3 to 5 real prospects or customers is a sense check before sending; the real test is the offer test with real sends (`scoring-and-validation.md`).

---

## Delivery format

Unless the user names a format:

| Situation | Deliver | Goes to the client |
|---|---|---|
| Quick mode, Resonance check, small Refresh | Chat only | Nothing, unless asked |
| Full build | Chat summary, the internal working brief as a shareable document, and the client-facing summary as its own file | The client-facing summary only |
| Full build with a sizing model or list spec | Also a spreadsheet: ICP table, evidence table, assumptions tab (each with source and confidence), sizing model with live formulas, list-building filters | The client-facing summary; the spreadsheet only if the client asks for the model |

**Which packs.** The client-facing summary is always produced. The answer to blocking question B5 ("What will the ICP be used for?") decides the other two:

| B5 answer | Pack 1 (list-building) | Pack 2 (messaging) |
|---|---|---|
| Outbound list-building | Yes | Yes |
| Messaging and copy | No | Yes |
| Positioning or product decisions | No | Yes |
| Pitching the client | No | No |
| Not answered | Yes | Yes |

**Named prospects are not a pack.** If the user asks for named companies or people, say that is the list builder's job, and hand over the handoff file (`handoff-format.md`).

Offer any pack not produced in one line at the end ("I can also write the list-building spec"). Say which format you chose in one line and offer to switch. Load the instructions of whichever document or spreadsheet tool you use before writing.

---

## Validation plan

End every brief with two to four concrete actions that would raise the evidence tier, **split by who does them**:

```
We will do:
- [contractor action, with a date]
- ...
Only you can do (at most two):
- [client action, in plain words]
- ...
```

Examples:

- Run the top-5 customer conversations (script in `intake-questions.md`, Part C1)
- Test the scoring model on the held-out 20%, and compare Tier 1 with Tier 2 at each stage of the customer journey
- Offer test: send each candidate offer in one plain template to a Tier 1 list picked on firmographics only, and count replies per email sent against a benchmark agreed with the client in advance; until then the offer status stays "untested"
- Then a weekly pain-segment test: one pain-qualified segment a week, a small hand-checked list, hand-written messages, kept or dropped the next week
- Three-campaign test of the readiness signals: no signals, one signal per campaign, real-time triggers; keep a signal's points only if it beats the no-signal campaign
- Run a four-to-six-week pilot that changes one thing per comparison: the list (ICP order against a control group, same plain message) or the message (tailored against plain, same list)
- Pull a 100-company test list matching Tier 1 and check how many truly fit
- Get won and lost deal recordings or transcripts from the last 6 months: at least 5, ideally 20 to 30 won deals where they exist
- Send a five-question survey to active customers, segmented by Tier 1 versus Tier 2
- Ask the client to confirm the three biggest assumptions
- Ask five customers what else they considered and why they picked the client, to confirm or overturn the differentiated-value thesis

---

## What changed (Refresh mode)

One line per change, previous value first, with the evidence that moved it:

```
- [Criterion]: from "[old value]" to **[new value]**. [Evidence: source, n]
```

Then: the old and new evidence tier, the scoring model's old and new version, and any criterion dropped because nothing supports it. Copy the same lines into the client folder's `changelog.md`.
