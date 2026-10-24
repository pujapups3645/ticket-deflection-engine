from typing import List, Dict, Optional

# Knowledge Base simulating our unified Azure AI Search index
# (Contains technical manuals and ServiceNow tickets)
KNOWLEDGE_BASE = [
    {
        "id": "KB-101",
        "title": "Oracle Listener Connection Guide",
        "content": "Resolution for Error 505 / ORA-12541: Run 'lsnrctl status' as oracle OS user. Verify listener.ora file in $ORACLE_HOME/network/admin. Ensure PORT 1521 is accepting connections. Restart listener using 'lsnrctl stop' then 'lsnrctl start'."
    },
    {
        "id": "KB-102",
        "title": "PostgreSQL Connection Pool Exhaustion",
        "content": "Resolution for Error 503 / Max Client Connections: Check pg_stat_activity to find idle connections. Terminate leaked connections using pg_terminate_backend(pid). Increase max_connections in postgresql.conf and reload configuration."
    },
    {
        "id": "KB-103",
        "title": "ServiceNow Vancouver MID Server Outage",
        "content": "Resolution for MID Server timeout: Check Windows service ServiceNow MID Server state. If stopped, restart service and check agent/logs/wrapper.log for authentication failures."
    }
]


def retrieve_context_node(
    user_query: str, 
    knowledge_base: Optional[List[Dict]] = None,
    top_k: int = 2
) -> List[str]:
    """
    Executes a Hybrid search query against the unified search index.
    Matches technical keywords and conceptual relevance, returning top_k pristine chunks.
    """
    if knowledge_base is None:
        knowledge_base = KNOWLEDGE_BASE

    query_tokens = set(user_query.lower().split())
    ranked_results = []

    for doc in knowledge_base:
        # Score the document based on technical keyword hits (simulating BM25 + Semantic scoring)
        content_tokens = set(doc["content"].lower().split())
        title_tokens = set(doc["title"].lower().split())
        
        # Title hits get 2x weight, body hits get 1x
        score = (len(query_tokens & title_tokens) * 2) + len(query_tokens & content_tokens)
        
        if score > 0:
            ranked_results.append((score, doc["content"]))

    # Sort descending by relevance score (highest score first)
    ranked_results.sort(key=lambda x: x[0], reverse=True)

    # Return only the top_k clean text chunks
    return [content for _, content in ranked_results[:top_k]]


# Test the clean retrieval node locally
if __name__ == "__main__":
    print("Testing Unified Context Retrieval Node...")
    
    test_ticket = "User reporting Error 505 with Oracle database listener not responding"
    
    retrieved_chunks = retrieve_context_node(user_query=test_ticket, top_k=1)
    
    print(f"\nIncoming Ticket: '{test_ticket}'")
    print(f"Top Chunks Retrieved: {len(retrieved_chunks)}\n")
    
    for i, chunk in enumerate(retrieved_chunks, 1):
        print(f"--- Chunk #{i} ---")
        print(f"{chunk}\n")