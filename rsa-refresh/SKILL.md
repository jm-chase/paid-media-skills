---
name: rsa-refresh
description: Refresh RSA ad copy by scraping the business website, identifying LOW-performing assets, and generating replacement headlines and descriptions using AI. Uses Firecrawl for scraping and Claude for copy generation.
---

# RSA Refresh Skill

Refreshes Responsive Search Ad copy by replacing LOW-performing assets with new AI-generated headlines and descriptions verified against the actual business website.

## Workflow

### Stage 1: Prepare Context
```bash
cd google-ads-mcp && PYTHONPATH=. python queries/rsa_refresh_generator.py \
  --cid YOUR_CID \
  --sheet-id YOUR_SHEET_ID \
  --prepare-for-claude
```

This will:
1. Query existing RSAs and asset performance labels (BEST/GOOD/LOW/LEARNING)
2. Scrape the business website using Firecrawl
3. Extract property/business features from the site
4. Output `rsa_context_{cid}.json` with all data Claude needs

### Stage 2: Generate Copy (Claude Code)
Read `rsa_context_{cid}.json` and generate replacement headlines + descriptions following the reference docs:
- `references/pm-headline-structure.md` -- 15 headline rules (1 customizer + 14 AI-generated)
- `references/description-voice-lifting.md` -- 3 descriptions with voice lifting technique
- `references/hallucination-filter.md` -- Defense-in-depth filter for unverified claims

Save output as `copy_{cid}.json`

### Stage 3: Resume and Write to Sheet
```bash
cd google-ads-mcp && PYTHONPATH=. python queries/rsa_refresh_generator.py \
  --cid YOUR_CID \
  --sheet-id YOUR_SHEET_ID \
  --copy-file copy_YOUR_CID.json
```

This merges AI copy with existing ad structure and writes to Google Sheets with "Original RSAs" and "Refreshed RSAs" tabs.

## Key Rules
- **Empty > Inaccurate** -- never include unverified claims
- Only use information explicitly found on the business website
- See `references/hallucination-filter.md` for forbidden terms
- LOW-performing assets are the primary replacement targets
- BEST and GOOD assets are preserved

## Prerequisites
- `FIRECRAWL_API_KEY` environment variable (get from firecrawl.dev)
- Google Ads API credentials configured
- Google Sheets API credentials configured

## Optional: Pre-Refresh Baseline
```bash
cd google-ads-mcp && PYTHONPATH=. python queries/rsa_baseline_snapshot.py \
  --cid YOUR_CID \
  --sheet-id YOUR_SHEET_ID
```
Captures IWQS, QS components, ad metrics, and impression share before making changes.

## Related Skills
- `ad-copy-verification-standard` -- Mandatory verification protocol
- `google-ads-creation` -- RSA validation rules
