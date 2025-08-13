<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=22&duration=5000&pause=2000&color=6fa8dc&center=true&vCenter=true&width=600&lines=ContextS.+Let+AI+experts+help+your+AI." alt="Typing SVG" />

# ContextS - Smart Documentation MCP Server

*An AI to help your AI*

</div>

**ContextS** is an intelligent MCP (Model Context Protocol) server that enhances Context7 with AI-powered code examples and guidance. The "S" stands for **Smart** - it supports Google Gemini API, OpenAI API, and Anthropic Claude API models to provide targeted, practical documentation with working code examples tailored to your specific needs.

## Features

- **Smart Documentation**: AI-enhanced docs with practical code examples tailored to your project
- **Multi AI Support**: Choose between Google Gemini, OpenAI models, and Anthropic Sonnet 4 (1m)
- **Intelligent Fallback**: Automatically switches between AI providers  
- **Model Selection**: Pick the right model for speed vs quality tradeoffs
- **Library Search**: Find the right library IDs for any package
- **Version-Specific Docs**: Get documentation for specific library versions
- **Context-Aware**: Provide project details to get highly relevant examples
- **Up-to-Date Content**: Powered by Context7's real-time documentation database
- **MCP Compatible**: Works with Claude Desktop, Cursor, and other MCP clients
- **Multi-Library Support**: Optional integration examples from multiple libraries

## Requirements

- Python 3.8+
- At least one AI API key (Gemini and/or OpenAI)
- MCP-compatible client (Claude Desktop, Cursor, etc.)

### AI Provider Support

ContextS supports **Google Gemini**, **OpenAI**, and **Anthropic Sonnet 4 (1m)** models:

#### Google Gemini Models
- `gemini-2.5-pro` - Slowest, highest quality
- `gemini-2.5-flash` - Default, good balance (recommended)
- `gemini-2.5-flash-lite` - Fastest, lower quality

#### OpenAI Models  
- `gpt-4.1` - Slowest, highest quality
- `gpt-4.1-mini` - Balanced speed and quality
- `gpt-4.1-nano` - Fastest, lower quality

#### Anthropic Models  
- `claude-sonnet-4-20250514` with 1 million token context length (in beta) - Balanced speed and quality
**Note**: Claude Sonnet 4 with 1 million token context is in beta, and requires tier 4 API status. Technically, the normal Claude models would work with 200K context, but that's a bit tight.

**Intelligent Fallback**: If all APIs are configured, ContextS defaults to Gemini 2.5 Flash, then falls back to GPT-4.1, and finally tries Claude Sonnet 4 1m before giving up.
## Installation

### Step 1: Clone and Setup

```bash
# Clone the ContextS repository
git clone https://github.com/ProCreations-Official/contextS.git
cd contextS

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Get AI API Keys

You need **at least one** of the following API keys:

#### Option A: Google Gemini
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Set the environment variable:

```bash
export GEMINI_API_KEY="your-gemini-api-key-here"
```

#### Option B: OpenAI
1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Set the environment variable:

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

#### Option C: Anthropic
1. Go to [Anthropic Console API key settings](https://console.anthropic.com/settings/keys)
2. Create a new API key
3. Set the environment variable:

```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key-here"
```

#### Option C: All APIs (Best Experience)
For maximum reliability, configure all:

```bash
export GEMINI_API_KEY="your-gemini-api-key-here"
export OPENAI_API_KEY="your-openai-api-key-here"
export ANTHROPIC_API_KEY="your-anthropic-api-key-here"
```

**Note**: ContextS requires at least one AI API key to function. The server will not start without AI capabilities.

### Step 3: Configure Your MCP Client

#### For Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "contexts": {
      "command": "python3",
      "args": ["/path/to/ContextS/main.py"],
      "env": {
        "GEMINI_API_KEY": "your-gemini-api-key-here",
        "OPENAI_API_KEY": "your-openai-api-key-here",
        "ANTHROPIC_API_KEY": "your-anthropic-api-key-here"

      }
    }
  }
}
```

#### For Claude Code

Run this command:

```claude mcp add contextS python3 /path/to/ContextS/main.py  --env GEMINI_API_KEY=your-gemini-api-key-here OPENAI_API_KEY=your-openai-api-key-here ANTHROPIC_API_KEY=your-anthropic-api-key-here```


#### For Cursor IDE

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "contexts": {
      "command": "python3",
      "args": ["/path/to/ContextS/main.py"],
      "env": {
        "GEMINI_API_KEY": "your-gemini-api-key-here",
        "OPENAI_API_KEY": "your-openai-api-key-here",
        "ANTHROPIC_API_KEY": "your-anthropic-api-key-here"
      }
    }
  }
}
```

#### For Other MCP Clients

Follow your client's MCP server configuration documentation, using:
- **Command**: `python3`
- **Args**: `["/path/to/ContextS/main.py"]`
- **Environment**: Include the API keys you have configured:
  ```json
  {
  "GEMINI_API_KEY": "your-gemini-api-key-here",
  "OPENAI_API_KEY": "your-openai-api-key-here",
  "ANTHROPIC_API_KEY": "your-anthropic-api-key-here"
  }
  ```

**Note**: You only need to include the API keys you have. If you only have Gemini, just include `GEMINI_API_KEY`. If you only have OpenAI, just include `OPENAI_API_KEY`. If you only have Anthropic, just include `ANTHROPIC_API_KEY`.

## Usage

ContextS provides two main tools:

### 1. `resolve_library_id` - Search for Libraries

Find the correct library ID for any package:

```
resolve_library_id(query="next.js")
```

**Returns**: A list of matching libraries with their Context7-compatible IDs.

### 2. `get_smart_docs` - Get AI-Enhanced Documentation

**For most use cases, you only need `library_id` and `context`:**

```
get_smart_docs(
    library_id="vercel/next.js",
    context="building a blog with dynamic routes using Next.js 14, need comprehensive examples with file-based routing, dynamic segments, and SEO optimization"
)
```

**Use `extra_libraries` ONLY when your project requires multiple libraries working together:**

```
get_smart_docs(
    library_id="vercel/next.js",
    context="building a full-stack e-commerce site with Next.js frontend, Supabase for auth/database, and Stripe for payments - need integration examples",
    extra_libraries=["supabase/supabase", "stripe/stripe-js"]
)
```

**Parameters**:
- `library_id` (required): Context7-compatible library ID for your main/primary library
- `context` (required): Detailed context about what you're trying to accomplish - provide comprehensive details about your project, requirements, and specific implementation needs
- `tokens` (optional): Max tokens to retrieve per library (default: 200,000)
- `version` (optional): Specific version for main library (e.g., "v14.3.0-canary.87")
- `model` (optional): AI model to use for enhancement. Options:
  - **Gemini Models**: `gemini-2.5-pro`, `gemini-2.5-flash`, `gemini-2.5-flash-lite`
  - **OpenAI Models**: `gpt-4.1`, `gpt-4.1-mini`, `gpt-4.1-nano`
  - **Anthropic Models**: `claude-sonnet-4-20250514` with 1M token context (beta)
  - If not specified, uses fallback (Gemini 2.5 Flash → GPT-4.1 → Sonnet 4 1M)
- `extra_libraries` (optional): **ONLY use when you need help with multiple libraries together.** List of up to 2 additional library IDs. Don't use this for single library questions.

## Example Workflows

### 1. Find and Learn Next.js Routing

```
# Step 1: Find Next.js
resolve_library_id(query="next.js")

# Step 2: Get smart routing docs
get_smart_docs(
    library_id="vercel/next.js",
    context="I want to create dynamic blog post pages with Next.js, including slug-based routing, metadata generation, and static generation for better performance",
    model="claude-sonnet-4-20250514"
)
```

### 2. Learn Supabase Authentication

```
# Step 1: Find Supabase
resolve_library_id(query="supabase")

# Step 2: Get authentication docs
get_smart_docs(
    library_id="supabase/supabase",
    context="implementing user login and signup with Supabase Auth, including social providers, email verification, password reset, and role-based access control",
    model="gpt-4.1-mini"
)
```

### 3. MongoDB Database Operations

```
# Step 1: Find MongoDB docs
resolve_library_id(query="mongodb")

# Step 2: Get enhanced docs
get_smart_docs(
    library_id="mongodb/docs",
    context="setting up CRUD operations for a user management system with MongoDB, including schema design, indexing strategies, validation, and error handling",
    model="gemini-2.5-pro"
)
```

### When to Use Multi-Library Integration

**Use `extra_libraries` only when you need help integrating multiple technologies together in one project.**

**❌ Don't use extra_libraries for:**
- Learning just one library (use single library approach)
- Comparing different options (ask separate questions)
- General research

**✅ Do use extra_libraries when:**
- Building full-stack applications with multiple technologies
- Need specific integration patterns between libraries
- Want to see how libraries work together in practice

```
# Perfect example: Building an app that uses multiple libraries together
get_smart_docs(
    library_id="vercel/next.js",
    context="building a complete e-commerce application with Next.js frontend, Supabase backend and auth, and Tailwind for styling - need integration examples showing how these work together",
    extra_libraries=["supabase/supabase", "tailwindlabs/tailwindcss"]
)
```

## Configuration

### Environment Variables

- `GEMINI_API_KEY`: Your Google Gemini API key (optional, but recommended)
- `OPENAI_API_KEY`: Your OpenAI API key (optional, but recommended)

**Note**: At least one API key is required for ContextS to function.

### Model Selection Strategy

When multiple APIs are configured, ContextS uses this priority:

1. **Manual Selection**: If you specify a `model` parameter, it uses that model
2. **Automatic Fallback**: If the requested model's API isn't available, it falls back to the other provider
3. **Default Priority**: Gemini 2.5 Flash → GPT-4.1
4. **Error Handling**: If no AI service is available, returns raw documentation with an error message

### Custom Configuration

You can modify `main.py` to:
- Change default model preferences in `_determine_ai_model()`
- Adjust AI generation parameters (temperature, max_tokens, etc.)
- Modify the enhancement prompts
- Add custom processing logic
- Configure model-specific settings

## How the AI Enhancement Works

When you request documentation, ContextS:

1. **Fetches** raw documentation from Context7 API
2. **Selects** the optimal AI model (Gemini or OpenAI)
3. **Analyzes** the content using your chosen or default model
4. **Generates** practical code examples
5. **Provides** step-by-step guidance
6. **Focuses** on your specific use case and context

The AI enhancement includes:
- Key concept summaries
- Quick start examples
- Advanced usage patterns
- Best practices and tips
- Complete enhanced documentation

## API Reference

### Context7 Endpoints Used

- `GET /api/v1/search?query={query}` - Search libraries
- `GET /api/v1/{library_id}?type=txt&tokens={tokens}` - Get docs

### Library ID Format

Library IDs follow the pattern: `{org}/{project}` or `{org}/{project}/{version}`

Examples:
- `vercel/next.js`
- `mongodb/docs`
- `supabase/supabase`
- `vercel/next.js/v14.3.0-canary.87`

## Troubleshooting

### Common Issues

1. **"Library not found" error**
   - Use `resolve_library_id` to find the correct ID
   - Check spelling and formatting

2. **Server won't start**
   - Verify at least one API key (`GEMINI_API_KEY` or `OPENAI_API_KEY`) is set correctly
   - Check your API quotas and billing
   - Ensure the API keys have proper permissions

3. **Timeout errors**
   - Try reducing the `tokens` parameter
   - Check your internet connection

4. **MCP server not starting**
   - Verify Python path in configuration
   - Check all dependencies are installed
   - Review MCP client logs

### Debug Mode

To enable debug logging, modify the logging level in `main.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

Contributions are welcome! Areas for improvement:

- Additional AI models support
- Better error handling
- Caching for faster responses
- Custom prompt templates
- Integration with more documentation sources

## License

Shield: [![CC BY 4.0][cc-by-shield]][cc-by]

This work is licensed under a
[Creative Commons Attribution 4.0 International License][cc-by].

[![CC BY 4.0][cc-by-image]][cc-by]

[cc-by]: http://creativecommons.org/licenses/by/4.0/
[cc-by-image]: https://i.creativecommons.org/l/by/4.0/88x31.png
[cc-by-shield]: https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg

## Acknowledgments

- **Context7** for providing the excellent documentation API
- **Google Gemini** for powerful AI capabilities
- **OpenAI** for advanced language model capabilities
- **MCP** for the Model Context Protocol standard

---

**ContextS** - An AI to help your AI. Making documentation smarter, one query at a time.
