# Forge OS — Org-Federated Desktop Architecture

> Status: Design  
> Version: 0.3.0-planned  
> Author: Mrinal Aswin  
> Date: 2026-05-14

---

## Vision

Evolve Forge OS from a single-user local tool into a **multi-user, org-aware desktop application** where:

- Documentation never pollutes project code repositories
- Organizational knowledge accumulates automatically across projects
- Git identity is the authentication mechanism — no custom auth infrastructure
- Every user's Forge install is a node in the org's shared knowledge network

---

## Three-Layer System Model

```
┌─────────────────────────────────────────────────────────────────┐
│  Layer 0: Org Repo  (github.com/{org}/forge-knowledge)           │
│  "Knowledge Nucleus"                                             │
│                                                                  │
│  projects/{project-id}/     ← per-project doc archives          │
│  knowledge/{domain}.md      ← distilled org patterns            │
│  patterns/*.md              ← reusable decision patterns        │
│  agents/                    ← org-scoped agent personas         │
│  forge.config.yaml          ← user registry, roles, settings   │
│  learnings/                 ← raw learning deltas from gates    │
└────────────────────┬────────────────────────────────────────────┘
                     │  git pull (read context + learnings)
                     │  git push (write project docs + learnings)
┌────────────────────▼────────────────────────────────────────────┐
│  Layer 1: Forge Desktop App  (per-user install)                  │
│                                                                  │
│  ~/.forge/                  ← global install root               │
│    projects/{project-id}/   ← full .forge/ contents per project │
│    config.yaml              ← local user config, token ref      │
│                                                                  │
│  - Wraps existing HTTP server + dashboard in Electron            │
│  - Authenticates via GitHub/GitLab OAuth (token in OS keychain) │
│  - Resolves org repo from user config or .forge dotfile          │
│  - Syncs ~/.forge/ ↔ org repo on open/close/gate-pass           │
│  - Injects org context into every generation prompt              │
└────────────────────┬────────────────────────────────────────────┘
                     │  reads .forge dotfile
                     │  writes final code artifacts only
┌────────────────────▼────────────────────────────────────────────┐
│  Layer 2: Project Repos  (github.com/{org}/{product})            │
│                                                                  │
│  src/                       ← product code                      │
│  tests/                                                          │
│  Dockerfile                                                      │
│  .forge                     ← pointer dotfile only (not a dir)  │
│                                                                  │
│  No .forge/ directory. No documentation folders.                 │
│  Only final build artifacts written here by the pipeline.        │
└─────────────────────────────────────────────────────────────────┘
```

---

## The `.forge` Dotfile

The only Forge artifact committed to a project repository. Acts as a pointer, not a container.

```yaml
# .forge
version: "0.3.0"
project_id: "a3f8c1d2-4e5f-6789-abcd-ef0123456789"
project_name: "My Product"
org: "github.com/acme/forge-knowledge"
output_dir: "."
```

| Field | Purpose |
|---|---|
| `project_id` | UUID — stable identifier across machines and users |
| `org` | Git URL of the org knowledge repo |
| `output_dir` | Where `15-build/` artifacts are written (default: project root) |

The app reads this file on project open, resolves `~/.forge/projects/{project_id}/`, and pulls from the org repo if not present locally.

---

## Global Install Layout (`~/.forge/`)

Mirrors the current `.forge/` structure but scoped per-project by UUID:

```
~/.forge/
├── config.yaml                      ← user identity, default org, token ref
├── projects/
│   └── {project-id}/
│       ├── 00-raw-input/
│       ├── 00-context/
│       ├── 01-requirements/
│       ├── 02-design/
│       ├── 03-analysis/
│       ├── 04-architecture/
│       ├── 05-delivery/
│       ├── 06-engineering/
│       ├── 07-quality/
│       ├── 08-operations/
│       ├── 09-release/
│       ├── 10-marketing/
│       ├── 11-agents/
│       ├── 12-gates/
│       ├── 13-decisions/
│       ├── 14-assets/
│       ├── 15-build/
│       ├── runs/
│       ├── reviews.json
│       └── project-state.json
└── org-cache/
    └── {org-name}/                  ← local clone of org repo
        ├── projects/
        ├── knowledge/
        ├── patterns/
        ├── agents/
        └── forge.config.yaml
```

---

## Git as Authentication

No custom auth server. Identity and access control are fully delegated to the git host.

### User Flow

```
1. User installs Forge Desktop
2. App prompts: "Connect your GitHub account"
3. OAuth flow → access token stored in OS keychain (not on disk)
4. App reads user's org memberships via GitHub API
5. User selects org → app resolves {org}/forge-knowledge repo
6. App clones org repo to ~/.forge/org-cache/{org-name}/
7. User opens a project repo → app reads .forge dotfile → loads project context
```

### Admin Flow

```
1. Admin creates github.com/{org}/forge-knowledge (private repo)
2. Admin adds forge.config.yaml (roles, settings, shared agents)
3. Admin invites team via GitHub org membership (standard GitHub flow)
4. Team members install Forge Desktop → auto-discover org on login
```

Access control = GitHub repo permissions. No extra permission system to maintain.

---

## Data Flow: Project Lifecycle

```
User opens project repo in Forge Desktop
    → Read .forge dotfile → get project_id + org
    → Pull ~/.forge/projects/{project_id}/ from org repo (if not local)
    → Load org context: knowledge/, patterns/, agents/ from org-cache

User runs Generate (any stage)
    → Org context files injected into generation prompts
    → Output written to ~/.forge/projects/{project_id}/{stage}/
    → Project repo untouched

User passes a gate (all files reviewed)
    → Learning delta extracted: decisions, patterns, risks surfaced
    → Delta written to org repo: learnings/{date}-{project-slug}.md
    → Async push to github.com/{org}/forge-knowledge

Build step runs
    → Artifacts from 15-build/ written to project repo (output_dir)
    → Only code files committed and pushed to project repo
    → Project docs remain in ~/.forge/ and org repo only
```

---

## Continuous Learning Loop

```
Gate passes in any project
    └── Learning delta extracted (decisions, patterns, surfaced risks)
            └── Pushed to org repo: /learnings/{date}-{slug}.md

Distillation agent (runs nightly or on-demand)
    └── Reads all /learnings/*.md
    └── Produces/updates:
            /knowledge/{domain}.md    ← domain expertise accumulation
            /patterns/*.md            ← reusable decision patterns
            /agents/*.md              ← refined agent personas

Next project opens
    └── knowledge/ + patterns/ injected into generation prompts
    └── Org learns faster with each project completed
```

The distillation agent uses the same mechanism as existing stage agents — an AI call with structured prompt, output written as markdown to the org repo.

---

## Desktop App Technology

**Recommended: Electron (Phase 1), migrate to Tauri (Phase 2+)**

| Option | Pros | Cons | Verdict |
|---|---|---|---|
| Electron | Mature, auto-update, code signing, fast | Large binary (~150MB) | Phase 1 choice |
| Tauri | Tiny binary, native, Rust-based | Complex build toolchain | Future target |
| PyWebView | Python-only, lightweight | No auto-update, limited tray | Not recommended |

Electron wraps the existing Python HTTP server + dashboard. The server subprocess model is unchanged. Electron handles:
- Window lifecycle
- System tray
- Auto-update (electron-updater)
- macOS/Windows/Linux builds via GitHub Actions
- OS keychain access (for OAuth tokens)

---

## Implementation Phases

### Phase 1 — Desktop Shell
**Scope**: Electron wrapper around existing server + dashboard  
**Effort**: 2–3 weeks  
**Deliverables**:
- Electron app bootstraps Python server subprocess on launch
- System tray with show/hide, quit
- macOS `.app` + Windows `.exe` builds via GitHub Actions CI
- Auto-update via electron-updater (GitHub Releases as update channel)
- App icon, name, code signing scaffold

### Phase 2 — Git Auth + Org Repo
**Scope**: GitHub OAuth, org discovery, forge-knowledge repo setup  
**Effort**: 2–3 weeks  
**Deliverables**:
- GitHub OAuth flow in Electron (browser-based, token to keychain)
- Org membership resolution via GitHub API
- Org repo clone/pull to `~/.forge/org-cache/`
- `forge.config.yaml` schema and admin tooling
- Org indicator in dashboard UI

### Phase 3 — Global Install + Dotfile Separation
**Scope**: Migrate `.forge/` from project root to `~/.forge/projects/{id}/`  
**Effort**: 2 weeks  
**Deliverables**:
- `.forge` dotfile schema + generation on `forge init`
- `AEOS_REPO_ROOT` / path resolution rewrite (inverts current assumption)
- `~/.forge/` global directory init on first app launch
- Org repo sync: push/pull project docs at open/close
- Migration script for existing `.forge/` installs
- Project repo now contains only `.forge` dotfile + code

### Phase 4 — Org Context Injection
**Scope**: Org knowledge fed into generation prompts  
**Effort**: 1–2 weeks  
**Deliverables**:
- `knowledge/` + `patterns/` + `agents/` loaded from org-cache at generate time
- Prompt injection layer in `stage_runner.py`
- "Org context active" indicator in dashboard Generate view
- Per-project override capability (ignore org context for a stage)

### Phase 5 — Learning Loop + Distillation
**Scope**: Post-gate learning extraction, distillation agent, org knowledge growth  
**Effort**: 3–4 weeks  
**Deliverables**:
- Learning delta extraction on gate pass (AI-assisted summarization)
- Push to org repo `/learnings/`
- Distillation agent: nightly cron or on-demand trigger from dashboard
- Knowledge base view in dashboard (browse org knowledge, patterns, learnings)
- Org repo grows smarter with each project

---

## Key Open Decisions

| Decision | Options | Recommendation |
|---|---|---|
| Git host scope | GitHub only vs multi-provider | GitHub-first, abstract later |
| Desktop wrapper | Electron vs Tauri | Electron for Phase 1 |
| Org repo naming | Convention (`forge-knowledge`) vs user-defined | Convention with override |
| Learning granularity | Per-gate delta vs per-project summary | Per-gate (more frequent signal) |
| Offline mode | Full offline vs online-required | Offline with cached org context |
| Multi-org | One org per user vs multiple | Single active org, switchable |

---

## Constraints + Non-Goals

- The Python stdlib-only constraint applies to the CLI/server only. Electron uses Node.js — this is acceptable as it is the desktop shell layer, not the core engine.
- Project repos must never contain `.forge/` directories. The dotfile (`.forge`) is the only forge artifact in project repos.
- The org repo is a standard git repo. No custom server, no database, no SaaS dependency.
- Users who do not belong to an org can still use Forge in standalone mode (`~/.forge/` only, no org sync).
