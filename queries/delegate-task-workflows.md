---
title: Delegate Task Workflows for Clean Room
created: 2026-04-15
updated: 2026-04-15
type: query
tags: [agent-delegation, delegate-task, subagent-orchestration, agent-workflow, autonomous-development]
sources: []
---

# Delegate Task Workflows for Clean Room

This document provides practical examples and workflows for using `delegate_task` to create autonomous subagent teams for clean room implementation.

## Core Concepts

### delegate_task Tool

The `delegate_task` tool spawns independent subagent processes that work autonomously on defined tasks. Each subagent has its own conversation, terminal session, and toolset.

### Key Properties

```python
delegate_task(
    goal="What the subagent should accomplish",
    context="Background information the subagent needs",
    toolsets=["toolset1", "toolset2"],  # Available tools
    max_iterations=50,  # Max tool-calling turns
    toolsets=['browser', 'terminal', 'file']  # Common combination
)
```

## Workflow 1: Feature Implementation Pipeline

### Overview

End-to-end workflow for implementing a feature using subagent delegation.

```
FEATURE_IMPLEMENTATION:
  1. Spec Agent → Creates tests
  2. Impl Agent → Writes code
  3. Test Agent → Validates tests
  4. Verify Agent → Checks parity
  5. Commit Agent → Commits changes
```

### Implementation

```python
class FeatureImplementationPipeline:
    def __init__(self, feature_name):
        self.feature = feature_name
    
    def execute(self):
        """
        Execute full feature implementation pipeline
        """
        # Step 1: Specification
        spec_result = self._create_specification()
        
        # Step 2: Implementation
        impl_result = self._implement_feature(spec_result)
        
        # Step 3: Testing
        test_result = self._run_tests(impl_result)
        
        # Step 4: Verification
        verify_result = self._verify_parity(test_result)
        
        # Step 5: Commit
        commit_result = self._commit_changes(verify_result)
        
        return {
            'feature': self.feature,
            'spec': spec_result,
            'implementation': impl_result,
            'tests': test_result,
            'verification': verify_result,
            'commit': commit_result
        }
    
    def _create_specification(self):
        """
        Spawn specification agent
        """
        return delegate_task(
            goal=f"Create behavioral tests for {self.feature} feature",
            context=f"""
            Your task: Create pytest test suite for {self.feature}
            
            Original system to observe:
            - Base URL: https://api.original-system.com/v1
            - Documentation: See raw/specs/original-api-docs.md
            
            Requirements:
            1. Probe all {self.feature} endpoints
            2. Document request/response formats
            3. Identify error conditions
            4. Create comprehensive pytest test cases
            
            Output format:
            - Directory: tests/behavioral/spec_{self.feature}/
            - Files: test_spec_{self.feature}.py
            - Each test: Clear behavior description in docstring
            
            Constraint: Observe original only, do NOT implement
            """,
            toolsets=['browser', 'terminal', 'file'],
            max_iterations=25
        )
    
    def _implement_feature(self, spec_result):
        """
        Spawn implementation agent (with sanitized context)
        """
        # Extract only test file contents, remove original system reference
        test_files = self._extract_tests(spec_result)
        
        return delegate_task(
            goal=f"Implement {self.feature} using TDD",
            context=f"""
            Your task: Write implementation code using Test-Driven Development
            
            Test suite to pass:
            {''.join(test_files)}
            
            TDD Cycle:
            1. RED: Run tests - they should fail
            2. GREEN: Write minimal code to pass
            3. REFACTOR: Improve code quality
            
            Project structure:
            - Source: src/{self.feature}/
            - Tests: tests/behavioral/spec_{self.feature}/
            - Run: pytest tests/behavioral/spec_{self.feature}/ -v
            
            Constraints:
            - NO access to original system
            - NO peeking at original implementation
            - Follow TDD strictly - write code ONLY to pass tests
            
            Deliverable:
            - Implementation in src/{self.feature}/
            - All tests passing
            - Clean code, no TODOs
            """,
            toolsets=['terminal', 'file'],
            max_iterations=40
        )
    
    def _run_tests(self, impl_result):
        """
        Spawn test validation agent
        """
        return delegate_task(
            goal=f"Run and validate all tests for {self.feature}",
            context=f"""
            Your task: Run test suite and validate results
            
            Project location: /workspace/{self.feature}/
            
            Test commands:
            - Unit tests: pytest tests/ -v
            - Behavioral tests: pytest tests/behavioral/ -v
            - Integration tests: pytest tests/integration/ -v
            
            Acceptance criteria:
            - All tests pass (exit code 0)
            - No warnings
            - Test coverage > 95%
            
            Output:
            - Test results summary
            - Coverage report
            - Any failures with fixes
            """,
            toolsets=['terminal'],
            max_iterations=15
        )
    
    def _verify_parity(self, test_result):
        """
        Spawn verification agent
        """
        return delegate_task(
            goal=f"Verify behavioral parity for {self.feature}",
            context=f"""
            Your task: Verify new implementation matches original behavior
            
            New implementation: /workspace/{self.feature}/new/
            Original system: https://api.original-system.com/v1
            
            Parity test:
            1. Run identical inputs to both systems
            2. Compare outputs for equivalence
            3. Flag any divergences
            
            Test cases from: tests/behavioral/spec_{self.feature}/test_*.py
            
            Acceptance:
            - All parity tests pass
            - Zero divergences
            - Performance within 20% of original
            
            Output:
            - Parity report
            - Any divergences found
            - Performance comparison
            """,
            toolsets=['browser', 'terminal', 'file'],
            max_iterations=20
        )
    
    def _commit_changes(self, verify_result):
        """
        Spawn commit agent
        """
        if verify_result['all_passed']:
            return delegate_task(
                goal=f"Commit {self.feature} implementation",
                context=f"""
                Your task: Commit changes with proper messages
                
                Changes to commit:
                - src/{self.feature}/ - new implementation
                - tests/behavioral/spec_{self.feature}/ - test suite
                
                Commit requirements:
                - Signed off commit message
                - Reference feature ticket
                - Include test and parity verification
                
                Commit format:
                feat({self.feature}): implement with behavioral parity
                
                Co-authored-by: <your-name>
                Tested-by: automated parity verification
                Verified-by: <your-name>
                """,
                toolsets=['terminal'],
                max_iterations=5
            )
        else:
            return {'committed': False, 'reason': 'verification failed'}
```

## Workflow 2: Parallel API Discovery

### Overview

Multiple agents simultaneously discover different API surfaces.

```python
class ParallelAPIDiscovery:
    def __init__(self):
        self.endpoints = {
            'users': 'https://api.system.com/v1/users',
            'auth': 'https://api.system.com/v1/auth',
            'orders': 'https://api.system.com/v1/orders',
            'inventory': 'https://api.system.com/v1/inventory',
            'reports': 'https://api.system.com/v1/reports',
        }
    
    def discover_all(self):
        """
        Discover all APIs in parallel
        """
        # Create discovery tasks
        tasks = []
        for endpoint_name, endpoint_url in self.endpoints.items():
            task = delegate_task(
                goal=f"Discover API specification for {endpoint_name}",
                context=f"""
                Your task: Map {endpoint_name} API behavior
                
                API endpoint: {endpoint_url}
                
                Discovery checklist:
                1. List all endpoints under this path
                2. Document each endpoint's methods
                3. Record request parameters
                4. Record response formats
                5. Identify error conditions
                
                Output:
                - YAML specification file
                - pytest test cases
                
                File: specs/{endpoint_name}_api.yaml
                Tests: tests/behavioral/spec_{endpoint_name}.py
                """,
                toolsets=['browser', 'terminal', 'file'],
                max_iterations=20
            )
            tasks.append((endpoint_name, task))
        
        # Wait for all to complete
        results = {}
        for name, task in tasks:
            results[name] = task.result()
        
        # Merge results
        merged = self._merge_discoveries(results)
        
        return merged
    
    def _merge_discoveries(self, discoveries):
        """
        Merge multiple API discovery results
        """
        merged = {
            'endpoints': {},
            'tests': {}
        }
        
        for name, discovery in discoveries.items():
            merged['endpoints'][name] = discovery.specification
            merged['tests'][name] = discovery.tests
        
        return merged
```

## Workflow 3: Edge Case Discovery Swarm

### Overview

Multiple agents systematically discover edge cases.

```python
class EdgeCaseSwarm:
    def __init__(self):
        self.agent_templates = [
            {
                'name': 'boundary_agent',
                'goal': 'Discover boundary condition behaviors',
                'focus': 'min/max values, empty/null, overflow'
            },
            {
                'name': 'type_agent',
                'goal': 'Discover type variation behaviors',
                'focus': 'type coercion, encoding, charset'
            },
            {
                'name': 'state_agent',
                'goal': 'Discover state machine transitions',
                'focus': 'valid transitions, invalid states'
            },
            {
                'name': 'error_agent',
                'goal': 'Discover error handling behaviors',
                'focus': 'error recovery, partial failures'
            },
            {
                'name': 'timing_agent',
                'goal': 'Discover timing-related behaviors',
                'focus': 'concurrency, race conditions, timeouts'
            },
        ]
    
    def discover_all(self):
        """
        Run all edge case discovery agents
        """
        findings = {}
        
        for agent_template in self.agent_templates:
            result = delegate_task(
                goal=agent_template['goal'],
                context=f"""
                Your task: Discover {agent_template['focus']} edge cases
                
                Focus areas:
                {agent_template['focus']}
                
                System to test: https://api.system.com/v1
                
                Output:
                - List of edge cases discovered
                - Test cases for each edge case
                - Behavior observations
                
                File: edge_cases/{agent_template['name']}_findings.md
                Tests: tests/edge_cases/test_{agent_template['name']}.py
                """,
                toolsets=['browser', 'terminal', 'file'],
                max_iterations=25
            )
            findings[agent_template['name']] = result
        
        # Aggregate findings
        return self._aggregate_findings(findings)
```

## Workflow 4: Multi-Feature Implementation

### Overview

Implement multiple features with proper dependency management.

```python
class MultiFeatureImplementation:
    def __init__(self, features):
        """
        features: list of dicts with 'name' and 'dependencies'
        """
        self.features = features
    
    def execute(self):
        """
        Execute multi-feature implementation
        """
        # Topological sort for dependency order
        ordered = self._topological_sort()
        
        results = {}
        
        for feature in ordered:
            print(f"Implementing {feature['name']}...")
            
            # Get specs for all dependencies first
            spec_files = []
            for dep in feature.get('dependencies', []):
                if dep in results:
                    spec_files.extend(results[dep].get('test_specs', []))
            
            # Implement current feature
            result = self._implement_single(
                feature['name'],
                feature.get('dependencies', []),
                spec_files
            )
            
            results[feature['name']] = result
        
        return results
    
    def _implement_single(self, feature_name, dependencies, spec_files):
        """
        Implement single feature with dependency specs
        """
        # Specification
        spec = delegate_task(
            goal=f"Create tests for {feature_name}",
            context=f"""
            Create tests for {feature_name}
            
            Dependency specs (for integration tests):
            {' '.join(spec_files)}
            
            Output: test_{feature_name}.py
            """,
            toolsets=['terminal', 'file'],
            max_iterations=20
        )
        
        # Implementation
        impl = delegate_task(
            goal=f"Implement {feature_name}",
            context=f"""
            Implement {feature_name} passing spec tests
            
            Tests: {spec.output_path}
            
            Output: src/{feature_name}/
            """,
            toolsets=['terminal', 'file'],
            max_iterations=30
        )
        
        return {
            'feature': feature_name,
            'test_specs': spec.output_path,
            'implementation': impl.output_path
        }
```

## Common Patterns

### Pattern 1: Chained Delegation

```python
# Chain: Spec → Impl → Test → Verify → Commit
spec = delegate_task(goal="Create tests", ...)
impl = delegate_task(
    goal="Implement",
    context=f"Tests: {spec.output}",
    ...
)
test = delegate_task(
    goal="Run tests",
    context=f"Implementation: {impl.output}",
    ...
)
```

### Pattern 2: Fan-out Discovery

```python
# Fan-out: Multiple agents discover different parts
agents = [
    delegate_task(goal="Discover API A", ...),
    delegate_task(goal="Discover API B", ...),
    delegate_task(goal="Discover API C", ...),
]
results = [a.result() for a in agents]
```

### Pattern 3: Aggregation

```python
# Aggregate: Collect and merge results
all_findings = self._merge_results(results)
```

## Best Practices

### Practice 1: Clear Context

Provide complete context in delegate_task:

```python
# Good
context = """
Your task: Implement X
Background: Y
Constraints: Z
Output format: A
"""

# Bad
context = "Implement X"
```

### Practice 2: Manage Context Size

Keep context manageable:

```python
# Chunk large contexts
large_context = """
[First part - 500 chars]
"""
task1 = delegate_task(context=large_context, ...)

# Then pass summary to next task
summary = """
[Summary of task1 result - 100 chars]
"""
task2 = delegate_task(context=summary, ...)
```

### Practice 3: Error Handling

```python
try:
    result = delegate_task(...)
    if result.failed:
        # Retry with adjusted context
        result = delegate_task(context=adjusted, ...)
except Exception as e:
    # Log and handle
    pass
```

### Practice 4: Verification

Always verify agent outputs:

```python
result = delegate_task(...)

# Check output validity
if not self._validate_output(result):
    # Request revision
    revision = delegate_task(
        goal="Revise based on feedback",
        context=f"Feedback: {self._get_feedback(result)}",
        ...
    )
```

## Pitfalls

### Pitfall 1: Context Switching

Too many agents with small tasks creates overhead.

**Solution:** Group related work into larger tasks.

### Pitfall 2: Lost Context

Subagents lose context between iterations.

**Solution:** Keep contexts self-contained, summarize progress between tasks.

### Pitfall 3: Circular Dependencies

Agent A depends on B, B depends on A.

**Solution:** Use topological sort, resolve dependencies first.

### Pitfall 4: No Isolation

Agents sharing forbidden information.

**Solution:** Sanitize context before passing between agent types.

## Related Concepts

- [[ai-agent-methodologies]]
- [[multi-agent-coordination]]
- [[delegate-task-workflows]]
- [[clean-room-engineering]]
- [[test-driven-development]]