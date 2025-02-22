from __future__ import annotations

from dataclasses import dataclass, field

from chik_rs import AugSchemeMPL, G1Element, G2Element, PrivateKey

from chik._tests.core.make_block_generator import GROUP_ORDER, int_to_public_key
from chik.simulator.block_tools import test_constants
from chik.types.coin_spend import CoinSpend
from chik.util.condition_tools import conditions_dict_for_solution, pkm_pairs_for_conditions_dict


@dataclass
class KeyTool:
    dict: dict[G1Element, int] = field(default_factory=dict)

    def add_secret_exponents(self, secret_exponents: list[int]) -> None:
        for _ in secret_exponents:
            self.dict[int_to_public_key(_)] = _ % GROUP_ORDER

    def sign(self, public_key: G1Element, message: bytes) -> G2Element:
        secret_exponent = self.dict.get(public_key)
        if not secret_exponent:
            raise ValueError(f"unknown pubkey {bytes(public_key).hex()}")
        bls_private_key = PrivateKey.from_bytes(secret_exponent.to_bytes(32, "big"))
        return AugSchemeMPL.sign(bls_private_key, message)

    def signature_for_solution(self, coin_spend: CoinSpend, additional_data: bytes) -> G2Element:
        signatures = []
        conditions_dict = conditions_dict_for_solution(
            coin_spend.puzzle_reveal, coin_spend.solution, test_constants.MAX_BLOCK_COST_KLVM
        )
        for public_key, message in pkm_pairs_for_conditions_dict(conditions_dict, coin_spend.coin, additional_data):
            signature = self.sign(public_key, message)
            signatures.append(signature)
        return AugSchemeMPL.aggregate(signatures)
