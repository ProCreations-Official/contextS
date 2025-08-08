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
    """Search for libraries and get search results.
    
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
    context: str,
    topic: Optional[str] = None,
    tokens: int = 150000,
    version: Optional[str] = None,
    model: Optional[str] = None,
    extra_libraries: Optional[list[str]] = None
) -> str:
    f"""Get AI-enhanced documentation with targeted code examples.
    
    For single library documentation, only use library_id and context.
    For multi-library integration help, use extra_libraries when your project needs multiple libraries working together.
    
    Args:
        library_id: The library ID for your primary/main library (e.g., 'vercel/next.js', 'mongodb/docs')
        context: REQUIRED - Detailed context about what you're trying to accomplish. Provide comprehensive details about your project, requirements, and specific implementation needs to get the best code examples and explanations. Note that this is what the internal AI powering this tool will give you documentation on or help you with code based on this parameter. Be comprehensive and give full detail about what you need.
        topic: OPTIONAL - Specific topic to focus documentation on (e.g., 'routing', 'authentication', 'setup')
        tokens: OPTIONAL - Maximum tokens to retrieve per library (default: 150000, capped at 200k). Please note that this is the number of tokens the internal AI powering this tool will recive of documentation to assist you, so we recommend either not setting this value (will use default), or set a high number, capped at 200000.
        version: Optional specific version for the main library (e.g., 'v14.3.0-canary.87')
        model: {generate_model_description()}
        extra_libraries: ONLY use when you need help integrating MULTIPLE libraries together. List of up to 2 additional library IDs. Example: if building a Next.js app with Supabase auth and Tailwind styling, use library_id="vercel/next.js" and extra_libraries=["supabase/supabase", "tailwindlabs/tailwindcss"]
    
    Returns:
        AI-enhanced documentation with practical code examples and guidance, based on what you entered in 'context'. If extra_libraries provided, includes integration patterns showing how the libraries work together.
    
    Examples:
        # Single library - just learning Next.js routing
        get_smart_docs("vercel/next.js", "learning dynamic routing for blog posts")
        
        # Multi-library - building full-stack app with multiple technologies
        get_smart_docs("vercel/next.js", "building e-commerce site with auth and payments", 
                      extra_libraries=["supabase/supabase", "stripe/stripe-js"])
    """
    if not library_id:
        return "Error: library_id parameter is required"
    
    if not context or not context.strip():
        return "Error: context parameter is required - provide detailed context about what you're trying to accomplish"
    
    # Validate extra_libraries parameter
    if extra_libraries is not None:
        if not isinstance(extra_libraries, list):
            return "Error: extra_libraries must be a list of library IDs"
        if len(extra_libraries) > 2:
            return "Error: maximum 2 extra libraries allowed"
        if len(extra_libraries) == 0:
            return "Error: extra_libraries cannot be empty if provided"
        for lib in extra_libraries:
            if not isinstance(lib, str) or not lib.strip():
                return "Error: each extra library must be a non-empty string"
    
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
        # Fetch documentation for main library
        main_docs, main_error = await _fetch_library_docs(library_id, topic, tokens, version)
        if main_error:
            return main_error
        
        # Build docs dictionary starting with main library
        all_docs = {library_id: main_docs}
        
        # Fetch documentation for extra libraries if provided
        if extra_libraries:
            for extra_lib in extra_libraries:
                extra_docs, extra_error = await _fetch_library_docs(extra_lib, topic, tokens, None)  # No version for extra libs
                if extra_error:
                    # Include partial results with error message
                    all_docs[extra_lib] = f"[ERROR: {extra_error}]"
                else:
                    all_docs[extra_lib] = extra_docs
        
        # Enhance with AI (Gemini or OpenAI based on availability and model selection)
        enhanced_docs = await enhance_with_ai(all_docs, library_id, topic, context, model)
        return enhanced_docs
        
    except Exception as e:
        return f"Error: {str(e)}"

async def _fetch_library_docs(library_id: str, topic: Optional[str], tokens: int, version: Optional[str]) -> tuple[str, str]:
    """Fetch documentation for a single library from Context7.
    
    Returns:
        Tuple of (docs_content, error_message). If error_message is not None, docs_content will be empty.
    """
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
            
            return response.text, None
            
    except httpx.HTTPStatusError as e:
        error_msg = f"Error fetching docs for '{library_id}': HTTP {e.response.status_code}"
        if e.response.status_code == 404:
            error_msg += f". Library '{library_id}' not found. Use resolve_library_id to search for the correct ID."
        return "", error_msg
    except Exception as e:
        return "", f"Error fetching docs for '{library_id}': {str(e)}"

async def enhance_with_ai(docs_dict: dict[str, str], main_library_id: str, topic: Optional[str], context: str, selected_model: Optional[str] = None) -> str:
    """Enhance documentation with AI-powered insights and code examples."""
    
    # Determine which model to use based on availability and preference
    model_to_use, error_message = await _determine_ai_model(selected_model)
    
    if error_message:
        main_docs = docs_dict.get(main_library_id, "")
        return f"# Documentation for {main_library_id}\n\n{main_docs}\n\n*{error_message}*"
    
    try:
        # Create enhancement prompt for multiple libraries
        libraries_list = list(docs_dict.keys())
        main_docs = docs_dict.get(main_library_id, "")
        
        docs_sections = []
        for lib_id, lib_docs in docs_dict.items():
            if lib_id == main_library_id:
                docs_sections.append(f"## PRIMARY LIBRARY: {lib_id}\n{lib_docs}")
            else:
                docs_sections.append(f"## ADDITIONAL LIBRARY: {lib_id}\n{lib_docs}")
        
        all_docs_text = "\n\n".join(docs_sections)
        
        # Create appropriate prompt based on number of libraries
        has_multiple_libraries = len(libraries_list) > 1
        
        if has_multiple_libraries:
            # Multi-library prompt
            additional_libs = [lib for lib in libraries_list if lib != main_library_id]
            prompt = f"""You are ContextS, a world-class technical documentation expert. Transform raw documentation into comprehensive, practical guides that make developers instantly productive.

**Context (what the user needs):** {context}
**Primary Library:** {main_library_id}
**Integration Libraries:** {', '.join(additional_libs)}
**Focus:** {topic or "complete integration guide"}

**Source Documentation:**
{all_docs_text}

**Your Mission:**
Create a definitive integration guide that shows exactly how to use {main_library_id} with {', '.join(additional_libs)}. Every code example must be:
- Complete and ready to run
- Explained with clear reasoning
- Focused on real-world implementation
- Optimized for the user's specific context
- Answers any questions the user has in 'context'

**Required Structure:**

# {main_library_id} + {', '.join(additional_libs)} Integration Guide

## Quick Start
[Most essential setup and basic integration example - get users running in minutes]

## Core Integration Patterns
[The 3-4 most important ways these libraries work together, with complete examples]

## Production Implementation
[Full, deployable example addressing the user's specific context with:
- Complete setup and configuration
- Error handling and edge cases
- Performance and security best practices
- Testing strategy]

## Advanced Techniques
[Power-user patterns and optimizations specific to this library combination]

## Common Issues & Solutions
[Real problems developers face with these libraries together, with fixes]

## Complete API Reference
[Enhanced reference with integration-focused examples]

**Quality Requirements:**
- All code examples must be complete and runnable
- Explain WHY, not just HOW
- Focus ruthlessly on the user's stated context
- Prioritize practical over theoretical
- Include error handling in all examples
- Show performance implications of choices

Make this the definitive resource for using these libraries together."""
        else:
            # Single library prompt
            prompt = f"""You are ContextS, a world-class technical documentation expert. Transform raw documentation into comprehensive, practical guides that make developers instantly productive.

**Context (what the user needs):** {context}
**Library:** {main_library_id}
**Focus:** {topic or "complete implementation guide"}

**Source Documentation:**
{all_docs_text}

**Your Mission:**
Create the definitive guide for {main_library_id} that directly addresses the user's context. Every code example must be:
- Complete and ready to run
- Explained with clear reasoning
- Focused on real-world implementation
- Optimized for the user's specific needs

**Required Structure:**

# Complete {main_library_id} Implementation Guide

## Quick Start
[Get the user productive in under 5 minutes with the most essential example]

## Core Concepts & Implementation
[The fundamental patterns and concepts, with complete working examples that build toward the user's goal]

## Production-Ready Solution
[Full implementation addressing the user's specific context with:
- Complete setup and configuration
- Error handling and edge cases
- Performance optimization
- Security best practices
- Testing approach]

## Advanced Techniques
[Power-user patterns and optimizations for complex scenarios]

## Common Issues & Solutions
[Real problems developers encounter, with detailed troubleshooting steps]

## Complete API Reference
[Enhanced reference with practical examples for each major feature]

**Quality Requirements:**
- All code examples must be complete and runnable
- Explain the reasoning behind every design choice
- Focus ruthlessly on the user's stated context and goals
- Prioritize practical implementation over theoretical concepts
- Include comprehensive error handling
- Show performance and security implications
- Provide multiple approaches when relevant

Make this THE resource developers need to master {main_library_id} for their specific use case."""

        # Generate enhanced documentation based on selected model
        if model_to_use.startswith("gemini"):
            return await _enhance_with_gemini(prompt, model_to_use, main_library_id, main_docs)
        elif model_to_use.startswith("gpt"):
            return await _enhance_with_openai(prompt, model_to_use, main_library_id, main_docs)
        else:
            return f"# Documentation for {main_library_id}\n\n{main_docs}\n\n*Unsupported model: {model_to_use}*"
            
    except Exception as e:
        logger.error(f"AI enhancement failed: {e}")
        return f"# Documentation for {main_library_id}\n\n{main_docs}\n\n*AI enhancement failed: {str(e)}*"


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
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 24576,
            },
            system_instruction="You are ContextS, a world-class technical documentation expert who creates comprehensive, practical guides. You excel at transforming raw documentation into immediately actionable resources that make developers productive. Focus on complete, runnable examples with clear explanations of WHY each choice matters."
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
                {"role": "system", "content": "You are ContextS, a world-class technical documentation expert who creates comprehensive, practical guides. You excel at transforming raw documentation into immediately actionable resources that make developers productive. Focus on complete, runnable examples with clear explanations of WHY each choice matters."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=24576,
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
