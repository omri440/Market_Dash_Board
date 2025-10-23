from passlib.context import CryptContext

# קונטקסט הצפנה עם bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain_password: str) -> str:
    """
    מקבלת סיסמה רגילה ומחזירה hash לשמירה במסד.
    מוגנת מקריסות של bcrypt במקרה של סיסמאות ארוכות מדי.
    """
    if not plain_password:
        raise ValueError("Password cannot be empty.")

    encoded = plain_password.encode("utf-8")
    print(f"🔍 DEBUG: Original password length (bytes): {len(encoded)}")

    # אם ארוכה מדי, נחתוך
    if len(encoded) > 72:
        encoded = encoded[:72]
        plain_password = encoded.decode("utf-8", errors="ignore")
        print(f"✂️ DEBUG: Trimmed password length (bytes): {len(encoded)}")

    try:
        hashed = pwd_context.hash(plain_password)
        print(f"✅ DEBUG: Successfully hashed password of length {len(plain_password.encode('utf-8'))} bytes")
        return hashed
    except Exception as e:
        print(f"❌ DEBUG: Hash failed with password length {len(plain_password.encode('utf-8'))}")
        raise ValueError(f"Failed to hash password: {e}")



def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    בודקת אם סיסמה רגילה תואמת ל-hash ששמור במסד.
    """
    if not plain_password or not hashed_password:
        return False

    # במידה והסיסמה ארוכה מדי – נחתוך גם כאן
    if len(plain_password.encode("utf-8")) > 72:
        plain_password = plain_password[:72]

    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False

