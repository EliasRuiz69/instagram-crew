import requests
import os
import time
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class InstagramPublishInput(BaseModel):
    imagen_path: str = Field(..., description="Ruta local del archivo PNG")
    caption: str = Field(..., description="Texto del post en español")
    hashtags: str = Field(..., description="String de hashtags separados por espacio")


class InstagramPublisherTool(BaseTool):
    name: str = "InstagramPublisherTool"
    description: str = (
        "Publica un post en Instagram Business vía Meta Graph API v21.0. "
        "Sube la imagen a imgbb, crea el media container y ejecuta la publicación."
    )
    args_schema: type[BaseModel] = InstagramPublishInput

    def _upload_to_imgbb(self, imagen_path: str) -> str:
        imgbb_key = os.environ.get("IMGBB_API_KEY")
        with open(imagen_path, "rb") as img_file:
            response = requests.post(
                "https://api.imgbb.com/1/upload",
                params={"key": imgbb_key},
                files={"image": img_file},
                timeout=60
            )
        response.raise_for_status()
        return response.json()["data"]["url"]

    def _run(self, imagen_path: str, caption: str, hashtags: str) -> str:
        access_token = os.environ.get("INSTAGRAM_ACCESS_TOKEN")
        account_id = os.environ.get("INSTAGRAM_ACCOUNT_ID")
        base_url = f"https://graph.instagram.com/v21.0/{account_id}"

        full_caption = f"{caption}\n\n{hashtags}"

        # Subir imagen a imgbb
        image_url = self._upload_to_imgbb(imagen_path)

        # Paso 1: crear media container
        container_resp = requests.post(
            f"{base_url}/media",
            params={
                "image_url": image_url,
                "caption": full_caption,
                "media_type": "IMAGE",
                "access_token": access_token
            },
            timeout=30
        )
        container_resp.raise_for_status()
        creation_id = container_resp.json().get("id")

        # Pausa recomendada por Meta entre pasos
        time.sleep(5)

        # Paso 2: publicar el container
        publish_resp = requests.post(
            f"{base_url}/media_publish",
            params={
                "creation_id": creation_id,
                "access_token": access_token
            },
            timeout=30
        )
        publish_resp.raise_for_status()
        post_id = publish_resp.json().get("id")

        return f"Post publicado. Post ID: {post_id} | Preview: {full_caption[:50]}..."