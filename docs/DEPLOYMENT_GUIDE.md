# CodeSnippetBank Deployment Guide

## 🚀 Deploying Tissues to Edge Devices

This guide covers everything you need to know about deploying CodeSnippetBank tissues to various edge devices, from tiny ESP32 microcontrollers to powerful edge servers.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Device-Specific Guides](#device-specific-guides)
3. [Pack Generation](#pack-generation)
4. [Deployment Methods](#deployment-methods)
5. [Runtime Configuration](#runtime-configuration)
6. [Performance Optimization](#performance-optimization)
7. [Troubleshooting](#troubleshooting)

## 🏃 Quick Start

### 1. Identify Your Tissues
```bash
# Search for needed tissues
python -m codesnippetbank.api search "face detection"

# Get recommendations for your use case
python -m codesnippetbank.api recommend \
    --task "privacy camera" \
    --device "raspberry_pi"
```

### 2. Generate Device Pack
```bash
# Create optimized pack
python tools/offline_tissue_pack_generator.py \
    --device raspberry_pi \
    --tissues CV-TISSUE-005,CV-TISSUE-003 \
    --optimize \
    --output privacy_camera_pack.zip
```

### 3. Deploy to Device
```bash
# Copy to device
scp privacy_camera_pack.zip pi@raspberrypi:/home/pi/

# Install on device
ssh pi@raspberrypi
unzip privacy_camera_pack.zip -d /opt/tissues/
python /opt/tissues/runtime/install.py
```

### 4. Use in Your Application
```python
from tissue_loader import TissueLoader

# Load tissues
loader = TissueLoader("/opt/tissues")
detect_faces = loader.get_tissue_function("CV-TISSUE-005")
blur_regions = loader.get_tissue_function("CV-TISSUE-003")

# Use in your app
faces = detect_faces(image)
result = blur_regions(image, faces['boxes'])
```

## 📱 Device-Specific Guides

### ESP32 Deployment

**Device Constraints:**
- RAM: 520KB (320KB available)
- Flash: 4MB
- CPU: 240MHz dual-core
- No OS filesystem

**Deployment Steps:**

1. **Generate Mini Pack**
```bash
python tools/offline_tissue_pack_generator.py \
    --device esp32 \
    --tissues CV-TISSUE-001 \
    --max-size 50 \
    --output esp32_mini.pack
```

2. **Flash to Device**
```python
# convert_to_esp32.py
import micropython
import ubinascii

# Convert pack to MicroPython format
with open('esp32_mini.pack', 'rb') as f:
    pack_data = f.read()
    
# Generate frozen modules
with open('frozen_tissues.py', 'w') as f:
    f.write(f"TISSUE_DATA = {repr(pack_data)}")
```

3. **Use in MicroPython**
```python
# main.py on ESP32
from frozen_tissues import TISSUE_DATA
import ujson

# Simple tissue loader for ESP32
class MiniTissueLoader:
    def __init__(self):
        self.tissues = ujson.loads(TISSUE_DATA)
    
    def run_tissue(self, tissue_id, data):
        code = self.tissues[tissue_id]['code']
        exec(code)
        return locals()['process'](data)

# Use tissue
loader = MiniTissueLoader()
result = loader.run_tissue('CV-TISSUE-001', sensor_data)
```

### Raspberry Pi Deployment

**Device Variants:**
- Pi Zero W: 512MB RAM, 1GHz single-core
- Pi 3B+: 1GB RAM, 1.4GHz quad-core
- Pi 4: 2-8GB RAM, 1.5GHz quad-core

**Optimized Deployment:**

1. **System Preparation**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install minimal dependencies
sudo apt install python3-numpy python3-pip -y

# Configure for performance
echo "gpu_mem=128" | sudo tee -a /boot/config.txt
```

2. **Install Tissue Runtime**
```bash
# Download runtime
wget https://codebank.ai/runtime/rpi-runtime.tar.gz
tar -xzf rpi-runtime.tar.gz

# Install
cd rpi-runtime
sudo python3 install.py --device rpi4 --optimize
```

3. **Deploy Application**
```python
# app.py
from tissue_runtime import TissueRuntime
import picamera2

# Initialize optimized runtime
runtime = TissueRuntime(
    device_profile='rpi4',
    cache_size=50,  # MB
    enable_gpu=True
)

# Load tissues
face_detector = runtime.load_tissue('CV-TISSUE-005')
motion_tracker = runtime.load_tissue('CV-TISSUE-015')

# Camera processing loop
with picamera2.Picamera2() as camera:
    camera.configure(camera.create_preview_configuration(
        main={"size": (640, 480), "format": "RGB888"}
    ))
    camera.start()
    
    while True:
        frame = camera.capture_array()
        
        # Process with tissues
        faces = face_detector.process(frame)
        motion = motion_tracker.process(frame)
        
        # Your application logic
        if faces['count'] > 0 or motion['detected']:
            handle_event(frame, faces, motion)
```

### Mobile Deployment (Android/iOS)

**Deployment via React Native:**

1. **Generate Mobile Pack**
```bash
python tools/offline_tissue_pack_generator.py \
    --device mobile \
    --tissues NLP-TISSUE-009,NLP-TISSUE-001 \
    --format js \
    --output mobile_nlp.pack
```

2. **React Native Integration**
```javascript
// TissueLoader.js
import { NativeModules } from 'react-native';
const { TissueRuntime } = NativeModules;

export class TissueLoader {
  async loadPack(packPath) {
    return await TissueRuntime.loadPack(packPath);
  }
  
  async runTissue(tissueId, input) {
    const startTime = Date.now();
    const result = await TissueRuntime.execute(tissueId, input);
    result.executionTime = Date.now() - startTime;
    return result;
  }
}

// App.js
import { TissueLoader } from './TissueLoader';

const loader = new TissueLoader();
await loader.loadPack('mobile_nlp.pack');

// Sentiment analysis
const sentiment = await loader.runTissue('NLP-TISSUE-009', {
  text: userInput,
  language: 'en'
});
```

### Edge Server Deployment

**For Jetson Nano/Xavier:**

1. **GPU-Optimized Pack**
```bash
python tools/offline_tissue_pack_generator.py \
    --device jetson_nano \
    --tissues CV-TISSUE-001,CV-TISSUE-005,CV-TISSUE-010 \
    --enable-gpu \
    --optimize-tensorrt \
    --output jetson_cv_pack.zip
```

2. **Docker Deployment**
```dockerfile
# Dockerfile
FROM nvcr.io/nvidia/l4t-ml:r32.6.1-py3

# Install tissue runtime
COPY tissue_runtime /opt/tissue_runtime
WORKDIR /opt/tissue_runtime
RUN pip3 install -r requirements.txt

# Copy tissue pack
COPY jetson_cv_pack.zip /opt/tissues/
RUN cd /opt/tissues && unzip jetson_cv_pack.zip

# Configure for Jetson
ENV TISSUE_DEVICE_PROFILE=jetson_nano
ENV TISSUE_ENABLE_GPU=1
ENV TISSUE_CACHE_SIZE=500

# Run application
CMD ["python3", "tissue_server.py"]
```

## 📦 Pack Generation

### Basic Pack Generation
```bash
# Simple pack with default optimization
python tools/offline_tissue_pack_generator.py \
    --tissues CV-TISSUE-001,CV-TISSUE-002 \
    --output basic_pack.zip
```

### Advanced Pack Options
```bash
# Full-featured pack generation
python tools/offline_tissue_pack_generator.py \
    --device raspberry_pi \
    --tissues CV-TISSUE-001,CV-TISSUE-005,NLP-TISSUE-009 \
    --domains ml \  # Include entire ML domain
    --optimize \
    --compression-level 9 \
    --remove-docs \
    --remove-tests \
    --inline-constants \
    --max-size 10 \  # MB
    --output advanced_pack.zip
```

### Multi-Device Pack
```bash
# Create pack that adapts to multiple devices
python tools/offline_tissue_pack_generator.py \
    --devices esp32,rpi_zero,rpi4 \
    --tissues CORE-TISSUE-SET-1 \
    --adaptive \
    --output universal_pack.zip
```

## 🔧 Deployment Methods

### 1. Direct File Copy
```bash
# Simple deployment
scp tissue_pack.zip user@device:/path/to/tissues/
ssh user@device "cd /path/to/tissues && unzip tissue_pack.zip"
```

### 2. OTA (Over-The-Air) Updates
```python
# ota_updater.py
import requests
import hashlib

class TissueOTAUpdater:
    def __init__(self, device_id, update_server):
        self.device_id = device_id
        self.update_server = update_server
        
    def check_updates(self):
        """Check for tissue updates"""
        response = requests.get(
            f"{self.update_server}/api/v1/updates/{self.device_id}"
        )
        return response.json()
    
    def download_update(self, update_info):
        """Download and verify update"""
        pack_url = update_info['pack_url']
        expected_hash = update_info['sha256']
        
        # Download pack
        response = requests.get(pack_url, stream=True)
        pack_data = response.content
        
        # Verify integrity
        actual_hash = hashlib.sha256(pack_data).hexdigest()
        if actual_hash != expected_hash:
            raise ValueError("Pack integrity check failed")
            
        return pack_data
    
    def apply_update(self, pack_data):
        """Apply tissue pack update"""
        # Backup current tissues
        backup_current_tissues()
        
        try:
            # Extract new pack
            extract_pack(pack_data, '/opt/tissues_new')
            
            # Validate new tissues
            if validate_tissues('/opt/tissues_new'):
                # Atomic swap
                os.rename('/opt/tissues', '/opt/tissues_old')
                os.rename('/opt/tissues_new', '/opt/tissues')
                
                # Cleanup
                shutil.rmtree('/opt/tissues_old')
                return True
        except Exception as e:
            # Rollback on failure
            restore_tissue_backup()
            raise e
```

### 3. Container Deployment
```yaml
# docker-compose.yml
version: '3.8'
services:
  tissue-runtime:
    image: codebank/tissue-runtime:latest
    volumes:
      - ./tissue_packs:/opt/tissues
      - ./app:/app
    environment:
      - TISSUE_DEVICE_PROFILE=edge_server
      - TISSUE_CACHE_SIZE=1000
    devices:
      - /dev/video0:/dev/video0  # Camera access
    restart: unless-stopped
```

### 4. Kubernetes Deployment
```yaml
# tissue-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tissue-worker
spec:
  replicas: 3
  selector:
    matchLabels:
      app: tissue-worker
  template:
    metadata:
      labels:
        app: tissue-worker
    spec:
      containers:
      - name: tissue-runtime
        image: codebank/tissue-runtime:edge
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "2000m"
        volumeMounts:
        - name: tissue-pack
          mountPath: /opt/tissues
      volumes:
      - name: tissue-pack
        configMap:
          name: tissue-pack-config
```

## ⚙️ Runtime Configuration

### Configuration File
```json
{
  "device_profile": "raspberry_pi_4",
  "tissue_path": "/opt/tissues",
  "cache": {
    "enabled": true,
    "size_mb": 100,
    "ttl_seconds": 3600
  },
  "performance": {
    "max_threads": 4,
    "enable_gpu": false,
    "memory_limit_mb": 500
  },
  "logging": {
    "level": "INFO",
    "file": "/var/log/tissue_runtime.log"
  },
  "monitoring": {
    "enabled": true,
    "metrics_port": 9090,
    "report_interval": 60
  }
}
```

### Environment Variables
```bash
# Basic configuration
export TISSUE_DEVICE_PROFILE=raspberry_pi_4
export TISSUE_ROOT=/opt/tissues
export TISSUE_CACHE_SIZE=100

# Performance tuning
export TISSUE_MAX_WORKERS=4
export TISSUE_MEMORY_LIMIT=500M
export TISSUE_GPU_ENABLED=false

# Monitoring
export TISSUE_METRICS_ENABLED=true
export TISSUE_METRICS_PORT=9090
```

## 🚀 Performance Optimization

### 1. Memory Optimization
```python
# Optimize for low-memory devices
runtime_config = {
    'esp32': {
        'preload_tissues': False,
        'lazy_loading': True,
        'gc_threshold': 0.8,
        'chunk_size': 1024
    },
    'rpi_zero': {
        'preload_tissues': ['CV-TISSUE-001'],  # Only critical
        'lazy_loading': True,
        'gc_threshold': 0.7,
        'chunk_size': 4096
    }
}
```

### 2. CPU Optimization
```python
# Adaptive threading based on device
import multiprocessing

def get_optimal_threads(device_profile):
    if device_profile == 'esp32':
        return 1  # Single thread only
    elif device_profile == 'rpi_zero':
        return 1
    elif device_profile == 'rpi4':
        return min(4, multiprocessing.cpu_count())
    else:
        return multiprocessing.cpu_count()
```

### 3. Startup Optimization
```python
# Fast startup for real-time applications
class FastTissueLoader:
    def __init__(self, priority_tissues):
        # Load critical tissues first
        self.priority_cache = {}
        for tissue_id in priority_tissues:
            self.priority_cache[tissue_id] = self._load_tissue(tissue_id)
        
        # Lazy load others
        self.lazy_load_queue = Queue()
        self.loader_thread = Thread(target=self._background_loader)
        self.loader_thread.start()
```

## 🔍 Monitoring & Debugging

### Performance Monitoring
```python
# tissue_monitor.py
class TissueMonitor:
    def __init__(self):
        self.metrics = {
            'execution_times': defaultdict(list),
            'memory_usage': defaultdict(list),
            'error_counts': defaultdict(int)
        }
    
    def record_execution(self, tissue_id, duration_ms, memory_mb):
        self.metrics['execution_times'][tissue_id].append(duration_ms)
        self.metrics['memory_usage'][tissue_id].append(memory_mb)
    
    def get_stats(self, tissue_id):
        times = self.metrics['execution_times'][tissue_id]
        memory = self.metrics['memory_usage'][tissue_id]
        
        return {
            'avg_time_ms': sum(times) / len(times) if times else 0,
            'max_time_ms': max(times) if times else 0,
            'avg_memory_mb': sum(memory) / len(memory) if memory else 0,
            'error_rate': self.metrics['error_counts'][tissue_id] / len(times)
        }
```

### Debug Mode
```bash
# Enable debug logging
export TISSUE_DEBUG=1
export TISSUE_LOG_LEVEL=DEBUG

# Run with profiling
python -m cProfile -s cumtime app.py

# Memory profiling
python -m memory_profiler app.py
```

## ❗ Troubleshooting

### Common Issues

**1. Import Errors**
```python
# Problem: numpy not available on ESP32
# Solution: Use micropython compatibility layer
try:
    import numpy as np
except ImportError:
    import mini_numpy as np  # Minimal implementation
```

**2. Memory Errors**
```python
# Problem: Out of memory on small devices
# Solution: Implement chunked processing
def process_large_image(image, chunk_size=1000):
    height, width = image.shape
    results = []
    
    for y in range(0, height, chunk_size):
        for x in range(0, width, chunk_size):
            chunk = image[y:y+chunk_size, x:x+chunk_size]
            results.append(process_chunk(chunk))
    
    return merge_results(results)
```

**3. Performance Issues**
```python
# Problem: Slow execution on edge device
# Solution: Use device-specific optimization
def adaptive_algorithm(data, device_profile):
    if device_profile in ['esp32', 'rpi_zero']:
        return fast_approximate_algorithm(data)
    else:
        return full_precision_algorithm(data)
```

### Debugging Tools

**1. Tissue Validator**
```bash
# Validate tissue pack before deployment
python tools/validate_pack.py tissue_pack.zip --device rpi4

# Output:
# ✓ Pack structure valid
# ✓ All tissues loadable
# ✓ Dependencies satisfied
# ✓ Memory requirements: 45MB (OK for rpi4)
# ✓ Performance requirements met
```

**2. Runtime Diagnostics**
```python
# diagnose.py
from tissue_runtime import diagnostics

# Run diagnostics
report = diagnostics.full_system_check()
print(f"Device: {report['device_profile']}")
print(f"Available RAM: {report['available_ram_mb']}MB")
print(f"Loaded tissues: {report['loaded_tissues']}")
print(f"Cache hit rate: {report['cache_hit_rate']:.1%}")
print(f"Average latency: {report['avg_latency_ms']}ms")
```

## 📋 Deployment Checklist

- [ ] Select appropriate tissues for your use case
- [ ] Choose correct device profile
- [ ] Generate optimized pack
- [ ] Test pack on target device
- [ ] Configure runtime parameters
- [ ] Set up monitoring
- [ ] Implement error handling
- [ ] Plan update strategy
- [ ] Document deployment process
- [ ] Create rollback procedure

## 🎯 Best Practices

1. **Start Small**: Deploy minimal tissue set first
2. **Test Thoroughly**: Validate on actual hardware
3. **Monitor Performance**: Track metrics in production
4. **Plan Updates**: Have OTA strategy ready
5. **Handle Failures**: Implement graceful degradation
6. **Optimize Gradually**: Profile before optimizing
7. **Document Everything**: Future you will thank you

---

*CodeSnippetBank: Deploy Once, Run Everywhere!* 🚀