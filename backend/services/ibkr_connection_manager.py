import asyncio
from typing import Dict, Optional
from ib_async import IB
from backend.models.broker_account import BrokerAccount


class IBKRConnectionManager:
    def __init__(self):
        self._connections: Dict[int, IB] = {}  # broker_account_id -> IB instance
        self._locks: Dict[int, asyncio.Lock] = {}

    async def get_or_create_connection(self, broker_account: BrokerAccount) -> IB:
        """Get existing connection or create new one."""
        ba_id = broker_account.id

        if ba_id not in self._locks:
            self._locks[ba_id] = asyncio.Lock()

        async with self._locks[ba_id]:
            if ba_id in self._connections:
                ib = self._connections[ba_id]
                if ib.isConnected():
                    return ib
                else:
                    # Reconnect
                    await ib.connectAsync(
                        broker_account.conn_host or "127.0.0.1",
                        broker_account.conn_port or 7497,
                        broker_account.client_id or ba_id
                    )
                    return ib

            # Create new connection
            ib = IB()
            await ib.connectAsync(
                broker_account.conn_host or "127.0.0.1",
                broker_account.conn_port or 7497,
                broker_account.client_id or ba_id
            )
            self._connections[ba_id] = ib
            return ib

    async def disconnect(self, broker_account_id: int):
        """Disconnect specific broker account."""
        if broker_account_id in self._connections:
            ib = self._connections[broker_account_id]
            if ib.isConnected():
                ib.disconnect()
            del self._connections[broker_account_id]

    async def disconnect_all(self):
        """Disconnect all connections (on shutdown)."""
        for ib in self._connections.values():
            if ib.isConnected():
                ib.disconnect()
        self._connections.clear()


# Global singleton
connection_manager = IBKRConnectionManager()