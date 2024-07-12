from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from chik.types.blockchain_format.sized_bytes import bytes32
from chik.util.ints import uint32
from chik.util.streamable import Streamable, streamable
from chik.wallet.notification_store import Notification
from chik.wallet.signer_protocol import SignedTransaction, SigningInstructions, SigningResponse, Spend


@streamable
@dataclass(frozen=True)
class GetNotifications(Streamable):
    ids: Optional[List[bytes32]] = None
    start: Optional[uint32] = None
    end: Optional[uint32] = None


@streamable
@dataclass(frozen=True)
class GetNotificationsResponse(Streamable):
    notifications: List[Notification]


@streamable
@dataclass(frozen=True)
class GatherSigningInfo(Streamable):
    spends: List[Spend]


@streamable
@dataclass(frozen=True)
class GatherSigningInfoResponse(Streamable):
    signing_instructions: SigningInstructions


@streamable
@dataclass(frozen=True)
class ApplySignatures(Streamable):
    spends: List[Spend]
    signing_responses: List[SigningResponse]


@streamable
@dataclass(frozen=True)
class ApplySignaturesResponse(Streamable):
    signed_transactions: List[SignedTransaction]


@streamable
@dataclass(frozen=True)
class SubmitTransactions(Streamable):
    signed_transactions: List[SignedTransaction]


@streamable
@dataclass(frozen=True)
class SubmitTransactionsResponse(Streamable):
    mempool_ids: List[bytes32]
