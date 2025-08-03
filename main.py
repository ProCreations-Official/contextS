#!/usr/bin/env python3
"""
ContextS MCP Server
A smart version of Context7 that enhances documentation with AI-powered code examples.
"""

import logging
import os
from typing import Optional

import httpx
import google.generativeai as genai
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Gemini AI (required)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is required for ContextS to function.")
genai.configure(api_key=GEMINI_API_KEY)
    
# Context7 API base URL
CONTEXT7_BASE_URL = "https://context7.com/api/v1"

# Create FastMCP server instance
mcp = FastMCP("ContextS")

@mcp.tool()
async def resolve_library_id(query: str) -> str:
    """Search for libraries and get Context7-compatible IDs.
    
    Args:
        query: Library name to search for (e.g., 'next.js', 'supabase')
    
    Returns:
        Formatted list of available libraries with their IDs
    """
    if not query:
        return "Error: Query parameter is required"
    
    try:
        async with httpx.AsyncClient() as client:
            url = f"{CONTEXT7_BASE_URL}/search"
            params = {"query": query}
            headers = {"Content-Type": "application/json"}
            
            response = await client.get(url, params=params, headers=headers, timeout=30.0)
            response.raise_for_status()
            
            data = response.json()
            
            # Context7 API returns results in {"results": [...]} format
            results = data.get("results", [])
            
            # Format the response nicely
            if results:
                result = "Available Libraries:\n\n"
                for idx, item in enumerate(results[:10], 1):  # Limit to top 10 results
                    name = item.get("title", "Unknown")
                    library_id = item.get("id", "Unknown")
                    description = item.get("description", "No description")
                    versions = item.get("versions", [])
                    trust_score = item.get("trustScore", 0)
                    stars = item.get("stars", 0)
                    
                    result += f"{idx}. **{name}**\n"
                    result += f"   - Library ID: `{library_id}`\n"
                    result += f"   - Description: {description}\n"
                    if versions:
                        result += f"   - Available versions: {', '.join(versions[:5])}\n"
                    result += f"   - Trust Score: {trust_score}/10, Stars: {stars:,}\n"
                    result += "\n"
                
                result += "\n**Usage:** Use the Library ID with the `get_smart_docs` tool to fetch documentation."
                return result
            else:
                return f"No libraries found for query: {query}"
            
    except httpx.TimeoutException:
        return "Error: Request timed out"
    except httpx.HTTPStatusError as e:
        return f"Error: HTTP {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def get_smart_docs(
    library_id: str,
    topic: Optional[str] = None,
    tokens: int = 200000,
    version: Optional[str] = None,
    context: Optional[str] = None
) -> str:
    """Get AI-enhanced documentation with targeted code examples.
    
    Args:
        library_id: Context7-compatible library ID (e.g., 'vercel/next.js', 'mongodb/docs')
        topic: Optional topic to focus on (e.g., 'routing', 'authentication')
        tokens: Maximum tokens to retrieve (default: 200000)
        version: Optional specific version (e.g., 'v14.3.0-canary.87')
        context: Detailed context about what you're trying to accomplish - provide comprehensive details about your project, requirements, and specific implementation needs to get the best code examples and explanations
    
    Returns:
        AI-enhanced documentation with practical code examples
    """
    if not library_id:
        return "Error: library_id parameter is required"
    
    try:
        # Construct Context7 URL
        url_path = library_id.lstrip('/')  # Remove leading slash if present
        if version:
            url_path = f"{url_path}/{version}"
        
        url = f"{CONTEXT7_BASE_URL}/{url_path}"
        
        # Build query parameters
        params = {
            "type": "txt",
            "tokens": min(tokens, 200000)  # Cap at 200k tokens
        }
        
        if topic:
            params["topic"] = topic
        
        headers = {
            "Content-Type": "application/json",
            "X-Context7-Source": "mcp-server"
        }
        
        # Fetch documentation from Context7
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers, timeout=60.0)
            response.raise_for_status()
            
            raw_docs = response.text
            
        # Enhance with Gemini AI (required)
        enhanced_docs = await enhance_with_ai(raw_docs, library_id, topic, context or "")
        return enhanced_docs
        
    except httpx.HTTPStatusError as e:
        error_msg = f"Error fetching docs: HTTP {e.response.status_code}"
        if e.response.status_code == 404:
            error_msg += f"\n\nLibrary '{library_id}' not found. Use resolve_library_id to search for the correct ID."
        return error_msg
    except Exception as e:
        return f"Error: {str(e)}"

async def enhance_with_ai(docs: str, library_id: str, topic: Optional[str], context: str) -> str:
    """Enhance documentation with AI-powered insights and code examples."""
    try:
        # Configure Gemini model
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config={
                "temperature": 0.3,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
        )
        
        # Create enhancement prompt
        prompt = f"""You are ContextS, an expert technical documentation assistant specializing in creating comprehensive, in-depth code documentation with extensive explanations. Your mission is to transform raw documentation into detailed, educational resources that teach developers not just HOW to use the code, but WHY it works and WHAT to do with it.

**Library:** {library_id}
**Topic:** {topic or "comprehensive coverage"}
**Developer Context:** {context or "comprehensive development guidance needed"}

**Raw Documentation:**
{docs}

**Your Enhancement Mission:**
Create an exhaustive, educational guide that provides DEEP context and EXTENSIVE explanations. For every code example, explain:

1. **What the code does** - Line-by-line explanations when needed
2. **Why it's structured this way** - Design patterns and architectural decisions
3. **How to implement it** - Complete, production-ready examples with full context
4. **What to watch out for** - Common pitfalls, edge cases, and debugging tips
5. **How to extend it** - Ways to modify and adapt the code for different scenarios
6. **When to use it** - Appropriate use cases and alternatives

**Required Response Structure:**
# Complete ContextS Documentation for {library_id}

## 📋 Comprehensive Overview
[Detailed explanation of what this library does, its core philosophy, and when/why to use it]

## 🚀 Essential Concepts Deep Dive
[In-depth explanation of fundamental concepts with detailed examples and reasoning]

## 💡 Step-by-Step Implementation Guide
[Complete walkthrough with extensive code examples, each with detailed explanations of:
- What each line does
- Why it's necessary
- How it fits into the bigger picture
- Alternative approaches and their trade-offs]

## 🔧 Advanced Usage Patterns
[Complex real-world scenarios with comprehensive code examples and thorough explanations]

## ⚡ Production-Ready Examples
[Complete, deployable code examples with:
- Full error handling
- Best practices implementation
- Performance considerations
- Security considerations
- Testing approaches]

## 🛠️ Implementation Strategies
[Detailed guidance on how to structure projects, organize code, and integrate with other tools]

## 🔍 Troubleshooting & Debugging
[Comprehensive troubleshooting guide with common issues, their causes, and detailed solutions]

## 📚 Enhanced Complete Reference
[Reorganized and enhanced version of the original documentation with additional context and examples]

**Quality Standards:**
- Provide EXTENSIVE explanations for all code examples
- Include complete, working code that can be copy-pasted and used
- Explain the reasoning behind architectural decisions
- Cover edge cases and error scenarios
- Provide multiple approaches when applicable
- Make it educational and comprehensive, not just functional

Create documentation that teaches developers to become experts, not just users."""

        # Generate enhanced documentation
        import asyncio
        response = await asyncio.to_thread(model.generate_content, prompt)
        
        if response and response.text:
            return response.text
        else:
            return f"# Documentation for {library_id}\n\n{docs}\n\n*AI enhancement unavailable at the moment.*"
            
    except Exception as e:
        logger.error(f"AI enhancement failed: {e}")
        return f"# Documentation for {library_id}\n\n{docs}\n\n*AI enhancement failed: {str(e)}*"


def main():
    """Main server entry point."""
    mcp.run()


if __name__ == "__main__":
    main()