---
name: lead-sources
description: Reads an ICP handoff file (icp-handoff.json from icp-tam-builder) and finds where the target companies, their buying signals and their decision-makers can actually be found for that market, then writes a sources plan. For each source it gives what it lists, how much of the market it covers, how fresh it is, what it costs or requires, and a 20 to 30 record sample check. Searches every source type on a checklist (registers, regulators, associations, directories, databases, job boards, app stores, review sites, maps, communities) with a logged method that stops only when two rounds find nothing new, using Exa as well when it is connected. Use when the user has a finished or draft ICP and asks where to find the leads, which lead sources or databases to use, where to get a list of a type of company, how to build the raw market list, or "what's the next step after the ICP", even without saying "lead sources". Not for building the ICP itself (icp-tam-builder), writing Apollo, Prospeo or Clay searches (the search-query skill), or pulling and scoring the full list (the list builder).
---

# Lead sources

**Bottom line:** this skill answers one question: *where can we find these companies, their signals and their people, and how much can we trust each place?* It reads the ICP handoff file, searches every source type for the market, checks a sample from each good source, and writes a sources plan the next skills work from. It does not build the ICP, write tool searches, or pull the full list.

## Where it sits

1. **icp-tam-builder:** who to target, and how big the market is. Writes `icp-handoff.json`.
2. **lead-sources (this skill):** where to find them. Writes `sources-plan.md` and `sources.json`.

**File names follow the client folder.** The names in these steps are the plain ones. If the client folder already names its files after the client (for example `exampleco-icp-handoff.json`, which icp-tam-builder writes when it follows the user's layout), write this skill's files the same way: `<client>-sources-plan.md`, `<client>-sources.json`, `<client>-search-log.csv` and a `<client>-samples/` folder. Use those names wherever the files point to each other (`built_from.handoff`, each `sample.file`, `search.log`) and in the commands in Step 6. Say the names in one line in the reply.
3. **search-query:** turns the ICP and the database sources into search links (Apollo and Prospeo; Clay through Clay's own clay-search-query).
4. **List builder** (planned): pulls, cleans, scores and checks the full list.

**Stay in scope.** The only records this skill pulls are the 20 to 30 per source for the sample check. It names a database and the filters worth trying, but never writes a search link or query for a tool: that is the search-query skill's job, from each tool's current documentation.

## Files

| File | Read it when |
|---|---|
| `references/research-method.md` | Before any searching. The routine every search follows |
| `references/source-types.md` | Step 2. The checklists of source types |
| `references/sources-format.md` | Steps 4 to 6. What to record per source, the sample check, and the output files |
| `scripts/check_sources.py` | Step 6. Checks `sources.json` before delivery |

## Step 0. Read the handoff file

1. Find the handoff file in the client folder: `icp-handoff.json`, or `<client>-icp-handoff.json` where the folder names files after the client. If there is more than one, use the newest and say which. Ask for it only if there is none. If the user has no handoff file, say this skill needs one and offer to run icp-tam-builder first. If they insist, work from whatever ICP they give, and label every output "No handoff file: ICP not checked".
2. Check it. If icp-tam-builder is installed next to this skill, run `python ../icp-tam-builder/scripts/check_handoff.py <file>`. If it reports errors, stop and list them: a later skill would misread the file. Otherwise, read the file and confirm by hand that it has `client`, `tiers` (with T1 filters), `signals`, `roles` and `market`.
3. Carry forward every warning. If `review.status` is `draft`, every output says "Draft: ICP not reviewed".
4. Say in three lines what you will search for: the Tier 1 entity types and places, the signals, and the roles. If the client type is `local_consumer`, use the consumer checklist (`source-types.md`, B) and the handoff's `channels`.

## Step 1. Write the hit lines

One line per search job, before any searching (`research-method.md`, Step 1):

- **Market list:** one per Tier 1 entity type and place (for example, "a source that lists licensed microfinance banks in Nigeria, with the name and one more field").
- **Signals:** one per handoff signal, from its `where` field.
- **People:** where the champion's and the economic buyer's names and contact routes can be found (the role titles come from `roles`).
- **Tier 2:** one short line only, unless the user asks for Tier 2 now.

## Step 2. Search

Follow `research-method.md` with the right checklist from `source-types.md`, for each hit line: every source type marked, three phrasings or more, each source's own index opened, links followed, every tool used (Exa as well when connected), and two empty rounds before stopping. Log every search in `search-log.csv`.

Before a large run (more than about 60 searches, or any Exa `agent_run`), tell the user the expected size and any Exa cost first.

## Step 3. Open and assess each source

For every hit, open it and record the fields in `sources-format.md`: what it lists, the fields it holds, how many records, its date, access and cost, format, and the terms of use. Respect a site's terms: if it forbids automated collection, say so and mark the source for manual or licensed use. **Read the terms of use for every source ranked `start` or `add`**, because the list builder collects data from those: find the site's terms or legal page, and record what it says about reuse and automated collection. For signal and people sources, `unclear` is acceptable when no terms page is found quickly.

**Coverage.** Compare the source's record count with the handoff's market count (`market.companies` and its `count_basis`). Say "about 60% of the 785 counted", or "unknown: no market count" when there is none. Never guess a count.

## Step 4. Sample check the main sources

For each source the plan would start from (usually two to five), take 20 to 30 records, spread across the list (not just the first page), and check each against a second, independent source:

- Does the entity exist and still operate (licence active, website live, recent activity)?
- Does it fit the Tier 1 filters the source claims to cover?
- Are the fields it holds correct? (Fields it does not hold go in `fields_missing`, with the source that fills them; they are not sample failures.)

Record the results in `samples/<source-id>.csv` and the rates in `sources.json`. A source with an accuracy rate under 80% on the sample is flagged "use with care". A sample under 20 records (because the source is small or blocked) is reported with its size, never as a rate alone.

Sample records can include people's names. Keep them in the client folder; do not paste them into chat or send them to outside services.

## Step 5. Rank and write the plan

Rank the sources into:

1. **Start here:** the most complete, checkable list for each Tier 1 entity type (usually a register).
2. **Add:** sources that fill gaps the first one leaves (entity types or places it misses), with the overlap found in the sample.
3. **Signals:** one or more source per handoff signal, with how to read the date.
4. **People:** where to find names and contact routes for each role.
5. **Open by hand:** sources that blocked automated reading, with the link.
6. **Gaps:** entity types, places or signals with no source found, and what was searched.

Write `sources-plan.md` and `sources.json` in the formats in `sources-format.md`, and keep `search-log.csv` and `samples/` beside them.

## Step 6. Check before delivery

1. Run `python scripts/check_sources.py <sources file> --handoff <handoff file>`, for example `sources.json --handoff icp-handoff.json`, or `exampleco-sources.json --handoff exampleco-icp-handoff.json` in a folder that names files after the client. Fix every error.
2. Run the icp-tam-builder link checker on `sources-plan.md` and on every source URL in `sources.json`, if it is installed (`python ../icp-tam-builder/scripts/check_links.py <file>`). A source ranked `start`, `add`, `signal` or `people` whose link fails is opened once more; if it still fails, re-rank it `open_by_hand` (blocked or timed out) or `not_used` (gone), update the plan, and say so.
3. Check the report against `research-method.md`, Step 10: rounds, empty types, blocked sources, and what the method cannot see.

## Reply

Lead with the bottom line: where to start, how much of the market it covers, and how far to trust it. Then the ranked plan in short, the gaps, the warnings carried from the handoff, and the files written. Say plainly what was not searched (paid databases the user has not opened, private groups, pages behind logins).

## Handing off

`sources.json` (or `<client>-sources.json`) is what the search-query skill and the list builder read. The database entries name the database and the filters worth trying, in the ICP's words. The search-query skill turns them into each tool's filter values.
