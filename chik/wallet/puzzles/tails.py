from __future__ import annotations

from typing import Any, Optional

from chik_rs import Coin

from chik.types.blockchain_format.program import Program
from chik.types.blockchain_format.sized_bytes import bytes32
from chik.util.byte_types import hexstr_to_bytes
from chik.util.ints import uint64
from chik.wallet.cat_wallet.cat_info import CATInfo
from chik.wallet.cat_wallet.cat_utils import (
    CAT_MOD,
    SpendableCAT,
    construct_cat_puzzle,
    unsigned_spend_bundle_for_spendable_cats,
)
from chik.wallet.cat_wallet.lineage_store import CATLineageStore
from chik.wallet.dao_wallet.dao_utils import create_cat_launcher_for_singleton_id
from chik.wallet.lineage_proof import LineageProof
from chik.wallet.payment import Payment
from chik.wallet.puzzles.load_klvm import load_klvm_maybe_recompile
from chik.wallet.transaction_record import TransactionRecord
from chik.wallet.wallet_action_scope import WalletActionScope
from chik.wallet.wallet_spend_bundle import WalletSpendBundle

GENESIS_BY_ID_MOD = load_klvm_maybe_recompile(
    "genesis_by_coin_id.clsp", package_or_requirement="chik.wallet.cat_wallet.puzzles"
)
GENESIS_BY_PUZHASH_MOD = load_klvm_maybe_recompile(
    "genesis_by_puzzle_hash.clsp", package_or_requirement="chik.wallet.cat_wallet.puzzles"
)
EVERYTHING_WITH_SIG_MOD = load_klvm_maybe_recompile(
    "everything_with_signature.clsp", package_or_requirement="chik.wallet.cat_wallet.puzzles"
)
DELEGATED_LIMITATIONS_MOD = load_klvm_maybe_recompile(
    "delegated_tail.clsp", package_or_requirement="chik.wallet.cat_wallet.puzzles"
)
GENESIS_BY_ID_OR_SINGLETON_MOD = load_klvm_maybe_recompile(
    "genesis_by_coin_id_or_singleton.clsp", package_or_requirement="chik.wallet.cat_wallet.puzzles"
)


class LimitationsProgram:
    @staticmethod
    def match(uncurried_mod: Program, curried_args: Program) -> tuple[bool, list[Program]]:
        raise NotImplementedError("Need to implement 'match' on limitations programs")

    @staticmethod
    def construct(args: list[Program]) -> Program:
        raise NotImplementedError("Need to implement 'construct' on limitations programs")

    @staticmethod
    def solve(args: list[Program], solution_dict: dict) -> Program:
        raise NotImplementedError("Need to implement 'solve' on limitations programs")

    @classmethod
    async def generate_issuance_bundle(
        cls, wallet, cat_tail_info: dict, amount: uint64, action_scope: WalletActionScope
    ) -> WalletSpendBundle:
        raise NotImplementedError("Need to implement 'generate_issuance_bundle' on limitations programs")


class GenesisById(LimitationsProgram):
    """
    This TAIL allows for coins to be issued only by a specific "genesis" coin ID.
    There can therefore only be one issuance. There is no minting or melting allowed.
    """

    @staticmethod
    def match(uncurried_mod: Program, curried_args: Program) -> tuple[bool, list[Program]]:
        if uncurried_mod == GENESIS_BY_ID_MOD:
            genesis_id = curried_args.first()
            return True, [genesis_id]
        else:
            return False, []

    @staticmethod
    def construct(args: list[Program]) -> Program:
        return GENESIS_BY_ID_MOD.curry(args[0])

    @staticmethod
    def solve(args: list[Program], solution_dict: dict) -> Program:
        return Program.to([])

    @classmethod
    async def generate_issuance_bundle(
        cls,
        wallet,
        _: dict,
        amount: uint64,
        action_scope: WalletActionScope,
        fee: uint64 = uint64(0),
    ) -> WalletSpendBundle:
        coins = await wallet.standard_wallet.select_coins(amount + fee, action_scope)

        origin = coins.copy().pop()
        origin_id = origin.name()

        cat_inner: Program = await wallet.standard_wallet.get_puzzle(
            new=not action_scope.config.tx_config.reuse_puzhash
        )
        tail: Program = cls.construct([Program.to(origin_id)])

        wallet.lineage_store = await CATLineageStore.create(
            wallet.wallet_state_manager.db_wrapper, tail.get_tree_hash().hex()
        )
        await wallet.add_lineage(origin_id, LineageProof())

        minted_cat_puzzle_hash: bytes32 = construct_cat_puzzle(CAT_MOD, tail.get_tree_hash(), cat_inner).get_tree_hash()

        async with wallet.wallet_state_manager.new_action_scope(
            action_scope.config.tx_config, push=False
        ) as inner_action_scope:
            await wallet.standard_wallet.generate_signed_transaction(
                amount, minted_cat_puzzle_hash, inner_action_scope, fee, coins, origin_id=origin_id
            )

        async with action_scope.use() as interface:
            interface.side_effects.transactions = inner_action_scope.side_effects.transactions

        inner_tree_hash = cat_inner.get_tree_hash()
        inner_solution = wallet.standard_wallet.add_condition_to_solution(
            Program.to([51, 0, -113, tail, []]),
            wallet.standard_wallet.make_solution(primaries=[Payment(inner_tree_hash, amount, [inner_tree_hash])]),
        )
        eve_spend = unsigned_spend_bundle_for_spendable_cats(
            CAT_MOD,
            [
                SpendableCAT(
                    next(
                        filter(
                            lambda a: a.amount == amount,
                            [add for tx in inner_action_scope.side_effects.transactions for add in tx.additions],
                        )
                    ),
                    tail.get_tree_hash(),
                    cat_inner,
                    inner_solution,
                    limitations_program_reveal=tail,
                )
            ],
        )

        if wallet.cat_info.my_tail is None:
            await wallet.save_info(CATInfo(tail.get_tree_hash(), tail))

        return eve_spend


class GenesisByPuzhash(LimitationsProgram):
    """
    This TAIL allows for issuance of a certain coin only by a specific puzzle hash.
    There is no minting or melting allowed.
    """

    @staticmethod
    def match(uncurried_mod: Program, curried_args: Program) -> tuple[bool, list[Program]]:
        if uncurried_mod == GENESIS_BY_PUZHASH_MOD:
            genesis_puzhash = curried_args.first()
            return True, [genesis_puzhash]
        else:
            return False, []

    @staticmethod
    def construct(args: list[Program]) -> Program:
        return GENESIS_BY_PUZHASH_MOD.curry(args[0])

    @staticmethod
    def solve(args: list[Program], solution_dict: dict) -> Program:
        pid = hexstr_to_bytes(solution_dict["parent_coin_info"])
        return Program.to([pid, solution_dict["amount"]])


class EverythingWithSig(LimitationsProgram):
    """
    This TAIL allows for issuance, minting, and melting as long as you provide a signature with the spend.
    """

    @staticmethod
    def match(uncurried_mod: Program, curried_args: Program) -> tuple[bool, list[Program]]:
        if uncurried_mod == EVERYTHING_WITH_SIG_MOD:
            pubkey = curried_args.first()
            return True, [pubkey]
        else:
            return False, []

    @staticmethod
    def construct(args: list[Program]) -> Program:
        return EVERYTHING_WITH_SIG_MOD.curry(args[0])

    @staticmethod
    def solve(args: list[Program], solution_dict: dict) -> Program:
        return Program.to([])


class DelegatedLimitations(LimitationsProgram):
    """
    This TAIL allows for another TAIL to be used, as long as a signature of that TAIL's puzzlehash is included.
    """

    @staticmethod
    def match(uncurried_mod: Program, curried_args: Program) -> tuple[bool, list[Program]]:
        if uncurried_mod == DELEGATED_LIMITATIONS_MOD:
            pubkey = curried_args.first()
            return True, [pubkey]
        else:
            return False, []

    @staticmethod
    def construct(args: list[Program]) -> Program:
        return DELEGATED_LIMITATIONS_MOD.curry(args[0])

    @staticmethod
    def solve(args: list[Program], solution_dict: dict) -> Program:
        signed_program = ALL_LIMITATIONS_PROGRAMS[solution_dict["signed_program"]["identifier"]]
        inner_program_args = [Program.fromhex(item) for item in solution_dict["signed_program"]["args"]]
        inner_solution_dict = solution_dict["program_arguments"]
        return Program.to(
            [
                signed_program.construct(inner_program_args),
                signed_program.solve(inner_program_args, inner_solution_dict),
            ]
        )


class GenesisByIdOrSingleton(LimitationsProgram):
    """
    This TAIL allows for another TAIL to be used, as long as a signature of that TAIL's puzzlehash is included.
    """

    @staticmethod
    def match(uncurried_mod: Program, curried_args: Program) -> tuple[bool, list[Program]]:  # pragma: no cover
        if uncurried_mod == GENESIS_BY_ID_OR_SINGLETON_MOD:
            genesis_id = curried_args.first()
            return True, [genesis_id]
        else:
            return False, []

    @staticmethod
    def construct(args: list[Program]) -> Program:
        return GENESIS_BY_ID_OR_SINGLETON_MOD.curry(
            args[0],
            args[1],
        )

    @staticmethod
    def solve(args: list[Program], solution_dict: dict) -> Program:  # pragma: no cover
        pid = hexstr_to_bytes(solution_dict["parent_coin_info"])
        return Program.to([pid, solution_dict["amount"]])

    @classmethod
    async def generate_issuance_bundle(
        cls,
        wallet,
        tail_info: dict,
        amount: uint64,
        action_scope: WalletActionScope,
        fee: uint64 = uint64(0),
    ) -> WalletSpendBundle:
        if "coins" in tail_info:
            coins: list[Coin] = tail_info["coins"]
            origin_id = coins.copy().pop().name()
        else:  # pragma: no cover
            coins = await wallet.standard_wallet.select_coins(amount + fee, action_scope)
            origin = coins.copy().pop()
            origin_id = origin.name()

        cat_inner: Program = await wallet.standard_wallet.get_puzzle(
            new=not action_scope.config.tx_config.reuse_puzhash
        )
        # GENESIS_ID
        # TREASURY_SINGLETON_STRUCT  ; (SINGLETON_MOD_HASH, (LAUNCHER_ID, LAUNCHER_PUZZLE_HASH))
        launcher_puzhash = create_cat_launcher_for_singleton_id(tail_info["treasury_id"]).get_tree_hash()
        tail: Program = cls.construct(
            [
                Program.to(origin_id),
                Program.to(launcher_puzhash),
            ]
        )

        wallet.lineage_store = await CATLineageStore.create(
            wallet.wallet_state_manager.db_wrapper, tail.get_tree_hash().hex()
        )
        await wallet.add_lineage(origin_id, LineageProof())

        minted_cat_puzzle_hash: bytes32 = construct_cat_puzzle(CAT_MOD, tail.get_tree_hash(), cat_inner).get_tree_hash()

        async with wallet.wallet_state_manager.new_action_scope(
            action_scope.config.tx_config, push=False
        ) as inner_action_scope:
            await wallet.standard_wallet.generate_signed_transaction(
                amount,
                minted_cat_puzzle_hash,
                inner_action_scope,
                fee,
                coins=set(coins),
                origin_id=origin_id,
            )

        async with action_scope.use() as interface:
            interface.side_effects.transactions.extend(inner_action_scope.side_effects.transactions)
        tx_record: TransactionRecord = inner_action_scope.side_effects.transactions[0]
        assert tx_record.spend_bundle is not None
        payment = Payment(cat_inner.get_tree_hash(), amount)
        inner_solution = wallet.standard_wallet.add_condition_to_solution(
            Program.to([51, 0, -113, tail, []]),
            wallet.standard_wallet.make_solution(
                primaries=[payment],
            ),
        )
        eve_spend = unsigned_spend_bundle_for_spendable_cats(
            CAT_MOD,
            [
                SpendableCAT(
                    next(filter(lambda a: a.amount == amount, tx_record.additions)),
                    tail.get_tree_hash(),
                    cat_inner,
                    inner_solution,
                    limitations_program_reveal=tail,
                )
            ],
        )

        if wallet.cat_info.my_tail is None:
            await wallet.save_info(CATInfo(tail.get_tree_hash(), tail))

        return eve_spend


# This should probably be much more elegant than just a dictionary with strings as identifiers
# Right now this is small and experimental so it can stay like this
ALL_LIMITATIONS_PROGRAMS: dict[str, Any] = {
    "genesis_by_id": GenesisById,
    "genesis_by_puzhash": GenesisByPuzhash,
    "everything_with_signature": EverythingWithSig,
    "delegated_limitations": DelegatedLimitations,
    "genesis_by_id_or_singleton": GenesisByIdOrSingleton,
}


def match_limitations_program(limitations_program: Program) -> tuple[Optional[LimitationsProgram], list[Program]]:
    uncurried_mod, curried_args = limitations_program.uncurry()
    for key, lp in ALL_LIMITATIONS_PROGRAMS.items():
        matched, args = lp.match(uncurried_mod, curried_args)
        if matched:
            return lp, args
    return None, []
