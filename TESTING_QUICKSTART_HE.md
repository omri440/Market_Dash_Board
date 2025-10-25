# 🚀 מדריך מהיר - הרצת טסטים

## התקנה מהירה

```bash
# התקן את כל התלויות
pip install -r requirements.txt

# או התקן רק תלויות טסטים
pip install pytest pytest-asyncio pytest-mock pytest-cov httpx
```

---

## הרצה מהירה

### הרץ את כל הטסטים
```bash
pytest
```

### הרץ עם פירוט
```bash
pytest -v
```

### הרץ טסט בודד
```bash
pytest tests/test_auth.py::test_create_access_token -v
```

---

## ✅ מה הטסטים בודקים

| קובץ | מה נבדק |
|------|---------|
| `test_config.py` | טעינת הגדרות מ-.env, ערכי ברירת מחדל |
| `test_auth.py` | יצירת JWT, אימות tokens, get_current_user |
| `test_ibkr_connection_manager.py` | יצירת חיבורים, reconnection, disconnect |
| `test_broker_endpoints.py` | API endpoints (/connect, /sync, /accounts) |
| `test_ibkr_sync.py` | סנכרון נתונים מ-IBKR לDB |

---

## 🎯 פלט מצופה

כשהכל עובד אתה צריך לראות:
```
=============== test session starts ===============
collected 25 items

tests/test_config.py ....                    [ 16%]
tests/test_auth.py ........                  [ 48%]
tests/test_ibkr_connection_manager.py ...... [ 72%]
tests/test_ibkr_sync.py ......               [100%]

=============== 25 passed in 2.34s ===============
```

---

## 🐛 אם יש כשלים

### הצג פרטים מלאים
```bash
pytest --tb=long
```

### הצג prints
```bash
pytest -s
```

### עצור אחרי כשל ראשון
```bash
pytest -x
```

---

## 📊 Coverage (כיסוי קוד)

```bash
# הרץ עם coverage
pytest --cov=backend --cov-report=html

# פתח את הדוח
open htmlcov/index.html
```

---

## ⚠️ בעיות נפוצות

### Import Error
```bash
# פתרון:
export PYTHONPATH="${PYTHONPATH}:${PWD}"
pytest
```

### ModuleNotFoundError
```bash
# וודא שאתה בתיקיית הפרויקט
cd /path/to/Market_Dash_Board
pytest
```

---

## 💡 טיפים

1. **הרץ טסטים לפני commit:**
   ```bash
   pytest && git commit
   ```

2. **רק טסטים מהירים:**
   ```bash
   pytest -m "unit"
   ```

3. **דלג על טסטים איטיים:**
   ```bash
   pytest -m "not slow"
   ```

---

## 📖 מידע נוסף

ראה `tests/README_TESTS_HE.md` למדריך מפורט.
