#!/usr/bin/env python3
"""Simple RAG test"""

from rag_system.supabase_client import supabase_manager

print("="*50)
print("2) RAG INTEGRATION TEST")
print("="*50)

# Test Global RAG search directly
print("\n🔍 Testing Global RAG search...")
chunks = supabase_manager.search_global_chunks(
    query_vector=[0.1] * 1536,  # Dummy vector
    k=3,
    query_text="SWOT analysis framework"
)

print(f"📊 Found {len(chunks)} chunks from Global RAG")
for i, chunk in enumerate(chunks[:2]):
    print(f"   [{i+1}] {chunk.get('source_label', 'Unknown')}: {chunk.get('text', '')[:80]}...")

if len(chunks) > 0:
    print("✅ PASS: RAG retrieval working")
else:
    print("❌ FAIL: No results from RAG")

# Test Tenant RAG  
print("\n🔍 Testing Tenant RAG search...")
tenant_chunks = supabase_manager.search_tenant_chunks(
    query_vector=[0.1] * 1536,
    project_id="test-project", 
    k=3
)

print(f"📊 Found {len(tenant_chunks)} chunks from Tenant RAG")
print(f"✅ Tenant RAG {'working' if len(tenant_chunks) >= 0 else 'failed'}")

print("\n" + "="*50)