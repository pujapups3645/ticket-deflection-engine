from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from src.pipeline import process_support_ticket

app = FastAPI(
    title="IT Ticket Deflection & Resolution RAG Service",
    description="Enterprise GenAI RAG engine with automated confidence gate escalation",
    version="1.0.0"
)

# Pydantic Request Validation Model
class TicketRequest(BaseModel):
    ticket_id: str = Field(..., example="INC-10921", description="ServiceNow Ticket ID")
    ticket_text: str = Field(..., min_length=10, example="Oracle DB Error 505 connection listener down")


# 1. Mandatory Kubernetes / Azure Health Check Endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ticket-deflection-rag",
        "version": "1.0.0"
    }


# 2. The Main Ticket Resolution Endpoint
@app.post("/api/v1/resolve-ticket")
def resolve_ticket(request: TicketRequest):
    """
    Ingests a support ticket, runs Hybrid Search + GPT-4o reasoning,
    and returns resolution or MS Teams escalation status.
    """
    try:
        pipeline_output = process_support_ticket(request.ticket_text)
        
        return {
            "ticket_id": request.ticket_id,
            "status": pipeline_output["pipeline_result"]["status"],
            "confidence_score": pipeline_output["pipeline_result"].get("confidence_score", 0),
            "details": pipeline_output["pipeline_result"].get("resolution") or pipeline_output["pipeline_result"].get("action")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Pipeline Error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)