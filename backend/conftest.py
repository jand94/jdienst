def pytest_collection_modifyitems(session, config, items):
    target_suffix = "tests/test_test_results_email.py::test_send_test_results_email"
    target_items = [item for item in items if item.nodeid.endswith(target_suffix)]
    if not target_items:
        return
    remaining_items = [item for item in items if not item.nodeid.endswith(target_suffix)]
    items[:] = [*remaining_items, *target_items]
