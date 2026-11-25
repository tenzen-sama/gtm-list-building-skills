# lead-sources

**Bottom line:** the second skill in the list-building chain. Give it a client's `icp-handoff.json` (from icp-tam-builder) and it tells you where the target companies, their buying signals and their decision-makers can be found, how much of the market each source covers, how far to trust it, and what a 20 to 30 record sample showed.

## How you use it

1. Finish the ICP with icp-tam-builder, so the client folder has `icp-handoff.json` (or `<client>-icp-handoff.json`, such as `exampleco-icp-handoff.json`).
2. Ask, for example: "Find the lead sources for Example Co" or "Where do we get the list for this ICP?"
3. You get, in the client folder: `sources-plan.md` (read this), `sources.json` (the next skill reads this), `search-log.csv` and a `samples/` folder. If your client folder names files after the client, these do too: `exampleco-sources-plan.md` and so on.

It does not build the ICP, write Apollo, Prospeo or Clay searches, or pull the full list. Those are the other skills in the chain.

## The chain

1. icp-tam-builder: who to target and how big the market is.
2. **lead-sources:** where to find them.
3. search-query: Apollo and Prospeo search links.
4. List builder (planned): pull, clean, score and check the list.

## Files

| File | What it is |
|---|---|
| `SKILL.md` | The steps |
| `references/research-method.md` | The search routine: hit line, checklist, phrasings, open each index, follow links, two empty rounds, search log |
| `references/source-types.md` | Checklists of source types: companies, local consumers, one person's own words |
| `references/sources-format.md` | What to record per source, the sample check, and the output files |
| `scripts/check_sources.py` | Checks `sources.json` (and against the handoff with `--handoff`) |
| `examples/sources.json` | Illustrative example matching icp-tam-builder's dental example |
| `tests/run_tests.py` | 20 tests for the checker |

## Exa

The skill uses Exa as well as its own search when the Exa plugin is connected. Searches send the query text to Exa, so client names stay out of queries unless you agree. Exa's research agent (`agent_run`) costs credits; the skill says the cost before using it.

## Versions

- **v0.1 (20 November 2026):** first draft. The research method was benchmarked on a research task about one person: 25 of 44 known sources with my own tools, 42 of 44 with Exa search added (my earlier searching found 13). Lessons added to the method.

- **v0.2 (20 November 2026):** fixes from the first real run. Unclear-terms warnings grouped into one line; `fields_ok` now means the fields the source holds are correct, with needed-but-missing fields in `fields_missing`; sources whose links fail the final check are re-ranked; the search log is written as each search is made. 20 tests. Terms of use must be read for every start and add source (the checker warns per source when they are not).

- **v0.3 (22 November 2026):** file names follow the client folder. The skill finds `<client>-icp-handoff.json` as well as `icp-handoff.json`, and where the folder names files after the client it writes `<client>-sources-plan.md`, `<client>-sources.json`, `<client>-search-log.csv` and `<client>-samples/`, with the same names inside `sources.json`. Found on a real client folder: the ICP skill had written `exampleco-icp-handoff.json`, which this skill would not have looked for. Instructions only; the checker already accepts any file name. 20 tests.

## Known limits

- One real run so far (20 November 2026). Its results are client work and are not published.
- The v0.3 naming rule has not been tried on a fresh run yet.
- The checker cannot tell whether a source is real or a sample was really checked; it checks the record is complete and consistent.
- It needs icp-tam-builder installed next to it to run the full handoff check; otherwise it checks the handoff's main fields by hand.
