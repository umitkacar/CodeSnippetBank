# Kubernetes Deployment Strategies Comparison

## 1. Rolling Update (Default)
- Gradually replaces old pods with new ones
- Zero downtime
- Easy rollback
- Resource efficient

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0
```

## 2. Blue-Green Deployment
- Two identical environments (blue/active, green/inactive)
- Instant switch
- Easy rollback
- Requires double resources

```bash
# Switch service from blue to green
kubectl patch service myapp -p '{"spec":{"selector":{"version":"green"}}}'
```

## 3. Canary Deployment
- Gradual traffic shift to new version
- Test with small percentage of users
- Lower risk
- More complex setup

```yaml
# 90% stable, 10% canary
stable: 9 replicas
canary: 1 replica
```

## 4. A/B Testing
- Route users based on criteria (headers, cookies)
- Multiple versions simultaneously
- Business-driven decisions
- Requires service mesh

## 5. Recreate
- Terminate all old pods before creating new ones
- Downtime
- Simple
- Useful for development

```yaml
strategy:
  type: Recreate
```

## 6. Shadow/Dark Launch
- New version receives copy of production traffic
- No impact on users
- Test with real data
- Requires infrastructure

## Comparison Matrix

| Strategy | Downtime | Rollback Speed | Resource Cost | Risk | Complexity |
|----------|----------|----------------|---------------|------|------------|
| Rolling | None | Medium | Low | Low | Low |
| Blue-Green | None | Fast | High (2x) | Low | Medium |
| Canary | None | Fast | Medium | Very Low | High |
| A/B Test | None | Fast | Medium | Low | High |
| Recreate | Yes | Slow | Low | High | Very Low |
| Shadow | None | N/A | High | Very Low | Very High |

## When to Use Each Strategy

### Rolling Update
- Default for most applications
- Stateless applications
- Gradual deployments acceptable

### Blue-Green
- Critical applications
- Need instant rollback
- Can afford double resources
- Database migrations

### Canary
- High-traffic applications
- Want to test with real users
- Risk-averse deployments
- Performance testing

### A/B Testing
- Feature experimentation
- Business metrics driven
- Different versions for different users

### Recreate
- Development/staging
- Stateful applications
- Not concerned about downtime
- Database schema changes

### Shadow
- Performance validation
- Load testing
- High-risk changes
- Migration validation
