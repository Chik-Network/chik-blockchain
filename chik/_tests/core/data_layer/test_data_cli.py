from __future__ import annotations

import json

import pytest

from chik._tests.core.data_layer.util import ChikRoot

pytestmark = pytest.mark.data_layer


@pytest.mark.anyio
async def test_help(chik_root: ChikRoot) -> None:
    """Just a trivial test to make sure the subprocessing is at least working and the
    data executable does run.
    """
    completed_process = chik_root.run(args=["data", "--help"])
    assert "Show this message and exit" in completed_process.stdout


@pytest.mark.skip
@pytest.mark.anyio
def test_round_trip(chik_root: ChikRoot, chik_daemon: None, chik_data: None) -> None:
    """Create a table, insert a row, get the row by its hash."""

    with chik_root.print_log_after():
        create = chik_root.run(args=["data", "create_data_store"])
        print(f"create_data_store: {create}")
        dic = json.loads(create.stdout)
        assert dic["success"]
        store_id = dic["id"]
        key = "1a6f915513173902a7216e7d9e4a16bfd088e20683f45de3b432ce72e9cc7aa8"
        value = "ffff8353594d8083616263"
        changelist: list[dict[str, str]] = [{"action": "insert", "key": key, "value": value}]
        print(json.dumps(changelist))
        update = chik_root.run(
            args=["data", "update_data_store", "--id", store_id, "--changelist", json.dumps(changelist)]
        )
        dic = json.loads(create.stdout)
        assert dic["success"]
        print(f"update_data_store: {update}")
        completed_process = chik_root.run(args=["data", "get_value", "--id", store_id, "--key", key])
        parsed = json.loads(completed_process.stdout)
        expected = {"value": value, "success": True}
        assert parsed == expected
        get_keys_values = chik_root.run(args=["data", "get_keys_values", "--id", store_id])
        print(f"get_keys_values: {get_keys_values}")
        changelist = [{"action": "delete", "key": key}]
        update = chik_root.run(
            args=["data", "update_data_store", "--id", store_id, "--changelist", json.dumps(changelist)]
        )
        print(f"update_data_store: {update}")
        completed_process = chik_root.run(args=["data", "get_value", "--id", store_id, "--key", key])
        parsed = json.loads(completed_process.stdout)
        expected = {"data": None, "success": True}
        assert parsed == expected
