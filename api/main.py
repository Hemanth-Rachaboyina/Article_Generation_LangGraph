from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
from backend.services.langgraph_services import run_workflow

app = FastAPI(
    title="Article Writer API",
    description="AI-powered article writing and improvement API using LangGraph",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class ArticleRequest(BaseModel):
    user_query: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_query": "Write a comprehensive article on the benefits of renewable energy."
            }
        }

class ArticleResponse(BaseModel):
    success: bool
    best_article: str
    best_score: float
    iterations: int
    final_grade: float
    justification: str
    message: Optional[str] = None

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Article Writer API is running",
        "status": "healthy",
        "endpoints": {
            "health": "/health",
            "generate_article": "/api/generate-article",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "article-writer-api"}

# Main article generation endpoint
@app.post("/api/generate-article", response_model=ArticleResponse)
async def generate_article(request: ArticleRequest):
    """
    Generate and iteratively improve an article based on the user query.
    
    The system will:
    1. Write an initial article
    2. Grade it against editorial standards
    3. Suggest improvements if score < 8
    4. Apply improvements and re-grade
    5. Repeat up to 3 iterations or until score >= 8
    
    Returns the best article produced during the process.
    """
    try:
        if not request.user_query or request.user_query.strip() == "":
            raise HTTPException(status_code=400, detail="user_query cannot be empty")
        
        # Run the LangGraph workflow
        result_state = run_workflow(request.user_query)
        
        return ArticleResponse(
            success=True,
            best_article=result_state["best_article"],
            best_score=result_state["best_score"],
            iterations=result_state["iterations"],
            final_grade=result_state["grade"],
            justification=result_state["justification"],
            message="Article generated successfully"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating article: {str(e)}"
        )

# Additional endpoint to get article status/info
@app.get("/api/info")
async def get_api_info():
    return {
        "service": "Article Writer API",
        "features": [
            "AI-powered article generation",
            "Iterative improvement with editorial review",
            "Quality grading system",
            "Best article tracking across iterations"
        ],
        "max_iterations": 3,
        "target_score": 8.0
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Enable auto-reload during development
    )