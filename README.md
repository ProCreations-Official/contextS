<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=22&duration=5000&pause=2000&color=6fa8dc&center=true&vCenter=true&width=600&lines=ContextS.+Let+AI+experts+help+your+AI." alt="Typing SVG" />

# ContextS - Smart Documentation MCP Server

*An AI to help your AI*

</div>

**ContextS** is an intelligent MCP (Model Context Protocol) server that enhances Context7 with AI-powered code examples and guidance. The "S" stands for **Smart** - it supports Google Gemini API, OpenAI API, and Anthropic Claude API models to provide targeted, practical documentation with working code examples tailored to your specific needs.

## Features

- **Smart Documentation**: AI-enhanced docs with practical code examples tailored to your project
- **Multi AI Support**: Choose between Google Gemini, OpenAI models, and Anthropic Sonnet 4 (1m)
- **Flexible AI Providers**: Use powerful models via API keys (Gemini, OpenAI, Anthropic) or through locally installed command-line tools (`gemini`, `claude`, `codex`).
- **Intelligent Fallback**: Automatically cascades through available AI providers, from SDKs to CLIs, to ensure maximum uptime.
- **Easy Configuration**: A simple command-line interface to set up API keys and check status.
- **Command-Line Interface**: Manage the server and configuration with easy `contextS` commands.
- **MCP Compatible**: Works with Claude Desktop, Cursor, and other MCP clients.
- **Library Search**: Find the right library IDs for any package.
- **Version-Specific Docs**: Get documentation for specific library versions.
- **Context-Aware**: Provide project details to get highly relevant examples.
- **Up-to-Date Content**: Powered by Context7's real-time documentation database.
- **Multi-Library Support**: Optional integration examples from multiple libraries.

## Requirements

- Python 3.8+
- **Optional**: API keys for Google Gemini, OpenAI, and/or Anthropic.
- **Optional**: `gemini`, `claude`, and/or `codex` CLIs installed on your system.
- An MCP-compatible client (Claude Desktop, Cursor, etc.) to use the AI tools.

*ContextS requires at least one configured AI provider to function, either an API key or a detected CLI tool.*

### AI Provider Support

ContextS can use AI models from a variety of sources.

#### 1. API Providers (Recommended)
- **Google Gemini**: `gemini-2.5-pro`, `gemini-2.5-flash`, `gemini-2.5-flash-lite`
- **OpenAI**: `gpt-4.1`, `gpt-4.1-mini`, `gpt-4.1-nano`
- **Anthropic**: `claude-sonnet-4-20250514`

#### 2. CLI Providers (Fallback)
If API keys are not configured or if API calls fail, ContextS can fall back to using these command-line tools if they are installed on your system:
- **Google Gemini CLI**: The `gemini` command.
- **Anthropic Claude Code CLI**: The `claude` command.
- **OpenAI Codex CLI**: The `codex` command.

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/ProCreations-Official/contextS.git
cd contextS
```

### Step 2: Install Dependencies and the `contextS` Command

This command installs all required Python packages and makes the `contextS` command available in your shell.

```bash
pip install .
```

### Step 3: Configure AI Providers

You have two options for configuring AI providers. You can use either or both.

#### Option A: Interactive Setup (Recommended)

Run the interactive setup command. It will prompt you for your API keys and save them to a local configuration file.

```bash
contextS setup
```

This will store your keys in `~/.config/contextS/keys.env`.

#### Option B: Install CLI Tools

If you have the `gemini`, `claude`, or `codex` CLIs installed, ContextS will automatically detect and use them as fallbacks.

#### Option C: Manual Environment Variables

You can still set environment variables manually if you prefer:
```bash
export GEMINI_API_KEY="your-gemini-api-key-here"
export OPENAI_API_KEY="your-openai-api-key-here"
export ANTHROPIC_API_KEY="your-anthropic-api-key-here"
```

## Usage

ContextS is now a command-line tool.

### Checking Status

To see which API keys and CLI tools are configured correctly, run:
```bash
contextS status
```

### Running the MCP Server

To start the server so you can connect your MCP client (like Claude Desktop or Cursor), run:
```bash
contextS server
```
This is the default command, so you can also just run `contextS`.

### Configuring Your MCP Client

In your MCP client, you now point to the installed `contextS` command.

**Example for Claude Desktop (`claude_desktop_config.json`):**
```json
{
  "mcpServers": {
    "contexts": {
      "command": "contextS",
      "args": ["server"]
    }
  }
}
```
*Note: You no longer need to pass environment variables here if you used `contextS setup`.*

### Using the AI Tools

Once the server is running and your client is connected, you can use the `resolve_library_id` and `get_smart_docs` tools as before.

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

ContextS can be configured in multiple ways, which are loaded in the following order of precedence:

1.  **Environment Variables**: `GEMINI_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`.
2.  **Configuration File**: A file located at `~/.config/contextS/keys.env`, managed automatically by the `contextS setup` command.

### Model Selection and Fallback Strategy

ContextS has a robust fallback mechanism to ensure high availability. When you make a request to `get_smart_docs`:

1.  **Manual Model Selection**: If you specify a `model` (e.g., `model="gpt-4.1-nano"`), ContextS will attempt to use that specific model.

2.  **Primary Provider (API Keys)**: If no model is specified, or if the selected model is not available, ContextS will try to use the best available model from your configured API keys. The default priority is: Gemini → OpenAI → Anthropic.

3.  **CLI Fallback**: If all configured API key providers fail, or if you have no API keys configured, ContextS will automatically fall back to using locally installed CLI tools in the following order:
    1.  `gemini` CLI
    2.  `claude` CLI
    3.  `codex` CLI

4.  **Error**: If all API and CLI providers are unavailable or fail, the request will return the raw, un-enhanced documentation with an error message.

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

- Additional AI models support (we look for models with 400k+ context length, and good instruction following)
- Better error handling
- Caching for faster responses
- Custom prompt templates
- Integration with more documentation sources
- And more!

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
- **Anthropic** for the great, ethical models
- **OpenAI** for advanced language model capabilities
- **MCP** for the Model Context Protocol standard

---

**ContextS** - An AI to help your AI. Making documentation smarter, one query at a time.
