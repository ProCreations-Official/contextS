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

# Initialize Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
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
    user_context: Optional[str] = None
) -> str:
    """Get AI-enhanced documentation with targeted code examples.
    
    Args:
        library_id: Context7-compatible library ID (e.g., 'vercel/next.js', 'mongodb/docs')
        topic: Optional topic to focus on (e.g., 'routing', 'authentication')
        tokens: Maximum tokens to retrieve (default: 200000)
        version: Optional specific version (e.g., 'v14.3.0-canary.87')
        user_context: What you're trying to accomplish (helps AI generate relevant examples)
    
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
            
        # If no Gemini API key, return raw docs
        if not GEMINI_API_KEY:
            return f"# Documentation for {library_id}\n\n{raw_docs}\n\n*Note: Set GEMINI_API_KEY environment variable to enable AI enhancement.*"
        
        # Enhance with Gemini AI
        enhanced_docs = await enhance_with_ai(raw_docs, library_id, topic, user_context or "")
        return enhanced_docs
        
    except httpx.HTTPStatusError as e:
        error_msg = f"Error fetching docs: HTTP {e.response.status_code}"
        if e.response.status_code == 404:
            error_msg += f"\n\nLibrary '{library_id}' not found. Use resolve_library_id to search for the correct ID."
        return error_msg
    except Exception as e:
        return f"Error: {str(e)}"

async def enhance_with_ai(docs: str, library_id: str, topic: Optional[str], user_context: str) -> str:
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
        prompt = f"""You are ContextS, a smart documentation assistant. Your job is to enhance technical documentation with practical, targeted code examples and guidance.

**Library:** {library_id}
**Topic:** {topic or "general"}
**User Context:** {user_context or "general development"}

**Raw Documentation:**
{docs}

**Instructions:**
1. Analyze the documentation and identify the most important concepts
2. Create practical, working code examples that demonstrate key features
3. Provide step-by-step guidance for common use cases
4. Focus on actionable insights that help developers get things done
5. Keep examples concise but complete
6. Include error handling and best practices where relevant

**Format your response as:**
# Smart Documentation for {library_id}

## Key Concepts
[Brief overview of main concepts]

## Quick Start Examples
[2-3 practical code examples with explanations]

## Advanced Usage
[More complex examples if applicable]

## Best Practices & Tips
[Practical advice and common gotchas]

## Complete Documentation
[Enhanced version of the original docs with better organization]

Generate targeted, practical examples that help developers implement solutions quickly."""

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