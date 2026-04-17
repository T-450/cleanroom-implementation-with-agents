---
title: Multi-Agent Coordination
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [multi-agent, agent-coordination, agent-workflow, clean-room-methodology, ai-agent]
sources: []
---

# Multi-Agent Coordination for Clean Room

This page covers coordination patterns and protocols for managing multiple AI agents working together on clean room implementation projects.

## Coordination Challenges

### Challenge 1: Agent Isolation

Agents must operate in isolated environments to maintain clean room integrity:

```
ISOLATION_REQUIREMENTS:
  
  Observation Agents:
    - Can access original system APIs
    - Cannot access implementation codebase
    - Cannot communicate with implementation agents directly
    
  Implementation Agents:
    - Can access test specifications
    - Cannot access original system
    - Cannot communicate with observation agents directly
    
  Verification Agents:
    - Can access both systems for comparison
    - Cannot modify either system
    - Only communicates with orchestration layer
```

### Challenge 2: Information Flow

Controlled flow of information between agents:

```
INFORMATION_FLOW_MATRIX:
  
  | From/To       | Observation | Implementation | Verification |
  |---------------|-------------|----------------|---------------|
  | Observation   |     -       |   (blocked)    |      ✓        |
  | Implementation| (blocked)   |       -        |      ✓        |
  | Verification  |     ✓       |       ✓        |       -       |
  | Orchestration |     ✓       |       ✓        |      ✓        |
```

### Challenge 3: Conflict Resolution

Multiple agents may produce conflicting outputs:

```
CONFLICT_TYPES:
  
  - Duplicate work: Two agents working on same feature
  - Specification conflict: Two agents observing different behaviors
  - Implementation conflict: Two agents modifying same code
  - Verification conflict: Two agents reporting different results
```

## Coordination Patterns

### Pattern 1: Centralized Coordinator

A single orchestrator agent manages all other agents.

```
COORDINATOR_ARCHITECTURE:
  
  Coordinator Agent
        │
        ├──→ Task Queue
        │       │
        │       └──→ Worker Agent Pool
        │
        ├──→ State Store
        │       │
        │       └──→ Consistency Checks
        │
        └──→ Conflict Resolver
                │
                └──→ Resolution Policies
```

### Implementation

```python
class CentralizedOrchestrator:
    def __init__(self):
        self.task_queue = asyncio.Queue()
        self.agent_pool = {}
        self.state_store = AgentStateStore()
        self.conflict_resolver = ConflictResolver()
    
    async def assign_task(self, task_spec):
        """
        Assign task to appropriate agent
        """
        # Determine agent type needed
        agent_type = self._determine_agent_type(task_spec)
        
        # Find available agent
        agent = self._find_available_agent(agent_type)
        
        if agent:
            await self.task_queue.put({
                'agent': agent.id,
                'task': task_spec,
                'deadline': task_spec.deadline
            })
            return agent.id
        else:
            # Agent pool exhausted, create new agent
            return await self._create_agent(agent_type)
```

### Pattern 2: Distributed Coordination

Agents coordinate directly without a central coordinator.

```
DISTRIBUTED_COORDINATION:
  
  Agent A ←→ Agent B ←→ Agent C
      ↑         ↑         ↑
      └─────────┴─────────┘
          Peer Sync
```

### Implementation

```python
class DistributedAgentCoordinator:
    def __init__(self):
        self.known_agents = {}
        self.work_registry = {}
    
    def register_agent(self, agent_id, capabilities):
        """
        Agent announces itself and capabilities
        """
        self.known_agents[agent_id] = {
            'capabilities': capabilities,
            'status': 'available',
            'current_work': None
        }
        
        # Broadcast registration
        self._broadcast(f"AGENT_REGISTERED:{agent_id}:{capabilities}")
    
    def claim_work(self, agent_id, work_spec):
        """
        Agent claims work from registry
        """
        if work_spec.id in self.work_registry:
            # Check if already claimed
            existing = self.work_registry[work_spec.id]
            if existing['claimed_by']:
                # Conflict: work already claimed
                raise WorkAlreadyClaimedError(work_spec.id)
            
            # Claim the work
            self.work_registry[work_spec.id]['claimed_by'] = agent_id
            self.work_registry[work_spec.id]['claimed_at'] = now()
            
            return work_spec
        else:
            # Work not in registry, add and claim
            self.work_registry[work_spec.id] = {
                'spec': work_spec,
                'claimed_by': agent_id,
                'claimed_at': now(),
                'result': None
            }
            return work_spec
```

### Pattern 3: Hierarchical Agent Teams

Agents organized in hierarchical teams with clear reporting lines.

```
HIERARCHICAL_TEAMS:
  
  Level 1: Project Coordinator
          │
          ├──→ Team A (Observation)
          │       │
          │       ├──→ Sub-agent A1
          │       ├──→ Sub-agent A2
          │       └──→ Sub-agent A3
          │
          ├──→ Team B (Implementation)
          │       │
          │       ├──→ Sub-agent B1
          │       ├──→ Sub-agent B2
          │       └──→ Sub-agent B3
          │
          └──→ Team C (Verification)
                  │
                  ├──→ Sub-agent C1
                  └──→ Sub-agent C2
```

### Implementation

```python
class HierarchicalTeam:
    def __init__(self, team_type, lead_agent):
        self.team_type = team_type
        self.lead = lead_agent
        self.members = []
    
    def add_member(self, agent):
        """
        Add agent to team
        """
        self.members.append(agent)
        agent.lead = self.lead
    
    async def execute_task(self, task_spec):
        """
        Execute task through team delegation
        """
        # Lead determines team assignment
        assignments = self.lead._distribute_task(task_spec)
        
        # Execute assignments in parallel
        futures = [
            member.execute_task(assignment)
            for member, assignment in assignments
        ]
        
        # Collect results
        results = await asyncio.gather(*futures)
        
        # Lead aggregates results
        return self.lead._aggregate_results(results)
```

## Communication Protocols

### Protocol 1: Handoff Messages

Structured messages for agent handoffs.

```python
HANDOFF_MESSAGE_SCHEMA:
  type: "handoff"
  from_agent: str
  to_agent: str
  payload:
    type: "specification" | "test_suite" | "implementation"
    content: object
    checksum: str
    signature: str
  
  metadata:
    timestamp: datetime
    version: int
    previous_handoffs: list
  
  integrity:
    signature_algorithm: "sha256"
    signing_key: "handoff_private_key"
```

### Protocol 2: Status Updates

Regular status updates from agents.

```python
STATUS_UPDATE_SCHEMA:
  type: "status"
  agent_id: str
  status: "idle" | "working" | "blocked" | "error"
  current_task: str | null
  progress:
    completed_steps: int
    total_steps: int
    estimated_remaining: int
  
  blockers:
    - blocker_description
    - blocker_description
  
  metrics:
    tasks_completed: int
    tasks_failed: int
    hours_worked: float
```

### Protocol 3: Conflict Resolution Messages

Messages for resolving agent conflicts.

```python
CONFLICT_RESOLUTION_SCHEMA:
  type: "conflict"
  conflict_id: str
  conflicting_agents: [agent_id, agent_id]
  conflict_type: "work_overlap" | "spec_divergence" | "implementation_conflict"
  proposed_resolutions:
    - resolution_option_1
    - resolution_option_2
  recommendation: resolution_option_1
  escalation_required: bool
```

## Coordination Tools

### Tool 1: Task Registry

Central registry for tracking agent tasks.

```python
class TaskRegistry:
    def __init__(self):
        self.tasks = {}
        self.locks = {}
    
    def register_task(self, task_id, task_spec, agent_id):
        """
        Register a new task
        """
        with self._lock(task_id):
            self.tasks[task_id] = {
                'spec': task_spec,
                'agent_id': agent_id,
                'status': 'claimed',
                'created_at': now(),
                'completed_at': None,
                'result': None
            }
    
    def get_task(self, task_id):
        """
        Get task status
        """
        return self.tasks.get(task_id)
    
    def complete_task(self, task_id, result):
        """
        Mark task complete
        """
        with self._lock(task_id):
            self.tasks[task_id]['status'] = 'completed'
            self.tasks[task_id]['completed_at'] = now()
            self.tasks[task_id]['result'] = result
```

### Tool 2: Conflict Detector

Automated detection of agent conflicts.

```python
class ConflictDetector:
    def __init__(self, task_registry):
        self.registry = task_registry
    
    def detect_overlapping_work(self):
        """
        Detect when agents are working on same things
        """
        tasks = self.registry.get_all_tasks()
        
        conflicts = []
        for task in tasks:
            if self._is_overlapping(task):
                conflicts.append({
                    'task': task,
                    'agents': self._find_conflicting_agents(task)
                })
        
        return conflicts
    
    def _is_overlapping(self, task):
        """
        Check if task overlaps with other tasks
        """
        # Compare task signatures
        signature = self._task_signature(task)
        
        for other_task in self.registry.get_all_tasks():
            if other_task.id != task.id:
                other_sig = self._task_signature(other_task)
                if self._signatures_overlap(signature, other_sig):
                    return True
        
        return False
```

## Coordination Best Practices

### Practice 1: Clear Task Boundaries

Define clear boundaries for agent work:

```
TASK_BOUNDARY_RULES:
  - Each task has exactly one owning agent
  - Tasks are small enough to complete independently
  - Task outputs are clearly defined
  - Task dependencies are explicit
```

### Practice 2: Regular Heartbeats

Agents send regular heartbeats to indicate status:

```
HEARTBEAT_SCHEDULE:
  - Idle agents: every 5 minutes
  - Working agents: every 1 minute
  - Blocked agents: every 30 seconds
  
HEARTBEAT_CONTENT:
  - Status
  - Current task progress
  - Any blockers
```

### Practice 3: Deadman Switch

If an agent stops sending heartbeats, its work is reassigned:

```
DEADMAN_SWITCH:
  - Heartbeat timeout: 5 minutes
  - On timeout: Mark agent as dead
  - Reclaim all work
  - Reassign to available agents
  - Log incident for investigation
```

### Practice 4: Audit Trail

All agent actions are logged for audit:

```
AUDIT_LOG_ENTRIES:
  - Agent registration
  - Task claim/release
  - Task completion
  - Handoff events
  - Conflict resolutions
  - Status changes
  - Deadman events
```

## Coordination Pitfalls

### Pitfall 1: Bottleneck Coordinator

A single coordinator agent becomes a bottleneck.

**Mitigation:**
- Use distributed coordination where possible
- Horizontal scale coordinator agents
- Batch task assignments

### Pitfall 2: Information Leakage

Agents inadvertently share forbidden information.

**Mitigation:**
- Strict network segmentation
- Automated content filtering on messages
- Regular audits of message content

### Pitfall 3: Coordination Overhead

Too much coordination creates latency.

**Mitigation:**
- Minimize synchronous coordination
- Use asynchronous message passing
- Batch coordination where appropriate

### Pitfall 4: Single Point of Failure

Coordinator agent failure halts all work.

**Mitigation:**
  - Coordinator redundancy
  - Automatic failover
  - State persistence for recovery

## Related Concepts

- [[ai-agent-methodologies]]
- [[ai-agent-patterns]]
- [[delegate-task-workflows]]
- [[clean-room-engineering]]