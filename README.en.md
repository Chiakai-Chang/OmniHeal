[繁體中文](README.md) | English

# OmniHeal

**Zero-install AI project health checker.**

Git clone OmniHeal into any project, then tell any AI coding agent:
> "Please read @OmniHeal/ to get started"

The agent reads `LAUNCH.md` and autonomously completes the entire project scan and improvement recommendations.

---

## Why OmniHeal?

Existing linting / static analysis tools have three fundamental problems:

| Problem | Existing Tools | OmniHeal |
|---------|--------------|---------|
| **Installation overhead** | Requires `npm install`, `pip install`, CI setup | `git clone` and go — zero dependencies |
| **No resume on interrupt** | Restart from scratch, or no resume support | Task Queue architecture — resumes from first pending task |
| **Only finds problems** | Outputs 47 findings, developers don't know where to start | SWOT+TOWS analysis — outputs "fix today / this-week PR / next-quarter plan" action roadmap |

**The key difference:** OmniHeal doesn't just tell you "what's wrong" — it tells you "spend 2 person-days this week, fix these 3 things, and here's what happens if you don't."

---

## Getting Started: 2-Minute Setup + Fully Automatic

After launch, the agent runs a **one-time pre-flight confirmation** (Pre-flight Step 5), then the entire scan runs automatically.

| Phase | Do you need to be present? | Time estimate |
|-------|--------------------------|--------------|
| Pre-flight confirmation (business domain — only interactive step) | ✅ Once, ~2 minutes | Leave after answering |
| Phase 0 → Phase 1 → Phase 1.5 (full scan) | ✗ Fully automatic | Minutes to hours (depends on project size) |

> **Recommendation:** After launching the Agent, complete the pre-flight questionnaire (~2 minutes), then leave it to run overnight.
> If you leave immediately, the Agent will wait at the pre-flight confirmation — you'll need to answer in the morning to continue.

---

## Usage

**Step 1: Clone OmniHeal into your target project**

```bash
cd your-project/
```

```bash
git clone https://github.com/Chiakai-Chang/OmniHeal.git
```

**Step 2: Tell any AI Agent (Claude, Copilot, etc.)**

```
Please read @OmniHeal/ to get started
```

Or more specifically:

```
Please read @OmniHeal/, run a code health check on ./src using the code_lint skill
```

The agent takes over from here.

---

## What You Get

After the scan completes, OmniHeal produces two documents:

### `summary.md` (Audit snapshot)
```
Scan time: 2026-05-19 | 157 files total | 8 high-risk findings
Skipped: 3 (2 encoding issues, 1 oversized binary)
⚠️ AI Limitation Notice: This report is based on static analysis and does not guarantee exhaustive coverage
```

### `action_plan.md` (Action roadmap)
```
⚡ Fix Today (high threat × low effort)
- [ ] config.py:12 — Hardcoded API Key (~30 min)
  Risk if ignored: Credential leak enables third-party service access

📅 This Week's PR (weakness clusters × opportunity)
- [ ] src/db/ SQL injection systematic fix (resolves #1, #4, #7 — same root cause)
  Reference pattern: src/auth/ already correctly implemented

💪 Maintain Strengths
- src/auth/: zero high findings → use as reference template for other modules
```

---

## How It Works

| Phase | What it does |
|-------|------------|
| Pre-flight | Detects framework conventions, CI toolchain, business domain risk level |
| Phase 0 | Scans directory, MECE governance questions, generates Task Queue |
| Phase 1 | Consumes queue, scans file by file, 3-Strike Protocol ensures no interruption |
| Phase 1.5 | SWOT analysis → produces `summary.md` + `action_plan.md` |

---

## Available Skills

| Skill | Target |
|-------|--------|
| `skill_code_lint` | Code files: naming, security risks, outdated patterns |
| `skill_log_parse` | Log files: format inconsistencies, high-frequency errors, anomalies |
| `skill_text_align` | Transcripts: AI transcription errors, homophone substitutions |

---

## Design Foundation: Distilled from 14 Repos

Every design decision in OmniHeal has a source. Key adoptions:

| Source | Adopted Design | Problem Solved |
|--------|--------------|--------------|
| [Manus AI / planning-with-files](https://github.com/OthmanAdi/planning-with-files) | 3-file progress structure, 3-Strike Protocol, Reboot Test | Seamless recovery after agent restart |
| [Anthropic / claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | Confidence threshold (≥80), false-positive-first design | Avoid "47 findings, 30 are false positives" |
| [ECC (Hackathon Winner)](https://github.com/affaan-m/everything-claude-code) | Analysis depth levels (fast/standard/deep), Context Budget gate, Phase 1.5 De-Sloppify | Consistent scan quality across large projects |
| [Continuous-Claude-v3](https://github.com/parcadei/Continuous-Claude-v3) | Claim Verification (✓ VERIFIED / ? INFERRED) | Research shows 80% of AI code claims are output without reading source |
| [PageIndex + llm-wiki-plugin](https://github.com/VectifyAI/PageIndex) | Index-first then deep-dive, dual-layer findings structure, surgical append | No blind line-by-line scanning of large projects |
| [Understand-Anything](https://github.com/Lum1104/Understand-Anything) | Determinism-first (probe.py for structure extraction, LLM for semantic judgment) | No wasted LLM tokens on rule-computable tasks |
| [ARIS](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep) | Task Queue checkpoint design, last_updated timestamps | Robust overnight unattended long-running scans |
| [PUA + YES.md](https://github.com/tanweai/pua) | Pattern Alert (iceberg principle), Level-2 direction self-check | Proactively check same-type files when one problem is found |
| [AIBDD](https://github.com/Waterball-Software-Academy/aixbdd) | D/S/I verb model, Atomic Finding principle | One problem, one location, one recommendation per finding |
| [MECE-ECS](https://github.com/Chiakai-Chang/mece-ecs) | MECE governance question design | Phase 0 governance questions: no overlap, no gaps |
| [Andrej Karpathy Principles](https://github.com/multica-ai/andrej-karpathy-skills) | Think Before Coding / Simplicity First / Surgical Changes | External validation of OmniHeal's design philosophy |

> Full research decision log: [`reference/RATIONALE.md`](reference/RATIONALE.md) (14 repos, each with adoption items and rejection reasons)

---

## Core Design Principles

- **Zero install**: Only dependency is Python 3 (standard library only)
- **Never interrupt**: 3-Strike Protocol ensures a single file failure doesn't stop the entire scan
- **Precision-first**: Only outputs `✓ VERIFIED` (source code read) findings with confidence ≥ 80
- **Resumable**: Task Queue architecture — checkpoint = first incomplete task in queue, no reliance on agent memory
- **Consulting, not Audit**: SWOT+TOWS analysis upgrades output from "47-problem list" to "which 3 to fix this week"

---

## License

[MIT](LICENSE) © 2026 Chiakai Chang
