# Evidence analysis

Contents:
- Website crawl
- Transcripts and interviews
- Surveys
- CRM data
- Combining sources

---

## Website crawl

**Goal:** read everything that reveals who the client sells to, what they sell, and how they talk about it.

### Procedure

1. Fetch the homepage. Note the navigation, footer links and any "Customers", "Industries", "Solutions", "Who it's for" or "Resources" menus.
2. Try `/sitemap.xml` (and `/robots.txt` for a sitemap link) to get a full page list. Many sites list every case study there even when the navigation hides them.
3. Fetch pages in this priority order:
   1. Case studies / customer stories / success stories
   2. Testimonials and reviews
   3. Logo walls and "trusted by" sections
   4. Industry, solution and use-case pages
   5. Services / products / features
   6. Pricing and plans
   7. About, team and careers (size, footprint, what they are hiring for)
   8. Blog and resources (which reader the content is written for)
   9. Partners, integrations and press
   10. Legal and contact pages (registered entity, locations)
4. Look off-site for third-party proof: review platforms (G2, Capterra, Trustpilot, Google reviews), press coverage, the company's LinkedIn page, conference talks and webinars. If a source cannot be reached, say so.
5. Keep a **pages log**: URL, read / not reachable, one line on what it gave. If a page is blocked or rendered so you cannot read it, record it as not reachable and ask the user to paste or screenshot it. Under it, keep three lines of **research notes**: what was hard to find, what you tried when a search failed, and how you checked facts (quote check, link check, a second source).

### Extract

- Every distinct offer, in a list, with product names
- Named customers and exactly what each bought
- Testimonial speakers: name, job title, company (titles tell you the buyer and champion roles)
- Industries and company types mentioned, and whether case studies actually back up the sector claims
- Company-size clues (customer team sizes, "SMB" or "enterprise" language, pricing tiers)
- Geographies served, languages, currencies
- Pricing signals, including a deliberate absence ("contact us")
- How the client describes the problem, in their own words
- Competitors or alternatives named
- **Logos without a case study** are weaker evidence than a described engagement; note which is which

### Interpret

- Compare what the site *claims* (industries listed) with what it *proves* (case studies). The gap is a key question for the user.
- Count: how many case studies per industry or size band? That is the evidence for the Tier 1 versus Tier 2 split. Leave out case studies whose customer fails a disqualifier (for example a public body when public procurement is not supported): the client chose to publicise every case study, which does not make each one a good fit.
- The language the site uses for the problem may differ from how buyers describe it. Flag this for the transcript analysis.

---

## Transcripts and interviews

### First: tag every source by group

Before counting anything, tag every transcript, interview, survey response and CRM account with one group:

| Group | Who belongs |
|---|---|
| Best-fit customer | The client's best customers: from the user's answer to "which customers are best", the best-customer scorecard (`scoring-and-validation.md`, "Building the 0-100 fit model", step 1), or CRM outcomes (won, still active, healthy) |
| Other customer | Won, but not among the best |
| Lost | Evaluated the client and chose something else |
| Churned or struggling | Bought, then left or had a poor result |

If nobody has said which customers are best, use won-and-still-active as the default, mark the tagging `[Assumption]`, and put it in the ICP sign-off as a question. Not every customer is good evidence: pains voiced by bad-fit buyers would otherwise shape the ranking, the personas and the messages.

### One pass per source, written to a file

Process each transcript or interview **on its own**, one at a time (in a subagent if one is available), and write its record to a file in the client folder (`evidence/T1.md`, `evidence/T2.md`...). Build the pain counts, the alternatives and the quote bank from those record files, not from all the transcripts held in context at once: that is how counts drift and quotes get mixed up.

### Per transcript, record

| Field | Notes |
|---|---|
| ID | T1, T2... (use for citations) |
| Group | Best-fit customer / other customer / lost / churned or struggling |
| Who pushed for the purchase | The champion: the role that pushed for it inside the company, and whether it was the person speaking |
| Company attributes | Industry, size, location, tools in use. Only what is stated. |
| Speaker roles | Title and seniority of everyone who speaks for the buyer |
| Stated problem | One short verbatim quote |
| Trigger | What happened that made them look for a solution |
| Alternatives | What they used or considered, including "do nothing" |
| Why they chose | Why they picked the client over the alternatives, or the alternative over the client (verbatim where possible) |
| Objections | Price, timing, risk, internal politics, missing feature |
| Decision process | Who decides, who influences, steps, timeline |
| Budget signals | Any figures or budget statements |
| Outcome | Won / lost / stalled, and the stated reason |
| Buyer language | Distinctive phrases for the problem and the benefit |

### Aggregate

- **Pain frequency, from the best-fit group:** rank each pain by how many best-fit sources mention it, and state n ("3 of 4 best-fit customers"). Show the other groups in a separate contrast column (lost, churned, other customers), never merged into the ranking. Persona pains and Pack 2's message angles come from the best-fit ranking.
- **Alternatives:** each alternative and how many transcripts name it (n), including doing nothing, with why the buyer chose the client or the alternative. This is the input to Step 4 ("Why they buy").
- **Won vs lost:** which attributes (size, industry, role, trigger) separate wins from losses?
- **Role map:** who raises the problem, who pushes for the purchase (the champion), who evaluates, who signs, who could block it?
- **Quote bank:** short verbatim quotes (up to about 25 words each) labelled with transcript ID, drawn from the best-fit group first. Never paraphrase a quote and present it as verbatim. When the transcripts are files, check the bank with `scripts/check_quotes.py` (see SKILL.md Step 2).
- **How many won accounts the pain rests on:** state the number of won accounts behind the pain heuristics in Step 4, against 20 to 30 where won-deal recordings exist.

### Cautions

- Sales calls over-represent what the salesperson asked about. Where possible, favour what the buyer volunteered.
- Do not infer company size or industry that nobody stated; mark it `[Assumption]` or leave it blank.
- Treat any personal details in transcripts as sensitive. Use roles and company attributes in the output, not private contact details.

---

## Surveys

- Break results down by customer segment (industry, size, tenure), not just the overall average.
- The best-fit segment is usually the one with the highest satisfaction and retention, which is not always the one with the most responses.
- Free-text answers: treat like quote bank material and count recurring themes.
- State response count and the likely bias (for example, only happy customers replied).

---

## CRM data

**Phase 0: check the accounts are real.** Before analysing, confirm each account is a real, operating company (a working website, a company page or a register entry), and drop test records, duplicates and personal sign-ups. Say how many were dropped. Note which accounts are current customers and which are open deals: they are excluded from every prospect list (`scoring-and-validation.md`).

Group customers by industry, company size band, geography, lead source and buyer title. For each group compute where the data allows:

- Number of customers
- Win rate
- Average deal size (ACV)
- Sales cycle length
- Churn or retention

**Best fit** = high win rate + healthy ACV + low churn + short cycle. Where cost-to-serve, support load or margin data exists, include it too, since a large account that needs constant custom work can be worse than a small one that renews. Name the groups that score well on several of these, and the groups that look good on one metric but poor on others (for example: big deals but 40% churn).

If the dataset is too small to segment (under about 20 customers), say so and describe patterns qualitatively instead of with percentages.

Missing fields are common. Report coverage ("size is filled for 62% of records") rather than silently skipping.

**Win versus loss comparison (separator test).** Pull won, lost, churned and stalled accounts for a defined period, and compare how often each attribute appears in each group. A large gap marks a discriminator that belongs in the fit model. An attribute about equally common in wins and losses describes the market, not the ideal customer. Promote an attribute only if the gap holds in two periods or two segments. Full method in `scoring-and-validation.md`.

**Survivorship bias.** A CRM records who found the client (inbound, referrals, event scans), not the market. Say so in the output, and recommend testing against companies that never contacted the client.

---

## Customer interviews

Interviews explain the *why* behind CRM patterns. Use the guide in `intake-questions.md` (Part C2). Interview more than one outcome group (successful, struggled, churned, lost), use a consistent guide, and separate observed facts from interpretations: "three recent buyers mentioned a coming migration" is evidence; "companies like this hate their tools" is a hypothesis.

---

## Combining sources

| Question | Strongest source | Cross-check with |
|---|---|---|
| Who actually buys? | CRM | Case studies, transcripts |
| Why do they buy? | Transcripts, interviews | Surveys |
| What do they compare the client with? | Transcripts, interviews (alternatives) | Lost-deal reasons, review sites, the client's comparison pages |
| Who is the buyer / champion? | Transcripts | Testimonial titles |
| What do they call the problem? | Transcripts, surveys | Website copy |
| Who is the intended market? | Website | Client answers |
| Why do deals fail? | Lost-deal transcripts, CRM notes | Competitor pages |

When two sources disagree, report both and ask the user which to trust, in the ICP sign-off (SKILL.md Step 6) unless the conflict blocks the work sooner. Do not average them or quietly choose.
