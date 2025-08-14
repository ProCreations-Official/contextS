#!/usr/bin/env python3
"""
Simple test script for ContextS MCP Server
"""

import asyncio
import sys
from main import resolve_library_id, get_smart_docs

async def test_tools():
    """Test the ContextS tools."""
    print("🧪 Testing ContextS Tools...")
    
    # Test 1: Library search
    print("\n1️⃣ Testing library search...")
    try:
        result = await resolve_library_id("next.js")
        print("✅ Library search successful!")
        print(f"Result length: {len(result)} characters")
        if "vercel/next.js" in result:
            print("✅ Found expected library ID!")
        else:
            print("⚠️ Expected library ID not found")
    except Exception as e:
        print(f"❌ Library search failed: {e}")
    
    # Test 2: Documentation fetch (without AI enhancement)
    print("\n2️⃣ Testing documentation fetch...")
    try:
        result = await get_smart_docs("vercel/next.js", context="routing", tokens=1000)
        print("✅ Documentation fetch successful!")
        print(f"Result length: {len(result)} characters")
        if "routing" in result.lower() or "next.js" in result.lower():
            print("✅ Documentation contains expected content!")
        else:
            print("⚠️ Expected content not found")
    except Exception as e:
        print(f"❌ Documentation fetch failed: {e}")
    
    print("\n🎉 Testing complete!")

if __name__ == "__main__":
    asyncio.run(test_tools())