---
name: c4-cards
description: Generate C4 architecture diagrams as PNG images from Structurizr workspace JSON. Renders visual cards for each C4 level using Google Gemini image generation.
---

# C4 Architecture Cards

Generate publication-ready PNG architecture diagrams from C4 models. Works with the Structurizr workspace JSON produced by `c4-prep`, or any C4 model you describe.

## Prerequisites

- **Google API key**: Set `GOOGLE_API_KEY` or `GEMINI_API_KEY` environment variable
- **uv**: Used to run the image generation script with dependencies ([install uv](https://docs.astral.sh/uv/getting-started/installation/))

## How to execute

Parse `$ARGUMENTS` to determine the mode:
- `<path-to-json>` — Load a Structurizr workspace JSON and generate cards from it
- (empty) — Ask the user to describe the architecture or point to a JSON file

### Step 1: Load the C4 Model

**If a JSON path is provided:**
- Read the Structurizr workspace JSON file
- Extract: people, software systems, containers, components, relationships
- Identify which C4 levels have content (L1 always, L2 if containers exist, L3 if components exist)

**If no path:**
- Ask: "Do you have a Structurizr workspace JSON file, or should I work from a description?"
- If description: collect system name, key actors, containers, and relationships conversationally
- If they haven't run `c4-prep` yet, suggest: "Run `/c4-prep` first to build the model interactively, then come back here to render cards."

### Step 2: Choose What to Render

Ask the user (use AskUserQuestion):

1. **Which levels to render?**
   - Options: "All levels", "L1 Context only", "L2 Containers only", "L3 Components only"

2. **Visual style?**
   - Options: "Clean minimal (white background, flat boxes)", "Blueprint (dark background, light lines)", "Hand-drawn sketch (cream paper, ink style)"

3. **Aspect ratio?**
   - Options: "16:9 landscape (presentations)", "4:3 landscape (documents)", "1:1 square (social media)"

### Step 3: Generate ASCII Preview

For each selected level, generate an ASCII diagram showing:
- All elements at that level with their names
- Relationships as arrows with labels
- External systems marked with `[EXT]`

Example for L1:
```
                    ┌──────────┐
                    │  User    │
                    └────┬─────┘
                         │ Uses (HTTPS)
                         ▼
                 ┌───────────────┐
                 │  My System    │
                 │               │
                 └───────┬───────┘
                         │ Sends emails via (SMTP)
                         ▼
                 ┌───────────────┐
                 │ Email Service │
                 │    [EXT]      │
                 └───────────────┘
```

Show the preview and ask: "Does this look right? Any changes before I render?"

Do NOT proceed until the user confirms.

### Step 4: Generate Image Prompts

For each confirmed diagram, create a prompt file. Save to a temporary directory.

**Determine the plugin scripts directory** by finding `nb.py` relative to this skill:
```bash
PLUGIN_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
# nb.py is at $PLUGIN_DIR/scripts/nb.py
```

In practice, since Claude executes the commands, locate `nb.py` in the plugin's `scripts/` directory. The plugin is installed at a path like `~/.claude/plugins/one1zero1one__claude-playground-c4/scripts/nb.py`. Use `find` or check the known plugin install path.

**Prompt template** (adapt per style choice):

For "Clean minimal":
```
Create a C4 {LEVEL_NAME} diagram card.

DESIGN: Clean and minimal. White background (#FFFFFF). Flat colored boxes with
subtle rounded corners. Dark gray text (#333333). Blue accent (#4A90D9) for the
primary system. Gray (#999999) for external systems. 2K resolution, {ASPECT_RATIO}.

TITLE: "{SYSTEM_NAME} — {LEVEL_NAME}" top-left, bold, 28pt.

LAYOUT:
{ASCII_DIAGRAM}

ELEMENTS:
{ELEMENT_DESCRIPTIONS}

RELATIONSHIPS: Show as labeled arrows between boxes. Arrow labels in small italic text.

Keep maximum whitespace. No decorative elements. No icons. No gradients.
```

For "Blueprint":
```
Create a C4 {LEVEL_NAME} diagram card.

DESIGN: Blueprint style. Dark navy background (#1a1a2e). Light cyan lines and text
(#00d4ff). Boxes drawn with thin cyan borders, no fill. Monospace font feel.
2K resolution, {ASPECT_RATIO}. Technical drawing aesthetic.

TITLE: "{SYSTEM_NAME} — {LEVEL_NAME}" top-left, 28pt.

LAYOUT:
{ASCII_DIAGRAM}

ELEMENTS:
{ELEMENT_DESCRIPTIONS}

RELATIONSHIPS: Thin cyan arrows with small labels.
```

For "Hand-drawn sketch":
```
Create a C4 {LEVEL_NAME} diagram card.

DESIGN: Hand-drawn napkin sketch. Cream paper background (#FAFAFA). Dark gray
ink lines (#2D2D2D). Blue accent (#4A90A4) for highlights. Slightly wobbly
hand-drawn lines. Clean sans-serif labels. 2K resolution, {ASPECT_RATIO}.

TITLE: "{SYSTEM_NAME} — {LEVEL_NAME}" top-left, handwritten style, 28pt.

LAYOUT:
{ASCII_DIAGRAM}

ELEMENTS:
{ELEMENT_DESCRIPTIONS}

RELATIONSHIPS: Hand-drawn arrows with small italic labels.
```

Save each prompt to a temp file.

### Step 5: Render with Nano Banana

Find the `nb.py` script bundled with this plugin:

```bash
# Locate nb.py in the plugin installation
NB_SCRIPT="$(find ~/.claude/plugins -path '*/claude-playground-c4/scripts/nb.py' 2>/dev/null | head -1)"

# If not found via plugins, check if running from repo clone
if [ -z "$NB_SCRIPT" ]; then
  NB_SCRIPT="$(find . -path '*/scripts/nb.py' 2>/dev/null | head -1)"
fi
```

Generate each card:

```bash
uv run --with google-genai --with Pillow python "$NB_SCRIPT" \
  -f /tmp/c4-cards/prompt-l1.txt \
  -o /tmp/c4-cards/l1-context.png
```

Repeat for each level.

**Report results:**
- List generated files with sizes
- Remind the user to review the images

### Step 6: Iteration

If the user wants changes:
- Adjust the specific prompt file
- Re-render only that card
- Keep previous versions (append `-v2`, `-v3` etc.)

## Example: Hello World End-to-End

Here's the complete flow for a simple "Todo App":

**1. User runs `/c4-prep`** and models a todo app with:
- One user ("Developer")
- One system ("Todo App")
- Two containers: "Web UI" (React) and "API" (Node.js) and "Database" (SQLite)
- Saves to `todo-app.json`

**2. User runs `/c4-cards todo-app.json`**

**3. Claude reads the JSON**, finds L1 (1 user, 1 system) and L2 (3 containers).

**4. Claude asks:**
- Which levels? → "All levels"
- Style? → "Clean minimal"
- Aspect ratio? → "16:9"

**5. Claude shows ASCII preview:**
```
L1 Context:
         ┌───────────┐
         │ Developer  │
         └─────┬──────┘
               │ Manages todos (HTTPS)
               ▼
        ┌──────────────┐
        │   Todo App   │
        └──────────────┘

L2 Containers:
         ┌───────────┐
         │ Developer  │
         └─────┬──────┘
               │ Uses (HTTPS)
               ▼
        ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
        │   Web UI     │────▶│     API      │────▶│   Database   │
        │   (React)    │     │  (Node.js)   │     │   (SQLite)   │
        └──────────────┘     └──────────────┘     └──────────────┘
```

User confirms: "Looks good!"

**6. Claude generates prompts and renders:**
```
Generated cards:
- /tmp/c4-cards/l1-context.png (185 KB)
- /tmp/c4-cards/l2-containers.png (243 KB)
```

## Tips

- Run `c4-prep` first if you don't have a workspace JSON — it guides you through the modeling
- Use `playground` after c4-cards if you want an interactive HTML version alongside the PNG cards
- The "Hand-drawn sketch" style works well for early-stage architecture discussions
- The "Clean minimal" style is best for formal documentation
- The "Blueprint" style suits technical presentations
