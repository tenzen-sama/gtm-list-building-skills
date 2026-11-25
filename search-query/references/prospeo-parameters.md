# Prospeo links: what can go in one

**Bottom line:** a Prospeo people-search link is the whole filter set, written as compact JSON and then base64url-encoded (no padding), after `https://app.prospeo.io/search/people/`. Only the job title filter has been seen in a link from the user's own account. The rest come from Prospeo's official filters documentation. The script writes them and flags each one until the user confirms it.

## Sources

- **The user's two captured links** (17 Nov 2026). Both contain only `person_job_title`. The tests rebuild both character for character.
- **Prospeo's filters documentation:** https://prospeo.io/api-docs/filters-documentation (page last updated 5 Aug 2026; read 22 Nov 2026). Keys, field names and limits below are from it.
- **Prospeo's value lists:** https://prospeo.io/api-docs/enum/industries, `/seniorities`, `/departments`, `/employee-ranges` (downloaded 22 Nov 2026 into `prospeo-values.json`: 256 industries, 10 seniorities, 14 departments with their sub-departments, 11 headcount bands).
- **Why the documented keys should work in a link:** Prospeo's search-person API page says the dashboard's "..." menu > "Search API" shows the payload for the search on screen, and the user's captured links decode to that same format. That the dashboard accepts every documented key from a link is **inference**, which is why each carries a check.
- **The earlier chat's evidence:** its US link, built from documented keys, gave the user 531 contacts. Nobody checked which chips appeared, so it doesn't prove any single key.

## Filters the script writes

| Spec key | Prospeo key | Format and limits | Status |
|---|---|---|---|
| `titles`, `exclude_titles`, `title_match`, `similar_intensity` | `person_job_title` | `include`, `exclude` (100 each, 2 to 100 characters), `match_mode` CONTAINS (default), EXACT or SIMILAR, `smart_intensity` LOOSE (default), NORMAL or STRICT. Written lowercase, as in the user's links | Seen |
| `person_locations`, `exclude_person_locations` | `person_location_search` | `include` / `exclude`, up to 100. Must be Prospeo's own suggestion wording | Documented |
| `company_locations`, `exclude_company_locations` | `company_location_search` | Same, for company HQ | Documented |
| `headcount` | `company_headcount_custom` | One `{min, max}`, 1 to 999,999 | Documented |
| `headcount_ranges` | `company_headcount_range` | Prospeo's 11 bands (1-10 ... 10000+). Not with `headcount` | Documented |
| `industries`, `exclude_industries` | `company_industry` | Names from Prospeo's 256-item list | Documented |
| `keywords`, `exclude_keywords`, `keywords_match_all` | `company_keywords` | Up to 20 each, 3 to 100 characters; exclusions need at least one include; searches all sources | Documented |
| `seniority`, `exclude_seniority` | `person_seniority` | Prospeo's 10 values; include or exclude, not both | Documented |
| `departments`, `exclude_departments` | `person_department` | Prospeo's departments (a top-level one includes its sub-departments); include or exclude, not both | Documented |
| `department_headcount` | `company_headcount_by_department` | Up to 10 of `{department, min, max}`; a missing end is written as null | Documented |
| `months_in_current_role` | `person_time_in_current_role` | `{min, max}` in months, 0 to 600 | Documented |

Prospeo rejects a search made only of exclusions, so the script does too.

## Locked on the user's plan (Free)

From the "Minimum plan" lines in the filters documentation (verified 22 Nov 2026). These go in the spec's not-applied keys and are reported, never written:

| Spec key | Prospeo key | Plan needed |
|---|---|---|
| `technologies`, `exclude_technologies` | `company_technology` | Starter |
| `job_postings` | `company_job_posting_hiring_for` | Starter |
| `funding` | `company_funding` | Starter |
| `revenue` | `company_revenue` | Starter |
| `job_change` | `person_job_change` | Growth |
| `key_exec_changes` | `company_key_execs` | Pro |

Also reported, not written: `buying_intent` (Free includes 3 intent topics, but the script doesn't write that filter yet) and `exclude_companies`.

**Inference:** the ten documented filters above are usable on Free. The documentation gives a minimum plan only for restricted filters and none for these, and the Help Center's premium-filters table (`tool-docs/prospeo-filters.md`) doesn't list them. Neither says outright that they are free.

## Not supported yet

- **Company search** (`app.prospeo.io/search/company/...` is likely, but no company link has been captured).
- Filters not in the table, for example company type, founded year, headcount growth, NAICS and SIC codes. `parse` names them if they appear in a pasted link.

## Making a filter "seen"

1. The user builds a search in the Prospeo dashboard with that filter, and copies the link (or opens one of this skill's links and reports that the chip appeared).
2. Run `python scripts/prospeo_links.py confirm-key <prospeo_key> "<link>"`. It checks that the key is in the link, marks it seen, and stores the value it saw.
3. If the dashboard's link writes the filter differently from the script (field names, order, letter case), `compare` the two links, change `build_one` in `prospeo_links.py` to match the dashboard, add a test that rebuilds the dashboard link exactly, and sync the master and installed copies.

## Refreshing the value lists

Prospeo can add or rename values. To refresh, download the four enum pages again and rebuild `prospeo-values.json` the same way (one value per line in the page's code block; departments are indented under their parent). Don't edit the file by hand.
