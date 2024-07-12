from __future__ import annotations

import dataclasses
from typing import List, Optional, Tuple

import pytest

from chik.types.blockchain_format.program import Program
from chik.util.streamable import Streamable, streamable
from chik.wallet.util.klvm_streamable import (
    byte_deserialize_klvm_streamable,
    byte_serialize_klvm_streamable,
    klvm_streamable,
    json_deserialize_with_klvm_streamable,
    json_serialize_with_klvm_streamable,
    program_deserialize_klvm_streamable,
    program_serialize_klvm_streamable,
)


@klvm_streamable
@dataclasses.dataclass(frozen=True)
class BasicKLVMStreamable(Streamable):
    a: str


def test_basic_serialization() -> None:
    instance = BasicKLVMStreamable(a="1")
    assert program_serialize_klvm_streamable(instance) == Program.to(["1"])
    assert byte_serialize_klvm_streamable(instance).hex() == "ff3180"
    assert json_serialize_with_klvm_streamable(instance) == "ff3180"
    assert program_deserialize_klvm_streamable(Program.to(["1"]), BasicKLVMStreamable) == instance
    assert byte_deserialize_klvm_streamable(bytes.fromhex("ff3180"), BasicKLVMStreamable) == instance
    assert json_deserialize_with_klvm_streamable("ff3180", BasicKLVMStreamable) == instance


@streamable
@dataclasses.dataclass(frozen=True)
class OutsideStreamable(Streamable):
    inside: BasicKLVMStreamable
    a: str


@klvm_streamable
@dataclasses.dataclass(frozen=True)
class OutsideKLVM(Streamable):
    inside: BasicKLVMStreamable
    a: str


def test_nested_serialization() -> None:
    instance = OutsideStreamable(a="1", inside=BasicKLVMStreamable(a="1"))
    assert json_serialize_with_klvm_streamable(instance) == {"inside": "ff3180", "a": "1"}
    assert json_deserialize_with_klvm_streamable({"inside": "ff3180", "a": "1"}, OutsideStreamable) == instance
    assert OutsideStreamable.from_json_dict({"a": "1", "inside": {"a": "1"}}) == instance

    instance_klvm = OutsideKLVM(a="1", inside=BasicKLVMStreamable(a="1"))
    assert program_serialize_klvm_streamable(instance_klvm) == Program.to([["1"], "1"])
    assert byte_serialize_klvm_streamable(instance_klvm).hex() == "ffff3180ff3180"
    assert json_serialize_with_klvm_streamable(instance_klvm) == "ffff3180ff3180"
    assert program_deserialize_klvm_streamable(Program.to([["1"], "1"]), OutsideKLVM) == instance_klvm
    assert byte_deserialize_klvm_streamable(bytes.fromhex("ffff3180ff3180"), OutsideKLVM) == instance_klvm
    assert json_deserialize_with_klvm_streamable("ffff3180ff3180", OutsideKLVM) == instance_klvm


@streamable
@dataclasses.dataclass(frozen=True)
class Compound(Streamable):
    optional: Optional[BasicKLVMStreamable]
    list: List[BasicKLVMStreamable]


@klvm_streamable
@dataclasses.dataclass(frozen=True)
class CompoundKLVM(Streamable):
    optional: Optional[BasicKLVMStreamable]
    list: List[BasicKLVMStreamable]


def test_compound_type_serialization() -> None:
    # regular streamable + regular values
    instance = Compound(optional=BasicKLVMStreamable(a="1"), list=[BasicKLVMStreamable(a="1")])
    assert json_serialize_with_klvm_streamable(instance) == {"optional": "ff3180", "list": ["ff3180"]}
    assert json_deserialize_with_klvm_streamable({"optional": "ff3180", "list": ["ff3180"]}, Compound) == instance
    assert Compound.from_json_dict({"optional": {"a": "1"}, "list": [{"a": "1"}]}) == instance

    # regular streamable + falsey values
    instance = Compound(optional=None, list=[])
    assert json_serialize_with_klvm_streamable(instance) == {"optional": None, "list": []}
    assert json_deserialize_with_klvm_streamable({"optional": None, "list": []}, Compound) == instance
    assert Compound.from_json_dict({"optional": None, "list": []}) == instance

    # klvm streamable + regular values
    instance_klvm = CompoundKLVM(optional=BasicKLVMStreamable(a="1"), list=[BasicKLVMStreamable(a="1")])
    assert program_serialize_klvm_streamable(instance_klvm) == Program.to([[True, "1"], [["1"]]])
    assert byte_serialize_klvm_streamable(instance_klvm).hex() == "ffff01ff3180ffffff31808080"
    assert json_serialize_with_klvm_streamable(instance_klvm) == "ffff01ff3180ffffff31808080"
    assert program_deserialize_klvm_streamable(Program.to([[True, "1"], [["1"]]]), CompoundKLVM) == instance_klvm
    assert byte_deserialize_klvm_streamable(bytes.fromhex("ffff01ff3180ffffff31808080"), CompoundKLVM) == instance_klvm
    assert json_deserialize_with_klvm_streamable("ffff01ff3180ffffff31808080", CompoundKLVM) == instance_klvm

    # klvm streamable + falsey values
    instance_klvm = CompoundKLVM(optional=None, list=[])
    assert program_serialize_klvm_streamable(instance_klvm) == Program.to([[0], []])
    assert byte_serialize_klvm_streamable(instance_klvm).hex() == "ffff8080ff8080"
    assert json_serialize_with_klvm_streamable(instance_klvm) == "ffff8080ff8080"
    assert program_deserialize_klvm_streamable(Program.to([[0, 0], []]), CompoundKLVM) == instance_klvm
    assert byte_deserialize_klvm_streamable(bytes.fromhex("ffff8080ff8080"), CompoundKLVM) == instance_klvm
    assert json_deserialize_with_klvm_streamable("ffff8080ff8080", CompoundKLVM) == instance_klvm

    with pytest.raises(ValueError, match="@klvm_streamable"):

        @klvm_streamable
        @dataclasses.dataclass(frozen=True)
        class DoesntWork(Streamable):
            tuples_are_not_supported: Tuple[str]
