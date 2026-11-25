# Research method: finding every source, not the first few

**Bottom line:** a search engine shows the pages it ranks highest, not every page that exists. Full coverage comes from a routine: decide what counts as a hit, go through every source type on a checklist, search each type in several phrasings, open each source's own index (its archive, member list or register search) instead of trusting search results, follow links outward, and stop only when two rounds in a row find nothing new. Log every search, so the gaps are visible.

**Why this exists.** In the review-panel research (19 November 2026), my own searching found 13 sources for one person; Exa's research agent found 44 unique ones, including all 13 of mine. The gap was not the search engine alone. I never opened the newsletter's archive page (11 posts missed), never searched the platform's own post list (17 LinkedIn posts missed), and never looked for podcast or video appearances. Every step below closes one of those gaps.

**Running example:** finding where a Nigerian microfinance bank's details can be found (Tier 1 for a client that sells to microfinance banks).

---

## Step 1. Define a hit before searching

Write one line saying what counts and what does not.

> A hit is a source that lists, or lets us look up, licensed microfinance banks in Nigeria, with at least the name and one more field (state, licence category, address or contact). A news article naming one bank is not a hit.

Without this line, searching drifts and coverage cannot be counted.

## Step 2. Go through every source type on the checklist

Use the checklist for the job (`source-types.md`). Mark each type, in the search log, as one of:

- **Found:** at least one hit, listed.
- **Searched, none found:** with the phrasings tried.
- **Not applicable:** with one line saying why (for example, no app store for a register).

A source type is never skipped silently. An empty row is a finding: it tells the next person where not to waste time, and where a gap may still hide.

## Step 3. Search each type in at least three phrasings

Search engines match words. One phrasing finds one cluster. For each type, vary:

- **The name:** full name, short name, abbreviation (Central Bank of Nigeria, CBN).
- **The local term:** the word the market uses, not the client's (in Nigeria, "MFB" and "microfinance bank"; elsewhere "credit union", "SACCO").
- **The regulator's or publisher's term:** the title the list itself would carry ("list of licensed microfinance banks", "financial institutions directory").
- **The format:** "PDF", "Excel", "directory", "register", "member list".
- **The subject's own vocabulary:** once the first hits are in, reuse their titles and pet phrases as search terms. In the benchmark, my own search missed a podcast titled "Building a Company Brain for AI" with six phrasings built from the person's name and field, but returned it when the phrasing used the episode's own words. (Exa found it from the name and company alone.) That suggests, but does not prove, that topic words from early hits help find later ones: treat this step as worth trying, not as tested.

Record every phrasing in the log, including the ones that found nothing.

## Step 4. Open each source's own index

Search results show a few pages from a site. The site usually holds far more. When a hit belongs to a larger collection, go to the collection itself:

| Where the hit is | Open this |
|---|---|
| A newsletter post (Substack, Beehiiv, Ghost) | The archive page (`/archive` on Substack), then `sitemap.xml` and the RSS feed (`/feed`): in the benchmark the archive page showed only the 12 newest posts, and the sitemap held 13 older ones |
| Any website | `sitemap.xml` (and `robots.txt`, which often names it): the full list of the site's pages |
| A register or directory entry | The register's search or full list, and its download if one exists |
| One page of a paginated list | Every page, or the export |
| A LinkedIn post | The author's or company's activity page; then search the platform's own posts for the name |
| A podcast episode | The show's episode list; then search for the person's other guest appearances |
| A video | The channel's video list, and its RSS feed (`youtube.com/feeds/videos.xml?channel_id=...`), which lists videos when the page itself shows a consent screen |
| A code repository | The owner's full repository list (GitHub's public API: `api.github.com/users/<name>/repos`) |
| A member's profile on an association site | The association's full member directory |
| A PDF from a regulator | The page it was published on, for newer versions and related lists |

If the index will not open for automated reading (blocked, a login, a 403), list it as **open by hand**, with the link. Never count it as searched.

## Step 5. Follow links outward

Each good source points to others: "see also" pages, the regulator a directory cites, the association a company belongs to, the podcast a post links to. Open the links on every hit once, and add any new source type or collection to the checklist.

## Step 6. Use every search tool available, and note which found what

- **My own web search and page reader** are always available.
- **Exa**, when it is connected (the Exa plugin), adds `web_search_exa` (its own index, often finding pages my search misses) and `agent_run` (a multi-step research run that costs credits). Run Exa searches alongside my own, not instead of them.
- **Use Exa's page reader (`web_fetch_exa`) for pages my own reader cannot open.** In the benchmark it opened LinkedIn posts, which my reader cannot (LinkedIn blocks it).
- **Keep opening indexes with my own reader even when Exa is connected.** In the benchmark, Exa's search found nearly all the LinkedIn posts and podcast pages, but my reader opening sitemaps, feeds and repository lists found 73 pages Exa's search did not.
- My own web search may refuse a search built only on a private person's name. Search the name with their company, newsletter or field instead.
- Record the tool in the log for every search. Over time, this shows which tool finds which kinds of source.

**What the benchmark showed** (20 Nov 2026, one run each, finding one person's published words against 44 known sources): my earlier searching, 13; this method with my own tools only, 25; this method with Exa search added, 42. Without Exa, the method finds owned archives well but sees no LinkedIn posts, few podcasts on other people's sites and no X copies. For a job that depends on those, say so in the coverage report, or connect Exa.

Exa costs credits. Before an `agent_run`, say which effort level and its fixed price (Exa pricing, read 20 Nov 2026: minimal $0.012, low $0.025, medium $0.10, high $0.50, xhigh $1.00; auto and ultra are metered, with $5 and $20 default caps). Searches through Exa send the query text to Exa, so keep client names and private details out of queries unless the user agrees.

## Step 7. Stop only when two rounds find nothing new

A round is one pass over the checklist with new phrasings, plus the indexes and links from the last round's hits. Keep going until **two rounds in a row add no new hit**. Then stop, and say so.

Most jobs need two to four rounds. If a job is still finding new hits after five, the hit definition is probably too broad: tighten it and say so.

**Very large sources.** Some sources hold hundreds of items (a person's LinkedIn feed held over 200 posts in the benchmark, and the run hit its call cap still finding 1 or 2 a search). Decide a window in the hit line before searching (for example, "posts from the last 12 months"), or a cap, and apply the stop rule inside it. Report the source as "more beyond the window" rather than as complete.

## Step 8. Open and check every hit

A search result is a lead, not a hit. Open each one and record:

- the date checked;
- whether it holds what the hit line requires (and how many records, if it is a list);
- its own date (published, last updated, or "no date shown");
- any access limit (free, a login, paid, blocked).

## Step 9. Keep the search log

One row per search, in `search-log.csv` next to the results. Write each row when the search is made, not afterwards from memory: a log rebuilt later loses the counts that show where coverage came from.

| Column | What it holds |
|---|---|
| round | 1, 2, 3 ... |
| source_type | from the checklist |
| tool | own search, page reader, exa search, exa agent |
| query | the exact text, or the index URL opened |
| results | how many results came back |
| new_hits | how many hits not already found |
| note | blocked, login, nothing relevant, and so on |

## Step 10. Report coverage honestly

The report says:

- the hit line from Step 1;
- hits found, by source type;
- source types searched with nothing found;
- sources to open by hand;
- the rounds run, and that the last two found nothing new;
- what the method cannot see (paid databases not searched, pages behind logins, private groups).

Never call a search complete when an index was blocked or a source type was skipped.
