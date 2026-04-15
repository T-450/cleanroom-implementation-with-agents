---
title: Migration Approach Comparison
created: 2026-04-15
updated: 2026-04-15
type: comparison
tags: [migration, technical-debt]
sources: []
---

# Migration Approach Comparison

This document compares different approaches to migrating from a legacy system to a clean room implementation.

## Migration Approaches

### Approach 1: Big Bang Replacement

```
TIMELINE: Single event (day/week)
RISK: Very High
DOWNTIME: Significant (hours to days)
ROLLBACK: Complex, data sync required
ACCEPTANCE: Low
```

### Approach 2: Strangler Fig

```
TIMELINE: Gradual (months to years)
RISK: Low
DOWNTIME: Zero (per feature)
ROLLBACK: Simple (per feature)
ACCEPTANCE: High
```

### Approach 3: Parallel Running

```
TIMELINE: Concurrent operation
RISK: Medium
DOWNTIME: Zero
ROLLBACK: Trivial (switch routing)
ACCEPTANCE: Medium
```

## Comparison Matrix

| Criterion | Big Bang | Strangler Fig | Parallel |
|-----------|----------|---------------|----------|
| Risk | Very High | Low | Medium |
| Downtime | High | Zero | Zero |
| Team workload | Bursty | Steady | Sustained |
| Time to value | Fast | Slow | Medium |
| Rollback ease | Difficult | Easy | Very Easy |
| Cost | Medium | High | High |
| User adoption | Low | High | Medium |

## Recommendation

**Strangler Fig is recommended for:**
- Enterprise systems (>500K lines)
- Systems with >10K users
- Mission-critical applications
- Complex integrations

**Big Bang may be acceptable for:**
- Small systems (<100K lines)
- Limited user base (<1K users)
- Non-critical applications
- Simple integrations
