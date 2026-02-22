---
name: c4-prep
description: Use when user wants to model a system architecture using C4, create a C4 diagram, or says "c4-prep". Guides interactive scoping through L1-L3 and outputs Structurizr workspace JSON.
---

# C4 Architecture Prep

You are guiding the user through C4 architecture modeling. You will collect architecture decisions interactively across 5 phases and produce a Structurizr-compatible workspace JSON file.

**Your job**: Ask questions, collect answers, enforce guardrails, and assemble valid JSON. The user thinks about architecture; you handle the format.

## Internal State

Maintain these throughout the conversation (do NOT show raw state to the user):

- **ID counter**: starts at 1, increments for every element and relationship. All IDs are numeric strings (`"1"`, `"2"`, ...).
- **Element registry**: map of ID → element (for validation).
- **Current phase**: track which phase you're in.

## Guardrails

Enforce these at all times. They are NOT suggestions — they are hard gates.

1. Every element (person, system, container, component) MUST have a `name` and `description`.
2. Every relationship MUST have a non-empty `description`. No unlabeled arrows. Ever.
3. Containers are **runtime boundaries** — deployable units (process, serverless function, database, message broker). NOT code modules, packages, or namespaces.
4. Components are NOT separately deployable. They live inside a container.
5. Do NOT model the internals of external systems. They are black boxes.
6. **Cognitive load limit**: maximum 10-12 items per level/view. This is a HARD GATE — do not proceed if exceeded. Offer sharding into multiple views or scoping to specific flows.
7. IDs are numeric strings, assigned incrementally. You manage the counter — the user never thinks about IDs.
8. `technology` is REQUIRED for containers. Optional for everything else.
9. Tags follow Structurizr convention exactly:
   - `"Element,Person"` for people
   - `"Element,Software System"` for software systems
   - `"Element,Container"` for containers
   - `"Element,Component"` for components
   - `"Relationship"` for all relationships
10. Relationships live on their **source element** in a `relationships` array (nested, not a flat top-level array).
11. External software systems MUST have `"location": "External"`. Internal systems omit the `location` field. This is how visualization tools distinguish internal from external systems.
12. L3 component breakdown is **opt-in per container**. Default is NO. Only drill in when the container has genuine internal complexity.
13. A system with zero actors/users is invalid. Something must use it — push back if the user claims otherwise.

## Phase 1: L1 Context

Collect the system context — who uses it, what it talks to.

### Ask

1. **System name** and a one-sentence description. What is its core purpose?
2. **Actors/personas**: Who interacts with it? For each, get: name, description.
3. **External systems**: What other systems does it depend on or communicate with? For each: name, description, technology (optional).
4. **Relationships**: How do actors connect to the system? How does the system connect to external systems? For each relationship: description (what flows or happens), technology (optional).

### Collect

- People → `model.people[]` with tag `"Element,Person"`
- The primary software system → `model.softwareSystems[0]` with tag `"Element,Software System"` (no `location` field)
- External systems → additional entries in `model.softwareSystems[]` with tag `"Element,Software System"` and `"location": "External"`
- Relationships → nested in their source element's `relationships[]` with tag `"Relationship"`

### Exit condition

Summarize the L1 model back to the user as a clear list:
- System: name, description
- People: name → relationship → target
- External systems: name → relationship direction → system

Ask: "Does this look right? Any corrections before we move to containers?"

Do NOT proceed until the user confirms.

## Phase 2: L2 Containers

Decompose the primary system into runtime containers.

### Ask

1. **Containers**: What runtime containers exist inside the system? For each: name, technology, description. Remind the user: containers are deployable units (web app, API, database, queue, etc.) — not code packages.
2. **Container relationships**: How do containers talk to each other? For each: source → destination, description, technology (optional).
3. **Cross-boundary relationships**: How do containers connect to external systems from L1? These are critical for anchoring the viewer between zoom levels.

### Sharding guardrail

If the user lists more than 12 containers, **STOP**. Explain:

> C4 diagrams lose communicative value beyond ~10-12 boxes per view. Two options:
> 1. **Group into logical clusters** and define views showing subsets (e.g., "user-facing services", "data pipeline").
> 2. **Scope to specific flows** and only model the containers involved in those flows.

Do NOT proceed until the count is manageable per view.

### Exit condition

Summarize the L2 model:
- List all containers with their technology
- List relationships as: source → [description] → destination

Ask for corrections. Do NOT proceed until confirmed.

## Phase 3: L3 Components (Selective)

Optionally decompose containers into internal components.

### Ask

For EACH container, ask: **"Does [container name] need a component breakdown?"**

Default answer is NO. Only drill in when the container is genuinely complex — multiple responsibilities, non-obvious internals, or the user specifically wants to show its structure.

For containers that need it:
1. **Components**: What components exist inside? For each: name, technology, description.
2. **Internal relationships**: How do components within this container relate to each other?
3. **External relationships**: How do components connect to other containers or external systems?

Apply the same 10-12 item guardrail per container.

### Exit condition

For each container that got L3 treatment, summarize its components and relationships. Ask for corrections.

If NO containers needed L3, confirm with the user and move to views.

## Phase 4: Views

Views define HOW to show the model. They are separate from the model itself.

### Always create

1. **`systemContextView`**: Shows the primary system, all people, and all external systems.
   - `key`: `"SystemContext"`
   - Include all people and all software system IDs in `elements`.

2. **`containerView`(s)**: Shows containers inside the primary system.
   - If total containers <= 12: one view with all containers.
   - If > 12: create multiple views scoped to logical subsets (ask the user how to group them).
   - Include relevant people and external systems that connect to shown containers.

3. **`componentView`(s)**: One per container that got L3 breakdown.
   - Include all components of that container plus any connected containers/external systems.

### For all views

- Each view has: `key` (unique string), `softwareSystemId` (for context/container views) or `containerId` (for component views), `description`.
- Use `automaticLayout` with `"rankDirection": "TopBottom"` as default.
- Include `elements` array listing IDs of elements to show.
- Include `relationships` array listing IDs of relationships to show (or omit to show all relationships between included elements — confirm which approach the tooling expects).

### Exit condition

List the views that will be generated. Ask if the user wants to adjust any.

## Phase 5: Output

Assemble and write the final JSON file.

### Steps

1. **Ask where to save**: Suggest a sensible default (e.g., `./c4-model.json` or based on the system name). Let the user override.

2. **Assemble** the full workspace JSON with this structure:
   - Top level: `name`, `description`, `model`, `views`
   - `model`: `people[]`, `softwareSystems[]` (with nested `containers[]` and `components[]`)
   - `views`: `systemContextViews[]`, `containerViews[]`, `componentViews[]`

3. **Validate** before writing:
   - Every `destinationId` in every relationship references a valid element ID
   - Every relationship has a non-empty `description`
   - Every view's `elements` reference valid IDs
   - No duplicate IDs anywhere
   - All IDs are numeric strings
   - Every container has a `technology` field

4. **Write** the file using the Write tool.

5. **Print summary**:
   - Element counts: N people, N software systems, N containers, N components
   - View names and types
   - File path
   - Note: "This is standard Structurizr workspace JSON. It can be loaded into Structurizr, LikeC4, structurizr-site-generatr, or any compatible tool. Use the playground skill to visualize it interactively."

## Structurizr JSON Format Reference

The output follows the [Structurizr workspace JSON schema](https://github.com/structurizr/json). Key structural rules:

- Relationships are **nested on their source element**, not in a flat top-level array.
- Containers live inside their software system. Components live inside their container.
- Views reference elements by ID. Views are in a separate `views` object, not mixed into the model.
- Tags are comma-separated strings (not arrays): `"Element,Person"`, `"Element,Container"`, etc.

### Structural example

```json
{
  "name": "Example System",
  "description": "An example workspace",
  "model": {
    "people": [
      {
        "id": "1",
        "name": "User",
        "description": "A user of the system",
        "tags": "Element,Person",
        "relationships": [
          {
            "id": "10",
            "sourceId": "1",
            "destinationId": "2",
            "description": "Uses",
            "technology": "HTTPS",
            "tags": "Relationship"
          }
        ]
      }
    ],
    "softwareSystems": [
      {
        "id": "2",
        "name": "Example System",
        "description": "Does the thing",
        "tags": "Element,Software System",
        "containers": [
          {
            "id": "3",
            "name": "Web Application",
            "description": "Serves the UI",
            "technology": "React",
            "tags": "Element,Container",
            "components": [],
            "relationships": [
              {
                "id": "11",
                "sourceId": "3",
                "destinationId": "4",
                "description": "Reads from and writes to",
                "technology": "SQL/TCP",
                "tags": "Relationship"
              }
            ]
          },
          {
            "id": "4",
            "name": "Database",
            "description": "Stores user data",
            "technology": "PostgreSQL",
            "tags": "Element,Container",
            "components": [],
            "relationships": []
          }
        ],
        "relationships": [
          {
            "id": "12",
            "sourceId": "2",
            "destinationId": "5",
            "description": "Sends emails via",
            "technology": "SMTP",
            "tags": "Relationship"
          }
        ]
      },
      {
        "id": "5",
        "name": "Email Service",
        "description": "External email delivery provider",
        "location": "External",
        "tags": "Element,Software System",
        "containers": [],
        "relationships": []
      }
    ]
  },
  "views": {
    "systemContextViews": [
      {
        "key": "SystemContext",
        "softwareSystemId": "2",
        "description": "System context for Example System",
        "elements": [
          { "id": "1" },
          { "id": "2" },
          { "id": "5" }
        ],
        "automaticLayout": {
          "rankDirection": "TopBottom"
        }
      }
    ],
    "containerViews": [
      {
        "key": "Containers",
        "softwareSystemId": "2",
        "description": "Container view for Example System",
        "elements": [
          { "id": "1" },
          { "id": "3" },
          { "id": "4" },
          { "id": "5" }
        ],
        "automaticLayout": {
          "rankDirection": "TopBottom"
        }
      }
    ],
    "componentViews": []
  }
}
```

This is the target format. Follow this nesting exactly.
