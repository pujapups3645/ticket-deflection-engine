import tiktoken
from typing import List, Dict

# OpenAI's tokenizer used for GPT-4o and text-embedding-3-large
DEFAULT_ENCODING = "cl100k_base"

def chunk_text(
    text: str, 
    chunk_size: int = 512, 
    overlap_percentage: float = 0.10,
    encoding_name: str = DEFAULT_ENCODING
) -> List[Dict[str, any]]:
    """
    Splits text into chunks of exact token sizes with a sliding window overlap.
    Preserves multi-line stack traces and technical instructions.
    """
    if not text.strip():
        return []

    tokenizer = tiktoken.get_encoding(encoding_name)
    tokens = tokenizer.encode(text)
    
    total_tokens = len(tokens)
    overlap_tokens = int(chunk_size * overlap_percentage)  # 10% of 512 = 51 tokens
    step_size = chunk_size - overlap_tokens                # Step forward by 461 tokens

    chunks = []
    chunk_index = 0

    for i in range(0, total_tokens, step_size):
        chunk_tokens = tokens[i : i + chunk_size]
        chunk_text_decoded = tokenizer.decode(chunk_tokens)
        
        chunks.append({
            "chunk_id": chunk_index,
            "token_count": len(chunk_tokens),
            "content": chunk_text_decoded
        })
        chunk_index += 1
        
        # Stop if we have consumed all tokens
        if i + chunk_size >= total_tokens:
            break

    return chunks


# Quick test simulation if run directly
if __name__ == "__main__":
    sample_manual = """
    Oracle Database 19c Enterprise Edition - Maintenance Guide
    Section 4.2: Handling ORA-12541 TNS:no listener error.
    When a client application attempts to establish a connection to Oracle 19c on port 1521,
    the listener service must be in a RUNNING state. If the connection fails with Error 505 / ORA-12541,
    follow these diagnostic steps:
    1. Verify listener status using: 'lsnrctl status' from the oracle OS user.
    2. Check listener.ora file located in $ORACLE_HOME/network/admin.
    3. Ensure the HOST parameter matches the server IP or hostname.
    4. Restart listener using 'lsnrctl stop' followed by 'lsnrctl start'.
    """ * 15  # Multiply text to simulate a large document

    print("Running token chunker test...")
    results = chunk_text(sample_manual, chunk_size=512, overlap_percentage=0.10)
    
    print(f"Total chunks created: {len(results)}")
    for c in results:
        print(f"Chunk #{c['chunk_id']} | Tokens: {c['token_count']}")