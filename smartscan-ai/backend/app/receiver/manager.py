"""
smartscan.backend.app.receiver.manager
======================================
ReceiverManager providing mode selection (REAL_RF_REPLAY vs LIVE_RTL_SDR)
and unified hardware status tracking.
"""

from enum import Enum
from typing import Dict, Any, Optional
from app.receiver.base_receiver import BaseReceiver, ReceiverState
from app.receiver.replay_receiver import ReplayReceiver
from app.receiver.rtlsdr_receiver import RTLSDRReceiver
from app.receiver.usrp_receiver import FutureUSRPReceiver


class ReceiverMode(str, Enum):
    REAL_RF_REPLAY = "REAL_RF_REPLAY"
    LIVE_RTL_SDR   = "LIVE_RTL_SDR"
    LIVE_USRP      = "LIVE_USRP"


class ReceiverManager:
    """
    Manages active receiver instance and seamless switching between replay and live SDR modes.
    """

    def __init__(self, default_mode: ReceiverMode = ReceiverMode.REAL_RF_REPLAY):
        self.mode = default_mode
        self.active_receiver: BaseReceiver = self._create_receiver(default_mode)

    def _create_receiver(self, mode: ReceiverMode) -> BaseReceiver:
        if mode == ReceiverMode.LIVE_RTL_SDR:
            return RTLSDRReceiver()
        elif mode == ReceiverMode.LIVE_USRP:
            return FutureUSRPReceiver()
        return ReplayReceiver()

    def set_mode(self, mode: ReceiverMode) -> ReceiverState:
        if self.active_receiver:
            self.active_receiver.disconnect()
        self.mode = mode
        self.active_receiver = self._create_receiver(mode)
        return self.active_receiver.get_state()

    def get_receiver(self) -> BaseReceiver:
        return self.active_receiver

    def status(self) -> Dict[str, Any]:
        state = self.active_receiver.get_state()
        res = state.to_dict()
        res["mode"] = self.mode.value
        return res
