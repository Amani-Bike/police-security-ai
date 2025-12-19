import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from fastapi.responses import FileResponse, Response
from backend.database.db_setup import create_tables
from backend.routes import user_routes, police_routes, emergency_routes, chat_routes, auth_routes
from backend.routes.chat_history_routes import router as chat_history_router
from backend.routes.admin_routes import router as admin_router

app = FastAPI(title="Police Security AI")

# ===== Initialize Database =====
create_tables()
print("Database tables created successfully!")

# ===== CORS Configuration =====
# Allow all origins in development, restrict in production
origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Include API Routes =====
app.include_router(auth_routes.router, prefix="/auth")
app.include_router(user_routes.router, prefix="/users")  # Changed prefix to avoid conflict
app.include_router(police_routes.router, prefix="/police")
app.include_router(emergency_routes.router, prefix="/emergency")
app.include_router(chat_routes.router, prefix="/chat")
app.include_router(chat_history_router, prefix="/chat-history")
app.include_router(admin_router, prefix="/admin")

# ===== Serve Frontend Files =====
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Serve civilian frontend
app.mount("/civilian", StaticFiles(directory=os.path.join(FRONTEND_DIR, "civilian"), html=True), name="civilian_frontend")

# Serve police frontend
app.mount("/police", StaticFiles(directory=os.path.join(FRONTEND_DIR, "police"), html=True), name="police_frontend")

# Serve root redirect to landing page - this should be defined BEFORE mounting static files
@app.get("/")
async def read_root():
    return FileResponse(os.path.join(FRONTEND_DIR, "landing.html"))

# Serve static files from frontend root (for favicon, assets, etc.)
# This should come AFTER all specific routes are defined
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")

# Favicon route
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    favicon_path = os.path.join(FRONTEND_DIR, "favicon.ico.txt")  # Original file was favicon.ico.txt
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    # Return a simple response if favicon doesn't exist
    return Response(status_code=204)  # No content

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=port,
        reload=False 
    )

