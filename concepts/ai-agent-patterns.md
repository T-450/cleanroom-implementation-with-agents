---
title: AI Agent Patterns
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [ai-agent, agent-patterns, autonomous-development, delegate-task, subagent-orchestration]
sources: []
---

# AI Agent Patterns for Clean Room Implementation

This page catalogs proven patterns for using AI agents in clean room implementation projects. These patterns have been validated through practical experience.

## Pattern Categories

### Category 1: Discovery Patterns

Patterns for discovering and documenting original system behavior.

### Category 2: Implementation Patterns

Patterns for implementing features using AI agents.

### Category 3: Verification Patterns

Patterns for verifying behavioral parity.

### Category 4: Coordination Patterns

Patterns for coordinating multiple AI agents.

---

## Discovery Patterns

### Pattern 1: Systematic API Probing

```
PATTERN_NAME: Systematic API Probing

PURPOSE:
  Discover all API endpoints and their behaviors

APPLICABILITY:
  When starting a clean room project
  When exploring unknown API surfaces

STRUCTURE:
  Agent: API Probing Agent
  Tools: browser, terminal, file
  Iterations: 20-30
  
  Workflow:
  1. Enumerate all known endpoints
  2. For each endpoint, probe with valid inputs
  3. Record response formats
  4. Probe with invalid inputs
  5. Record error responses
  6. Map all edge cases
  7. Generate specification document

OUTPUT:
  - API specification document
  - Request/response examples
  - Error condition catalog
  - pytest test cases

EXAMPLE:
  delegate_task(
      goal="Discover and document all API endpoints",
      context="""
      System: https://api.system.com/v1
      
      Deliverables:
      1. Complete API endpoint list
      2. Request/response schemas
      3. Error handling documentation
      4. Test cases for each endpoint
      
      Process:
      - Enumerate endpoints
      - Test normal cases
      - Test error cases
      - Document findings
      """,
      toolsets=['browser', 'file'],
      max_iterations=25
  )
```

### Pattern 2: State Machine Discovery

```
PATTERN_NAME: State Machine Discovery

PURPOSE:
  Discover state machine behavior and transitions

APPLICABILITY:
  When system has complex state
  When behavior depends on state

STRUCTURE:
  Agent: State Discovery Agent
  Tools: browser, terminal, file
  Iterations: 30-40
  
  Workflow:
  1. Identify possible states
  2. Test transitions between states
  3. Document transition triggers
  4. Document transition constraints
  5. Test edge case transitions
  6. Identify invalid transitions
  7. Generate state machine diagram

OUTPUT:
  - State machine diagram
  - Transition table
  - State validation tests
  - State-specific test cases

EXAMPLE:
  delegate_task(
      goal="Discover system state machine",
      context="""
      Discover all system states and transitions
      
      Deliverables:
      1. State diagram (Mermaid format)
      2. Transition table
      3. Tests for valid transitions
      4. Tests for invalid transitions
      
      Focus areas:
      - User account states
      - Order states
      - Payment states
      """,
      toolsets=['browser', 'file'],
      max_iterations=35
  )
```

### Pattern 3: Error Condition Cataloging

```
PATTERN_NAME: Error Condition Cataloging

PURPOSE:
  Discover all error conditions and responses

APPLICABILITY:
  After API discovery
  Before implementation starts

STRUCTURE:
  Agent: Error Discovery Agent
  Tools: browser, terminal, file
  Iterations: 15-20
  
  Workflow:
  1. Inject invalid inputs
  2. Record error responses
  3. Categorize error types
  4. Document error codes
  5. Test error recovery
  6. Document error handling patterns

OUTPUT:
  - Error catalog
  - Error handling tests
  - Recovery procedure tests

EXAMPLE:
  delegate_task(
      goal="Catalog all error conditions",
      context="""
      Discover and document all error conditions
      
      Test for:
      - Invalid input types
      - Missing required fields
      - Constraint violations
      - Rate limiting
      - Authentication failures
      
      Output: error_catalog.md with all error types
      """,
      toolsets=['browser', 'file'],
      max_iterations=18
  )
```

## Implementation Patterns

### Pattern 1: TDD by Agent

```
PATTERN_NAME: TDD by Agent

PURPOSE:
  Implement features using agent-driven TDD

APPLICABILITY:
  For all feature implementations

STRUCTURE:
  Agent: Implementation Agent
  Tools: terminal, file
  Iterations: 30-50
  
  Workflow:
  1. Receive specification tests
  2. Run tests (RED phase)
  3. Write minimal implementation (GREEN phase)
  4. Run tests again (verify GREEN)
  5. Refactor code (REFACTOR phase)
  6. Run tests again (verify REFACTOR)
  7. Commit changes

OUTPUT:
  - Implementation code
  - Passing tests
  - Clean, refactored code

EXAMPLE:
  delegate_task(
      goal="Implement feature using TDD",
      context=f"""
      Tests to implement:
      {specification_output}
      
      Follow TDD strictly:
      1. Run tests - they MUST fail
      2. Write minimal code to pass
      3. Verify all tests pass
      4. Refactor
      5. Verify tests still pass
      
      Constraint: NO access to original system
      """,
      toolsets=['terminal', 'file'],
      max_iterations=40
  )
```

### Pattern 2: Parallel Feature Development

```
PATTERN_NAME: Parallel Feature Development

PURPOSE:
  Implement multiple features simultaneously

APPLICABILITY:
  When features are independent
  When multiple agents available

STRUCTURE:
  Agents: Multiple Implementation Agents
  Tools: terminal, file per agent
  Iterations: 30-50 per agent
  
  Workflow:
  1. Assign independent features to agents
  2. Each agent implements feature with TDD
  3. Agents work independently
  4. Merge results
  5. Run integration tests

OUTPUT:
  - Multiple feature implementations
  - Integration test results

EXAMPLE:
  def parallel_implementation(feature_specs):
      agents = [
          delegate_task(
              goal=f"Implement {spec['name']}",
              context=f"Tests: {spec['tests']}",
              ...
          )
          for spec in feature_specs
      ]
      results = [a.result() for a in agents]
      return merge_results(results)
```

### Pattern 3: Spec-Driven Implementation

```
PATTERN_NAME: Spec-Driven Implementation

PURPOSE:
  Implement features directly from specification documents

APPLICABILITY:
  When complete specification exists
  When implementation is straightforward

STRUCTURE:
  Agent: Spec Implementation Agent
  Tools: file, terminal
  Iterations: 20-40
  
  Workflow:
  1. Read specification document
  2. Parse requirements
  3. Create implementation structure
  4. Implement each requirement
  5. Generate tests from spec
  6. Run all tests

OUTPUT:
  - Implementation matching spec
  - Tests derived from spec

EXAMPLE:
  delegate_task(
      goal="Implement from specification",
      context=f"""
      Specification:
      {specification_content}
      
      Implement each requirement:
      - Read requirement
      - Write implementation
      - Write test
      - Verify
      
      Output: Complete implementation with tests
      """,
      toolsets=['file', 'terminal'],
      max_iterations=35
  )
```

## Verification Patterns

### Pattern 1: Parallel Parity Testing

```
PATTERN_NAME: Parallel Parity Testing

PURPOSE:
  Verify new implementation matches original behavior

APPLICABILITY:
  After each feature implementation
  Before merging changes

STRUCTURE:
  Agent: Parity Verification Agent
  Tools: browser, terminal, file
  Iterations: 15-25
  
  Workflow:
  1. Run test against original system
  2. Run test against new implementation
  3. Compare results
  4. Log divergences
  5. Report parity status

OUTPUT:
  - Parity report
  - Divergence details (if any)

EXAMPLE:
  delegate_task(
      goal="Verify behavioral parity",
      context=f"""
      Original system: https://api.original.com/v1
      New implementation: /workspace/new-system/
      
      Run each test:
      1. Against original
      2. Against new
      3. Compare results
      
      Acceptance: All tests produce identical results
      """,
      toolsets=['browser', 'terminal'],
      max_iterations=20
  )
```

### Pattern 2: Automated Regression Detection

```
PATTERN_NAME: Automated Regression Detection

PURPOSE:
  Detect regressions in existing features

APPLICABILITY:
  After each code change
  Before deployment

STRUCTURE:
  Agent: Regression Detection Agent
  Tools: terminal, file
  Iterations: 10-15
  
  Workflow:
  1. Run full test suite
  2. Compare with baseline results
  3. Identify regressions
  4. Report with details

OUTPUT:
  - Regression report
  - Affected tests
  - Root cause analysis

EXAMPLE:
  delegate_task(
      goal="Detect regressions",
      context="""
      Run all tests and compare with baseline
      
      Baseline: tests/baseline_results.json
      Current: Run test suite
      
      Report:
      - Tests that pass/fail differently
      - Performance regressions
      - New failures
      
      Fail: Any new failures
      """,
      toolsets=['terminal'],
      max_iterations=12
  )
```

## Coordination Patterns

### Pattern 1: Hierarchical Task Delegation

```
PATTERN_NAME: Hierarchical Task Delegation

PURPOSE:
  Coordinate multiple agents through hierarchy

APPLICABILITY:
  When implementing complex systems
  When multiple features need coordination

STRUCTURE:
  Level 1: Project Coordinator Agent
  Level 2: Team Lead Agents (Observation, Implementation, Verification)
  Level 3: Worker Agents
  
  Workflow:
  1. Coordinator assigns work to team leads
  2. Team leads assign work to workers
  3. Workers report to leads
  4. Leads aggregate and report to coordinator

OUTPUT:
  - Coordinated implementation
  - Consistent outputs

EXAMPLE:
  def hierarchical_delegation(task):
      coordinator = delegate_task(
          goal=f"Coordinate {task}",
          ...
      )
      
      team_leads = [
          delegate_task(
              goal="Implementation Team Lead",
              context=f"Task: {task}",
              ...
          ),
          # Other team leads
      ]
      
      workers = []
      for lead in team_leads:
          worker = delegate_task(
              goal="Worker Agent",
              context=f"Task from: {lead.id}",
              ...
          )
          workers.append(worker)
      
      results = [coordinator.result()] + [w.result() for w in workers]
      return results
```

### Pattern 2: Consensus-Based Decision Making

```
PATTERN_NAME: Consensus-Based Decision Making

PURPOSE:
  Make decisions through agent consensus

APPLICABILITY:
  When multiple agents have conflicting views
  For specification decisions

STRUCTURE:
  Agents: Multiple Observation Agents
  Tools: browser, file
  Iterations: 10-20 each
  
  Workflow:
  1. Each agent observes independently
  2. Agents share observations
  3. Compare observations
  4. Resolve conflicts
  5. Reach consensus

OUTPUT:
  - Consensus decision
  - Conflict resolution record

EXAMPLE:
  def consensus_decisions(topic):
      agents = [
          delegate_task(goal=f"Observe {topic}", ...),
          delegate_task(goal=f"Observe {topic}", ...),
          delegate_task(goal=f"Observe {topic}", ...),
      ]
      
      results = [a.result() for a in agents]
      
      # Find consensus
      consensus = find_most_common(results)
      
      return consensus
```

## Pattern Selection Guide

| Pattern | When to Use | Complexity |
|---------|-------------|------------|
| Systematic API Probing | Initial exploration | Low |
| State Machine Discovery | Complex state systems | Medium |
| Error Cataloging | After API discovery | Low |
| TDD by Agent | Feature implementation | Medium |
| Parallel Features | Independent features | High |
| Spec-Driven | Complete spec exists | Low |
| Parallel Parity | Verification | Medium |
| Regression Detection | CI/CD | Low |
| Hierarchical Delegation | Complex projects | High |
| Consensus | Conflict resolution | Medium |

## Pitfalls

### Pitfall 1: Pattern Mismatch

Using wrong pattern for context.

**Mitigation:** Match pattern to situation.

### Pitfall 2: Over-Complexity

Too many patterns creates overhead.

**Mitigation:** Start simple, add patterns as needed.

### Pitfall 3: Pattern Coupling

Patterns too tightly coupled.

**Mitigation:** Define clear interfaces between patterns.

### Pitfall 4: Inconsistent Application

Using patterns inconsistently.

**Mitigation:** Document patterns, train agents.

## Related Concepts
- [[ai-agent-methodologies]]
- [[multi-agent-coordination]]
- [[delegate-task-workflows]]

## See Also
- [[clean-room-engineering]] - Clean room requirements
- [[legal/insider-knowledge-risks]] - Agent isolation rules
- [[diagrams/clean-room-fundamentals-diagram]] - Pattern visualizations- [[delegate-task-workflows]]
- [[clean-room-engineering]]
- [[test-driven-development]]