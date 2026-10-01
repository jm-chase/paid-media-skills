# Paid media skills for Claude Code

Twenty-five skills for running Google Ads accounts with Claude Code: auditing, querying,
search term work, ad copy, measurement and the safety rails that keep an agent from
changing an account nobody approved.

These came out of running a nine-account portfolio, roughly $630K in managed spend over
18 months. Every rule in them exists because something went wrong once.

## Install

```bash
git clone https://github.com/jm-chase/paid-media-skills ~/.claude/skills
```

Or copy individual skill folders into `~/.claude/skills/`. Claude Code picks them up by
name; a skill loads when what you ask matches its description.

## What is in here

**Auditing and diagnosis**

- `account-audit` — Comprehensive single-account Google Ads health audit
- `anomaly-detection`
- `impression-share-diagnostics` — Impression share analysis and root cause diagnosis for Google Ads Search campaigns
- `investigation-methodology` — Structured hypothesis-driven investigation framework for diagnosing Google Ads performance issues
- `change-history-checker`
- `non-serving-keyword-scanner` — Scans your agency accounts for keywords with 0 impressions in last 180 days
- `youtube-placement-audit` — Audit Google Ads accounts for bad YouTube placements (kids content, adult, gaming, non-English, spam) across PMAX, Demand Gen, and Display campaigns

**Querying the API**

- `gaql-query-patterns` — Reusable GAQL query templates for Google Ads API
- `google-ads-samples` — Reference library of official Google Ads API code samples

**Search terms and keywords**

- `sqr-3run`
- `sqr-classifier` — Classify search terms by intent

**Ad copy**

- `ad-copy-generation-framework`
- `ad-copy-verification-standard` — Mandatory verification requirements for all ad copy creation (RSAs, extensions, callouts, structured snippets)
- `rsa-refresh` — Refresh RSA ad copy by scraping the business website, identifying LOW-performing assets, and generating replacement headlines and descriptions using AI
- `rsa-bulk-edit`
- `pmax-builder`
- `dgen-automation-disable` — Bulk-disable Demand Gen ad-level asset automation settings

**Measurement and lead quality**

- `ga4-campaign-cross-reference` — Cross-referencing framework for comparing GA4 behavioral data with Google Ads campaign settings to identify discrepancies and configuration gaps
- `ga4-cross-analysis`
- `lead-quality-pattern-analysis` — Red flag detection frameworks for lead quality analysis across GA4 behavioral data
- `lead-quality-recommendation-prioritization` — Recommendation prioritization framework with implementation timelines for lead quality investigations

**Budget and reporting**

- `budget-recommendation-calculator` — Calculates conservative budget recommendations for Google Ads accounts based on pacing variance, impression share analysis, and performance constraints
- `client-communication-standards` — Client-facing report formatting standards
- `markdown-to-sheets-presenter` — Transforms markdown reports into professionally formatted Google Sheets for client presentation

**Safety**

- `mutation-safety` — MANDATORY safety system for ALL Google Ads mutations AND destructive Google Sheets writes

## Three rules worth stealing even if you take nothing else

**Mutations are two-step.** `mutation-safety` makes every write to an account show a
dry-run first — current value, proposed value, how many things change, and whether it can
be undone — then wait for a human. An agent that can edit a live ad account without that
is a liability, however good its reasoning is.

**Ad copy is sourced, never invented.** `ad-copy-verification-standard` requires every
claim in an ad to trace to the client's own website. Empty beats inaccurate, and a
plausible hallucinated claim in a live ad is a problem nobody catches until the client does.

**Thresholds, not adjectives.** Every decision rule names the number that triggers it.
"Check if spend looks high" is an instruction to guess; "spend is more than 40% above
the daily target" is a rule two people apply the same way.

## Scope

Client names, credentials and account identifiers are not in here. Examples use
placeholder customer ids. Some skills reference scripts that live in private repositories;
the skill still documents the procedure and the thresholds, which is the part worth having.

Built by [James Chase](https://jameschase.co/portfolio). MIT licensed.
