#!/bin/bash
# CodeSnippetBank Installation Script

echo "🚀 Installing CodeSnippetBank CLI..."
echo "=================================="

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.6"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then 
    echo "❌ Error: Python $required_version or higher is required (found $python_version)"
    exit 1
fi

echo "✅ Python $python_version detected"

# Create virtual environment (optional)
read -p "Create virtual environment? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Install package
echo "📦 Installing CodeSnippetBank..."
pip install -e .

# Create config directory
mkdir -p ~/.codebank
echo "✅ Created config directory: ~/.codebank"

# Download sample tissues (optional)
read -p "Download sample tissue pack? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📥 Downloading sample tissues..."
    mkdir -p ~/.codebank/tissues
    # In real implementation, would download from CDN
    cp -r tissues/* ~/.codebank/tissues/
    echo "✅ Sample tissues installed"
fi

# Test installation
echo -e "\n🧪 Testing installation..."
tissue --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Installation successful!"
    echo ""
    echo "🎉 CodeSnippetBank CLI is ready to use!"
    echo ""
    echo "Quick start:"
    echo "  tissue search 'edge detection'      # Search for tissues"
    echo "  tissue info CV-TISSUE-001          # Show tissue details"
    echo "  tissue test CV-TISSUE-001          # Test a tissue"
    echo "  tissue pack CV-001 --device esp32  # Create deployment pack"
    echo ""
    echo "For more help: tissue --help"
else
    echo "❌ Installation failed. Please check the error messages above."
    exit 1
fi