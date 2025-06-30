# CodeSnippetBank CLI Guide

## 🚀 Installation

### Quick Install
```bash
# Clone repository
git clone https://github.com/codebase/codebank.git
cd codebank

# Run installer
./install.sh
```

### Manual Install
```bash
# Install with pip
pip install -e .

# Or install globally
sudo pip install .
```

### Verify Installation
```bash
tissue --help
```

## 📋 Commands Overview

The CodeSnippetBank CLI provides the following commands:

| Command | Description | Example |
|---------|-------------|---------|
| `search` | Search for tissues | `tissue search "edge detection"` |
| `info` | Show tissue details | `tissue info CV-TISSUE-001` |
| `test` | Test a tissue | `tissue test CV-TISSUE-001 --device esp32` |
| `pack` | Create deployment pack | `tissue pack CV-001 CV-005 --device rpi` |
| `recommend` | Get recommendations | `tissue recommend "face blur"` |
| `update` | Update tissues | `tissue update --risk low` |
| `stats` | Show statistics | `tissue stats` |
| `config` | Configure CLI | `tissue config default_device rpi4` |

## 🔍 Searching for Tissues

### Basic Search
```bash
# Search by keyword
tissue search "face detection"

# Search in specific domain
tissue search "detection" --domain cv

# Search with tags
tissue search "edge" --tags fast lightweight

# Limit results
tissue search "ml" --limit 5
```

### Advanced Search Examples
```bash
# Find all computer vision edge detection tissues
tissue search "edge" --domain cv --tags detection

# Find NLP tissues for mobile devices
tissue search "text" --domain nlp --tags mobile lightweight

# Find machine learning tissues with low memory usage
tissue search "classify" --domain ml --tags low-memory
```

## 📄 Viewing Tissue Information

### Basic Info
```bash
# Show tissue details
tissue info CV-TISSUE-001
```

### Output includes:
- Basic metadata (name, domain, version)
- Quality metrics (performance, memory, edge compatibility)
- Performance benchmarks on different devices
- Dependencies
- Usage examples
- Recent version history

### Example Output:
```
📄 Tissue Details: CV-TISSUE-001
============================================================

📋 Basic Information:
   Name: Edge Detector Sobel
   Domain: cv
   Category: edge_detection
   Version: 1.2.0
   Tags: edge, detection, sobel, gradient

⭐ Quality Metrics:
   Overall Score: 0.92
   Performance: 0.95
   Memory: 0.90
   Edge Compatibility: 0.88

📊 Performance Benchmarks:
   ESP32:
     • Time: 25ms for 320x240
     • Memory: 150KB
   Raspberry Pi 4:
     • Time: 2ms for 640x480
     • Memory: 5MB

📦 Dependencies: numpy

💡 Usage Example:
   ```python
   edges = detect_edges_sobel(image, threshold=0.5)
   cv2.imshow('Edges', edges['edges'])
   ```

🔄 Recent Updates:
   v1.2.0 - 2024-01-15 - Added ESP32 optimization
   v1.1.0 - 2024-01-01 - Improved memory efficiency
   v1.0.0 - 2023-12-15 - Initial release
```

## 🧪 Testing Tissues

### Basic Test
```bash
# Test with default device
tissue test CV-TISSUE-001

# Test on specific device
tissue test CV-TISSUE-001 --device esp32
tissue test NLP-TISSUE-009 --device mobile
```

### Test Output:
```
🧪 Testing tissue: CV-TISSUE-001
📱 Device profile: raspberry_pi_4

🏃 Running test...
✅ Test passed!
   ⏱️  Duration: 2.34ms
   💾 Memory: 4.2MB
```

## 📦 Creating Deployment Packs

### Basic Pack Creation
```bash
# Create pack for Raspberry Pi
tissue pack CV-TISSUE-001 CV-TISSUE-005 --device raspberry_pi

# Create pack with custom output name
tissue pack NLP-TISSUE-001 NLP-TISSUE-009 --device mobile --output my_nlp_pack.zip

# Create pack without optimization (larger but faster)
tissue pack ML-TISSUE-001 --device edge_server --no-optimize
```

### Multi-Tissue Packs
```bash
# Pack entire domain
tissue pack CV-TISSUE-001 CV-TISSUE-002 CV-TISSUE-003 CV-TISSUE-004 CV-TISSUE-005 \
    --device esp32 --output esp32_cv_pack.zip

# Pack mixed domains
tissue pack CV-TISSUE-001 NLP-TISSUE-001 ML-TISSUE-001 \
    --device raspberry_pi --output multi_domain_pack.zip
```

## 🤖 Getting Recommendations

### Basic Recommendations
```bash
# Get recommendations for a task
tissue recommend "privacy camera"

# Specify target device
tissue recommend "real-time sentiment analysis" --device mobile

# Get more recommendations
tissue recommend "object detection" --limit 10
```

### Example Output:
```
🤖 Getting recommendations
   Task: privacy camera
   Device: raspberry_pi_4

💡 Recommended tissues:

1. CV-TISSUE-005 - Face Detector Haar
   📊 Score: 0.95
   💭 Reason: Fast face detection essential for privacy applications
   ⚡ raspberry_pi_4 performance: 8ms for 640x480

2. CV-TISSUE-003 - Gaussian Blur
   📊 Score: 0.92
   💭 Reason: Efficient blurring for privacy protection
   ⚡ raspberry_pi_4 performance: 3ms for 640x480

3. CV-TISSUE-015 - Motion Tracker
   📊 Score: 0.88
   💭 Reason: Detect motion to trigger face blurring
   ⚡ raspberry_pi_4 performance: 5ms for 640x480
```

## 🔄 Updating Tissues

### Check for Updates
```bash
# Update all tissues (auto mode)
tissue update

# Update specific tissues
tissue update CV-TISSUE-001 NLP-TISSUE-001

# Conservative update (low risk only)
tissue update --risk low

# Accept all updates including breaking changes
tissue update --risk high
```

### Update Process:
```
🔄 Checking for tissue updates...

📋 Updates available for 3 tissue(s):

• CV-TISSUE-001
  Current: v1.1.0 → Latest: v1.2.0
  Risk: low - Performance improvements only

• NLP-TISSUE-009
  Current: v2.0.0 → Latest: v2.1.0
  Risk: medium - New optional parameters

• ML-TISSUE-005
  Current: v1.0.0 → Latest: v2.0.0
  Risk: high - Breaking API changes

🚀 Auto-updating tissues with medium risk or lower...

📦 Updating CV-TISSUE-001...
✅ Updated to v1.2.0

📦 Updating NLP-TISSUE-009...
✅ Updated to v2.1.0
```

## 📊 Viewing Statistics

```bash
tissue stats
```

Output:
```
📊 CodeSnippetBank Statistics
============================================================

🧬 Tissue Library:
   Total tissues: 40
   By domain:
     • cv: 20
     • nlp: 10
     • ml: 10

📈 Usage Stats:
   Total accesses: 15,234
   Average quality: 0.91

🔥 Most Popular:
   1. CV-TISSUE-005 (2,341 uses)
   2. NLP-TISSUE-009 (1,892 uses)
   3. ML-TISSUE-001 (1,455 uses)
   4. CV-TISSUE-001 (1,232 uses)
   5. NLP-TISSUE-001 (1,098 uses)

⭐ Highest Quality:
   1. CV-TISSUE-010 (score: 0.98)
   2. ML-TISSUE-008 (score: 0.97)
   3. NLP-TISSUE-006 (score: 0.96)
   4. CV-TISSUE-005 (score: 0.95)
   5. ML-TISSUE-003 (score: 0.94)
```

## ⚙️ Configuration

### View Configuration
```bash
# Show all settings
tissue config

# Show specific setting
tissue config default_device
```

### Update Configuration
```bash
# Set default device
tissue config default_device raspberry_pi_4

# Set output directory
tissue config output_dir ~/my_tissues

# Enable/disable auto-update
tissue config auto_update true

# Set quality threshold
tissue config quality_threshold 0.85
```

### Configuration File
The configuration is stored in `~/.codebank/config.json`:

```json
{
  "default_device": "raspberry_pi_4",
  "output_dir": "/home/user/tissues",
  "auto_update": true,
  "quality_threshold": 0.8
}
```

## 🔧 Advanced Usage

### Batch Operations
```bash
# Test multiple tissues
for tissue in CV-TISSUE-001 CV-TISSUE-002 CV-TISSUE-003; do
    tissue test $tissue --device esp32
done

# Create device-specific packs
for device in esp32 raspberry_pi mobile; do
    tissue pack CV-TISSUE-001 CV-TISSUE-005 --device $device
done
```

### Integration with Scripts
```python
#!/usr/bin/env python3
import subprocess
import json

# Search for tissues programmatically
result = subprocess.run(
    ['tissue', 'search', 'face', '--limit', '5', '--json'],
    capture_output=True,
    text=True
)
tissues = json.loads(result.stdout)

# Test each tissue
for tissue in tissues:
    subprocess.run(['tissue', 'test', tissue['id']])
```

### CI/CD Integration
```yaml
# .github/workflows/tissue-test.yml
name: Test Tissues

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Install CodeSnippetBank
      run: ./install.sh
    
    - name: Test all tissues
      run: |
        for tissue in tissues/*/*.py; do
          tissue_id=$(basename $tissue .py)
          tissue test $tissue_id
        done
    
    - name: Create deployment packs
      run: |
        tissue pack CV-TISSUE-001 CV-TISSUE-005 --device raspberry_pi
        tissue pack NLP-TISSUE-001 NLP-TISSUE-009 --device mobile
```

## 🚀 Tips & Tricks

1. **Use aliases for common operations:**
   ```bash
   alias ts='tissue search'
   alias ti='tissue info'
   alias tt='tissue test'
   alias tp='tissue pack'
   ```

2. **Create project-specific tissue lists:**
   ```bash
   # Save tissue list
   echo "CV-TISSUE-001 CV-TISSUE-005 NLP-TISSUE-009" > .tissues
   
   # Create pack from list
   tissue pack $(cat .tissues) --device raspberry_pi
   ```

3. **Test before deployment:**
   ```bash
   # Test and pack in one command
   tissue test CV-TISSUE-001 && tissue pack CV-TISSUE-001 --device esp32
   ```

4. **Monitor tissue quality:**
   ```bash
   # Check quality before using
   tissue info CV-TISSUE-001 | grep "Overall Score"
   ```

## ❓ Troubleshooting

### Common Issues

**Issue: "Tissue not found"**
```bash
# Update local index
tissue update-index

# Search with broader terms
tissue search "detect" --domain cv
```

**Issue: "Test failed on device"**
```bash
# Check device constraints
tissue info TISSUE-ID | grep -A5 "Performance Benchmarks"

# Try with different device profile
tissue test TISSUE-ID --device raspberry_pi
```

**Issue: "Pack too large"**
```bash
# Use optimization
tissue pack TISSUES --device esp32 --optimize

# Create minimal pack
tissue pack TISSUE --device esp32 --minimal
```

## 📚 Additional Resources

- [Tissue Creation Guide](TISSUE_CREATION_GUIDE.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [API Documentation](../api/API_DOCUMENTATION.md)
- [Architecture Overview](ARCHITECTURE.md)

---

*Happy tissue hunting! 🧬*