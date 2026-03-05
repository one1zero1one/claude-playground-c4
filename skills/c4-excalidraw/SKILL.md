---
name: c4-excalidraw
description: Render C4 architecture diagrams as editable Excalidraw files from Structurizr workspace JSON. Produces .excalidraw JSON you can open, edit, and rearrange in excalidraw.com or the desktop app. Use when the user asks for "excalidraw c4", "editable c4 diagram", or wants a hand-editable architecture visualization.
allowed-tools: Write, Read, Bash, Grep, Glob, Edit
---

# C4 Excalidraw Diagrams

Render C4 architecture models as editable Excalidraw files from Structurizr workspace JSON. The output is `.excalidraw` JSON — open it in excalidraw.com, the desktop app, or any Excalidraw-compatible tool. Drag nodes, add annotations, export to PNG/SVG.

Works with the Structurizr workspace JSON produced by `c4-prep`, or any Structurizr-compatible JSON.

## How to execute

Parse `$ARGUMENTS` to determine the mode:
- `<path-to-json>` — Load a Structurizr workspace JSON and render it
- (empty) — Ask the user to point to a JSON file, or offer to run `c4-prep` first

### Step 1: Load the C4 Model

**If a JSON path is provided:**
- Read the Structurizr workspace JSON file
- Extract: people, software systems (internal + external), containers, components, relationships
- Identify which C4 levels have content (L1 always, L2 if containers exist, L3 if components exist)

**If no path:**
- Look for `*.json` files in the current directory that look like Structurizr workspace files
- If found, suggest them
- If not found, ask: "Do you have a Structurizr workspace JSON? Run `/c4-prep` first to build one from your codebase."

### Step 2: Determine Which Levels to Render

Ask the user (use AskUserQuestion):
- **Which levels?** Options: "All levels", "L1 Context only", "L2 Containers only", "L3 Components only"

Generate one `.excalidraw` file per level. This keeps each file focused and manageable.

### Step 3: Build Excalidraw JSON for Each Level

For each selected level, generate an Excalidraw JSON file by:
1. Mapping C4 elements to Excalidraw shapes
2. Positioning elements using the layout strategy
3. Drawing arrows for relationships
4. Adding boundary rectangles where needed
5. Adding a title and legend

#### File Structure

Each `.excalidraw` file follows this structure:

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "c4-excalidraw",
  "elements": [...],
  "appState": {
    "viewBackgroundColor": "#ffffff",
    "gridSize": 20
  },
  "files": {}
}
```

### C4 Color Palette

These colors follow C4 conventions and work well in Excalidraw's white-background canvas.

| C4 Element | Fill | Stroke | Text Color |
|---|---|---|---|
| Person | `#08427b` | `#073b6e` | `#ffffff` |
| Software System (internal) | `#1168bd` | `#0e5ca3` | `#ffffff` |
| Software System (external) | `#999999` | `#777777` | `#ffffff` |
| Container | `#438dd5` | `#3a7aba` | `#ffffff` |
| Container (database) | `#438dd5` | `#3a7aba` | `#ffffff` |
| Container (queue) | `#438dd5` | `#3a7aba` | `#ffffff` |
| Component | `#85bbf0` | `#6fa8e0` | `#1e3a5f` |
| Boundary | `transparent` | `#888888` | `#888888` |
| Arrow | — | `#707070` | `#555555` |

### Element Templates

#### Person

A person is a rounded rectangle with the person's name, and a small circle "head" above it.

**Head circle:**
```json
{
  "type": "ellipse",
  "id": "person_{id}_head",
  "x": {center_x - 15}, "y": {y - 40},
  "width": 30, "height": 30,
  "strokeColor": "#073b6e",
  "backgroundColor": "#08427b",
  "fillStyle": "solid",
  "strokeWidth": 2, "strokeStyle": "solid",
  "roughness": 0, "opacity": 100,
  "angle": 0, "seed": {unique},
  "groupIds": ["person_{id}"],
  "boundElements": null, "roundness": {"type": 2}
}
```

**Body rectangle:**
```json
{
  "type": "rectangle",
  "id": "person_{id}_body",
  "x": {x}, "y": {y},
  "width": 160, "height": 70,
  "strokeColor": "#073b6e",
  "backgroundColor": "#08427b",
  "fillStyle": "solid",
  "strokeWidth": 2, "strokeStyle": "solid",
  "roughness": 0, "opacity": 100,
  "roundness": {"type": 3},
  "groupIds": ["person_{id}"],
  "boundElements": [{"id": "person_{id}_name", "type": "text"}]
}
```

**Name text (centered in body):**
```json
{
  "type": "text",
  "id": "person_{id}_name",
  "x": {x + 10}, "y": {y + 8},
  "width": 140, "height": 25,
  "text": "{name}",
  "originalText": "{name}",
  "fontSize": 16, "fontFamily": 3,
  "textAlign": "center", "verticalAlign": "top",
  "strokeColor": "#ffffff",
  "containerId": "person_{id}_body",
  "lineHeight": 1.25
}
```

**Description text (below name, inside body):**
```json
{
  "type": "text",
  "id": "person_{id}_desc",
  "x": {x + 10}, "y": {y + 35},
  "width": 140, "height": 20,
  "text": "[Person]",
  "originalText": "[Person]",
  "fontSize": 12, "fontFamily": 3,
  "textAlign": "center", "verticalAlign": "top",
  "strokeColor": "#cccccc",
  "containerId": "person_{id}_body",
  "lineHeight": 1.25
}
```

#### Software System / Container / Component

All are rounded rectangles with three lines of text: name (bold via size), type tag, and description.

**Rectangle:**
```json
{
  "type": "rectangle",
  "id": "elem_{id}",
  "x": {x}, "y": {y},
  "width": 200, "height": 100,
  "strokeColor": "{stroke from palette}",
  "backgroundColor": "{fill from palette}",
  "fillStyle": "solid",
  "strokeWidth": 2, "strokeStyle": "solid",
  "roughness": 0, "opacity": 100,
  "roundness": {"type": 3},
  "boundElements": [
    {"id": "elem_{id}_text", "type": "text"},
    ... // arrow bindings added later
  ]
}
```

**Text (centered in rectangle):**
```json
{
  "type": "text",
  "id": "elem_{id}_text",
  "x": {x + 10}, "y": {y + 10},
  "width": 180, "height": 80,
  "text": "{name}\n[{type tag}]\n{short description}",
  "originalText": "{name}\n[{type tag}]\n{short description}",
  "fontSize": 14, "fontFamily": 3,
  "textAlign": "center", "verticalAlign": "middle",
  "strokeColor": "{text color from palette}",
  "containerId": "elem_{id}",
  "lineHeight": 1.25
}
```

**Type tags:**
- Software System (internal): `[Software System]`
- Software System (external): `[External System]`
- Container: `[Container: {technology}]`
- Container (database): `[Database: {technology}]`
- Container (queue): `[Queue: {technology}]`
- Component: `[Component: {technology}]`

**Database detection:** If `technology` contains "database", "db", "postgres", "mysql", "mongo", "redis", "sqlite", "dynamo", "sql" (case-insensitive), tag as database.

**Queue detection:** If `technology` contains "queue", "mq", "rabbit", "kafka", "sqs", "pubsub", "nats", "event" (case-insensitive), tag as queue.

#### Boundary (Dashed Rectangle)

Used for System_Boundary at L2 and Container_Boundary at L3.

```json
{
  "type": "rectangle",
  "id": "boundary_{id}",
  "x": {x - 20}, "y": {y - 50},
  "width": {calculated to contain all children + padding},
  "height": {calculated to contain all children + padding},
  "strokeColor": "#888888",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 2, "strokeStyle": "dashed",
  "roughness": 0, "opacity": 100,
  "roundness": {"type": 3},
  "boundElements": null
}
```

**Boundary label (free-floating text above top-left corner):**
```json
{
  "type": "text",
  "id": "boundary_{id}_label",
  "x": {boundary_x + 10}, "y": {boundary_y + 10},
  "width": 200, "height": 20,
  "text": "{system or container name} [boundary]",
  "originalText": "{system or container name} [boundary]",
  "fontSize": 14, "fontFamily": 3,
  "textAlign": "left", "verticalAlign": "top",
  "strokeColor": "#888888",
  "containerId": null,
  "lineHeight": 1.25
}
```

#### Arrow (Relationship)

```json
{
  "type": "arrow",
  "id": "rel_{id}",
  "x": {source_center_x}, "y": {source_center_y},
  "width": {dx}, "height": {dy},
  "strokeColor": "#707070",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 2, "strokeStyle": "solid",
  "roughness": 0, "opacity": 100,
  "points": [[0, 0], [{dx}, {dy}]],
  "startBinding": {"elementId": "{source_shape_id}", "focus": 0, "gap": 4},
  "endBinding": {"elementId": "{target_shape_id}", "focus": 0, "gap": 4},
  "startArrowhead": null,
  "endArrowhead": "arrow"
}
```

**Arrow label (free-floating text near arrow midpoint):**
```json
{
  "type": "text",
  "id": "rel_{id}_label",
  "x": {midpoint_x - 60}, "y": {midpoint_y - 20},
  "width": 120, "height": 20,
  "text": "{description}",
  "originalText": "{description}",
  "fontSize": 12, "fontFamily": 3,
  "textAlign": "center", "verticalAlign": "top",
  "strokeColor": "#555555",
  "containerId": null,
  "lineHeight": 1.25
}
```

If the relationship has a technology, append it: `"{description}\n[{technology}]"`

### Layout Strategy

Use a column-based layout for clean C4 diagrams.

#### L1 — System Context

```
Column 1 (x=100):     Column 2 (x=500):     Column 3 (x=900):
  People                 Internal Systems       External Systems
  (stacked vertically,   (stacked vertically,   (stacked vertically,
   180px apart)           180px apart)           180px apart)
```

- Title text at y=30, centered across all columns
- People at x=100, starting y=120, spaced 180px apart
- Internal systems at x=500, starting y=120, spaced 180px apart
- External systems at x=900, starting y=120, spaced 180px apart

#### L2 — Container

```
Column 1 (x=100):     Boundary (x=350):                    Column 3 (x=950):
  People               ┌─────────────────────────────┐       External Systems
                       │ System Name [boundary]       │
                       │                              │
                       │  Container  Container        │
                       │  Container  Container        │
                       │                              │
                       └─────────────────────────────────────┘
```

- People on the left at x=100
- System boundary starts at x=350
- Containers inside boundary in a 2-column grid: x offsets 380 and 620, y spacing 140px
- External systems on the right at x=950
- Boundary size calculated to contain all containers with 40px padding

#### L3 — Component

Same pattern as L2 but:
- Container boundary instead of system boundary
- Components inside the boundary
- Sibling containers on the right instead of external systems
- External systems further right

### Step 4: Collect Relationships

Relationships in Structurizr JSON are nested on their source element. To collect all relationships for a given level:

1. Walk every element in the model (people, systems, containers, components)
2. For each element's `relationships[]`, check if both `sourceId` and `destinationId` refer to elements visible in the current view
3. If yes, include the relationship
4. Build a lookup table: `rawId → excalidrawShapeId` for all elements in the current view

Map source/destination IDs to the Excalidraw shape IDs you assigned (e.g., `elem_3`, `person_1_body`).

**For arrow bindings:** When creating arrows, also update the target shapes' `boundElements` arrays to include the arrow ID. This is required for Excalidraw to properly bind arrows to shapes.

### Step 5: Add Title and Legend

**Title** — free-floating text at top center:
```json
{
  "type": "text",
  "id": "title",
  "x": {center_x - 150}, "y": 30,
  "width": 300, "height": 30,
  "text": "{System Name} — {Level Name}",
  "fontSize": 24, "fontFamily": 3,
  "textAlign": "center", "verticalAlign": "top",
  "strokeColor": "#1e3a5f"
}
```

**Legend** — small color swatches in bottom-left showing what each color means. Use small (20x12) rectangles with labels.

### Step 6: Build Section by Section

**Do NOT generate the entire elements array in one pass.** For diagrams with more than ~10 elements, build section by section:

1. **Create the base file** with the JSON wrapper and title/legend elements
2. **Add people** as a section
3. **Add systems/containers/components** as a section
4. **Add the boundary rectangle** (calculated after positioning children)
5. **Add arrows** last (after all shapes have their final positions)
6. **Update boundElements** on all shapes that arrows connect to

Use descriptive string IDs throughout (e.g., `"person_1_body"`, `"elem_3"`, `"rel_10"`) so cross-references are readable.

Namespace seeds by section (section 1: 100xxx, section 2: 200xxx, etc.) to avoid collisions.

### Step 7: Save Files

**File naming:** `{system-name}-c4-{level}.excalidraw`
- L1: `{system-name}-c4-context.excalidraw`
- L2: `{system-name}-c4-containers.excalidraw`
- L3: `{system-name}-c4-{container-name}-components.excalidraw`

**Default location:** Same directory as the input JSON file, or project root.

### Step 8: Render & Validate (if available)

Check if the excalidraw render script exists:

```bash
RENDER_SCRIPT=$(find ~/.claude/skills/excalidraw-diagram/references -name 'render_excalidraw.py' 2>/dev/null | head -1)
```

**If found**, run the render-view-fix loop for each generated file:

1. **Render:** `cd ~/.claude/skills/excalidraw-diagram/references && uv run python render_excalidraw.py <path-to-file.excalidraw>`
2. **View:** Read the generated PNG with the Read tool
3. **Audit:** Check for:
   - Text clipped by or overflowing containers
   - Overlapping elements
   - Arrows crossing through elements
   - Uneven spacing
   - Labels not clearly anchored to their elements
   - Boundary rectangle too small or too large for its children
4. **Fix:** Edit the JSON to address issues
5. **Re-render and re-view** until clean

Typically takes 2-3 iterations per file.

**If not found**, skip rendering and tell the user:
```
Note: Install the excalidraw-diagram skill for automatic PNG rendering and validation.
Without it, open the .excalidraw files in excalidraw.com to preview.
```

### Step 9: Report

```
Created C4 Excalidraw diagrams:
- {system-name}-c4-context.excalidraw — L1: {N} people, {N} systems
- {system-name}-c4-containers.excalidraw — L2: {N} containers
- {system-name}-c4-{container}-components.excalidraw — L3: {N} components

Open in excalidraw.com or the Excalidraw desktop app to view and edit.
Tip: Use /c4-mermaid for lightweight HTML, /playground for interactive SVG, /c4-cards for PNG exports.
```

## Element Size Reference

| Element Type | Width | Height |
|---|---|---|
| Person (body) | 160 | 70 |
| Person (head) | 30 | 30 |
| Software System | 200 | 100 |
| Container | 200 | 100 |
| Component | 180 | 90 |
| Boundary padding | 40px on each side | 60px top (for label), 40px bottom |

## Edge Cases

- **No L2 content:** Only generate L1 file.
- **No L3 content:** Generate L1 and L2 files only.
- **Multiple containers with components:** Generate one L3 file per container.
- **Many containers (>6):** Use a 3-column grid inside the boundary instead of 2-column. Adjust boundary width.
- **Relationships with missing endpoints:** Skip silently.
- **Empty descriptions:** Use the element name as fallback.
- **Long names/descriptions:** Truncate descriptions to 60 characters in the shape text. Widen shapes if names exceed 16 characters (add 8px per extra character).
- **Special characters:** Excalidraw handles unicode natively in the `text` field. No escaping needed.
