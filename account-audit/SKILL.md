---
name: account-audit
description: Comprehensive single-account Google Ads health audit. Pulls 27 datasets covering performance, conversion configuration, impression share, landing pages, demographics, geo and audiences; scores the account, detects bleed and opportunity items, and renders a client-facing HTML report plus an internal brief. Auto-invoke when user says 'run account audit', 'audit [account]', 'account health check', or 'full audit for [account]'.
allowed-tools: [Bash, Read, Write, Edit]
---

# Account Audit

Deep health audit for a single Google Ads account. Read-only — it never mutates.

**Engine:** `~/Projects/ppc-audit/` (standalone; runs from any project)
**Output:** `~/Projects/ppc-audit/audits\<YYYYMMDD>-<slug>\`

---

## Which audit skill to use

| Situation | Use |
|---|---|
| Account we manage, full depth, client- or internal-facing | **this skill** |
| Cold prospect, no relationship context, fast turnaround | `prospect-teardown` |

`prospect-teardown` runs 5 checks and is deliberately shallow — it's a lead-gen offer for
accounts we know nothing about. This skill runs the full engine and assumes we have context.

---

## What it actually checks

**Collected (27 datasets):** account info, daily KPIs, campaigns (90d + 30d), campaign
settings, bid targets, keywords, negative keywords, search terms, conversion actions, ads,
asset coverage, ad groups, device split, demographics, geo performance, landing pages,
asset group URLs, audiences, auction insights (account-level and per-keyword), change
history, PMax assets.

**Computed:**

| Area | Checks |
|---|---|
| Performance | 90d totals, 45d-vs-prior trend, weekly series, campaign-type breakdown |
| Waste | Zero-conversion campaigns with spend, zero-conv keywords, un-negated search terms |
| Conversion health | Active/dead/unverified actions, duplicate-tracking detection |
| Conversion config | Primary vs secondary, value weighting, counting mode on lead actions, lookback windows, legacy Universal Analytics goals |
| Impression share | Budget-lost vs rank-lost diagnosis, per-campaign caps |
| Bidding | Smart bidding on thin conversion data, bid-strategy/target mismatches |
| Keywords | QS distribution, redundant keywords cannibalising across ad groups, match-type mix |
| Creative | RSA ad strength, disapprovals/limited eligibility, asset coverage gaps |
| Destinations | **Live HTTP check on every final URL** — 404s, with bot-blocks excluded |
| Landing pages | Where paid clicks actually land, concentration, zero-converting pages |
| PMax | Final URL expansion **inferred** from traffic vs asset-group-declared URLs |
| Targeting | Age/gender segments and geo regions taking budget at poor efficiency |
| Audiences | Remarketing list sizes against the Search serving threshold |
| GA4 | All-paid-channel traffic and landing pages (sees Meta, which Ads cannot), plus Ads-vs-GA4 reconciliation scoped to this customer ID |
| Competitive | Branded vs non-branded efficiency. **Auction insights do not work** — see Gotchas |
| Structure | Theme alignment between keywords and ad copy, negative keyword gaps |
| Hygiene | Change history — flags accounts with no changes in 30 days |

Everything rolls into **bleed items** and **opportunity items**, each rated HIGH/MEDIUM/LOW,
plus a 0–100 health score with a letter grade.

---

## How to run it

Default is the two-phase mode: the script does the deterministic work, **you write the
narrative on the Claude Code subscription**. No Anthropic API credits.

### Phase 1 — collect and analyse

```bash
cd "C:/Users/james/Projects/ppc-audit"
py prospect-auditor.py --cid <digits> --slug <client-slug> --no-narrative
py prospect-auditor.py --cid <digits> --mcc <manager-id> --slug <client-slug> --no-narrative
py prospect-auditor.py --cid <digits> --mcc <id> --ga4-property <numeric-id> --slug <s> --no-narrative
```

**Pass `--ga4-property` whenever a GA4 property exists** (look it up in
`ppc-management/clients.py`). It adds the only view of non-Google paid channels and the
Ads-vs-GA4 reconciliation. A shared property is scoped by customer ID automatically, so a
property serving several Ads accounts still reports correctly.

`--slug` currently only names the output directory. It was built to inject client context
(targets, brand keywords, conversion meanings) but the `client_context` module it imports no
longer exists in ppc-management — see Gotchas. The script catches this and continues, so the
audit is unaffected; just don't expect target-aware interpretation. Supply targets yourself
when writing the narrative.

The script prints the paths and stops. Collection takes a few minutes; the URL checker makes
one live request per unique final URL.

### Phase 2 — read the brief, write the narrative

Read `analytics-brief.txt` from the output directory. It is pre-computed and compact
(~3–5k chars) — everything you need is in it. **Do not re-query the API to second-guess it.**

Write the narrative to `claude-output.txt` in the same directory, in exactly this format —
the renderer parses these tags and will fall back to placeholder text if they're missing:

```
---EXEC_SUMMARY---
[3-4 sentences. Lead with the single most important finding. Opportunity framing, not criticism.]
---FINDINGS---
1. [Specific, data-backed, rated HIGH/MEDIUM/LOW]
...max 6, most impactful first
---OPPORTUNITIES---
1. [Title] | [One sentence on impact or rationale]
...max 5
---NEXT_STEPS---
1. [What to do, which campaign/setting, expected outcome]
...max 5
---END---
```

**Rules for the narrative:**
- Every number comes from the brief. Never invent or estimate.
- Client-facing language — say "ad relevance score", not "QS".
- Frame as opportunity, not failure.
- **Run the prose through a voice skill of your own before writing the file.** The exec summary and
  opportunities land in a client-facing HTML report, so the external output gate applies.
- Findings and next steps also feed the internal brief — be direct and specific there.

### Phase 3 — render

```bash
py prospect-auditor.py --slug <client-slug> --skip-collect --narrative "<path-to-claude-output.txt>"
```

Reuses the collected CSVs, renders the HTML, and builds the internal brief.

### API fallback

Omit `--no-narrative` to have the script call the Anthropic API itself. Costs credits, and
the narrative skips the a voice skill of your own pass. Use only for unattended/batch runs.

---

## Reading the brief

**Impression share — answer the budget question honestly.** The brief carries the three real
numbers and a diagnosis; Google's "Limited by budget" flag is not evidence. Per-campaign
detail is in `campaigns.csv`.

| Pattern | Diagnosis | Action |
|---|---|---|
| Budget-lost IS ≥10%, rank-lost low | Genuine budget constraint | Increase is defensible |
| Rank-lost IS dominant | More money buys little | Fix QS, bids, relevance |
| Search IS >80% | Capturing available demand | No action |

Most accounts flagged "limited by budget" are rank-limited. Say so.

**Conversion health and configuration first.** Broken measurement invalidates every other
number in the audit. Read both sections: dead/duplicate actions, and then how the live ones
are configured — how many are primary, what values they carry, whether a lead action counts
many-per-click. An account can have healthy-looking conversions that are still steering
bidding badly.

**Branded vs non-branded.** A strong blended return that is mostly branded means they're
paying for demand they already had. Non-branded efficiency is the real signal.

**Broken URLs are the easiest win.** They're concrete, verifiable by the client in one click,
and always HIGH.

---

## Outputs

| File | Audience |
|---|---|
| `audit-report-<slug>.html` | Client — self-contained, no external assets |
| `internal-brief.txt` | Us — full narrative + raw analytics brief appended |
| `analytics-brief.txt` | Us — the computed input |
| `data/*.csv` | Us — raw pulls, reusable via `--skip-collect` |

---

## Gotchas

- **Check for sub-accounts first.** Auditing one and presenting it as the whole picture once
  made a real client look 40% worse than reality.
- **`--skip-collect` resolves the output directory from today's date + slug.** Resuming on a
  later day won't find the data; pass the same `--slug` and re-run on the same day, or
  collect again.
- **Quality Score is often absent** — Google doesn't always populate it.
- **Auction insights never populate.** There is no `auction_insight` resource in the Google
  Ads API — it is a UI-only report. The collector degrades to empty, so the audit carries no
  competitive data. The working route is the Google Ads Script at
  `ppc-management/auction_insights_collector.js`, which writes weekly branded/non-branded
  splits to a sheet; reading that sheet here would close the gap.
- **Single account only.** No portfolio mode.
- **Snapshot, not a trend line** beyond the built-in 45d-vs-prior comparison.
- **Client-context injection is dead code.** `audit_analytics.py` imports `client_context`
  (`get_tcpa_target`, `context_for_claude`) and `prospect-auditor.py` imports `client_context.load`
  — that module no longer exists; `client_profiles.py` appears to be its successor but the APIs
  differ. All call sites are guarded, so nothing crashes. Restoring it means writing a shim from
  `client_profiles` to the old API. Worth doing if target-aware bid-strategy checks matter.
- The engine hardcodes credentials paths (`~/.google/google-ads-credentials.json`) and a dev
  token in `audit_collector.py`. Fine locally; must move to config before this is productised.

---

## Related

`prospect-teardown` (shallow, cold accounts) · `impression-share-diagnostics` (IS framework)
· `conversion-tracking-health` (portfolio-wide conversion audit) · a voice skill of your own (mandatory
finishing pass) · `budget-recommendation-calculator` (if the audit justifies a budget move)

---

## Version History

| Version | Date | Changes |
|---|---|---|
| 1.0 | 2025-01-02 | Initial — 13 sections, referenced `google-ads-mcp/queries/account_audit.py` |
| 2.0 | 2026-08-04 | Repointed to the real `ppc-audit` engine (the 1.0 script never existed at that path). Two-phase subscription mode, voice gate, accurate check list. |
