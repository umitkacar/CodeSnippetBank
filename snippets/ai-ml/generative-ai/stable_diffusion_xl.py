"""
Stable Diffusion XL
Text-to-image generation with SDXL and advanced features.
"""

import torch
from typing import List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

try:
    from diffusers import (
        StableDiffusionXLPipeline,
        StableDiffusionXLImg2ImgPipeline,
        StableDiffusionXLInpaintPipeline,
        DPMSolverMultistepScheduler
    )
    from PIL import Image
    DIFFUSERS_AVAILABLE = True
except ImportError:
    DIFFUSERS_AVAILABLE = False


@dataclass
class GenerationConfig:
    """Configuration for image generation."""
    prompt: str
    negative_prompt: Optional[str] = None
    num_inference_steps: int = 50
    guidance_scale: float = 7.5
    width: int = 1024
    height: int = 1024
    seed: Optional[int] = None


class SDXLGenerator:
    """Production-ready SDXL text-to-image generator."""

    def __init__(
        self,
        model_id: str = "stabilityai/stable-diffusion-xl-base-1.0",
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
        use_fp16: bool = True
    ):
        """
        Initialize SDXL generator.

        Args:
            model_id: HuggingFace model ID
            device: Device to use
            use_fp16: Use half precision
        """
        if not DIFFUSERS_AVAILABLE:
            raise ImportError("diffusers not installed")

        torch_dtype = torch.float16 if use_fp16 else torch.float32

        self.pipe = StableDiffusionXLPipeline.from_pretrained(
            model_id,
            torch_dtype=torch_dtype,
            use_safetensors=True
        )

        self.pipe.to(device)

        # Optimize
        if device == "cuda":
            self.pipe.enable_model_cpu_offload()

    def generate(
        self,
        config: GenerationConfig,
        num_images: int = 1
    ) -> List[Image.Image]:
        """
        Generate images from text.

        Args:
            config: Generation configuration
            num_images: Number of images to generate

        Returns:
            List of PIL Images
        """
        generator = None

        if config.seed is not None:
            generator = torch.Generator(device=self.pipe.device).manual_seed(config.seed)

        images = self.pipe(
            prompt=config.prompt,
            negative_prompt=config.negative_prompt,
            num_inference_steps=config.num_inference_steps,
            guidance_scale=config.guidance_scale,
            width=config.width,
            height=config.height,
            num_images_per_prompt=num_images,
            generator=generator
        ).images

        return images


# Usage Example
if __name__ == "__main__":
    if not DIFFUSERS_AVAILABLE:
        print("Please install diffusers: pip install diffusers transformers accelerate")
        exit(1)

    print("=== Stable Diffusion XL ===")

    # Initialize
    # generator = SDXLGenerator()

    # Generate
    # config = GenerationConfig(
    #     prompt="A beautiful sunset over mountains, digital art",
    #     negative_prompt="blurry, low quality",
    #     num_inference_steps=30,
    #     seed=42
    # )

    # images = generator.generate(config)
    # images[0].save("output.png")

    print("SDXL generator ready!")
