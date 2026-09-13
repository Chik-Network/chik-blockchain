from __future__ import annotations

import dataclasses

import pytest
from chik_rs.sized_bytes import bytes32
from chik_rs.sized_ints import uint64

from chik.types.blockchain_format.program import Program
from chik.util.streamable import Streamable, streamable
from chik.wallet.signer_protocol import Coin, Spend
from chik.wallet.util.clvk_streamable import (
    TranslationLayer,
    TranslationLayerMapping,
    byte_deserialize_clvk_streamable,
    byte_serialize_clvk_streamable,
    clvk_streamable,
    json_deserialize_with_clvk_streamable,
    json_serialize_with_clvk_streamable,
    program_deserialize_clvk_streamable,
    program_serialize_clvk_streamable,
)


@clvk_streamable
@dataclasses.dataclass(frozen=True)
class BasicCLVKStreamable(Streamable):
    a: str


def test_basic_serialization() -> None:
    instance = BasicCLVKStreamable(a="1")
    assert program_serialize_clvk_streamable(instance) == Program.to([("a", "1")])
    assert byte_serialize_clvk_streamable(instance).hex() == "ffff613180"
    assert json_serialize_with_clvk_streamable(instance) == "ffff613180"
    assert program_deserialize_clvk_streamable(Program.to([("a", "1")]), BasicCLVKStreamable) == instance
    assert byte_deserialize_clvk_streamable(bytes.fromhex("ffff613180"), BasicCLVKStreamable) == instance
    assert json_deserialize_with_clvk_streamable("ffff613180", BasicCLVKStreamable) == instance


@streamable
@dataclasses.dataclass(frozen=True)
class OutsideStreamable(Streamable):
    inside: BasicCLVKStreamable
    a: str


@clvk_streamable
@dataclasses.dataclass(frozen=True)
class OutsideCLVK(Streamable):
    inside: BasicCLVKStreamable
    a: str


def test_nested_serialization() -> None:
    instance = OutsideStreamable(a="1", inside=BasicCLVKStreamable(a="1"))
    assert json_serialize_with_clvk_streamable(instance) == {"inside": "ffff613180", "a": "1"}
    assert json_deserialize_with_clvk_streamable({"inside": "ffff613180", "a": "1"}, OutsideStreamable) == instance
    assert OutsideStreamable.from_json_dict({"a": "1", "inside": {"a": "1"}}) == instance

    instance_clvk = OutsideCLVK(a="1", inside=BasicCLVKStreamable(a="1"))
    assert program_serialize_clvk_streamable(instance_clvk) == Program.to([["inside", ("a", "1")], ("a", "1")])
    assert byte_serialize_clvk_streamable(instance_clvk).hex() == "ffff86696e73696465ffff613180ffff613180"
    assert json_serialize_with_clvk_streamable(instance_clvk) == "ffff86696e73696465ffff613180ffff613180"
    assert (
        program_deserialize_clvk_streamable(Program.to([["inside", ("a", "1")], ("a", "1")]), OutsideCLVK)
        == instance_clvk
    )
    assert (
        byte_deserialize_clvk_streamable(bytes.fromhex("ffff86696e73696465ffff613180ffff613180"), OutsideCLVK)
        == instance_clvk
    )
    assert json_deserialize_with_clvk_streamable("ffff86696e73696465ffff613180ffff613180", OutsideCLVK) == instance_clvk


@streamable
@dataclasses.dataclass(frozen=True)
class Compound(Streamable):
    optional: BasicCLVKStreamable | None
    list: list[BasicCLVKStreamable]


@clvk_streamable
@dataclasses.dataclass(frozen=True)
class CompoundCLVK(Streamable):
    optional: BasicCLVKStreamable | None
    list: list[BasicCLVKStreamable]


def test_compound_type_serialization() -> None:
    # regular streamable + regular values
    instance = Compound(optional=BasicCLVKStreamable(a="1"), list=[BasicCLVKStreamable(a="1")])
    assert json_serialize_with_clvk_streamable(instance) == {"optional": "ffff613180", "list": ["ffff613180"]}
    assert (
        json_deserialize_with_clvk_streamable({"optional": "ffff613180", "list": ["ffff613180"]}, Compound) == instance
    )
    assert Compound.from_json_dict({"optional": {"a": "1"}, "list": [{"a": "1"}]}) == instance

    # regular streamable + falsey values
    instance = Compound(optional=None, list=[])
    assert json_serialize_with_clvk_streamable(instance) == {"optional": None, "list": []}
    assert json_deserialize_with_clvk_streamable({"optional": None, "list": []}, Compound) == instance
    assert Compound.from_json_dict({"optional": None, "list": []}) == instance

    # clvk streamable + regular values
    instance_clvk = CompoundCLVK(optional=BasicCLVKStreamable(a="1"), list=[BasicCLVKStreamable(a="1")])
    assert program_serialize_clvk_streamable(instance_clvk) == Program.to(
        [["optional", 1, (97, 49)], ["list", [(97, 49)]]]
    )
    assert (
        byte_serialize_clvk_streamable(instance_clvk).hex()
        == "ffff886f7074696f6e616cff01ffff613180ffff846c697374ffffff6131808080"
    )
    assert (
        json_serialize_with_clvk_streamable(instance_clvk)
        == "ffff886f7074696f6e616cff01ffff613180ffff846c697374ffffff6131808080"
    )
    assert (
        program_deserialize_clvk_streamable(Program.to([["optional", 1, (97, 49)], ["list", [(97, 49)]]]), CompoundCLVK)
        == instance_clvk
    )
    assert (
        byte_deserialize_clvk_streamable(
            bytes.fromhex("ffff886f7074696f6e616cff01ffff613180ffff846c697374ffffff6131808080"), CompoundCLVK
        )
        == instance_clvk
    )
    assert (
        json_deserialize_with_clvk_streamable(
            "ffff886f7074696f6e616cff01ffff613180ffff846c697374ffffff6131808080", CompoundCLVK
        )
        == instance_clvk
    )

    # clvk streamable + falsey values
    instance_clvk = CompoundCLVK(optional=None, list=[])
    assert program_serialize_clvk_streamable(instance_clvk) == Program.to([["optional", 0], ["list"]])
    assert byte_serialize_clvk_streamable(instance_clvk).hex() == "ffff886f7074696f6e616cff8080ffff846c6973748080"
    assert json_serialize_with_clvk_streamable(instance_clvk) == "ffff886f7074696f6e616cff8080ffff846c6973748080"
    assert program_deserialize_clvk_streamable(Program.to([["optional", 0], ["list"]]), CompoundCLVK) == instance_clvk
    assert (
        byte_deserialize_clvk_streamable(bytes.fromhex("ffff886f7074696f6e616cff8080ffff846c6973748080"), CompoundCLVK)
        == instance_clvk
    )
    assert (
        json_deserialize_with_clvk_streamable("ffff886f7074696f6e616cff8080ffff846c6973748080", CompoundCLVK)
        == instance_clvk
    )

    with pytest.raises(ValueError, match="@clvk_streamable"):

        @clvk_streamable
        @dataclasses.dataclass(frozen=True)
        class DoesntWork(Streamable):
            tuples_are_not_supported: tuple[str]


@clvk_streamable
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

    assert byte_serialize_clvk_streamable(foo_spend) == byte_serialize_clvk_streamable(
        spend, translation_layer=FOO_TRANSLATION
    )
    assert program_serialize_clvk_streamable(foo_spend) == program_serialize_clvk_streamable(
        spend, translation_layer=FOO_TRANSLATION
    )
    assert json_serialize_with_clvk_streamable(foo_spend) == json_serialize_with_clvk_streamable(
        spend, translation_layer=FOO_TRANSLATION
    )
    assert spend == byte_deserialize_clvk_streamable(
        byte_serialize_clvk_streamable(foo_spend), Spend, translation_layer=FOO_TRANSLATION
    )
    assert spend == program_deserialize_clvk_streamable(
        program_serialize_clvk_streamable(foo_spend), Spend, translation_layer=FOO_TRANSLATION
    )
    assert spend == json_deserialize_with_clvk_streamable(
        json_serialize_with_clvk_streamable(foo_spend), Spend, translation_layer=FOO_TRANSLATION
    )

    # Deserialization should only work now if using the translation layer
    with pytest.raises(Exception):
        byte_deserialize_clvk_streamable(byte_serialize_clvk_streamable(foo_spend), Spend)
    with pytest.raises(Exception):
        program_deserialize_clvk_streamable(program_serialize_clvk_streamable(foo_spend), Spend)
    with pytest.raises(Exception):
        json_deserialize_with_clvk_streamable(json_serialize_with_clvk_streamable(foo_spend), Spend)

    # Test that types not registered with translation layer are serialized properly
    assert coin == byte_deserialize_clvk_streamable(
        byte_serialize_clvk_streamable(coin, translation_layer=FOO_TRANSLATION), Coin, translation_layer=FOO_TRANSLATION
    )
    assert coin == program_deserialize_clvk_streamable(
        program_serialize_clvk_streamable(coin, translation_layer=FOO_TRANSLATION),
        Coin,
        translation_layer=FOO_TRANSLATION,
    )
    assert coin == json_deserialize_with_clvk_streamable(
        json_serialize_with_clvk_streamable(coin, translation_layer=FOO_TRANSLATION),
        Coin,
        translation_layer=FOO_TRANSLATION,
    )
