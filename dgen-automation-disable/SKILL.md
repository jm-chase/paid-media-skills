---
name: "DGen Automation Disable"
description: "Bulk-disable Demand Gen ad-level asset automation settings. Auto-invoke when user says 'disable dgen automation', 'fix dgen asset settings', 'turn off dgen auto assets', or 'dgen automation fix'."
allowed-tools: [Bash, Read]
---

# DGen Ad-Level Automation Disable Skill

**Purpose:** Programmatically turn OFF all ad-level asset automation settings for Demand Gen ads across accounts.

**Type:** Mutation skill (requires MutationGuard approval)

**Status:** Production

## Auto-Invoke When

- "disable dgen automation"
- "fix dgen asset settings"
- "turn off dgen auto assets"
- "dgen automation fix"
- "fix demand gen automation"

## Background

Demand Gen asset automation operates at the **AD level** (not campaign level like PMax). These settings auto-generate creative variations which can reduce quality control for managed accounts.

### Settings Controlled

**DemandGenMultiAssetAd:**
| Setting | Description | Default |
|---------|-------------|---------|
| GENERATE_DESIGN_VERSIONS_FOR_IMAGES | Adds design elements to images | ON |
| GENERATE_VIDEOS_FROM_OTHER_ASSETS | Generates videos from images/text | ON |

**DemandGenVideoResponsiveAd:**
| Setting | Description | Default |
|---------|-------------|---------|
| GENERATE_VERTICAL_YOUTUBE_VIDEOS | Converts horizontal to vertical | ON |
| GENERATE_SHORTER_YOUTUBE_VIDEOS | Shortens videos | ON |
| GENERATE_LANDING_PAGE_PREVIEW | Landing page preview in ads | OFF (but found ON in many accounts) |

## Claude MutationGuard Workflow (MANDATORY)

**Claude MUST follow this protocol. NEVER pipe "yes" or bypass confirmation.**

### Step 1: Run Dry-Run Preview

```bash
cd google-ads-mcp && set PYTHONPATH=. && python queries/fix_dgen_ad_automation.py --all
```

Show the full output to the user.

### Step 2: Present MutationGuard Preview

After showing dry-run results, present:

```
================================================================================
MUTATION GUARD - DRY-RUN PREVIEW
================================================================================

Operation: DISABLE_DGEN_AUTOMATION
Scope: [N] accounts, [N] ads, [N] settings
Description: Disable all DGen ad-level asset automation settings

================================================================================
TO PROCEED WITH THIS CHANGE:
================================================================================

Step 1: Respond with:
  "Claude, I approve [APPROVAL_CODE], unlock and ready to post"

(Or say 'cancel' to abort)
================================================================================
```

### Step 3: Wait for User Approval

User must say: `"Claude, I approve APPROVE-XXXXXXXX-XXXXXX, unlock and ready to post"`

Verify the approval code matches. If not, reject.

### Step 4: Wait for POST NOW

Present confirmation and wait for user to say: `POST NOW`

### Step 5: Execute with Approval Code

```bash
cd google-ads-mcp && set PYTHONPATH=. && python queries/fix_dgen_ad_automation.py --all --execute --approval-code APPROVE-XXXXXXXX-XXXXXX
```

### Step 6: Confirm Logging

Verify output shows both logs were written:
- Local: `google-ads-mcp/logs/mutations_log.jsonl`
- Sheet: Mutations Log Google Sheet

## Arguments

| Argument | Description |
|----------|-------------|
| `<search>` | Search for account by name |
| `--cid <id>` | Target specific Customer ID |
| `--all` | Process all accounts |
| `--portfolio <name>` | Filter: "Portfolio A", "Portfolio B" |
| `--execute` | Execute changes (default: dry-run) |
| `--approval-code <code>` | MutationGuard pre-approved code (skips interactive prompt) |
| `--verify` | Re-query after execution to confirm |

## Safety Mechanisms

1. **Dry-run is default** - No `--execute` = no changes
2. **Approval code required** - Must type exact approval code (not just "yes")
3. **MutationGuard integration** - `--approval-code` for Claude-mediated flows
4. **Profile lock** - Must have valid Google Ads API credentials
5. **Per-account error handling** - One failure doesn't stop batch
6. **Dual logging** - All mutations logged locally AND to Google Sheets

## Mutation Logging

Every execution is logged to two locations:

### Local Log
- **Path:** `google-ads-mcp/logs/mutations_log.jsonl`
- **Format:** JSON Lines (machine-readable)
- **Also:** Human-readable summary in `mutations_summary.txt`

### Google Sheets Log
- **Sheet ID:** `[SHEET_ID]`
- **URL:** Configure mutations_log_sheet in config/sheet-ids.yaml
- **Columns:** Timestamp, Account, CID, Action Type, Details, Success, Error, Approval Code

### What Gets Logged
- Account name and CID
- Number of ads updated
- Settings changed (by ad type)
- Success/failure status
- Approval code for traceability

## Critical Implementation Note

**Replacement behavior:** When updating `ad_group_ad_asset_automation_settings`, you must specify ALL settings you want to keep. If you only specify one setting, others reset to defaults (OPTED_IN).

The script handles this by always setting ALL applicable settings for each ad type.

## Script Location

**Path:** `google-ads-mcp/queries/fix_dgen_ad_automation.py`

## Related Documentation

- Phase 2 test script: `google-ads-mcp/queries/test_phase2_dgen.py`
- Settings audit: see mutation-safety skill
- Mutation safety: `.claude/skills/mutation-safety/SKILL.md`

---

**Created:** 2026-01-29
**Updated:** 2026-01-29 (added MutationGuard integration + dual logging)
