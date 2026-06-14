"""Observability hooks: Prometheus /metrics and OpenTelemetry tracing.

Both are opt-in via ENABLE_METRICS / ENABLE_TRACING and degrade silently if the
optional packages (install with ``.[observability]``) are missing.
"""
from __future__ import annotations

from app.core.config import settings


def setup_metrics(app) -> None:
    if not settings.enable_metrics:
        return
    try:
        from prometheus_fastapi_instrumentator import Instrumentator

        Instrumentator().instrument(app).expose(app, endpoint="/metrics")
    except ImportError:
        pass


def setup_tracing(app) -> None:
    if not settings.enable_tracing:
        return
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        provider = TracerProvider(resource=Resource.create({"service.name": settings.app_name}))
        if settings.otel_exporter_endpoint:
            provider.add_span_processor(
                BatchSpanProcessor(OTLPSpanExporter(endpoint=settings.otel_exporter_endpoint))
            )
        trace.set_tracer_provider(provider)
        FastAPIInstrumentor.instrument_app(app)
    except ImportError:
        pass
