# Ransomware Victim Tracker

**Last updated:** 2026-10-13T13:51:22.324075+00:00

## Overview

- **Total unique victims:** 0
- **Groups represented:** 0

## Victims by Ransomware Group

| Rank | Ransomware Group | Victims |
| ---: | --- | ---: |
| - | No victim records yet | 0 |

## Victims by Status

| Status | Victims |
| --- | ---: |

## Victims by Country

| Country | Victims |
| --- | ---: |

## Victims by Sector

| Sector | Victims |
| --- | ---: |

---

This dashboard is automatically generated from `data/statistics.json`.



I am a beginner with GitHub, and I am building a ransomware OSINT project in my GitHub repository:

https://github.com/MewtwoMalware/Ransomware-OSINT-Tracker

Please continue helping me step-by-step from where my previous ChatGPT conversation stopped.

IMPORTANT INSTRUCTIONS

Give me ONE step at a time.
Wait for me to confirm I completed each step before giving me the next one.
Use beginner-friendly language and tell me exactly where to click in GitHub.
Do not overwhelm me with multiple steps at once.
Do not assume I know how GitHub works.
Do not skip steps or invent progress that has not been confirmed.
Do not commit changes unless the current step specifically requires it.
Preserve my existing files and functionality.
My project

My repository contains ransomware-group .md files, each documenting a chronological OSINT timeline of events, such as arrests, leaks, TTPs, sanctions, infrastructure, victims, and other developments.

The repository also contains an existing project/workflow called Check OSINT Data, which is a work-in-progress scraper intended to scrape leak sites and articles and update the ransomware-group timeline files.

Do not modify, interfere with, or replace that existing scraper or its workflow.

Separate victim-tracking system

We have built a separate victim-counting system that must remain independent of the existing scraper and timeline files.

Current structure:

.github/workflows/victim-tracker.yml
data/victims.json
data/victim_aliases.json
data/victim_queue.json
data/statistics.json
scripts/victim_tracker.py
scripts/generate_victim_dashboard.py
victim-dashboard.md

The victim-tracker workflow:

Runs manually using workflow_dispatch.
Runs automatically daily using cron.
Has permissions: contents: write.
Runs scripts/victim_tracker.py.
Runs scripts/generate_victim_dashboard.py.
Displays the generated statistics.
Commits generated changes when necessary.
Does not modify my existing ransomware timeline .md files.

The GitHub Actions workflow has previously run successfully with green checkmarks.

Database and design

data/victims.json currently contains no victims:

{"last_updated": null, "victims": []}

data/victim_queue.json currently contains no pending records:

{"pending": []}

A fake Example Corporation test record was previously used but has been removed. Do not reintroduce fake victims.

The alias system is intended to prevent duplicate organizations from being counted separately.

The statistics and dashboard track total unique victims, groups represented, victims by ransomware group, status, country, and sector.

The eventual system should support statuses such as claimed, confirmed, disputed, removed, and unknown, as well as confidence levels of high, medium, low, and unknown.

The long-term goal is to accept standardized victim records from a future scraper integration, without modifying the existing scraper. The victim tracker should handle ingestion, normalization, deduplication, aliases, statistics, and dashboard generation.

The system must not automatically count every company mentioned in an article as a victim. It must distinguish actual victim claims from contextual mentions, arrests, law enforcement, sanctions, infrastructure, malware, affiliates, security researchers, and other unrelated entities.

Work completed so far

Step 41: The pending-record report helper was saved in GitHub.

Step 42: We connected the helper inside main() in scripts/victim_tracker.py by adding:

pending = load_queue()

print_review_summary(pending)
print_pending_records(pending)


The new line was added immediately after print_review_summary(pending).

Step 43: We reopened victim_tracker.py and confirmed those lines were present.

Step 44: We manually ran the existing Ransomware Victim Tracker workflow through GitHub Actions.

Step 45 — CURRENT POSITION: The user confirmed that the workflow run was green and successful.

We have not yet checked the workflow logs to confirm the pending-record report output.

Resume here

Continue at Step 45, without repeating completed steps.

Give me only the next action needed to finish Step 45:

Tell me exactly how to open the successful workflow run logs.
Guide me to expand the Run victim tracker step.
Ask me to look for the pending-record report, which should indicate that there are no records awaiting review because the queue is empty.

Wait for my response before giving me another step.

Do not assume the expected message appeared just because the workflow succeeded. We still need to inspect the logs.

After Step 45 is verified, help me plan the next step based on the existing project and code. Do not invent a Step 46 without first explaining what we are trying to accomplish.

Remember: one step at a time, beginner-friendly, and do not interfere with the existing scraper or ransomware timeline files.
