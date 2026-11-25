# Apollo link parameters: what is verified

**Bottom line:** an Apollo search is a link with the filters written into it. This skill only writes the parameters below, because each one has been seen in a working link from the user's own Apollo account. Anything else is reported as "not applied", never guessed: Apollo silently ignores a parameter it doesn't recognise, so a guessed one gives a link that looks right and searches wrong.


## Two search pages

| Page | Link starts | Use for |
|---|---|---|
| People | `https://app.apollo.io/#/people?` | Contacts: titles, people's locations, time in role, plus company filters |
| Companies | `https://app.apollo.io/#/companies?` | Accounts only. Person filters are not allowed here |

## Verified parameters

| Spec key | Parameter | Format | Seen on |
|---|---|---|---|
| `titles` | `personTitles[]` | one per title, written lowercase | people |
| `person_locations` | `personLocations[]` | lowercase place name | people |
| `company_locations` | `organizationLocations[]` | lowercase place name (company HQ) | people |
| `headcount` | `organizationNumEmployeesRanges[]` | `min,max`, encoded `100%2C5000` | people |
| `industries` | `organizationIndustryTagIds[]` | Apollo's 24-character ID, from `apollo-industries.json` | people, companies |
| `keywords` | `qOrganizationKeywordTags[]` | one per keyword, case kept; a company matches any of them | people |
| `days_in_current_role` | `personDaysInCurrentTitleRange[min]` and `[max]` | **days**; works on the Free plan | people |
| `sort` | `sortByField` | `recommendations_score` (default) or `[none]` | people, companies |
| (always) | `sortAscending=false`, `page=1`, `recommendationConfigId=score` | | people, companies |
| (companies page) | `includedOrganizationKeywordFields[]=tags` and `=name` | always present in company links | companies |

A company filter used on the companies page, but only seen on the people page (company location, headcount, keywords), is built with a warning to check its chip.

**Locations:** only `united states` has been seen in a working link. Any other place is built with a warning to check its chip. `united kingdom` is unconfirmed.

**Parameter order doesn't matter.** Apollo writes parameters in different orders in different links, so the script compares links as sets of parameters (`compare`).

## Not applied, and why

| Spec key | Reason |
|---|---|
| `technologies` | Locked on the user's Free plan; parameter not captured |
| `job_postings` | Locked on Free; parameter not captured |
| `funding` | Locked on Free; parameter not captured |
| `department_headcount` | Locked on Free (# of employees by department); parameter not captured |
| `revenue`, `buying_intent` | Plan filters in Apollo's article; parameter not captured |
| `seniority` | Management level isn't available as a filter on the user's plan; use titles |
| `job_change` | Only finds contacts who changed jobs since you saved them; use `days_in_current_role` |
| `exclude_companies`, `exclude_titles`, `exclude_industries`, `exclude_keywords`, `exclude_technologies` | No exclusion parameter captured yet |

## The user's plan

Free, on both Apollo and Prospeo (user, 17 and 22 Nov 2026). If the user upgrades, a locked filter becomes usable only once its parameter is captured (see "Adding a parameter").

## Filters 2.0: the check that matters most

An outside project (walutani1/apollo-url-builder) says Apollo's "Filters 2.0" moves filters out of the link for some accounts, so a link points at a filter set stored on Apollo's side. The user's links from 17 to 22 November 2026 still carry their filters. Whenever the user pastes a new Apollo link, run `parse`: if it reports no readable filters, stop and tell the user. This skill can't build Apollo links for an account where that has happened.

## Adding a parameter

Only from a working link in the user's account, never from memory or a third-party list:

1. The user applies only the new filter in Apollo and copies the link.
2. Run `parse` on it. The new parameter shows under "unrecognised parameters".
3. Add it to the script (`APPLIED` and `KNOWN_PARAMS`) and to the table above, with the date and where it was seen, and add a test that rebuilds the captured link.
4. This changes the skill: update the repository copy and the installed copy together.
