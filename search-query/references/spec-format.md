# The search spec

**Bottom line:** the spec is the one thing the model writes. It says what to search for in plain fields; `scripts/apollo_links.py build` or `scripts/prospeo_links.py build` turns it into links. Write one spec per tool, because the tools name industries, places and time in role differently. Keep the specs per job, so the searches can be rebuilt or changed later without starting again.

**Running example:** `examples/apollo-spec.json` and `examples/prospeo-spec.json`, the user's own request from their 17 Nov 2026 chat, written for each tool.

## Shape (both tools)

```json
{
  "spec_version": "1",
  "tool": "apollo or prospeo",
  "name": "What these searches are for, in one line",
  "built_from": "Where the request came from: a plain-language request, or the handoff file's name",
  "base": { "...filters every search shares..." },
  "searches": [
    {"name": "US base", "set": {"...filters added or replaced..."}},
    {"name": "US, without keywords", "drop": ["keywords"]}
  ]
}
```

Each search starts from `base`, removes the keys in `drop`, then applies `set`. With no `searches`, `base` is built as one search. `tool` is a label for people reading the file; the script you run decides the tool.

## Apollo filter keys

| Key | Value | Notes |
|---|---|---|
| `page_type` | `"people"` (default) or `"companies"` | Companies search allows no person filters |
| `titles` | list of job titles | Champion's titles first. Include the common spellings Apollo users have ("vice president of sales" as well as "vp of sales") |
| `person_locations` | list of places | Where the person is. Lowercase, for example "united states" |
| `company_locations` | list of places | Company HQ |
| `headcount` | list of `{"min": 100, "max": 5000}` | Both ends required |
| `industries` | list of industry names from `apollo-industries.json` | Use `industries` to see names; aliases work. Never put an ID here |
| `keywords` | list of company keywords | Matched on any. Add close variants ("cyber security", "cybersecurity") |
| `days_in_current_role` | `{"min": 0, "max": 90}` | Days. The free stand-in for "new in the job"; it also catches internal promotions |
| `sort` | `"recommendations_score"` (default) or `"[none]"` | |
| `page` | number | Default 1 |
| `technologies`, `job_postings`, `funding`, `department_headcount`, `revenue`, `buying_intent`, `seniority`, `job_change`, `exclude_*` | anything | Recorded and reported as "not applied" with the reason. Put the user's wish here rather than dropping it, so the report shows it |

## Prospeo filter keys

People search only. Limits are in `prospeo-parameters.md`.

| Key | Value | Notes |
|---|---|---|
| `titles`, `exclude_titles` | lists of job titles | `exclude_titles` needs at least one title included |
| `title_match` | `"contains"` (default), `"exact"` or `"similar"` | "similar" also finds related titles ("CEO" finds "Chief Executive Officer") |
| `similar_intensity` | `"loose"` (default), `"normal"`, `"strict"` | Only matters with "similar" |
| `person_locations`, `company_locations` (and `exclude_` forms) | lists of places | Prospeo's own wording, for example "United States" |
| `headcount` | `[{"min": 100, "max": 5000}]` | One custom range |
| `headcount_ranges` | list of Prospeo bands, for example `["101-200", "201-500"]` | Instead of `headcount`, not with it |
| `industries`, `exclude_industries` | Prospeo industry names | Check with `values industries <text>`. Apollo's names don't work here |
| `keywords`, `exclude_keywords` | lists, 20 at most | `keywords_match_all: true` makes them AND instead of OR |
| `seniority` or `exclude_seniority` | Prospeo's values (C-Suite, Vice President, Head, Director, Manager...) | One or the other |
| `departments` or `exclude_departments` | Prospeo's departments, for example "Sales" or "Revenue Operations" | One or the other |
| `department_headcount` | `[{"department": "Sales", "min": 20}]` | Free on Prospeo (locked on Apollo's Free plan) |
| `months_in_current_role` | `{"min": 0, "max": 3}` | Months, not days |
| `technologies`, `exclude_technologies`, `job_postings`, `funding`, `revenue`, `job_change`, `key_exec_changes`, `buying_intent`, `exclude_companies` | anything | Reported as not applied, with the plan it needs |

Any other key is an error in either tool, which catches typos. Using `days_in_current_role` in a Prospeo spec is an error that points to `months_in_current_role`.

## Rules for writing it

1. **One search per signal.** Filters combine with AND, so a search that needs every signal finds almost nobody. Build the base search, then one search per signal the tool can express, and rank companies later by how many searches they appear in.
2. **One search per region when the user wants a split.** Neither tool has a ratio filter: "US 70%, UK 30%" is two searches, and the split is applied when the lists are pulled.
3. **Ask before broad titles.** Bare functional terms ("revenue operations", "sales operations") also pull in analysts and coordinators. Use VP, Head, Director or Manager forms unless the user agrees. In Prospeo, "contains" matching already widens a title ("vice president of sales" also finds "vice president of sales operations").
4. **Nothing silently dropped.** Every part of the request either becomes a filter or goes in a not-applied key, or is named in the reply as something the tool can't express (for example "board pressure").
5. **From a handoff file:** titles from `roles` (champion first, then economic buyer if the user wants both), industries, places and headcount from the Tier 1 `filters`, signals from `signals` (one search each where expressible), exclusions from `disqualifiers`. In Apollo they are reported as not applied until an exclusion parameter is captured; in Prospeo, industry, place, title, keyword, seniority and department exclusions can be written. Tier 2 gets its own searches only when the user asks.
6. **The same request in both tools:** keep the titles, keywords and searches the same, and translate only what the tools name differently (industries, place wording, days or months). Then the two tools' counts can be compared.
