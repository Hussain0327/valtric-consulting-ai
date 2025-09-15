#!/usr/bin/env python3
from openai import OpenAI
import os, time

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), timeout=10)

print("="*50)
print("PRODUCTION TEST RESULTS")
print("="*50)

# Test both models with proper settings
tests = [
    ("gpt-5-mini", "What is 2+2?", "Simple math"),
    ("o4-mini", "Analyze pros and cons of remote work", "Complex analysis"),
    ("gpt-5-mini", "What is SWOT analysis?", "Framework query"),
    ("o4-mini", "Create a business strategy for market expansion", "Strategic planning")
]

results = []

for model, query, test_type in tests:
    print(f"\n📝 {test_type}: {model}")
    print(f"   Query: {query}")
    
    t = time.time()
    try:
        kwargs = {
            "model": model, 
            "input": query, 
            "max_output_tokens": 200,
            "store": False
        }
        
        if "o4" in model:
            kwargs["reasoning"] = {"effort": "low"}  # Faster reasoning
        
        response = client.responses.create(**kwargs)
        elapsed = int((time.time() - t) * 1000)
        
        output = response.output_text or ""
        
        print(f"   ✅ Response in {elapsed}ms")
        print(f"   📏 Length: {len(output)} chars")
        print(f"   💬 Preview: {output[:100]}...")
        
        # Quality check for SWOT
        if "swot" in query.lower():
            keywords = ["strength", "weakness", "opportunit", "threat"]
            found = sum(1 for k in keywords if k.lower() in output.lower())
            print(f"   🎯 SWOT keywords: {found}/4 found")
        
        results.append({
            "model": model,
            "query": query,
            "success": True,
            "time_ms": elapsed,
            "length": len(output)
        })
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append({
            "model": model, 
            "query": query,
            "success": False,
            "error": str(e)
        })

# Summary
print(f"\n{'='*50}")
print("SUMMARY")
print("="*50)

successful = [r for r in results if r.get("success")]
print(f"✅ Successful tests: {len(successful)}/{len(results)}")

if successful:
    gpt5_times = [r["time_ms"] for r in successful if "gpt-5" in r["model"]]
    o4_times = [r["time_ms"] for r in successful if "o4" in r["model"]]
    
    if gpt5_times:
        print(f"⚡ gpt-5-mini avg: {sum(gpt5_times)//len(gpt5_times)}ms")
    if o4_times:
        print(f"🧠 o4-mini avg: {sum(o4_times)//len(o4_times)}ms")

print("\n✅ PRODUCTION TEST COMPLETE")