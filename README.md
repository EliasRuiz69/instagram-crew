# Instagram Crew

Automatización de contenido para Instagram Business usando [CrewAI](https://crewai.com). Un equipo de 4 agentes de IA genera y publica posts de forma autónoma: investiga tendencias, redacta el copy, crea la imagen y la publica en Instagram.

## Agentes

| Agente | Rol | Herramienta |
|---|---|---|
| `trend_researcher` | Investiga el tema en internet | Tavily Search |
| `instagram_copywriter` | Redacta el caption y hashtags | — |
| `image_creator` | Genera la imagen con IA | HuggingFace FLUX.1-schnell |
| `instagram_publisher` | Publica el post en Instagram | Meta Graph API |

## Flujo de trabajo

```
[Usuario ingresa tema]
        ↓
  trend_researcher  →  Investigación + datos clave (JSON)
        ↓
instagram_copywriter →  Caption (100-125 palabras) + 10 hashtags + prompt imagen (JSON)
        ↓
   image_creator    →  Genera imagen 1024×1024 px con FLUX.1-schnell
        ↓
instagram_publisher →  Sube imagen a imgbb → crea media container → publica en Instagram
```

## Tecnologías

- **LLM**: Claude Sonnet 4.5 (`anthropic/claude-sonnet-4-5-20250929`) vía Anthropic API
- **Búsqueda web**: Tavily Search API
- **Generación de imágenes**: FLUX.1-schnell vía HuggingFace Inference API
- **Hosting de imágenes**: imgbb
- **Publicación**: Meta Graph API v21.0 (`graph.instagram.com`)
- **Framework**: CrewAI >= 0.80.0
- **Gestión de paquetes**: uv

## Requisitos

- Python >= 3.10, < 3.13
- [uv](https://docs.astral.sh/uv/) instalado
- Cuentas y API keys en: Anthropic, Tavily, HuggingFace, imgbb
- Instagram Business Account con token de acceso de Meta

## Instalación

```bash
git clone https://github.com/EliasRuiz69/instagram-crew.git
cd instagram-crew

# Instalar dependencias
uv sync

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys reales
```

## Configuración

Copia `.env.example` a `.env` y completa cada valor:

```env
ANTHROPIC_API_KEY=           # API key de Anthropic
TAVILY_API_KEY=              # API key de Tavily
HUGGINGFACE_API_KEY=         # API key de HuggingFace
HUGGINGFACE_MODEL=black-forest-labs/FLUX.1-schnell
INSTAGRAM_ACCESS_TOKEN=      # Token de acceso de Meta
INSTAGRAM_ACCOUNT_ID=        # ID de tu cuenta de Instagram Business
IMGBB_API_KEY=               # API key de imgbb
CREWAI_DISABLE_TELEMETRY=true
```

## Uso

```bash
uv run crewai run
```

El programa pedirá el tema del post:

```
¿Sobre qué tema quieres publicar en Instagram hoy? → inteligencia artificial
```

La imagen generada se guarda en `output/post_image.png`.

## Estructura del proyecto

```
instagram-crew/
├── src/instagram_crew/
│   ├── config/
│   │   ├── agents.yaml       # Definición de agentes
│   │   └── tasks.yaml        # Definición de tareas
│   ├── tools/
│   │   ├── imagen_tool.py    # HuggingFace image generation
│   │   └── instagram_tool.py # Meta Graph API publisher
│   ├── crew.py               # Definición del crew
│   └── main.py               # Punto de entrada
├── output/                   # Imágenes generadas (ignorado por git)
├── .env.example              # Plantilla de variables de entorno
├── pyproject.toml
└── uv.lock
```
