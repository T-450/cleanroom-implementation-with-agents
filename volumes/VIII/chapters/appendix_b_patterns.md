---
title: Appendix B - Pattern Library
created: 2026-04-16
updated: 2026-04-16
type: appendix
tags: [patterns, reference, catalog, implementation]
appendix: B
pages: 20
---

# Appendix B: Pattern Library

This appendix catalogs all patterns referenced throughout Volumes I-VII. Patterns are organized by category and include:
- Pattern name and ID
- Purpose and applicability
- AI agent workflow templates
- Cross-references to Volume usage
- Known variations and anti-patterns

## Pattern ID Convention

Patterns use the format: **CATEGORY-NUMBER**

- **DISC** - Discovery patterns
- **IMPL** - Implementation patterns  
- **VERI** - Verification patterns
- **COORD** - Coordination patterns
- **MIGR** - Migration patterns

Examples: DISC-01, IMPL-05, COORD-12

---

## B.1 Discovery Patterns

Discovery patterns are used by specification teams to observe and document original system behavior.

### DISC-01: Systematic API Probing

**Source**: Pattern from Vol. IV, Ch. 16; Vol. VI, Ch. 27
**Also Known As**: API Surface Discovery, Endpoint Enumeration

#### Purpose
Systematically discover all API endpoints, request/response formats, and behavioral characteristics through controlled interaction with the original system.

#### Applicability
- Starting a clean room project
- API-first systems
- REST, GraphQL, gRPC interfaces
- Internal microservices

#### Structure

```
┌─────────────────────────────────────────────────────────────┐
│                  DISC-01: SYSTEMATIC API PROBING            │
├─────────────────────────────────────────────────────────────┤
│ AGENT:        API Probing Agent                             │
│ TOOLS:        browser, terminal, file                       │
│ ITERATIONS:   20-30                                         │
│ TEAM:         Specification                                 │
├─────────────────────────────────────────────────────────────┤
│ WORKFLOW:                                                   │
│ 1. Enumerate all known API entry points                     │
│ 2. For each endpoint:                                       │
│    a. Probe with valid inputs across types                  │
│    b. Document response structure and codes                 │
│    c. Probe with invalid inputs                             │
│    d. Document error responses                              │
│    e. Test boundary conditions                              │
│    f. Document rate limits and throttling                   │
│ 3. Map parameter dependencies between endpoints             │
│ 4. Document authentication requirements                     │
│ 5. Generate comprehensive API specification                 │
├─────────────────────────────────────────────────────────────┤
│ OUTPUT:                                                     │
│ • API specification document (OpenAPI/Swagger)              │
│ • Request/response example library                          │
│ • Error condition catalog                                   │
│ • Generated test cases for each endpoint                    │
│ • Dependency graph between endpoints                        │
└─────────────────────────────────────────────────────────────┘
```

#### AI Agent Delegation Template

```python
delegate_task(
    goal="Systematic API Discovery and Documentation",
    context="""
    TARGET SYSTEM: [protocol]://[host]:[port]
    AUTHENTICATION: [method and credentials]
    
    DELIVERABLES:
    1. Complete API endpoint inventory
    2. OpenAPI 3.0 specification file
    3. Request/response schema documentation
    4. Error handling matrix
    5. pytest test cases for each endpoint
    
    DISCOVERY PROCESS:
    Phase 1 - Basic Enumeration (iterations 1-5):
    - Identify all HTTP methods per endpoint
    - Document base response structure
    - Map URL patterns and parameters
    
    Phase 2 - Deep Probing (iterations 6-15):
    - Test valid input variations
    - Test invalid input handling
    - Document error codes and messages
    - Probe rate limiting behavior
    
    Phase 3 - Edge Case Discovery (iterations 16-25):
    - Test boundary conditions
    - Test character encoding handling
    - Test maximum payload sizes
    - Test concurrent access patterns
    
    CONSTRAINTS:
    - Never access source code or implementation details
    - Document only observable behavior
    - All findings go to specification team only
    - No cross-contamination with implementation team
    """,
    toolsets=['browser', 'file'],
    max_iterations=25
)
```

#### Variations
- **DISC-01-V1**: GraphQL introspection variant
- **DISC-01-V2**: SOAP/WSDL discovery variant  
- **DISC-01-V3**: gRPC reflection variant

#### Known Anti-Patterns
- Probing production systems without rate limiting
- Documentation that includes inferred implementation
- Sharing findings directly with implementation team
- Inadequate error case coverage

#### Cross-References
- Used in: Vol. IV, Ch. 16 "Discovery Phase with AI Agents"
- Related: DISC-03 (Error Discovery), DISC-05 (State Machine Discovery)
- Complements: IMPL-01 (TDD Implementation)

---

### DISC-02: State Machine Discovery

**Source**: Pattern from Vol. IV, Ch. 16; Vol. V, Ch. 19
**Also Known As**: State Space Exploration, Behavioral State Mapping

#### Purpose
Discover and document the complete state space of a system, including all valid states, transitions, and state-dependent behavior.

#### Applicability
- Systems with complex lifecycle management
- Order processing systems
- User account management
- Workflow engines
- Payment processing

#### Structure

```
┌─────────────────────────────────────────────────────────────┐
│                DISC-02: STATE MACHINE DISCOVERY             │
├─────────────────────────────────────────────────────────────┤
│ AGENT:        State Discovery Agent                         │
│ TOOLS:        browser, terminal, file                       │
│ ITERATIONS:   30-40                                         │
│ TEAM:         Specification                                 │
├─────────────────────────────────────────────────────────────┤
│ WORKFLOW:                                                   │
│ 1. Identify all state domains in system                     │
│ 2. For each domain:                                         │
│    a. Identify observable states                            │
│    b. Discover all possible state values                    │
│    c. Test transitions between states                       │
│    d. Document transition triggers                          │
│    e. Document transition preconditions                     │
│    f. Test invalid transitions                              │
│    g. Discover side effects on transitions                  │
│ 3. Map inter-domain state dependencies                      │
│ 4. Generate state machine diagrams                          │
│ 5. Create state-based test suite                            │
├─────────────────────────────────────────────────────────────┤
│ OUTPUT:                                                     │
│ • State machine diagram (Mermaid/PlantUML)                  │
│ • Complete transition table                                 │
│ • State validation test cases                               │
│ • Invalid transition test cases                             │
│ • State-dependent behavior specification                    │
│ • State history requirements                                │
└─────────────────────────────────────────────────────────────┘
```

#### AI Agent Delegation Template

```python
delegate_task(
    goal="Comprehensive State Machine Discovery",
    context="""
    TARGET DOMAIN: [order lifecycle / user account / document workflow]
    KNOWN STARTING STATES: [list initial observable states]
    
    DISCOVERY PROCESS:
    Phase 1 - State Enumeration:
    - Interact with system to identify all observable states
    - Map state attributes that indicate state
    - Document how state is exposed (API field, UI indicator, etc.)
    
    Phase 2 - Transition Mapping:
    - For each identified state, attempt all possible actions
    - Document which actions cause state changes
    - Record the resulting state for each transition
    - Test timing and ordering dependencies
    
    Phase 3 - Constraint Discovery:
    - Attempt transitions that should be invalid
    - Document error responses and guards
    - Test preconditions for valid transitions
    - Discover hidden/implicit states
    
    Phase 4 - Side Effect Analysis:
    - Document notifications triggered by transitions
    - Map data changes accompanying state changes
    - Identify asynchronous processes triggered
    - Test rollback/recovery from states
    
    DELIVERABLES:
    1. Mermaid state diagram showing all states and transitions
    2. Transition table (from_state, action, to_state, guard_conditions)
    3. Test cases for each valid transition
    4. Test cases for invalid transition attempts
    5. State history and audit trail requirements
    
    CONSTRAINTS:
    - Infer states only from observable behavior
    - Do not assume implementation details
    - Test thoroughly for unreachable states
    - Document timing and race condition observations
    """,
    toolsets=['browser', 'file'],
    max_iterations=35
)
```

#### Common State Machines Discovered

| Domain | Typical States | Transitions | Complexity |
|--------|---------------|-------------|------------|
| Order Processing | 5-12 | 15-40 | Medium |
| User Account | 4-8 | 10-25 | Low |
| Payment | 6-15 | 20-50 | High |
| Document Workflow | 8-20 | 30-80 | High |
| Subscription | 4-10 | 12-30 | Medium |

#### Cross-References
- Used in: Vol. III, Ch. 12 (BIOS state machines), Vol. V, Ch. 19
- Related: DISC-04 (Workflow Discovery), IMPL-06 (State-Based Implementation)
- Complements: DISC-01 (API Discovery)

---

### DISC-03: Error Condition Cataloging

**Source**: Pattern from Vol. IV, Ch. 17
**Also Known As**: Negative Testing Discovery, Failure Mode Analysis

#### Purpose
Systematically discover all error conditions, failure modes, and error responses across the entire system surface area.

#### Applicability
- All systems (critical for completeness)
- High-reliability systems
- Financial systems
- Safety-critical applications

#### Structure

```
┌─────────────────────────────────────────────────────────────┐
│            DISC-03: ERROR CONDITION CATALOGING              │
├─────────────────────────────────────────────────────────────┤
│ AGENT:        Error Discovery Agent                         │
│ TOOLS:        browser, terminal, file                       │
│ ITERATIONS:   15-20                                         │
│ TEAM:         Specification                                 │
├─────────────────────────────────────────────────────────────┤
│ WORKFLOW:                                                   │
│ 1. For each discovered endpoint/operation:                  │
│    a. Identify all input parameters                         │
│    b. Test with missing required parameters                 │
│    c. Test with invalid data types                          │
│    d. Test with out-of-range values                         │
│    e. Test with malformed data                              │
│    f. Test with unauthorized access                         │
│    g. Test rate limiting and throttling                     │
│    h. Test concurrent access scenarios                      │
│ 2. Categorize error responses                               │
│ 3. Document recovery procedures from errors                 │
│ 4. Test error recovery actions                              │
│ 5. Generate error catalog and test suite                    │
├─────────────────────────────────────────────────────────────┤
│ OUTPUT:                                                     │
│ • Comprehensive error catalog                               │
│ • Error response matrix (input → error → response)          │
│ • Error code taxonomy                                       │
│ • Error handling tests                                      │
│ • Recovery procedure tests                                  │
│ • Security/validation boundary tests                        │
└─────────────────────────────────────────────────────────────┘
```

#### Error Discovery Taxonomy

```
ERROR CATEGORIES:
├── INPUT VALIDATION ERRORS
│   ├── Missing required fields
│   ├── Invalid data types
│   ├── Out-of-range values
│   ├── Malformed format
│   └── Invalid encoding
├── BUSINESS RULE ERRORS
│   ├── State violations
│   ├── Constraint violations
│   ├── Duplicate submissions
│   ├── Insufficient resources
│   └── Timing violations
├── AUTHENTICATION ERRORS
│   ├── Invalid credentials
│   ├── Expired tokens
│   ├── Insufficient permissions
│   └── Session expiration
├── SYSTEM ERRORS
│   ├── Service unavailable
│   ├── Timeout
│   ├── Rate limit exceeded
│   └── Internal errors
└── DEPENDENCY ERRORS
    ├── External service failure
    ├── Database connection issues
    ├── Network errors
    └── Resource exhaustion
```

#### AI Agent Delegation Template

```python
delegate_task(
    goal="Complete Error Condition Discovery",
    context="""
    CONTEXT: [API endpoints from prior discovery / UI workflow]
    
    ERROR TEST MATRIX:
    For each endpoint/operation discovered:
    
    1. VALIDATION ERRORS:
       - Omit each required field individually
       - Use wrong data type for each field
       - Exceed maximum length limits
       - Use out-of-range numeric values
       - Use invalid character encodings
       - Submit malformed JSON/XML
       - Use null/undefined values
    
    2. BUSINESS LOGIC ERRORS:
       - Perform invalid state transitions
       - Exceed account limits
       - Submit duplicate requests rapidly
       - Use expired references
       - Access resources out of scope
    
    3. AUTHENTICATION ERRORS:
       - Use invalid tokens/credentials
       - Submit expired tokens
       - Omit authentication entirely
       - Use insufficient scope tokens
       - Test session timeout handling
    
    4. SYSTEM STRESS ERRORS:
       - Exceed rate limits
       - Send oversize payloads
       - Create resource exhaustion
       - Test timeout scenarios
       - Test concurrent modification
    
    DOCUMENTATION REQUIRED:
    - Error code received
    - HTTP status code
    - Error message text
    - Response structure
    - Retry guidance (if any)
    - Recovery procedure
    
    OUTPUT: error_catalog.md with:
    1. Categorized error inventory
    2. Error-to-test mapping
    3. Recovery procedure documentation
    4. Edge case behaviors
    """,
    toolsets=['browser', 'file'],
    max_iterations=18
)
```

#### Cross-References
- Used in: Vol. VI, Ch. 25 (Negative Testing)
- Related: DISC-01 (API Probing), VERI-04 (Error Recovery Testing)
- Complements: IMPL-03 (Error Handling Implementation)

---

### DISC-04: Data Flow Mapping

**Source**: Pattern from Vol. V, Ch. 18
**Also Known As**: Information Flow Discovery, Data Lineage Analysis

#### Purpose
Trace the complete lifecycle of data through the system, from input through processing to output and persistence.

#### Applicability
- Data-intensive applications
- ETL systems
- Report generation systems
- Multi-step processing pipelines
- Compliance-sensitive data handling

#### Structure

```
┌─────────────────────────────────────────────────────────────┐
│              DISC-04: DATA FLOW MAPPING                     │
├─────────────────────────────────────────────────────────────┤
│ AGENT:        Data Flow Agent                               │
│ TOOLS:        browser, terminal, file, database client      │
│ ITERATIONS:   25-35                                         │
│ TEAM:         Specification                                 │
├─────────────────────────────────────────────────────────────┤
│ WORKFLOW:                                                   │
│ 1. Identify all data input sources                          │
│ 2. Track data transformations:                              │
│    a. Capture input format                                  │
│    b. Observe validation rules applied                      │
│    c. Document calculations/transformations                 │
│    d. Map intermediate storage                              │
│    e. Observe output generation                             │
│ 3. Map data persistence:                                    │
│    a. Storage locations                                     │
│    b. Retention periods                                     │
│    c. Update/delete behavior                                │
│ 4. Document data dependencies                               │
│ 5. Generate data flow diagrams                              │
├─────────────────────────────────────────────────────────────┤
│ OUTPUT:                                                     │
│ • Data flow diagrams                                        │
│ • Input/output specifications per flow                      │
│ • Transformation rules documentation                        │
│ • Data retention requirements                               │
│ • Compliance-relevant data handling                         │
│ • Data lineage test cases                                   │
└─────────────────────────────────────────────────────────────┘
```

#### Cross-References
- Used in: Vol. V, Ch. 18; Vol. VII, Ch. 22
- Related: DISC-01 (API Probing), MIGR-02 (Data Migration)
- Complements: IMPL-04 (Data Transformation)

---

### DISC-05: Performance Baseline Establishment

**Source**: Pattern from Vol. VI, Ch. 26
**Also Known As**: Performance Profiling, Benchmark Creation

#### Purpose
Establish quantitative baselines for system performance across all operations to enable parity measurement and improvement validation.

#### Applicability
- All systems with response time requirements
- High-throughput systems
- User-facing applications
- SLA-bound services

#### Structure

```
┌─────────────────────────────────────────────────────────────┐
│         DISC-05: PERFORMANCE BASELINE ESTABLISHMENT         │
├─────────────────────────────────────────────────────────────┤
│ AGENT:        Performance Discovery Agent                   │
│ TOOLS:        terminal, browser, performance tools          │
│ ITERATIONS:   15-20                                         │
│ TEAM:         Specification                                 │
├─────────────────────────────────────────────────────────────┤
│ WORKFLOW:                                                   │
│ 1. Identify all measurable operations                       │
│ 2. For each operation:                                      │
│    a. Measure response time (p50, p95, p99)                 │
│    b. Measure throughput                                    │
│    c. Identify resource usage patterns                      │
│    d. Test under different load conditions                  │
│    e. Document performance characteristics                  │
│ 3. Establish performance profiles                           │
│ 4. Document scalability characteristics                     │
│ 5. Generate performance specification                       │
├─────────────────────────────────────────────────────────────┤
│ OUTPUT:                                                     │
│ • Performance baseline document                             │
│ • Response time distribution data                           │
│ • Throughput specifications                                   │
│ • Resource usage baselines                                  │
│ • Scalability characteristics                               │
│ • Performance regression tests                              │
└─────────────────────────────────────────────────────────────┘
```

#### Performance Metrics Template

```yaml
operation_performance:
  operation_name: "GetUserDetails"
  endpoint: "GET /api/users/{id}"
  
  response_times_ms:
    p50: 45
    p95: 120
    p99: 250
    max_observed: 500
    
  throughput:
    requests_per_second: 1000
    concurrent_users: 500
    
  resource_usage:
    cpu_percent: 15
    memory_mb: 50
    db_queries: 3
    
  scalability:
    linear_to: 3000_rps
    degradation_point: 5000_rps
    bottleneck: "database_connection_pool"
    
  test_conditions:
    data_volume: "1M users in database"
    cache_warm: true
    network_latency_ms: 10
```

#### Cross-References
- Used in: Vol. VI, Ch. 26; Appendix C.2
- Related: VERI-06 (Performance Testing)
- Complements: IMPL-08 (Performance Optimization)

---

## B.2 Implementation Patterns

Implementation patterns are used by the implementation team to write code based on specifications.

### IMPL-01: TDD by Agent

**Source**: Pattern from Vol. IV, Ch. 16; Vol. V, Ch. 20
**Also Known As**: Agent-Driven Test-First Development

#### Purpose
Implement features following strict test-driven development cycle, with AI agents handling the red-green-refactor loop.

#### Applicability
- All feature implementations
- Greenfield development
- Incremental additions
- Bug fixes

#### Structure

```
┌─────────────────────────────────────────────────────────────┐
│                IMPL-01: TDD BY AGENT                        │
├─────────────────────────────────────────────────────────────┤
│ AGENT:        Implementation Agent                          │
│ TOOLS:        terminal, file                                │
│ ITERATIONS:   30-50                                         │
│ TEAM:         Implementation                                │
├─────────────────────────────────────────────────────────────┤
│ WORKFLOW:                                                   │
│ 1. RECEIVE specification tests from spec team               │
│ 2. [RED] Run tests and verify failure                       │
│ 3. [GREEN] Write minimal implementation to pass tests       │
│ 4. Run tests and verify pass                                │
│ 5. [REFACTOR] Improve code quality                          │
│ 6. Run tests and verify still pass                          │
│ 7. [COMMIT] Commit with specification reference             │
│ 8. Request code review                                      │
├─────────────────────────────────────────────────────────────┤
│ CONSTRAINTS:                                                │
│ • NO access to original system                              │
│ • ONLY specification documents as source                    │
│ • ALL tests must pass before refactor                       │
│ • COMMIT message links to specification                     │
│ • CODE review required before merge                         │
├─────────────────────────────────────────────────────────────┤
│ OUTPUT:                                                     │
│ • Implementation code                                       │
│ • Passing test suite                                        │
│ • Refactored, clean code                                    │
│ • Commit history with spec references                       │
│ • Code review approval                                      │
└─────────────────────────────────────────────────────────────┘
```

#### AI Agent Delegation Template

```python
def implement_with_tdd(specification_tests, spec_reference):
    """
    Implements features using strict TDD cycle.
    
    Args:
        specification_tests: Test cases from specification team
        spec_reference: Reference to source specification document
    """
    
    return delegate_task(
        goal=f"Implement feature using strict TDD - {spec_reference}",
        context=f"""
        SPECIFICATION REFERENCE: {spec_reference}
        
        PROVIDED TESTS:
        ```python
        {specification_tests}
        ```
        
        TDD CYCLE - FOLLOW EXACTLY:
        
        PHASE 1 - RED (iterations 1-5):
        1. Set up test environment
        2. Place tests in appropriate test file
        3. Run tests - they MUST fail (verify this)
        4. Document expected behavior from test failures
        5. Plan implementation approach
        
        PHASE 2 - GREEN (iterations 6-20):
        1. Create minimal implementation file
        2. Implement just enough to pass first test
        3. Run tests - verify progress
        4. Repeat for each test
        5. ONLY pass tests, no extra functionality
        6. ALL tests must pass to proceed
        
        PHASE 3 - REFACTOR (iterations 21-35):
        1. Review code for duplication
        2. Look for naming improvements
        3. Check for SOLID violations
        4. Apply design patterns appropriately
        5. Run tests after each change
        6. ALL tests must continue to pass
        
        PHASE 4 - COMPLETE (iterations 36-40):
        1. Final test run - 100% pass
        2. Add docstrings where missing
        3. Type hints if applicable
        4. Code style compliance check
        5. Commit with message: "Implement {spec_reference}"
        
        CRITICAL CONSTRAINTS:
        - NO access to original system
        - NO reverse engineering
        - ONLY specification documents
        - ALL tests must pass before commit
        - CODE review required
        
        SUCCESS CRITERIA:
        - All tests pass
        - Code coverage > 80%
        - No code duplication > 3 lines
        - All functions < 50 lines
        - Cyclomatic complexity < 10 per function
        """,
        toolsets=['terminal', 'file'],
        max_iterations=40
    )
```

#### Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Test Coverage | ≥ 80% | Coverage tool |
| Red-Green Cycles | Per test | Commit history |
| Refactoring Commits | ≥ 2 per feature | Git log |
| Spec References | 100% of commits | Message analysis |
| Build Time | < 5 min | CI metrics |

#### Cross-References
- Used in: Vol. IV, Ch. 16; Vol. V, Ch. 20
- Related: IMPL-02 (Parallel Implementation), DISC-01 (API Probing)
- Complements: VERI-01 (Parity Testing)

---

### IMPL-02: Parallel Feature Development

**Source**: Pattern from Vol. IV, Ch. 16
**Also Known As**: Concurrent Implementation, Multi-Agent Development

#### Purpose
Implement multiple independent features simultaneously using multiple AI agents to accelerate delivery.

#### Applicability
- Large projects with independent features
- Multiple modules without cross-dependencies
- Sufficient agent resources available
- Feature teams working in parallel

#### Structure

```
┌─────────────────────────────────────────────────────────────┐
│           IMPL-02: PARALLEL FEATURE DEVELOPMENT             │
├─────────────────────────────────────────────────────────────┤
│ AGENTS:       Multiple Implementation Agents                │
│ TOOLS:        terminal, file (isolated work areas)          │
│ ITERATIONS:   30-50 per agent                               │
│ TEAM:         Implementation                                │
├─────────────────────────────────────────────────────────────┤
│ WORKFLOW:                                                   │
│ 1. Identify independent feature groups                      │
│ 2. Assign features to agents:                               │
│    a. Ensure no overlapping code areas                      │
│    b. Define integration interfaces                         │
│    c. Establish contract tests                              │
│ 3. Agents implement concurrently (IMPL-01)                  │
│ 4. Monitor progress independently                           │
│ 5. Integrate completed features:                            │
│    a. Merge code branches                                   │
│    b. Run integration tests                                 │
│    c. Verify contract compliance                            │
│ 6. Resolve conflicts if any                                 │
│ 7. Run full regression suite                                │
├─────────────────────────────────────────────────────────────┤
│ OUTPUT:                                                     │
│ • Multiple feature implementations                          │
│ • Integrated codebase                                       │
│ • Integration test results                                  │
│ • Contract test suite                                       │
└─────────────────────────────────────────────────────────────┘
```

#### Coordination Template

```python
def parallel_implementation(feature_specs, max_parallel=4):
    """
    Coordinate parallel feature implementation.
    
    Args:
        feature_specs: List of feature specifications
        max_parallel: Maximum concurrent agents
    """
    
    # Phase 1: Dependency analysis
    dependencies = analyze_dependencies(feature_specs)
    
    # Phase 2: Assign to parallel tracks
    tracks = distribute_to_tracks(feature_specs, dependencies, max_parallel)
    
    results = []
    
    # Phase 3: Execute in parallel
    for track_id, features in enumerate(tracks):
        for feature in features:
            result = delegate_task(
                goal=f"Implement {feature['name']} (Track {track_id})",
                context=f"""
                FEATURE: {feature['name']}
                SPEC REF: {feature['spec_reference']}
                TRACK: {track_id}
                
                DEPENDENCIES: {feature.get('dependencies', 'None')}
                
                IF dependencies exist:
                - Use interface contracts, not implementations
                - Implement against stub/mock
                - Contract tests will verify integration
                
                FOLLOW: IMPL-01 TDD pattern
                
                ISOLATION:
                - Work in directory: /workspace/track_{track_id}/{feature['id']}
                - Do not access other tracks' code
                - Do not access original system
                """,
                toolsets=['terminal', 'file'],
                max_iterations=45
            )
            results.append(result)
    
    # Phase 4: Integration
    return integrate_results(results, dependencies)
```

#### Dependency Analysis Rules

```python
def analyze_dependencies(features):
    """
    Determines which features can be developed in parallel.
    
    Returns dependency graph and suggested execution order.
    """
    graph = DependencyGraph()
    
    for feature in features:
        for dep in feature.get('dependencies', []):
            graph.add_edge(dep, feature['id'])
    
    # Calculate parallelization potential
    levels = graph.topological_sort_levels()
    
    return {
        'dependency_graph': graph,
        'execution_levels': levels,
        'parallelizable_features': [
            features for features in levels.values()
            if len(features) > 1
        ],
        'critical_path': graph.find_critical_path()
    }
```

#### Cross-References
- Used in: Vol. IV, Ch. 16; Vol. V, Ch. 21
- Related: COORD-01 (Hierarchical Delegation), COORD-02 (Consensus)
- Complements: IMPL-01 (TDD), VERI-02 (Regression Testing)

---

### IMPL-03: Spec-Driven Implementation

**Source**: Pattern from Vol. V, Ch. 20
**Also Known As**: Direct Specification Translation

#### Purpose
Implement features directly from specification documents when complete specifications exist, treating the spec as a contract.

#### Applicability
- Well-specified features
- API implementations
- Protocol implementations
- Configuration-driven features

#### Structure

```
┌─────────────────────────────────────────────────────────────┐
│            IMPL-03: SPEC-DRIVEN IMPLEMENTATION              │
├─────────────────────────────────────────────────────────────┤
│ AGENT:        Specification Implementation Agent            │
│ TOOLS:        file, terminal                                │
│ ITERATIONS:   20-40                                         │
│ TEAM:         Implementation                                │
├─────────────────────────────────────────────────────────────┤
│ WORKFLOW:                                                   │
│ 1. Read and analyze specification document                  │
│ 2. Parse requirements into discrete items                   │
│ 3. Create implementation scaffolding                        │
│ 4. For each requirement:                                    │
│    a. Create corresponding implementation                   │
│    b. Generate test from spec                               │
│    c. Verify implementation meets test                      │
│ 5. Verify all requirements addressed                        │
│ 6. Generate traceability matrix                             │
├─────────────────────────────────────────────────────────────┤
│ OUTPUT:                                                     │
│ • Implementation code                                       │
│ • Tests derived from spec                                   │
│ • Requirements traceability matrix                          │
│ • Coverage report against spec                              │
└─────────────────────────────────────────────────────────────┘
```

#### Cross-References
- Used in: Vol. V, Ch. 20
- Related: IMPL-01 (TDD), DISC-01 (API Probing)
- Complements: VERI-01 (Parity Testing)

---

### IMPL-04: Modular Decomposition Implementation

**Source**: Pattern from Vol. V, Ch. 18
**Also Known As**: Component-Based Implementation

#### Purpose
Break large system implementations into manageable, loosely-coupled modules implemented independently.

#### Structure

```
┌─────────────────────────────────────────────────────────────┐
│         IMPL-04: MODULAR DECOMPOSITION IMPLEMENTATION       │
├─────────────────────────────────────────────────────────────┤
│ AGENTS:       Multiple specialized implementation agents    │
│ TOOLS:        terminal, file, architecture diagramming      │
│ ITERATIONS:   Varies per module                             │
│ TEAM:         Implementation                                │
├─────────────────────────────────────────────────────────────┤
│ WORKFLOW:                                                   │
│ 1. Analyze system for module boundaries                     │
│ 2. Define module interfaces/contracts                       │
│ 3. Create module architecture                               │
│ 4. Assign modules to agents                                 │
│ 5. Implement modules respecting interfaces                  │
│ 6. Integration testing of module combinations               │
│ 7. System-level integration                                 │
├─────────────────────────────────────────────────────────────┤
│ OUTPUT:                                                     │
│ • Module implementations                                    │
│ • Interface definitions                                     │
│ • Module test suites                                        │
│ • Integration test suite                                    │
│ • Architecture documentation                                │
└─────────────────────────────────────────────────────────────┘
```

#### Cross-References
- Used in: Vol. V, Ch. 18; Vol. VII, Ch. 21
- Related: IMPL-02 (Parallel), COORD-01 (Hierarchical)
- Complements: MIGR-03 (Strangler Fig)

---

## B.3 Verification Patterns

Verification patterns are used to validate that the implementation matches the original system behavior.

### VERI-01: Parallel Parity Testing

**Source**: Pattern from Vol. IV, Ch. 16; Vol. VI, Ch. 23
**Also Known As**: Dual System Verification, Behavioral Equivalence Testing

#### Purpose
Verify that the new implementation produces identical results to the original system when given the same inputs.

#### Applicability
- All clean room implementations
- Regression testing
- Feature parity validation
- Migration validation

#### Structure

```
┌─────────────────────────────────────────────────────────────┐
│           VERI-01: PARALLEL PARITY TESTING                  │
├─────────────────────────────────────────────────────────────┤
│ AGENT:        Parity Verification Agent                     │
│ TOOLS:        browser, terminal, file                       │
│ ITERATIONS:   15-25                                         │
│ TEAM:         Verification                                  │
├─────────────────────────────────────────────────────────────┤
│ WORKFLOW:                                                   │
│ 1. Select test case from test suite                         │
│ 2. Execute test against original system:                    │
│    a. Record inputs                                         │
│    b. Record outputs                                        │
│    c. Record response time                                  │
│ 3. Execute test against new implementation:                 │
│    a. Use identical inputs                                  │
│    b. Record outputs                                        │
│    c. Record response time                                  │
│ 4. Compare results:                                         │
│    a. Output equivalence (semantic)                         │
│    b. Performance comparison                                │
│    c. Error response equivalence                            │
│ 5. Log any divergences                                      │
│ 6. Generate parity report                                   │
├─────────────────────────────────────────────────────────────┤
│ OUTPUT:                                                     │
│ • Parity test results                                       │
│ • Divergence reports                                        │
│ • Performance comparison data                               │
│ • Pass/fail status for each test                            │
└─────────────────────────────────────────────────────────────┘
```

#### AI Agent Delegation Template

```python
def verify_parity(test_cases, original_url, new_url):
    """
    Execute parity testing between original and new system.
    
    Args:
        test_cases: List of test cases to execute
        original_url: Base URL of original system
        new_url: Base URL of new implementation
    """
    
    return delegate_task(
        goal="Verify behavioral parity between systems",
        context=f"""
        ORIGINAL SYSTEM: {original_url}
        NEW IMPLEMENTATION: {new_url}
        
        TEST CASES: {len(test_cases)} tests
        
        PARITY VERIFICATION PROCESS:
        
        For each test case:
        
        1. PREPARE (iteration 1-2):
           - Load test case definition
           - Initialize result storage
           - Configure request parameters
        
        2. EXECUTE ON ORIGINAL (iteration 3-5):
           - Send request to original system
           - Record response status code
           - Record response body (sanitized if needed)
           - Record response headers
           - Record response time
           - Store as baseline
        
        3. EXECUTE ON NEW (iteration 6-8):
           - Send identical request to new system
           - Record response status code
           - Record response body
           - Record response headers
           - Record response time
           - Store as candidate
        
        4. COMPARE (iteration 9-12):
           - Status code match? (exact)
           - Response body equivalent? (semantic)
           - Headers reasonable? (subset/equivalent)
           - Response time within 110%? (performance)
           - Error handling equivalent?
           
           EQUIVALENCE RULES:
           - Status codes: exact match required
           - Response body: semantic equivalence
             (e.g., timestamps may differ format)
           - Headers: required headers present
           - Performance: new within 110% of original
           - Errors: same error type and message pattern
        
        5. LOG RESULTS (iteration 13-15):
           - Pass/Fail status
           - Any divergences logged
           - Evidence captured
           - Performance delta calculated
        
        ACCEPTANCE CRITERIA:
        - 100% functional parity for critical paths
        - 95%+ functional parity overall
        - Performance within 110% of original
        - No behavioral regressions
        
        OUTPUT FILES:
        - parity_results.json: Machine-readable results
        - parity_report.md: Human-readable summary
        - divergences/: Directory of detailed divergence reports
        """,
        toolsets=['browser', 'terminal', 'file'],
        max_iterations=20
    )
```

#### Cross-References
- Used in: Vol. IV, Ch. 16; Vol. VI, Ch. 23-24
- Related: VERI-02 (Regression Detection), DISC-01 (API Probing)
- Complements: IMPL-01 (TDD Implementation)

---

### VERI-02: Automated Regression Detection

**Source**: Pattern from Vol. VI, Ch. 24
**Also Known As**: Regression Testing, Change Impact Analysis

#### Purpose
Automatically detect when changes to the new implementation cause previously working behavior to fail.

#### Structure

```
┌─────────────────────────────────────────────────────────────┐
│         VERI-02: AUTOMATED REGRESSION DETECTION             │
├─────────────────────────────────────────────────────────────┤
│ AGENT:        Regression Detection Agent                    │
│ TOOLS:        terminal, file                                │
│ ITERATIONS:   10-15                                         │
│ TEAM:         Verification                                  │
├─────────────────────────────────────────────────────────────┤
│ WORKFLOW:                                                   │
│ 1. Maintain baseline test results                           │
│ 2. For each code change:                                    │
│    a. Run full test suite                                   │
│    b. Compare results to baseline                           │
│    c. Identify any regressions                              │
│    d. Analyze affected scope                                │
│ 3. Report regressions immediately                           │
│ 4. Block merge if regressions present                       │
│ 5. Update baseline on intentional change                    │
├─────────────────────────────────────────────────────────────┤
│ OUTPUT:                                                     │
│ • Regression reports                                        │
│ • Affected components                                       │
│ • Baseline comparison                                       │
│ • CI/CD gate status                                         │
└─────────────────────────────────────────────────────────────┘
```

#### Cross-References
- Used in: Vol. VI, Ch. 24
- Related: VERI-01 (Parity Testing), IMPL-01 (TDD)
- Complements: COORD-03 (Monitoring Integration)

---

### VERI-03: Property-Based Verification

**Source**: Pattern from Vol. VI, Ch. 25
**Also Known As**: Generative Testing, Fuzzing

#### Purpose
Verify system properties using generated inputs to explore edge cases not covered by example-based tests.

#### Structure

```
┌─────────────────────────────────────────────────────────────┐
│          VERI-03: PROPERTY-BASED VERIFICATION               │
├─────────────────────────────────────────────────────────────┤
│ AGENT:        Property Verification Agent                   │
│ TOOLS:        terminal, file, hypothesis/scalacheck         │
│ ITERATIONS:   20-30                                         │
│ TEAM:         Verification                                  │
├─────────────────────────────────────────────────────────────┤
│ WORKFLOW:                                                   │
│ 1. Identify system properties to verify                     │
│ 2. Define input generators                                  │
│ 3. Formalize properties as assertions                       │
│ 4. Run property tests:                                      │
│    a. Generate random inputs                                │
│    b. Execute operations                                    │
│    c. Verify properties hold                                │
│    d. Shrink failing cases                                  │
│ 5. Report property violations                               │
│ 6. Add found bugs to regression suite                       │
├─────────────────────────────────────────────────────────────┤
│ OUTPUT:                                                     │
│ • Property definitions                                      │
│ • Test execution results                                    │
│ • Discovered edge cases                                     │
│ • Minimal failing examples                                  │
└─────────────────────────────────────────────────────────────┘
```

#### Cross-References
- Used in: Vol. VI, Ch. 25
- Related: DISC-03 (Error Discovery), VERI-01 (Parity)
- Complements: IMPL-01 (TDD)

---

## B.4 Coordination Patterns

Coordination patterns manage the interaction between multiple AI agents.

### COORD-01: Hierarchical Task Delegation

**Source**: Pattern from Vol. IV, Ch. 16; Vol. IV, Ch. 17
**Also Known As**: Tree Delegation, Manager-Worker Pattern

#### Purpose
Coordinate multiple agents through hierarchical structure for complex multi-phase tasks.

#### Structure

```
┌─────────────────────────────────────────────────────────────┐
│         COORD-01: HIERARCHICAL TASK DELEGATION              │
├─────────────────────────────────────────────────────────────┤
│ AGENTS:       Coordinator + Multiple Workers                │
│ STRUCTURE:    Tree hierarchy                                │
│ DEPTH:        2-3 levels typical                            │
├─────────────────────────────────────────────────────────────┤
│ HIERARCHY:                                                  │
│ Level 1: Project Coordinator                                │
│   └─ Level 2: Team Leads (Specification, Implementation,   │
│               Verification)                                 │
│       └─ Level 3: Worker Agents                             │
│           ├─ API Probe Agent                                │
│           ├─ State Machine Agent                            │
│           ├─ Implementation Agent                           │
│           ├─ Test Agent                                     │
│           └─ Quality Assurance Agent                        │
├─────────────────────────────────────────────────────────────┤
│ WORKFLOW:                                                   │
│ 1. Coordinator decomposes project                           │
│ 2. Coordinator assigns to team leads                        │
│ 3. Team leads decompose further                             │
│ 4. Team leads assign to workers                             │
│ 5. Workers execute tasks                                    │
│ 6. Workers report to team leads                             │
│ 7. Team leads aggregate and report up                       │
│ 8. Coordinator integrates all results                       │
├─────────────────────────────────────────────────────────────┤
│ COMMUNICATION:                                              │
│ • Specifications flow down tree                             │
│ • Results flow up tree                                      │
│ • Same-level isolation maintained                           │
│ • No cross-contamination between branches                   │
└─────────────────────────────────────────────────────────────┘
```

#### Cross-References
- Used in: Vol. IV, Ch. 16-17; Vol. V, Ch. 21
- Related: IMPL-02 (Parallel), COORD-02 (Consensus)
- Complements: All other patterns

---

### COORD-02: Consensus-Based Decision Making

**Source**: Pattern from Vol. IV, Ch. 17
**Also Known As**: Voting, Multi-Agent Agreement

#### Purpose
Resolve uncertainty or make decisions requiring multiple perspectives through agent consensus.

#### Structure

```
┌─────────────────────────────────────────────────────────────┐
│       COORD-02: CONSENSUS-BASED DECISION MAKING             │
├─────────────────────────────────────────────────────────────┤
│ AGENTS:       Multiple peer agents (3-7)                    │
│ DECISION:     Complex or ambiguous                          │
│ METHOD:       Distributed voting                            │
├─────────────────────────────────────────────────────────────┤
│ WORKFLOW:                                                   │
│ 1. Pose decision question to multiple agents                │
│ 2. Each agent independently analyzes:                       │
│    a. Review available evidence                             │
│    b. Apply relevant criteria                               │
│    c. Form recommendation                                   │
│    d. Assign confidence level                               │
│ 3. Collect all recommendations                              │
│ 4. Evaluate consensus:                                      │
│    a. Agreement > threshold? (e.g., 80%)                    │
│    b. Confidence adequate?                                  │
│ 5. If consensus: implement decision                         │
│ 6. If no consensus: escalate for human review               │
├─────────────────────────────────────────────────────────────┤
│ OUTPUT:                                                     │
│ • Decision with confidence level                            │
│ • Supporting rationale                                      │
│ • Dissenting opinions (if any)                              │
│ • Escalation flag (if needed)                               │
└─────────────────────────────────────────────────────────────┘
```

#### Cross-References
- Used in: Vol. IV, Ch. 17
- Related: COORD-01 (Hierarchical), COORD-03 (Monitoring)
- Complements: All verification patterns

---

### COORD-03: Continuous Monitoring and Alerting

**Source**: Pattern from Vol. IV, Ch. 17; Vol. VII, Ch. 23
**Also Known As**: Observability Integration, Monitoring Agents

#### Purpose
Maintain continuous awareness of project status, health, and progress through dedicated monitoring agents.

#### Structure

```
┌─────────────────────────────────────────────────────────────┐
│       COORD-03: CONTINUOUS MONITORING AND ALERTING          │
├─────────────────────────────────────────────────────────────┤
│ AGENTS:       Monitoring Agent + Checker Agents             │
│ FREQUENCY:    Continuous/Scheduled                          │
│ ALERTING:     Threshold-based with escalation               │
├─────────────────────────────────────────────────────────────┤
│ MONITORING DUTIES:                                          │
│ 1. Test execution status                                    │
│ 2. Code quality metrics                                     │
│ 3. Performance benchmarks                                   │
│ 4. Clean room compliance status                             │
│ 5. Documentation completeness                               │
│ 6. Schedule adherence                                       │
│ 7. Budget consumption                                       │
│ 8. Risk indicator tracking                                  │
├─────────────────────────────────────────────────────────────┤
│ WORKFLOW:                                                   │
│ 1. Monitor agent polls data sources                         │
│ 2. Metrics stored in time-series database                   │
│ 3. Rules engine evaluates thresholds                        │
│ 4. Alerts generated on threshold breach                     │
│ 5. Escalation rules route to appropriate owner              │
│ 6. Dashboard updates for visualization                      │
├─────────────────────────────────────────────────────────────┤
│ OUTPUT:                                                     │
│ • Real-time dashboard                                       │
│ • Automated alerts                                          │
│ • Trend reports                                             │
│ • Early warning indicators                                  │
└─────────────────────────────────────────────────────────────┘
```

#### Cross-References
- Used in: Vol. IV, Ch. 17; Vol. VII, Ch. 23
- Related: VERI-02 (Regression), A.2.4 (Compliance Audit)
- Complements: All project management

---

## B.5 Migration Patterns

Patterns for migrating from original to new system.

### MIGR-01: Big Bang Migration

**Source**: Pattern from Vol. VII, Ch. 22
**Also Known As**: Cutover Migration, Flash Cut

#### Purpose
Migrate entire system usage from original to new implementation in a single event.

#### When to Use
- Simple, stateless systems
- Small user base
- Well-understood failure modes
- Strong rollback capability

#### Structure

```
┌─────────────────────────────────────────────────────────────┐
│            MIGR-01: BIG BANG MIGRATION                      │
├─────────────────────────────────────────────────────────────┤
│ RISK LEVEL:   High                                          │
│ DOWNTIME:     Hours to days                                 │
│ ROLLBACK:     Must be prepared                              │
│ TIMING:       Off-peak window                               │
├─────────────────────────────────────────────────────────────┤
│ PHASES:                                                     │
│ 1. FINAL PREPARATION (2-4 weeks before)                     │
│    - All testing complete                                   │
│    - Rollback scripts tested                                │
│    - Communication sent to all users                        │
│    - Support team on standby                                │
│                                                             │
│ 2. DATA MIGRATION (hours before cutover)                    │
│    - Final data sync from old to new                        │
│    - Validation of migrated data                            │
│    - Incremental sync for changes during migration          │
│                                                             │
│ 3. CUTOVER (maintenance window)                             │
│    - Put old system in read-only (if possible)              │
│    - Final data sync                                        │
│    - Switch DNS/load balancer to new system                 │
│    - Verify new system responding                           │
│    - Smoke tests pass                                       │
│                                                             │
│ 4. VALIDATION (hours after cutover)                         │
│    - Monitor metrics closely                                │
│    - Support team active response                           │
│    - User feedback collected                                │
│    - Decision: stabilize or rollback                        │
│                                                             │
│ 5. STABILIZATION (days after)                               │
│    - Normal operations monitoring                           │
│    - Issue resolution                                       │
│    - Performance optimization                               │
│    - Decommission old system                                │
├─────────────────────────────────────────────────────────────┤
│ SUCCESS FACTORS:                                            │
│ • Comprehensive testing done                                │
│ • Rollback tested and ready                                 │
│ • Support team prepared                                     │
│ • Communication plan executed                               │
│ • Monitoring in place                                       │
└─────────────────────────────────────────────────────────────┘
```

#### Cross-References
- Used in: Vol. VII, Ch. 22
- Related: A.3.5 (Deployment Readiness)
- Complements: VERI-01 (Parity Testing)

---

### MIGR-02: Database Migration

**Source**: Pattern from Vol. VII, Ch. 22
**Also Known As**: Data Migration, ETL Migration

#### Purpose
Migrate data from original system storage to new system storage while maintaining integrity.

#### Structure

```
┌─────────────────────────────────────────────────────────────┐
│            MIGR-02: DATABASE MIGRATION                      │
├─────────────────────────────────────────────────────────────┤
│ APPROACHES:                                                 │
│ 1. Full reload (small data sets)                            │
│ 2. Incremental sync (large data sets)                       │
│ 3. Dual-write (zero downtime)                               │
│ 4. Event sourcing replay (event-based systems)              │
├─────────────────────────────────────────────────────────────┤
│ WORKFLOW:                                                   │
│ 1. Schema mapping (old schema → new schema)                 │
│ 2. Data transformation rules defined                        │
│ 3. Extraction process created                               │
│ 4. Load process created                                     │
│ 5. Validation rules defined                                 │
│ 6. Migration rehearsal (multiple times)                     │
│ 7. Final migration execution                                │
│ 8. Post-migration validation                                │
│ 9. Incremental sync until cutover                           │
├─────────────────────────────────────────────────────────────┤
│ VALIDATION:                                                 │
│ • Row counts match                                          │
│ • Random sampling checks pass                               │
│ • Aggregations match                                        │
│ • Referential integrity maintained                          │
│ • Constraints verified                                      │
└─────────────────────────────────────────────────────────────┘
```

#### Cross-References
- Used in: Vol. VII, Ch. 22
- Related: DISC-04 (Data Flow), A.3.1 (Integration Testing)
- Complements: MIGR-01, MIGR-03

---

### MIGR-03: Strangler Fig Pattern

**Source**: Pattern from Vol. V, Ch. 18; Vol. VII, Ch. 21
**Also Known As**: Incremental Migration, Modular Replacement

#### Purpose
Gradually replace original system components with new implementation while maintaining fully operational system throughout.

#### Structure

```
┌─────────────────────────────────────────────────────────────┐
│          MIGR-03: STRANGLER FIG PATTERN                     │
├─────────────────────────────────────────────────────────────┤
│ RISK LEVEL:   Low (per increment)                           │
│ DOWNTIME:     Minimal (per component)                       │
│ COMPLEXITY:   High (routing and coordination)               │
│ DURATION:     Months to years                               │
├─────────────────────────────────────────────────────────────┤
│ ARCHITECTURE:                                               │
│                                                             │
│   Users                                                     │
│     │                                                       │
│     ▼                                                       │
│  ┌─────────────────┐                                        │
│  │ Request Router  │ Route based on feature flags/config    │
│  │ (Strangler Fig) │                                        │
│  └────────┬────────┘                                        │
│           │                                                 │
│     ┌─────┴─────┐                                           │
│     ▼           ▼                                           │
│  ┌────────┐  ┌──────────┐                                   │
│  │ Legacy │  │ New Impl │                                   │
│  │ System │  │ (Module) │                                   │
│  └────────┘  └──────────┘                                   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ WORKFLOW:                                                   │
│ 1. Identify module boundaries in legacy system              │
│ 2. Implement router/strangler facade                        │
│ 3. Route 0% traffic to new module (testing)                 │
│ 4. Route 1% traffic (canary)                                │
│ 5. Gradually increase to 100%                               │
│ 6. Remove legacy module                                     │
│ 7. Repeat for next module                                   │
├─────────────────────────────────────────────────────────────┤
│ ADVANTAGES:                                                 │
│ • Continuous operation                                      │
│ • Risk spread across time                                   │
│ • Learning and adjustment                                   │
│ • Early value delivery                                      │
│                                                             │
│ CHALLENGES:                                                 │
│ • Data synchronization                                      │
│ • Transaction consistency across systems                    │
│ • Complex routing logic                                     │
│ • Extended project duration                                 │
└─────────────────────────────────────────────────────────────┘
```

#### Cross-References
- Used in: Vol. V, Ch. 18; Vol. VII, Ch. 21
- Related: IMPL-04 (Modular), COORD-03 (Monitoring)
- Complements: VERI-01 (Parity Testing)

---

## B.6 Pattern Quick Reference Index

### By Category

| Category | Pattern ID | Name | Page Reference |
|----------|------------|------|----------------|
| Discovery | DISC-01 | Systematic API Probing | B.1.1 |
| Discovery | DISC-02 | State Machine Discovery | B.1.2 |
| Discovery | DISC-03 | Error Condition Cataloging | B.1.3 |
| Discovery | DISC-04 | Data Flow Mapping | B.1.4 |
| Discovery | DISC-05 | Performance Baseline | B.1.5 |
| Implementation | IMPL-01 | TDD by Agent | B.2.1 |
| Implementation | IMPL-02 | Parallel Feature Development | B.2.2 |
| Implementation | IMPL-03 | Spec-Driven Implementation | B.2.3 |
| Implementation | IMPL-04 | Modular Decomposition | B.2.4 |
| Verification | VERI-01 | Parallel Parity Testing | B.3.1 |
| Verification | VERI-02 | Automated Regression Detection | B.3.2 |
| Verification | VERI-03 | Property-Based Verification | B.3.3 |
| Coordination | COORD-01 | Hierarchical Task Delegation | B.4.1 |
| Coordination | COORD-02 | Consensus-Based Decision Making | B.4.2 |
| Coordination | COORD-03 | Continuous Monitoring | B.4.3 |
| Migration | MIGR-01 | Big Bang Migration | B.5.1 |
| Migration | MIGR-02 | Database Migration | B.5.2 |
| Migration | MIGR-03 | Strangler Fig Pattern | B.5.3 |

### By Volume Reference

| Volume/Chapter | Patterns Referenced |
|----------------|---------------------|
| Vol. IV, Ch. 16 | DISC-01, DISC-02, IMPL-01, IMPL-02, VERI-01, COORD-01 |
| Vol. IV, Ch. 17 | IMPL-01, COORD-01, COORD-02, COORD-03 |
| Vol. V, Ch. 18 | DISC-04, IMPL-04, MIGR-03 |
| Vol. V, Ch. 19 | DISC-02 |
| Vol. V, Ch. 20 | IMPL-01, IMPL-03 |
| Vol. V, Ch. 21 | IMPL-02, COORD-01, COORD-02 |
| Vol. VI, Ch. 23 | VERI-01 |
| Vol. VI, Ch. 24 | VERI-01, VERI-02 |
| Vol. VI, Ch. 25 | DISC-03, VERI-03 |
| Vol. VI, Ch. 26 | DISC-05 |
| Vol. VI, Ch. 27 | DISC-01 |
| Vol. VII, Ch. 21 | IMPL-04, MIGR-03 |
| Vol. VII, Ch. 22 | MIGR-01, MIGR-02, MIGR-03 |
| Vol. VII, Ch. 23 | COORD-03 |

### By Phase of Implementation

| Phase | Recommended Patterns |
|-------|---------------------|
| Pre-Implementation | None (planning phase) |
| Phase 1: Discovery | DISC-01, DISC-02, DISC-03, DISC-04, DISC-05 |
| Phase 2: Implementation | IMPL-01, IMPL-02, IMPL-03, IMPL-04, COORD-01, COORD-02, COORD-03 |
| Phase 3: Verification | VERI-01, VERI-02, VERI-03, COORD-03 |
| Phase 4: Migration | MIGR-01, MIGR-02, MIGR-03 |

### Pattern Selection Flowchart

```
START: Need to perform task
    │
    ├─→ Discovering original system behavior?
    │   └─→ Use DISC series (B.1)
    │
    ├─→ Implementing new features?
    │   └─→ Use IMPL series (B.2)
    │       ├─→ Single feature? Use IMPL-01
    │       ├─→ Multiple independent features? Use IMPL-02
    │       └─→ Well-specified contract? Use IMPL-03
    │
    ├─→ Verifying implementation?
    │   └─→ Use VERI series (B.3)
    │       └─→ Checking parity with original? Use VERI-01
    │
    ├─→ Coordinating multiple agents?
    │   └─→ Use COORD series (B.4)
    │       └─→ Complex task breakdown? Use COORD-01
    │
    └─→ Migrating to new system?
        └─→ Use MIGR series (B.5)
            ├─→ Small/simple system? Consider MIGR-01
            ├─→ Data migration? Use MIGR-02
            └─→ Large system? Use MIGR-03
```

---

*End of Appendix B - Approximately 20 pages*
