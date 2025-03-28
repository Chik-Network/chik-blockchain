from __future__ import annotations

import logging

import pytest
from chik_rs import G1Element
from chik_rs.sized_bytes import bytes32
from chik_rs.sized_ints import uint8, uint64

from chik.plot_sync.delta import Delta, DeltaType, PathListDelta, PlotListDelta
from chik.protocols.harvester_protocol import Plot

log = logging.getLogger(__name__)


def dummy_plot(path: str) -> Plot:
    return Plot(
        filename=path,
        size=uint8(32),
        plot_id=bytes32(b"\00" * 32),
        pool_public_key=G1Element(),
        pool_contract_puzzle_hash=None,
        plot_public_key=G1Element(),
        file_size=uint64(0),
        time_modified=uint64(0),
        compression_level=uint8(0),
    )


@pytest.mark.parametrize(
    ["delta"],
    [
        pytest.param(PathListDelta(), id="path list"),
        pytest.param(PlotListDelta(), id="plot list"),
    ],
)
def test_list_delta(delta: DeltaType) -> None:
    assert delta.empty()
    if type(delta) is PathListDelta:
        assert delta.additions == []
    elif type(delta) is PlotListDelta:
        assert delta.additions == {}
    else:
        assert False
    assert delta.removals == []
    assert delta.empty()
    if type(delta) is PathListDelta:
        delta.additions.append("0")
    elif type(delta) is PlotListDelta:
        delta.additions["0"] = dummy_plot("0")
    else:
        assert False, "Invalid delta type"
    assert not delta.empty()
    delta.removals.append("0")
    assert not delta.empty()
    delta.additions.clear()
    assert not delta.empty()
    delta.clear()
    assert delta.empty()


@pytest.mark.parametrize(
    ["old", "new", "result"],
    [
        [[], [], PathListDelta()],
        [["1"], ["0"], PathListDelta(["0"], ["1"])],
        [["1", "2", "3"], ["1", "2", "3"], PathListDelta([], [])],
        [["2", "1", "3"], ["2", "3", "1"], PathListDelta([], [])],
        [["2"], ["2", "3", "1"], PathListDelta(["3", "1"], [])],
        [["2"], ["1", "3"], PathListDelta(["1", "3"], ["2"])],
        [["1"], ["1", "2", "3"], PathListDelta(["2", "3"], [])],
        [[], ["1", "2", "3"], PathListDelta(["1", "2", "3"], [])],
        [["-1"], ["1", "2", "3"], PathListDelta(["1", "2", "3"], ["-1"])],
        [["-1", "1"], ["2", "3"], PathListDelta(["2", "3"], ["-1", "1"])],
        [["-1", "1", "2"], ["2", "3"], PathListDelta(["3"], ["-1", "1"])],
        [["-1", "2", "3"], ["2", "3"], PathListDelta([], ["-1"])],
        [["-1", "2", "3", "-2"], ["2", "3"], PathListDelta([], ["-1", "-2"])],
        [["-2", "2", "3", "-1"], ["2", "3"], PathListDelta([], ["-2", "-1"])],
    ],
)
def test_path_list_delta_from_lists(old: list[str], new: list[str], result: PathListDelta) -> None:
    assert PathListDelta.from_lists(old, new) == result


def test_delta_empty() -> None:
    delta: Delta = Delta()
    all_deltas: list[DeltaType] = [delta.valid, delta.invalid, delta.keys_missing, delta.duplicates]
    assert delta.empty()
    for d1 in all_deltas:
        delta.valid.additions["0"] = dummy_plot("0")
        delta.invalid.additions.append("0")
        delta.keys_missing.additions.append("0")
        delta.duplicates.additions.append("0")
        assert not delta.empty()
        for d2 in all_deltas:
            if d2 is not d1:
                d2.clear()
            assert not delta.empty()
        assert not delta.empty()
        d1.clear()
        assert delta.empty()
