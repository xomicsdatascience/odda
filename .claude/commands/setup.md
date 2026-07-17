---
description: Configure ODDA's bring-your-own-key model provider (chat + embedding) and verify it.
---

# ODDA model setup (bring-your-own-key)

ODDA has **no default model provider**. The user must configure their own chat and
embedding providers before article extraction, semantic search, or synthesis will
run. This skill collects that configuration, writes `.claude/model.config`, and
verifies it. Chat and embedding are configured **independently** (some chat
providers, e.g. Claude, cannot produce embeddings).

The configuration is consumed by `odda_utils/src/odda_utils/llm.py`
(`complete_json` / `embed`). Read that file's header for the authoritative format.

## Rules
- **Never print API keys** back to the user or into logs. Prefer storing the key in
  a separate file referenced by `api_key_file` (those files are gitignored:
  `.claude/*.key`, `.claude/model.config`).
- Confirm the secret files are covered by `.gitignore` before writing anything; if
  `.gitignore` is missing the `.claude/*.key` / `.claude/model.config` entries, add
  them first.
- Do not commit `.claude/model.config` or any key file.

## Steps
1. Explain briefly that ODDA needs a chat provider and an embedding provider, and
   that keys stay local.
2. Ask (AskUserQuestion) for the **chat provider**:
   - `azure_claude` — Claude hosted on Azure AI Foundry (this lab's choice). Needs a
     Foundry `resource` name (or `base_url`), a `model` (Foundry Claude deployment
     id), and an API key.
   - `anthropic` — Anthropic direct (needs api_key, optional base_url).
   - `openai` — OpenAI direct (needs api_key).
   - `azure_openai` — Azure OpenAI (needs endpoint, api_key, deployment model).
   - `ollama` — local, no key (needs base_url, default `http://localhost:11434/v1`).
3. Ask for the **embedding provider** (only `azure_openai`, `openai`, or `ollama`
   are valid — Claude/Anthropic cannot embed). This lab uses `azure_openai` with
   `text-embedding-3-small`.
4. Collect the required fields for each choice. For keys, ask the user to place the
   secret in a file and give its path (recommended), e.g. `.claude/azure_claude.key`
   and `.claude/azure.key`; or accept an env-var name via `*_env`. Only accept an
   inline key if the user insists.
5. Write `.claude/model.config` as JSON with separate `chat` and `embedding` blocks.
   Use `api_key_file` / `endpoint_file` references rather than inline secrets where
   possible.
6. Verify: write a temp script (per project convention) that calls
   `odda_utils.llm.describe_config()` and, if the user consents to a live check, a
   tiny `complete_json("return {\"ok\": true}")` and `embed("test")`; report the
   resolved provider + model for each role. Do NOT print secrets.

## Template for this lab (Azure-Claude chat + Azure-OpenAI embeddings)
Write `.claude/model.config` like this (adjust names; keys live in the referenced
files):

```json
{
  "chat": {
    "provider": "azure_claude",
    "model": "<your-foundry-claude-deployment-id>",
    "resource": "<your-foundry-resource-name>",
    "api_key_file": ".claude/azure_claude.key"
  },
  "embedding": {
    "provider": "azure_openai",
    "model": "text-embedding-3-small",
    "endpoint_file": ".claude/azure.endpoint",
    "api_key_file": ".claude/azure.key",
    "api_version": "2024-02-01"
  }
}
```

The user then creates the referenced key/endpoint files (gitignored). Equivalent
env vars also work: `ODDA_CHAT_PROVIDER`, `ODDA_CHAT_MODEL`, `ODDA_CHAT_RESOURCE`,
`ODDA_CHAT_API_KEY`, and `ODDA_EMBEDDING_PROVIDER`, `ODDA_EMBEDDING_MODEL`,
`ODDA_EMBEDDING_ENDPOINT`, `ODDA_EMBEDDING_API_KEY`.
