---
title: "Alien Parser — Extract YARA Matches from THOR JSON Logs"
date: 2026-06-29
draft: false
tags: ["dfir", "threat-hunting", "yara", "tools", "python"]
description: "A CLI tool that extracts YARA match results from THOR JSON logs and converts them into clean, filterable CSV files for incident response workflows."
---

## Overview

When running THOR scans during incident response or threat hunting engagements, the resulting JSON logs can be massive and difficult to triage quickly. **Alien Parser** solves this by extracting YARA rule matches and converting them into clean, filterable CSV files — so you can focus on the findings that matter.

**GitHub:** [mzalzahrani/Alien-parser](https://github.com/mzalzahrani/Alien-parser)

## Features

- Extract YARA matches from THOR JSON logs
- Convert results to CSV for easy analysis in Excel or pandas
- Filter matches by minimum score threshold (0–100)
- Filter by specific rule names
- Generate JSON summary reports with host statistics
- No external dependencies — standard Python 3.7+ only

## Usage

Basic extraction:

```bash
python yaraconvert.py -i thor_log.json -o results.csv
```

Filter high-priority matches (score ≥ 80):

```bash
python yaraconvert.py -i thor_log.json -o high_priority.csv --min-score 80
```

## Why I Built This

During threat hunting engagements, THOR produces detailed JSON output but triaging hundreds of YARA hits manually is slow. This tool lets you pipe results directly into a spreadsheet or further scripting — cutting triage time significantly.

## Requirements

- Python 3.7+
- No external libraries required
