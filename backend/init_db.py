from backend.db import engine, Base

# חשוב: יבוא של כל המודלים כדי שיירשמו ל־Base.metadata
from backend.models.user import User
from backend.models.broker_account import BrokerAccount
from backend.models.portfolio import Portfolio
from backend.models.positions_history import PositionHistory
from backend.models.account_summary import AccountSummary
from backend.models.trade import Trade
# אם יש Journal וכו'—ייבא גם אותם

def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ DB schema created/updated")

if __name__ == "__main__":
    init_db()
