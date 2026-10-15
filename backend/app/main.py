from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.routes import router
from backend.app.db.database import DatabaseManager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[*] Starting FreightTiger Watchdog Engine...")
    db = DatabaseManager.get_instance()
    db.initialize()
    print("[+] Engine ready.")
    yield

app = FastAPI(
    title="FreightTiger Shipping Cost Watchdog API",
    description="Intelligent logistics cost watchdog with grounded RAG reasoning and zero-hallucination guardrails",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for local Vite React dev server and production deployments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def root():
    return {
        "service": "FreightTiger Shipping Cost Watchdog API",
        "status": "online",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
