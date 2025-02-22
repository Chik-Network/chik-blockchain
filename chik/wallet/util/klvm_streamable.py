from __future__ import annotations

import dataclasses
import functools
from types import MappingProxyType
from typing import Any, Callable, Generic, Optional, TypeVar, Union, get_args, get_type_hints

from hsmk.klvm_serde import from_program_for_type, to_program_for_type
from typing_extensions import TypeGuard

from chik.types.blockchain_format.program import Program
from chik.util.streamable import (
    Streamable,
    function_to_convert_one_item,
    is_type_List,
    is_type_SpecificOptional,
    is_type_Tuple,
    recurse_jsonify,
    streamable,
)

_T_Streamable = TypeVar("_T_Streamable", bound=Streamable)


def klvm_streamable(cls: type[Streamable]) -> type[Streamable]:
    wrapped_cls: type[Streamable] = streamable(cls)
    setattr(wrapped_cls, "_klvm_streamable", True)

    hints = get_type_hints(cls)
    # no way to hint that wrapped_cls is a dataclass here but @streamable checks that
    for field in dataclasses.fields(wrapped_cls):  # type: ignore[arg-type]
        field.metadata = MappingProxyType({"key": field.name, **field.metadata})
        if is_type_Tuple(hints[field.name]):
            raise ValueError("@klvm_streamable does not support tuples")

    return wrapped_cls


def program_serialize_klvm_streamable(
    klvm_streamable: Streamable, translation_layer: Optional[TranslationLayer] = None
) -> Program:
    if translation_layer is not None:
        mapping = translation_layer.get_mapping(klvm_streamable.__class__)
        if mapping is not None:
            klvm_streamable = translation_layer.serialize_for_translation(klvm_streamable, mapping)
    # Underlying hinting problem with klvm_serde
    return to_program_for_type(type(klvm_streamable))(klvm_streamable)  # type: ignore[no-any-return]


def byte_serialize_klvm_streamable(
    klvm_streamable: Streamable, translation_layer: Optional[TranslationLayer] = None
) -> bytes:
    return bytes(program_serialize_klvm_streamable(klvm_streamable, translation_layer=translation_layer))


def json_serialize_with_klvm_streamable(
    streamable: object,
    next_recursion_step: Optional[Callable[..., dict[str, Any]]] = None,
    translation_layer: Optional[TranslationLayer] = None,
    **next_recursion_env: Any,
) -> Union[str, dict[str, Any]]:
    if next_recursion_step is None:
        next_recursion_step = recurse_jsonify
    if is_klvm_streamable(streamable):
        # If we are using klvm_serde, we stop JSON serialization at this point and instead return the klvm blob
        return byte_serialize_klvm_streamable(streamable, translation_layer=translation_layer).hex()
    else:
        return next_recursion_step(
            streamable, json_serialize_with_klvm_streamable, translation_layer=translation_layer, **next_recursion_env
        )


def program_deserialize_klvm_streamable(
    program: Program, klvm_streamable_type: type[_T_Streamable], translation_layer: Optional[TranslationLayer] = None
) -> _T_Streamable:
    type_to_deserialize_from: type[Streamable] = klvm_streamable_type
    if translation_layer is not None:
        mapping = translation_layer.get_mapping(klvm_streamable_type)
        if mapping is not None:
            type_to_deserialize_from = mapping.to_type
    as_instance = from_program_for_type(type_to_deserialize_from)(program)
    if translation_layer is not None and mapping is not None:
        return translation_layer.deserialize_from_translation(as_instance, mapping)
    else:
        # Underlying hinting problem with klvm_serde
        return as_instance  # type: ignore[no-any-return]


def byte_deserialize_klvm_streamable(
    blob: bytes, klvm_streamable_type: type[_T_Streamable], translation_layer: Optional[TranslationLayer] = None
) -> _T_Streamable:
    return program_deserialize_klvm_streamable(
        Program.from_bytes(blob), klvm_streamable_type, translation_layer=translation_layer
    )


def is_compound_type(typ: Any) -> bool:
    return is_type_SpecificOptional(typ) or is_type_Tuple(typ) or is_type_List(typ)


# TODO: this is more than _just_ a Streamable, but it is also a Streamable and that's
#       useful for now
def is_klvm_streamable_type(v: type[object]) -> TypeGuard[type[Streamable]]:
    return issubclass(v, Streamable) and hasattr(v, "_klvm_streamable")


# TODO: this is more than _just_ a Streamable, but it is also a Streamable and that's
#       useful for now
def is_klvm_streamable(v: object) -> TypeGuard[Streamable]:
    return isinstance(v, Streamable) and hasattr(v, "_klvm_streamable")


def json_deserialize_with_klvm_streamable(
    json_dict: Union[str, dict[str, Any]],
    streamable_type: type[_T_Streamable],
    translation_layer: Optional[TranslationLayer] = None,
) -> _T_Streamable:
    if isinstance(json_dict, str):
        return byte_deserialize_klvm_streamable(
            bytes.fromhex(json_dict), streamable_type, translation_layer=translation_layer
        )
    else:
        old_streamable_fields = streamable_type.streamable_fields()
        new_streamable_fields = []
        for old_field in old_streamable_fields:
            if is_compound_type(old_field.type):
                inner_type = get_args(old_field.type)[0]
                if is_klvm_streamable_type(inner_type):
                    new_streamable_fields.append(
                        dataclasses.replace(
                            old_field,
                            convert_function=function_to_convert_one_item(
                                old_field.type,
                                functools.partial(
                                    json_deserialize_with_klvm_streamable,
                                    streamable_type=inner_type,
                                    translation_layer=translation_layer,
                                ),
                            ),
                        )
                    )
                else:
                    new_streamable_fields.append(old_field)
            elif is_klvm_streamable_type(old_field.type):
                new_streamable_fields.append(
                    dataclasses.replace(
                        old_field,
                        convert_function=functools.partial(
                            json_deserialize_with_klvm_streamable,
                            streamable_type=old_field.type,
                            translation_layer=translation_layer,
                        ),
                    )
                )
            else:
                new_streamable_fields.append(old_field)

        setattr(streamable_type, "_streamable_fields", tuple(new_streamable_fields))
        return streamable_type.from_json_dict(json_dict)


_T_KlvmStreamable = TypeVar("_T_KlvmStreamable", bound="Streamable")
_T_TLKlvmStreamable = TypeVar("_T_TLKlvmStreamable", bound="Streamable")


@dataclasses.dataclass(frozen=True)
class TranslationLayerMapping(Generic[_T_KlvmStreamable, _T_TLKlvmStreamable]):
    from_type: type[_T_KlvmStreamable]
    to_type: type[_T_TLKlvmStreamable]
    serialize_function: Callable[[_T_KlvmStreamable], _T_TLKlvmStreamable]
    deserialize_function: Callable[[_T_TLKlvmStreamable], _T_KlvmStreamable]


@dataclasses.dataclass(frozen=True)
class TranslationLayer:
    type_mappings: list[TranslationLayerMapping[Any, Any]]

    def get_mapping(
        self, _type: type[_T_KlvmStreamable]
    ) -> Optional[TranslationLayerMapping[_T_KlvmStreamable, Streamable]]:
        mappings = [m for m in self.type_mappings if m.from_type == _type]
        if len(mappings) == 1:
            return mappings[0]
        elif len(mappings) == 0:
            return None
        else:  # pragma: no cover
            raise RuntimeError("Malformed TranslationLayer")

    def serialize_for_translation(
        self, instance: _T_KlvmStreamable, mapping: TranslationLayerMapping[_T_KlvmStreamable, _T_TLKlvmStreamable]
    ) -> _T_TLKlvmStreamable:
        if mapping is None:
            return instance
        else:
            return mapping.serialize_function(instance)

    def deserialize_from_translation(
        self, instance: _T_TLKlvmStreamable, mapping: TranslationLayerMapping[_T_KlvmStreamable, _T_TLKlvmStreamable]
    ) -> _T_KlvmStreamable:
        if mapping is None:
            return instance
        else:
            return mapping.deserialize_function(instance)
