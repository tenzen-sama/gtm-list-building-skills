# Sources format: what to record, and the output files

**Bottom line:** every source gets the same record, so sources can be compared and the next skill can read them. Three files come out: `sources-plan.md` for people, `sources.json` for the next skills, and `search-log.csv` with the `samples/` folder as the working record. Where the client folder names files after the client, each name takes the same prefix (`exampleco-sources.json`, `exampleco-samples/S1.csv`), and so do the file names recorded inside `sources.json`.

**Running example:** `examples/sources.json`, for the illustrative dental-clinic client in icp-tam-builder's examples. Its sources and figures are made up for the example, and its URLs end in `.test` so nobody mistakes them for real ones.

---

## What to record for each source

| Field | What it holds |
|---|---|
| `id` | Short and unique: `S1`, `S2` ... |
| `name` | The source's own name |
| `url` | The page you opened. Never a search link for a database tool |
| `source_type` | The row in `source-types.md` it belongs to |
| `jobs` | The hit-line ids it serves (Step 1) |
| `rank` | `start`, `add`, `signal`, `people`, `open_by_hand` or `not_used` (Step 5) |
| `lists` | What it lists, in one line |
| `fields` | The fields it holds (name, address, licence category, phone and so on) |
| `fields_missing` | Optional: fields the list builder needs that this source lacks, and which source fills each |
| `records` | How many records, if shown or countable; otherwise `null` with `records_note` |
| `coverage_pct` | Records against the handoff's market count, as a percentage; `null` if either is unknown, with `coverage_note` |
| `date` | Its own date as shown (published or last updated), or "no date shown" |
| `checked_on` | The date you opened it |
| `access` | `free`, `login`, `paid` or `blocked` |
| `cost_note` | The price or plan limit, with where it is stated |
| `format` | `html`, `pdf`, `csv`, `xlsx`, `api` or `search_only` (no list, only look-ups) |
| `terms` | `allowed`, `forbids_automated` or `unclear`, with `terms_note` saying where you looked |
| `reliability` | High, Medium or Low, with `reliability_reason` |
| `sample` | The sample check (below), or `null` if not sampled |
| `filters_to_try` | Databases only: the filters worth trying, in the ICP's words, not the tool's |

**Reliability scale:**

| Rating | Means |
|---|---|
| High | Official or self-maintained by the entities listed (a regulator's register, an association's own member list), dated, and the sample held up |
| Medium | Maintained by a third party with a stated method, or official but undated; the sample mostly held up |
| Low | Scraped or aggregated with no stated method, undated, or the sample found many errors |

## The sample check

For each source ranked `start` (and any `add` source the plan leans on), check 20 to 30 records spread across the list against a second, independent source.

`samples/<id>.csv`, one row per record checked:

| Column | What it holds |
|---|---|
| record | The name as the source gives it |
| position | Where in the list it came from (page or row), to show the spread |
| exists | yes, no or unclear: does it still exist and operate? |
| fits_tier1 | yes, no or unclear |
| fields_ok | yes, no or partly: are the fields this source holds correct for this record? (A names-only list whose names are right is yes.) |
| second_source | The URL or name of what you checked it against |
| note | Anything odd |

In `sources.json`, `sample` holds: `size`, `exists` (count of yes), `fits_tier1`, `fields_ok`, `second_source` (in one line), `file`. Rates are worked out by the script, not typed in.

Fields the list builder needs but the source does not hold (for example a state, a phone number or a licence category) are not sample failures. List them in the source's `fields_missing`, and say which other source fills them.

## sources.json

```
{
  "sources_version": "1",
  "client": {"name": "...", "client_type": "..."},
  "built_from": {"handoff": "icp-handoff.json", "date": "YYYY-MM-DD"},
  "review": {"status": "reviewed or draft, copied from the handoff"},
  "market_count": {"companies": 0, "count_basis": "copied from the handoff"},
  "hit_lines": [{"id": "H1", "job": "market | signal | people | tier2", "target": "...", "line": "..."}],
  "sources": [ { the fields above } ],
  "gaps": [{"job": "H3", "what": "...", "searched": "..."}],
  "search": {"rounds": 0, "searches": 0, "exa_calls": 0, "empty_rounds_at_end": 0, "log": "search-log.csv"},
  "cannot_see": ["paid databases not opened", "..."]
}
```

For a signal hit line, `target` is the signal's `name` exactly as in the handoff, so the script can check that every signal has a source or a gap.

## sources-plan.md

In this order:

1. **Bottom line:** where to start, how much of the market it covers, how far to trust it. The draft label if the handoff is a draft.
2. **Start here:** one short block per `start` source: what it lists, records and coverage, date, access, the sample result, and how to get the data out.
3. **Add:** each `add` source and the gap it fills.
4. **Signals:** a table with one row per handoff signal: source, how to read the date, reliability.
5. **People:** where each role's names and contact routes can be found.
6. **Open by hand:** the links, and why.
7. **Gaps:** what was searched and found nothing.
8. **How this was searched:** hit lines, rounds, searches, Exa calls, empty source types, what the method cannot see.
9. **Carry forward:** the handoff's warnings.

Edit `sources.json` first, then the plan, so the two never disagree.
