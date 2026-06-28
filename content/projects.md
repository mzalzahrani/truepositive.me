---
title: "Projects"
layout: "single"
url: "/projects/"
summary: "projects"
---

## Tools & Projects

---

### Alien Parser

**DFIR tool for extracting YARA matches from THOR JSON logs**

A CLI utility for DFIR analysts and threat hunters. Processes THOR scan output and converts YARA rule matches into clean, filterable CSV files — cutting triage time during incident response.

**Features:**
- Extract YARA matches from THOR JSON logs
- Filter by score threshold (0–100)
- Filter by specific rule name
- Generate JSON summary reports with host statistics
- No external dependencies (Python 3.7+ standard library only)

**Usage:**
```bash
# Basic extraction
python yaraconvert.py -i thor_log.json -o results.csv

# High priority only (score >= 80)
python yaraconvert.py -i thor_log.json -o high_priority.csv --min-score 80

# Filter by rule name
python yaraconvert.py -i thor_log.json -o results.csv --rule-name RULE123
```

**Output fields:** timestamp, hostname, file path, hashes (MD5/SHA1/SHA256), YARA rule name, tags, author, matched data, offset, context.

[View on GitHub](https://github.com/mzalzahrani/Alien-parser) — MIT License
