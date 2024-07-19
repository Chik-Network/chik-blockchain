from __future__ import annotations

from dataclasses import dataclass
from typing import List

import chik_rs

from chik.types.blockchain_format.reward_chain_block import RewardChainBlock
from chik.types.end_of_slot_bundle import EndOfSubSlotBundle
from chik.types.header_block import HeaderBlock
from chik.util.streamable import Streamable, streamable

SubEpochData = chik_rs.SubEpochData

# number of challenge blocks
# Average iters for challenge blocks
# |--A-R----R-------R--------R------R----R----------R-----R--R---|       Honest difficulty 1000
#           0.16

#  compute total reward chain blocks
# |----------------------------A---------------------------------|       Attackers chain 1000
#                            0.48
# total number of challenge blocks == total number of reward chain blocks


SubEpochChallengeSegment = chik_rs.SubEpochChallengeSegment
SubEpochSegments = chik_rs.SubEpochSegments
SubSlotData = chik_rs.SubSlotData


@streamable
@dataclass(frozen=True)
# this is used only for serialization to database
class RecentChainData(Streamable):
    recent_chain_data: List[HeaderBlock]


@streamable
@dataclass(frozen=True)
class ProofBlockHeader(Streamable):
    finished_sub_slots: List[EndOfSubSlotBundle]
    reward_chain_block: RewardChainBlock


@streamable
@dataclass(frozen=True)
class WeightProof(Streamable):
    sub_epochs: List[SubEpochData]
    sub_epoch_segments: List[SubEpochChallengeSegment]  # sampled sub epoch
    recent_chain_data: List[HeaderBlock]
