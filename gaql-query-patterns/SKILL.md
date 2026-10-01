---
name: gaql-query-patterns
description: Reusable GAQL query templates for Google Ads API. Auto-invoke when writing Google Ads queries, analyzing campaign data, querying performance metrics, or building custom reports.
---

# GAQL Query Patterns

Ready-to-use GAQL (Google Ads Query Language) query templates for common PPC analysis tasks.

## Campaign Queries

### 7-Day Campaign Spend Analysis

```sql
SELECT
    campaign.id,
    campaign.name,
    campaign.status,
    campaign.advertising_channel_type,
    campaign.bidding_strategy_type,
    campaign_budget.amount_micros,
    campaign_budget.explicitly_shared,
    metrics.cost_micros,
    metrics.impressions,
    metrics.clicks,
    metrics.conversions,
    metrics.conversions_value
FROM campaign
WHERE segments.date DURING LAST_7_DAYS
ORDER BY campaign.name
```

**Use for:** Recent spend analysis, budget utilization, campaign health checks

---

### Month-to-Date Pacing

```sql
SELECT
    campaign.id,
    campaign.name,
    campaign_budget.amount_micros,
    metrics.cost_micros
FROM campaign
WHERE segments.date DURING THIS_MONTH
ORDER BY campaign.name
```

**Use for:** Monthly pacing calculations, budget tracking

---

### Campaign Settings Audit

```sql
SELECT
    campaign.id,
    campaign.name,
    campaign.status,
    campaign.advertising_channel_type,
    campaign.bidding_strategy_type,
    campaign.target_cpa.target_cpa_micros,
    campaign.target_roas.target_roas,
    campaign_budget.amount_micros,
    campaign_budget.explicitly_shared
FROM campaign
WHERE campaign.status = 'ENABLED'
```

**Use for:** Configuration audits, bidding strategy checks, budget review

---

## Impression Share

### Search Impression Share Analysis

```sql
SELECT
    campaign.id,
    campaign.name,
    campaign.advertising_channel_type,
    metrics.search_impression_share,
    metrics.search_budget_lost_impression_share,
    metrics.search_rank_lost_impression_share,
    metrics.impressions
FROM campaign
WHERE segments.date DURING LAST_7_DAYS
  AND campaign.advertising_channel_type IN ('SEARCH', 'PERFORMANCE_MAX')
ORDER BY metrics.search_budget_lost_impression_share DESC
```

**Use for:** Diagnosing underspending, identifying budget constraints vs. quality issues

**Interpreting results:**
- High Budget Lost IS → increase budget to capture more impressions
- High Rank Lost IS → quality/relevance issue (not a budget problem)
- Both high → budget is primary constraint, but quality also needs work

---

## Search Terms

### Search Term Report (Last 30 Days)

```sql
SELECT
    search_term_view.search_term,
    campaign.name,
    ad_group.name,
    metrics.impressions,
    metrics.clicks,
    metrics.cost_micros,
    metrics.conversions,
    search_term_view.status
FROM search_term_view
WHERE segments.date DURING LAST_30_DAYS
  AND metrics.impressions > 0
ORDER BY metrics.cost_micros DESC
```

**Use for:** Negative keyword discovery, search term audits, intent analysis

---

### High-Spend Non-Converting Search Terms

```sql
SELECT
    search_term_view.search_term,
    campaign.name,
    metrics.clicks,
    metrics.cost_micros,
    metrics.conversions
FROM search_term_view
WHERE segments.date DURING LAST_30_DAYS
  AND metrics.conversions = 0
  AND metrics.cost_micros > 0
ORDER BY metrics.cost_micros DESC
```

**Use for:** Finding wasted spend, negative keyword candidates

---

## Keywords

### Keyword Performance with Quality Score

```sql
SELECT
    ad_group.name,
    ad_group_criterion.keyword.text,
    ad_group_criterion.keyword.match_type,
    ad_group_criterion.quality_info.quality_score,
    ad_group_criterion.quality_info.creative_quality_score,
    ad_group_criterion.quality_info.post_click_quality_score,
    ad_group_criterion.quality_info.search_predicted_ctr,
    metrics.impressions,
    metrics.clicks,
    metrics.cost_micros,
    metrics.conversions
FROM keyword_view
WHERE segments.date DURING LAST_30_DAYS
  AND ad_group_criterion.status = 'ENABLED'
ORDER BY metrics.cost_micros DESC
```

**Use for:** Quality score audits, keyword performance analysis

---

### Non-Serving Keywords (Zero Impressions)

```sql
SELECT
    campaign.name,
    ad_group.name,
    ad_group_criterion.keyword.text,
    ad_group_criterion.keyword.match_type,
    ad_group_criterion.status,
    metrics.impressions
FROM keyword_view
WHERE segments.date DURING LAST_180_DAYS
  AND campaign.status = 'ENABLED'
  AND ad_group.status = 'ENABLED'
  AND ad_group_criterion.status = 'ENABLED'
  AND metrics.impressions = 0
```

**Use for:** Finding dead keywords to clean up, account hygiene

---

## Ads

### RSA Performance

```sql
SELECT
    campaign.name,
    ad_group.name,
    ad_group_ad.ad.id,
    ad_group_ad.ad.responsive_search_ad.headlines,
    ad_group_ad.ad.responsive_search_ad.descriptions,
    ad_group_ad.ad_strength,
    metrics.impressions,
    metrics.clicks,
    metrics.conversions,
    metrics.cost_micros
FROM ad_group_ad
WHERE segments.date DURING LAST_30_DAYS
  AND ad_group_ad.ad.type = 'RESPONSIVE_SEARCH_AD'
  AND ad_group_ad.status = 'ENABLED'
ORDER BY metrics.impressions DESC
```

**Use for:** Ad performance review, RSA optimization

---

## Conversions

### Conversion Actions List

```sql
SELECT
    conversion_action.id,
    conversion_action.name,
    conversion_action.type,
    conversion_action.status,
    conversion_action.category,
    conversion_action.value_settings.default_value,
    conversion_action.counting_type,
    conversion_action.attribution_model_settings.attribution_model
FROM conversion_action
WHERE conversion_action.status = 'ENABLED'
ORDER BY conversion_action.name
```

**Use for:** Conversion tracking audits, identifying misconfigured actions

---

### Conversion Performance by Action

```sql
SELECT
    segments.conversion_action_name,
    segments.conversion_action_category,
    metrics.conversions,
    metrics.conversions_value,
    metrics.all_conversions,
    metrics.cost_micros
FROM campaign
WHERE segments.date DURING LAST_30_DAYS
ORDER BY metrics.conversions DESC
```

**Use for:** Understanding which conversion actions are firing, value distribution

---

## Geographic Performance

```sql
SELECT
    geographic_view.country_criterion_id,
    geographic_view.location_type,
    campaign.name,
    metrics.impressions,
    metrics.clicks,
    metrics.cost_micros,
    metrics.conversions
FROM geographic_view
WHERE segments.date DURING LAST_30_DAYS
ORDER BY metrics.cost_micros DESC
```

**Use for:** Geographic bid adjustments, location targeting audits

---

## Device Performance

```sql
SELECT
    campaign.name,
    segments.device,
    metrics.impressions,
    metrics.clicks,
    metrics.cost_micros,
    metrics.conversions,
    metrics.average_cpc
FROM campaign
WHERE segments.date DURING LAST_30_DAYS
ORDER BY campaign.name, segments.device
```

**Use for:** Device bid adjustments, mobile vs. desktop analysis

---

## Account-Level Summary

```sql
SELECT
    customer.id,
    customer.descriptive_name,
    metrics.cost_micros,
    metrics.impressions,
    metrics.clicks,
    metrics.conversions,
    metrics.conversions_value
FROM customer
WHERE segments.date DURING LAST_30_DAYS
```

**Use for:** High-level account overview, executive reporting

---

## Date Range Reference

| Keyword | Meaning |
|---------|---------|
| `YESTERDAY` | Yesterday only |
| `TODAY` | Today only |
| `LAST_7_DAYS` | Last 7 days |
| `LAST_14_DAYS` | Last 14 days |
| `LAST_30_DAYS` | Last 30 days |
| `THIS_MONTH` | Current month to date |
| `LAST_MONTH` | Previous calendar month |
| `THIS_WEEK_MON_TODAY` | This week (Monday to today) |

> **The `LAST_N_DAYS` literals are a CLOSED set — only 7 / 14 / 30.** There is **no** `LAST_60_DAYS`, `LAST_90_DAYS`, or `LAST_180_DAYS`. Using one fails with `INVALID_VALUE_WITH_DURING_OPERATOR: Invalid date literal supplied for DURING operator`. For any other window use an explicit range: `WHERE segments.date BETWEEN '2026-04-16' AND '2026-07-15'`. (⚠️ The "Non-Serving Keywords" template above uses `DURING LAST_180_DAYS` and will error as written — swap it to a `BETWEEN` range.)

---

## API Gotchas — Living Log

Append quirks here the moment you hit them, with the exact error string so future-you greps and finds it. Confirmed against Google Ads API v23.

### `change_event.changed_fields` lists a field even when its value is the default

On a `CREATE` operation, `changed_fields.paths` contains **every field set on the new
resource**, including booleans that are `false`. `negative` appears on every criterion
CREATE — positive keywords included. Classifying on the path is silently wrong:

```python
# WRONG — labels 302 positive keywords as negatives
is_negative = "negative" in ev.changed_fields.paths

# RIGHT — read the value off the resource
res  = ev.old_resource if op == "REMOVE" else ev.new_resource
crit = res.ad_group_criterion   # or .campaign_criterion
is_negative = bool(crit.negative)
```

Verified 2026-07-29: `ad_group,criterion_id,keyword.match_type,keyword.text,negative,
resource_name,status` → `negative=False`, `keyword.text="licensed landscaping company"`.
Use `changed_fields` to know *which* fields moved; use `old_resource`/`new_resource` for
*what they moved to*. On `REMOVE`, `new_resource` is empty — read `old_resource`.

### Relative date literals are a fixed enum (see Date Range Reference above)
Only `TODAY`, `YESTERDAY`, `LAST_7_DAYS`, `LAST_14_DAYS`, `LAST_30_DAYS`, `THIS_MONTH`, `LAST_MONTH`, and the `THIS_WEEK_*` / `LAST_WEEK_*` variants exist. Everything else → `BETWEEN 'YYYY-MM-DD' AND 'YYYY-MM-DD'`.

### `change_event` / `change_status` require a FINITE (bounded) date range
Filtering with only a `>=` (or no date filter) fails:
`CHANGE_DATE_RANGE_INFINITE — request is missing filters on ...date_time or is filtering with an infinite range.`
You must supply **both** a lower and upper bound. Additional rules:
- `change_event`: last **30 days only**, requires a `LIMIT` (≤10,000), full detail (old/new resource, changed_fields, user_email). Datetime format needs seconds: `'2026-06-15 00:00:00'`.
- `change_status`: **no age limit**, lighter detail (resource_type/status/date), still needs both bounds. Field is `last_change_date_time`.
```sql
-- change_event (30d window, both bounds + LIMIT)
WHERE change_event.change_date_time >= '2026-06-15 00:00:00'
  AND change_event.change_date_time <= '2026-07-15 23:59:59'
ORDER BY change_event.change_date_time DESC LIMIT 500
```

### Local Services Ads (LSA) have NO keywords or search terms
LSAs match on **service categories**, not queries. There is no `search_term_view` / `keyword_view` equivalent. Pull leads from `local_services_lead` (`category_id`, `service_id`, `lead_type`, `lead_status`, `creation_date_time`). Notes:
- `service_id` is frequently **empty** (lead came in under the category without a tagged service).
- The LSA campaign shows up in a normal `campaign` query as `advertising_channel_type = 'LOCAL_SERVICES'` — that's where spend/budget live. On some accounts (e.g. a landscaping account) LSA and Search share one CID, so exclude `LOCAL_SERVICES` when summing Search spend to avoid double-counting.

### proto-plus default vs. "no data"
With `use_proto_plus=True`, an absent numeric metric reads back as `0.0`, indistinguishable from a real zero. For impression-share fields (which are legitimately 0.0 when there's no data), treat `0.0` as "no data" rather than "0% IS." See `lead_metrics.impression_share`.

### AI Max impact CANNOT be measured by summing `AI_MAX_*` rows
`segments.search_term_match_source` on `search_term_view` returns `ADVERTISER_PROVIDED_KEYWORD`, `AI_MAX_BROAD_MATCH`, `AI_MAX_KEYWORDLESS`, `DYNAMIC_SEARCH_ADS`, `PERFORMANCE_MAX`, `VERTICAL_ADS_DATA_FEED`, `UNKNOWN`. It is the right field for attribution, but **it materially understates AI Max's footprint**: AI Max also loosens matching on your *existing* keywords, and that expanded traffic is still labelled `ADVERTISER_PROVIDED_KEYWORD`.

Verified on a health ecommerce account (AI Max off 2026-07-17, generic Lyme Guide campaign), 10d either side:

| | Impr | Clicks | Conv |
|---|---|---|---|
| Pre — `ADVERTISER_PROVIDED_KEYWORD` | 62,273 | 3,229 | 3.6 |
| Pre — both `AI_MAX_*` sources | 3,289 | 242 | 0.0 |
| Post — `ADVERTISER_PROVIDED_KEYWORD` | 4,373 | 342 | 44.8 |

Labelled AI Max was 4% of account spend, yet turning it off cut *advertiser-keyword* impressions by 93%. **To size AI Max, run a real pre/post on the toggle date — do not trust the labelled share.** Related: AI Max toggles do NOT appear in Change History, so the toggle date must be logged manually at the time of the change.

Other segments available on `search_term_view` (19 total): `ad_network_type`, `ad_sub_network_type`, `conversion_action{,_category,_name}`, `date`/`week`/`month`/`quarter`/`year`/`day_of_week`/`month_of_year`, `device`, `external_conversion_source`, `keyword.ad_group_criterion`, `keyword.info.match_type`, `keyword.info.text`, `search_term_match_source`, `search_term_match_type`.

⚠️ Adding `segments.keyword.info.*` **silently drops** Shopping/PMax rows (no keyword exists), e.g. 98,313 → 1,046 rows on VP Primary. Omit it when you need full coverage.

### `segments.new_versus_returning_customers` accepts conversion metrics ONLY
Selecting it alongside `metrics.impressions`/`clicks`/`cost_micros` fails:
`Cannot select the following segments because at least one unsupported metric is found in SELECT or WHERE clause: 'segments.new_versus_returning_customers' (unsupported metrics: 'clicks', 'cost_micros', 'impressions').`
Use `metrics.all_conversions`, `all_conversions_value`, `conversions`, `conversions_value`. Consequence: **there is no cost split by new vs returning**, so no CPA or ROAS by segment — conversion counts and value only.

### `campaign_audience_view` rejects bare `criterion_id`
`Unrecognized field in the query: 'criterion_id'.` Select `campaign_audience_view.resource_name` and parse it (`customers/{cid}/campaignAudienceViews/{campaignId}~{criterionId}`) instead.

---


### Rows where EVERY selected metric is zero are silently dropped

Found on an ecommerce account (2026-09-01) building the PMax label classifier. The API returns no row at
all when all the metrics you SELECTED are zero — it does not zero-fill. Which rows vanish
therefore depends on which metrics you asked for, so two queries over the same resource and
date range legitimately return different product sets.

```sql
-- 2,674 distinct core products
SELECT segments.product_item_id, campaign.name,
       metrics.clicks, metrics.conversions_value, metrics.cost_micros
FROM shopping_performance_view WHERE segments.date BETWEEN '2025-12-24' AND '2026-08-31'

-- 6,620 distinct core products — same range, one extra field
SELECT segments.product_item_id, campaign.name, metrics.impressions,
       metrics.clicks, metrics.conversions_value, metrics.cost_micros
FROM shopping_performance_view WHERE segments.date BETWEEN '2025-12-24' AND '2026-08-31'
```

3,946 products differed; 3,718 of them had impressions but zero clicks AND zero cost, so the
first query had nothing non-zero to return them on.

**Rule:** when the question is "which entities exist / served", always SELECT the widest metric
in the funnel — `metrics.impressions` for shopping and search. Reserve narrow metric sets for
"which entities spent". Getting this wrong silently under-counts the denominator by ~60% and
every downstream rate is then computed against the wrong base.

## Key Field Notes

### Micros Conversion
The API returns monetary values in **micros** (1,000,000 = $1):
```
50000000 micros = $50.00
1234567 micros = $1.23
```
Always divide by 1,000,000 when displaying to users.

### Impression Share Returns Decimals
The API returns impression share as **decimals (0.0 - 1.0)**, NOT percentages:
- API value `0.2464` = **24.64%** actual impression share
- Always multiply by 100 when displaying

### Metrics Require Date Segmentation
Any query with `metrics.*` fields MUST include a `WHERE segments.date` clause. Without it, the query will fail.

### Impression Share is Search/PMax Only
`search_impression_share`, `search_budget_lost_impression_share`, and `search_rank_lost_impression_share` are only available for Search and Performance Max campaigns.

### AND vs OR
GAQL doesn't support `OR`. Use `IN` instead:
```sql
-- Wrong
WHERE campaign.status = 'ENABLED' OR campaign.status = 'PAUSED'

-- Correct
WHERE campaign.status IN ('ENABLED', 'PAUSED')
```
