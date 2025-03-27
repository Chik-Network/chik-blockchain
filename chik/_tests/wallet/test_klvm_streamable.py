from __future__ import annotations

import dataclasses
from typing import Optional

import pytest
from chik_rs.sized_bytes import bytes32
from chik_rs.sized_ints import uint64

from chik.types.blockchain_format.program import Program
from chik.util.streamable import Streamable, streamable
from chik.wallet.signer_protocol import Coin, Spend
from chik.wallet.util.klvm_streamable import (
    TranslationLayer,
    TranslationLayerMapping,
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
    assert program_serialize_klvm_streamable(instance) == Program.to([("a", "1")])
    assert byte_serialize_klvm_streamable(instance).hex() == "ffff613180"
    assert json_serialize_with_klvm_streamable(instance) == "ffff613180"
    assert program_deserialize_klvm_streamable(Program.to([("a", "1")]), BasicKLVMStreamable) == instance
    assert byte_deserialize_klvm_streamable(bytes.fromhex("ffff613180"), BasicKLVMStreamable) == instance
    assert json_deserialize_with_klvm_streamable("ffff613180", BasicKLVMStreamable) == instance


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
    assert json_serialize_with_klvm_streamable(instance) == {"inside": "ffff613180", "a": "1"}
    assert json_deserialize_with_klvm_streamable({"inside": "ffff613180", "a": "1"}, OutsideStreamable) == instance
    assert OutsideStreamable.from_json_dict({"a": "1", "inside": {"a": "1"}}) == instance

    instance_klvm = OutsideKLVM(a="1", inside=BasicKLVMStreamable(a="1"))
    assert program_serialize_klvm_streamable(instance_klvm) == Program.to([["inside", ("a", "1")], ("a", "1")])
    assert byte_serialize_klvm_streamable(instance_klvm).hex() == "ffff86696e73696465ffff613180ffff613180"
    assert json_serialize_with_klvm_streamable(instance_klvm) == "ffff86696e73696465ffff613180ffff613180"
    assert (
        program_deserialize_klvm_streamable(Program.to([["inside", ("a", "1")], ("a", "1")]), OutsideKLVM)
        == instance_klvm
    )
    assert (
        byte_deserialize_klvm_streamable(bytes.fromhex("ffff86696e73696465ffff613180ffff613180"), OutsideKLVM)
        == instance_klvm
    )
    assert json_deserialize_with_klvm_streamable("ffff86696e73696465ffff613180ffff613180", OutsideKLVM) == instance_klvm


@streamable
@dataclasses.dataclass(frozen=True)
class Compound(Streamable):
    optional: Optional[BasicKLVMStreamable]
    list: list[BasicKLVMStreamable]


@klvm_streamable
@dataclasses.dataclass(frozen=True)
class CompoundKLVM(Streamable):
    optional: Optional[BasicKLVMStreamable]
    list: list[BasicKLVMStreamable]


def test_compound_type_serialization() -> None:
    # regular streamable + regular values
    instance = Compound(optional=BasicKLVMStreamable(a="1"), list=[BasicKLVMStreamable(a="1")])
    assert json_serialize_with_klvm_streamable(instance) == {"optional": "ffff613180", "list": ["ffff613180"]}
    assert (
        json_deserialize_with_klvm_streamable({"optional": "ffff613180", "list": ["ffff613180"]}, Compound) == instance
    )
    assert Compound.from_json_dict({"optional": {"a": "1"}, "list": [{"a": "1"}]}) == instance

    # regular streamable + falsey values
    instance = Compound(optional=None, list=[])
    assert json_serialize_with_klvm_streamable(instance) == {"optional": None, "list": []}
    assert json_deserialize_with_klvm_streamable({"optional": None, "list": []}, Compound) == instance
    assert Compound.from_json_dict({"optional": None, "list": []}) == instance

    # klvm streamable + regular values
    instance_klvm = CompoundKLVM(optional=BasicKLVMStreamable(a="1"), list=[BasicKLVMStreamable(a="1")])
    assert program_serialize_klvm_streamable(instance_klvm) == Program.to(
        [["optional", 1, (97, 49)], ["list", [(97, 49)]]]
    )
    assert (
        byte_serialize_klvm_streamable(instance_klvm).hex()
        == "ffff886f7074696f6e616cff01ffff613180ffff846c697374ffffff6131808080"
    )
    assert (
        json_serialize_with_klvm_streamable(instance_klvm)
        == "ffff886f7074696f6e616cff01ffff613180ffff846c697374ffffff6131808080"
    )
    assert (
        program_deserialize_klvm_streamable(Program.to([["optional", 1, (97, 49)], ["list", [(97, 49)]]]), CompoundKLVM)
        == instance_klvm
    )
    assert (
        byte_deserialize_klvm_streamable(
            bytes.fromhex("ffff886f7074696f6e616cff01ffff613180ffff846c697374ffffff6131808080"), CompoundKLVM
        )
        == instance_klvm
    )
    assert (
        json_deserialize_with_klvm_streamable(
            "ffff886f7074696f6e616cff01ffff613180ffff846c697374ffffff6131808080", CompoundKLVM
        )
        == instance_klvm
    )

    # klvm streamable + falsey values
    instance_klvm = CompoundKLVM(optional=None, list=[])
    assert program_serialize_klvm_streamable(instance_klvm) == Program.to([["optional", 0], ["list"]])
    assert byte_serialize_klvm_streamable(instance_klvm).hex() == "ffff886f7074696f6e616cff8080ffff846c6973748080"
    assert json_serialize_with_klvm_streamable(instance_klvm) == "ffff886f7074696f6e616cff8080ffff846c6973748080"
    assert program_deserialize_klvm_streamable(Program.to([["optional", 0], ["list"]]), CompoundKLVM) == instance_klvm
    assert (
        byte_deserialize_klvm_streamable(bytes.fromhex("ffff886f7074696f6e616cff8080ffff846c6973748080"), CompoundKLVM)
        == instance_klvm
    )
    assert (
        json_deserialize_with_klvm_streamable("ffff886f7074696f6e616cff8080ffff846c6973748080", CompoundKLVM)
        == instance_klvm
    )

    with pytest.raises(ValueError, match="@klvm_streamable"):

        @klvm_streamable
        @dataclasses.dataclass(frozen=True)
        class DoesntWork(Streamable):
            tuples_are_not_supported: tuple[str]


@klvm_streamable
@dataclasses.dataclass(frozen=True)
class FooSpend(Streamable):
    coin: Coin
    puzzle_and_solution: Program

    @staticmethod
    def from_wallet_api(_from: Spend) -> FooSpend:
        return FooSpend(
            _from.coin,
            Program.to((_from.puzzle, _from.solution)),
        )

    @staticmethod
    def to_wallet_api(_from: FooSpend) -> Spend:
        return Spend(
            _from.coin,
            _from.puzzle_and_solution.first(),
            _from.puzzle_and_solution.rest(),
        )


def test_translation_layer() -> None:
    FOO_TRANSLATION = TranslationLayer(
        [
            TranslationLayerMapping(
                Spend,
                FooSpend,
                FooSpend.from_wallet_api,
                FooSpend.to_wallet_api,
            )
        ]
    )

    coin = Coin(bytes32.zeros, bytes32.zeros, uint64(0))
    spend = Spend(
        coin,
        Program.to("puzzle"),
        Program.to("solution"),
    )
    foo_spend = FooSpend(
        coin,
        Program.to(("puzzle", "solution")),
    )

    byte_serialize_klvm_streamable(foo_spend) == byte_serialize_klvm_streamable(
        spend, translation_layer=FOO_TRANSLATION
    )
    program_serialize_klvm_streamable(foo_spend) == program_serialize_klvm_streamable(
        spend, translation_layer=FOO_TRANSLATION
    )
    json_serialize_with_klvm_streamable(foo_spend) == json_serialize_with_klvm_streamable(
        spend, translation_layer=FOO_TRANSLATION
    )
    assert spend == byte_deserialize_klvm_streamable(
        byte_serialize_klvm_streamable(foo_spend), Spend, translation_layer=FOO_TRANSLATION
    )
    assert spend == program_deserialize_klvm_streamable(
        program_serialize_klvm_streamable(foo_spend), Spend, translation_layer=FOO_TRANSLATION
    )
    assert spend == json_deserialize_with_klvm_streamable(
        json_serialize_with_klvm_streamable(foo_spend), Spend, translation_layer=FOO_TRANSLATION
    )

    # Deserialization should only work now if using the translation layer
    with pytest.raises(Exception):
        byte_deserialize_klvm_streamable(byte_serialize_klvm_streamable(foo_spend), Spend)
    with pytest.raises(Exception):
        program_deserialize_klvm_streamable(program_serialize_klvm_streamable(foo_spend), Spend)
    with pytest.raises(Exception):
        json_deserialize_with_klvm_streamable(json_serialize_with_klvm_streamable(foo_spend), Spend)

    # Test that types not registered with translation layer are serialized properly
    assert coin == byte_deserialize_klvm_streamable(
        byte_serialize_klvm_streamable(coin, translation_layer=FOO_TRANSLATION), Coin, translation_layer=FOO_TRANSLATION
    )
    assert coin == program_deserialize_klvm_streamable(
        program_serialize_klvm_streamable(coin, translation_layer=FOO_TRANSLATION),
        Coin,
        translation_layer=FOO_TRANSLATION,
    )
    assert coin == json_deserialize_with_klvm_streamable(
        json_serialize_with_klvm_streamable(coin, translation_layer=FOO_TRANSLATION),
        Coin,
        translation_layer=FOO_TRANSLATION,
    )
