# C4 Architecture Playground

A [Claude Code plugin](https://docs.anthropic.com/en/docs/claude-code) that models, explores, and renders C4 architecture diagrams.

Three skills form a pipeline:

1. **`c4-prep`** models your architecture through conversation (L1 Context, L2 Containers, L3 Components), enforces C4 guardrails, and outputs [Structurizr workspace JSON](https://github.com/structurizr/json).

2. **`playground`** turns that JSON into a self-contained HTML explorer with drag-and-drop nodes, drill-down across levels, and position persistence.

3. **`c4-cards`** renders publication-ready PNG diagrams from the same JSON using Google Gemini (Nano Banana Pro).

```
/c4-prep  →  workspace JSON  →  /playground  →  /c4-cards
(model)                         (explore)       (render PNGs)
```

## Hello World

Model a todo app, explore it, render it:

```
You: /c4-prep

Claude: What system are we modeling?

You: A todo app. One user ("Developer"), a React web UI,
     a Node.js API, and a SQLite database.

Claude: [walks through L1 → L2, asks clarifying questions]
Claude: Saved to todo-app.json
```

```
You: Make a playground from todo-app.json

Claude: [writes todo-app.html — open it in your browser]
```

```
You: /c4-cards todo-app.json

Claude: Which levels? → All
        Style? → Clean minimal
        Aspect ratio? → 16:9

        [ASCII preview]

         ┌───────────┐
         │ Developer  │
         └─────┬──────┘
               │ Uses (HTTPS)
               ▼
        ┌────────────┐   ┌────────────┐   ┌────────────┐
        │  Web UI    │──▶│    API     │──▶│  Database   │
        │  (React)   │   │ (Node.js)  │   │  (SQLite)   │
        └────────────┘   └────────────┘   └────────────┘

        Looks right? → Yes

Claude: Generated:
        - l1-context.png (185 KB)
        - l2-containers.png (243 KB)
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

Walks you through C4 modeling level by level. Enforces guardrails: 10-12 items per view, labeled relationships, runtime boundaries only. Outputs Structurizr-compatible JSON you can also load in [Structurizr](https://structurizr.com/) or [LikeC4](https://likec4.dev/).

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

Playground skill: Copyright 2025 Anthropic (original), modifications by Daniel Radu.
c4-prep, c4-cards: Copyright 2025 Daniel Radu.
