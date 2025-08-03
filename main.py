#!/usr/bin/env python3
"""
ContextS MCP Server
A smart version of Context7 that enhances documentation with AI-powered code examples.
"""

import logging
import os
from typing import Optional, Literal

import httpx
import google.generativeai as genai
from mcp.server.fastmcp import FastMCP

# Try to import OpenAI (optional dependency)
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize AI services (at least one is required)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configure Gemini if available
GEMINI_AVAILABLE = bool(GEMINI_API_KEY)
if GEMINI_AVAILABLE:
    genai.configure(api_key=GEMINI_API_KEY)

# Validate that at least one AI service is configured
if not (GEMINI_AVAILABLE or (OPENAI_AVAILABLE and OPENAI_API_KEY)):
    raise ValueError(
        "At least one AI service must be configured. Set GEMINI_API_KEY and/or OPENAI_API_KEY environment variables."
    )
    
# Context7 API base URL
CONTEXT7_BASE_URL = "https://context7.com/api/v1"

# Model availability functions
def get_available_models() -> dict:
    """Get available AI models based on configured API keys."""
    available = {
        "gemini": [],
        "openai": []
    }
    
    if GEMINI_AVAILABLE:
        available["gemini"] = [
            "gemini-2.5-pro",      # Slowest, highest quality
            "gemini-2.5-flash",    # Default for Gemini, good balance  
            "gemini-2.5-flash-lite" # Fastest, worst quality
        ]
    
    if OPENAI_AVAILABLE and OPENAI_API_KEY:
        available["openai"] = [
            "gpt-4.1",      # Slowest, highest quality
            "gpt-4.1-mini", # Balance of speed and quality
            "gpt-4.1-nano"  # Fastest, worst quality
        ]
    
    return available

def get_all_available_models() -> list:
    """Get a flat list of all available model names."""
    available = get_available_models()
    all_models = []
    all_models.extend(available["gemini"])
    all_models.extend(available["openai"])
    return all_models

def generate_model_description() -> str:
    """Generate dynamic model parameter description based on available models."""
    available = get_available_models()
    
    if not available["gemini"] and not available["openai"]:
        return "No AI models available. Please configure GEMINI_API_KEY and/or OPENAI_API_KEY."
    
    description = "Optional AI model to use. Available options:\n"
    
    if available["gemini"]:
        description += "\nGemini models (require GEMINI_API_KEY):\n"
        for model in available["gemini"]:
            if model == "gemini-2.5-pro":
                description += f'               - "{model}": Slowest, highest quality\n'
            elif model == "gemini-2.5-flash":
                description += f'               - "{model}": Default for Gemini, good balance\n'
            elif model == "gemini-2.5-flash-lite":
                description += f'               - "{model}": Fastest, worst quality\n'
    
    if available["openai"]:
        description += "\nOpenAI models (require OPENAI_API_KEY):\n"
        for model in available["openai"]:
            if model == "gpt-4.1":
                description += f'               - "{model}": Slowest, highest quality\n'
            elif model == "gpt-4.1-mini":
                description += f'               - "{model}": Balance of speed and quality\n'
            elif model == "gpt-4.1-nano":
                description += f'               - "{model}": Fastest, worst quality\n'
    
    # Set default
    if available["gemini"]:
        description += f'\n               If not specified, will use "gemini-2.5-flash".'
    elif available["openai"]:
        description += f'\n               If not specified, will use "gpt-4.1".'
    
    return description

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
    context: Optional[str] = None,
    model: Optional[str] = None
) -> str:
    f"""Get AI-enhanced documentation with targeted code examples.
    
    Args:
        library_id: Context7-compatible library ID (e.g., 'vercel/next.js', 'mongodb/docs')
        topic: Optional topic to focus on (e.g., 'routing', 'authentication')
        tokens: Maximum tokens to retrieve (default: 200000)
        version: Optional specific version (e.g., 'v14.3.0-canary.87')
        context: Detailed context about what you're trying to accomplish - provide comprehensive details about your project, requirements, and specific implementation needs to get the best code examples and explanations
        model: {generate_model_description()}
    
    Returns:
        AI-enhanced documentation with practical code examples
    """
    if not library_id:
        return "Error: library_id parameter is required"
    
    # Validate requested model is available
    if model:
        available_models = get_all_available_models()
        if not available_models:
            return "Error: No AI models configured. Please set up GEMINI_API_KEY and/or OPENAI_API_KEY environment variables."
        
        if model not in available_models:
            # Provide specific error messages based on model type
            if model.startswith("gemini"):
                if not GEMINI_AVAILABLE:
                    return f"Error: Gemini model '{model}' requested but GEMINI_API_KEY not configured. Please set up Gemini API or try an OpenAI model if available."
                else:
                    return f"Error: Unknown Gemini model '{model}'. Available Gemini models: {', '.join([m for m in available_models if m.startswith('gemini')])}."
            elif model.startswith("gpt"):
                if not (OPENAI_AVAILABLE and OPENAI_API_KEY):
                    return f"Error: OpenAI model '{model}' requested but OpenAI API not configured. Please set up OPENAI_API_KEY or try a Gemini model if available."
                else:
                    return f"Error: Unknown OpenAI model '{model}'. Available OpenAI models: {', '.join([m for m in available_models if m.startswith('gpt')])}."
            else:
                return f"Error: Unknown model '{model}'. Available models: {', '.join(available_models)}."
    
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
            
        # Enhance with AI (Gemini or OpenAI based on availability and model selection)
        enhanced_docs = await enhance_with_ai(raw_docs, library_id, topic, context or "", model)
        return enhanced_docs
        
    except httpx.HTTPStatusError as e:
        error_msg = f"Error fetching docs: HTTP {e.response.status_code}"
        if e.response.status_code == 404:
            error_msg += f"\n\nLibrary '{library_id}' not found. Use resolve_library_id to search for the correct ID."
        return error_msg
    except Exception as e:
        return f"Error: {str(e)}"

async def enhance_with_ai(docs: str, library_id: str, topic: Optional[str], context: str, selected_model: Optional[str] = None) -> str:
    """Enhance documentation with AI-powered insights and code examples."""
    
    # Determine which model to use based on availability and preference
    model_to_use, error_message = await _determine_ai_model(selected_model)
    
    if error_message:
        return f"# Documentation for {library_id}\n\n{docs}\n\n*{error_message}*"
    
    try:
        # Create enhancement prompt (same for both AI services)
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

        # Generate enhanced documentation based on selected model
        if model_to_use.startswith("gemini"):
            return await _enhance_with_gemini(prompt, model_to_use, library_id, docs)
        elif model_to_use.startswith("gpt"):
            return await _enhance_with_openai(prompt, model_to_use, library_id, docs)
        else:
            return f"# Documentation for {library_id}\n\n{docs}\n\n*Unsupported model: {model_to_use}*"
            
    except Exception as e:
        logger.error(f"AI enhancement failed: {e}")
        return f"# Documentation for {library_id}\n\n{docs}\n\n*AI enhancement failed: {str(e)}*"


async def _determine_ai_model(requested_model: Optional[str]) -> tuple[Optional[str], Optional[str]]:
    """Determine which AI model to use based on availability and request.
    
    Returns:
        Tuple of (model_name, error_message). If error_message is not None, model_name will be None.
    """
    
    # If a specific model is requested, validate it's available
    if requested_model:
        available_models = get_all_available_models()
        
        if not available_models:
            return None, "No AI models configured. Please set up GEMINI_API_KEY and/or OPENAI_API_KEY environment variables."
        
        if requested_model not in available_models:
            if requested_model.startswith("gemini"):
                if not GEMINI_AVAILABLE:
                    return None, f"Gemini model '{requested_model}' requested but GEMINI_API_KEY not configured. Please set up Gemini API."
                else:
                    gemini_models = [m for m in available_models if m.startswith('gemini')]
                    return None, f"Unknown Gemini model '{requested_model}'. Available Gemini models: {', '.join(gemini_models)}."
            elif requested_model.startswith("gpt"):
                if not (OPENAI_AVAILABLE and OPENAI_API_KEY):
                    return None, f"OpenAI model '{requested_model}' requested but OpenAI API not configured. Please set up OPENAI_API_KEY."
                else:
                    openai_models = [m for m in available_models if m.startswith('gpt')]
                    return None, f"Unknown OpenAI model '{requested_model}'. Available OpenAI models: {', '.join(openai_models)}."
            else:
                return None, f"Unknown model '{requested_model}'. Available models: {', '.join(available_models)}."
        
        # Requested model is available
        return requested_model, None
    
    # No specific model requested, use default priority: Gemini first, then OpenAI
    if GEMINI_AVAILABLE:
        return "gemini-2.5-flash", None
    elif OPENAI_AVAILABLE and OPENAI_API_KEY:
        return "gpt-4.1", None
    
    return None, "No AI models configured. Please set up GEMINI_API_KEY and/or OPENAI_API_KEY environment variables."


async def _enhance_with_gemini(prompt: str, model_name: str, library_id: str, docs: str) -> str:
    """Enhance documentation using Google Gemini."""
    try:
        # Configure Gemini model
        gemini_model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={
                "temperature": 0.3,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
        )
        
        # Generate enhanced documentation
        import asyncio
        response = await asyncio.to_thread(gemini_model.generate_content, prompt)
        
        if response and response.text:
            return response.text
        else:
            return f"# Documentation for {library_id}\n\n{docs}\n\n*Gemini AI enhancement unavailable at the moment.*"
            
    except Exception as e:
        logger.error(f"Gemini enhancement failed: {e}")
        raise


async def _enhance_with_openai(prompt: str, model_name: str, library_id: str, docs: str) -> str:
    """Enhance documentation using OpenAI."""
    try:
        # Create async OpenAI client
        client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        
        # Use the exact model names as they exist in the OpenAI API
        actual_model = model_name
        
        # Generate enhanced documentation
        response = await client.chat.completions.create(
            model=actual_model,
            messages=[
                {"role": "system", "content": "You are ContextS, an expert technical documentation assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=8192,
        )
        
        await client.close()
        
        if response and response.choices and response.choices[0].message:
            return response.choices[0].message.content
        else:
            return f"# Documentation for {library_id}\n\n{docs}\n\n*OpenAI enhancement unavailable at the moment.*"
            
    except Exception as e:
        logger.error(f"OpenAI enhancement failed: {e}")
        raise


def main():
    """Main server entry point."""
    mcp.run()


if __name__ == "__main__":
    main()