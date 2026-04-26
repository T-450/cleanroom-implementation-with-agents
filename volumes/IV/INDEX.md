# Volume IV — Index

A one-page map of every artefact in Volume IV. Use this as the starting
navigation aid when reading the chapters.

## Chapters

- `chapters/chapter18_llm_specification_extraction.md`
- `chapters/chapter19_automated_behavioral_testing.md`
- `chapters/chapter20_multi_agent_orchestration.md`
- `chapters/chapter21_ai_driven_code_generation.md`
- `chapters/chapter22_verification_and_validation_ai.md`

## Schemas (the data formats)

| Schema                                           | Used by                                                      |
| ------------------------------------------------ | ------------------------------------------------------------ |
| `schemas/spec-artifact.schema.json`              | spec-extractor, test-generator, tdd-implementer, parity-runner |
| `schemas/parity-report.schema.json`              | parity-oracle MCP, parity-runner, divergence-triager, certifier |
| `schemas/audit-event.schema.json`                | audit_logger.py, audit-log MCP, /audit-replay                |
| `schemas/tool-policy.schema.json` + `tool-policy.json` | firewall.py                                            |
| `schemas/cost-ledger.schema.json`                | cost_cap.py, audit-log MCP                                   |

## Diagrams

- `diagrams/volume-iv-concept-map.md` — five-chapter overview
- `diagrams/reference-impl-component-diagram.md` — subagents ↔ skills ↔ MCPs
- `diagrams/information-firewall-sequence.md` — denied-Read sequence
- `diagrams/pipeline-workflow-sequence.md` — `/run-cleanroom-pipeline` flow
- `diagrams/delegation-tree-feature.md` — coordinator's delegation tree
- `diagrams/hook-lifecycle-timeline.md` — when each hook fires
- `diagrams/coordinator-information-wall.md` — prose-level firewall
- `diagrams/cicd-integration.md` — nightly CI deployment

## Reference implementation: `reference-impl/redis-cleanroom/`

### Top-level

- `README.md` — runbook
- `CLAUDE.md` — project charter
- `CLAUDE.md.observation`, `CLAUDE.md.implementation`,
  `CLAUDE.md.verification` — per-team overlays
- `.claude/settings.json` — hooks, permissions, env, model defaults
- `.mcp.json` — MCP server registration (spec-store, parity-oracle,
  audit-log)
- `justfile` — task runner: `bootstrap`, `smoke`, `full-pipeline`,
  `verify-firewall`, `verify-cost-cap`, `doctor`, `clean`

### Subagents (`.claude/agents/`)

Coordinator/triage/escalation, Observation (3), Test generation (2),
Implementation (4), Verification (3). See chapter 20 §1 for the full
delegation tree.

### Slash commands (`.claude/commands/`)

`/discover-command`, `/generate-tests`, `/implement-command`,
`/verify-parity`, `/audit-replay`, `/run-cleanroom-pipeline`.

### Skills (`.claude/skills/`)

`tdd-loop`, `property-based-test`, `parity-diff`,
`behavioral-spec-extraction`, `audit`, `cost-cap`.

### Hooks (`hooks/`)

| Script              | Event             | Purpose                                       |
| ------------------- | ----------------- | --------------------------------------------- |
| `firewall.py`       | PreToolUse / Task | File-level RBAC + Task-prompt token grep      |
| `audit_logger.py`   | PostToolUse       | Append every tool call to the audit queue     |
| `cost_cap.py`       | PreToolUse        | Refuse if remaining budget < estimate         |
| `redactor.py`       | UserPromptSubmit  | Refuse pasted original-source fingerprints    |
| `notifier.py`       | Stop / SubagentStop | Emit resume events                          |

### MCP servers (`mcp-servers/`)

- `spec-store/` — CRUD spec artifacts; resources: `spec://command/<id>`
- `parity-oracle/` — Differential runner; tool: `run_corpus`,
  `replay_case`
- `audit-log/` — Append-only SQLite (WAL); resources:
  `audit://session/<id>`, `audit://policy-denials`,
  `audit://task-prompt-redactions`

### Worked-example tree

`original/`, `specs/`, `specs-raw/`, `transcripts/observation/`,
`tests/parity/`, `tests/properties/`, `src/`, `reports/`,
`.github/workflows/cleanroom-ci.yml`.
