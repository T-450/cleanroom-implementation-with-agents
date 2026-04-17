---
title: Chapter 27 - Specification Agent Patterns
created: 2026-04-15
updated: 2026-04-15
volume: VI
chapter_number: 27
pages_target: 20
type: chapter
tags: [specification-patterns, api-discovery, behavior-extraction, agent-patterns, clean-room-specification]
---

# Chapter 27: Specification Agent Patterns

Specification agents form the foundation of clean room engineering. They are responsible for observing and documenting the behavior of systems without accessing implementation details. This chapter provides comprehensive patterns for building specification agents using the Hermes `delegate_task` system.

## Chapter Objectives

By the end of this chapter, you will be able to:
- Deploy API discovery agents that systematically map system behaviors
- Implement behavior extraction agents using multiple observation strategies
- Generate formal specifications from observed behaviors
- Manage specification versioning and dependency tracking
- Integrate specification agents into multi-agent clean room workflows

## 27.1 Overview of Specification Agent Architecture

Specification agents operate under strict isolation requirements. They may observe the original system's behavior but must never access its internal implementation details. This creates a one-way information flow from the original system to test specifications.

### 27.1.1 Isolation Requirements

```
SPECIFICATION_AGENT_ISOLATION_BOUNDARY:
  
  ALLOWED_ACCESS:
    - Original system API endpoints
    - Public documentation and specifications
    - Observable behaviors (inputs, outputs, side effects)
    - Network traffic patterns
    - Public dataset samples
  
  FORBIDDEN_ACCESS:
    - Source code repositories
    - Internal implementation documentation
    - Design documents
    - Code comments
    - Developer discussions or internal notes
    - Proprietary algorithms described in detail
```

The isolation boundary ensures that any specification produced by an agent can be legally used by a separate implementation team without contamination concerns.

### 27.1.2 Specification Agent Types

**API Discovery Agents**: Map available endpoints, methods, parameters, and response formats. These agents systematically probe the API surface to understand its structure without examining the code.

**Behavior Extraction Agents**: Document the actual behavior of API calls, including error conditions, edge cases, side effects, and state transitions. These agents go beyond structure to capture semantics.

**Formal Specification Agents**: Transform observed behaviors into formal specifications using languages such as Alloy, TLA+, or custom domain-specific languages. These enable automated verification.

**Test Generation Agents**: Create executable test cases from observed behaviors. These tests serve as the primary specification for clean room implementations.

### 27.1.3 Core Workflow

```
SPECIFICATION_AGENT_WORKFLOW:
  
  Phase 1: System Scanning
    - Identify accessible endpoints/interfaces
    - Map parameter spaces
    - Discover authentication/authorization requirements
  
  Phase 2: Behavior Probing
    - Make representative API calls
    - Document request/response pairs
    - Identify error conditions
    - Map state dependencies
  
  Phase 3: Edge Case Discovery
    - Test boundary conditions
    - Probe type variations
    - Identify rate limits
    - Discover timing behaviors
  
  Phase 4: Specification Synthesis
    - Consolidate findings
    - Generate test suite
    - Create formal documentation
    - Produce parity checklist
  
  Phase 5: Verification
    - Self-check completeness
    - Verify test coverage
    - Check for missing scenarios
    - Validate output formats
```

## 27.2 API Discovery Agent Patterns

API discovery agents systematically explore the surface area of an API to understand its structure and capabilities.

### 27.2.1 Endpoint Discovery Pattern

The endpoint discovery pattern maps all available endpoints in an API surface.

**Prompt Template: Endpoint Discovery Agent**

```
GOAL: Discover all API endpoints for {API_NAME} at {BASE_URL}

CONTEXT:
You are a specification extraction agent for a clean room engineering project.
Your task is to discover and document all API endpoints without accessing 
implementation details.

API Configuration:
- Base URL: {BASE_URL}
- Authentication: {AUTH_TYPE} (if applicable, credentials: {CREDENTIALS_REF})
- Documentation URL (if available): {DOCS_URL}

TASK:
1. Discover all available endpoints under {BASE_URL}
2. Document the HTTP methods supported by each endpoint
3. Identify path parameters and query parameters
4. Map response formats and status codes
5. Identify rate limiting and throttling behavior

APPROACH:
Start with well-known endpoints:
- /health or /status
- / or /api
- /v1, /v2, etc. for version detection
- Common resource names: /users, /items, /orders, /accounts

Use systematic exploration:
- Try common REST patterns
- Check OPTIONS responses for allowed methods
- Probe for sub-resources
- Check for pagination patterns

OUTPUT_FORMAT:
```yaml
endpoints:
  - path: "/example/resource"
    methods: ["GET", "POST", "PUT", "DELETE"]
    description: "Brief description"
    parameters:
      path:
        - name: "id"
          type: "string"
          required: true
          description: "Resource identifier"
      query:
        - name: "limit"
          type: "integer"
          required: false
          default: 10
          description: "Number of items to return"
    responses:
      200:
        description: "Success"
        schema:
          type: "object"
          properties:
            id: { type: "string" }
            name: { type: "string" }
    rate_limit:
      requests_per_minute: 60
      burst_allowance: 10
```

DELIVERABLES:
1. File: specs/{API_NAME}_endpoints.yaml - Complete endpoint specification
2. File: tests/behavioral/test_endpoint_discovery.py - pytest test suite verifying all endpoints
3. Documentation: docs/api_discovered.md - Human-readable summary

CONSTRAINTS:
- DO NOT access {SOURCE_CODE_REPO} or any implementation details
- DO NOT reverse engineer code or algorithms
- DO examine only observable API behavior
- DO document everything you cannot access (authentication requirements, etc.)

SUCCESS_CRITERIA:
- All accessible endpoints documented
- Parameter schemas complete
- Response schemas documented
- Rate limits identified
- Tests verify each endpoint is reachable
```

**Implementation Example**

```python
# Python implementation for endpoint discovery agent
delegate_task(
    goal="Discover all API endpoints for OrderService at https://api.orders.example.com",
    context="""
    You are a specification extraction agent for a clean room engineering project.
    Your task is to discover and document all API endpoints without accessing 
    implementation details.

    API Configuration:
    - Base URL: https://api.orders.example.com
    - Authentication: Bearer token (see environment: ORDER_API_TOKEN)
    - Documentation available at: https://docs.orders.example.com/api

    [Full prompt template from above follows...]
    """,
    toolsets=['browser', 'terminal', 'file'],
    max_iterations=40
)
```

### 27.2.2 Sequential Resource Discovery Pattern

Many APIs expose related resources that must be discovered sequentially (e.g., you need a user ID to discover user orders).

**Prompt Template: Sequential Discovery Agent**

```
GOAL: Discover resource relationships in {API_NAME}

CONTEXT:
Resources in this API have hierarchical relationships:
- Users contain Orders
- Orders contain LineItems
- Accounts contain Transactions

SEQUENCE:
1. First discover top-level resources (Users, Accounts)
2. Use discovered IDs to probe sub-resources
3. Map full resource hierarchy

RESOURCES_TO_MAP:
{RESOURCES_LIST}

DEPENDENCY_CHAIN:
{DEPENDENCY_GRAPH}

OUTPUT:
For each resource, document:
- Resource path
- Required parent resources
- Child resources available
- Sub-resource discovery endpoints

Example:
```yaml
resources:
  users:
    path: "/users"
    parent: null
    children: ["orders", "addresses"]
    discover_via: "GET /users"
    
  orders:
    path: "/users/{user_id}/orders"
    parent: "users"
    identification: "user_id from parent"
    children: ["line_items"]
    discover_via: "GET /users/{user_id}/orders"
```

STOPPING_CONDITION:
Stop when no new resources discovered in a full traversal.
```

### 27.2.3 Method Matrix Pattern

Document all HTTP methods available for each endpoint and their semantic differences.

**Prompt Template: Method Matrix Agent**

```
GOAL: Build complete method matrix for {ENDPOINT_PATH}

CONTEXT:
The endpoint {ENDPOINT_PATH} may support multiple HTTP methods with different
behaviors. Document all methods and their specific semantics.

METHODS_TO_TEST: ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]

FOR EACH METHOD:
1. Send request with appropriate payload
2. Document response
3. Document side effects (e.g., resource creation)
4. Document error conditions
5. Note any method-specific headers required

OUTPUT_FORMAT:
```yaml
endpoint: "/api/v1/orders"
methods:
  GET:
    description: "List orders"
    parameters:
      query: ["limit", "offset", "status"]
    responses:
      200: "Order list returned"
      401: "Authentication required"
    side_effects: null
    
  POST:
    description: "Create new order"
    parameters:
      body: "Order creation request object"
    responses:
      201: "Order created, Location header set"
      400: "Validation error"
    side_effects: "Creates order, emits webhook"
    
  [continue for each method...]
```

Unless documented otherwise, assume each method behaves according to HTTP/1.1 RFC 7231.
```

## 27.3 Behavior Extraction Agent Patterns

Beyond discovering the structure of an API, behavior extraction agents document what the API actually does.

### 27.3.1 Request-Response Pair Extraction

Systematically capture request/response pairs to understand data transformation behavior.

**Prompt Template: Request-Response Extraction Agent**

```
GOAL: Extract comprehensive request/response pairs for {ENDPOINT_PATH}

CONTEXT:
For clean room implementation, we need to understand exactly how the API
transforms inputs into outputs. Capture request/response pairs covering:

VARIATION_DIMENSIONS:
1. Valid inputs (normal cases)
2. Invalid inputs (validation errors)
3. Boundary values (min/max/max_length/etc.)
4. Type variations (strings vs numbers)
5. Optional fields (present vs absent)
6. Encoding variations (UTF-8, ASCII, etc.)

ENDPOINT: {ENDPOINT_PATH}
METHOD: {HTTP_METHOD}

PARAMETER_SCHEMA (from discovery):
{SCHEMA}

EXTRACTION_STRATEGY:
Generate variations using boundary analysis:
- For strings: empty, single char, max length, max+1, special chars
- For numbers: 0, 1, -1, max, min, very large, very small
- For dates: epoch, today, far future, far past
- For enums: each valid value
- For objects: omit optional fields, null values, nested variations

OUTPUT_FORMAT:
```yaml
request_response_pairs:
  - id: "test_001"
    description: "Valid order creation"
    request:
      method: "POST"
      path: "/orders"
      headers:
        Content-Type: "application/json"
      body:
        customer_id: "CUST123"
        items:
          - sku: "PROD-001"
            quantity: 2
    response:
      status: 201
      headers:
        Location: "/orders/ORD-456"
        Content-Type: "application/json"
      body:
        order_id: "ORD-456"
        status: "pending"
        total: 49.99
        created_at: "2024-01-15T10:30:00Z"
    
  - id: "test_002"
    description: "Invalid customer ID"
    request:
      [as above with invalid customer_id]
    response:
      status: 400
      body:
        error: "ValidationError"
        message: "Invalid customer_id format"
```

COVERAGE_TARGET: {COVERAGE_PERCENT}% of parameter combinations
MAX_PAIRS: {MAX_PAIR_LIMIT} (prioritize edge cases)
```

**Implementation Example**

```python
class RequestResponseExtractor:
    def __init__(self, endpoint, schema):
        self.endpoint = endpoint
        self.schema = schema
        self.pairs = []
    
    def generate_boundary_cases(self):
        """Generate boundary condition test cases"""
        boundary_cases = []
        
        for field, field_schema in self.schema['properties'].items():
            cases = self._field_boundary_cases(field, field_schema)
            boundary_cases.extend(cases)
        
        return boundary_cases
    
    def _field_boundary_cases(self, field, schema):
        """Generate boundary cases for a single field"""
        cases = []
        field_type = schema.get('type')
        
        if field_type == 'string':
            max_length = schema.get('maxLength', 100)
            cases.extend([
                {field: ""},  # Empty string
                {field: "a"},  # Single character
                {field: "a" * max_length},  # Max length
                {field: "a" * (max_length + 1)},  # Exceeds max
                {field: "<script>alert(1)</script>"},  # XSS attempt
                {field: "test@example.com\x00"},  # Null byte
            ])
        elif field_type == 'integer':
            cases.extend([
                {field: 0},
                {field: -1},
                {field: 1},
                {field: 2147483647},  # Max int32
                {field: -2147483648},  # Min int32
            ])
        
        return cases
```

### 27.3.2 State Machine Extraction

Many APIs maintain internal state that affects behavior. State machine extraction agents map out state transitions.

**Prompt Template: State Machine Extraction Agent**

```
GOAL: Extract state machine for {RESOURCE_TYPE} resources

CONTEXT:
The {RESOURCE_TYPE} resource changes state in response to API operations.
We need to map the complete state machine including transitions and triggers.

RESOURCE_ENDPOINT: {RESOURCE_ENDPOINT}
KNOWN_STATES (if any): {STATES}

EXTRACTION_PROCEDURE:
1. Create a resource instance
2. Query its current state
3. Attempt each possible operation
4. Document which operations cause state changes
5. Continue until all states and transitions mapped

STATE_DETECTION:
- Check response body for 'status' or 'state' field
- Check response headers for state indicators
- Use dedicated status endpoint if available
- Infer state from available operations

OPERATIONS_TO_TEST:
{OPERATIONS_LIST}

OUTPUT_FORMAT:
```yaml
state_machine:
  initial_state: "pending"
  final_states: ["completed", "cancelled", "failed"]
  
  states:
    pending:
      properties:
        cancellable: true
        modifiable: true
      available_transitions:
        - name: "process"
          target: "processing"
          trigger: "POST {resource}/process"
        - name: "cancel"
          target: "cancelled"
          trigger: "POST {resource}/cancel"
          
    processing:
      properties:
        cancellable: false
        modifiable: false
      available_transitions:
        - name: "complete"
          target: "completed"
          trigger: "automatic on processing finish"
        - name: "fail"
          target: "failed"
          trigger: "automatic on processing error"
  
  [continue for all states...]
```

COMPLETE_COVERAGE: Document all reachable states and transitions excluding error transitions.
```

### 27.3.3 Error Condition Extraction

Systematically document all error conditions and their triggers.

**Prompt Template: Error Condition Extraction Agent**

```
GOAL: Extract all error conditions for {ENDPOINT_PATH}

CONTEXT:
Document every possible error response from this endpoint. Error responses
are critical for clean room implementations as they often contain complex
validation logic.

ERROR_CATEGORIES:
1. Authentication errors (401, 403)
2. Validation errors (400)
3. Resource errors (404, 409, 410)
4. Rate limit errors (429)
5. Server errors (500, 502, 503)

ERROR_TRIGGERS TO TEST:
- Invalid authentication
- Expired authentication
- Insufficient permissions
- Missing required fields
- Field type mismatches
- Field value out of range
- Duplicate unique fields
- Non-existent references
- Concurrent modification
- Service unavailable
- Timeout conditions

OUTPUT_FORMAT:
```yaml
error_conditions:
  - code: 400
    type: "ValidationError"
    triggers:
      - "Missing required field 'email'"
      - "Invalid email format"
      - "Email exceeds 254 characters"
    response_schema:
      type: "object"
      properties:
        error:
          type: "string"
          enum: ["ValidationError"]
        message:
          type: "string"
        field_errors:
          type: "array"
          items:
            type: "object"
            properties:
              field: { type: "string" }
              message: { type: "string" }
    
  - code: 409
    type: "ConflictError"
    triggers:
      - "Email already exists"
      - "Concurrent modification detected"
```

ERROR_MESSAGE_DOCUMENTATION:
- Document exact error message text when possible
- Note any message parameters (e.g., "Field {field} is required")
- Document localization behavior if applicable
```

### 27.3.4 Side Effect Detection

Identify all side effects of API operations (database changes, webhook calls, event emissions).

**Prompt Template: Side Effect Detection Agent**

```
GOAL: Detect all side effects of operations on {ENDPOINT_PATH}

CONTEXT:
API operations may have side effects beyond the immediate response:
- Database modifications
- Webhook calls
- Event emissions
- Email notifications
- Audit log entries
- Caching operations

DETECTION_STRATEGIES:
1. Webhook capture: Set up webhook endpoint, trigger API calls, capture callbacks
2. Event stream monitoring: Subscribe to event streams, track emitted events
3. Read-after-write: Create resource, immediately read, compare for side effects
4. Cross-resource queries: After modifying resource A, query related resources B, C

ENDPOINT: {ENDPOINT_PATH}
RELATED_RESOURCES: {RELATED_ENDPOINTS}
WEBHOOK_SUPPORT: {WEBHOOK_CONFIG}

OUTPUT_FORMAT:
```yaml
side_effects:
  operation: "POST /orders"
  detected_effects:
    webhooks:
      - event: "order.created"
        payload: { order_id, customer_id, total }
        timing: "within 5 seconds"
        retries: 3
      
    events:
      - type: "order_events"
        topic: "orders"
        key: {order_id}
        value: { status: "pending", ... }
    
    related_modifications:
      - resource: "/inventory/{sku}"
        effect: "quantity decreased by order quantity"
      
    notifications:
      - type: "email"
        recipient: "customer email"
        template: "order_confirmation"
  
  idempotency:
    behavior: "Duplicate request with same idempotency key returns same response"
    key_location: "header: Idempotency-Key"
```

DETECT_ASYNC_EFFECTS: Wait up to {TIMEOUT} seconds for delayed side effects.
```

## 27.4 Formal Specification Generation

Behavior extraction produces raw observations. Formal specification agents transform these into precise, analyzable specifications.

### 27.4.1 Property Specification Pattern

Document formal properties that implementations must satisfy.

**Prompt Template: Property Specification Agent**

```
GOAL: Generate formal property specifications for {RESOURCE_NAME}

CONTEXT:
Transform observed behaviors into formal properties that can be verified
in implementations. Properties should be precise, testable, and complete.

PROPERTY_CATEGORIES:
1. Invariants - Always true properties
2. Preconditions - Required before operations
3. Postconditions - Guaranteed after operations
4. Transition guards - Conditions for state changes

INPUT: Observed behaviors from extraction agents
OUTPUT_FORMAT: Formal specification + natural language description

TEMPLATE:
```
PROPERTY: {resource}_{operation}_{property_name}
CATEGORY: Invariant | Precondition | Postcondition | Guard
DESCRIPTION: 
  Natural language description of the property
FORMAL_SPEC:
  Formal notation (optional, based on available tools)
TEST_IMPLEMENTATION:
  How to test this property
EXAMPLES:
  - Example 1: [valid case]
  - Example 2: [invalid case]

CONFLICT_RESOLUTION:
  - If conflict with observed behavior: Document discrepancy
  - If conflict with documentation: Prefer observed behavior
  - If multiple observations conflict: Document all, flag for review
```

EXAMPLE_PROPERTIES:
1. "Order total always equals sum of line item prices"
2. "Cannot cancel order in 'shipped' state"
3. "Creating order requires valid customer_id"
4. "Order ID format is ORD-{8 digit alphanumeric}"

PROPERTY_SPECIFICATION_LANGUAGE: Use {SPEC_LANGUAGE} if specified, otherwise natural language with test examples.
```

**Implementation Example**

```python
class PropertyGenerator:
    def generate_invariants(self, observations):
        """Generate invariant properties from observations"""
        invariants = []
        
        # Check for field relationships that hold in all observations
        relationships = self._analyze_field_relationships(observations)
        
        for rel in relationships:
            if rel.confidence > 0.95:  # Must hold in 95%+ of cases
                invariants.append({
                    'name': f"{rel.field_a}_{rel.field_b}_relationship",
                    'description': rel.description,
                    'formal': rel.formal_spec,
                    'test': rel.test_code
                })
        
        return invariants
    
    def generate_preconditions(self, operation, observations):
        """Generate precondition properties"""
        preconditions = []
        
        # Analyze successful vs failed calls
        successful = [o for o in observations if o.success]
        failed = [o for o in observations if not o.success]
        
        # Find differences that predict success
        success_patterns = self._extract_patterns(successful)
        failure_patterns = self._extract_patterns(failed)
        
        for pattern in success_patterns:
            if pattern not in failure_patterns:
                preconditions.append({
                    'name': pattern.name,
                    'description': pattern.description,
                    'required': True
                })
        
        return preconditions
```

### 27.4.2 Alloy Model Generation

Generate Alloy models for formal verification (if Alloy is available).

**Prompt Template: Alloy Specification Agent**

```
GOAL: Generate Alloy formal model for {SYSTEM_NAME}

CONTEXT:
Alloy is a formal specification language that can verify properties
of systems. Generate an Alloy model from observed behaviors.

ALLOY_MODEL_STRUCTURE:
```alloy
module {system_name}

// Signatures representing entities
abstract sig Resource {
  id: one String
}

sig {ResourceA} extends Resource {
  field1: one {Type},
  field2: lone {Type},  // Optional
  relation: set {ResourceB}  // One-to-many
}

// State signatures
abstract sig State {}
lone sig Pending, Processing, Completed, Failed extends State {}

// State machine facts
fact state_transitions {
  all r: {Resource} |
    r.state = Pending => r.state' in Pending + Processing + Failed
    r.state = Processing => r.state' in Processing + Completed + Failed
    // Terminal states
    r.state in Completed + Failed => r.state' = r.state
}

// Invariants
fact invariants {
  all r: {Resource} |
    // Field relationships
    r.field2 => r.field1  // If field2 present, field1 must be
}

// Operation predicates
pred create{Resource}[params] {
  // Preconditions
  no r: {Resource} | r.id = params.id
  // Postconditions
  one r: {Resource}' | r.id = params.id
}

// Property assertions
assert no_orphaned_relations {
  all r: {ResourceA} | r.relation in {ResourceB}
}

check no_orphaned_relations for 10
```

GENERATION_GUIDELINES:
1. Create signatures for each resource type
2. Model states as state signature hierarchy
3. Encode observed state transitions as facts
4. Express invariants as facts
5. Encode operations as predicates
6. Generate assertions for key properties
7. Include scope specification for checking

LIMITATIONS:
- Alloy has limited integer arithmetic
- Complex string operations may need abstraction
- Temporal properties require trace-based modeling
- Note any abstractions made for Alloy compatibility
```

## 27.5 Test Generation from Specifications

The ultimate output of specification agents is executable test suites that serve as the specification for implementation.

### 27.5.1 Behavioral Test Generation

Generate pytest test suites from specifications.

**Prompt Template: Behavioral Test Generation Agent**

```
GOAL: Generate comprehensive pytest test suite for {API_NAME}

CONTEXT:
Generate pytest tests that verify behavior of {API_NAME}. These tests
serve as the executable specification for clean room implementation.

SPECIFICATION_INPUT: specs/{API_NAME}_specification.yaml

TEST_CATEGORIES:
1. Happy path tests - Valid inputs, expected outputs
2. Validation tests - Invalid inputs, error responses
3. Boundary tests - Edge case inputs
4. State transition tests - Resource lifecycle
5. Security tests - Authentication/authorization
6. Integration tests - Multi-resource operations

TEST_FILE_STRUCTURE:
```python
# tests/behavioral/test_{api_name}.py

import pytest
import requests
from typing import Dict, Any

class Test{ResourceName}:
    """Tests for {resource_name} resource behavior"""
    
    @pytest.fixture
    def api_client(self):
        """Configure API client for tests"""
        return APIClient(base_url="{BASE_URL}")
    
    @pytest.fixture
    def valid_{resource}(self, api_client):
        """Create valid {resource} for tests"""
        return api_client.create_{resource}(DEFAULT_VALID_PAYLOAD)
    
    # Happy path tests
    def test_create_{resource}_success(self, api_client):
        """Test successful {resource} creation"""
        response = api_client.create_{resource}(VALID_PAYLOAD)
        assert response.status_code == 201
        assert "id" in response.json()
        # Additional assertions based on specification
    
    # Validation tests  
    def test_create_{resource}_missing_required_field(self, api_client):
        """Test validation of required fields"""
        # Implementation based on spec
    
    # Boundary tests
    @pytest.mark.parametrize("field,value", [
        ("name", ""),  # Empty string
        ("name", "a" * 256),  # Max length exceeded
        ("quantity", -1),  # Negative number
        ("quantity", 0),  # Zero
    ])
    def test_{resource}_boundary_values(self, api_client, field, value):
        """Test boundary value handling"""
        # Implementation
```

TEST_REQUIREMENTS:
- Each observable behavior has at least one test
- Tests are independent and isolated
- Tests use descriptive names explaining behavior
- Tests include docstrings with expected behavior
- Tests are parameterized where appropriate
- Fixtures provide test data setup/teardown

ASSERTION_STANDARDS:
- Assert exact status codes per specification
- Assert response structure matches schema
- Assert error messages match expected patterns
- Assert state transitions occur as specified
- Assert side effects occur as specified

COVERAGE_TARGET: {COVERAGE_PERCENT}% of specification elements
MAX_TEST_EXECUTION_TIME: {TIMEOUT_SECONDS}s per test
```

**Implementation Example**

```python
# Example generated test structure
# tests/behavioral/test_orders_api.py

import pytest
import requests
from datetime import datetime

BASE_URL = "https://api.orders.example.com"

class TestOrderCreation:
    """Tests for order creation behavior"""
    
    def test_create_order_success(self, auth_headers):
        """
        SPEC: Order creation with valid data returns 201
        with order details including generated ID
        """
        payload = {
            "customer_id": "CUST123",
            "items": [
                {"sku": "PROD-001", "quantity": 2}
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/orders",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "order_id" in data
        assert data["order_id"].startswith("ORD-")
        assert data["status"] == "pending"
        assert "created_at" in data
    
    @pytest.mark.parametrize("missing_field", [
        "customer_id", "items"
    ])
    def test_create_order_missing_required_field(self, missing_field, auth_headers):
        """
        SPEC: Missing required field returns 400 with ValidationError
        """
        payload = self._valid_order_payload()
        del payload[missing_field]
        
        response = requests.post(
            f"{BASE_URL}/orders",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert response.json()["error"] == "ValidationError"
```

### 27.5.2 Property-Based Test Generation

Generate Hypothesis property-based tests where appropriate.

**Prompt Template: Property-Based Test Generation Agent**

```
GOAL: Generate Hypothesis property-based tests for {RESOURCE_NAME}

CONTEXT:
Property-based testing generates test cases automatically from properties.
Use Hypothesis to generate tests that should hold for all valid inputs.

PROPERTY_CANDIDATES:
1. Round-trip properties: create → read → compare
2. Validation properties: invalid inputs always rejected
3. State properties: state transitions follow specification
4. Idempotency properties: repeated calls with same idempotency key

HYPOTHESIS_STRATEGIES:
```python
from hypothesis import given, strategies as st, settings

# Generate valid payloads
valid_payloads = st.fixed_dictionaries({
    'field1': st.text(min_size=1, max_size=100),
    'field2': st.integers(min_value=0, max_value=10000),
    'optional_field': st.one_of(st.none(), st.text()),
})

# Generate invalid payloads  
invalid_payloads = st.one_of(
    st.fixed_dictionaries({'field1': st.text(max_size=0)}),  # Empty
    st.fixed_dictionaries({'field1': st.text(min_size=101)}),  # Too long
    st.fixed_dictionaries({'field2': st.integers(max_value=-1)}),  # Negative
)
```

TEST_TEMPLATES:
```python
@given(payload=valid_payloads)
@settings(max_examples=100)
def test_create_always_succeeds_with_valid_data(self, payload):
    """
    PROPERTY: Any payload matching schema should create successfully
    """
    response = self.api.create(payload)
    assert response.status_code == 201
    assert self._is_valid_response(response.json())

@given(payload=invalid_payloads)
@settings(max_examples=100)
def test_create_always_fails_with_invalid_data(self, payload):
    """
    PROPERTY: Any payload violating schema should be rejected
    """
    response = self.api.create(payload)
    assert response.status_code == 400
```

GENERATION_RULES:
- Generate strategies matching field constraints
- Include edge cases in strategy design
- Use composite strategies for related fields
- Minimize examples while maintaining coverage
- Set appropriate max examples based on execution time
```

## 27.6 Multi-Agent Specification Orchestration

Complex systems require multiple specification agents working in parallel or sequence.

### 27.6.1 Fan-Out Discovery Pattern

Deploy multiple agents simultaneously to discover different API sections.

**Implementation Example**

```python
class FanOutSpecificationOrchestrator:
    def __init__(self, api_sections):
        self.api_sections = api_sections
    
    def execute_discovery(self):
        """Deploy agents in parallel for each API section"""
        tasks = []
        
        for section_name, section_config in self.api_sections.items():
            task = delegate_task(
                goal=f"Discover {section_name} API section",
                context=f"""
                API Section: {section_name}
                Base Path: {section_config['path']}
                Resources: {section_config['resources']}
                
                Use Endpoint Discovery Pattern to map:
                - All endpoints under {section_config['path']}
                - All parameters and responses
                - All error conditions
                
                Output: specs/{section_name}_spec.yaml
                """,
                toolsets=['browser', 'terminal', 'file'],
                max_iterations=30
            )
            tasks.append((section_name, task))
        
        # Collect results
        results = {}
        for section_name, task in tasks:
            results[section_name] = task.result()
        
        # Merge specifications
        return self._merge_specifications(results)
    
    def _merge_specifications(self, section_specs):
        """Merge individual section specifications"""
        merged = {
            'api_version': '1.0',
            'sections': {},
            'shared_components': {}
        }
        
        for section_name, spec in section_specs.items():
            merged['sections'][section_name] = spec
            
            # Extract shared schemas
            if 'schemas' in spec:
                for schema_name, schema in spec['schemas'].items():
                    merged['shared_components'][schema_name] = schema
        
        return merged
```

### 27.6.2 Chained Specification Pattern

Some specifications require sequential work where later agents depend on earlier results.

**Implementation Example**

```python
class ChainedSpecificationOrchestrator:
    def execute_chain(self, target_api):
        """Execute specification agents in dependency order"""
        
        # Phase 1: Endpoint discovery
        endpoints_spec = delegate_task(
            goal=f"Discover all endpoints for {target_api}",
            context=f"API: {target_api}",
            toolsets=['browser', 'terminal', 'file'],
            max_iterations=25
        )
        
        # Phase 2: Request/response extraction (depends on endpoints)
        request_response_spec = delegate_task(
            goal=f"Extract request/response pairs for {target_api}",
            context=f"""
            API: {target_api}
            Endpoints: {endpoints_spec.output}
            
            Extract comprehensive request/response pairs
            for all discovered endpoints.
            """,
            toolsets=['browser', 'terminal', 'file'],
            max_iterations=40
        )
        
        # Phase 3: Behavior analysis (depends on request/response)
        behavior_spec = delegate_task(
            goal=f"Analyze behaviors for {target_api}",
            context=f"""
            API: {target_api}
            Request/Response pairs: {request_response_spec.output}
            
            Analyze patterns to identify:
            - State machines
            - Side effects
            - Error conditions
            - Validation rules
            """,
            toolsets=['terminal', 'file'],
            max_iterations=30
        )
        
        # Phase 4: Test generation (depends on all above)
        test_suite = delegate_task(
            goal=f"Generate test suite for {target_api}",
            context=f"""
            API: {target_api}
            
            Inputs:
            - Endpoints: {endpoints_spec.output}
            - Request/Response: {request_response_spec.output}
            - Behaviors: {behavior_spec.output}
            
            Generate comprehensive pytest test suite.
            """,
            toolsets=['terminal', 'file'],
            max_iterations=25
        )
        
        return {
            'endpoints': endpoints_spec,
            'request_response': request_response_spec,
            'behavior': behavior_spec,
            'tests': test_suite
        }
```

### 27.6.3 Conflict Resolution for Multi-Agent Specifications

When multiple agents produce conflicting specifications, resolution is required.

**Conflict Resolution Protocol**

```python
class SpecificationConflictResolver:
    def resolve_conflicts(self, agent_specs):
        """Resolve conflicts between agent specifications"""
        
        conflicts = self._detect_conflicts(agent_specs)
        resolved = {}
        
        for conflict in conflicts:
            if conflict.type == 'parameter_type':
                # Prefer observed behavior over documentation
                observed = self._get_observed_value(conflict)
                resolved[conflict.field] = observed
                
            elif conflict.type == 'error_code':
                # Prefer actual status codes returned
                actual = self._get_most_frequent(conflict.samples)
                resolved[conflict.operation] = actual
                
            elif conflict.type == 'optional_field':
                # Field is required if any agent found it required
                if any(a.found_required for a in conflict.agents):
                    resolved[conflict.field] = 'required'
                else:
                    resolved[conflict.field] = 'optional'
        
        return resolved
```

## 27.7 Specification Quality Assurance

Ensure specifications are complete, consistent, and usable.

### 27.7.1 Completeness Checklist

```
SPECIFICATION_COMPLETENESS_CHECKLIST:

Structural Completeness:
  [ ] All endpoints documented
  [ ] All parameters documented (path, query, body, header)
  [ ] All response codes documented
  [ ] All response schemas documented
  [ ] Authentication requirements documented

Behavioral Completeness:
  [ ] Happy path behaviors documented
  [ ] All error conditions documented
  [ ] State machine transitions documented
  [ ] Side effects documented
  [ ] Rate limiting behavior documented

Edge Case Coverage:
  [ ] Boundary values tested
  [ ] Empty/null input handling documented
  [ ] Maximum size limits documented
  [ ] Concurrent access behavior documented
  [ ] Timeout behaviors documented

Test Coverage:
  [ ] Each endpoint has test cases
  [ ] Each error condition has test case
  [ ] Each state transition has test case
  [ ] Property-based tests for invariants
  [ ] Integration tests for workflows
```

### 27.7.2 Self-Verification Prompt

**Prompt Template: Specification Self-Verification Agent**

```
GOAL: Verify specification completeness for {API_NAME}

CONTEXT:
Specification: specs/{API_NAME}_spec.yaml
Test Suite: tests/behavioral/test_{API_NAME}.py

VERIFICATION_TASKS:
1. Check every endpoint has corresponding tests
2. Verify every documented error has test case
3. Check schema definitions match observed examples
4. Verify all parameter constraints are tested
5. Check for undocumented behaviors in tests

COVERAGE_REPORT:
Generate report showing:
- Endpoints covered: X/Y (%)
- Error conditions covered: X/Y (%)
- Parameter variations covered: X/Y (%)
- Gaps requiring additional specification work

REQUIRED_OUTPUT:
- verification_report.md - Detailed findings
- missing_coverage.md - List of gaps
- recommended_actions.md - Prioritized fixes
```

## 27.8 Integration with Clean Room Workflow

Specification agents feed into the broader clean room workflow.

### 27.8.1 Handoff to Implementation Agents

```
SPECIFICATION_TO_IMPLEMENTATION_HANDOFF:

Required Package:
1. spec.yaml - Complete API specification
2. behavioral_tests.py - Test suite (executable specification)
3. examples/ - Sample request/response pairs
4. edge_cases/ - Documented edge behaviors
5. formal_spec/ - Formal properties (if generated)

NOTICE_TO_IMPLEMENTATION_TEAM:
"You have received a clean specification package. 
You may not access the original system or its documentation.
Your implementation must pass all provided behavioral tests.
Questions should be directed to the specification team, not 
the original system developers."
```

### 27.8.2 Specification Versioning

```python
class SpecificationVersionManager:
    def create_version(self, spec_package):
        """Create versioned specification package"""
        version = self._generate_version()
        
        versioned_package = {
            'version': version,
            'created_at': datetime.utcnow(),
            'specification': spec_package,
            'checksum': self._compute_checksum(spec_package),
            'parent_version': self._get_parent_version()
        }
        
        # Store immutable version
        self._store_version(versioned_package)
        
        return versioned_package
```

## 27.9 Best Practices

### 27.9.1 Specification Agent Do's and Don'ts

**Do:**
- Observe actual API behavior extensively
- Document observed behavior even if it differs from documentation
- Generate tests for every behavior
- Version specifications immutably
- Include negative test cases (error conditions)

**Don't:**
- Assume documentation is accurate
- Skip edge cases because they seem "unlikely"
- Modify specifications after handoff to implementation
- Access source code or design documents
- Make assumptions about implementation details

### 27.9.2 Error Handling

```python
class SpecificationAgentErrorHandler:
    def handle_discovery_failure(self, endpoint, error):
        """Handle failures during specification discovery"""
        
        if error.type == 'authentication_failure':
            # Document authentication requirement
            return {
                'status': 'blocked',
                'reason': 'authentication_required',
                'documentation': self._document_auth_requirement(endpoint)
            }
        
        elif error.type == 'rate_limit':
            # Implement backoff and retry
            time.sleep(error.retry_after)
            return {'status': 'retry'}
        
        elif error.type == 'endpoint_unavailable':
            # Document as unavailable
            return {
                'status': 'unavailable',
                'documentation': self._document_unavailability(endpoint)
            }
```

## 27.10 Chapter Summary

Specification agents form the critical foundation of clean room engineering. They:

1. **Extract behavior without accessing implementation** - Maintaining clean room integrity
2. **Generate executable specifications** - Test suites that drive implementation
3. **Operate in isolation** - Preventing knowledge contamination
4. **Work in coordinated teams** - Parallel discovery for complex systems
5. **Produce versioned artifacts** - Enabling specification evolution

The patterns in this chapter provide copy-paste ready templates for deploying specification agents using the Hermes `delegate_task` system. By following these patterns, teams can rapidly generate comprehensive, legally-safe specifications that serve as the foundation for clean room implementations.

Key outputs from specification agents:
- Complete API endpoint documentation
- Request/response pair catalogs
- State machine definitions
- Error condition taxonomies
- Executable behavioral test suites
- Formal property specifications

These artifacts flow directly into implementation workflows (Chapter 28) and verification workflows (Chapter 29), forming the backbone of AI-augmented clean room engineering.

---

## Copy-Paste Quick Reference

### Quick Start: Full Specification Pipeline

```python
# Complete specification pipeline using delegate_task

def full_specification_pipeline(api_name, base_url):
    """
    Run complete specification pipeline for an API.
    Returns comprehensive specification package.
    """
    
    # Step 1: Endpoint discovery
    endpoints = delegate_task(
        goal=f"Discover endpoints for {api_name}",
        context=f"API: {api_name}, Base URL: {base_url}",
        toolsets=['browser', 'terminal', 'file']
    )
    
    # Step 2: Behavior extraction
    behaviors = delegate_task(
        goal=f"Extract behaviors for {api_name}",
        context=f"Endpoints: {endpoints}",
        toolsets=['browser', 'terminal', 'file']
    )
    
    # Step 3: Test generation
    tests = delegate_task(
        goal=f"Generate tests for {api_name}",
        context=f"Behaviors: {behaviors}",
        toolsets=['terminal', 'file']
    )
    
    # Step 4: Verification
    verification = delegate_task(
        goal=f"Verify specification completeness",
        context=f"Spec, Behaviors, Tests",
        toolsets=['terminal']
    )
    
    return {
        'api_name': api_name,
        'endpoints': endpoints,
        'behaviors': behaviors,
        'tests': tests,
        'verified': verification
    }
```

***
*Chapter 27 - Agent Patterns & Workflows - 20 pages*
