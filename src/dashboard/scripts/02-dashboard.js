// ============================================================
// Icons
// ============================================================
const ICONS = {
  sparkles: `<path d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z"/>`,
  check: `<path d="M4.5 12.75l6 6 9-13.5"/>`,
  arrowPath: `<path d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99"/>`,
  externalLink: `<path d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25"/>`,
  gitBranch: `<path d="M6 3v12"/><circle cx="18" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M18 9a9 9 0 01-9 9"/>`,
  cloudUp: `<path d="M12 16.5V9.75m0 0l3 3m-3-3l-3 3M6.75 19.5a4.5 4.5 0 01-1.41-8.775 5.25 5.25 0 0110.233-2.33 3 3 0 013.758 3.848A3.752 3.752 0 0118 19.5H6.75z"/>`,
  eye: `<path d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"/><path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>`,
  wrench: `<path d="M11.42 15.17L17.25 21A2.652 2.652 0 0021 17.25l-5.877-5.877M11.42 15.17l2.496-3.03c.317-.384.74-.626 1.208-.766M11.42 15.17l-4.655 5.653a2.548 2.548 0 11-3.586-3.586l6.837-5.63m5.108-.233c.55-.164 1.163-.188 1.743-.14a4.5 4.5 0 004.486-6.336l-3.276 3.277a3.004 3.004 0 01-2.25-2.25l3.276-3.276a4.5 4.5 0 00-6.336 4.486c.091 1.076-.071 2.264-.904 2.95l-.102.085m-1.745 1.437L5.909 7.5H4.5L2.25 3.75l1.5-1.5L7.5 4.5v1.409l4.26 4.26m-1.745 1.437l1.745-1.437"/>`,
  star: `<path d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.562.562 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.562.562 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z"/>`,
  trendUp: `<path d="M2.25 18L9 11.25l4.306 4.307a11.95 11.95 0 015.814-5.519l2.74-1.22m0 0l-5.94-2.28m5.94 2.28l-2.28 5.941"/>`,
  questionCircle: `<path d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z"/>`,
  server: `<path d="M21.75 17.25v.75a3 3 0 01-3 3h-13.5a3 3 0 01-3-3v-.75m19.5 0a3 3 0 00-3-3H5.25a3 3 0 00-3 3m19.5 0v.75M2.25 11.25h19.5M2.25 6.75h19.5M5.25 6.75V3.75m13.5 3V3.75M5.25 11.25V8.25m13.5 3V8.25"/>`,
  beaker: `<path d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23-.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5"/>`,
};

function icon(name, size = 14) {
  const paths = ICONS[name] || '';
  return `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0">${paths}</svg>`;
}

const ISSUE_TYPE_ICONS = {
  bug: 'wrench',
  feature: 'star',
  improvement: 'trendUp',
  question: 'questionCircle',
};

// ============================================================
// Markdown Renderer Setup
// ============================================================
function escHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// Minimal syntax highlighter — One Dark palette, handles common tokens
function simpleHighlight(code, lang) {
  const esc = escHtml(code);
  if (!lang) return esc;
  const L = lang.toLowerCase();
  // Tokeniser patterns, applied in order (order matters)
  // Note: avoid triple-quote sequences to prevent issues with Python string embedding
  const q3 = '"'.repeat(3); // dynamically builds triple-quote for regex without appearing literally
  const patterns = [
    // block comments first (before line comments)
    [/\/\*[\s\S]*?\*\//g, '<span class="sc">$&</span>'],
    // line comments (//, #, --)
    [/\/\/[^\n]*|(?:^|\s)#[^\n]*/g, '<span class="sc">$&</span>'],
    // template literals / backtick strings
    [/`[^`]*`/g, '<span class="ss">$&</span>'],
    // double-quoted strings (single-line)
    [/"(?:\\.|[^"\\])*"/g, '<span class="ss">$&</span>'],
    // single-quoted strings (single-line)
    [/'(?:\\.|[^'\\])*'/g, '<span class="ss">$&</span>'],
    // numbers
    [/\b(0x[\da-fA-F]+|\d+\.?\d*(?:[eE][+-]?\d+)?)\b/g, '<span class="sn">$&</span>'],
    // keywords (broad coverage)
    [/\b(import|export|from|as|default|const|let|var|function|return|class|extends|new|this|super|if|else|for|while|do|switch|case|break|continue|try|catch|finally|throw|async|await|yield|typeof|instanceof|in|of|void|delete|null|undefined|true|false|None|True|False|def|pass|lambda|with|global|nonlocal|raise|except|and|or|not|is|elif|require|module|use|pub|fn|mut|impl|struct|enum|trait|type|interface|abstract|static|public|private|protected|readonly|override|virtual|sealed|namespace|using|include|package|go|chan|select|defer|map|range)\b/g, '<span class="sk">$&</span>'],
    // built-in types
    [/\b(string|number|boolean|int|float|double|char|byte|bool|void|any|object|Array|Object|Promise|Error|Set|Map|String|Number|Boolean)\b/g, '<span class="sa">$&</span>'],
    // function/method calls
    [/\b([a-zA-Z_]\w*)\s*(?=\()/g, '<span class="sf">$&</span>'],
    // decorators / annotations
    [/@[a-zA-Z_]\w*/g, '<span class="so">$&</span>'],
  ];
  let out = esc;
  // Only apply if language looks like code (not bash one-liners etc)
  if (!['text','txt','markdown','md','plaintext'].includes(L)) {
    for (const [re, tpl] of patterns) {
      out = out.replace(re, tpl);
    }
  }
  return out;
}

// marked replaced by inline parseMarkdown()

let viewerRawMode = false;

function setViewerMode(mode) {
  viewerRawMode = (mode === 'raw');
  const rendered = document.getElementById('viewer-content');
  const raw = document.getElementById('viewer-raw-pre');
  const btnR = document.getElementById('btn-mode-rendered');
  const btnRaw = document.getElementById('btn-mode-raw');
  if (viewerRawMode) {
    rendered.style.display = 'none';
    raw.style.display = 'block';
    btnR.classList.remove('active');
    btnRaw.classList.add('active');
  } else {
    rendered.style.display = '';
    raw.style.display = 'none';
    btnR.classList.add('active');
    btnRaw.classList.remove('active');
  }
}

function renderMarkdown(text) {
  try { return parseMarkdown(text); } catch(e) { return '<pre style="white-space:pre-wrap">' + escHtml(text) + '</pre>'; }
}

// ============================================================
// State
// ============================================================
let state = {};
let projectsState = { projects: [], active_project_id: '', active_project: null };
let appMode = 'projects';
let projectSearchTerm = '';
let projectDraftName = '';
let projectListMode = 'active';
let pendingDeleteProjectId = '';
let currentView = 'overview';
let currentInputFile = null;
let currentReviewFile = null;
let runtimeInitialized = false;
let pollInterval = null;

// Generation tracking
let lastProcessingStatus = 'idle';
let lastSeenErrorTs = localStorage.getItem('forge_lastSeenErrorTs') || null;
let optimisticRunning = null;  // {stage, startTime} — card spinner only, never drives toasts
let fixingFile = null;
let viewingVersion = null;  // {id, timestamp} when viewing a historic version, null = current

const PIPELINE_STAGE_ORDER = ['context','requirements','design','analysis','architecture','delivery','engineering','qa','operations','release','marketing'];

const PHASES = ['input', 'generate', 'review', 'build', 'deploy'];
const PHASE_LABELS = { input: 'Input', generate: 'Generate', review: 'Review', build: 'Build', deploy: 'Deploy' };

const STAGES = [
  { key: 'context', label: 'Context', dir: '00-context', desc: 'Product vision & market' },
  { key: 'requirements', label: 'Requirements', dir: '01-requirements', desc: 'BRD, PRD, metrics' },
  { key: 'design', label: 'Design', dir: '02-design', desc: 'UX, design system' },
  { key: 'analysis', label: 'Analysis', dir: '03-analysis', desc: 'Domain model, journeys' },
  { key: 'architecture', label: 'Architecture', dir: '04-architecture', desc: 'System design, APIs' },
  { key: 'delivery', label: 'Delivery', dir: '05-delivery', desc: 'Roadmap, sprints' },
  { key: 'engineering', label: 'Engineering', dir: '06-engineering', desc: 'Specs, implementation' },
  { key: 'qa', label: 'Quality', dir: '07-quality', desc: 'Test strategy, acceptance' },
  { key: 'operations', label: 'Operations', dir: '08-operations', desc: 'Runbooks, monitoring' },
  { key: 'release', label: 'Release', dir: '09-release', desc: 'Notes, rollout strategy' },
  { key: 'marketing', label: 'Marketing', dir: '10-marketing', desc: 'GTM, positioning' },
];

const PROJECT_UI_TEXT = {
  eyebrow: 'Workspace Control Plane',
  title: 'Projects',
  subtitle: 'Create, open, and switch generated Forge projects from one top-level orchestrator workspace.',
  totalProjects: 'Total Projects',
  activeProject: 'Active Project',
  createTitle: 'Create Project',
  createCopy: 'Each project gets its own isolated runtime state under the workspace projects directory.',
  projectNameLabel: 'Project Name',
  projectNamePlaceholder: 'Task Flow',
  createButton: 'Create Project',
  listTitle: 'Project Directory',
  listCopy: 'Open active projects or manage archived projects before permanent deletion.',
  searchPlaceholder: 'Search projects',
  emptyTitle: 'No projects yet',
  emptyCopy: 'Create a project from the form on this page to start.',
  emptyArchivedTitle: 'No archived projects',
  emptyArchivedCopy: 'Archived projects stay recoverable here until you permanently delete them.',
  noMatchesTitle: 'No matching projects',
  noMatchesCopy: 'Clear the search field or create a new project.',
  active: 'Active',
  archived: 'Archived',
  activeTab: 'Active',
  archivedTab: 'Archived',
  updated: 'Updated',
  created: 'Created',
  archivedAt: 'Archived',
  openProject: 'Open Project',
  archiveProject: 'Archive',
  restoreProject: 'Restore',
  deleteProject: 'Delete',
  confirmDeleteProject: 'Confirm Delete',
  cancelDelete: 'Cancel',
  unnamed: 'Unnamed Project',
  never: 'Never',
  enterName: 'Enter a project name',
  createFailed: 'Failed to create project',
  createdToast: 'Project created',
  openFailed: 'Failed to open project',
  archiveFailed: 'Failed to archive project',
  archivedToast: 'Project archived',
  restoreFailed: 'Failed to restore project',
  restoredToast: 'Project restored',
  deleteFailed: 'Failed to delete project',
  deletedToast: 'Project deleted',
  projectsButton: 'Projects'
};

// ============================================================
// Core
// ============================================================
async function loadState() {
  try {
    await loadProjectsState();
    renderProjectsHome();
    if (appMode === 'projects') {
      renderTopbar();
      return;
    }
    const res = await apiFetch('/api/state');
    if (!res.ok) return;
    state = await res.json();
    renderAll();
  } catch (e) {
    console.warn('State fetch failed', e);
  }
}

async function loadProjectsState() {
  try {
    const res = await apiFetch('/api/projects');
    if (!res.ok) return;
    projectsState = await res.json();
  } catch (e) {
    console.warn('Projects state fetch failed', e);
  }
}

function renderAll() {
  document.getElementById('projects-shell').style.display = 'none';
  document.getElementById('app').style.display = 'flex';
  renderTopbar();
  renderOverview();
  renderInput();
  renderGenerate();
  renderReview();
  renderBuild();
  renderDeploy();
  renderIssues();
  if (!runtimeInitialized) {
    renderSettings();
    runtimeInitialized = true;
  }
}

function startPolling() {
  loadState();
  pollInterval = setInterval(loadState, 3000);
}

function renderProjectsHome() {
  const shell = document.getElementById('projects-shell');
  if (!shell) return;
  const projects = projectsState.projects || [];
  const activeProjects = projects.filter((p) => (p.status || 'active') === 'active');
  const archivedProjects = projects.filter((p) => p.status === 'archived');
  const sourceProjects = projectListMode === 'archived' ? archivedProjects : activeProjects;
  const normalizedSearch = projectSearchTerm.trim().toLowerCase();
  const visibleProjects = normalizedSearch
    ? sourceProjects.filter((p) => `${p.name || ''} ${p.slug || ''} ${p.path || ''}`.toLowerCase().includes(normalizedSearch))
    : sourceProjects;
  const activeId = projectsState.active_project_id || '';
  const activeProject = activeProjects.find((p) => p.id === activeId);
  const summaryActiveName = activeProject?.name || '';

  // Sidebar recent list — show up to 8 rows from sourceProjects (no search filter)
  const sidebarList = (projectListMode === 'archived' ? archivedProjects : activeProjects)
    .slice(0, 8)
    .map((p) => {
      const isActive = p.id === activeId;
      const isArchived = (p.status || 'active') === 'archived';
      return `
        <div class="proj-recent-item ${isActive ? 'is-active' : ''}" onclick="openProject('${escHtmlJs(p.id)}')">
          <div class="proj-recent-item-info">
            <div class="proj-recent-item-name" title="${escHtmlJs(p.name || PROJECT_UI_TEXT.unnamed)}">${escHtmlJs(p.name || PROJECT_UI_TEXT.unnamed)}</div>
            <div class="proj-recent-item-slug">${escHtmlJs(p.slug || '')}</div>
          </div>
          ${!isArchived ? `<button class="proj-recent-item-open" onclick="event.stopPropagation();openProject('${escHtmlJs(p.id)}')">${PROJECT_UI_TEXT.openProject}</button>` : ''}
        </div>
      `;
    }).join('');

  // Main grid cards
  const projectCards = visibleProjects.map((p) => {
    const isActive = p.id === activeId;
    const updated = formatProjectDate(p.updated_at);
    const created = formatProjectDate(p.created_at);
    const archivedAt = formatProjectDate(p.archived_at);
    const isArchived = (p.status || 'active') === 'archived';
    const isDeletePending = pendingDeleteProjectId === p.id;
    return `
      <div class="project-card ${isActive ? 'active' : ''}">
        <div class="project-card-head">
          <div style="min-width:0;">
            <div class="project-name" title="${escHtmlJs(p.name || PROJECT_UI_TEXT.unnamed)}">${escHtmlJs(p.name || PROJECT_UI_TEXT.unnamed)}</div>
            <div class="project-slug">${escHtmlJs(p.slug || '')}</div>
          </div>
          ${isActive ? `<span class="active-pill">${PROJECT_UI_TEXT.active}</span>` : ''}
          ${isArchived ? `<span class="archive-pill">${PROJECT_UI_TEXT.archived}</span>` : ''}
        </div>
        <div class="project-meta-grid">
          <div class="project-meta-item">
            <div class="project-meta-label">${PROJECT_UI_TEXT.updated}</div>
            <div class="project-meta-value" title="${escHtmlJs(updated)}">${escHtmlJs(updated)}</div>
          </div>
          <div class="project-meta-item">
            <div class="project-meta-label">${PROJECT_UI_TEXT.created}</div>
            <div class="project-meta-value" title="${escHtmlJs(created)}">${escHtmlJs(created)}</div>
          </div>
          ${isArchived ? `
          <div class="project-meta-item">
            <div class="project-meta-label">${PROJECT_UI_TEXT.archivedAt}</div>
            <div class="project-meta-value" title="${escHtmlJs(archivedAt)}">${escHtmlJs(archivedAt)}</div>
          </div>
          ` : ''}
        </div>
        <div class="project-path" title="${escHtmlJs(p.path || '')}">${escHtmlJs(p.path || '')}</div>
        <div class="project-card-actions">
          ${isArchived ? `
            <button class="btn btn-secondary btn-sm" onclick="restoreProject('${escHtmlJs(p.id)}')">${PROJECT_UI_TEXT.restoreProject}</button>
            ${isDeletePending ? `
              <button class="btn btn-danger btn-sm" onclick="deleteArchivedProject('${escHtmlJs(p.id)}')">${PROJECT_UI_TEXT.confirmDeleteProject}</button>
              <button class="btn btn-secondary btn-sm" onclick="cancelDeleteProject()">${PROJECT_UI_TEXT.cancelDelete}</button>
            ` : `
              <button class="btn btn-danger btn-sm" onclick="requestDeleteProject('${escHtmlJs(p.id)}')">${PROJECT_UI_TEXT.deleteProject}</button>
            `}
          ` : `
            <button class="btn btn-primary btn-sm" onclick="openProject('${escHtmlJs(p.id)}')">${PROJECT_UI_TEXT.openProject}</button>
            <button class="btn btn-secondary btn-sm" onclick="archiveProject('${escHtmlJs(p.id)}')">${PROJECT_UI_TEXT.archiveProject}</button>
          `}
        </div>
      </div>
    `;
  }).join('');

  const emptyState = sourceProjects.length
    ? renderProjectsEmpty(PROJECT_UI_TEXT.noMatchesTitle, PROJECT_UI_TEXT.noMatchesCopy)
    : projectListMode === 'archived'
      ? renderProjectsEmpty(PROJECT_UI_TEXT.emptyArchivedTitle, PROJECT_UI_TEXT.emptyArchivedCopy)
      : renderProjectsEmpty(PROJECT_UI_TEXT.emptyTitle, PROJECT_UI_TEXT.emptyCopy);

  const statsActiveChip = activeProject
    ? `<div class="proj-stat-chip active-chip"><strong>${escHtmlJs(activeProject.name)}</strong> &mdash; active</div>`
    : '';

  shell.innerHTML = `
    <aside class="projects-sidebar">
      <div class="proj-sidebar-logo">
        <div class="proj-sidebar-logo-mark">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <rect x="6"   y="4.5" width="3"  height="15"  rx="0.5" fill="currentColor"/>
            <rect x="6"   y="4.5" width="12" height="2.8"  rx="0.5" fill="currentColor"/>
            <rect x="6"   y="12"  width="9"  height="2.5"  rx="0.5" fill="currentColor"/>
            <path transform="translate(18.5,5.1)"
              d="M0,-1.6 C.22,-.52 .52,-.22 1.6,0 C.52,.22 .22,.52 0,1.6 C-.22,.52 -.52,.22 -1.6,0 C-.52,-.22 -.22,-.52 0,-1.6Z"
              fill="currentColor" opacity="0.85"/>
          </svg>
        </div>
        <span class="proj-sidebar-wordmark">Forge OS</span>
      </div>

      <button class="proj-new-btn" onclick="(document.getElementById('project-create-name')?.value?.trim() ? createProjectFromHome() : document.getElementById('project-create-name')?.focus())">${PROJECT_UI_TEXT.createButton}</button>
      <input
        id="project-create-name"
        class="proj-name-input"
        value="${escHtmlJs(projectDraftName)}"
        placeholder="${PROJECT_UI_TEXT.projectNamePlaceholder}"
        oninput="onProjectDraftChange(this.value)"
      />

      <div class="proj-sidebar-divider"></div>
      <div class="proj-sidebar-section-label">${projectListMode === 'archived' ? PROJECT_UI_TEXT.archivedTab : 'Recent Projects'}</div>

      <div class="proj-recent-list">
        ${sidebarList || `<div style="color:rgba(255,255,255,.36);font-size:12px;padding:8px 0;">${PROJECT_UI_TEXT.emptyTitle}</div>`}
      </div>

      <div class="proj-sidebar-tabs">
        <button class="proj-sidebar-tab ${projectListMode === 'active' ? 'active' : ''}" onclick="setProjectListMode('active')">${PROJECT_UI_TEXT.activeTab} (${activeProjects.length})</button>
        <button class="proj-sidebar-tab ${projectListMode === 'archived' ? 'active' : ''}" onclick="setProjectListMode('archived')">${PROJECT_UI_TEXT.archivedTab} (${archivedProjects.length})</button>
      </div>
    </aside>

    <main class="projects-main">
      <div class="proj-main-topbar">
        <div>
          <div class="proj-main-title">Projects</div>
          <div class="proj-main-subtitle">${PROJECT_UI_TEXT.subtitle}</div>
        </div>
        <div class="proj-search-wrap">
          <input id="project-search" class="projects-search" value="${escHtmlJs(projectSearchTerm)}" placeholder="${PROJECT_UI_TEXT.searchPlaceholder}" oninput="onProjectSearch(this.value)" />
        </div>
      </div>

      <div class="proj-stats-row">
        <div class="proj-stat-chip"><strong>${activeProjects.length}</strong>&nbsp;${activeProjects.length === 1 ? 'project' : 'projects'}</div>
        ${statsActiveChip}
        ${archivedProjects.length ? `<div class="proj-stat-chip">${archivedProjects.length} archived</div>` : ''}
      </div>

      ${visibleProjects.length ? `<div class="projects-grid">${projectCards}</div>` : emptyState}
    </main>
  `;
  bindProjectHomeEvents();
}

function openProjectsHome() {
  appMode = 'projects';
  renderTopbar();
  renderProjectsHome();
}

function renderProjectsEmpty(title, copy) {
  return `
    <div class="empty-projects">
      <div class="empty-projects-title">${title}</div>
      <div>${copy}</div>
    </div>
  `;
}

function bindProjectHomeEvents() {
  document.getElementById('project-create-name')?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') createProjectFromHome();
  });
}

function onProjectDraftChange(value) {
  projectDraftName = value || '';
}

function onProjectSearch(value) {
  projectSearchTerm = value || '';
  renderProjectsHome();
  const input = document.getElementById('project-search');
  if (input) {
    input.focus();
    input.setSelectionRange(input.value.length, input.value.length);
  }
}

function setProjectListMode(mode) {
  projectListMode = mode === 'archived' ? 'archived' : 'active';
  pendingDeleteProjectId = '';
  renderProjectsHome();
}

function formatProjectDate(value) {
  if (!value) return PROJECT_UI_TEXT.never;
  try {
    const d = new Date(value);
    if (isNaN(d.getTime())) return PROJECT_UI_TEXT.never;
    // Compact format: "16 May '26  01:49" — fits in narrow meta cells
    const date = d.toLocaleDateString(undefined, { day: '2-digit', month: 'short', year: '2-digit' });
    const time = d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit', hour12: false });
    return `${date}  ${time}`;
  } catch (e) {
    return PROJECT_UI_TEXT.never;
  }
}

async function createProjectFromHome() {
  const input = document.getElementById('project-create-name');
  const name = (input?.value || '').trim();
  if (!name) {
    showToast(PROJECT_UI_TEXT.enterName, 'error');
    return;
  }
  try {
    const res = await apiFetch('/api/projects', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name })
    });
    const data = await res.json();
    if (!res.ok) {
      showToast(data.error || PROJECT_UI_TEXT.createFailed, 'error');
      return;
    }
    if (input) input.value = '';
    projectDraftName = '';
    await loadProjectsState();
    renderProjectsHome();
    showToast(PROJECT_UI_TEXT.createdToast, 'success');
  } catch (e) {
    showToast(PROJECT_UI_TEXT.createFailed, 'error');
  }
}

async function openProject(projectId) {
  try {
    const res = await apiFetch('/api/projects/select', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project_id: projectId })
    });
    const data = await res.json();
    if (!res.ok) {
      showToast(data.error || PROJECT_UI_TEXT.openFailed, 'error');
      return;
    }
    appMode = 'dashboard';
    runtimeInitialized = false;
    await loadState();
  } catch (e) {
    showToast(PROJECT_UI_TEXT.openFailed, 'error');
  }
}

async function archiveProject(projectId) {
  try {
    const res = await apiFetch('/api/projects/archive', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project_id: projectId })
    });
    const data = await res.json();
    if (!res.ok) {
      showToast(data.error || PROJECT_UI_TEXT.archiveFailed, 'error');
      return;
    }
    await loadProjectsState();
    renderProjectsHome();
    showToast(PROJECT_UI_TEXT.archivedToast, 'success');
  } catch (e) {
    showToast(PROJECT_UI_TEXT.archiveFailed, 'error');
  }
}

async function restoreProject(projectId) {
  try {
    const res = await apiFetch('/api/projects/restore', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project_id: projectId })
    });
    const data = await res.json();
    if (!res.ok) {
      showToast(data.error || PROJECT_UI_TEXT.restoreFailed, 'error');
      return;
    }
    pendingDeleteProjectId = '';
    await loadProjectsState();
    renderProjectsHome();
    showToast(PROJECT_UI_TEXT.restoredToast, 'success');
  } catch (e) {
    showToast(PROJECT_UI_TEXT.restoreFailed, 'error');
  }
}

function requestDeleteProject(projectId) {
  pendingDeleteProjectId = projectId;
  renderProjectsHome();
}

function cancelDeleteProject() {
  pendingDeleteProjectId = '';
  renderProjectsHome();
}

async function deleteArchivedProject(projectId) {
  try {
    const res = await apiFetch('/api/projects', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project_id: projectId })
    });
    const data = await res.json();
    if (!res.ok) {
      showToast(data.error || PROJECT_UI_TEXT.deleteFailed, 'error');
      return;
    }
    pendingDeleteProjectId = '';
    await loadProjectsState();
    renderProjectsHome();
    showToast(PROJECT_UI_TEXT.deletedToast, 'success');
  } catch (e) {
    showToast(PROJECT_UI_TEXT.deleteFailed, 'error');
  }
}

// ============================================================
// Topbar
// ============================================================
function renderTopbar() {
  const stepper = document.getElementById('phase-stepper');
  const pill = document.getElementById('status-pill');
  const projectsBtn = document.getElementById('btn-projects-home');

  if (appMode === 'projects') {
    document.getElementById('projects-shell').style.display = 'flex';
    document.getElementById('app').style.display = 'none';
    stepper.style.display = 'none';
    pill.style.display = 'none';
    projectsBtn.style.display = 'none';
    document.body.classList.add('projects-mode');
    if (window.__webglControl) window.__webglControl.start();
    return;
  }

  if (window.__webglControl) window.__webglControl.stop();
  document.body.classList.remove('projects-mode');
  stepper.style.display = 'flex';
  pill.style.display = 'flex';
  projectsBtn.style.display = 'inline-flex';

  const phase = state.phase || 'input';
  const phaseIdx = PHASES.indexOf(phase);
  stepper.innerHTML = PHASES.map((p, i) => {
    const cls = i < phaseIdx ? 'done' : (i === phaseIdx ? 'active' : '');
    const arrow = i < PHASES.length - 1 ? '<span class="phase-arrow">›</span>' : '';
    return `
      <span class="phase-step ${cls}" onclick="switchView('${p}')">
        <span class="phase-dot"></span>${PHASE_LABELS[p]}
      </span>${arrow}`;
  }).join('');

  const statusText = document.getElementById('status-text');
  const processing = state.processing || {};
  const processingStatus = processing.status || 'idle';
  const isRunning = processingStatus === 'running';
  const isFixing = processingStatus === 'fixing';

  if (isRunning) {
    pill.className = 'running';
    const stageLabel = processing.stage ? ` — ${processing.stage}` : '';
    statusText.textContent = `Generating${stageLabel}`;
  } else if (isFixing) {
    pill.className = 'running';
    const shortFile = (processing.file || '').split('/').pop().replace('.md','');
    statusText.textContent = `Fixing — ${shortFile}`;
    fixingFile = processing.file || fixingFile;
  } else {
    pill.className = '';
    statusText.textContent = 'Idle';
    const lastError = state.processing?.last_error;
    if (lastProcessingStatus === 'running') {
      // Only show success if the run didn't produce any errors
      if (!lastError) {
        showToast('Generation complete', 'success');
      }
    }
    if (lastProcessingStatus === 'fixing' && fixingFile) {
      if (!lastError) {
        showToast('Regeneration complete', 'success');
      }
      if (currentReviewFile === fixingFile) {
        reloadCurrentFile();
      }
      fixingFile = null;
    }
    // Show error toast once per unique error
    if (lastError && lastError.timestamp !== lastSeenErrorTs) {
      lastSeenErrorTs = lastError.timestamp;
      localStorage.setItem('forge_lastSeenErrorTs', lastSeenErrorTs);
      showToast(lastError.message, 'error');
    }
  }
  lastProcessingStatus = processingStatus;

  // Product name in topbar
  const nameEl = document.getElementById('topbar-product-name');
  const pname = state.project_name || '';
  if (pname) {
    nameEl.textContent = pname;
    nameEl.style.display = '';
  } else {
    nameEl.style.display = 'none';
  }

  const issues = (state.issues || []).filter(i => i.status === 'open');
  const badge = document.getElementById('issues-badge');
  if (issues.length > 0) {
    badge.textContent = issues.length;
    badge.style.display = '';
  } else {
    badge.style.display = 'none';
  }

}

// ============================================================
// Overview
// ============================================================
function renderOverview() {
  const phase = state.phase || 'input';
  const phaseIdx = PHASES.indexOf(phase);
  const summary = state.stageReviewSummary || {};
  const gates = state.gates || {};
  const issues = state.issues || [];

  const pname = state.project_name || 'Unnamed Project';
  document.getElementById('overview-subtitle').textContent = pname;

  // Lifecycle stepper
  const stepperEl = document.getElementById('lifecycle-stepper');
  stepperEl.innerHTML = '';
  PHASES.forEach((p, i) => {
    const cls = i < phaseIdx ? 'done' : (i === phaseIdx ? 'active' : '');
    const num = i + 1;
    const circleContent = i < phaseIdx
      ? `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 12.75l6 6 9-13.5"/></svg>`
      : num;
    stepperEl.insertAdjacentHTML('beforeend', `
      <div class="lifecycle-step ${cls}" onclick="switchView('${p}')">
        <div class="step-circle">${circleContent}</div>
        <div class="step-label">${PHASE_LABELS[p]}</div>
      </div>
      ${i < PHASES.length - 1 ? `<div class="step-connector ${i < phaseIdx ? 'done' : ''}"></div>` : ''}
    `);
  });

  // Stats
  const totalGenerated = Object.values(summary).reduce((a, s) => a + s.generated, 0);
  const totalReviewed = Object.values(summary).reduce((a, s) => a + s.reviewed, 0);
  const gatesPassed = Object.values(gates).filter(v => v === 'PASSED').length;
  const openIssues = issues.filter(i => i.status === 'open').length;

  document.getElementById('overview-stats').innerHTML = `
    <div class="stat-card">
      <div class="stat-value" style="color:var(--blue)">${totalGenerated}</div>
      <div class="stat-label">Docs Generated</div>
    </div>
    <div class="stat-card">
      <div class="stat-value" style="color:var(--green)">${totalReviewed}</div>
      <div class="stat-label">Docs Reviewed</div>
    </div>
    <div class="stat-card">
      <div class="stat-value" style="color:var(--purple)">${gatesPassed}</div>
      <div class="stat-label">Gates Passed</div>
    </div>
    <div class="stat-card">
      <div class="stat-value" style="color:${openIssues > 0 ? 'var(--amber)' : 'var(--text-3)'}">${openIssues}</div>
      <div class="stat-label">Open Issues</div>
    </div>
  `;

  const guidance = {
    input: 'Create your first input file describing your product idea. Go to <b>Input</b> and click "New File".',
    generate: 'You have input files ready. Go to <b>Generate</b> and click "Generate All Stages" to start the AI pipeline.',
    review: 'Documents have been generated. Go to <b>Review</b>, read each document, and mark them as reviewed.',
    build: 'All documents are reviewed. Go to <b>Build</b> to create a git branch and commit your docs.',
    deploy: 'Build is complete. Go to <b>Deploy</b> to see your environments and set up CI/CD.',
  };
  document.getElementById('overview-guidance').innerHTML = guidance[phase] || 'Continue to the next phase.';

  const actions = {
    input: `<button class="btn btn-primary btn-sm" onclick="switchView('input');openNewFileDialog()">${icon('sparkles',12)} Create Input File</button>`,
    generate: `<button class="btn btn-primary btn-sm" onclick="switchView('generate');generate('all')">${icon('sparkles',12)} Generate All</button>`,
    review: `<button class="btn btn-primary btn-sm" onclick="switchView('review')">${icon('eye',12)} Start Review</button>`,
    build: `<button class="btn btn-primary btn-sm" onclick="switchView('build');startBuild()">${icon('gitBranch',12)} Start Build</button>`,
    deploy: `<button class="btn btn-primary btn-sm" onclick="switchView('deploy')">${icon('cloudUp',12)} View Deploy</button>`,
  };
  document.getElementById('overview-quick-action').innerHTML = actions[phase] || '';
}

// ============================================================
// Input
// ============================================================
let newFileCat = '';

function selectCategory(btn, cat) {
  newFileCat = cat;
  document.querySelectorAll('#category-chips .category-chip').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  updateFilePreview();
}

function updateFilePreview() {
  const name = document.getElementById('new-file-name').value.trim();
  const fname = name ? (name.endsWith('.md') ? name : name + '.md') : '';
  const full = newFileCat ? `${newFileCat}/${fname || 'untitled.md'}` : (fname || 'untitled.md');
  document.getElementById('new-file-preview').textContent = full;
}

function renderInput() {
  const rawInputs = state.rawInputs || [];
  const count = rawInputs.length;

  document.getElementById('input-file-count').textContent = count;

  const listEl = document.getElementById('input-file-list');
  listEl.innerHTML = '';

  if (count === 0) {
    document.getElementById('input-empty-state').style.display = '';
    document.getElementById('input-editor-container').style.display = 'none';
    currentInputFile = null;
    return;
  }

  document.getElementById('input-empty-state').style.display = 'none';

  // Group files by folder
  const grouped = {};
  rawInputs.forEach(f => {
    const parts = f.name.split('/');
    const folder = parts.length > 1 ? parts[0] : '';
    const base = parts[parts.length - 1];
    if (!grouped[folder]) grouped[folder] = [];
    grouped[folder].push({ ...f, base });
  });

  // Render: root files first (empty folder key), then alphabetical folders
  const folders = Object.keys(grouped).sort((a, b) => {
    if (a === '') return -1;
    if (b === '') return 1;
    return a.localeCompare(b);
  });

  folders.forEach(folder => {
    if (folder !== '') {
      // Folder header
      listEl.insertAdjacentHTML('beforeend', `
        <div class="file-folder-header">
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7a2 2 0 012-2h4l2 2h8a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V7z"/></svg>
          ${escHtmlJs(folder)}
        </div>
      `);
    }
    grouped[folder].forEach(f => {
      const isActive = currentInputFile === f.name;
      const size = f.size > 0 ? `${(f.size/1024).toFixed(1)} KB` : 'empty';
      const modified = f.modifiedAt ? new Date(f.modifiedAt * 1000).toLocaleDateString() : '';
      const indent = folder ? 'padding-left:22px;' : '';
      listEl.insertAdjacentHTML('beforeend', `
        <div class="file-item ${isActive ? 'active' : ''}" style="${indent}" onclick="openInputFile('${escHtmlJs(f.name)}')">
          <div class="file-item-name" title="${escHtmlJs(f.name)}">${escHtmlJs(f.base)}</div>
          <div class="file-item-meta">${size} · ${modified}</div>
        </div>
      `);
    });
  });
}

function escHtmlJs(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}

async function openInputFile(name) {
  currentInputFile = name;
  document.getElementById('input-empty-state').style.display = 'none';
  const container = document.getElementById('input-editor-container');
  container.style.display = 'flex';
  // Show just the filename portion in the header (not the full path)
  const displayName = name.includes('/') ? name : name;
  document.getElementById('editing-filename').textContent = displayName;

  renderInput(); // re-render to update active highlight

  try {
    const res = await apiFetch(`/api/raw-input?name=${encodeURIComponent(name)}`);
    const text = await res.text();
    document.getElementById('input-editor').value = text;
  } catch (e) {
    showToast('Failed to load file', 'error');
  }
}

async function saveCurrentFile() {
  if (!currentInputFile) return;
  const content = document.getElementById('input-editor').value;
  try {
    await apiFetch('/api/raw-input', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: currentInputFile, content })
    });
    showToast('File saved', 'success');
    loadState();
  } catch (e) {
    showToast('Save failed', 'error');
  }
}

async function deleteCurrentFile() {
  if (!currentInputFile) return;
  if (!confirm(`Delete ${currentInputFile}?`)) return;
  try {
    await apiFetch('/api/raw-input', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: currentInputFile })
    });
    currentInputFile = null;
    document.getElementById('input-empty-state').style.display = '';
    document.getElementById('input-editor-container').style.display = 'none';
    showToast('File deleted', 'success');
    loadState();
  } catch (e) {
    showToast('Delete failed', 'error');
  }
}

function openNewFileDialog() {
  newFileCat = '';
  document.querySelectorAll('#category-chips .category-chip').forEach((b, i) => b.classList.toggle('active', i === 0));
  document.getElementById('new-file-name').value = '';
  document.getElementById('new-file-preview').textContent = 'untitled.md';
  document.getElementById('new-file-dialog').classList.remove('hidden');
  document.getElementById('new-file-name').focus();
}

function closeNewFileDialog() {
  document.getElementById('new-file-dialog').classList.add('hidden');
}

async function createNewFile() {
  const rawName = document.getElementById('new-file-name').value.trim();
  if (!rawName) { showToast('Enter a file name', 'error'); return; }
  const fname = rawName.endsWith('.md') ? rawName : rawName + '.md';
  const fullPath = newFileCat ? `${newFileCat}/${fname}` : fname;
  const title = fname.replace('.md', '').replace(/[-_]/g, ' ');
  const placeholder = newFileCat
    ? `# ${title.charAt(0).toUpperCase() + title.slice(1)}\n\nDescribe your ${newFileCat} details here...\n`
    : `# ${title.charAt(0).toUpperCase() + title.slice(1)}\n\nDescribe your product idea here...\n`;
  try {
    await apiFetch('/api/raw-input', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: fullPath, content: placeholder })
    });
    closeNewFileDialog();
    await loadState();
    openInputFile(fullPath);
    switchView('input');
  } catch (e) {
    showToast('Create failed', 'error');
  }
}

// ============================================================
// Generate
// ============================================================
function dismissGenerationError() {
  lastSeenErrorTs = 'dismissed';
  localStorage.setItem('forge_lastSeenErrorTs', lastSeenErrorTs);
  document.getElementById('generate-error-bar').style.display = 'none';
}

function renderGenerate() {
  const processing = state.processing || {};
  const serverRunning = processing.status === 'running';

  // Clear optimistic spinner once server confirms real running state (or after 15 s timeout)
  if (optimisticRunning) {
    if (serverRunning || Date.now() - optimisticRunning.startTime > 15000) {
      optimisticRunning = null;
    }
  }

  const isRunning = serverRunning || !!optimisticRunning;
  const summary = state.stageReviewSummary || {};

  document.getElementById('btn-generate-all').disabled = isRunning;

  // Error bar — show when there's an unacknowledged error from the last run
  const errBar = document.getElementById('generate-error-bar');
  const lastError = processing.last_error;
  if (lastError && lastSeenErrorTs !== 'dismissed' && lastError.timestamp === lastSeenErrorTs) {
    const shortFile = (lastError.file || '').split('/').pop().replace('.md', '');
    document.getElementById('generate-error-text').textContent =
      shortFile ? `${shortFile}: ${lastError.message}` : lastError.message;
    errBar.style.display = 'flex';
  } else if (!lastError || isRunning) {
    errBar.style.display = 'none';
  }

  // Determine which stages are "done" (have generated content)
  const runningIdx = PIPELINE_STAGE_ORDER.indexOf(processing.stage);

  if (isRunning) {
    const stageObj = STAGES.find(s => s.key === processing.stage);
    const label = stageObj ? stageObj.label : (processing.stage || 'pipeline');
    document.getElementById('generate-status-bar').innerHTML =
      `<span style="display:flex;align-items:center;gap:8px;">
        <span class="gen-spinner" style="width:11px;height:11px;border-width:1.5px;"></span>
        <span style="color:var(--amber);font-weight:600;">Generating ${label}</span>
        <span style="color:var(--text-3);">— other stages queued</span>
      </span>`;
  } else {
    const totalDone = STAGES.filter(s => (summary[s.dir] || {}).generated > 0).length;
    document.getElementById('generate-status-bar').innerHTML = totalDone > 0
      ? `<span style="color:var(--green);">${icon('check',12)} ${totalDone} stage${totalDone!==1?'s':''} generated</span> <span style="color:var(--text-3);margin-left:8px;">Ready to generate more or proceed to Review.</span>`
      : `Ready to generate. Run all stages or trigger individual stages below.`;
  }

  const grid = document.getElementById('stage-grid');
  grid.innerHTML = '';

  STAGES.forEach((s, idx) => {
    const stageSummary = summary[s.dir] || { generated: 0, reviewed: 0, total: 0 };
    const { generated, reviewed, total } = stageSummary;
    const pct = total > 0 ? Math.round((generated / total) * 100) : 0;
    const effectiveStage = serverRunning ? processing.stage : (optimisticRunning ? optimisticRunning.stage : null);
    const isThisRunning  = isRunning && (effectiveStage === s.key || (optimisticRunning && optimisticRunning.stage === null));
    const stageIdx       = PIPELINE_STAGE_ORDER.indexOf(s.key);
    const isQueued       = serverRunning && stageIdx > runningIdx && runningIdx >= 0;
    const hasContent    = generated > 0 && !isThisRunning;
    const allReviewed   = hasContent && reviewed === total && total > 0;
    const needsReview   = hasContent && !allReviewed;
    const hasError      = !isRunning && processing.last_error?.stage === s.key;

    // Card class drives border/bg
    const cardClass = isThisRunning ? 'running' : (allReviewed ? 'reviewed' : (needsReview ? 'needs-review' : (hasError ? 'error' : '')));

    // Progress bar colour
    const progressColor = allReviewed ? 'green' : (isThisRunning ? 'amber' : '');

    // Per-file progress from stage_runner
    const fileIdx   = isThisRunning ? (processing.file_index || 1) : 0;
    const fileTotal = isThisRunning ? (processing.file_total  || total || 1) : 0;
    const fileName  = isThisRunning ? (processing.file || '') : '';
    const fileBase  = fileName.split('/').pop().replace(/\.md$/, '');
    const filePct   = isThisRunning && fileTotal > 0 ? Math.round(((fileIdx - 1) / fileTotal) * 100) : pct;

    // Top-right badge
    let statusBadge = '';
    if (isThisRunning) {
      statusBadge = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="var(--amber)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="animation:spin 1.2s linear infinite;flex-shrink:0"><path d="M21 12a9 9 0 11-6.219-8.56"/></svg>`;
    } else if (hasError) {
      statusBadge = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="var(--red)" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`;
    } else if (allReviewed) {
      statusBadge = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="var(--green)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 12.75l6 6 9-13.5"/></svg>`;
    } else if (needsReview) {
      statusBadge = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="var(--amber)" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"/><path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>`;
    }

    // Stats label
    const statsLabel = isThisRunning
      ? `${fileIdx}/${fileTotal} files`
      : needsReview
        ? `${reviewed}/${total} reviewed`
        : `${generated}/${total} files`;

    // Subtitle
    const subtitle = isThisRunning && fileBase
      ? fileBase
      : hasError
        ? (processing.last_error?.file || '').split('/').pop().replace(/\.md$/, '') || 'failed'
        : s.desc;

    grid.insertAdjacentHTML('beforeend', `
      <div class="stage-card ${cardClass}" style="${isQueued ? 'opacity:0.45;pointer-events:none' : ''}">
        <div class="stage-card-header">
          <div>
            <div class="stage-name">${s.label}</div>
            <div class="stage-subtitle" style="${needsReview ? 'color:var(--amber);' : ''}">${needsReview ? 'Needs review' : subtitle}</div>
          </div>
          <div style="display:flex;flex-direction:column;align-items:flex-end;gap:6px;">
            ${statusBadge}
            <div class="stage-stats">${statsLabel}</div>
          </div>
        </div>
        <div class="progress-bar">
          <div class="progress-fill ${progressColor}" style="width:${Math.max(filePct, pct)}%;${isThisRunning ? 'animation:progress-pulse 1.5s ease-in-out infinite;' : ''}"></div>
        </div>
        <button class="btn btn-secondary btn-sm" ${isRunning ? 'disabled' : ''} onclick="generate('${s.key}')">
          ${icon('sparkles', 12)}
          ${isThisRunning ? 'Generating...' : 'Regenerate'}
        </button>
      </div>
    `);
  });
}

async function generate(stage) {
  // Show spinner on the card immediately WITHOUT touching state.processing.
  // Mutating state.processing would corrupt lastProcessingStatus and fire false toasts.
  optimisticRunning = { stage: stage === 'all' ? null : stage, startTime: Date.now() };
  renderGenerate();

  try {
    await apiFetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ stage })
    });
    switchView('generate');
    loadState();
  } catch (e) {
    optimisticRunning = null;
    renderGenerate();
    showToast('Generate request failed', 'error');
  }
}

// ============================================================
// Review
// ============================================================
// ── Review view filter state ───────────────────────────────────────────────────
// Persisted in localStorage so the user's preferred lens survives navigation.

const REVIEW_VIEWS = [
  { id: 'all',          label: 'All' },
  { id: 'product',      label: 'Product',      dirs: ['00-context','01-requirements','02-design','03-analysis','13-decisions'] },
  { id: 'engineering',  label: 'Engineering',  dirs: ['04-architecture','05-delivery','06-engineering','07-quality','15-build'] },
  { id: 'architecture', label: 'Architecture', dirs: ['03-analysis','04-architecture','02-design','13-decisions'] },
  { id: 'qa',           label: 'QA',           dirs: ['01-requirements','07-quality','06-engineering'] },
  { id: 'operations',   label: 'Operations',   dirs: ['05-delivery','08-operations','15-build','09-release'] },
  { id: 'marketing',    label: 'Marketing',    dirs: ['10-marketing','09-release','14-assets'] },
];

let reviewViewFilter   = localStorage.getItem('review-view')   || 'all';
let reviewStatusFilter = localStorage.getItem('review-status') || 'all';

function setReviewView(id) {
  reviewViewFilter = id;
  localStorage.setItem('review-view', id);
  renderReview();
}

function setReviewStatus(s) {
  reviewStatusFilter = s;
  localStorage.setItem('review-status', s);
  // Update status button active states
  ['all','pending','reviewed'].forEach(k => {
    const el = document.getElementById(`rsf-${k}`);
    if (el) el.classList.toggle('active', k === s);
  });
  renderReview();
}

function renderReviewViewPills() {
  const tree    = state.tree    || {};
  const reviews = state.reviews || {};
  const container = document.getElementById('review-view-filters');
  if (!container) return;

  container.innerHTML = REVIEW_VIEWS.map(v => {
    // Count reviewed/total for this view's dirs using f.status from the tree
    let reviewed = 0, total = 0;
    Object.entries(tree).forEach(([dir, files]) => {
      const inView = !v.dirs || v.dirs.some(d => dir.startsWith(d));
      if (!inView) return;
      files.forEach(f => {
        if (f.size === 0) return;
        total++;
        if (f.status === 'reviewed') reviewed++;
      });
    });
    const countLabel = total > 0 ? ` <span style="opacity:0.55;font-weight:400">${reviewed}/${total}</span>` : '';
    return `<button class="review-view-pill${reviewViewFilter === v.id ? ' active' : ''}" onclick="setReviewView('${v.id}')">${v.label}${countLabel}</button>`;
  }).join('');

  // Sync status filter buttons on initial render
  ['all','pending','reviewed'].forEach(k => {
    const el = document.getElementById(`rsf-${k}`);
    if (el) el.classList.toggle('active', k === reviewStatusFilter);
  });
}

function renderReview() {
  const tree  = state.tree  || {};
  const gates = state.gates || {};

  renderReviewViewPills();

  const treeEl = document.getElementById('review-tree-body');
  const searchVal = document.getElementById('review-search').value.toLowerCase();
  const activeView = REVIEW_VIEWS.find(v => v.id === reviewViewFilter) || REVIEW_VIEWS[0];
  treeEl.innerHTML = '';

  let totalVisible = 0;

  Object.entries(tree).forEach(([dir, files]) => {
    // View filter: skip dirs not in the active view
    if (activeView.dirs && !activeView.dirs.some(d => dir.startsWith(d))) return;

    // Apply search + status filters
    const filtered = files.filter(f => {
      if (searchVal && !f.name.toLowerCase().includes(searchVal)) return false;
      if (reviewStatusFilter !== 'all') {
        const isReviewed = f.status === 'reviewed';
        if (reviewStatusFilter === 'reviewed' && !isReviewed) return false;
        if (reviewStatusFilter === 'pending'  &&  isReviewed) return false;
      }
      return true;
    });
    if (filtered.length === 0) return;
    totalVisible += filtered.length;

    const summary = state.stageReviewSummary?.[dir] || {};
    treeEl.insertAdjacentHTML('beforeend', `
      <div class="stage-group">
        <div class="stage-group-header">
          <span>${dir}</span>
          <span style="font-size:9px;color:var(--text-3)">${summary.reviewed||0}/${summary.generated||0}</span>
        </div>
        ${filtered.map(f => {
          const path = `${dir}/${f.name}`;
          const isActive = currentReviewFile === path;
          const isBeingFixed = fixingFile === path;
          const dotClass = isBeingFixed ? 'fixing' : f.status;
          return `
            <div class="tree-file-item ${isActive ? 'active' : ''}" onclick="openReviewFile('${path}','${f.status}',${f.size},${f.modifiedAt})">
              <span class="tree-file-dot ${dotClass}"></span>
              ${f.name.replace('.md','')}
            </div>
          `;
        }).join('')}
      </div>
    `);
  });

  if (totalVisible === 0) {
    treeEl.innerHTML = `<div style="padding:24px 16px;text-align:center;color:var(--text-3);font-size:11px;">No files match the current filter.</div>`;
  }

  const gatesEl = document.getElementById('review-gates-summary');
  gatesEl.innerHTML = Object.entries(gates).map(([g, status]) => `
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:5px;">
      <span style="font-size:10px;color:var(--text-2)">${g}</span>
      <span class="badge badge-${status.toLowerCase()}">${status}</span>
    </div>
  `).join('');

  // Overlay: show when the currently-viewed file is being fixed
  const isViewerBeingFixed = !!(fixingFile && fixingFile === currentReviewFile);
  const overlay = document.getElementById('viewer-fix-overlay');
  if (overlay) {
    overlay.style.display = isViewerBeingFixed ? 'flex' : 'none';
    if (isViewerBeingFixed) {
      document.getElementById('viewer-fix-filename').textContent = fixingFile;
    }
  }
  const fixBtn = document.getElementById('btn-fix-regenerate');
  if (fixBtn) fixBtn.disabled = !!fixingFile;
}

function filterReviewTree(val) {
  renderReview();
}

async function openReviewFile(path, status, size, modifiedAt) {
  currentReviewFile = path;

  // Clear any active version view when switching files
  viewingVersion = null;
  document.getElementById('viewer-version-banner').style.display = 'none';
  document.getElementById('btn-mark-reviewed').style.opacity = '';
  document.getElementById('btn-mark-reviewed').style.pointerEvents = '';
  document.getElementById('btn-needs-review').style.opacity = '';
  document.getElementById('btn-needs-review').style.pointerEvents = '';

  document.getElementById('viewer-filename').textContent = path;
  document.getElementById('btn-mark-reviewed').style.display = '';
  document.getElementById('btn-needs-review').style.display = '';
  document.getElementById('viewer-mode-toggle').style.display = '';

  document.getElementById('meta-path').textContent = path;
  document.getElementById('meta-status').innerHTML = `<span class="badge badge-${status.replace('_','-')}">${status.replace('_',' ')}</span>`;
  document.getElementById('meta-size').textContent = size > 0 ? `${(size/1024).toFixed(1)} KB` : '0 bytes';
  document.getElementById('meta-modified').textContent = modifiedAt ? new Date(modifiedAt * 1000).toLocaleString() : '—';

  try {
    const res = await apiFetch(`/api/file?path=${encodeURIComponent(path)}`);
    if (res.ok) {
      const text = await res.text();
      const raw = text || '(empty file)';
      document.getElementById('viewer-content').innerHTML = renderMarkdown(raw);
      document.getElementById('viewer-raw-pre').textContent = raw;
    } else {
      document.getElementById('viewer-content').innerHTML = '<p style="color:var(--text-3)">(file not found)</p>';
      document.getElementById('viewer-raw-pre').textContent = '(file not found)';
    }
  } catch (e) {
    document.getElementById('viewer-content').innerHTML = '<p style="color:var(--red)">(error loading file)</p>';
    document.getElementById('viewer-raw-pre').textContent = '(error loading file)';
  }
  // Always open in rendered mode for a fresh file
  setViewerMode('rendered');

  renderReview();
  fetchVersions(path);
}

async function markFile(status) {
  if (!currentReviewFile) return;
  try {
    await apiFetch('/api/review', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: currentReviewFile, status })
    });
    showToast(status === 'reviewed' ? 'Marked as reviewed' : 'Marked for review', 'success');
    document.getElementById('meta-status').innerHTML = `<span class="badge badge-${status.replace('_','-')}">${status.replace('_',' ')}</span>`;
    loadState();
  } catch (e) {
    showToast('Failed', 'error');
  }
}

// ============================================================
// Version History
// ============================================================
function timeAgo(isoStr) {
  const diff = Math.floor((Date.now() - new Date(isoStr)) / 1000);
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff/60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff/3600)}h ago`;
  return `${Math.floor(diff/86400)}d ago`;
}

async function fetchVersions(path) {
  const listEl = document.getElementById('version-list');
  const labelEl = document.getElementById('versions-label');
  listEl.innerHTML = '<span style="font-size:10px;color:var(--text-3)">Loading...</span>';
  try {
    const res = await apiFetch(`/api/versions?path=${encodeURIComponent(path)}`);
    const data = await res.json();
    const versions = data.versions || [];
    labelEl.textContent = versions.length ? `Version History (${versions.length})` : 'Version History';
    if (versions.length === 0) {
      listEl.innerHTML = '<span style="font-size:10px;color:var(--text-3)">No prior versions yet.</span>';
      return;
    }
    listEl.innerHTML = versions.map((v, i) => {
      const isActive = viewingVersion && viewingVersion.id === v.id;
      const label = i === 0 ? 'Latest saved' : `v${versions.length - i}`;
      return `
        <div class="version-item ${isActive ? 'active' : ''}" onclick="openVersion('${v.id}','${v.timestamp}')">
          <span>${label}</span>
          <span class="vi-meta">${timeAgo(v.timestamp)} · ${(v.size/1024).toFixed(1)}KB</span>
        </div>`;
    }).join('');
  } catch(e) {
    listEl.innerHTML = '<span style="font-size:10px;color:var(--red)">Failed to load.</span>';
  }
}

async function openVersion(id, timestamp) {
  if (!currentReviewFile) return;
  try {
    const res = await apiFetch(`/api/version?path=${encodeURIComponent(currentReviewFile)}&id=${encodeURIComponent(id)}`);
    if (!res.ok) { showToast('Version not found', 'error'); return; }
    const text = await res.text();
    viewingVersion = { id, timestamp };

    document.getElementById('viewer-content').innerHTML = renderMarkdown(text);
    document.getElementById('viewer-raw-pre').textContent = text;

    const banner = document.getElementById('viewer-version-banner');
    banner.style.display = 'flex';
    document.getElementById('vb-label').textContent =
      `Viewing version from ${new Date(timestamp).toLocaleString()} — not the current file`;

    // Dim action buttons while viewing historic version
    document.getElementById('btn-mark-reviewed').style.opacity = '0.3';
    document.getElementById('btn-mark-reviewed').style.pointerEvents = 'none';
    document.getElementById('btn-needs-review').style.opacity = '0.3';
    document.getElementById('btn-needs-review').style.pointerEvents = 'none';

    // Re-render version list to highlight active
    fetchVersions(currentReviewFile);
  } catch(e) {
    showToast('Failed to load version', 'error');
  }
}

function closeVersion() {
  viewingVersion = null;
  document.getElementById('viewer-version-banner').style.display = 'none';
  document.getElementById('btn-mark-reviewed').style.opacity = '';
  document.getElementById('btn-mark-reviewed').style.pointerEvents = '';
  document.getElementById('btn-needs-review').style.opacity = '';
  document.getElementById('btn-needs-review').style.pointerEvents = '';
  // Reload current live file
  reloadCurrentFile().then(() => fetchVersions(currentReviewFile));
}

async function restoreVersion() {
  if (!currentReviewFile || !viewingVersion) return;
  try {
    const res = await apiFetch('/api/version/restore', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: currentReviewFile, id: viewingVersion.id })
    });
    if (!res.ok) { showToast('Restore failed', 'error'); return; }
    showToast('Version restored as current file', 'success');
    closeVersion();
    loadState();
  } catch(e) {
    showToast('Restore failed', 'error');
  }
}

async function reloadCurrentFile() {
  if (!currentReviewFile) return;
  try {
    const res = await apiFetch(`/api/file?path=${encodeURIComponent(currentReviewFile)}`);
    if (res.ok) {
      const text = await res.text();
      const raw = text || '(empty file)';
      document.getElementById('viewer-content').innerHTML = renderMarkdown(raw);
      document.getElementById('viewer-raw-pre').textContent = raw;
    }
  } catch (e) {}
}

async function submitFix() {
  if (!currentReviewFile) { showToast('Select a file first', 'error'); return; }
  const critique = document.getElementById('critique-textarea').value.trim();
  if (!critique) { showToast('Enter a critique first', 'error'); return; }

  // Immediately show fixing state before the request even goes out
  fixingFile = currentReviewFile;
  document.getElementById('critique-textarea').value = '';
  const overlay = document.getElementById('viewer-fix-overlay');
  if (overlay) {
    overlay.style.display = 'flex';
    document.getElementById('viewer-fix-filename').textContent = fixingFile;
  }
  const fixBtn = document.getElementById('btn-fix-regenerate');
  if (fixBtn) fixBtn.disabled = true;
  document.getElementById('meta-status').innerHTML = `<span class="badge badge-needs-review">regenerating</span>`;

  try {
    await apiFetch('/api/fix', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: currentReviewFile, critique })
    });
    showToast('Regeneration started', 'info');
  } catch (e) {
    showToast('Failed to start regeneration', 'error');
    fixingFile = null;
    if (overlay) overlay.style.display = 'none';
    if (fixBtn) fixBtn.disabled = false;
  }
}

// ============================================================
// Build
// ============================================================
// ============================================================
// Build System
// ============================================================
const BUILD_STEPS_META = {
  backend:     { label: 'Backend & API',     desc: 'Models, endpoints, business logic' },
  frontend:    { label: 'Frontend UI',       desc: 'Components, pages, routing' },
  integration: { label: 'Integration Layer', desc: 'API client, third-party adapters' },
  tests:       { label: 'Test Suite',        desc: 'Unit, integration, and e2e tests' },
  infra:       { label: 'Infrastructure',    desc: 'Docker, CI/CD, monitoring config' },
};

let buildStepsState = {};  // populated from /api/build-system
let buildCodePanelStep = null;

async function fetchBuildSteps() {
  try {
    const res = await apiFetch('/api/build-system');
    if (res.ok) {
      const data = await res.json();
      buildStepsState = data.steps || {};
      renderBuildSteps();
    }
  } catch (e) {}
}

function renderBuildSteps() {
  const grid = document.getElementById('build-steps-grid');
  if (!grid) return;
  const isRunning = (state.processing && state.processing.status === 'running');

  grid.innerHTML = Object.entries(BUILD_STEPS_META).map(([key, meta]) => {
    const st = buildStepsState[key] || { status: 'idle', files: [] };
    const fileCount = (st.files || []).length;
    const isThisRunning = isRunning && (state.processing.stage === key || state.processing.stage === 'all');

    let statusBadge, footerHtml;
    if (isThisRunning) {
      statusBadge = `<span class="badge" style="background:var(--blue-light,#dbeafe);color:var(--blue);">
        <span class="spinner" style="display:inline-block;width:8px;height:8px;border:1.5px solid var(--blue);border-top-color:transparent;border-radius:50%;animation:spin 0.7s linear infinite;margin-right:4px;vertical-align:middle;"></span>Building</span>`;
      footerHtml = `<span style="font-size:11px;color:var(--text-3);">Running...</span>`;
    } else if (st.status === 'complete') {
      statusBadge = `<span class="badge badge-success">Complete</span>`;
      footerHtml = `<span style="font-size:11px;color:var(--text-3);">${fileCount} file${fileCount !== 1 ? 's' : ''} generated</span>
        <button class="btn btn-secondary btn-sm" onclick="openBuildCodePanel('${key}')">View Code</button>`;
    } else if (st.status === 'error') {
      statusBadge = `<span class="badge badge-error" title="${escapeHtml(st.error || '')}">Error</span>`;
      footerHtml = `<span style="font-size:11px;color:var(--red);max-width:120px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${escapeHtml(st.error || '')}">${escapeHtml((st.error || 'Failed').substring(0, 40))}</span>`;
    } else {
      statusBadge = `<span class="badge" style="background:var(--bg-2);color:var(--text-3);">Not started</span>`;
      footerHtml = `<span style="font-size:11px;color:var(--text-3);">Ready to build</span>`;
    }

    const canRun = !isRunning;
    return `<div class="card" style="padding:12px;display:flex;flex-direction:column;gap:8px;${st.status==='error'?'border-color:var(--red);':st.status==='complete'?'border-color:var(--green);':''}">
      <div style="display:flex;align-items:center;justify-content:space-between;">
        <span style="font-size:12px;font-weight:600;color:var(--text-1);">${meta.label}</span>
        ${statusBadge}
      </div>
      <div style="font-size:11px;color:var(--text-3);flex:1;">${meta.desc}</div>
      <div style="display:flex;align-items:center;justify-content:space-between;gap:6px;flex-wrap:wrap;">
        ${footerHtml}
        <button class="btn btn-primary btn-sm" onclick="runBuildStep('${key}')" ${canRun ? '' : 'disabled'} style="margin-left:auto;">
          ${st.status === 'complete' ? 'Rebuild' : 'Build'}
        </button>
      </div>
    </div>`;
  }).join('');
}

async function runBuildStep(step) {
  try {
    optimisticRunning = { stage: step, startTime: Date.now() };
    renderBuildSteps();
    const res = await apiFetch('/api/build-system', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ step })
    });
    if (!res.ok) {
      const data = await res.json();
      showToast(data.error || 'Build failed to start', 'error');
      optimisticRunning = null;
    }
  } catch (e) {
    showToast('Build failed to start', 'error');
    optimisticRunning = null;
  }
}

async function openBuildCodePanel(step) {
  buildCodePanelStep = step;
  const panel = document.getElementById('build-code-panel');
  const title = document.getElementById('build-code-panel-title');
  panel.style.display = 'block';
  title.textContent = BUILD_STEPS_META[step]?.label + ' — Generated Files';
  document.getElementById('build-file-content').textContent = '';

  const files = (buildStepsState[step] || {}).files || [];
  const tree = document.getElementById('build-file-tree');
  if (files.length === 0) {
    tree.innerHTML = '<div style="font-size:11px;color:var(--text-3);padding:8px;">No files yet.</div>';
    return;
  }
  tree.innerHTML = files.map(f => `
    <div class="tree-file" onclick="loadBuildFile('${step}','${escapeHtml(f)}')"
      style="padding:3px 6px;border-radius:4px;cursor:pointer;font-size:11px;color:var(--text-2);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"
      onmouseover="this.style.background='var(--bg-2)'" onmouseout="this.style.background=''">
      ${escapeHtml(f)}
    </div>`).join('');

  // Auto-load first file
  if (files.length > 0) loadBuildFile(step, files[0]);
}

async function loadBuildFile(step, path) {
  try {
    const res = await apiFetch('/api/build-file?step=' + encodeURIComponent(step) + '&path=' + encodeURIComponent(path));
    if (res.ok) {
      const data = await res.json();
      document.getElementById('build-file-content').textContent = data.content;
    }
  } catch (e) {}
}

function closeBuildCodePanel() {
  document.getElementById('build-code-panel').style.display = 'none';
  buildCodePanelStep = null;
}

const BUILD_STATUS_LABELS = {
  merged:     'Merged',
  pr_created: 'PR Open',
  pushed:     'Pushed',
  pushing:    'Pushing…',
  committed:  'Committed',
  branched:   'Branched',
  pending:    'Pending',
  error:      'Error',
};

const BUILD_STEP_ICONS = {
  pr_created: 'checkCircle',
  pushed:     'cloudUp',
  pushing:    'cloudUp',
  committed:  'gitBranch',
  branched:   'gitBranch',
  pending:    'clock',
  error:      'xCircle',
};

function renderBuild() {
  fetchBuildSteps();
  syncReviewStatus();
  checkAllPrStatuses();
  const git = state.git || {};
  const builds = state.builds || [];

  const gitSummary = document.getElementById('build-git-summary');
  if (git.repo_url) {
    gitSummary.innerHTML = `
      <div style="display:flex;flex-direction:column;gap:4px;">
        <div><span style="color:var(--text-3)">Repo:</span> <code style="font-size:11px">${escapeHtml(git.repo_url)}</code></div>
        <div><span style="color:var(--text-3)">Branch prefix:</span> <code style="font-size:11px">${escapeHtml(git.branch_prefix || 'forge')}</code></div>
        <div><span style="color:var(--text-3)">Default branch:</span> <code style="font-size:11px">${escapeHtml(git.default_branch || 'main')}</code></div>
      </div>
    `;
  } else {
    gitSummary.innerHTML = `<span style="color:var(--text-3)">No git repository configured. <a href="#" onclick="switchView('settings')" style="color:var(--blue)">Configure in Settings</a></span>`;
  }

  const historyEl = document.getElementById('build-history');
  if (builds.length === 0) {
    historyEl.innerHTML = `<div style="font-size:12px;color:var(--text-3);padding:20px;text-align:center;">No builds yet. Click "Review &amp; Push" to create your first build.</div>`;
    return;
  }

  historyEl.innerHTML = [...builds].reverse().map(b => {
    const logs = (b.log || []).join('\n');
    const statusLabel = BUILD_STATUS_LABELS[b.status] || b.status;
    const isLive = !b.log; // in-progress entries have no log yet

    const isMerged = b.status === 'merged';
    const prCard = b.pr_url ? (isMerged ? `
      <div style="display:flex;align-items:center;gap:10px;padding:10px 12px;background:rgba(139,92,246,.12);border-radius:6px;border:1px solid #8b5cf6;margin-top:8px;">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#8b5cf6" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M6 3v12"/><circle cx="18" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M18 9a9 9 0 01-9 9"/></svg>
        <div style="flex:1;min-width:0;">
          <div style="font-size:12px;font-weight:700;color:#8b5cf6;">Shipped to ${escapeHtml((state.git||{}).default_branch||'main')} ✓</div>
          <div style="font-size:11px;color:var(--text-3);">
            ${b.merged_by ? `Merged by <b>${escapeHtml(b.merged_by)}</b>` : 'Merged'}
            ${b.merged_at ? ' · ' + new Date(b.merged_at).toLocaleString() : ''}
            ${b.branch_deleted ? ' · <span style="color:#8b5cf6">branch deleted</span>' : ''}
          </div>
        </div>
        <a href="${b.pr_url}" target="_blank" class="btn btn-ghost btn-sm" style="white-space:nowrap;flex-shrink:0;">
          ${icon('externalLink',12)} View PR
        </a>
      </div>` : `
      <div style="display:flex;align-items:center;gap:10px;padding:10px 12px;background:var(--green-dim);border-radius:6px;border:1px solid var(--green);margin-top:8px;">
        ${icon('checkCircle',16)}
        <div style="flex:1;min-width:0;">
          <div style="font-size:12px;font-weight:600;color:var(--green);">Pull Request Open — awaiting review</div>
          <div style="font-size:11px;color:var(--text-2);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${escapeHtml(b.pr_url)}</div>
        </div>
        <button class="btn btn-ghost btn-xs" onclick="checkPrStatus('${escapeHtml(b.pr_url)}')" style="flex-shrink:0;" title="Check if merged">
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M1 4v6h6"/><path d="M23 20v-6h-6"/><path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4-4.64 4.36A9 9 0 0 1 3.51 15"/></svg>
        </button>
        <a href="${b.pr_url}" target="_blank" class="btn btn-sm" style="background:var(--green);color:#fff;border-color:var(--green);white-space:nowrap;flex-shrink:0;">
          ${icon('externalLink',12)} Open PR
        </a>
      </div>`) : '';

    const liveProgress = isLive ? `
      <div style="margin-top:8px;padding:8px 10px;background:var(--bg-2);border-radius:6px;font-size:11px;color:var(--text-2);display:flex;align-items:center;gap:8px;">
        <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--blue);animation:pulse 1.2s ease-in-out infinite;"></span>
        ${statusLabel} — branch <code>${escapeHtml(b.branch)}</code>
      </div>` : '';

    const copyBtn = `<button class="btn btn-ghost btn-sm" onclick="navigator.clipboard.writeText('${escapeHtml(b.branch)}')" style="margin-left:4px;padding:2px 6px;" title="Copy branch name">${icon('clipboardCopy',11)}</button>`;

    return `
      <div class="build-history-item" ${isLive ? 'style="border-color:var(--blue)"' : ''}>
        <div class="build-history-header">
          <span class="badge badge-${b.status}">${statusLabel}</span>
          <span class="build-branch">${escapeHtml(b.branch)}</span>
          ${copyBtn}
          <span class="build-date" style="margin-left:auto;">${new Date(b.created_at).toLocaleString()}</span>
        </div>
        ${liveProgress}
        ${prCard}
        ${logs ? `<details style="margin-top:8px;"><summary style="font-size:11px;color:var(--text-3);cursor:pointer;">Build log (${(b.log||[]).length} lines)</summary><div class="build-log" style="margin-top:4px;">${escapeHtml(logs)}</div></details>` : ''}
      </div>
    `;
  }).join('');
}

// ============================================================
// Pre-push review flow
// ============================================================
// ============================================================
// PR merge status
// ============================================================
const _checkedPrUrls = new Set();   // avoid re-checking already-merged PRs this session

async function checkAllPrStatuses() {
  const builds = state.builds || [];
  const git = state.git || {};
  if (!git.token) return;           // no token = can't call GitHub API
  for (const b of builds) {
    if (!b.pr_url) continue;
    if (b.status === 'merged') continue;          // already terminal
    if (_checkedPrUrls.has(b.pr_url)) continue;  // already checked this session
    _checkedPrUrls.add(b.pr_url);
    checkPrStatus(b.pr_url);        // fire-and-forget; result comes on next state poll
  }
}

async function checkPrStatus(prUrl) {
  try {
    const res = await apiFetch('/api/pr-status?pr_url=' + encodeURIComponent(prUrl));
    const d = await res.json();
    if (d.merged) {
      // Remove from checked cache so the badge re-renders on next loadState()
      _checkedPrUrls.delete(prUrl);
      loadState();  // force immediate re-poll so merged badge appears without waiting
    }
  } catch (e) { /* silent */ }
}

let _reviewPollTimer = null;

async function syncReviewStatus() {
  // Called on every renderBuild() — re-attaches polling and panel after refresh/tab switch
  try {
    const res = await apiFetch('/api/build-review');
    const d = await res.json();
    if (!d || d.status === 'idle') return;
    // Show panel regardless of how we got here
    showReviewPanel(d);
    // Re-enable or disable the push button based on review state
    const btn = document.getElementById('btn-start-build');
    if (btn) btn.disabled = (d.status === 'reviewing');
    // If still running and no poll is active, restart polling
    if (d.status === 'reviewing' && !_reviewPollTimer) {
      pollReview();
    }
  } catch (e) { /* silent — network may not be ready */ }
}

async function startReviewAndPush() {
  const btn = document.getElementById('btn-start-build');
  btn.disabled = true;
  btn.innerHTML = `<span style="opacity:.6">Starting review…</span>`;

  try {
    const res = await apiFetch('/api/build-review', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });
    const d = await res.json();
    if (d.status === 'started' || d.status === 'already_reviewing') {
      showReviewPanel({ status: 'reviewing' });
      pollReview();
    } else {
      showToast('Could not start review', 'error');
      btn.disabled = false;
      btn.innerHTML = `${icon('eye',14)} Review &amp; Push`;
    }
  } catch (e) {
    showToast('Review failed to start', 'error');
    btn.disabled = false;
    btn.innerHTML = `${icon('eye',14)} Review &amp; Push`;
  }
}

function pollReview() {
  if (_reviewPollTimer) clearInterval(_reviewPollTimer);
  _reviewPollTimer = setInterval(async () => {
    try {
      const res = await apiFetch('/api/build-review');
      const d = await res.json();
      showReviewPanel(d);
      if (d.status !== 'reviewing') {
        clearInterval(_reviewPollTimer);
        _reviewPollTimer = null;
        // Re-enable the button
        const btn = document.getElementById('btn-start-build');
        if (btn) { btn.disabled = false; btn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7z"/><circle cx="12" cy="12" r="3"/></svg> Review &amp; Push`; }
      }
    } catch (e) { /* silent */ }
  }, 2500);
}

function showReviewPanel(data) {
  const panel = document.getElementById('review-panel');
  if (!panel) return;

  if (!data || data.status === 'idle') {
    panel.style.display = 'none';
    return;
  }

  panel.style.display = 'block';

  if (data.status === 'reviewing') {
    const linesNote = data.total_changed_lines > 800
      ? `<div style="font-size:11px;color:var(--text-3);margin-top:4px;">${data.total_changed_lines.toLocaleString()} lines changed — sending diff headers only to keep review fast.</div>`
      : '';
    panel.innerHTML = `
      <div class="card" style="border-color:var(--blue)">
        <div style="display:flex;align-items:center;gap:10px;padding:4px 0 8px">
          <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:var(--blue);animation:pulse 1.2s ease-in-out infinite;flex-shrink:0;"></span>
          <span style="font-size:13px;font-weight:600;color:var(--text-1)">AI code review in progress…</span>
        </div>
        <div style="font-size:12px;color:var(--text-3)">Reviewing only staged changes against spec docs.</div>
        ${linesNote}
        <div style="margin-top:12px;display:flex;gap:8px;">
          <button class="btn btn-ghost btn-sm" onclick="cancelReview()" style="color:var(--red);border-color:var(--red);">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
            Cancel Review
          </button>
          <button class="btn btn-secondary btn-sm" onclick="skipReviewAndPush()">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M6 3v12"/><circle cx="18" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M18 9a9 9 0 01-9 9"/></svg>
            Skip &amp; Push Directly
          </button>
        </div>
      </div>`;
    return;
  }

  if (data.status === 'cancelled') {
    panel.innerHTML = `
      <div class="card" style="border-color:var(--border)">
        <div style="font-size:13px;font-weight:600;color:var(--text-2);margin-bottom:8px;">Review cancelled</div>
        <div style="font-size:12px;color:var(--text-3);margin-bottom:12px;">Changes unstaged. You can start a new review or push directly.</div>
        <div style="display:flex;gap:8px;">
          <button class="btn btn-primary btn-sm" onclick="startReviewAndPush()">Start New Review</button>
          <button class="btn btn-secondary btn-sm" onclick="skipReviewAndPush()">Push Directly</button>
          <button class="btn btn-ghost btn-sm" onclick="cancelReview()">Dismiss</button>
        </div>
      </div>`;
    return;
  }

  if (data.status === 'no_changes') {
    panel.innerHTML = `
      <div class="card" style="border-color:var(--border)">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--text-3)" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          <span style="font-size:13px;font-weight:600;color:var(--text-2)">Nothing to push</span>
        </div>
        <div style="font-size:12px;color:var(--text-3);line-height:1.6;">${escapeHtml(data.review || 'No changes since the last commit.')}</div>
        <div style="margin-top:12px;">
          <button class="btn btn-ghost btn-sm" onclick="cancelReview()">Dismiss</button>
        </div>
      </div>`;
    return;
  }

  if (data.status === 'error') {
    panel.innerHTML = `
      <div class="card" style="border-color:var(--red)">
        <div style="font-size:13px;font-weight:600;color:var(--red);margin-bottom:8px;">${icon('xCircle',14)} Review Failed</div>
        <div style="font-size:12px;color:var(--text-2);white-space:pre-wrap;">${escapeHtml(data.review || 'Unknown error')}</div>
        <div style="margin-top:12px;display:flex;gap:8px;">
          <button class="btn btn-primary btn-sm" onclick="proceedWithPush()">Push Anyway</button>
          <button class="btn btn-ghost btn-sm" onclick="cancelReview()">Cancel</button>
        </div>
      </div>`;
    return;
  }

  // Review done
  const verdictMap = {
    approve:            { cls: 'var(--green)',  label: '✅ Approve',             hint: 'No blocking issues found.' },
    approve_with_notes: { cls: 'var(--yellow,#f59e0b)', label: '⚠️ Approve with Notes', hint: 'Minor issues noted — can proceed.' },
    request_changes:    { cls: 'var(--red)',    label: '❌ Request Changes',      hint: 'Issues must be fixed before merging.' },
    unknown:            { cls: 'var(--text-2)', label: '? Unknown verdict',       hint: '' },
    error:              { cls: 'var(--red)',    label: '! Error',                hint: '' },
  };
  const v = verdictMap[data.verdict] || verdictMap.unknown;

  const reviewHtml = (data.review || '').replace(/\n/g, '<br>').replace(/`([^`]+)`/g, '<code>$1</code>');

  panel.innerHTML = `
    <div class="card" style="border-color:${v.cls}">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
        <div>
          <div style="font-size:13px;font-weight:700;color:${v.cls}">${v.label}</div>
          <div style="font-size:11px;color:var(--text-3);margin-top:2px;">${v.hint}</div>
        </div>
        <div style="font-size:11px;color:var(--text-3);text-align:right;">
          ${data.diff_stat ? escapeHtml(data.diff_stat.split('\n').slice(-1)[0]) : ''}
        </div>
      </div>
      <details open style="margin-bottom:12px;">
        <summary style="font-size:12px;font-weight:600;color:var(--text-2);cursor:pointer;margin-bottom:8px;">Review details</summary>
        <div style="font-size:12px;color:var(--text-2);line-height:1.7;padding:10px;background:var(--bg-2);border-radius:6px;max-height:320px;overflow-y:auto;">${reviewHtml}</div>
      </details>
      ${data.diff_stat ? `
      <details style="margin-bottom:12px;">
        <summary style="font-size:12px;font-weight:600;color:var(--text-2);cursor:pointer;margin-bottom:8px;">Diff stat</summary>
        <pre style="font-size:10px;color:var(--green);background:var(--bg);padding:10px;border-radius:6px;overflow-x:auto;margin:0;">${escapeHtml(data.diff_stat)}</pre>
      </details>` : ''}
      <div style="display:flex;gap:8px;align-items:center;">
        <button class="btn btn-primary btn-sm" onclick="proceedWithPush()" style="${data.verdict === 'request_changes' ? 'background:var(--red);border-color:var(--red);' : ''}">
          ${icon('cloudUp',12)} ${data.verdict === 'request_changes' ? 'Push Anyway' : 'Approve &amp; Push'}
        </button>
        <button class="btn btn-ghost btn-sm" onclick="cancelReview()">
          Cancel
        </button>
        <span style="font-size:11px;color:var(--text-3);margin-left:auto;">${new Date(data.timestamp).toLocaleTimeString()}</span>
      </div>
    </div>`;
}

async function proceedWithPush() {
  const panel = document.getElementById('review-panel');
  if (panel) panel.innerHTML = `<div class="card" style="border-color:var(--blue)"><div style="font-size:13px;color:var(--blue);">${icon('cloudUp',14)} Pushing to GitHub…</div></div>`;

  try {
    const res = await apiFetch('/api/build', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reviewed: true })
    });
    const d = await res.json();
    showToast(`Build started: ${d.branch || ''}`, 'info');
    // Clear review file
    await apiFetch('/api/build-review', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'clear' }) });
    if (panel) panel.style.display = 'none';
    loadState();
  } catch (e) {
    showToast('Push failed', 'error');
  }
}

async function cancelReview() {
  // If reviewing → send cancel (kills AI process + unstages)
  // If done/cancelled/idle → just clear the panel
  let action = 'clear';
  try {
    const r = await apiFetch('/api/build-review');
    const d = await r.json();
    if (d.status === 'reviewing') action = 'cancel';
  } catch (e) { /* use clear */ }

  await apiFetch('/api/build-review', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action })
  });

  if (_reviewPollTimer) { clearInterval(_reviewPollTimer); _reviewPollTimer = null; }

  // If we cancelled a running review, show the cancelled card briefly then hide
  if (action === 'cancel') {
    // syncReviewStatus will pick up the cancelled state on next renderBuild cycle
    return;
  }

  // Otherwise just dismiss the panel
  const panel = document.getElementById('review-panel');
  if (panel) panel.style.display = 'none';
  const btn = document.getElementById('btn-start-build');
  if (btn) { btn.disabled = false; btn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7z"/><circle cx="12" cy="12" r="3"/></svg> Review &amp; Push`; }
}

async function skipReviewAndPush() {
  // Cancel any running review first, then push directly
  try {
    const r = await apiFetch('/api/build-review');
    const d = await r.json();
    if (d.status === 'reviewing') {
      await apiFetch('/api/build-review', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'cancel' })
      });
      // Give the server a moment to kill the process and unstage
      await new Promise(res => setTimeout(res, 800));
    }
  } catch (e) { /* proceed anyway */ }

  if (_reviewPollTimer) { clearInterval(_reviewPollTimer); _reviewPollTimer = null; }

  const panel = document.getElementById('review-panel');
  if (panel) panel.innerHTML = `<div class="card" style="border-color:var(--blue)"><div style="font-size:13px;color:var(--blue);">Pushing to GitHub…</div></div>`;

  try {
    const res = await apiFetch('/api/build', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });
    const d = await res.json();
    showToast(`Build started: ${d.branch || ''}`, 'info');
    await apiFetch('/api/build-review', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'clear' })
    });
    if (panel) panel.style.display = 'none';
    loadState();
  } catch (e) {
    showToast('Push failed', 'error');
  }
}

async function startBuild() {
  // Legacy: called from Overview quick action — goes directly to review flow
  switchView('build');
  await startReviewAndPush();
}

// ============================================================
// Deploy
// ============================================================
function renderDeploy() {
  const envs = state.environments || {};
  const envsEl = document.getElementById('deploy-envs');

  const envDefs = [
    { key: 'staging', label: 'Staging', iconName: 'beaker' },
    { key: 'production', label: 'Production', iconName: 'server' },
  ];

  envsEl.innerHTML = envDefs.map(def => {
    const env = envs[def.key] || {};
    const url = env.url || '';
    const branch = env.branch || '—';
    const status = env.status || 'not_deployed';
    const deployedAt = env.deployed_at ? new Date(env.deployed_at).toLocaleString() : 'Never';
    const statusBadge = status === 'deployed'
      ? '<span class="badge badge-pushed">Deployed</span>'
      : '<span class="badge badge-pending">Not Deployed</span>';

    return `
      <div class="env-card">
        <div class="env-name">${icon(def.iconName, 16)} ${def.label}</div>
        ${url ? `<div class="env-url"><a href="${url}" target="_blank" style="color:var(--blue);text-decoration:none">${url}</a></div>` : '<div class="env-url" style="color:var(--text-3)">No URL configured</div>'}
        <div class="env-field"><span class="env-field-key">Status</span><span>${statusBadge}</span></div>
        <div class="env-field"><span class="env-field-key">Branch</span><span class="env-field-val">${branch}</span></div>
        <div class="env-field"><span class="env-field-key">Last Deploy</span><span class="env-field-val">${deployedAt}</span></div>
        ${url ? `<a href="${url}" target="_blank" class="btn btn-ghost btn-sm" style="margin-top:8px;display:inline-flex">${icon('externalLink',12)} Open</a>` : ''}
      </div>
    `;
  }).join('');

  // Load secrets panel
  refreshSecrets();
}

// ============================================================
// Secrets & Variables
// ============================================================
let _secretsData = null;

async function refreshSecrets() {
  const container = document.getElementById('secrets-container');
  if (!container) return;
  try {
    const res = await apiFetch('/api/secrets');
    _secretsData = await res.json();
    renderSecretsTable(_secretsData);
  } catch (e) {
    container.innerHTML = `<div style="font-size:12px;color:var(--red);padding:12px 0">Failed to load secrets: ${e.message}</div>`;
  }
}

function renderSecretsTable(data) {
  const container = document.getElementById('secrets-container');
  if (!container) return;

  const secrets = data.secrets || [];
  const repo = data.repo || '';
  const hasToken = data.has_token;
  const ghCli = data.gh_cli;

  if (!hasToken) {
    container.innerHTML = `<div style="font-size:12px;color:var(--yellow,#f59e0b);padding:8px 0">${icon('warning',14)} GitHub token not configured. Add it in <button class="btn btn-ghost btn-xs" onclick="switchView('settings')">Settings</button> to push secrets.</div>`;
    return;
  }

  if (secrets.length === 0) {
    container.innerHTML = `<div style="font-size:12px;color:var(--text-3);padding:12px 0">No <code>secrets-required.md</code> found in build output. Run the <b>Infrastructure</b> build step first.</div>`;
    return;
  }

  const configured = secrets.filter(s => s.configured).length;
  const total = secrets.length;
  const pct = Math.round((configured / total) * 100);

  const statusBar = document.getElementById('secrets-status-bar');
  if (statusBar) {
    const allDone = configured === total;
    statusBar.style.display = 'block';
    statusBar.style.background = allDone ? 'var(--green-dim)' : 'var(--bg-2)';
    statusBar.style.color = allDone ? 'var(--green)' : 'var(--text-2)';
    statusBar.innerHTML = `${icon(allDone ? 'checkCircle' : 'informationCircle', 13)} &nbsp;${configured}/${total} secrets configured${repo ? ` &nbsp;·&nbsp; <span style="opacity:.7">github.com/${repo}</span>` : ''}${ghCli ? '' : ' &nbsp;·&nbsp; <span style="opacity:.6">Using GitHub API (install <code>gh</code> CLI for simpler auth)</span>'}`;
  }

  container.innerHTML = `
    <table class="secrets-table">
      <thead>
        <tr>
          <th style="width:200px">Name</th>
          <th>Description</th>
          <th style="width:80px">Workflow</th>
          <th style="width:60px">Status</th>
          <th style="width:240px">Value</th>
          <th style="width:110px">Type</th>
          <th style="width:80px"></th>
        </tr>
      </thead>
      <tbody>
        ${secrets.map(s => `
          <tr id="secret-row-${s.name}">
            <td><span class="secret-name">${escapeHtml(s.name)}</span></td>
            <td><span class="secret-desc">${escapeHtml(s.description)}</span></td>
            <td><span style="font-size:10px;color:var(--text-3)">${escapeHtml(s.workflow || '')}</span></td>
            <td>
              ${s.configured
                ? `<span class="badge badge-configured" title="Set ${s.set_at ? new Date(s.set_at).toLocaleString() : ''}">${icon('checkCircle',11)} Set</span>`
                : `<span class="badge badge-missing">Missing</span>`
              }
            </td>
            <td>
              <div class="secret-input-wrap">
                <input type="password"
                  class="secret-input"
                  id="secret-val-${s.name}"
                  placeholder="${s.configured ? '••••••• (leave blank to skip)' : 'Enter value…'}"
                  autocomplete="new-password"
                />
              </div>
            </td>
            <td>
              <label class="secret-type-toggle">
                <input type="checkbox"
                  id="secret-prot-${s.name}"
                  ${s.protected !== false ? 'checked' : ''}
                  onchange="updateSecretTypeBadge('${s.name}')"
                />
                <span id="secret-type-badge-${s.name}" class="badge ${s.protected !== false ? 'badge-secret' : 'badge-variable'}">
                  ${s.protected !== false ? 'Secret' : 'Variable'}
                </span>
              </label>
            </td>
            <td>
              <button class="btn btn-primary btn-xs secrets-push-btn"
                onclick="pushSecret('${s.name}')"
                id="secret-btn-${s.name}">
                ${icon('cloudUp', 11)} Push
              </button>
            </td>
          </tr>
        `).join('')}
      </tbody>
    </table>
    <div style="margin-top:12px;display:flex;gap:8px;align-items:center">
      <button class="btn btn-primary btn-sm" onclick="pushAllSecrets()">
        ${icon('cloudUp', 12)} Push All Filled
      </button>
      <span style="font-size:11px;color:var(--text-3)">Only rows with a value entered will be pushed</span>
    </div>
  `;
}

function updateSecretTypeBadge(name) {
  const chk = document.getElementById(`secret-prot-${name}`);
  const badge = document.getElementById(`secret-type-badge-${name}`);
  if (!chk || !badge) return;
  if (chk.checked) {
    badge.className = 'badge badge-secret';
    badge.textContent = 'Secret';
  } else {
    badge.className = 'badge badge-variable';
    badge.textContent = 'Variable';
  }
}

async function pushSecret(name) {
  const valEl = document.getElementById(`secret-val-${name}`);
  const protEl = document.getElementById(`secret-prot-${name}`);
  const btn = document.getElementById(`secret-btn-${name}`);
  if (!valEl || !btn) return;

  const value = valEl.value.trim();
  if (!value) {
    showToast(`Enter a value for ${name} first`, 'error');
    return;
  }

  btn.disabled = true;
  btn.innerHTML = `<span style="opacity:.6">Pushing…</span>`;

  try {
    const res = await apiFetch('/api/secrets', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, value, protected: protEl ? protEl.checked : true }),
    });
    const d = await res.json();
    if (!res.ok) throw new Error(d.error || 'Failed');
    valEl.value = '';
    showToast(`${name} pushed to GitHub`, 'success');
    await refreshSecrets();
  } catch (e) {
    showToast(`Failed: ${e.message}`, 'error');
    btn.disabled = false;
    btn.innerHTML = `${icon('cloudUp', 11)} Push`;
  }
}

async function pushAllSecrets() {
  const secrets = (_secretsData && _secretsData.secrets) || [];
  const toPush = secrets.filter(s => {
    const v = document.getElementById(`secret-val-${s.name}`);
    return v && v.value.trim();
  });
  if (toPush.length === 0) {
    showToast('No values filled in — enter values first', 'error');
    return;
  }
  for (const s of toPush) {
    await pushSecret(s.name);
  }
}

// ============================================================
// Issues
// ============================================================
function renderIssues() {
  const issues = state.issues || [];
  const listEl = document.getElementById('issue-list');

  if (issues.length === 0) {
    listEl.innerHTML = `<div style="font-size:12px;color:var(--text-3);padding:20px;text-align:center;">No issues yet. Click "New Issue" to create one.</div>`;
    return;
  }

  listEl.innerHTML = [...issues].reverse().map(issue => {
    const iconName = ISSUE_TYPE_ICONS[issue.type] || 'questionCircle';
    const statusCls = issue.status === 'open' ? 'badge-open'
      : issue.status === 'in-progress' ? 'badge-in-progress'
      : 'badge-closed';
    const priorCls = `priority-${issue.priority || 'medium'}`;

    return `
      <div class="issue-item" id="issue-${issue.id}" onclick="toggleIssue('${issue.id}')">
        <div class="issue-item-header">
          <span class="issue-id">${issue.id}</span>
          <span class="issue-type-icon">${icon(iconName, 14)}</span>
          <span class="issue-title">${escapeHtml(issue.title)}</span>
          <span class="badge ${priorCls}">${issue.priority || 'medium'}</span>
          <span class="badge ${statusCls}">${issue.status}</span>
        </div>
        <div class="issue-body">
          <div class="issue-desc">${escapeHtml(issue.description || '')}</div>
          <div style="font-size:10px;color:var(--text-3);margin-bottom:8px">Created: ${new Date(issue.created_at).toLocaleString()}</div>
          <div class="issue-actions">
            ${issue.status !== 'closed'
              ? `<button class="btn btn-ghost btn-xs" onclick="event.stopPropagation();updateIssue('${issue.id}',{status:'closed'})">Close</button>`
              : `<button class="btn btn-ghost btn-xs" onclick="event.stopPropagation();updateIssue('${issue.id}',{status:'open'})">Reopen</button>`
            }
            ${issue.status === 'open'
              ? `<button class="btn btn-ghost btn-xs" onclick="event.stopPropagation();updateIssue('${issue.id}',{status:'in-progress'})">Start</button>`
              : ''
            }
          </div>
        </div>
      </div>
    `;
  }).join('');
}

function toggleIssue(id) {
  const el = document.getElementById(`issue-${id}`);
  if (el) el.classList.toggle('expanded');
}

function toggleIssueForm() {
  const form = document.getElementById('issue-create-form');
  form.style.display = form.style.display === 'none' ? '' : 'none';
}

async function createIssue() {
  const type = document.getElementById('new-issue-type').value;
  const priority = document.getElementById('new-issue-priority').value;
  const title = document.getElementById('new-issue-title').value.trim();
  const description = document.getElementById('new-issue-desc').value.trim();
  if (!title) { showToast('Title is required', 'error'); return; }

  try {
    await apiFetch('/api/issue', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type, priority, title, description })
    });
    document.getElementById('new-issue-title').value = '';
    document.getElementById('new-issue-desc').value = '';
    toggleIssueForm();
    showToast('Issue created', 'success');
    loadState();
  } catch (e) {
    showToast('Failed to create issue', 'error');
  }
}

async function updateIssue(id, data) {
  try {
    await apiFetch('/api/issue', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id, ...data })
    });
    showToast('Issue updated', 'success');
    loadState();
  } catch (e) {
    showToast('Failed to update issue', 'error');
  }
}

// ============================================================
// Settings
// ============================================================
let detectedTools = null;  // populated from /api/tools on settings open

async function fetchDetectedTools() {
  try {
    const res = await apiFetch('/api/tools');
    detectedTools = await res.json();
    // Rebuild tool dropdown to show only installed tools (with badge for uninstalled)
    const toolSel = document.getElementById('settings-tool');
    if (!toolSel) return;
    const currentTool = getValue('settings-tool') || state.tool || 'gemini';
    toolSel.innerHTML = Object.entries(detectedTools).map(([id, info]) => {
      const badge = info.installed ? '' : ' (not installed)';
      return `<option value="${id}" ${id === currentTool ? 'selected' : ''} ${info.installed ? '' : 'style="color:var(--text-3)"'}>${info.label}${badge}</option>`;
    }).join('');
    populateModelDropdown(currentTool, state.model || '');
  } catch(e) {}
}

function populateModelDropdown(tool, currentModel) {
  const sel = document.getElementById('settings-model');
  const hint = document.getElementById('settings-model-hint');
  if (!sel) return;
  const toolInfo = detectedTools ? detectedTools[tool] : null;
  const opts = toolInfo ? toolInfo.models : [];
  sel.innerHTML = opts.map(o =>
    `<option value="${o.id}" ${o.id === currentModel ? 'selected' : ''}>${o.label}</option>`
  ).join('');
  if (currentModel && !opts.find(o => o.id === currentModel)) {
    sel.insertAdjacentHTML('afterbegin', `<option value="${currentModel}" selected>${currentModel}</option>`);
  }
  const installed = toolInfo ? toolInfo.installed : true;
  if (hint) hint.textContent = installed
    ? `Passed as -m flag to the ${tool} CLI`
    : `⚠ ${tool} is not installed — generation will fail`;
}

function renderSettings() {
  const git = state.git || {};
  const envs = state.environments || {};

  setValue('settings-product-name', state.project_name || '');
  const vl = document.getElementById('settings-version-label');
  if (vl) vl.textContent = state.version ? `v${state.version}` : 'v—';
  setValue('settings-tool', state.tool || 'gemini');
  populateModelDropdown(state.tool || 'gemini', state.model || '');
  fetchDetectedTools();
  setValue('settings-repo-url', git.repo_url || '');
  setValue('settings-username', git.username || '');
  setValue('settings-email', git.email || '');
  setValue('settings-token', git.token || '');
  setValue('settings-default-branch', git.default_branch || 'main');
  setValue('settings-branch-prefix', git.branch_prefix || 'forge');
  setValue('settings-staging-url', (envs.staging || {}).url || '');
  setValue('settings-staging-branch', (envs.staging || {}).branch || 'staging');
  setValue('settings-production-url', (envs.production || {}).url || '');
  setValue('settings-production-branch', (envs.production || {}).branch || 'main');
}

async function saveSettings() {
  const data = {
    project_name: getValue('settings-product-name'),
    tool: getValue('settings-tool'),
    model: getValue('settings-model'),
    git: {
      repo_url: getValue('settings-repo-url'),
      username: getValue('settings-username'),
      email: getValue('settings-email'),
      token: getValue('settings-token'),
      default_branch: getValue('settings-default-branch'),
      branch_prefix: getValue('settings-branch-prefix'),
    },
    environments: {
      staging: {
        url: getValue('settings-staging-url'),
        branch: getValue('settings-staging-branch'),
      },
      production: {
        url: getValue('settings-production-url'),
        branch: getValue('settings-production-branch'),
      }
    }
  };

  try {
    await apiFetch('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    showToast('Settings saved', 'success');
    runtimeInitialized = false;
    loadState();
  } catch (e) {
    showToast('Failed to save settings', 'error');
  }
}

// ============================================================
// Navigation
// ============================================================
function switchView(name) {
  currentView = name;
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

  const viewEl = document.getElementById(`view-${name}`);
  if (viewEl) viewEl.classList.add('active');

  const navEl = document.querySelector(`.nav-item[data-view="${name}"]`);
  if (navEl) navEl.classList.add('active');
}

// ============================================================
// Utilities
// ============================================================
function showToast(msg, type = 'info') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = msg;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3500);
}

function escapeHtml(s) {
  if (!s) return '';
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function setValue(id, val) {
  const el = document.getElementById(id);
  if (!el) return;
  el.value = val;
}

function getValue(id) {
  const el = document.getElementById(id);
  return el ? el.value : '';
}

// ============================================================
// Reset
// ============================================================
function openResetDialog() {
  document.getElementById('reset-confirm-input').value = '';
  document.getElementById('btn-confirm-reset').disabled = true;
  document.getElementById('reset-dialog').classList.remove('hidden');
  document.getElementById('reset-confirm-input').focus();
}

function closeResetDialog() {
  document.getElementById('reset-dialog').classList.add('hidden');
}

async function resetPipeline() {
  closeResetDialog();
  try {
    const res = await apiFetch('/api/reset', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' });
    const data = await res.json();
    showToast(`Pipeline reset — ${data.cleared} files cleared`, 'success');
    currentReviewFile = null;
    document.getElementById('viewer-content').innerHTML = 'Select a file from the tree to review its contents.';
    document.getElementById('viewer-raw-pre').textContent = '';
    document.getElementById('viewer-filename').textContent = 'Select a file';
    document.getElementById('btn-mark-reviewed').style.display = 'none';
    document.getElementById('btn-needs-review').style.display = 'none';
    document.getElementById('viewer-mode-toggle').style.display = 'none';
    loadState();
  } catch (e) {
    showToast('Reset failed', 'error');
  }
}

// ============================================================
// Keyboard shortcuts
// ============================================================
const viewKeys = ['overview','input','generate','review','build','deploy','issues','settings'];
document.addEventListener('keydown', e => {
  if (appMode === 'projects') return;
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') return;
  const n = parseInt(e.key);
  if (n >= 1 && n <= viewKeys.length) {
    switchView(viewKeys[n - 1]);
  }
});

// ============================================================
// Init
// ============================================================
document.getElementById('project-create-name')?.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') createProjectFromHome();
});
startPolling();
