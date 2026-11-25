---
name: search-query
description: Turns a plain-language list request, an ICP handoff file (icp-handoff.json from icp-tam-builder) or a sources plan into Apollo and Prospeo search links the user pastes into their browser, with the filters already set. Scripts build every link from a structured spec. Apollo links use only parameters seen in the user's own Apollo links; Prospeo links use Prospeo's documented filter keys and exact allowed values, each flagged until seen in the user's account. Every filter that can't be applied (paid-plan filters, exclusions) is reported, not guessed. Splits signals and regions into separate searches, maps industries to each tool's names or IDs, checks links the user pastes back, and learns from them. Use when the user asks for an Apollo or Prospeo search, link or URL, "build this list in Apollo/Prospeo", "turn this ICP into searches", wants to find contacts or companies in Apollo or Prospeo from a description, pastes an Apollo or Prospeo link to check or learn from, or asks "what's the next step after lead sources", even without saying "search query". Not for Clay searches (use clay-search-query), building the ICP (icp-tam-builder), finding where the companies are listed (lead-sources), or pulling and scoring the full list.
---

# Search query (Apollo and Prospeo)

**Bottom line:** the user describes who they want, and gets back Apollo and Prospeo links that open with the filters set. The model writes a spec per tool; `scripts/apollo_links.py` and `scripts/prospeo_links.py` write every link. The model never types a link itself. One wrong character breaks an Apollo link, and a Prospeo link is encoded text no one can check by eye. Both tools may ignore a wrong filter without saying so, so a hand-made search can look right and isn't.

## Where it sits

1. **icp-tam-builder:** who to target. Writes `icp-handoff.json`.
2. **lead-sources:** where the companies are listed. Writes `sources-plan.md` and `sources.json`.
3. **search-query (this skill):** the searches to run in each tool.
4. **List builder** (planned): pulls, cleans, scores and checks the list.

**Stay in scope.** This skill builds links. It doesn't open either tool, log in, export or reveal contacts, or spend credits. The user opens the links themselves.

## How sure each tool's links are

- **Apollo:** every parameter has been seen in a working link from the user's own account. The uncertain part is some industry IDs (marked probable or unverified).
- **Prospeo:** only the job title filter has been seen in the user's own links. The other filters come from Prospeo's official filters documentation, which says its dashboard uses the same filter set. Each one stays flagged "not yet seen in your account" until the user confirms it (Step 4). Industry, seniority, department and headcount-band values are checked against Prospeo's official lists, so a misspelled value never reaches a link.

## Files

| File | Read it when |
|---|---|
| `references/apollo-parameters.md` | Before writing an Apollo spec: what can go in a link, the user's plan, the Filters 2.0 check |
| `references/prospeo-parameters.md` | Before writing a Prospeo spec: the filters, their limits, what is locked on the user's plan, how a filter becomes "seen" |
| `references/spec-format.md` | Writing either spec: keys, the base-and-searches shape, the rules |
| `references/apollo-industries.json` | Through `apollo_links.py industries`, to pick industry names |
| `references/prospeo-values.json` | Through `prospeo_links.py values <list> [text]`: Prospeo's allowed industries, seniorities, departments and headcount bands |
| `references/prospeo-keys.json` | Status of each Prospeo filter: seen, documented or locked, with the plan it needs |
| `scripts/apollo_links.py` | Apollo: `build`, `parse`, `compare`, `learn-industry`, `industries` |
| `scripts/prospeo_links.py` | Prospeo: `build`, `parse`, `compare`, `confirm-key`, `values` |
| `examples/apollo-spec.json`, `examples/prospeo-spec.json` | The user's own request from 17 Nov 2026, written for each tool |

All commands run from this skill's folder, for example `python scripts/prospeo_links.py values industries software`.

## Step 0. Find the input

- **A plain-language request** in the conversation: use it as written.
- **A client folder:** look for the handoff file, `icp-handoff.json` or `<client>-icp-handoff.json` where the folder names files after the client, and the sources plan's data file (`sources.json` or `<client>-sources.json`). Its database entries' `filters_to_try` say what to search for in the ICP's words. Read both if present.
- **A pasted Apollo or Prospeo link:** run that tool's `parse` first (see Step 4).

**Which tool.** Build for the tool the user names. If they name none, build both: both are on the user's Free plans and are separate databases, so the results can differ, and comparing the two counts is useful.

If the request is unclear on who (titles), what kind of company, or where, ask up to three questions, each with a default, in one message. Otherwise go ahead.

## Step 1. Write the spec

Follow `references/spec-format.md`. Write one spec per tool, because the tools name things differently:

- **Industries:** Apollo names from `apollo_links.py industries`; Prospeo names from `prospeo_links.py values industries <text>` (for example Apollo's "Computer Software" is Prospeo's "Software Development"). If an Apollo industry isn't in the list, don't guess: ask for a single-industry link (Step 4). If a Prospeo name is wrong, the build stops and names the closest values.
- **Time in role:** Apollo counts days, Prospeo months (`days_in_current_role` and `months_in_current_role`).
- **Places:** Apollo wants lowercase ("united states"); Prospeo wants its own suggestion wording ("United States").
- Titles: champion first, with the common spellings. Ask before bare functional terms that pull in junior roles.
- One search per signal the tool can express, and one per region when the user wants a split. Signals the tool can't express on the user's plan go in their not-applied keys, so they show in the report.
- Keep the user's wording in `name` and `built_from`.

Save the specs in the client folder when there is one: `apollo-spec.json` and `prospeo-spec.json`, or `<client>-apollo-spec.json` and `<client>-prospeo-spec.json` where the folder names files after the client. Otherwise keep them in the working folder and say where.

## Step 2. Build

Run `python scripts/<tool>_links.py build <spec> --out <links file>`, with the links file named like the spec (`apollo-links.md`, `prospeo-links.md`, or the client-prefixed forms).

- **Errors** (exit code 1) stop that search: an unknown key, a missing or disputed Apollo industry ID, a value not in Prospeo's lists, a limit broken (for example more than 20 Prospeo keywords), or a search with no filters or only exclusions. Fix the spec and rebuild. Never edit a link by hand to get round an error.
- **Warnings** don't stop it. They are things the user checks when opening the link: probable industry IDs, place wording, Prospeo filters not yet seen in the user's account, and a search that came out identical to another because its distinguishing filter is locked. Carry every one into the reply.

## Step 3. Reply

Lead with the links, grouped by tool, each with one line on what it finds. Then:

1. **What each link contains:** from the build output.
2. **Asked for but not applied:** every item and its reason. Say what would make it possible (for example "Prospeo's Starter plan") and where else the signal can be found, if the lead-sources plan names a source. Note when the same signal works in one tool and not the other (for example "20+ sales staff" is locked in Apollo but applied in Prospeo).
3. **What to check:** open each link; check the filter chips match; note the result count. Name the warnings to look at. Leave out any search the build marked as identical to another, and say why.
4. **If the count is too small or too large:** offer a loosening ladder, which is the same search with one filter dropped at a time (`drop`), so the counts show which filter cuts most.

Keep test machinery out of the reply. If the client folder has a changelog, add one line.

## Step 4. Links the user pastes

**Apollo**

- **Check a link:** `parse` shows the filters it holds, the industry name for each ID, and any parameter the skill doesn't know.
- **Filters 2.0 check:** if `parse` finds no readable filters in a link the user built with filters, stop and say so: the account may be on Apollo's "Filters 2.0", where links no longer hold the filters, and this skill can't build links for it.
- **Learn an industry:** from a link with exactly one industry ticked, run `learn-industry "<link>" "<Industry name>"`. It records the ID as confirmed, and marks any other industry that listed the same ID as disputed. It refuses a link with more than one industry, because the match wouldn't be certain.
- **A new filter:** `parse` lists it under unrecognised parameters. Adding it is a change to the skill: follow "Adding a parameter" in `references/apollo-parameters.md`.

**Prospeo**

- **Check a link:** `parse` decodes it and shows each filter with its status (seen, documented, locked, or unknown to this skill).
- **Confirm a filter:** when the user reports that a filter's chip appeared, or pastes a link they built in the dashboard with that filter, run `confirm-key <prospeo_key> "<link>"`. It marks the filter seen, and its warning stops appearing. Best evidence: a link built in the dashboard, not one this skill built.
- **A missing chip:** the dashboard ignored or reworded that filter. Ask the user to set it in the dashboard and paste the link; `compare` it with the skill's link to see the difference, then fix the script (see `references/prospeo-parameters.md`).
- **Format check:** if `parse` can't decode a Prospeo link, stop and say so: Prospeo may have changed its link format.

**Both:** `compare "<a>" "<b>"` shows what differs between two links of the same tool.

`learn-industry` and `confirm-key` write to the installed copy's `references/` files. Tell the user to sync them to the repository copy (or do it, if asked).

## Rules

- Every link comes from a script. No link written by hand, from memory, or from a third-party list.
- Every requested filter is either applied or reported with its reason.
- Nothing presented as more certain than it is: Apollo IDs and Prospeo filters not yet seen in the user's account carry a check.
- Plain words in the reply. Say "locked on your Free plan", not "PLAN_REQUIRED".
