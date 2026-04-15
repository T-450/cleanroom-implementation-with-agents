---
title: Test-Driven Development for Clean Room
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [test-first, behavioral-specification, core-concept]
sources: []
---

# Test-Driven Development for Clean Room

Test-driven development (TDD) is the PRIMARY mechanism for creating behavioral specifications in clean room implementation. Every feature is implemented through the red-green-refactor cycle, where tests capture the observed behavior of the original system.

## The Red-Green-Refactor Cycle

### RED — Write Failing Test

Write one minimal test showing what should happen, based on observed behavior:

```python
def test_user_login_with_valid_credentials():
    """
    Observed behavior: User can log in with valid username/password
    Source: API test against original system v2.3.1
    
    GIVEN: User 'alice' with password 'secret123' exists
    WHEN: POST /api/login with valid credentials
    THEN: Response is 200 OK
    AND: Response contains session_token
    AND: Session expires after 30 minutes of inactivity
    """
    response = post('/api/login', {
        'username': 'alice',
        'password': 'secret123'
    })
    
    assert response.status_code == 200
    assert 'session_token' in response.json()
```

**Critical rule**: The test MUST fail when run against the original system. This proves you're testing something real.

### GREEN — Minimal Code

Write the simplest code to pass the test. Nothing more:

```python
def login(username, password):
    # Minimal implementation to pass the test
    return {'session_token': 'abc123'}
```

**No implementation details**: Don't worry about security, validation, or error handling yet. That comes in REFACTOR.

### REFACTOR — Clean Up

After green only:
- Remove duplication
- Improve names
- Add proper validation
- Handle edge cases

Keep tests green throughout. Don't add behavior.

## The Iron Law of Clean Room TDD

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

**Write code before test? Delete it. Start over.**

This is the difference between:
- **Testing what you built** (after code)
- **Testing what you should build** (before code)

## Test-First Specification Workflow

### Step 1: Behavioral Observation

Observe the original system and document behavior:

```
OBSERVATION: Login API
Endpoint: POST /api/login
Request: {username: string, password: string}
Success response: {status: "ok", session_token: string, expires: timestamp}
Failure responses:
  - 401 Unauthorized (wrong credentials)
  - 423 Locked (account locked)
  - 429 Too Many Requests (rate limited)
```

### Step 2: Test Creation

Write the test BEFORE implementing anything:

```python
def test_login_success_with_valid_credentials():
    """
    Source: Observed behavior from /api/login endpoint
    """
    response = call_original_system('/api/login', {
        'username': 'test_user',
        'password': 'test_password'
    })
    
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'
    assert 'session_token' in response.json()
    assert 'expires' in response.json()
```

### Step 3: Test Verification

**MANDATORY**: Run the test and confirm it fails on the new implementation:

```bash
pytest tests/test_login.py::test_login_success_with_valid_credentials -v

# Expected: FAILED (feature not implemented yet)
```

### Step 4: Minimal Implementation

Implement only enough to pass the test:

```python
def handle_login(username, password):
    # Hardcoded for now - we'll fix this in refactor
    return {
        'status': 'ok',
        'session_token': 'temp_token',
        'expires': datetime.now() + timedelta(minutes=30)
    }
```

### Step 5: Verify Pass

**MANDATORY**: Confirm test passes:

```bash
pytest tests/test_login.py::test_login_success_with_valid_credentials -v

# Expected: PASSED
```

### Step 6: Refactor

Clean up the implementation while keeping tests green:

```python
def handle_login(username, password):
    # Proper implementation
    user = authenticate_user(username, password)
    if not user:
        raise AuthenticationError("Invalid credentials")
    
    token = generate_session_token(user.id)
    return {
        'status': 'ok',
        'session_token': token,
        'expires': datetime.now() + timedelta(minutes=30)
    }
```

## Behavioral Test Categories

### Category 1: Normal Flow Tests

Test happy path scenarios:

```python
class TestLoginNormalFlow:
    def test_login_with_valid_credentials(self):
        """Standard successful login"""
        pass
    
    def test_login_with_case_insensitive_username(self):
        """Username is case-insensitive"""
        pass
    
    def test_session_duration_is_30_minutes(self):
        """Sessions expire after exactly 30 minutes"""
        pass
```

### Category 2: Error Handling Tests

Test all error conditions:

```python
class TestLoginErrorHandling:
    def test_login_with_wrong_password(self):
        """Returns 401 Unauthorized"""
        pass
    
    def test_login_with_nonexistent_user(self):
        """Returns 401 without revealing user existence"""
        pass
    
    def test_login_with_locked_account(self):
        """Returns 423 Locked with recovery information"""
        pass
    
    def test_login_with_invalid_username_format(self):
        """Returns 400 Bad Request with validation details"""
        pass
```

### Category 3: Edge Case Tests

Test boundary conditions:

```python
class TestLoginEdgeCases:
    def test_login_with_empty_username(self):
        """Empty username is rejected"""
        pass
    
    def test_login_with_255_character_username(self):
        """Maximum length username is accepted"""
        pass
    
    def test_login_with_256_character_username(self):
        """Oversized username is rejected"""
        pass
    
    def test_login_with_unicode_username(self):
        """Unicode usernames work correctly"""
        pass
```

### Category 4: State Transition Tests

Test state machine behavior:

```python
class TestLoginStateTransitions:
    def test_account_locks_after_5_failures(self):
        """Account locks after exactly 5 consecutive failures"""
        pass
    
    def test_lockout_clears_after_30_minutes(self):
        """Lockout automatically clears after 30 minutes"""
        pass
    
    def test_successful_login_clears_failure_counter(self):
        """Successful login resets failure counter"""
        pass
    
    def test_admin_can_unlock_locked_account(self):
        """Administrators can unlock accounts"""
        pass
```

### Category 5: Concurrency Tests

Test concurrent operations:

```python
class TestLoginConcurrency:
    def test_same_credentials_parallel_requests(self):
        """Parallel login requests with same credentials work"""
        pass
    
    def test_multiple_sessions_same_user(self):
        """User can have multiple concurrent sessions"""
        pass
    
    def test_session_revoke_invalidates_all_others(self):
        """Revoking one session can invalidate all others"""
        pass
```

## Property-Based Testing for Discovery

Use property-based testing to discover behaviors you didn't know existed:

```python
from hypothesis import given, strategies as st

class TestLoginProperties:
    @given(
        username=st.text(min_size=1, max_size=255),
        password=st.text(min_size=1, max_size=128),
        attempt_count=st.integers(min_value=1, max_value=10)
    )
    def test_username_length_accepted(self, username, password, attempt_count):
        """System accepts usernames from 1 to 255 characters"""
        result = login(username, password)
        if 1 <= len(username) <= 255:
            assert result.success == True
        else:
            assert result.error_code == "INVALID_USERNAME"
    
    @given(attempts=st.lists(st.integers(), min_size=5, max_size=5))
    def test_lockout_after_five_failures(self, attempts):
        """System locks after exactly 5 consecutive failures"""
        results = [login('user', 'wrong') for _ in range(5)]
        assert all(r.success == False for r in results)
        # 5th attempt should lock account
```

## Test Structure for Clean Room

### Test Organization

```
tests/
├── behavioral_specs/
│   ├── test_login.py
│   ├── test_user_management.py
│   └── test_api_integration.py
├── contract/
│   ├── test_external_apis.py
│   └── test_data_formats.py
├── performance/
│   ├── test_response_times.py
│   └── test_throughput.py
└── security/
    ├── test_authentication.py
    └── test_authorization.py
```

### Test Template

```python
"""
Behavioral Specification: [Feature Name]
Source: Observed behavior from [system version]
Date: [YYYY-MM-DD]
Constraint: No access to source code - only observable behavior
"""

import pytest

class Test[FeatureName]:
    """
    Test suite for [feature] behavior
    
    All tests in this suite must:
    1. Be executable against original system (as oracle)
    2. Be executable against new implementation
    3. Pass on both systems with identical results
    """
    
    @pytest.fixture
    def original_system_api(self):
        """API client for original system"""
        pass
    
    @pytest.fixture
    def new_system_api(self):
        """API client for new implementation"""
        pass
    
    def test_behavior_against_original(self, original_system_api):
        """Verify behavior exists in original system"""
        pass
    
    def test_behavior_against_new(self, new_system_api):
        """Verify behavior exists in new implementation"""
        pass
```

## Parallel Testing Strategy

Run tests against both original and new systems:

```python
def test_login_behavior_parallel():
    """
    This test runs against both systems to verify identical behavior
    """
    # Test against original
    original_response = call_original('/api/login', {
        'username': 'test',
        'password': 'test'
    })
    
    # Test against new
    new_response = call_new('/api/login', {
        'username': 'test',
        'password': 'test'
    })
    
    # Verify identical behavior
    assert original_response.status_code == new_response.status_code
    assert original_response.json() == new_response.json()
```

## Verification Checklist

Before marking work complete:

- [ ] Every new function/method has a test
- [ ] Watched each test fail before implementing
- [ ] Each test failed for expected reason (feature missing, not typo)
- [ ] Wrote minimal code to pass each test
- [ ] All tests pass against new implementation
- [ ] All tests pass against original system
- [ ] Output pristine (no errors, warnings)
- [ ] Tests use real code (mocks only if unavoidable)
- [ ] Edge cases and errors covered
- [ ] Property-based tests discover additional behaviors

## Pitfalls

- **Deleting code before test**: You've violated clean room integrity
- **Test passes immediately**: You're testing existing behavior, not implementing new
- **Testing implementation details**: Test behavior, not internal structure
- **Skipping REFACTOR**: Technical debt accumulates quickly
- **Not verifying against original**: Divergence from original behavior

## Related Concepts
- [[behavioral-specification]]
- [[clean-room-engineering]]
- [[parallel-testing-strategy]]
- [[property-based-testing]]
- [[quality-assurance]]

## See Also
- [[practical-implementation-guide]] - TDD templates
- [[ai-agent-methodologies]] - Agent-driven TDD