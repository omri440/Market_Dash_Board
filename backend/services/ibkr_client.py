import asyncio
from ib_async import IB

class IBKRClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 7497, client_id: int = 1):
        self.host = host
        self.port = port
        self.client_id = client_id
        self.ib = IB()

    async def connect(self):
        """Connect to IBKR gateway asynchronously."""
        if not self.ib.isConnected():
            await self.ib.connectAsync(self.host, self.port, self.client_id)
        return self.ib

    def disconnect(self):
        """Disconnect cleanly."""
        if self.ib.isConnected():
            self.ib.disconnect()

    async def get_positions(self):
        """Fetch all open positions."""
        return await self.ib.reqPositionsAsync()

    async def get_account_summary(self):
        """Fetch account summary (cash, equity, buying power, etc.)."""
        return await self.ib.reqAccountSummaryAsync()

    async def get_executions(self):
        """Fetch trade executions (trade book)."""
        return await self.ib.reqExecutionsAsync()
