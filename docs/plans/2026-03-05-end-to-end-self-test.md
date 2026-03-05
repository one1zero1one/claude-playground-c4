# End-to-End Self-Test: C4 Model of the Plugin Itself

Use the plugin's own skills to model and render the `claude-playground-c4` plugin architecture. This tests the full pipeline and produces useful documentation as a side effect.

## Prerequisites

- Claude Code with the `claude-playground-c4` plugin installed (update to latest after the c4-mermaid/c4-excalidraw push)
- `GOOGLE_API_KEY` or `GEMINI_API_KEY` set (for c4-cards)
- `uv` installed (for c4-cards)
- `excalidraw-diagram` skill installed with renderer set up (for c4-excalidraw validation)
- Working directory: `/Users/daniel.radu/repo/mine/claude-playground-c4`

## Step 1: c4-prep — Model the plugin

Run `/c4-prep` from inside the `claude-playground-c4` repo. Let it explore the codebase first.

**Expected discovery:**
- **System:** "C4 Architecture Toolkit" — Claude Code plugin for modeling, exploring, and rendering C4 diagrams
- **Actors:** Developer (uses the skills via Claude Code CLI)
- **Containers:**
  - c4-prep (skill — explores codebase, builds Structurizr JSON)
  - playground (skill — generates interactive SVG HTML)
  - c4-cards (skill + nb.py script — generates PNG via Gemini)
  - c4-mermaid (skill — generates Mermaid HTML)
  - c4-excalidraw (skill — generates Excalidraw JSON)
- **External systems:**
  - Claude Code CLI (host environment that loads and runs skills)
  - Mermaid CDN (cdn.jsdelivr.net — renders Mermaid diagrams in browser)
  - Google Gemini API (generates PNG images for c4-cards)
  - Excalidraw (excalidraw.com — opens .excalidraw files)
  - Structurizr ecosystem (tools that consume the workspace JSON)

**Refinement notes:**
- The Structurizr workspace JSON is the central data artifact — all renderers consume it
- c4-prep produces the JSON; playground, c4-cards, c4-mermaid, c4-excalidraw consume it
- nb.py is internal to c4-cards, not a separate container
- The relationship between skills and Claude Code is "loaded and executed by"

**Output:** Save as `docs/examples/self-model.json`

**Validation:**
- [ ] JSON passes c4-prep's guardrails (<=12 items per view, all relationships labeled)
- [ ] All five skills appear as containers
- [ ] External systems are marked with `"location": "External"`
- [ ] Relationships between skills and the JSON artifact are captured

## Step 2: playground — Interactive SVG explorer

Run: "Make a playground from docs/examples/self-model.json"

**Output:** `docs/examples/self-model.html`

**Validation:**
- [ ] Opens in browser without errors
- [ ] L1 shows Developer → Toolkit → External systems
- [ ] L2 drill-down shows all five skill containers inside the toolkit
- [ ] L3 drill-down works for any container that has components
- [ ] Drag-and-drop repositions nodes
- [ ] Position persistence works (refresh page, positions saved)

## Step 3: c4-cards — PNG cards

Run: `/c4-cards docs/examples/self-model.json`

Choose:
- Levels: All
- Style: Clean minimal
- Aspect ratio: 16:9

**Output:** `docs/examples/self-model-l1-context.png`, `docs/examples/self-model-l2-containers.png`

**Validation:**
- [ ] PNGs generated without errors
- [ ] L1 card shows system, actor, and external systems
- [ ] L2 card shows all five containers
- [ ] Text is readable, layout is balanced

## Step 4: c4-mermaid — Mermaid HTML

Run: `/c4-mermaid docs/examples/self-model.json`

**Output:** `docs/examples/self-model-c4-mermaid.html`

**Validation:**
- [ ] Opens in browser without errors
- [ ] Tabs switch between L1 and L2 (and L3 if modeled)
- [ ] Mermaid diagrams render correctly (no syntax errors in console)
- [ ] Dark mode works (toggle system preference or use devtools)
- [ ] Key points section has useful content for each level
- [ ] Print preview shows all levels

## Step 5: c4-excalidraw — Editable Excalidraw files

Run: `/c4-excalidraw docs/examples/self-model.json`

Choose: All levels

**Output:** `docs/examples/self-model-c4-context.excalidraw`, `docs/examples/self-model-c4-containers.excalidraw`

**Validation:**
- [ ] Files are valid JSON (parseable)
- [ ] Open in excalidraw.com without errors
- [ ] Person shape has head circle + body rectangle
- [ ] C4 colors are correct (blue internal, gray external)
- [ ] Boundary rectangles are dashed and contain child elements
- [ ] Arrows connect correct elements with labels
- [ ] Elements are draggable and editable in Excalidraw
- [ ] If render script available: PNG renders cleanly, no overlaps

## Step 6: Compare outputs

Open all four renderings side by side:
1. Interactive SVG playground (self-model.html)
2. PNG cards (self-model-l1/l2.png)
3. Mermaid HTML (self-model-c4-mermaid.html)
4. Excalidraw (self-model-c4-context/containers.excalidraw)

**Check:**
- [ ] All four show the same architecture (same elements, same relationships)
- [ ] No renderer dropped elements or relationships present in the JSON
- [ ] Each format's strengths are visible (playground: interactive; cards: polished; mermaid: lightweight; excalidraw: editable)

## Step 7: Document findings

Create `docs/examples/README.md` with:
- What the self-model represents
- Links/paths to each output file
- Any issues found and fixes applied
- Screenshots if useful

Commit all example outputs to the repo as living documentation.
