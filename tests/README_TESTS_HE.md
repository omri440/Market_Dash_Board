# 🧪 מדריך הרצת טסטים - Trading Dashboard

## התקנת תלויות לטסטים

```bash
pip install pytest pytest-asyncio pytest-mock httpx
```

---

## הרצת כל הטסטים

```bash
# הרצת כל הטסטים
pytest

# הרצה עם פירוט מלא
pytest -v

# הרצה עם coverage (כיסוי קוד)
pip install pytest-cov
pytest --cov=backend --cov-report=html
```

---

## הרצת טסטים ספציפיים

### 1. טסטים לניהול הגדרות (Config)
```bash
pytest tests/test_config.py -v
```

**מה זה בודק:**
- ✅ טעינת הגדרות מקובץ `.env`
- ✅ ערכי ברירת מחדל
- ✅ Singleton pattern (instance אחד בלבד)

---

### 2. טסטים לאימות (Authentication)
```bash
pytest tests/test_auth.py -v
```

**מה זה בודק:**
- ✅ יצירת JWT tokens
- ✅ אימות tokens תקינים
- ✅ דחיית tokens לא תקינים
- ✅ דחיית tokens שפג תוקפם
- ✅ `get_current_user` dependency

---

### 3. טסטים למנהל חיבורים IBKR
```bash
pytest tests/test_ibkr_connection_manager.py -v
```

**מה זה בודק:**
- ✅ יצירת חיבור חדש
- ✅ שימוש חוזר בחיבור קיים
- ✅ ניתוק חיבור בודד
- ✅ ניתוק כל החיבורים
- ✅ בדיקת סטטוס חיבור

---

### 4. טסטים ל-Broker Endpoints
```bash
pytest tests/test_broker_endpoints.py -v
```

**מה זה בודק:**
- ✅ חיבור לברוקר (`POST /api/broker/connect`)
- ✅ סנכרון נתונים (`POST /api/broker/sync/{id}`)
- ✅ רשימת חשבונות (`GET /api/broker/accounts`)
- ✅ ניתוק חשבון (`DELETE /api/broker/disconnect/{id}`)
- ✅ סטטוס חיבור (`GET /api/broker/status/{id}`)

**⚠️ הערה:** טסטים אלו דורשים setup מורכב יותר עם DB fixtures

---

### 5. טסטים לסנכרון IBKR
```bash
pytest tests/test_ibkr_sync.py -v
```

**מה זה בודק:**
- ✅ `upsert_portfolio` - עדכון פוזיציות
- ✅ `upsert_account_summary` - עדכון סיכום חשבון
- ✅ `upsert_trades` - הוספת עסקאות (ללא כפילויות)
- ✅ `sync_broker_data` - תהליך הסנכרון המלא
- ✅ טיפול בשגיאות

---

## הרצת טסטים אסינכרוניים בלבד

```bash
pytest -k "asyncio" -v
```

---

## דילוג על טסטים איטיים

```bash
pytest -m "not slow"
```

---

## הצגת print statements בטסטים

```bash
pytest -s
```

---

## עצירה אחרי כשל ראשון

```bash
pytest -x
```

---

## 🎯 טסטים שצריך להוסיף בעתיד

### Integration Tests (דורשים DB אמיתי)
```python
# tests/integration/test_broker_flow.py
def test_full_broker_connection_flow():
    """Test: Register → Login → Connect Broker → Sync → Get Portfolio"""
    pass

def test_multiple_users_isolated_data():
    """Test that user A can't see user B's data"""
    pass
```

### End-to-End Tests
```python
# tests/e2e/test_frontend_backend.py
def test_login_from_angular_to_backend():
    """Test full flow from Angular UI to backend API"""
    pass
```

---

## 🐛 ניפוי באגים בטסטים

### הצגת traceback מלא
```bash
pytest --tb=long
```

### הרצה עם debugger
```bash
pytest --pdb
```

### רק טסט אחד ספציפי
```bash
pytest tests/test_auth.py::test_create_access_token -v
```

---

## 📊 Coverage Report (דוח כיסוי קוד)

```bash
# יצירת דוח HTML
pytest --cov=backend --cov-report=html

# פתיחת הדוח בדפדפן
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
```

**מטרה:** לפחות 80% coverage על הקוד שכתבנו

---

## ⚙️ הגדרת pytest.ini

צור קובץ `pytest.ini` בשורש הפרויקט:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto

# Markers
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests

# Output
addopts =
    -v
    --strict-markers
    --tb=short
    --disable-warnings
```

---

## 🚨 בעיות נפוצות ופתרונות

### בעיה: Import errors
```bash
# פתרון: הוסף את הנתיב לPYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}"
pytest
```

### בעיה: Async tests don't run
```bash
# פתרון: התקן pytest-asyncio
pip install pytest-asyncio
```

### בעיה: Database connection errors
```bash
# פתרון: השתמש ב-fixtures עם in-memory SQLite
# ראה examples בקוד
```

---

## 📝 כתיבת טסטים חדשים - Best Practices

### 1. שמות תיאוריים
```python
# ✅ טוב
def test_user_cannot_access_other_user_portfolio():
    pass

# ❌ רע
def test_portfolio():
    pass
```

### 2. Arrange-Act-Assert
```python
def test_create_token():
    # Arrange
    data = {"sub": "user"}

    # Act
    token = create_access_token(data)

    # Assert
    assert token is not None
```

### 3. Fixtures לקוד חוזר
```python
@pytest.fixture
def mock_user():
    return User(id=1, username="test")

def test_something(mock_user):
    assert mock_user.id == 1
```

---

## 🎓 למידה נוספת

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
