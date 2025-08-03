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
    context: str,
    topic: Optional[str] = None,
    tokens: int = 200000,
    version: Optional[str] = None,
    model: Optional[str] = None,
    extra_libraries: Optional[list[str]] = None
) -> str:
    f"""Get AI-enhanced documentation with targeted code examples.
    
    For single library documentation, only use library_id and context.
    For multi-library integration help, use extra_libraries when your project needs multiple libraries working together.
    
    Args:
        library_id: Context7-compatible library ID for your primary/main library (e.g., 'vercel/next.js', 'mongodb/docs')
        context: REQUIRED - Detailed context about what you're trying to accomplish. Provide comprehensive details about your project, requirements, and specific implementation needs to get the best code examples and explanations
        topic: Optional topic to focus on (e.g., 'routing', 'authentication', 'setup')
        tokens: Maximum tokens to retrieve per library (default: 200000, capped at 200k)
        version: Optional specific version for the main library (e.g., 'v14.3.0-canary.87')
        model: {generate_model_description()}
        extra_libraries: ONLY use when you need help integrating MULTIPLE libraries together. List of up to 2 additional library IDs. Example: if building a Next.js app with Supabase auth and Tailwind styling, use library_id="vercel/next.js" and extra_libraries=["supabase/supabase", "tailwindlabs/tailwindcss"]
    
    Returns:
        AI-enhanced documentation with practical code examples. If extra_libraries provided, includes integration patterns showing how the libraries work together.
    
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
            prompt = f"""You are ContextS, an expert technical documentation assistant specializing in creating comprehensive, in-depth code documentation with extensive explanations. Your mission is to transform raw documentation from multiple libraries into detailed, educational resources that teach developers not just HOW to use the code, but WHY it works and WHAT to do with it.

**Primary Library:** {main_library_id}
**Additional Libraries:** {', '.join(additional_libs)}
**Topic:** {topic or "comprehensive coverage"}
**Developer Context:** {context}

**Raw Documentation from Multiple Libraries:**
{all_docs_text}

**Your Enhancement Mission:**
Create an exhaustive, educational guide that provides DEEP context and EXTENSIVE explanations. Focus primarily on {main_library_id} but show how it integrates with the additional libraries. For every code example, explain:

1. **What the code does** - Line-by-line explanations when needed
2. **Why it's structured this way** - Design patterns and architectural decisions
3. **How to implement it** - Complete, production-ready examples with full context
4. **How libraries work together** - Integration patterns and best practices
5. **What to watch out for** - Common pitfalls, edge cases, and debugging tips
6. **How to extend it** - Ways to modify and adapt the code for different scenarios
7. **When to use it** - Appropriate use cases and alternatives

**Required Response Structure:**
# Complete ContextS Multi-Library Documentation

## Comprehensive Overview
[Detailed explanation of the primary library and how it works with additional libraries, core philosophy, and when/why to use this combination]

## Essential Concepts Deep Dive
[In-depth explanation of fundamental concepts across all libraries with detailed examples and reasoning]

## Step-by-Step Implementation Guide
[Complete walkthrough with extensive code examples showing library integration, each with detailed explanations of:
- What each line does
- Why it's necessary
- How it fits into the bigger picture
- How libraries complement each other
- Alternative approaches and their trade-offs]

## Advanced Usage Patterns
[Complex real-world scenarios with comprehensive code examples showing multi-library integration and thorough explanations]

## Production-Ready Examples
[Complete, deployable code examples with:
- Full error handling
- Best practices implementation
- Performance considerations
- Security considerations
- Testing approaches
- Multi-library coordination]

## Implementation Strategies
[Detailed guidance on how to structure projects, organize code, and integrate multiple libraries effectively]

## Troubleshooting & Debugging
[Comprehensive troubleshooting guide with common issues across all libraries, their causes, and detailed solutions]

## Enhanced Complete Reference
[Reorganized and enhanced version of the original documentation with additional context and cross-library examples]

**Quality Standards:**
- Provide EXTENSIVE explanations for all code examples
- Include complete, working code that can be copy-pasted and used
- Explain the reasoning behind architectural decisions
- Cover edge cases and error scenarios
- Show how libraries work together effectively
- Provide multiple approaches when applicable
- Make it educational and comprehensive, not just functional

Create documentation that teaches developers to become experts with multiple libraries, not just users."""
        else:
            # Single library prompt (original style with fewer emojis)
            prompt = f"""You are ContextS, an expert technical documentation assistant specializing in creating comprehensive, in-depth code documentation with extensive explanations. Your mission is to transform raw documentation into detailed, educational resources that teach developers not just HOW to use the code, but WHY it works and WHAT to do with it.

**Library:** {main_library_id}
**Topic:** {topic or "comprehensive coverage"}
**Developer Context:** {context}

**Raw Documentation:**
{all_docs_text}

**Your Enhancement Mission:**
Create an exhaustive, educational guide that provides DEEP context and EXTENSIVE explanations. For every code example, explain:

1. **What the code does** - Line-by-line explanations when needed
2. **Why it's structured this way** - Design patterns and architectural decisions
3. **How to implement it** - Complete, production-ready examples with full context
4. **What to watch out for** - Common pitfalls, edge cases, and debugging tips
5. **How to extend it** - Ways to modify and adapt the code for different scenarios
6. **When to use it** - Appropriate use cases and alternatives

**Required Response Structure:**
# Complete ContextS Documentation for {main_library_id}

## Comprehensive Overview
[Detailed explanation of what this library does, its core philosophy, and when/why to use it]

## Essential Concepts Deep Dive
[In-depth explanation of fundamental concepts with detailed examples and reasoning]

## Step-by-Step Implementation Guide
[Complete walkthrough with extensive code examples, each with detailed explanations of:
- What each line does
- Why it's necessary
- How it fits into the bigger picture
- Alternative approaches and their trade-offs]

## Advanced Usage Patterns
[Complex real-world scenarios with comprehensive code examples and thorough explanations]

## Production-Ready Examples
[Complete, deployable code examples with:
- Full error handling
- Best practices implementation
- Performance considerations
- Security considerations
- Testing approaches]

## Implementation Strategies
[Detailed guidance on how to structure projects, organize code, and integrate with other tools]

## Troubleshooting & Debugging
[Comprehensive troubleshooting guide with common issues, their causes, and detailed solutions]

## Enhanced Complete Reference
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