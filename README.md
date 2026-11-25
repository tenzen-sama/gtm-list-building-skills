# GTM list-building skills for Claude Code

**Bottom line:** three Claude Code skills that take you from "who should this client sell to?" to search links you can open in Apollo and Prospeo. Facts are sourced or labelled as assumptions, and anything a script cannot apply is reported rather than guessed.

A **skill** is a folder with a `SKILL.md` file of instructions, plus scripts and reference files, that Claude loads when a task matches its description.

## How they fit together

| Step | Skill | You give it | You get |
|---|---|---|---|
| 1 | [`icp-tam-builder`](icp-tam-builder/) | A client's website and, ideally, call transcripts and a customer list | Ideal customer profile (ICP), buyer personas, market size, a 0 to 100 scoring model and a handoff file (`icp-handoff.json`) |
| 2 | [`lead-sources`](lead-sources/) | The handoff file | Where those companies, their buying signals and decision-makers can be found, with a sample check on each source |
| 3 | [`search-query`](search-query/) | The handoff file, the sources plan or a plain request | Apollo and Prospeo links with the filters set, and a list of what could not be applied |

A list builder that pulls, cleans and scores the results is planned but not built.

## Example

For an invented client that sells booking software to dental clinics:

1. "Build the ICP and market size for my client. Here is their website text and six call transcripts."
2. "Find the lead sources for this ICP."
3. "Build Apollo and Prospeo searches from the handoff file."

Each skill has an `examples/` folder with sample files.

## Install

Copy the three folders into `.claude/skills/` inside your project (or into your personal `~/.claude/skills/`). The scripts need Python 3.

Run a skill's tests from its folder:

```
python tests/run_tests.py
```

## Known limits

- The Apollo and Prospeo skill has not yet been run on a live new request. As of 22 November 2026, only Prospeo's job title filter had been seen in a working link; the other Prospeo filters come from its documentation and are flagged.
- `lead-sources` has had one real run.
- Not every version of `icp-tam-builder` has been tested with its evals. Its README says which.
- Apollo and Prospeo can change their link formats at any time.
- Dated version notes in each skill's README mention test results and working files that are not published here.

## Credits

Some Apollo industry IDs come from the seed list in [walutani1/apollo-url-builder](https://github.com/walutani1/apollo-url-builder) (MIT licence). MaxIQ and Sketch Labs appear as worked examples. Neither company endorses this work.

## Licence

MIT. See [LICENSE](LICENSE).
