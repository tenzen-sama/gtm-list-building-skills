# search-query

**Bottom line:** the third skill in the list-building chain. Describe who you want, or point it at a client's ICP handoff file, and you get Apollo and Prospeo links that open with the filters already set. A script writes every link, so nothing is mistyped or guessed, and it tells you which parts of your request it could not put in a link and why.

## How you use it

1. Ask, for example: "Build Apollo and Prospeo searches for CROs and VP Sales at US software companies with 100 to 5,000 staff", or "Turn the Example Co ICP into searches". Name one tool to get only that one.
2. You get: one link per search (base search, one per signal, one per region), what each contains, what was asked for but not applied (for example "Salesforce: needs Prospeo's Starter plan"), and what to check when you open each link.
3. Open each link while logged in. Check the filter chips and note the result count. If a count looks wrong, ask for a loosening ladder.
4. Teach it as you go:
   - **Apollo industry:** tick only that industry, copy the link, and paste it with the industry's name.
   - **Prospeo filter:** tell me which chips appeared on a Prospeo link, or paste a link you built in Prospeo with that filter. Each filter confirmed this way stops being flagged.

With a client folder, it saves the specs and links there: `apollo-spec.json`, `apollo-links.md`, `prospeo-spec.json`, `prospeo-links.md` (or the `<client>-` forms if the folder names files after the client).

It does not open either tool, export contacts or spend credits. Clay searches are a different skill (Clay's `clay-search-query`).

## The chain

1. icp-tam-builder: who to target and how big the market is.
2. lead-sources: where the companies are listed.
3. **search-query:** the searches to run (Apollo and Prospeo).
4. List builder (planned): pull, clean, score and check the list.

## How sure the links are

- **Apollo:** every link part has been seen in your own working links. Some industry codes are only probable (below).
- **Prospeo:** only the job title filter has been seen in your own links. The other ten filters come from Prospeo's official documentation and are flagged on every link until you confirm them. Industry, seniority, department and headcount-band values are checked against Prospeo's own lists, so a misspelling stops the build instead of producing a link that quietly ignores it.

## Files

| File | What it is |
|---|---|
| `SKILL.md` | The steps |
| `references/apollo-parameters.md` | Apollo: verified link parameters, filters locked on your plan, the Filters 2.0 check, how to add a parameter |
| `references/prospeo-parameters.md` | Prospeo: the link format, the filters and their limits, what is locked on your plan, how a filter becomes confirmed |
| `references/spec-format.md` | The search spec Claude writes for each tool, and the rules for writing it |
| `references/apollo-industries.json` | Apollo industry IDs, each marked confirmed, probable, unverified or conflict |
| `references/prospeo-values.json` | Prospeo's official lists: 256 industries, 10 seniorities, departments, 11 headcount bands (downloaded 22 Nov 2026) |
| `references/prospeo-keys.json` | Each Prospeo filter: seen, documented or locked, and the plan it needs |
| `scripts/apollo_links.py` | Builds Apollo links; reads, compares and learns from links you paste |
| `scripts/prospeo_links.py` | Builds Prospeo links; reads, compares and confirms filters from links you paste; looks up allowed values |
| `examples/apollo-spec.json`, `examples/prospeo-spec.json` | Your request from the 17 Nov 2026 chat, written for each tool |
| `tests/run_tests.py` | Tests, including rebuilding your real Apollo and Prospeo links |

## Apollo industry IDs

Apollo filters industries by ID, not by name. As of 22 November 2026:

- **Confirmed (2):** Construction and Real Estate, from your single-industry links.
- **Probable (4):** Computer Software, Information Technology & Services, Computer & Network Security, Computer Hardware. These are in your people-search links, and an outside list names them the same way.
- **Unverified (22):** from walutani1/apollo-url-builder's seed list (MIT licence). Usable, with a warning to check the chip.
- **Conflict (2):** Animation and Industrial Automation share one ID in that list, so neither is used until one is confirmed.

Prospeo filters industries by name, from its own list of 256, so it needs no IDs.

## Versions

- **v0.2 (22 November 2026):** Prospeo added. People search, eleven filters (title seen in your links; ten from Prospeo's filters documentation, each flagged until confirmed). Values checked against Prospeo's official lists. Paid filters reported with the plan they need. A search that comes out identical to another, because its signal is locked, is flagged. 48 tests, including rebuilding both captured Prospeo links character for character.
- **v0.1 (22 November 2026):** first version, Apollo only. Built from the 17 Nov 2026 chat about Apollo and Prospeo links, the user's captured links, and the user's single-industry links of 22 Nov. Seven verified filters (titles, person and company location, headcount, industry, keywords, time in current role) on the people page, and industry on the companies page. Script tests rebuild all five captured Apollo links.

## Known limits

- **Built on your Free plans.** Apollo: technologies, job postings, funding and department headcount are locked. Prospeo: technologies, job postings, funding and revenue need Starter; job change needs Growth. Those parts of a request are reported, not applied.
- **Prospeo filters beyond job title aren't confirmed in your account yet.** The first Prospeo link you open settles most of them.
- **Prospeo place names must be Prospeo's own wording.** "United States" and "United Kingdom" are the expected forms, but only Prospeo's suggestions are authoritative.
- **No Prospeo company search, and no Apollo exclusions,** because no such link has been captured.
- **Both tools can change their links.** Apollo's "Filters 2.0" stops links carrying filters; Prospeo could change its encoding. The skill checks every link you paste for both.
- **Not tried on a live request yet.** The scripts reproduce your captured links, but the full skill (request to spec to links) hasn't been run on a new request.
- **Learned industries and confirmed filters land in the installed copy.** `learn-industry` and `confirm-key` write to the installed skill's files; sync them to this repo (the 12-hour auto-save backs up the installed copy either way).
