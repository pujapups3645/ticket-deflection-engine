import json
import os
import requests
from typing import Dict, List, Optional

SYSTEM_PROMPT = """
You are an enterprise IT resolution engine. Use the provided context to answer the user ticket.
Provide a "confidence_score" between 0 and 100 based on how well the context directly covers the question.
Output MUST be valid JSON matching this exact structure:
{
    "confidence_score": 85,
    "resolution": "Step-by-step resolution text here."
}
"""

def build_prompt_payload(user_query: str, retrieved_chunks: List[str]) -> str:
    """
    Constructs the prompt combining context with the user's issue.
    """
    context_text = "\n\n".join(f"Context Chunk {i+1}:\n{chunk}" for i, chunk in enumerate(retrieved_chunks))
    
    return f"""
System: {SYSTEM_PROMPT}

Retrieved Documentation:
{context_text}

User Issue:
{user_query}
"""


def simulate_gpt4o_call(user_query: str, retrieved_chunks: List[str]) -> str:
    """
    Simulates GPT-4o output with strict temperature (0.1) and JSON formatting.
    (Allows full local execution for $0 without requiring a paid Azure OpenAI key).
    """
    # If we have relevant context, generate high confidence resolution
    if retrieved_chunks and "oracle" in user_query.lower():
        simulated_response = {
            "confidence_score": 92,
            "resolution": "1. Run 'lsnrctl status' as the oracle user.\n2. Verify $ORACLE_HOME/network/admin/listener.ora.\n3. Verify port 1521 is open and restart using 'lsnrctl start'."
        }
    else:
        # If context is weak or query is unknown, model returns low confidence
        simulated_response = {
            "confidence_score": 45,
            "resolution": "Insufficient documentation available to guarantee resolution."
        }
        
    return json.dumps(simulated_response)


def confidence_gate_node(llm_output_string: str, webhook_url: Optional[str] = None) -> Dict[str, any]:
    """
    Parses the structured LLM payload and determines if the resolution 
    meets the 80% quality bar or requires escalation to an L1 engineer.
    """
    try:
        data = json.loads(llm_output_string)
    except json.JSONDecodeError:
        data = {"confidence_score": 0, "resolution": "Formatting error detected in LLM response."}
        
    score = data.get("confidence_score", 0)
    resolution = data.get("resolution", "")
    
    # 1. QUALITY BAR MET: Direct resolution
    if score >= 80:
        return {
            "status": "SUCCESS",
            "confidence_score": score,
            "resolution": resolution,
            "action": "Delivered directly to user."
        }
        
    # 2. ESCALATION TRIGGER (<80%): Fire Webhook to Azure Logic App / Teams
    target_url = webhook_url or os.getenv("LOGIC_APP_WEBHOOK_URL", "https://mock-logicapp.azurewebsites.net/webhook")
    
    escalation_payload = {
        "alert_type": "Low-Confidence AI Output",
        "confidence_score": score,
        "suggested_resolution": resolution
    }
    
    try:
        # Fire-and-forget escalation with short 5s timeout
        requests.post(target_url, json=escalation_payload, timeout=5)
    except requests.RequestException:
        pass  # In production, handled by Azure Monitor / Application Insights logging
        
    return {
        "status": "ESCALATED",
        "confidence_score": score,
        "action": "Ticket routed to L1 support queue via MS Teams Adaptive Card."
    }


# Test both branches of the Confidence Gate locally
if __name__ == "__main__":
    print("=== TEST CASE 1: High Confidence Query (>= 80%) ===")
    good_llm_json = json.dumps({
        "confidence_score": 90,
        "resolution": "Run lsnrctl start on port 1521 to resolve ORA-12541."
    })
    result_1 = confidence_gate_node(good_llm_json)
    print(f"Status: {result_1['status']} (Score: {result_1['confidence_score']}%)")
    print(f"Action: {result_1['action']}\n")

    print("=== TEST CASE 2: Low Confidence Query (< 80%) ===")
    bad_llm_json = json.dumps({
        "confidence_score": 55,
        "resolution": "Try rebooting the entire server."
    })
    result_2 = confidence_gate_node(bad_llm_json)
    print(f"Status: {result_2['status']} (Score: {result_2['confidence_score']}%)")
    print(f"Action: {result_2['action']}")