#!/bin/bash
# ContextS MCP Server Installation Script

echo "🚀 Installing ContextS MCP Server..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.8+ and try again."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "❌ Python 3.8+ is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python $python_version detected"

# Install pip if not available
if ! command -v pip3 &> /dev/null; then
    echo "📦 Installing pip..."
    python3 -m ensurepip --upgrade
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Failed to install dependencies. Please check the error messages above."
    exit 1
fi

echo ""
echo "🎉 ContextS MCP Server installation complete!"
echo ""
echo "📝 Next steps:"
echo "1. Get a Gemini API key from https://aistudio.google.com/app/apikey"
echo "2. Set your API key: export GEMINI_API_KEY='your-api-key-here'"
echo "3. Configure your MCP client (see README.md for details)"
echo "4. Start using ContextS with smart documentation!"
echo ""
echo "📚 For detailed setup instructions, see README.md"
echo "🚀 Happy coding with smart docs!"