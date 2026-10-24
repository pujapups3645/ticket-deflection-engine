import json
import pytest
from src.chunker import chunk_text
from src.retriever import retrieve_context_node
from src.reasoner import confidence_gate_node
from src.pipeline import process_support_ticket


# Test 1: Verify token chunker respects 512 limit
def test_chunker_token_limit():
    large_text = "Oracle Database troubleshooting procedure. " * 50
    chunks = chunk_text(large_text, chunk_size=512, overlap_percentage=0.10)
    
    assert len(chunks) > 0
    for chunk in chunks:
        # Every chunk must be <= 512 tokens
        assert chunk["token_count"] <= 512


# Test 2: Verify retrieval returns relevant documentation
def test_retrieval_finds_relevant_chunk():
    query = "Oracle Error 505 listener down"
    results = retrieve_context_node(user_query=query, top_k=1)
    
    assert len(results) == 1
    assert "lsnrctl status" in results[0]


# Test 3: Verify Confidence Gate escalates when score < 80%
def test_confidence_gate_escalates_low_confidence():
    low_confidence_payload = json.dumps({
        "confidence_score": 62,
        "resolution": "Uncertain steps."
    })
    
    result = confidence_gate_node(low_confidence_payload)
    assert result["status"] == "ESCALATED"
    assert "MS Teams Adaptive Card" in result["action"]


# Test 4: Verify Confidence Gate approves when score >= 80%
def test_confidence_gate_passes_high_confidence():
    high_confidence_payload = json.dumps({
        "confidence_score": 95,
        "resolution": "Definitive fix verified."
    })
    
    result = confidence_gate_node(high_confidence_payload)
    assert result["status"] == "SUCCESS"
    assert result["resolution"] == "Definitive fix verified."


# Test 5: Verify End-to-End Pipeline handles empty tickets defensively
def test_pipeline_empty_ticket():
    result = process_support_ticket("")
    assert result["status"] == "ERROR"