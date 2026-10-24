from typing import Dict, Any
try:
    # When run as a package (e.g. pytest or FastAPI)
    from src.retriever import retrieve_context_node
    from src.reasoner import simulate_gpt4o_call, confidence_gate_node
except ModuleNotFoundError:
    # When run directly (python src/pipeline.py)
    from retriever import retrieve_context_node
    from reasoner import simulate_gpt4o_call, confidence_gate_node


def process_support_ticket(user_ticket: str) -> Dict[str, Any]:
    """
    End-to-End GenAI Orchestration Pipeline:
    1. Ingestion / Hybrid Search: Retrieves top relevant context chunks.
    2. Reasoner: Feeds context and ticket to GPT-4o with temperature 0.1.
    3. Confidence Gate: Evaluates score; either deflects ticket or escalates to Teams.
    """
    if not user_ticket.strip():
        return {
            "status": "ERROR",
            "message": "Empty ticket provided."
        }

    # Step 1: Retrieve relevant context from unified index
    retrieved_chunks = retrieve_context_node(user_query=user_ticket, top_k=2)

    # Step 2: Call GPT-4o (with structured JSON output constraint)
    raw_llm_response = simulate_gpt4o_call(
        user_query=user_ticket, 
        retrieved_chunks=retrieved_chunks
    )

    # Step 3: Enforce Confidence Gate (<80% escalates to Logic App / Teams)
    final_result = confidence_gate_node(raw_llm_response)

    return {
        "ticket": user_ticket,
        "chunks_retrieved_count": len(retrieved_chunks),
        "pipeline_result": final_result
    }


# Quick live test of the entire pipeline
if __name__ == "__main__":
    print("==================================================")
    print("TESTING END-TO-END TICKET DEFLECTION PIPELINE")
    print("==================================================\n")

    # Ticket 1: Known issue with matching documentation
    ticket_1 = "Production Oracle DB returning Error 505: listener down on port 1521"
    res_1 = process_support_ticket(ticket_1)
    
    print(f"Ticket: '{res_1['ticket']}'")
    print(f"Chunks Found: {res_1['chunks_retrieved_count']}")
    print(f"Outcome: {res_1['pipeline_result']['status']}")
    print(f"Resolution Details:\n{res_1['pipeline_result'].get('resolution', 'N/A')}\n")

    print("--------------------------------------------------\n")

    # Ticket 2: Unknown / vague issue with no documentation
    ticket_2 = "My computer screen flickers when I open Spotify"
    res_2 = process_support_ticket(ticket_2)
    
    print(f"Ticket: '{res_2['ticket']}'")
    print(f"Chunks Found: {res_2['chunks_retrieved_count']}")
    print(f"Outcome: {res_2['pipeline_result']['status']}")
    print(f"Action: {res_2['pipeline_result']['action']}")