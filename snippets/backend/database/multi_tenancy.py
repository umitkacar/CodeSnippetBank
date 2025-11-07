# Multi-tenancy
filter_by_tenant = lambda q, tid: q.filter_by(tenant_id=tid)