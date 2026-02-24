# C4 Architecture Playground

A [Claude Code plugin](https://docs.anthropic.com/en/docs/claude-code) for building, visualizing, and rendering C4 architecture models.

## What it does

Three skills that work together:

1. **`c4-prep`** — Guides you through C4 architecture modeling (L1 Context, L2 Containers, L3 Components) via conversation. Enforces C4 guardrails (cognitive load limits, relationship labeling, runtime boundary definitions). Outputs standard [Structurizr workspace JSON](https://github.com/structurizr/json).

2. **`playground`** — Generates self-contained HTML playgrounds for visual exploration. Includes a C4 architecture template that consumes the Structurizr JSON from `c4-prep` and renders an interactive SVG diagram with drag-and-drop nodes, drill-down navigation across levels, and position persistence.

3. **`c4-cards`** — Renders publication-ready PNG architecture diagrams from your C4 model using Google Gemini image generation (Nano Banana Pro). Supports multiple visual styles (clean minimal, blueprint, hand-drawn sketch) and aspect ratios.

## Workflow

```
/c4-prep  →  answer questions  →  workspace JSON
                                       │
                        ┌──────────────┼──────────────┐
                        ▼              ▼              ▼
                   /playground     /c4-cards      Load in
                   interactive     PNG cards      Structurizr
                   HTML explorer   for docs       or LikeC4
```

## Quick Start: Hello World (end-to-end)

### 1. Model your architecture

```
You: /c4-prep

Claude: What system are we modeling?

You: A todo app. One user ("Developer") who manages tasks through a
     web UI built in React, backed by a Node.js API and SQLite database.

Claude: [guides you through L1 → L2, asks clarifying questions, outputs JSON]
Claude: Saved to todo-app.json
```

### 2. Generate PNG cards

```
You: /c4-cards todo-app.json

Claude: Found L1 (1 user, 1 system) and L2 (3 containers).
        Which levels? → All levels
        Style? → Clean minimal
        Aspect ratio? → 16:9

Claude: [shows ASCII preview]

         ┌───────────┐
         │ Developer  │
         └─────┬──────┘
               │ Uses (HTTPS)
               ▼
        ┌────────────┐   ┌────────────┐   ┌────────────┐
        │  Web UI    │──▶│    API     │──▶│  Database   │
        │  (React)   │   │ (Node.js)  │   │  (SQLite)   │
        └────────────┘   └────────────┘   └────────────┘

        Does this look right?

You: Looks good!

Claude: Generated cards:
        - /tmp/c4-cards/l1-context.png (185 KB)
        - /tmp/c4-cards/l2-containers.png (243 KB)
```

### 3. Explore interactively (optional)

```
You: Now make a playground from todo-app.json

Claude: [generates interactive HTML with drill-down navigation]
```

## Installation

```bash
claude plugin add one1zero1one/claude-playground-c4
```

### Requirements for c4-cards

The `c4-cards` skill generates images via Google Gemini and needs:

- **Google API key** — set `GOOGLE_API_KEY` or `GEMINI_API_KEY` environment variable ([get one here](https://aistudio.google.com/apikey))
- **uv** — Python package runner, handles dependencies automatically ([install uv](https://docs.astral.sh/uv/getting-started/installation/))

The `c4-prep` and `playground` skills have no extra requirements.

## Skills

### c4-prep

Interactive C4 model builder. Walks you through:
- **L1 Context** — actors, the system, external dependencies
- **L2 Containers** — runtime boundaries (web apps, APIs, databases, queues)
- **L3 Components** — internal structure of complex containers (opt-in)

Enforces C4 guardrails: max 10-12 items per view, required relationship labels, runtime boundary validation. Outputs Structurizr-compatible workspace JSON.

### playground

Self-contained HTML playground generator. Templates include:
- **c4-architecture** — C4 model visualization with drill-down
- **code-map** — Codebase architecture
- **concept-map** — Learning and exploration
- **data-explorer** — Data and query building
- **design-playground** — Visual design decisions
- **diff-review** — Code review
- **document-critique** — Document review

### c4-cards

PNG diagram generator with three visual styles:

| Style | Best for |
|-------|----------|
| **Clean minimal** | Documentation, formal architecture reviews |
| **Blueprint** | Technical presentations, engineering specs |
| **Hand-drawn sketch** | Early-stage discussions, whiteboard replacement |

Supports 16:9 (presentations), 4:3 (documents), and 1:1 (social) aspect ratios.

Uses Google Gemini (Nano Banana Pro) for image generation, with automatic fallback to Flash on timeout. Dependencies are handled on-the-fly by `uv` — no install step needed.

## Origin

The playground skill is derived from [Anthropic's official playground plugin](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/playground), licensed under Apache 2.0. The `c4-prep` skill, `c4-architecture` template, and `c4-cards` skill (including the Nano Banana image generation script) are original additions.

## License

Apache 2.0 — see [LICENSE](LICENSE).

Playground skill: Copyright 2025 Anthropic (original), modifications by Daniel Radu.
c4-prep skill, c4-cards skill: Copyright 2025 Daniel Radu.
