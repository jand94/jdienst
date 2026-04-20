from __future__ import annotations

import os
import platform
import subprocess
import time
from datetime import datetime, timezone

import pytest
from django.conf import settings
from django.core.mail import get_connection, send_mail

_MODULE_START_TS = time.time()


def _collect_node_ids(terminal_reporter, key: str) -> list[str]:
    reports = terminal_reporter.stats.get(key, [])
    node_ids = {
        report.nodeid
        for report in reports
        if getattr(report, "nodeid", None) and getattr(report, "when", "call") == "call"
    }
    return sorted(node_ids)


def _run_git_command(*args: str) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            check=True,
            capture_output=True,
            text=True,
            timeout=2,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return "unknown"
    value = completed.stdout.strip()
    return value or "unknown"


def _resolve_git_metadata() -> tuple[str, str]:
    branch = (
        getattr(settings, "TEST_RESULTS_EMAIL_BRANCH", None)
        or os.getenv("GITHUB_REF_NAME")
        or os.getenv("CI_COMMIT_BRANCH")
        or _run_git_command("rev-parse", "--abbrev-ref", "HEAD")
    )
    sha = (
        getattr(settings, "TEST_RESULTS_EMAIL_COMMIT", None)
        or os.getenv("GITHUB_SHA")
        or os.getenv("CI_COMMIT_SHA")
        or _run_git_command("rev-parse", "HEAD")
    )
    return branch, sha


def _resolve_duration_seconds(terminal_reporter) -> float:
    start_time = getattr(terminal_reporter, "_sessionstarttime", None)
    if isinstance(start_time, (int, float)):
        duration = max(0.0, datetime.now(timezone.utc).timestamp() - float(start_time))
        return duration
    return max(0.0, time.time() - _MODULE_START_TS)


@pytest.mark.django_db
def test_send_test_results_email(request):
    if not getattr(settings, "TEST_RESULTS_EMAIL_ENABLED", False):
        pytest.skip("Test result email is disabled.")

    recipients = [item for item in getattr(settings, "TEST_RESULTS_EMAIL_RECIPIENTS", []) if item]
    if not recipients:
        pytest.fail("TEST_RESULTS_EMAIL_RECIPIENTS must not be empty when email sending is enabled.")

    terminal_reporter = request.config.pluginmanager.getplugin("terminalreporter")
    if terminal_reporter is None:
        pytest.fail("Could not access pytest terminal reporter.")

    passed = _collect_node_ids(terminal_reporter, "passed")
    failed = _collect_node_ids(terminal_reporter, "failed")
    skipped = _collect_node_ids(terminal_reporter, "skipped")
    xfailed = _collect_node_ids(terminal_reporter, "xfailed")
    xpassed = _collect_node_ids(terminal_reporter, "xpassed")
    error = _collect_node_ids(terminal_reporter, "error")
    current_node_id = request.node.nodeid
    if current_node_id not in {*passed, *failed, *skipped, *xfailed, *xpassed, *error}:
        passed.append(current_node_id)

    total_collected = int(
        getattr(terminal_reporter, "_numcollected", 0)
        or getattr(request.session, "testscollected", 0)
    )
    executed = len({*passed, *failed, *skipped, *xfailed, *xpassed, *error})
    final_status = "FAILED" if failed or error else "PASSED"
    finished_at = datetime.now(timezone.utc)
    branch, commit_sha = _resolve_git_metadata()
    duration_seconds = _resolve_duration_seconds(terminal_reporter)
    duration_human = f"{duration_seconds:.2f}s"
    short_sha = commit_sha[:8] if commit_sha != "unknown" else "unknown"
    run_stamp = finished_at.strftime("%Y-%m-%d %H:%M:%S UTC")
    subject = (
        f"{settings.TEST_RESULTS_EMAIL_SUBJECT_PREFIX} "
        f"Testlauf {final_status} ({run_stamp}, {short_sha}): "
        f"{len(passed)} passed, {len(failed)} failed"
    )

    failed_lines = "\n".join(f"- {node_id}" for node_id in [*failed, *error]) or "- keine"
    body = (
        f"Testlauf beendet: {finished_at.isoformat()}\n"
        f"Host: {platform.node()}\n"
        f"Python: {platform.python_version()}\n\n"
        f"Branch: {branch}\n"
        f"Commit: {commit_sha}\n"
        f"Dauer: {duration_human}\n\n"
        f"Status: {final_status}\n"
        f"Collected: {total_collected}\n"
        f"Executed so far: {executed}\n"
        f"Passed: {len(passed)}\n"
        f"Failed: {len(failed)}\n"
        f"Errors: {len(error)}\n"
        f"Skipped: {len(skipped)}\n"
        f"XFailed: {len(xfailed)}\n"
        f"XPassed: {len(xpassed)}\n\n"
        "Fehlgeschlagene Tests:\n"
        f"{failed_lines}\n"
    )

    smtp_connection = get_connection(
        backend="django.core.mail.backends.smtp.EmailBackend",
        host=settings.EMAIL_HOST,
        port=settings.EMAIL_PORT,
        username=settings.EMAIL_HOST_USER,
        password=settings.EMAIL_HOST_PASSWORD,
        use_tls=settings.EMAIL_USE_TLS,
        use_ssl=settings.EMAIL_USE_SSL,
        timeout=settings.EMAIL_TIMEOUT,
    )
    sent_count = send_mail(
        subject=subject,
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
        fail_silently=False,
        connection=smtp_connection,
    )
    assert sent_count >= 1
