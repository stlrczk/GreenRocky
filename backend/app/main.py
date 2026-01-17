from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.services.tender_service import TenderService
from app.api.routes import tenders, ranking, feedback

# Initialize FastAPI app
app = FastAPI(
    title="Tender Matching API",
    description="AI-powered tender matching system using OpenAI embeddings",
    version="1.0.0"
)

# Configure CORS
origins = settings.cors_origins.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
tender_service = TenderService(settings.tenders_file)

# Load tenders into memory at startup
@app.on_event("startup")
async def startup_event():
    """Load tenders data into memory on startup."""
    tender_service.load_tenders()
    print(f"Loaded {tender_service.get_tenders_count()} tenders into memory")

# Include routers
app.include_router(tenders.router, prefix="/api", tags=["tenders"])
app.include_router(ranking.router, prefix="/api", tags=["ranking"])
app.include_router(feedback.router, prefix="/api", tags=["feedback"])

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Tender Matching API",
        "status": "running",
        "tenders_count": tender_service.get_tenders_count()
    }
