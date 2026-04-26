import requests
import os
from pathlib import Path
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class HuggingFaceImageInput(BaseModel):
    prompt: str = Field(..., description="Descripción detallada en inglés de la imagen a generar")
    negative_prompt: str = Field(
        default="text, watermark, logo, words, letters, blurry, low quality, distorted",
        description="Elementos a excluir de la imagen"
    )
    filename: str = Field(default="post_image.png", description="Nombre del archivo de salida")


class HuggingFaceImageTool(BaseTool):
    name: str = "HuggingFaceImageTool"
    description: str = (
        "Genera imágenes usando Hugging Face Inference API con FLUX.1-schnell "
        "(gratuito). Recibe un prompt en inglés y retorna la ruta local del PNG generado."
    )
    args_schema: type[BaseModel] = HuggingFaceImageInput

    def _run(self, prompt: str, negative_prompt: str, filename: str) -> str:
        api_key = os.environ.get("HUGGINGFACE_API_KEY")
        model = os.environ.get("HUGGINGFACE_MODEL", "black-forest-labs/FLUX.1-schnell")

        url = f"https://router.huggingface.co/hf-inference/models/{model}"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": prompt,
            "parameters": {
                "width": 1024,
                "height": 1024,
                "num_inference_steps": 4,
                "guidance_scale": 0.0
            }
        }

        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / filename

        response = requests.post(url, headers=headers, json=payload, timeout=180)

        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            return str(output_path.resolve())
        else:
            raise Exception(f"Error Hugging Face API: {response.status_code} - {response.text}")
