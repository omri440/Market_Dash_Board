from pydantic import BaseModel

# נתונים שנקלטים בהרשמה
class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"   # ברירת מחדל - user רגיל

# נתונים שנקלטים בהתחברות
class UserLogin(BaseModel):
    username: str
    password: str

# נתונים שיוחזרו אחרי התחברות
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
