from django.db import models


class HeaderName(models.TextChoices):
    IDEMPOTENCY_KEY = "Idempotency-Key", "Idempotency-Key"
    REQUEST_ID = "X-Request-ID", "X-Request-ID"
    CORRELATION_ID = "X-Correlation-ID", "X-Correlation-ID"
    TRACE_ID = "X-Trace-ID", "X-Trace-ID"
    TRACE_PARENT = "traceparent", "traceparent"
    TENANT_SLUG = "X-Tenant-Slug", "X-Tenant-Slug"
