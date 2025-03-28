from __future__ import annotations

import contextlib
from collections.abc import AsyncIterator
from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING, Optional, cast, final

from chik.data_layer.singleton_record import SingletonRecord
from chik.types.blockchain_format.coin import Coin
from chik.util.action_scope import ActionScope
from chik.util.streamable import Streamable, streamable
from chik.wallet.signer_protocol import SigningResponse
from chik.wallet.transaction_record import TransactionRecord
from chik.wallet.util.tx_config import TXConfig
from chik.wallet.wallet_spend_bundle import WalletSpendBundle

if TYPE_CHECKING:
    # Avoid a circular import here
    from chik.wallet.wallet_state_manager import WalletStateManager


@streamable
@dataclass(frozen=True)
class _StreamableWalletSideEffects(Streamable):
    transactions: list[TransactionRecord]
    signing_responses: list[SigningResponse]
    extra_spends: list[WalletSpendBundle]
    selected_coins: list[Coin]
    singleton_records: list[SingletonRecord]


@dataclass
class WalletSideEffects:
    transactions: list[TransactionRecord] = field(default_factory=list)
    signing_responses: list[SigningResponse] = field(default_factory=list)
    extra_spends: list[WalletSpendBundle] = field(default_factory=list)
    selected_coins: list[Coin] = field(default_factory=list)
    singleton_records: list[SingletonRecord] = field(default_factory=list)

    def __bytes__(self) -> bytes:
        return bytes(_StreamableWalletSideEffects(**self.__dict__))

    @classmethod
    def from_bytes(cls, blob: bytes) -> WalletSideEffects:
        return cls(**_StreamableWalletSideEffects.from_bytes(blob).__dict__)


@final
@dataclass(frozen=True)
class WalletActionConfig:
    push: bool
    merge_spends: bool
    sign: Optional[bool]
    additional_signing_responses: list[SigningResponse]
    extra_spends: list[WalletSpendBundle]
    tx_config: TXConfig

    def adjust_for_side_effects(self, side_effects: WalletSideEffects) -> WalletActionConfig:
        return replace(
            self,
            tx_config=replace(
                self.tx_config,
                excluded_coin_ids=[*self.tx_config.excluded_coin_ids, *(c.name() for c in side_effects.selected_coins)],
            ),
        )


WalletActionScope = ActionScope[WalletSideEffects, WalletActionConfig]


@contextlib.asynccontextmanager
async def new_wallet_action_scope(
    wallet_state_manager: WalletStateManager,
    tx_config: TXConfig,
    push: bool = False,
    merge_spends: bool = True,
    sign: Optional[bool] = None,
    additional_signing_responses: list[SigningResponse] = [],
    extra_spends: list[WalletSpendBundle] = [],
) -> AsyncIterator[WalletActionScope]:
    async with ActionScope.new_scope(
        WalletSideEffects,
        WalletActionConfig(push, merge_spends, sign, additional_signing_responses, extra_spends, tx_config),
    ) as self:
        self = cast(WalletActionScope, self)
        async with self.use() as interface:
            interface.side_effects.signing_responses = additional_signing_responses.copy()
            interface.side_effects.extra_spends = extra_spends.copy()

        yield self

    self.side_effects.transactions = await wallet_state_manager.add_pending_transactions(
        self.side_effects.transactions,
        push=push,
        merge_spends=merge_spends,
        sign=sign,
        additional_signing_responses=self.side_effects.signing_responses,
        extra_spends=self.side_effects.extra_spends,
        singleton_records=self.side_effects.singleton_records,
    )
