#!/usr/bin/env python3
"""
Simple test script for ContextS MCP Server
"""

import asyncio
import sys
from main import resolve_library_id, get_smart_docs, chat_continue

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
        result = await get_smart_docs("vercel/next.js", "routing")
        print("✅ Documentation fetch successful!")
        print(f"Result length: {len(result)} characters")
        if "routing" in result.lower() or "next.js" in result.lower():
            print("✅ Documentation contains expected content!")
        else:
            print("⚠️ Expected content not found")
    except Exception as e:
        print(f"❌ Documentation fetch failed: {e}")

    # Test 3: Chat continuation
    print("\n3️⃣ Testing chat continuation...")
    try:
        # Start a conversation
        print("   - Starting conversation with get_smart_docs...")
        initial_context = "how to handle basic routing in next.js"
        initial_response = await get_smart_docs("vercel/next.js", initial_context, model="gemini-2.5-flash")

        if "AI enhancement failed" in initial_response:
            print("   ✅ Initial get_smart_docs call failed as expected (no API key).")
        elif "error" in initial_response.lower():
            print(f"❌ Initial get_smart_docs call failed: {initial_response}")
        else:
            print("   ✅ Initial get_smart_docs call successful.")

        # Continue the conversation
        print("   - Continuing conversation with chat_continue...")
        follow_up_context = "what about dynamic routes?"
        chat_response = await chat_continue(follow_up_context)

        if "AI enhancement failed" in chat_response:
            print("   ✅ Chat continuation failed as expected (no API key).")
        elif "error" in chat_response.lower():
            print(f"❌ Chat continuation failed: {chat_response}")
        elif "dynamic" in chat_response.lower() and "route" in chat_response.lower():
            print("   ✅ Chat continuation successful with expected content.")
        else:
            print("   ⚠️ Chat continuation response did not contain expected content.")

    except Exception as e:
        print(f"❌ Chat continuation test failed: {e}")
    
    print("\n🎉 Testing complete!")

if __name__ == "__main__":
    asyncio.run(test_tools())