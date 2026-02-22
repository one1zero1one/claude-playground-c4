# C4 Architecture Playground

A [Claude Code plugin](https://docs.anthropic.com/en/docs/claude-code) for building and visualizing C4 architecture models interactively.

## What it does

Two skills that work together:

1. **`c4-prep`** — Guides you through C4 architecture modeling (L1 Context, L2 Containers, L3 Components) via conversation. Enforces C4 guardrails (cognitive load limits, relationship labeling, runtime boundary definitions). Outputs standard [Structurizr workspace JSON](https://github.com/structurizr/json).

2. **`playground`** — Generates self-contained HTML playgrounds for visual exploration. Includes a C4 architecture template that consumes the Structurizr JSON from `c4-prep` and renders an interactive SVG diagram with drag-and-drop nodes, drill-down navigation across levels, and position persistence.

## Workflow

```
/c4-prep  →  answer questions  →  get workspace JSON
                                        ↓
            "make a playground"  →  interactive HTML with drill-down
```

## Origin

The playground skill is derived from [Anthropic's official playground plugin](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/playground), licensed under Apache 2.0. The C4 architecture template and the `c4-prep` skill are original additions.

## Installation

```bash
claude plugin add one1zero1one/claude-playground-c4
```

## Templates

The playground skill includes templates for:

- **c4-architecture** — C4 model visualization (context, container, component views with drill-down)
- **code-map** — Codebase architecture (component relationships, data flow, layer diagrams)
- **concept-map** — Learning and exploration (draggable nodes, knowledge gap tracking)
- **data-explorer** — Data and query building (SQL, APIs, pipelines, regex)
- **design-playground** — Visual design decisions (components, layouts, spacing, color, typography)
- **diff-review** — Code review (git diffs with line-by-line commenting)
- **document-critique** — Document review (suggestions with approve/reject/comment workflow)

## License

Apache 2.0 — see [LICENSE](LICENSE).

Playground skill: Copyright 2025 Anthropic (original), modifications by Daniel Radu.
C4-prep skill: Copyright 2025 Daniel Radu.
