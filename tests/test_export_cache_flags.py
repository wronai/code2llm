from types import SimpleNamespace

from code2llm.cli_exports.orchestrator import _should_skip_export_cache


def test_force_skips_export_cache():
    args = SimpleNamespace(no_cache=False, force=True)

    assert _should_skip_export_cache(args, is_chunked=False) is True


def test_no_cache_skips_export_cache():
    args = SimpleNamespace(no_cache=True, force=False)

    assert _should_skip_export_cache(args, is_chunked=False) is True


def test_chunked_skips_export_cache():
    args = SimpleNamespace(no_cache=False, force=False)

    assert _should_skip_export_cache(args, is_chunked=True) is True


def test_standard_run_can_use_export_cache():
    args = SimpleNamespace(no_cache=False, force=False)

    assert _should_skip_export_cache(args, is_chunked=False) is False
