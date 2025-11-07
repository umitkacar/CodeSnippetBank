# 🤖 AI & Machine Learning Snippets

<div align="center">

![AI Badge](https://img.shields.io/badge/AI-Ready-00D9FF?style=for-the-badge&logo=ai&logoColor=white)
![ML Badge](https://img.shields.io/badge/ML-Optimized-FF6B6B?style=for-the-badge&logo=tensorflow&logoColor=white)
![DL Badge](https://img.shields.io/badge/Deep_Learning-Advanced-4ECDC4?style=for-the-badge&logo=pytorch&logoColor=white)

</div>

## 🌟 2024-2025 Trending Technologies

### 🤖 Large Language Models (LLMs)

#### GPT-4 Integration

```python
from openai import OpenAI

class GPT4Wrapper:
    """Production-ready GPT-4 wrapper with streaming and error handling"""

    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def chat(self, messages: list, temperature: float = 0.7, stream: bool = False):
        """Send chat request with streaming support"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=stream
            )

            if stream:
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            else:
                return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"GPT-4 API Error: {str(e)}")

# Usage
llm = GPT4Wrapper(api_key="your-api-key")
response = llm.chat([
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain quantum computing in simple terms"}
])
print(response)
```

#### LLaMA Local Deployment

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class LLaMALocal:
    """Run LLaMA models locally with optimizations"""

    def __init__(self, model_name: str = "meta-llama/Llama-2-7b-chat-hf"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map="auto",
            load_in_8bit=True  # Quantization for efficiency
        )

    def generate(self, prompt: str, max_length: int = 512):
        """Generate text from prompt"""
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                temperature=0.7,
                top_p=0.9,
                do_sample=True
            )

        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

# Usage
llama = LLaMALocal()
result = llama.generate("Tell me about artificial intelligence")
```

#### Mistral Edge Optimization

```python
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

class MistralEdge:
    """Optimized Mistral for edge devices"""

    def __init__(self, api_key: str):
        self.client = MistralClient(api_key=api_key)
        self.model = "mistral-small-latest"  # Lightweight for edge

    async def chat_async(self, messages: list[dict]):
        """Async chat for better performance"""
        chat_messages = [ChatMessage(**msg) for msg in messages]

        response = await self.client.chat_async(
            model=self.model,
            messages=chat_messages,
            temperature=0.7,
            max_tokens=512
        )

        return response.choices[0].message.content

    def embed(self, texts: list[str]):
        """Generate embeddings for RAG applications"""
        embeddings = self.client.embeddings(
            model="mistral-embed",
            input=texts
        )
        return embeddings.data

# Usage
import asyncio
mistral = MistralEdge(api_key="your-api-key")
result = asyncio.run(mistral.chat_async([
    {"role": "user", "content": "What is edge computing?"}
]))
```

### 🎨 Generative AI

#### Stable Diffusion XL

```python
from diffusers import StableDiffusionXLPipeline
import torch

class SDXL:
    """High-quality image generation with Stable Diffusion XL"""

    def __init__(self, model_id: str = "stabilityai/stable-diffusion-xl-base-1.0"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.pipe = StableDiffusionXLPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            variant="fp16",
            use_safetensors=True
        ).to(self.device)

        # Enable memory optimizations
        self.pipe.enable_attention_slicing()
        self.pipe.enable_vae_slicing()

    def generate(
        self,
        prompt: str,
        negative_prompt: str = "blurry, low quality, distorted",
        width: int = 1024,
        height: int = 1024,
        steps: int = 30,
        guidance_scale: float = 7.5
    ):
        """Generate high-quality image"""
        image = self.pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            num_inference_steps=steps,
            guidance_scale=guidance_scale
        ).images[0]

        return image

# Usage
sdxl = SDXL()
image = sdxl.generate(
    prompt="A futuristic city with flying cars at sunset, highly detailed",
    steps=50
)
image.save("output.png")
```

#### ControlNet Implementation

```python
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel
from PIL import Image
import torch
import cv2
import numpy as np

class ControlNetGenerator:
    """Control image generation with edge maps, poses, depth"""

    def __init__(self, controlnet_type: str = "canny"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Load ControlNet
        controlnet = ControlNetModel.from_pretrained(
            f"lllyasviel/sd-controlnet-{controlnet_type}",
            torch_dtype=torch.float16
        )

        self.pipe = StableDiffusionControlNetPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            controlnet=controlnet,
            torch_dtype=torch.float16
        ).to(self.device)

    def prepare_canny_image(self, image_path: str):
        """Prepare edge map from image"""
        image = cv2.imread(image_path)
        image = cv2.Canny(image, 100, 200)
        image = Image.fromarray(image)
        return image

    def generate(self, prompt: str, control_image: Image, steps: int = 30):
        """Generate image with ControlNet guidance"""
        output = self.pipe(
            prompt=prompt,
            image=control_image,
            num_inference_steps=steps,
            controlnet_conditioning_scale=1.0
        ).images[0]

        return output

# Usage
controlnet = ControlNetGenerator("canny")
control_img = controlnet.prepare_canny_image("input.jpg")
result = controlnet.generate(
    "A beautiful landscape painting in impressionist style",
    control_img
)
```

### 🔍 RAG & Embeddings

#### LangChain Pipeline

```python
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI

class RAGPipeline:
    """Complete RAG system with LangChain"""

    def __init__(self, openai_api_key: str):
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2"
        )

        # Initialize LLM
        self.llm = OpenAI(api_key=openai_api_key, temperature=0)

        # Text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

        self.vectorstore = None
        self.qa_chain = None

    def ingest_documents(self, documents: list[str]):
        """Process and store documents"""
        # Split texts
        texts = self.text_splitter.create_documents(documents)

        # Create vector store
        self.vectorstore = FAISS.from_documents(texts, self.embeddings)

        # Create QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3})
        )

    def query(self, question: str):
        """Query the RAG system"""
        if not self.qa_chain:
            raise ValueError("No documents ingested. Call ingest_documents first.")

        result = self.qa_chain.run(question)
        return result

# Usage
rag = RAGPipeline(openai_api_key="your-key")
rag.ingest_documents([
    "Document 1 content...",
    "Document 2 content..."
])
answer = rag.query("What is the main topic?")
```

### 👁️ Computer Vision

#### YOLO v9 Object Detection

```python
from ultralytics import YOLO
import cv2
import numpy as np

class YOLOv9Detector:
    """State-of-the-art object detection with YOLOv9"""

    def __init__(self, model_size: str = "yolov9c"):
        """
        model_size: yolov9n (nano), yolov9s (small), yolov9m (medium),
                   yolov9c (compact), yolov9e (extended)
        """
        self.model = YOLO(f"{model_size}.pt")
        self.classes = self.model.names

    def detect(self, image_path: str, conf_threshold: float = 0.5):
        """Detect objects in image"""
        results = self.model(image_path, conf=conf_threshold)

        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                detection = {
                    'class': self.classes[int(box.cls)],
                    'confidence': float(box.conf),
                    'bbox': box.xyxy[0].tolist(),
                    'center': box.xywh[0].tolist()
                }
                detections.append(detection)

        return detections

    def detect_video(self, video_path: str, output_path: str = None):
        """Real-time video detection"""
        cap = cv2.VideoCapture(video_path)

        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            results = self.model(frame)
            annotated = results[0].plot()

            if output_path:
                out.write(annotated)
            else:
                cv2.imshow('YOLOv9', annotated)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        cap.release()
        if output_path:
            out.release()
        cv2.destroyAllWindows()

# Usage
detector = YOLOv9Detector()
detections = detector.detect("image.jpg", conf_threshold=0.7)
for det in detections:
    print(f"{det['class']}: {det['confidence']:.2f}")
```

## 📚 Popular Repositories

- **[Hugging Face Transformers](https://github.com/huggingface/transformers)** ⭐ 125k+ - State-of-the-art NLP
- **[LangChain](https://github.com/langchain-ai/langchain)** ⭐ 80k+ - LLM application framework
- **[llama.cpp](https://github.com/ggerganov/llama.cpp)** ⭐ 60k+ - LLaMA in C/C++
- **[Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui)** ⭐ 130k+ - SD interface
- **[Ultralytics YOLOv8/v9](https://github.com/ultralytics/ultralytics)** ⭐ 25k+ - Object detection

## 🎯 Edge Optimization Tips

1. **Use quantization**: INT8/INT4 for 4x smaller models
2. **Enable attention slicing**: Reduce memory usage
3. **Batch processing**: Process multiple inputs together
4. **Model pruning**: Remove unnecessary weights
5. **ONNX Runtime**: 2-3x faster inference

---

<div align="center">

**[⬅️ Back to Main](../../README.md)** | **[Next: Frontend →](../frontend/README.md)**

</div>
