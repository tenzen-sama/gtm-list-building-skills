# Client types

Clients differ in who pays and how they buy, and the ICP method has to change with them. Classify the client in Step 0, then apply the matching variant on top of the core workflow.

Contents:
- How to classify
- B2B software / SaaS
- B2B services / agencies
- Local business / consumer (B2C)
- Hybrids and two-sided businesses

---

## How to classify

Ask one question: **who pays?**

| Who pays | Type | Method |
|---|---|---|
| A business, for software | B2B software / SaaS | Firmographic ICP + tech fit |
| A business, for a service delivered by people | B2B services / agencies | Firmographic ICP built around one outcome and one vertical |
| An individual or household | Local business / consumer (B2C) | Demographic and behavioural persona + catchment area |
| Both, or one pays and another uses | Hybrid | Separate ICP per audience |

If the website does not make it obvious, ask the user. Never run the firmographic template on a consumer business.

---

## B2B software / SaaS

**Segmenting**
- Firmographics plus technology fit: tools they already use, integrations needed, team structure, growth stage
- Buying committee: champion or user, economic buyer, and a possible blocker (IT, security, procurement, finance)

**Trigger candidates to test** (in the look-back in `scoring-and-validation.md`, "Readiness scoring"; none is a default readiness rule)
- Funding rounds, rapid hiring in the relevant function, a new leader in the buyer's role
- Tool changes or contract renewals, new regulation, entry into a new market
- Job postings that name the incumbent tool

Keep a candidate only if it appears clearly more often before won deals than before lost ones, or if the evidence ties it to the pain from Step 4.

**Evidence emphasis**
- Logos and case studies, integrations and partner pages, review sites, job posts that name tools
- If the product is self-serve or trial-led, build the ICP from activation and retention data, not only signed deals

**Sizing**
- `companies x ACV`
- Seat-based pricing: `companies x average seats x price per seat`
- Tiered pricing: size each tier separately, then add

---

## B2B services / agencies

Examples: marketing agencies, consultancies, accounting, legal, development shops, training providers.

**Segmenting**
- Services are sold on trust and referral, so triggers are often invisible. Define the ICP around **one specific outcome in one vertical** where the client has proof. "We do marketing for everyone" is not an ICP.
- Still run Step 4 ("Why they buy", `why-they-buy.md`): name the real alternatives (an in-house hire, another agency, freelancers, doing nothing) and look for a pain visible from outside. If none can be found, call the segment a pain hypothesis in the brief rather than quietly falling back to the vertical.
- The buyer is often the founder or owner in small companies and a department head in larger ones

**Evidence emphasis**
- Case studies with measurable outcomes, testimonials with the speaker's title, referral sources and repeat or retainer clients in the CRM, typical project size
- Separate **who the client's network already knows** from **who the market actually contains**. The current client base often reflects referrals, not the best-fit segment. Flag referral dependency.

**Sizing**
- ACV = annualised retainer, or `average project value x projects per client per year`
- Cross-check against what companies of that size typically spend on this service

**Capacity check (important for SOM)**
- For services, delivery capacity usually limits growth before sales does
- `max clients = delivery hours available / hours per client per year`
- Cap SOM at this number even if sales capacity says higher. In `scripts/tam_calc.py`, add a `delivery` block to `som` and subtract clients already on the books with `existing_clients` (see `examples/sizing-services.json`)

---

## Local business / consumer (B2C)

Examples: restaurants, clinics, gyms, salons, retail, consumer brands.

**Segmenting**
- No firmographics. Use **demographics** (age band, income band, household type), **geography**, **behaviours and occasions** (when and why they buy), **needs and motivations**, and **media habits**.
- For a local business, geography dominates. Define the **catchment**: a radius or drive or walk time, or named neighbourhoods.
- Build one to three persona(s). The persona is the main output; the "ICP" is the description of the best customer group.
- Step 4 ("Why they buy") still applies, translated: alternatives are other local options, doing it at home, or going without; the pain visible from outside is about places and groups, never named people (competitors' reviews, new housing in the catchment); the first offer is often a trial or first visit. Details in `why-they-buy.md`.

**Evidence emphasis**
- Reviews (Google, social), comments and direct messages, POS or loyalty data, repeat rate, order value, surveys, and short conversations with regulars
- Call transcripts are often absent. Use the top-5 customer conversation kit with regulars, or in-store and chat conversations.

**Sizing**
- Bottom-up: `target consumers in catchment x annual spend per consumer` (visit frequency x average ticket)
- Top-down: local household spending on the category x relevant share x geography
- SAM: consumers inside the catchment who match the persona, can afford it and can be reached by channels the client uses
- SOM: usually **physical capacity** (seats, slots, covers per day x days open x realistic utilisation). In the script, enter it as `"delivery": {"max_clients": n}`, where n is the number of regular customers that capacity can serve in a year

**Using the output**
- Outbound lead lists rarely apply. Offer alternatives instead: ad audience definitions (location, age, interests), local partnerships, community and referral programmes, B2B tie-ins such as employers or schools.
- Be careful with individuals' personal data. Use aggregated patterns, not named people.

**Script mapping**
- In `scripts/tam_calc.py`, use `"customers"` instead of `"companies"` and `"annual_value"` instead of `"acv"`.

---

## Hybrids and two-sided businesses

- **Sells to businesses and consumers:** run a separate ICP and TAM per audience. Do not blend them.
- **One pays, another uses** (for example an employer buys, employees use): the payer is the ICP, and the user is a persona inside it.
- **Marketplace or platform:** size and profile each side separately, and note which side is the harder one to get first.
