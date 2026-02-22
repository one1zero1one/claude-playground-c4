# C4 Architecture Template

Use this template when the playground visualizes software architecture using the C4 model: system context, container, and component diagrams with drill-down navigation. The data comes from a Structurizr workspace JSON model embedded in the HTML.

## Layout

```
+----------------------------------------------+
|  Breadcrumb: Context > System > Container     |
+--------+-------------------------------------+
|        |                                     |
| Side-  |  SVG Canvas                         |
| bar:   |  (nodes + labeled arrows)           |
|        |                                     |
| Level  |  Drag nodes to rearrange.           |
| View   |  Click to drill down.               |
| Group  |  External elements stay at edges.   |
| Show/  |                                     |
| Hide   |  Legend (bottom-left)               |
| Layout |                                     |
| Preset +-------------------------------------+
|        |  Prompt output                      |
|        |  [ Copy Prompt ]                    |
+--------+-------------------------------------+
```

C4 architecture playgrounds use an SVG canvas with drill-down navigation across three levels: System Context (L1), Container (L2), and Component (L3). Users can **drag nodes** to arrange them manually, click elements to zoom in, use breadcrumbs to zoom out, and toggle visibility of external systems, actors, labels, and groups via sidebar controls.

## Data input

The playground consumes a **Structurizr workspace JSON** embedded as a `<script type="application/json" id="c4-model">` block. This JSON follows the Structurizr JSON schema — the industry-standard format for C4 architecture models.

The JSON can be produced by:
- **Structurizr DSL/CLI** (`structurizr-cli export -f json`), feeding the output directly
- **Hand-authored JSON** following the Structurizr workspace schema
- Any tool in the Structurizr ecosystem that exports workspace JSON
- **Claude itself**, generating a model from the codebase context or user's description

If no JSON is provided, Claude should generate a sample model from the codebase context or the user's description, following the Structurizr workspace schema.

### Structurizr JSON structure (subset used)

The template only needs these parts of the Structurizr workspace JSON:

- `model.people[]` — actors/users. Each has `id`, `name`, `description`, `relationships[]`
- `model.softwareSystems[]` — top-level systems. Each has `id`, `name`, `description`, `location` ("External" or omitted for internal), `containers[]`, `relationships[]`
- `model.softwareSystems[].containers[]` — inside systems. Each has `id`, `name`, `description`, `technology`, `group` (optional), `components[]`, `relationships[]`
- `model.softwareSystems[].containers[].components[]` — inside containers. Each has `id`, `name`, `description`, `technology`, `relationships[]`
- Each `relationships[]` entry has: `id`, `sourceId`, `destinationId`, `description`, `technology`
- `views.systemContextViews[]` — which elements appear at L1
- `views.containerViews[]` — which elements appear at L2
- `views.componentViews[]` — which elements appear at L3

IDs are numeric strings (e.g., `"1"`, `"15"`), following Structurizr convention. If no `views` section exists, show all elements at each level.

## Control types for C4 architecture

| Decision | Control | Example |
|---|---|---|
| Current zoom level | Breadcrumb + sidebar buttons | Context / Container / Component |
| Named view | Dropdown (only shown if views exist in JSON) | "Deployment View", "Data Flow" |
| Container groups | Toggle | Show/hide group boundaries |
| External systems | Toggle | Show/hide external systems |
| Actors | Toggle | Show/hide actors (people) |
| Relationship labels | Toggle | Show/hide arrow labels |
| Layout management | Buttons | Reset to Auto Layout |
| Presets | Buttons | Full Context, Container Focus, Component Deep-dive, Minimal |

## Canvas rendering

Use an `<svg>` element with a dark background (`#1a1a2e`). Key patterns:

### Node types and visual rules

Every C4 element renders as a rounded rectangle containing three lines of text:
1. **Name** (bold, larger font)
2. **[Type]** in brackets and **Technology** (smaller, muted)
3. **Description** (smallest, muted, max 2 lines with ellipsis)

Colors by element type (dark theme):

| Element | Fill | Border | Text |
|---|---|---|---|
| Person/Actor | #08427b | #1168bd | #ffffff |
| Software System (internal) | #1168bd | #0b4884 | #ffffff |
| Software System (external) | #999999 | #6b6b6b | #ffffff |
| Container | #438dd5 | #2e6295 | #ffffff |
| Component | #85bbf0 | #5d99c6 | #000000 |
| Database | #438dd5 | #2e6295 | #ffffff (cylinder shape) |

**Person shape:** Render actors with a small circle "head" above the rectangle body, distinguishing them from system boxes.

**Database shape:** When the element's `technology` field contains "database", "db", or "storage" (case-insensitive), render the top of the rectangle with a curved "cylinder lid" SVG path instead of a straight top edge.

### Relationship arrows

- Solid lines with arrowhead markers, using quadratic bezier curves with slight midpoint offset to avoid straight-line overlap
- Label centered on the line, in a small semi-transparent box (`rgba(26, 26, 46, 0.85)`) for readability
- Technology annotation below the label in smaller italic text (e.g., "JSON/HTTPS")
- Arrow color: `#707070` (muted) so they don't compete with boxes
- Arrowhead markers defined per-color in SVG `<defs>`

### Drag-and-drop node positioning

**This is a core feature.** Users must be able to drag nodes to arrange the diagram manually.

**Interaction model:**
- **Mousedown on node** → start drag (track node ID, SVG-space start position, original node position)
- **Mousemove while dragging** → update node position, redraw edges in real time (no full re-layout)
- **Mouseup after drag** → save positions to localStorage, update sidebar indicator
- **Mouseup without movement** → treat as click, trigger drill-down
- **Mousedown on canvas background** → start pan (not drag)

**Coordinate conversion:** Use `svg.createSVGPoint()` + `svg.getScreenCTM().inverse()` to convert screen coordinates to SVG space. This is critical — raw clientX/clientY won't work because the viewBox transforms coordinates.

```javascript
function screenToSVG(clientX, clientY) {
  const svg = document.getElementById('canvas');
  const pt = svg.createSVGPoint();
  pt.x = clientX; pt.y = clientY;
  return pt.matrixTransform(svg.getScreenCTM().inverse());
}
```

**Visual feedback during drag:**
- Apply an SVG drop-shadow filter (`feDropShadow`, flood-color `#5577ff`) to the dragged node
- Thicken the border stroke (2px → 3px) and change border color to `#7799ff`
- Set `cursor: grab` on nodes (becomes `grabbing` during drag via the natural browser behavior)

**Separation from drill-down:** Track a `moved` boolean in drag state. Only trigger drill-down on mouseup if the node was NOT moved. This prevents accidental drill-downs when the user meant to drag.

### Position persistence (localStorage)

Save and restore node positions per view key using localStorage.

```javascript
const STORAGE_KEY = 'c4-playground-positions';

function getSavedPositions(viewKey) {
  try {
    const all = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
    return all[viewKey] || null;
  } catch { return null; }
}

function savePositions(viewKey, nodes) {
  try {
    const all = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
    const positions = {};
    nodes.forEach(n => { positions[n.id] = { x: Math.round(n.x), y: Math.round(n.y) }; });
    all[viewKey] = positions;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(all));
  } catch {}
}

function clearSavedPositions(viewKey) { /* delete key from stored object */ }
```

**Render flow:**
1. On view change: check localStorage for saved positions
2. If found: use saved positions (skip force-directed layout)
3. If not found: run force-directed layout, then auto-save the result
4. On node drag: save immediately after mouseup

**Sidebar indicator:** Show "Custom layout saved" (green text) or "Auto layout" (muted) below the Layout section header. Include a "Reset to Auto Layout" button that clears saved positions and re-runs force-directed.

### Level transitions (drill-down)

The core interaction: clicking (not dragging) a box at L1 zooms into L2, clicking at L2 zooms into L3.

**L1 (Context) -> L2 (Container):**
- Clicked system expands to fill center, showing its containers
- Actors that connected to the system move to the left edge, keeping their arrows
- External systems that connected move to the right edge, keeping their arrows
- Animate with a 300ms ease-out CSS transition (opacity + transform)
- External elements render at 60% opacity with smaller font

**L2 (Container) -> L3 (Component):**
- Clicked container expands to show its components
- Sibling containers from the same system move to edges at reduced opacity
- External connections from L1 that touch this container remain visible
- Same animation pattern

**Zoom out:**
- Click any breadcrumb segment to return to that level
- Reverse animation

### Layout algorithm

**CRITICAL: Use a virtual canvas, not the viewport.** Layout on a large virtual space (e.g., 3000x2000) and let the SVG viewBox auto-fit to the bounding box of laid-out nodes. Never constrain nodes to the visible viewport — this causes overlapping when there are many elements.

**Initial placement by category (before force-directed):**
- Actors on the far left, well-spaced vertically (120px apart)
- Internal systems/containers in a grid in the center (350px column spacing, 250px row spacing)
- External systems in a column on the right (180px apart, staggered horizontally)

**Force-directed constants (tuned for C4 diagrams with 200x90px nodes):**

```javascript
const IDEAL_EDGE_LEN = 350;   // target distance between connected nodes
const REPULSION_K = 50000;    // repulsion strength — MUST be high for large nodes
const ATTRACTION_K = 0.005;   // attraction along edges
const GRAVITY_K = 0.0008;     // very light center pull
const ITERATIONS = 120;       // simulation steps
const DAMPING = 0.85;         // velocity damping
const VELOCITY_SCALE = 0.3;   // velocity application scale
```

**Why these values matter:** The original template used `repulsion=5000` and `idealDistance=200`. With 200px-wide nodes, this causes constant overlap. The repulsion must be at least 10x higher to create readable spacing. The ideal edge length must exceed the node width by at least 150px.

```javascript
for (let iter = 0; iter < ITERATIONS; iter++) {
  // Repulsion between all pairs
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const a = nodes[i], b = nodes[j];
      const dx = a.x - b.x, dy = a.y - b.y;
      const dist = Math.max(Math.sqrt(dx*dx + dy*dy), 1);
      const f = REPULSION_K / (dist * dist);
      a.vx += (dx/dist)*f;  a.vy += (dy/dist)*f;
      b.vx -= (dx/dist)*f;  b.vy -= (dy/dist)*f;
    }
  }
  // Attraction along edges
  edges.forEach(e => {
    const dx = e.target.x - e.source.x, dy = e.target.y - e.source.y;
    const dist = Math.max(Math.sqrt(dx*dx + dy*dy), 1);
    const f = (dist - IDEAL_EDGE_LEN) * ATTRACTION_K;
    e.source.vx += (dx/dist)*f;  e.source.vy += (dy/dist)*f;
    e.target.vx -= (dx/dist)*f;  e.target.vy -= (dy/dist)*f;
  });
  // Light center gravity
  nodes.forEach(n => {
    n.vx += (cx - n.x) * GRAVITY_K;
    n.vy += (cy - n.y) * GRAVITY_K;
  });
  // Apply velocity with damping (NO boundary clamping)
  nodes.forEach(n => {
    n.x += n.vx * VELOCITY_SCALE;
    n.y += n.vy * VELOCITY_SCALE;
    n.vx *= DAMPING;  n.vy *= DAMPING;
  });
}
```

**Auto-fit viewBox:** After layout, compute the bounding box of all nodes (with padding) and set the SVG `viewBox` to fit. This ensures the diagram is always fully visible regardless of how spread out the layout is.

```javascript
function computeViewBox(nodes) {
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  nodes.forEach(n => {
    minX = Math.min(minX, n.x - n.w/2);
    minY = Math.min(minY, n.y - n.h/2);
    maxX = Math.max(maxX, n.x + n.w/2);
    maxY = Math.max(maxY, n.y + n.h/2);
  });
  const pad = 60;
  return { x: minX - pad, y: minY - pad, w: (maxX-minX) + pad*2, h: (maxY-minY) + pad*2 };
}
```

### Rendering architecture

Separate layout from drawing. Maintain a `currentNodes` array as a live reference that drag handlers can mutate directly:

```javascript
let currentNodes = [];      // live node positions
let currentNodeMap = {};    // id → node lookup
let currentRels = [];       // current view's relationships

function renderSVG(skipLayout) {
  if (!skipLayout) {
    // Check saved positions or run force-directed
    currentNodes = hasSavedPositions(viewKey) ? restorePositions() : layoutNodes(elementIds);
  }
  drawSVG();  // Renders currentNodes to SVG
}

function drawSVG() {
  // Pure rendering — reads currentNodes, writes SVG innerHTML
  // Called by both renderSVG and drag handler
}
```

This split is critical for drag performance — `drawSVG()` is fast (just string building), while `layoutNodes()` runs 120 iterations of force-directed simulation.

### Group rendering

When containers have a `group` field, draw a dashed rounded rectangle (`stroke-dasharray: 8,4`) around all containers in the same group, with a label in the top-left corner. Group boundary color: `#555555`. Groups can be toggled on/off via sidebar.

### Zoom controls

Include +/- buttons and a reset button for SVG viewBox zoom and pan, following the same pattern as code-map. Zoom and pan should call `renderSVG(true)` (skip layout) since they only change the viewBox.

## Prompt output for C4 architecture

The prompt describes the architecture at the current zoom level in natural language. Only describe what is currently visible. If external elements are hidden, don't mention them.

### L1 (Context):
> "[System] is used by [Actor A] to [relationship label] and by [Actor B] to [relationship label]. It depends on [External System] for [relationship label]. The system [description]."

### L2 (Container):
> "[System] contains [N] containers: [Container A] ([technology]), [Container B] ([technology]), ... [Container A] communicates with [Container B] via [label] ([technology]). External actor [Actor] connects to [Container A] to [label]."

### L3 (Component):
> "[Container] ([technology]) is composed of [N] components: [Component A] ([technology]) — [description], ... [Component A] depends on [Component B] for [label]."

## State management

Single state object with level stack for navigation:

```javascript
const state = {
  level: 'context',           // 'context' | 'container' | 'component'
  focusSystemId: null,        // which system we drilled into
  focusContainerId: null,     // which container we drilled into
  activeView: 'default',      // named view from model
  showExternals: true,
  showActors: true,
  showLabels: true,
  showGroups: true,
  zoom: 1,
  panX: 0, panY: 0,
};

const dragState = {
  nodeId: null,       // ID of node being dragged
  startX: 0, startY: 0,  // SVG coords at drag start
  origX: 0, origY: 0,    // node position at drag start
  moved: false,           // true if mouse moved during drag
};

function updateAll() {
  renderBreadcrumb();
  renderSidebar();
  renderSVG();
  updatePrompt();
}
```

## Presets

| Preset | Level | Externals | Actors | Labels | Groups |
|---|---|---|---|---|---|
| Full Context | L1 | on | on | on | n/a |
| Container Focus | L2 (first system) | off | off | on | on |
| Component Deep-dive | L3 (first container of first system) | off | off | on | off |
| Minimal | L1 | off | off | off | n/a |

Presets snap all controls to the defined configuration and call `updateAll()`.

## Pre-populating with real data

When building for a specific system:
- Embed the Structurizr workspace JSON as-is in the `<script id="c4-model">` block
- The JSON contains all levels, so the playground works immediately with drill-down
- If the JSON only contains L1+L2 (no components), disable L3 drill-down gracefully
- Default view: L1 Context with all elements visible (Full Context preset)

If no JSON is provided, generate a model from the user's description or codebase context, following the Structurizr workspace schema structure.

## Legend

Render a small legend in the bottom-left corner of the SVG showing:
- Color swatches for each element type (Person, Internal System, External System, Container, Component)
- Arrow style indicator
- Current level indicator

The legend should be semi-transparent and not interfere with the diagram.

## Example topics

- Microservices architecture (API gateway, services, databases, message brokers)
- Monolith internals (modules, layers, shared libraries)
- Platform overview (user-facing apps, backend services, infrastructure)
- Data platform (ingestion, processing, storage, serving layers)
- CI/CD pipeline architecture (source control, build, test, deploy, monitor)
- Home automation system (sensors, controllers, dashboards, integrations)
- SaaS product (web app, API, workers, databases, third-party services)
