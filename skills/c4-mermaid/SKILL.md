---
name: c4-mermaid
description: Render C4 architecture diagrams as interactive Mermaid.js HTML from Structurizr workspace JSON. Lightweight alternative to c4-cards — no API keys, no dependencies, just HTML + Mermaid CDN. Use when the user asks for "mermaid diagram", "mermaid c4", "lightweight c4 diagram", or wants a quick shareable architecture visualization.
allowed-tools: Write, Read, Bash, Grep, Glob
---

# C4 Mermaid Diagrams

Render C4 architecture models as Mermaid.js diagrams in a self-contained HTML file. No API keys, no Python, no external dependencies — just HTML and the Mermaid CDN.

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

### Step 2: Convert to Mermaid C4 Syntax

Transform the Structurizr JSON into Mermaid C4 diagram blocks. Generate one block per level that has content.

#### L1 — System Context (`C4Context`)

```
C4Context
    title System Context — {system.name}

    Person(p{id}, "{name}", "{description}")
    System(s{id}, "{name}", "{description}")
    System_Ext(s{id}, "{name}", "{description}")

    Rel(p{sourceId}, s{destId}, "{description}", "{technology}")
```

Mapping rules:
- `model.people[]` → `Person(p{id}, "{name}", "{description}")`
- `model.softwareSystems[]` without `"location": "External"` → `System(s{id}, "{name}", "{description}")`
- `model.softwareSystems[]` with `"location": "External"` → `System_Ext(s{id}, "{name}", "{description}")`
- All relationships between L1 elements → `Rel(source, dest, "{description}", "{technology}")`

Prefix all IDs with a letter (`p` for people, `s` for systems) because Mermaid C4 IDs must not start with a number.

#### L2 — Container (`C4Container`)

```
C4Container
    title Container Diagram — {system.name}

    Person(p{id}, "{name}", "{description}")

    System_Boundary(sb{systemId}, "{system.name}") {
        Container(c{id}, "{name}", "{technology}", "{description}")
        ContainerDb(c{id}, "{name}", "{technology}", "{description}")
    }

    System_Ext(s{id}, "{name}", "{description}")

    Rel(source, dest, "{description}", "{technology}")
```

Mapping rules:
- People who have relationships to containers → `Person(...)` outside boundary
- Primary system → `System_Boundary(sb{id}, "{name}") { ... }`
- `containers[]` → `Container(c{id}, "{name}", "{technology}", "{description}")`
- If `technology` contains "database", "db", "postgres", "mysql", "mongo", "redis", "sqlite", "dynamo", "sql" (case-insensitive) → use `ContainerDb(...)` instead
- External systems → `System_Ext(...)` outside boundary
- Relationships: collect all relationships from people, containers, and external systems that connect to elements visible at L2

#### L3 — Component (`C4Component`)

Generate one block per container that has components.

```
C4Component
    title Component Diagram — {container.name}

    Container_Boundary(cb{containerId}, "{container.name}") {
        Component(co{id}, "{name}", "{technology}", "{description}")
    }

    Container(c{id}, "{name}", "{technology}", "{description}")
    System_Ext(s{id}, "{name}", "{description}")

    Rel(source, dest, "{description}", "{technology}")
```

Mapping rules:
- Target container → `Container_Boundary(cb{id}, "{name}") { ... }`
- `components[]` → `Component(co{id}, "{name}", "{technology}", "{description}")`
- Sibling containers that connect to components → `Container(...)` outside boundary
- External systems that connect → `System_Ext(...)` outside boundary
- Relationships between visible elements

#### Relationship Gathering

Relationships in Structurizr JSON are nested on their source element. To collect all relationships for a given view:

1. Walk every element in the model (people, systems, containers, components)
2. For each element's `relationships[]`, check if both `sourceId` and `destinationId` refer to elements visible in the current view
3. If yes, include the relationship
4. Use the prefixed IDs (p, s, c, co) that match how you declared the elements

**Important**: An element at L2 might have a relationship targeting a container inside a system. The sourceId/destinationId in the JSON uses the raw numeric IDs — you need to map these to the prefixed IDs you assigned.

Build a lookup table: `rawId → prefixedId` for all elements in the current view before emitting `Rel(...)` lines.

### Step 3: Generate HTML File

Create a single self-contained HTML file with tabbed navigation between levels.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{system.name} — C4 Architecture</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
                         Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', sans-serif;
            background: #1a1a2e;
            color: #e0e0e0;
            line-height: 1.6;
        }

        .header {
            text-align: center;
            padding: 30px 20px 0;
        }

        .header h1 {
            font-size: 1.8rem;
            color: #ffffff;
            margin-bottom: 4px;
        }

        .header .subtitle {
            font-size: 0.9rem;
            color: #888;
        }

        /* Tabs */
        .tabs {
            display: flex;
            justify-content: center;
            gap: 4px;
            padding: 20px 20px 0;
        }

        .tab {
            padding: 10px 24px;
            background: #16213e;
            border: 1px solid #2a2a4a;
            border-bottom: none;
            border-radius: 8px 8px 0 0;
            color: #888;
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: 500;
            transition: all 0.2s;
        }

        .tab:hover {
            color: #bbb;
            background: #1a2744;
        }

        .tab.active {
            background: #0f3460;
            color: #ffffff;
            border-color: #1a5276;
        }

        /* Tab content */
        .tab-content {
            display: none;
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px 30px;
        }

        .tab-content.active {
            display: block;
        }

        .diagram-container {
            background: #16213e;
            border: 1px solid #2a2a4a;
            border-radius: 0 8px 8px 8px;
            padding: 30px;
            margin-bottom: 20px;
            overflow-x: auto;
        }

        .diagram-container .mermaid {
            display: flex;
            justify-content: center;
        }

        /* Key points */
        .key-points {
            background: #16213e;
            border: 1px solid #2a2a4a;
            border-radius: 8px;
            padding: 20px 30px;
        }

        .key-points h2 {
            color: #ffffff;
            font-size: 1.1rem;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid #2a2a4a;
        }

        .key-points h3 {
            color: #ccc;
            font-size: 0.95rem;
            margin-top: 16px;
            margin-bottom: 8px;
        }

        .key-points ul {
            list-style: none;
            padding: 0;
        }

        .key-points li {
            padding: 4px 0;
            color: #aaa;
            font-size: 0.9rem;
        }

        .key-points li::before {
            content: "→ ";
            color: #4a90d9;
        }

        .key-points code {
            background: #1a1a2e;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.85rem;
            color: #8bb4e0;
        }

        .key-points strong {
            color: #e0e0e0;
        }

        /* Light mode */
        @media (prefers-color-scheme: light) {
            body { background: #f5f5f5; color: #333; }
            .header h1 { color: #333; }
            .header .subtitle { color: #666; }
            .tabs .tab { background: #e8e8e8; border-color: #ddd; color: #666; }
            .tabs .tab:hover { background: #ddd; color: #444; }
            .tabs .tab.active { background: #ffffff; color: #333; border-color: #ccc; }
            .diagram-container { background: #ffffff; border-color: #ddd; }
            .key-points { background: #ffffff; border-color: #ddd; }
            .key-points h2 { color: #333; border-bottom-color: #eee; }
            .key-points h3 { color: #555; }
            .key-points li { color: #555; }
            .key-points code { background: #f0f0f0; color: #2d6da3; }
            .key-points strong { color: #333; }
        }

        /* Print */
        @media print {
            body { background: white; color: black; }
            .tabs { display: none; }
            .tab-content { display: block !important; page-break-inside: avoid; }
            .diagram-container, .key-points { border: 1px solid #ddd; box-shadow: none; }
        }

        /* Responsive */
        @media (max-width: 768px) {
            .header h1 { font-size: 1.4rem; }
            .tabs { flex-wrap: wrap; }
            .tab { padding: 8px 16px; font-size: 0.8rem; }
            .diagram-container { padding: 15px; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{system.name}</h1>
        <p class="subtitle">C4 Architecture — Mermaid Diagrams</p>
    </div>

    <div class="tabs">
        <!-- One tab per level that has content -->
        <div class="tab active" onclick="showTab('context')">L1 Context</div>
        <div class="tab" onclick="showTab('container')">L2 Containers</div>
        <!-- Only if L3 exists: -->
        <div class="tab" onclick="showTab('component-{containerId}')">L3 {container.name}</div>
    </div>

    <!-- L1 Context -->
    <div id="tab-context" class="tab-content active">
        <div class="diagram-container">
            <pre class="mermaid">
            <!-- C4Context mermaid code here -->
            </pre>
        </div>
        <div class="key-points">
            <h2>System Context</h2>
            <!-- Key points about L1 -->
        </div>
    </div>

    <!-- L2 Containers -->
    <div id="tab-container" class="tab-content">
        <div class="diagram-container">
            <pre class="mermaid">
            <!-- C4Container mermaid code here -->
            </pre>
        </div>
        <div class="key-points">
            <h2>Containers</h2>
            <!-- Key points about L2 -->
        </div>
    </div>

    <!-- L3 Components (one per container that has components) -->
    <div id="tab-component-{containerId}" class="tab-content">
        <div class="diagram-container">
            <pre class="mermaid">
            <!-- C4Component mermaid code here -->
            </pre>
        </div>
        <div class="key-points">
            <h2>Components — {container.name}</h2>
            <!-- Key points about L3 -->
        </div>
    </div>

    <script>
        mermaid.initialize({
            startOnLoad: true,
            theme: 'dark',
            c4: {
                diagramMarginY: 20,
                c4ShapeMargin: 10,
                c4ShapePadding: 8,
                width: 220,
                height: 120,
                c4BoundaryInRow: 1
            }
        });

        function showTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));

            document.getElementById('tab-' + tabId).classList.add('active');
            event.target.classList.add('active');

            // Re-render mermaid for the newly visible tab
            // (Mermaid may not render hidden elements correctly)
            const container = document.getElementById('tab-' + tabId);
            const mermaidEl = container.querySelector('.mermaid');
            if (mermaidEl && !mermaidEl.getAttribute('data-processed')) {
                mermaid.run({ nodes: [mermaidEl] });
            }
        }
    </script>
</body>
</html>
```

**Important rendering note:** Mermaid does not render elements inside `display: none` containers. Two approaches:

1. **Render all tabs on load, hide after.** Set all tabs visible initially, let Mermaid render, then hide non-active tabs via JS after `mermaid.run()` completes.
2. **Lazy render on tab switch.** Keep raw Mermaid source in a `data-source` attribute, render on first tab activation.

Use approach 1 — it is simpler and avoids flicker:

```javascript
// After mermaid renders all diagrams on load:
document.addEventListener('DOMContentLoaded', () => {
    // Short delay to let mermaid finish rendering
    setTimeout(() => {
        document.querySelectorAll('.tab-content').forEach((el, i) => {
            if (i > 0) el.classList.remove('active');
        });
    }, 500);
});
```

Set ALL `.tab-content` elements to have class `active` in the initial HTML so they are visible when Mermaid runs. Then the DOMContentLoaded handler hides all but the first one.

### Step 4: Key Points Section

For each level, generate a "Key Points" section that documents:

**L1 Context:**
- System name and purpose
- List of actors and what they do
- List of external systems and how they connect
- Number of relationships

**L2 Containers:**
- List of containers with their technology
- Which containers talk to which
- External connections
- Database containers highlighted

**L3 Components:**
- Which container this decomposes
- List of components with technology
- Internal wiring
- External connections from this container

### Step 5: Save and Report

**File naming:** Use the system name in kebab-case: `{system-name}-c4-mermaid.html`

**Default location:** Same directory as the input JSON file, or project root.

**Report:**
```
Created: /path/to/{system-name}-c4-mermaid.html

Rendered levels:
- L1 Context: {N} people, {N} systems ({N} external)
- L2 Containers: {N} containers in {system.name}
- L3 Components: {container.name} ({N} components)

Open in any browser — no setup needed.
Tip: Use /playground for interactive drill-down, /c4-cards for PNG exports.
```

## Mermaid C4 Syntax Reference

### Elements

```
Person(alias, "Label", "Description")
Person_Ext(alias, "Label", "Description")
System(alias, "Label", "Description")
System_Ext(alias, "Label", "Description")
Container(alias, "Label", "Technology", "Description")
ContainerDb(alias, "Label", "Technology", "Description")
ContainerQueue(alias, "Label", "Technology", "Description")
Component(alias, "Label", "Technology", "Description")
ComponentDb(alias, "Label", "Technology", "Description")
```

### Boundaries

```
System_Boundary(alias, "Label") {
    Container(...)
}

Container_Boundary(alias, "Label") {
    Component(...)
}

Enterprise_Boundary(alias, "Label") {
    System(...)
}
```

### Relationships

```
Rel(from, to, "Label")
Rel(from, to, "Label", "Technology")
Rel_D(from, to, "Label", "Technology")   %% downward
Rel_U(from, to, "Label", "Technology")   %% upward
Rel_L(from, to, "Label", "Technology")   %% left
Rel_R(from, to, "Label", "Technology")   %% right
BiRel(from, to, "Label", "Technology")   %% bidirectional
```

### Queue Detection

When a container's `technology` field contains "queue", "mq", "rabbit", "kafka", "sqs", "pubsub", "nats", "event" (case-insensitive), use `ContainerQueue(...)` instead of `Container(...)`.

### ID Prefixing Rules

Mermaid C4 aliases must be valid identifiers (no spaces, cannot start with a digit). Since Structurizr IDs are numeric strings:

| Element type | Prefix | Example |
|---|---|---|
| Person | `p` | `p1`, `p2` |
| Software System | `s` | `s3`, `s5` |
| Container | `c` | `c4`, `c6` |
| Component | `co` | `co7`, `co8` |
| System Boundary | `sb` | `sb3` |
| Container Boundary | `cb` | `cb4` |

## Edge Cases

- **No L2 content:** Only show L1 tab. Skip the tabs UI entirely — just show the single diagram.
- **No L3 content:** Show L1 and L2 tabs only.
- **Multiple containers with components:** Generate one L3 tab per container. Tab label = container name.
- **Relationships with missing endpoints:** Skip silently. Don't crash on invalid JSON.
- **Empty descriptions:** Use the element name as fallback.
- **Long descriptions:** Truncate to 80 characters with "..." for the Mermaid element. Full text goes in Key Points.
- **Special characters in names:** Escape double quotes in names/descriptions (`"` → `#quot;` in Mermaid).
