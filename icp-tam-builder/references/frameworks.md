# Frameworks: ICP, persona and market sizing

Contents:
- Definitions
- ICP categories
- TAM: bottom-up
- TAM: top-down
- Triangulating the two
- SAM
- SOM
- Where to find the numbers
- Common mistakes
- Segmented sizing
- Ranges and sensitivity
- Worked example (illustrative)

---

## Definitions

| Term | Meaning | Level |
|---|---|---|
| **TAM** (total addressable market) | Everyone who could be interested in the product or service. The whole potential market, independent of your ability to reach or serve it. | Market |
| **SAM** (serviceable addressable market) | The part of the TAM you can reach and serve with your business model, geography, channels and product fit. | Market |
| **SOM** (serviceable obtainable market) | The share of the SAM you can realistically capture in a given period, given your capacity and competition. | Market |
| **ICP** (ideal customer profile) | Granular, checkable details about the *businesses* most worth targeting. | Company |
| **Persona** | A semi-fictional profile of an ideal customer, built from real data, research and insight. | Person |
| **Target market** | The broad group of organisations the client could serve. The ICP is the narrower slice where the client wins most, keeps customers longest and serves them most profitably, right now, because those customers value what the client does better than their alternatives. | Market |
| **Firmographic data** | Characteristics that group companies into segments: industry, size, location, revenue and similar. | Company |

Relationship: TAM contains SAM, which contains SOM. The ICP defines *which companies count* in all three. The persona describes the *people* inside those companies.

---

## ICP categories

Core five (always fill):

1. **Company size**: employees, and where useful team size of the relevant department
2. **Geography / location**
3. **Industry / vertical**: be specific (not "healthcare" but "private dental clinics with 3 to 15 chairs")
4. **Presence of specific roles**: for example a head of operations, an in-house marketing team, a compliance officer. A role's presence often tells you more than industry.
5. **Revenue range**

Extended (fill where evidence exists):

- Business model or stage (subscription, project-based, venture-backed, family-owned)
- Technology or operational characteristics (tools they use, processes they run)
- What they use today, and the value they get only from the client (Step 4, `why-they-buy.md`)
- Pain points, ranked, each tied to evidence, and the public data that would show each from outside
- Trigger events (new funding, new regulation, a new hire, rapid growth, a failed incumbent)
- **Disqualifiers** (what rules a company out)

Quality test for every criterion: can you check a company against it with a yes or no, using information you can actually find? If not, rewrite it.

Persona attributes (separate from the ICP): job title and variants, seniority, goals, pains in their own words, objections, how they evaluate, what triggers them to look, where they get information.

---

## TAM: bottom-up (primary)

Written for B2B. For consumer and local clients, replace "companies" with "target consumers" and ACV with annual spend per consumer (see `client-types.md`).

Start from real customers.

1. Take the current best-fit customers (the ICP).
2. Count how many companies in the target market resemble them (match the ICP criteria). This is the **total number of companies**.
3. Multiply by the **annual contract value (ACV)**.

```
TAM (bottom-up) = number of ICP-fit companies x ACV
```

Notes:
- Use the ACV real customers pay, not list price or the biggest deal.
- If the client has several price tiers, size each tier separately and add them, or use the weighted average ACV and say so.
- If the offer is usage-based or has expansion revenue, state whether TAM is first-year or lifetime.
- **Counted or derived?** A true bottom-up count comes from a list you can open: a register, a directory, a database search. Multiplying a national total by a guessed share (17,000 companies x 15%) gives a *derived* count. It can still be useful, but label it `count_basis: derived`: it is really a top-down number in disguise.
- **Not all counted sources are equal.** Record the source type (`count_source_type`: register, directory, maps, aggregator or other) and your estimate of its coverage (`count_coverage_pct`, with its basis in `count_source`). A government or regulator register is usually the strongest, because the data is kept by law; an aggregator search (a B2B database) is directional only. Where one source alone is thin, combine sources and remove duplicates. The script flags an aggregator-only count.
- **Source every input.** Give `acv_source`, a `source` on each SAM filter, on the top-down figure and on the SOM basis (or a `source` inside a range). The script prints an "Unsourced inputs" list; each item on it is an `[Assumption]` in the brief.

---

## TAM: top-down (sanity check)

Start from the whole market.

1. Find the **total size of the overall market** for the product or service category.
2. Take the **portion relevant to your business** (the part your offer actually addresses).
3. Cut into **subsegments** (for example geography, company size band).

```
TAM (top-down) = market size x relevance % x subsegment %
```

Top-down numbers come from third-party reports and are usually less precise. Always record the source, year and definition of the market it measures.

---

## Triangulating the two

Compare the two TAMs.

- Within about 3x of each other: reasonable. Report both and say which you trust more and why.
- More than 3x apart: one input is wrong or the two methods measure different things. Find out which (company count? ACV? relevance %?) before presenting either number. `scripts/tam_calc.py` flags this.
- A top-down figure that is much *larger* than bottom-up often means the market definition is too broad. A bottom-up figure much larger usually means the company count is inflated or ACV is optimistic.
- **Agreement is only evidence when the methods are independent.** If the bottom-up count is derived, or both methods lean on the same assumption, a close match proves little. Say so instead of presenting it as confirmation. The script flags this.

---

## SAM

Apply realistic filters to the TAM, one after another. Typical filters:

- Geography the client can actually serve
- Languages and regulations
- Channels you can use to reach them (for example phone, email, events)
- Company types the product cannot serve or the client will not serve
- Price-point fit (can they afford the ACV?)
- Companies already locked into a competitor

Show the funnel step by step so the user can see which filter removes the most. Every filter percentage needs a source or an `[Assumption]` label.

**Reachable contacts.** Multiply the SAM companies by the number of roles to reach at each (from Pack 1) to get the number of people outreach can actually go to (`contacts_per_company` in `scripts/tam_calc.py`). Report it beside the SAM. A small pool cannot be emailed hard or for long, so follow-ups have to be fewer and slower; the outbound hand-off sets the actual pace.

```
SAM = TAM companies x filter 1 x filter 2 ... x ACV
```

---

## SOM

The share of the SAM obtainable in a stated period (default: first 12 months). Two approaches; use the first when possible.

**Capacity-based**

```
deals per year = reps x meetings per rep per month x 12 x close rate
SOM = deals per year x ACV
```

**Share-based** (when capacity data is missing)

```
SOM = SAM x realistic share %
```

**Capacity cap.** SOM can never exceed what the client can actually deliver and sell:

```
SOM = the smaller of (deals the sales funnel can produce, deals the sales team can close, deals delivery can serve) x ACV
```

In `scripts/tam_calc.py`, add `"delivery": {"max_clients": n}` (or `hours_available_per_year` and `hours_per_client_per_year`) and `existing_clients` to the `som` block. The script takes the smaller of the sales figure and the delivery cap and says which one binds. Give exactly one sales basis (deals per year, capacity or share); the script stops if you give more than one.

**Back-solving from a revenue target.** To see what a goal requires:

```
customers needed = target new revenue / ACV
qualified opportunities needed = customers needed / win rate
leads needed = qualified opportunities / (lead-to-opportunity rate)
salespeople needed = customers needed / (deals per person per year x attainment)
```

Use the client's own conversion rates. If they have none, mark every rate `[Assumption]`. Do not import conversion benchmarks from US software reports for other markets or business types.

Sanity checks: a year-1 SOM above about 10% of the SAM is aggressive; deals per year can never exceed the number of SAM companies. Consider the sales cycle: deals started this year may close next year.

---

## Where to find the numbers

For company counts (bottom-up):
- National company registers and regulator registers (licensed sectors are the easiest to count)
- Trade associations and industry directories
- Maps and business listings (useful for local businesses, and where databases are thin)
- Government or statistics-office business counts
- B2B database or search counts (for example LinkedIn or Clay-style searches). **Treat these as directional and sample-check 20 to 30 records** for accuracy and coverage before trusting them, especially outside the US and Europe, where coverage is often overstated.

For market size (top-down):
- Industry reports, trade body publications, public company filings, development-bank or government sector reports

Always record: figure, source, date, and what exactly it measures.

---

## Common mistakes

- **Calling the whole industry's revenue the TAM** when the offer serves only a slice of it
- **Counting companies that cannot afford the ACV** or lack the role that buys
- **Using global figures when the serviceable market is one country or city**
- **Mixing units** (companies in one place, revenue in another, different currencies or years)
- **Double-counting** companies that appear in two segments
- **Presenting a precise number from imprecise inputs.** Round, give a range, and name the weakest input.
- **Treating SOM as a target** instead of an estimate from capacity

---

## Segmented sizing

When the client has distinct segments or price tiers, size each one separately and add them up. Use the `segments` list in `scripts/tam_calc.py`.

```
Segment TAM = ICP count x ACV
Segment SAM = reachable count (after filters) x ACV
Total = sum of segments
```

Do not blend segments with very different ACVs into one average.

Each segment takes its own `count_basis` and `som` (or the shorthand `deals_per_year`). A segment with no SOM inputs is left out of the total SOM, and the script says so. A top-level `top_down` is compared with the total bottom-up TAM.

---

## Ranges and sensitivity

Any number in the input file can be written as `{"low": a, "base": b, "high": c}`. Write "low" as the value that gives the *smaller* market (for hours per client, that is the larger number of hours). The script then reports:

- a low / base / high scenario, with every ranged input at that value at once
- a sensitivity table: each ranged input moved on its own, the others at base, sorted by how much it moves SAM, with SOM alongside

The top row of the sensitivity table is the input to name in the brief's sensitivity note. See `examples/sizing-ranges.json`.

---

## Worked example (illustrative only)

All numbers here are made up to show the mechanics. They are not real market data.

A client sells scheduling software to private dental clinics at USD 4,800 per year.

**Bottom-up TAM:** 3,200 clinics fit the ICP x USD 4,800 = **USD 15.36M**

**Top-down TAM:** USD 400M regional practice-management software spend x 20% relevant to scheduling x 30% in the target geography = **USD 24M**

**Triangulation:** 24 / 15.36 = 1.56x apart. Acceptable. Bottom-up is preferred, since it rests on a counted list.

**SAM:** 3,200 x 60% (in the three cities served) x 70% (reachable by phone and with a web presence) = 1,344 clinics x USD 4,800 = **USD 6.45M**

**SOM (year 1):** 1 rep x 10 meetings per month x 12 x 20% close rate = 24 deals x USD 4,800 = **USD 115,200**, which is about 1.8% of SAM clinics.

Run it with: `python scripts/tam_calc.py examples/sizing-single.json`
