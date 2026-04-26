# Volume IV — AI-Enhanced Clean Room

> **One-line:** This volume ships a runnable, end-to-end clean-room workflow
> built natively from Claude Code primitives (subagents, skills, slash
> commands, hooks, MCP servers) and walks through every artefact in five
> chapters.

## Differentiation contract

Volume VI describes the **abstract** patterns of multi-agent clean-room
workflows in prose and pseudo-Python. Volume IV is its **concrete
realization**: the same patterns shipped as runnable `.md`, `.json`, `.py`,
`.rs`, and `.toml` files under `reference-impl/redis-cleanroom/`. Every
chapter opens with a "Prerequisite reading" box pointing back at Volume VI.

| Volume VI (existing, prose)              | Volume IV (new, artifacts)                          |
| ---------------------------------------- | --------------------------------------------------- |
| *Describes* agent roles                  | *Ships* `.claude/agents/*.md` files                 |
| *Pseudo-Python* `delegate_task` examples | *Runnable* `Task`-tool calls from a real coordinator |
| *YAML* spec templates                    | JSON-Schema-validated `spec-artifact` files         |
| *Talks about* isolation                  | *Enforces* isolation via hook + coordinator contract |
| *Generic* patterns                       | *One* working example: `redis-cleanroom`            |

## Worked example

[`reference-impl/redis-cleanroom/`](reference-impl/redis-cleanroom/) — a
subset of the Redis RESP2 protocol re-implemented in Rust without the
implementation team ever reading the original `redis-server` source. Why
Redis: real legal motivation (RSAL/SSPL since 2024), no widely-used Rust
clean-room exists, and per-command granularity gives every chapter its own
naturally-sized worked sub-example.

## Chapters

| Ch | Title                                                | Pages | Lines (target) |
| -- | ---------------------------------------------------- | ----- | -------------- |
| 18 | LLM-Based Specification Extraction                   | 25    | ~1,625         |
| 19 | Automated Behavioral Testing                         | 20    | ~1,300         |
| 20 | Multi-Agent Orchestration                            | 20    | ~1,300         |
| 21 | AI-Driven Code Generation                            | 20    | ~1,300         |
| 22 | Verification and Validation with AI                  | 15    | ~975           |

## Reading order

1. `INDEX.md` — where everything lives.
2. `chapters/chapter18_llm_specification_extraction.md`.
3. Continue chapters 19 → 22 in order.
4. After each chapter, browse the relevant primitive in
   `reference-impl/redis-cleanroom/.claude/`.

## Schemas

The four file formats every artefact in this volume speaks:

- `schemas/spec-artifact.schema.json` — the Observation → Implementation
  handoff format.
- `schemas/parity-report.schema.json` — the differential report format.
- `schemas/audit-event.schema.json` — single row of the audit log.
- `schemas/tool-policy.schema.json` — file-level firewall policy.
- `schemas/cost-ledger.schema.json` — token/$ accounting.

## Diagrams

See `diagrams/` for the Mermaid/PlantUML architecture references used
throughout the chapters.

## How to run

```sh
cd reference-impl/redis-cleanroom
just bootstrap
just smoke   # discover + implement + verify PING end to end
```

See `reference-impl/redis-cleanroom/README.md` for the full prerequisite
list and the operational details.

## Cross-references in the wider wiki

- `concepts/ai-agent-methodologies.md` — the abstract methodology this
  volume realizes.
- `concepts/multi-agent-coordination.md` — the coordination patterns.
- `legal/legal-framework.md` — the legal foundations the firewall protects.
- `volumes/VI/` — the prose-level pattern catalogue.

---

*Volume IV, Clean Room Engineering Study Case.*
