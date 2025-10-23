# main.py - FastAPI Setup with CORS

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import auth, portfolio, scanner, journal, analytics  # Your auth router
from backend.routers import broker


app = FastAPI(
    title="Market Dashboard API",
    version="1.0.0",
    description="Portfolio tracking API"
)

# ============================================
# CORS Configuration for Angular
# ============================================
origins = [
    "http://localhost:4200",  # Angular dev server
    "http://localhost:3000",  # Fallback
    "https://yourdomain.com",  # Production domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers (including Authorization)
)

# ============================================
# Include Routers
# ============================================
app.include_router(auth.router)
app.include_router(broker.router)
# app.include_router(portfolio.router)
# app.include_router(journal.router, prefix="/api")
# app.include_router(scanner.router, prefix="/api")
# app.include_router(analytics.router, prefix="/api")

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)