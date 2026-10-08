# Ransomware Victim Tracker

**Last updated:** 2026-10-08T17:57:26.155471+00:00

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
I am new to GitHub and I am building a ransomware OSINT project on my GitHub repository:

https://github.com/MewtwoMalware/Ransomware-OSINT-Tracker

I need you to continue helping me step-by-step from where my previous ChatGPT conversation stopped.

IMPORTANT: I am a beginner with GitHub, so give me ONE step at a time and wait for me to confirm that I completed it before moving to the next step. Do not overwhelm me with many steps at once.

My existing project

My repository contains ransomware-group .md files. Each group file is a chronological OSINT timeline.

For example:

Black Basta
Source	Date	Details
Article	Date	Details about arrests, leaks, TTPs, sanctions, infrastructure, victims, etc.

My timeline files are meant to document events chronologically. They are NOT simply victim lists.

I also have another project/workflow in this same repository called Check OSINT Data, which is a work-in-progress scraper that will eventually scrape leak sites/articles and automatically update the ransomware-group .md timeline files.

DO NOT modify, interfere with, or replace that existing scraper/workflow.

What we just built

We created a completely separate victim-counting system.

The purpose is to eventually track ransomware victims across all my ransomware-group timeline files without changing those timeline files.

Current structure:

Ransomware-OSINT-Tracker/
│
├── .github/
│   └── workflows/
│       └── victim-tracker.yml
│
├── data/
│   ├── victims.json
│   ├── victim_aliases.json
│   ├── victim_queue.json
│   └── statistics.json
│
├── scripts/
│   ├── victim_tracker.py
│   └── generate_victim_dashboard.py
│
├── victim-dashboard.md
│
├── Black-Basta.md
├── Silent-Ransom-Group.md
├── ...
└── README.md

Current functionality

The GitHub Actions workflow is working.

victim-tracker.yml currently:

Runs manually with workflow_dispatch
Runs automatically once per day using cron
Has permissions: contents: write
Runs scripts/victim_tracker.py
Runs scripts/generate_victim_dashboard.py
Generates data/statistics.json
Commits generated changes back to GitHub
Does NOT modify my existing ransomware timeline .md files

The workflow is currently working with green checkmarks.

The important workflow structure is:

name: Ransomware Victim Tracker

on:
  workflow_dispatch:
  schedule:
    - cron: "0 3 * * *"

permissions:
  contents: write

jobs:
  update-victim-tracker:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.x"

      - name: Run victim tracker
        run: |
          python scripts/victim_tracker.py

      - name: Generate victim dashboard
        run: |
          python scripts/generate_victim_dashboard.py

      - name: Show generated statistics
        run: |
          cat data/statistics.json

      - name: Commit updated tracker data
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add data/ victim-dashboard.md
          git diff --cached --quiet || git commit -m "Update ransomware victim statistics"
          git push


The workflow originally had a permissions error, but we fixed it by adding:

permissions:
  contents: write


and enabling GitHub Actions read/write permissions.

Current victim database

data/victims.json currently starts empty:

{
  "last_updated": null,
  "victims": []
}


We previously used a fake Example Corporation record to test the system, but it was completely removed.

There should currently be NO fake victims in the database.

Current victim queue

data/victim_queue.json currently starts empty:

{
  "pending": []
}

Alias system

data/victim_aliases.json exists.

It is intended to prevent obvious duplicate organization names from being counted separately.

Statistics

data/statistics.json is automatically generated.

It tracks things such as:

total unique victims
total groups
victims by ransomware group
victims by status
victims by country
victims by sector
Dashboard

scripts/generate_victim_dashboard.py generates:

victim-dashboard.md


The dashboard currently displays:

Total unique victims
Groups represented
Victims by ransomware group
Victims by status
Victims by country
Victims by sector

The dashboard is now appearing in the root of the GitHub repository and is being generated successfully by GitHub Actions.

What the victim system is supposed to eventually do

The intended architecture is:

Ransomware OSINT evidence
        ↓
Potential victim identification
        ↓
Victim queue
        ↓
Duplicate/alias handling
        ↓
Victim database
        ↓
Statistics
        ↓
Dashboard


The system should NOT simply count every company mentioned in an article.

My timeline articles contain many things that are not victims, including:

arrests
threat actors
law-enforcement targets
sanctions
leaks
doxes
infrastructure
TTPs
malware
affiliates
cryptocurrency activity
security researchers
companies mentioned for context
historical events

Therefore victim identification needs to be deliberate.

Eventually I want to distinguish things such as:

claimed
confirmed
disputed
removed
unknown


and have confidence levels such as:

high
medium
low
unknown

Important design goal

I want this system to eventually work with my other scraper project WITHOUT modifying the scraper.

The scraper should eventually be able to output standardized victim records such as:

{
  "group": "Silent Ransom Group",
  "victim": "Victim Name",
  "date": "2026-10-08",
  "status": "claimed",
  "confidence": "high",
  "country": "United States",
  "sector": "Healthcare",
  "source": "https://example.com",
  "source_title": "Article title",
  "notes": ""
}


Then the victim tracker handles:

ingestion
normalization
deduplication
aliases
statistics
dashboard generation

This keeps the two projects separated.

##
