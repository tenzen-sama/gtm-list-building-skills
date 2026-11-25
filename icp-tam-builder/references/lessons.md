# Lessons about the skill

Read this in Step 0 of every job, together with the work lessons file. This file holds what went wrong when the skill itself was tested, so the same mistake is not made twice.

**Two files, two jobs.**
- **This file** is part of the skill. It changes only when the skill is updated. Never write to it during a job.
- **The work lessons file** is `lessons.md` in the folder that holds the client folders (for example `project/clients/lessons.md`, or `clients/lessons.md`). It holds what users corrected on real jobs. It sits outside the skill, so a skill update never overwrites it. At the end of each engagement, and whenever the user corrects the ICP at the sign-off or after delivery, add one line there in the format below. Create it if it does not exist, starting with a heading line `# Lessons from client work`. Record what was corrected and what to do differently, not the client's confidential details.

Format:

```
- [date], [client or "skill test"]: [what happened]. Do instead: [what to do differently]. Source: [file or conversation]
```

---

## Lessons

- 19 Nov 2026, skill test (Quick mode, one run): the reply named its sources without URLs, where an earlier version gave page paths. One run, so this may be chance. Do instead: in Quick mode, give the URL of every page cited. Source: `icp-tam-builder-workspace/iteration-1/benchmark.md`.
- 19 Nov 2026, skill test (Refresh, older version of the skill): the refreshed brief contained a quote that is not in the transcript it cites. Do instead: run `scripts/check_quotes.py` on every brief, sign-off and quote bank before delivering, whenever the transcripts are files. Source: `icp-tam-builder-workspace/iteration-1/benchmark.md`.
- 19 Nov 2026, skill test (resonance check): the test prompt referred to an ICP but none was attached, and the run of the older version went searching the user's folders for one. Do instead: in a Resonance check, if the ICP is not in the conversation, ask for it; do not search for it. Source: `icp-tam-builder-workspace/iteration-1/benchmark.md`.
- 20 Nov 2026, skill test (Quick mode, v4, one run): the reply gave a URL for every page cited (21), so the 19 Nov missing-URL problem did not repeat. But it labelled a government survey table (an estimate) as "counted", while also saying it is not a list you can open. Do instead: keep giving URLs; follow frameworks.md, where counted means a list you can open, and when the count comes from a statistical table say so plainly rather than calling it counted without qualification. Source: `icp-tam-builder-workspace/iteration-2/benchmark-v4-light.md`.
- 20 Nov 2026, skill test (Full build, v4, one run): the ICP table's "Trigger events" row had a Tier 1 value and an empty "Why it matters" cell. Do instead: give every Tier 1 row a one-line reason tied to the value the buyer gets, or write "Unknown" with what would settle it. Source: `icp-tam-builder-workspace/iteration-2/benchmark-v4-light.md`.
