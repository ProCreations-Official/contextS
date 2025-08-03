# ContextS - Smart Documentation MCP Server

**ContextS** is an intelligent MCP (Model Context Protocol) server that enhances Context7 with AI-powered code examples and guidance. The "S" stands for **Smart** - it leverages Gemini 2.5 Flash to provide targeted, practical documentation with working code examples.

## 🚀 Features

- **Smart Documentation**: AI-enhanced docs with practical code examples
- **Library Search**: Find the right library IDs for any package
- **Version-Specific Docs**: Get documentation for specific library versions
- **Topic Filtering**: Focus on specific areas like routing, authentication, etc.
- **Up-to-Date Content**: Powered by Context7's real-time documentation database
- **MCP Compatible**: Works with Claude Desktop, Cursor, and other MCP clients

## 📋 Requirements

- Python 3.8+
- Gemini API key (required - ContextS requires AI enhancement to function)
- MCP-compatible client (Claude Desktop, Cursor, etc.)

> **Note**: Currently, ContextS uses Google Gemini as the AI provider. While Gemini is the only supported AI model for now, we will be adding support for more AI providers very soon!
## 🛠️ Installation

### Step 1: Clone and Setup

```bash
# Clone the ContextS repository
git clone https://github.com/ProCreations-Official/contextS.git
cd contextS

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Get Gemini API Key (Required)

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Set the environment variable:

```bash
export GEMINI_API_KEY="your-api-key-here"
```

**Note**: ContextS requires a Gemini API key to function. The server will not start without it as AI enhancement is core to its functionality.

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
        "GEMINI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

#### For Cursor IDE

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "contexts": {
      "command": "python3",
      "args": ["/path/to/ContextS/main.py"],
      "env": {
        "GEMINI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

#### For Other MCP Clients

Follow your client's MCP server configuration documentation, using:
- **Command**: `python3`
- **Args**: `["/path/to/ContextS/main.py"]`
- **Environment**: `{"GEMINI_API_KEY": "your-api-key-here"}`

## 🎯 Usage

ContextS provides two main tools:

### 1. `resolve_library_id` - Search for Libraries

Find the correct library ID for any package:

```
resolve_library_id(query="next.js")
```

**Returns**: A list of matching libraries with their Context7-compatible IDs.

### 2. `get_smart_docs` - Get AI-Enhanced Documentation

Get smart documentation with practical examples:

```
get_smart_docs(
    library_id="vercel/next.js",
    topic="routing", 
    context="building a blog with dynamic routes using Next.js 14, need comprehensive examples with file-based routing, dynamic segments, and SEO optimization"
)
```

**Parameters**:
- `library_id` (required): Context7-compatible library ID
- `topic` (optional): Focus area (e.g., "routing", "authentication")
- `tokens` (optional): Max tokens to retrieve (default: 200,000)
- `version` (optional): Specific version (e.g., "v14.3.0-canary.87")
- `context` (optional): Detailed context about what you're trying to accomplish - provide comprehensive details about your project, requirements, and specific implementation needs to get the best code examples and explanations

## 💡 Example Workflows

### 1. Find and Learn Next.js Routing

```
# Step 1: Find Next.js
resolve_library_id(query="next.js")

# Step 2: Get smart routing docs
get_smart_docs(
    library_id="vercel/next.js",
    topic="routing",
    context="I want to create dynamic blog post pages with Next.js, including slug-based routing, metadata generation, and static generation for better performance"
)
```

### 2. Learn Supabase Authentication

```
# Step 1: Find Supabase
resolve_library_id(query="supabase")

# Step 2: Get authentication docs
get_smart_docs(
    library_id="supabase/supabase",
    topic="authentication",
    context="implementing user login and signup with Supabase Auth, including social providers, email verification, password reset, and role-based access control"
)
```

### 3. MongoDB Database Operations

```
# Step 1: Find MongoDB docs
resolve_library_id(query="mongodb")

# Step 2: Get enhanced docs
get_smart_docs(
    library_id="mongodb/docs",
    context="setting up CRUD operations for a user management system with MongoDB, including schema design, indexing strategies, validation, and error handling"
)
```

## 🔧 Configuration

### Environment Variables

- `GEMINI_API_KEY`: Your Google Gemini API key (required)

### Custom Configuration

You can modify `main.py` to:
- Change the Gemini model (currently using `gemini-2.5-flash`)
- Adjust AI generation parameters (temperature, top_p, etc.)
- Modify the enhancement prompts
- Add custom processing logic

## 🤖 How the AI Enhancement Works

When you request documentation, ContextS:

1. **Fetches** raw documentation from Context7 API
2. **Analyzes** the content using Gemini 2.5 Flash
3. **Generates** practical code examples
4. **Provides** step-by-step guidance
5. **Focuses** on your specific use case and context

The AI enhancement includes:
- Key concept summaries
- Quick start examples
- Advanced usage patterns
- Best practices and tips
- Complete enhanced documentation

## 📚 API Reference

### Context7 Endpoints Used

- `GET /api/v1/search?query={query}` - Search libraries
- `GET /api/v1/{library_id}?type=txt&tokens={tokens}&topic={topic}` - Get docs

### Library ID Format

Library IDs follow the pattern: `{org}/{project}` or `{org}/{project}/{version}`

Examples:
- `vercel/next.js`
- `mongodb/docs`
- `supabase/supabase`
- `vercel/next.js/v14.3.0-canary.87`

## 🚨 Troubleshooting

### Common Issues

1. **"Library not found" error**
   - Use `resolve_library_id` to find the correct ID
   - Check spelling and formatting

2. **Server won't start**
   - Verify `GEMINI_API_KEY` is set correctly
   - Check your Gemini API quota
   - Ensure the API key has proper permissions

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

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Additional AI models support
- Better error handling
- Caching for faster responses
- Custom prompt templates
- Integration with more documentation sources

## 📄 License

MIT License - feel free to use and modify as needed.

## 🙏 Acknowledgments

- **Context7** for providing the excellent documentation API
- **Google Gemini** for powerful AI capabilities
- **MCP** for the Model Context Protocol standard

---

**ContextS** - Making documentation smarter, one query at a time! 🧠✨