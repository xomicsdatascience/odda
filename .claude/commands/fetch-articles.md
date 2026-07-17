---
name: fetch-articles
description: Fetches and processes articles matching a query.
---

# Instruction

Search PubMed for scientific articles and process them into the knowledge base using `search_and_fetch`. Gather parameters interactively, then execute the pipeline.

## Parameter Gathering

Ask the following questions sequentially using `AskUserQuestion`. Do not ask them all at once.

### Question 1: PubMed Query (required)

Ask the user for their PubMed search query string. In the question text, briefly mention that PubMed field tags like `[Title/Abstract]` and `[MeSH Terms]` are supported, as well as Boolean operators (`AND`, `OR`, `NOT`).

Provide 2-3 example options such as:
- `proteomics[Title/Abstract]`
- `single-cell RNA-seq[Title/Abstract] AND cancer[MeSH Terms]`

The user should be able to enter their own query via "Other".

### Question 2: Date Range (optional)

Ask if the user wants to filter by date range. Provide options:
- No date filter
- Last 30 days
- Last 6 months
- Last year
- Other (user enters custom YYYY-MM-DD start and end dates)

If the user selects a date range (anything other than "No date filter"), ask a follow-up question about the date type:
- `edat` - Entrez date (default, when article was added to PubMed)
- `pdat` - Publication date
- `mdat` - Modification date

Default to `edat` if the user doesn't specify.

### Question 3: Advanced Options

Present the following defaults and ask the user to confirm or modify. Use a multi-select question so the user can toggle individual options they want to change. If no changes are selected, use all defaults.

- **Database path**: `articles.sqlite`
- **Max results**: `100`
- **Download articles**: yes (to `/data/articles/`)
- **Extract LLM metadata**: yes
- **Overwrite existing**: no
- **Embedding model**: `text-embedding-3-small`
- **LLM model**: `gpt-5`
- **Azure endpoint file**: `.claude/azure.endpoint`
- **Azure API key file**: `.claude/azure.key`

For any option the user selects to change, ask a follow-up question to get the new value.

**Key dependency**: If the user declines downloading articles, force `extract_llm_metadata` to `false` regardless of what the user selected, because LLM extraction requires downloaded full text. Inform the user if this override occurs.

## Execution

1. Assemble all parameters from the user's answers combined with the default values for anything not changed.
2. Display a summary of the final configuration to the user before calling the tool. Warn that processing via LLMs can take some time and that no output will be visible.
3. Dispatch to the most relevant agent, instructing it to call `mcp__odda_utils__search_and_fetch` with the assembled parameters. If the user declined downloading, pass `download_dir` as `null`.
4. After the call completes, report the results: articles found, processed, skipped, and any errors.
