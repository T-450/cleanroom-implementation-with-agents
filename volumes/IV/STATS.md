Volume IV Statistics
====================

Chapter List:
- chapter18_llm_specification_extraction.md  (25 pp / ~1,625 lines)
- chapter19_automated_behavioral_testing.md  (20 pp / ~1,300 lines)
- chapter20_multi_agent_orchestration.md     (20 pp / ~1,300 lines)
- chapter21_ai_driven_code_generation.md     (20 pp / ~1,300 lines)
- chapter22_verification_and_validation_ai.md (15 pp /  ~975 lines)

Target: 100 pages (~50,000-60,000 words).
Density calibration: 65 lines per page (matches Volume VI ch27 = 1,458
lines / 20 pp and Volume VII chapters at 800-1,200 lines / 20 pp).

Total target: ~6,500 lines of chapter prose + a runnable reference
implementation under reference-impl/redis-cleanroom/.

Each chapter dissects part of the same worked example (Redis RESP
subset). Chapter excerpts code from the reference impl rather than
re-listing whole files; full sources are at
volumes/IV/reference-impl/redis-cleanroom/.

Reference implementation file count (approximate):
- 14 subagent .md files
-  6 slash command .md files
-  6 SKILL.md files
-  5 hook .py scripts
-  3 MCP server packages (spec-store, parity-oracle, audit-log)
-  4 CLAUDE.md files (base + 3 overlays)
-  1 justfile
-  1 .claude/settings.json + 1 .mcp.json
-  Rust crate skeleton (src/, tests/, Cargo.toml)
-  GitHub Actions workflow

Schemas: 5 JSON Schema files in volumes/IV/schemas/.
Diagrams: 8 Mermaid/PlantUML files in volumes/IV/diagrams/.
