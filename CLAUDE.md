# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Run the crew (interactive: prompts for topic)
uv run crewai run

# Reset CrewAI memories if the crew behaves inconsistently
uv run crewai reset-memories -a
```

There are no tests or linter configured in this project.

## Architecture

This is a sequential CrewAI crew that automates Instagram post creation end-to-end. The entry point is `main.py`, which calls `InstagramCrew().crew().kickoff(inputs={"topic": ..., "account_id": ...})`. The crew runs 4 agents in fixed order defined in `crew.py`:

1. **trend_researcher** — Searches the web via Tavily (basic depth, max 3 results, max 2 iterations) and returns a JSON with `tema`, `angulos_principales`, `datos_clave`, `tono_sugerido`, `contexto_visual`.
2. **instagram_copywriter** — Receives the research JSON via `context` and returns a JSON with `caption` (100–125 words, Spanish), `hashtags` (10 tags), `conteo_palabras`, `prompt_imagen` (English, for image generation).
3. **image_creator** — Uses `HuggingFaceImageTool` with the `prompt_imagen` field. Calls `router.huggingface.co/hf-inference/models/{model}` (FLUX.1-schnell, 1024×1024, 4 steps, guidance 0.0). Saves the PNG to `output/post_image.png` and returns the absolute path.
4. **instagram_publisher** — Uses `InstagramPublisherTool`: uploads the PNG to imgbb to get a public URL, then calls `graph.instagram.com/v21.0/{account_id}/media` (create container) and `/media_publish` (publish), with a 5-second sleep between steps.

### Key design decisions

- **`get_claude_llm()` is called per-agent** (not a shared module-level instance) to avoid state sharing between agents.
- **Agent and task definitions are split**: behaviour/role/backstory live in `config/agents.yaml` and `config/tasks.yaml`; tool assignment and LLM wiring live in `crew.py`.
- **`memory=False` and `planning=False`** are intentional — both were disabled to avoid dependency on OpenAI embeddings (CrewAI's memory system defaults to OpenAI).
- **`account_id` is passed as a crew input** (not read directly from env inside the tool) so the task prompt can reference it as `{account_id}`.
- **FLUX.1-schnell parameters**: `guidance_scale: 0.0` and `num_inference_steps: 4` are correct for this model — do not increase them thinking it improves quality.

### LLM

All agents use `anthropic/claude-sonnet-4-5-20250929` with `max_tokens=2048`. The `anthropic/` prefix is required by CrewAI's LiteLLM routing layer; without it the call fails.

### Custom tools

Both tools extend `crewai.tools.BaseTool` with a Pydantic `args_schema`. The tool name string (`name: str`) must be stable — CrewAI uses it to match the agent's tool call to the implementation.

- `HuggingFaceImageTool` (`tools/imagen_tool.py`) — image generation. The `negative_prompt` field exists in the schema but is not sent in the API payload (FLUX.1-schnell ignores it).
- `InstagramPublisherTool` (`tools/instagram_tool.py`) — two-step Meta Graph API publish flow.
