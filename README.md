# C4 Architecture Playground

A [Claude Code plugin](https://docs.anthropic.com/en/docs/claude-code) that models, explores, and renders C4 architecture diagrams.

Three skills form a pipeline:

1. **`c4-prep`** explores your codebase or conversation context, proposes a C4 model (L1 Context, L2 Containers, L3 Components), and refines it with you. Outputs [Structurizr workspace JSON](https://github.com/structurizr/json).

2. **`playground`** turns that JSON into a self-contained HTML explorer with drag-and-drop nodes, drill-down across levels, and position persistence.

3. **`c4-cards`** renders publication-ready PNG diagrams from the same JSON using Google Gemini (Nano Banana Pro).

```
/c4-prep  →  workspace JSON  →  /playground  →  /c4-cards
(model)                         (explore)       (render PNGs)
```

## Example

You're deep in a codebase and need to step back and see the system. Run `/c4-prep` and Claude explores the project before asking you anything:

```
You: /c4-prep

Claude: [reads README, docker-compose.yml, scans routes and DB connections]

Claude: Here's what I see:
        - System: "Acme API" — order management platform
        - Actors: Customer (mobile app), Admin (dashboard)
        - Containers: React SPA, Express API, PostgreSQL, Redis cache,
          RabbitMQ for async jobs
        - External: Stripe (payments), SendGrid (email)

        Does this match? What's wrong or missing?

You: The worker service is missing — it consumes from RabbitMQ.

Claude: [adds Worker container, refines relationships, walks through L2 → L3]
Claude: Saved to acme-api.json
```

Explore it interactively:

```
You: Make a playground from acme-api.json

Claude: [writes acme-api.html — open in browser, drill down L1 → L2 → L3]
```

Render PNG cards for documentation or slides:

```
You: /c4-cards acme-api.json

Claude: Which levels? → All
        Style? → Clean minimal
        Aspect ratio? → 16:9

        [ASCII preview, you confirm]

Claude: Generated:
        - l1-context.png (185 KB)
        - l2-containers.png (312 KB)
        - l3-api-components.png (278 KB)
```

## Install

```bash
claude plugin add one1zero1one/claude-playground-c4
```

### c4-cards requirements

`c4-cards` calls Google Gemini to generate images. It needs:

- A **Google API key**: set `GOOGLE_API_KEY` or `GEMINI_API_KEY` ([get one](https://aistudio.google.com/apikey))
- **uv**: runs the Python script with dependencies on the fly ([install](https://docs.astral.sh/uv/getting-started/installation/))

`c4-prep` and `playground` need nothing beyond Claude Code.

## Skills

### c4-prep

Explores your codebase, conversation context, or design docs first — then proposes a C4 model for you to refine. Spins up subagents to scan large projects in parallel. Enforces guardrails: 10-12 items per view, labeled relationships, runtime boundaries only. Outputs Structurizr-compatible JSON you can also load in [Structurizr](https://structurizr.com/) or [LikeC4](https://likec4.dev/).

### playground

Generates a single HTML file you open in any browser. The C4 template renders interactive SVG diagrams; other templates cover code maps, concept maps, data exploration, design decisions, diff review, and document critique.

### c4-cards

Generates PNG cards in three styles:

| Style | Use |
|-------|-----|
| **Clean minimal** | Documentation, architecture reviews |
| **Blueprint** | Technical presentations |
| **Hand-drawn sketch** | Early discussions, whiteboard replacement |

Aspect ratios: 16:9 (slides), 4:3 (docs), 1:1 (social). Tries Gemini Pro first; falls back to Flash on timeout. `uv` handles all Python dependencies — nothing to install.

## Origin

The playground skill derives from [Anthropic's official playground plugin](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/playground) (Apache 2.0). `c4-prep`, the C4 template, and `c4-cards` (including the Nano Banana image generation script) are original work.

## License

Apache 2.0 — see [LICENSE](LICENSE).
