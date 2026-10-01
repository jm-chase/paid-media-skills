# Anomaly Detection Skill

Proactive account health monitoring across all registered clients. Runs checks against
ppc_history.db and emails a digest to the configured recipient when anything warrants
attention. Sends nothing on clean days.

## When to Invoke

- Manually: "run anomaly check", "check for issues", "any flags today"
- Scheduled: daily via n8n or cron (see Scheduling section below)
- Before a brief session: run to confirm no active fires before building monthly context

## What It Checks

| Check | Trigger | Severity |
|-------|---------|----------|
| CPA spike | 7-day CPA > 30-day rolling by 25%+ (min $50 spend, min $10 CPA) | Critical/Warning |
| Conversion gap | 3-day avg < 25% of 14-day rolling avg (>75% drop) | Critical |
| Zero spend | $0 spend for 2+ days when 14-day avg > $30/day | Critical |
| Budget burn | MTD pacing >15% over or <25% under expected | Warning |

**Skipped checks by client type:**
- LSA-only clients (for example an electrician on Local Services only): skip CPA spike, conversion gap, zero spend — they have no GA campaigns
- Ecom clients (for example a pet-supplement or apparel store): skip CPA spike — use ROAS check instead (future)

**De-duplication:** Same alert type for same client suppressed for 3 days after first fire.

## Commands

```bash
# Run all checks — email digest if anything flagged
py anomaly_detector.py

# Preview without emailing or logging (safe to run anytime)
py anomaly_detector.py --dry-run

# Ignore de-duplication — force send even if recently alerted
py anomaly_detector.py --force
```

## Output

**No flags:** No email sent. Log line: "All clean — no alerts to send."

**Flags found:** Single digest email to the configured recipient with:
- One section per flagged client
- Severity badge (CRITICAL / WARNING)
- Headline with the actual numbers
- 1-2 sentence detail explaining what happened
- Suggested next action (specific, not generic)

Subject line format: `[N Flags] Account Anomaly Digest — June 9`

## Reading the Digest

**CPA spike:** First check change history (what changed?), then search terms (quality shift?), then conversion tracking (is it still firing?). Don't adjust bids until cause is identified.

**Conversion gap:** Almost always a tracking issue. Check GTM, check conversion action status in Google Ads. Run `conversion-tracking-health` skill for detail.

**Zero spend:** Check campaign status first (paused?), then billing, then budget exhaustion mid-month.

**Budget burn (over-pacing):** Review daily budget caps. Consider pausing lower-priority campaigns. Don't just cut budgets — find which campaign is over-spending.

**Budget burn (under-pacing):** Check impression share. If budget-constrained IS showing, the budget needs to increase or targeting needs to tighten to fit within budget.

## Alert Log

All sent alerts are logged to `anomaly_log` table in `ppc_history.db`:
- `client_slug`, `anomaly_type`, `severity`, `headline`, `detail`
- `alerted` flag (1 = email was sent)
- `detected_at` timestamp

Query to see recent alerts:
```sql
SELECT detected_at, client_slug, anomaly_type, severity, headline
FROM anomaly_log ORDER BY detected_at DESC LIMIT 20;
```

## Scheduling

To run daily automatically:

**Via n8n:** Create a Cron trigger workflow at 7:00 AM that runs:
```
py ~/Projects/ppc-management/anomaly_detector.py
```

**Via Windows Task Scheduler:**
```
Action: py anomaly_detector.py
Working dir: ~/Projects/ppc-management/
Trigger: Daily at 7:00 AM
```

**Via Claude schedule skill:**
```
/schedule "run py anomaly_detector.py in ~/Projects/ppc-management/ daily at 7am"
```

## Thresholds (current)

| Check | Threshold | Rationale |
|-------|-----------|-----------|
| CPA spike | +25% over 30-day rolling | Meaningful shift without over-alerting on normal variation |
| Min spend for CPA check | $50 | Ignore low-spend days that produce statistical noise |
| Min CPA for CPA check | $10 | Ecom micro-conversions at $1-2 CPA produce meaningless % swings |
| Conversion gap | >75% drop vs 14-day rolling | James's specified threshold |
| Min baseline for conv gap | 1 conv/day avg | Only check accounts with meaningful conversion volume |
| Zero spend | 2+ days with $0, avg >$30/day | One bad day can happen; two consecutive is a signal |
| Budget over-pacing | >15% above expected MTD | Within 15% is acceptable variation |
| Budget under-pacing | >25% below expected MTD | More tolerance on underspend than overspend |
| Pacing staleness | >4 days | Skip budget check if sync data is too old |
| De-duplication | 3 days | Same alert won't re-fire for 3 days |

To adjust any threshold, edit the constants at the top of `anomaly_detector.py` or the
threshold values within the individual check functions.
