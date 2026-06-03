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
  lock: `<path d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z"/>`,
  bolt: `<path d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z"/>`,
  cog: `<path d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z"/><path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>`,
  arrowUp: `<path d="M4.5 10.5L12 3m0 0l7.5 7.5M12 3v18"/>`,
  download: `<path d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3"/>`,
  clipboard: `<path d="M15.666 3.888A2.25 2.25 0 0013.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 01-.75.75H9a.75.75 0 01-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 01-2.25 2.25H6.75A2.25 2.25 0 014.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 011.927-.184"/>`,
  codeSquare: `<path d="M14.25 9.75L16.5 12l-2.25 2.25m-4.5 0L7.5 12l2.25-2.25M6 20.25h12A2.25 2.25 0 0020.25 18V6A2.25 2.25 0 0018 3.75H6A2.25 2.25 0 003.75 6v12A2.25 2.25 0 006 20.25z"/>`,
  warning: `<path d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"/>`,
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

function setViewerContent(html) {
  const el = document.getElementById('viewer-content');
  if (!el) return;
  el.innerHTML = html;
  if (typeof _renderMermaidInEl === 'function') _renderMermaidInEl(el);
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
let inputFileModified = false;
let currentReviewFile = null;
let runtimeInitialized = false;
let pollInterval = null;

// Phase auto-sync: tracks allReviewed across polls to detect 100% transition
let _prevAllReviewed = null;  // null = not yet seen (skip first load)

// Generation tracking
let lastProcessingStatus = 'idle';
let lastSeenErrorTs = localStorage.getItem('forge_lastSeenErrorTs') || null;
let optimisticRunning = null;  // {stage, startTime} — card spinner only, never drives toasts
let fixingFile = null;
let _fixSubmittedAt = 0; // timestamp when submitFix() was called
let viewingVersion = null;  // {id, timestamp} when viewing a historic version, null = current

const PIPELINE_STAGE_ORDER = ['context','requirements','design','analysis','architecture','delivery','engineering','qa','operations','release','marketing'];

const VIEWER_DEFAULT_HTML = `
  <div class="viewer-empty-state viewer-empty-state--default">
    <div class="viewer-empty-icon">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"/>
        <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
      </svg>
    </div>
    <div class="viewer-empty-title">Select a document</div>
    <div class="viewer-empty-desc">Choose a file from the left panel to read its contents and mark it as reviewed.</div>
  </div>`;

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

const STAGE_DIR_TO_LABEL = Object.fromEntries(STAGES.map(s => [s.dir, s.label]));

function _fmtFileName(name) {
  return name.replace(/\.md$/, '').replace(/[-_]/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

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
  unnamed: 'My Project',
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

const PROJECT_HOME_FOCUS_IDS = ['project-create-name', 'project-search'];

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

    // Auto-sync phases when review transitions to 100%
    const nowAllReviewed = !!state.allReviewed;
    if (_prevAllReviewed === false && nowAllReviewed) {
      _autoSyncPhases();
    }
    _prevAllReviewed = nowAllReviewed;

    // Kick off tool detection in background — doesn't block render
    fetchToolStatus(false).then(function() { renderAll(); });
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
  renderPhases();
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
  const focusSnapshot = captureProjectHomeFocus();
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
  restoreProjectHomeFocus(focusSnapshot);
}

function captureProjectHomeFocus() {
  const activeElement = document.activeElement;
  if (!activeElement || !PROJECT_HOME_FOCUS_IDS.includes(activeElement.id)) return null;
  return {
    id: activeElement.id,
    start: typeof activeElement.selectionStart === 'number' ? activeElement.selectionStart : null,
    end: typeof activeElement.selectionEnd === 'number' ? activeElement.selectionEnd : null,
  };
}

function restoreProjectHomeFocus(snapshot) {
  if (!snapshot) return;
  const input = document.getElementById(snapshot.id);
  if (!input) return;
  input.focus();
  if (snapshot.start !== null && snapshot.end !== null && typeof input.setSelectionRange === 'function') {
    input.setSelectionRange(snapshot.start, snapshot.end);
  }
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
    // Clear fixingFile when: we saw fixing→idle transition, OR we submitted a fix
    // and the server is idle 5s+ later (fast completion missed between polls).
    const fixMissedTransition = fixingFile && _fixSubmittedAt && (Date.now() - _fixSubmittedAt > 5000);
    if ((lastProcessingStatus === 'fixing' || fixMissedTransition) && fixingFile) {
      if (!lastError) {
        showToast('Regeneration complete', 'success');
      }
      if (currentReviewFile === fixingFile) {
        reloadCurrentFile();
      }
      // Notify about downstream docs that were reset to needs_review
      const consistency = processing.consistency_check;
      if (consistency && consistency.affected_count > 0) {
        const n = consistency.affected_count;
        setTimeout(() => {
          showToast(`${n} downstream doc${n > 1 ? 's' : ''} marked for re-review — check the Review tree`, 'info');
        }, 1200);
      }
      fixingFile = null;
      _fixSubmittedAt = 0;
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
  const git = state.git || {};
  const processing = state.processing || {};
  const rawInputs = state.rawInputs || [];
  const builds = state.builds || [];

  const pname = state.project_name || 'My Project';
  document.getElementById('overview-project-name').textContent = pname;

  // Quick action (header CTA)
  const quickActions = {
    input:    `<button class="btn btn-primary btn-sm" onclick="switchView('input');openNewFileDialog()">${icon('sparkles',12)} Create Input</button>`,
    generate: `<button class="btn btn-primary btn-sm" onclick="switchView('generate');generate('all')">${icon('sparkles',12)} Generate All</button>`,
    review:   `<button class="btn btn-primary btn-sm" onclick="switchView('review')">${icon('eye',12)} Review Docs</button>`,
    build:    `<button class="btn btn-primary btn-sm" onclick="switchView('build')">${icon('gitBranch',12)} Go to Build</button>`,
    deploy:   `<button class="btn btn-primary btn-sm" onclick="switchView('deploy')">${icon('cloudUp',12)} Go to Deploy</button>`,
  };
  document.getElementById('overview-quick-action').innerHTML = quickActions[phase] || '';

  // ── Phase progress strip ──────────────────────────────────────────────────
  const totalDocs = STAGES.reduce((n, s) => n + ((summary[s.dir] || {}).total || 0), 0);
  const totalGenerated = STAGES.reduce((n, s) => n + ((summary[s.dir] || {}).generated || 0), 0);
  const totalReviewed = STAGES.reduce((n, s) => n + ((summary[s.dir] || {}).reviewed || 0), 0);
  const gatesPassed = Object.values(gates).filter(v => v === 'PASSED').length;
  const gatesTotal = Object.keys(gates).length || 8;

  const subtitleParts = [];
  if (totalGenerated > 0) subtitleParts.push(`${totalGenerated} docs generated`);
  if (totalReviewed > 0) subtitleParts.push(`${totalReviewed} reviewed`);
  if (gatesPassed > 0) subtitleParts.push(`${gatesPassed}/${gatesTotal} gates passed`);
  document.getElementById('overview-subtitle').textContent = subtitleParts.length > 0 ? subtitleParts.join(' · ') : 'Product Lifecycle';

  // Phase badge — show input count or doc progress instead of redundant phase label
  const badgeEl = document.getElementById('overview-phase-badge');
  if (badgeEl) badgeEl.innerHTML = '';

  const phasePcts = {
    input:    rawInputs.length > 0 ? 100 : 0,
    generate: totalDocs > 0 ? Math.round((totalGenerated / totalDocs) * 100) : 0,
    review:   totalGenerated > 0 ? Math.round((totalReviewed / totalGenerated) * 100) : 0,
    build:    (() => { const hasBuildFiles = Object.values(buildStepsState).some(s => s.status === 'complete'); return hasBuildFiles ? 100 : 0; })(),
    deploy:   (() => { const envs = state.environments || {}; return ((envs.staging || {}).url || (envs.production || {}).url) ? 100 : 0; })(),
  };

  const phaseStates = PHASES.map((p, i) => {
    if (i < phaseIdx) return 'done';
    if (i === phaseIdx) return 'active';
    return 'pending';
  });

  const stripEl = document.getElementById('overview-phase-strip');
  stripEl.innerHTML = PHASES.map((p, i) => {
    const st = phaseStates[i];
    const pct = phasePcts[p];
    const checkSvg = `<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 12.75l6 6 9-13.5"/></svg>`;
    return `
      <div class="overview-phase-tile overview-phase-tile--${st}" onclick="switchView('${p}')">
        <div class="overview-phase-name overview-phase-name--${st}">
          ${st === 'done' ? checkSvg : ''}
          ${PHASE_LABELS[p]}
        </div>
        <div class="overview-phase-pct overview-phase-pct--${st}">${pct}%</div>
        <div class="overview-phase-bar">
          <div class="overview-phase-bar-fill overview-phase-bar-fill--${st}" style="width:${pct}%"></div>
        </div>
      </div>`;
  }).join('');

  // ── Attention card ────────────────────────────────────────────────────────
  const attentionEl = document.getElementById('overview-attention');
  const isRunning = processing.status === 'running';

  // Tool-not-installed is a system-level blocker — show before phase cards
  const _ovTool = state.tool || 'gemini';
  const _ovToolInfo = detectedTools ? detectedTools[_ovTool] : null;
  const _ovToolMissing = detectedTools && _ovToolInfo && !_ovToolInfo.installed;
  if (_ovToolMissing && !isRunning && phase !== 'input') {
    const _cmd = _ovToolInfo.install_cmd || '';
    attentionEl.innerHTML = '<div class="overview-attention-card overview-attention-card--error">'
      + '<div class="overview-attention-icon overview-attention-icon--error">' + icon('alert', 15) + '</div>'
      + '<div class="overview-attention-body">'
      + '<div class="overview-attention-title">' + escapeHtml(_ovToolInfo.label) + ' is not installed</div>'
      + '<div class="overview-attention-desc">The configured AI tool is not available on this machine. Generation will fail until it is installed.</div>'
      + (_cmd
        ? '<div class="install-banner-cmd-row" style="margin:8px 0 4px">'
          + '<code class="install-banner-cmd">' + escapeHtml(_cmd) + '</code>'
          + '<button class="btn btn-ghost btn-xs install-banner-copy" onclick="copyToClipboard(\'' + _cmd.replace(/\\/g,'\\\\').replace(/'/g,"\\'") + '\',this)">' + icon('copy', 11) + ' Copy</button>'
          + '</div>'
        : '')
      + '<div class="overview-attention-actions">'
      + '<button class="btn btn-secondary btn-sm" onclick="switchView(\'settings\')">' + icon('settings', 12) + ' Configure Tool</button>'
      + (_ovToolInfo.install_url ? '<a href="' + escapeHtml(_ovToolInfo.install_url) + '" target="_blank" class="btn btn-ghost btn-sm">' + icon('link', 12) + ' Install docs</a>' : '')
      + '</div>'
      + '</div>'
      + '</div>';
    return;
  }

  if (isRunning) {
    const stageLabel = (STAGES.find(s => s.key === processing.stage) || {}).label || processing.stage || 'pipeline';
    attentionEl.innerHTML = `
      <div class="overview-attention-card overview-attention-card--info">
        <div class="overview-attention-icon overview-attention-icon--info">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="animation:spin 1.2s linear infinite"><path d="M21 12a9 9 0 11-6.219-8.56"/></svg>
        </div>
        <div class="overview-attention-body">
          <div class="overview-attention-title">Generating ${escapeHtml(stageLabel)}</div>
          <div class="overview-attention-desc">AI pipeline is running. ${processing.file_index && processing.file_total ? `File ${processing.file_index} of ${processing.file_total}.` : 'This may take a minute.'}</div>
        </div>
      </div>`;
  } else if (phase === 'input') {
    attentionEl.innerHTML = `
      <div class="overview-attention-card overview-attention-card--warn">
        <div class="overview-attention-icon overview-attention-icon--warn">${icon('warning', 15)}</div>
        <div class="overview-attention-body">
          <div class="overview-attention-title">No input documents yet</div>
          <div class="overview-attention-desc">Add at least one product brief, requirements doc, or idea sketch to start the AI pipeline. The quality of your inputs directly determines the quality of everything generated downstream.</div>
          <div class="overview-attention-actions">
            <button class="btn btn-primary btn-sm" onclick="switchView('input');openNewFileDialog()">${icon('sparkles',12)} Create Input File</button>
          </div>
        </div>
      </div>`;
  } else if (phase === 'generate') {
    const notGenerated = STAGES.filter(s => ((summary[s.dir] || {}).generated || 0) === 0);
    const items = notGenerated.slice(0, 5).map(s => `<div class="overview-attention-item"><span class="overview-attention-dot"></span>${s.label}</div>`).join('');
    attentionEl.innerHTML = `
      <div class="overview-attention-card overview-attention-card--warn">
        <div class="overview-attention-icon overview-attention-icon--warn">${icon('sparkles', 15)}</div>
        <div class="overview-attention-body">
          <div class="overview-attention-title">${notGenerated.length} stage${notGenerated.length !== 1 ? 's' : ''} not yet generated</div>
          <div class="overview-attention-desc">Run the AI pipeline to generate documentation for all stages. Each stage builds on the previous — run them in order or use Generate All.</div>
          ${items ? `<div class="overview-attention-items">${items}${notGenerated.length > 5 ? `<div class="overview-attention-item"><span class="overview-attention-dot"></span>…and ${notGenerated.length - 5} more</div>` : ''}</div>` : ''}
          <div class="overview-attention-actions">
            <button class="btn btn-primary btn-sm" onclick="switchView('generate');generate('all')">${icon('sparkles',12)} Generate All Stages</button>
            <button class="btn btn-ghost btn-sm" onclick="switchView('generate')">${icon('eye',12)} View Pipeline</button>
          </div>
        </div>
      </div>`;
  } else if (phase === 'review') {
    const needsReview = STAGES.filter(s => {
      const st = summary[s.dir] || {};
      return st.generated > 0 && st.reviewed < st.generated;
    });
    const remaining = needsReview.reduce((n, s) => n + ((summary[s.dir] || {}).generated || 0) - ((summary[s.dir] || {}).reviewed || 0), 0);
    const items = needsReview.slice(0, 4).map(s => {
      const st = summary[s.dir] || {};
      return `<div class="overview-attention-item"><span class="overview-attention-dot" style="background:var(--amber)"></span>${s.label} — ${(st.generated||0) - (st.reviewed||0)} file${(st.generated||0)-(st.reviewed||0)!==1?'s':''}</div>`;
    }).join('');
    attentionEl.innerHTML = `
      <div class="overview-attention-card overview-attention-card--warn">
        <div class="overview-attention-icon overview-attention-icon--warn">${icon('eye', 15)}</div>
        <div class="overview-attention-body">
          <div class="overview-attention-title">${remaining} document${remaining !== 1 ? 's' : ''} awaiting review</div>
          <div class="overview-attention-desc">Review each generated document and mark it as approved. Gates only pass once all documents in a stage are reviewed. This unlocks Build.</div>
          ${items ? `<div class="overview-attention-items">${items}</div>` : ''}
          <div class="overview-attention-actions">
            <button class="btn btn-primary btn-sm" onclick="switchView('review')">${icon('eye',12)} Open Review</button>
          </div>
        </div>
      </div>`;
  } else if (phase === 'build') {
    const hasGit = !!(git.repo_url);
    const hasBuildFiles = Object.values(buildStepsState).some(s => s.status === 'complete');
    if (!hasGit) {
      attentionEl.innerHTML = `
        <div class="overview-attention-card overview-attention-card--warn">
          <div class="overview-attention-icon overview-attention-icon--warn">${icon('gitBranch', 15)}</div>
          <div class="overview-attention-body">
            <div class="overview-attention-title">Git repository not configured</div>
            <div class="overview-attention-desc">Connect a GitHub repository in Settings to enable the build and PR workflow.</div>
            <div class="overview-attention-actions">
              <button class="btn btn-primary btn-sm" onclick="switchView('settings')">${icon('cog',12)} Open Settings</button>
            </div>
          </div>
        </div>`;
    } else if (!hasBuildFiles) {
      attentionEl.innerHTML = `
        <div class="overview-attention-card overview-attention-card--info">
          <div class="overview-attention-icon overview-attention-icon--info">${icon('codeSquare', 15)}</div>
          <div class="overview-attention-body">
            <div class="overview-attention-title">Build system not yet generated</div>
            <div class="overview-attention-desc">Generate your build system files — backend, frontend, tests, and infra — from your reviewed specification documents.</div>
            <div class="overview-attention-actions">
              <button class="btn btn-primary btn-sm" onclick="switchView('build')">${icon('bolt',12)} Go to Build</button>
            </div>
          </div>
        </div>`;
    } else {
      attentionEl.innerHTML = `
        <div class="overview-attention-card overview-attention-card--success">
          <div class="overview-attention-icon overview-attention-icon--success">${icon('check', 15)}</div>
          <div class="overview-attention-body">
            <div class="overview-attention-title">Build complete — ready to push</div>
            <div class="overview-attention-desc">Build files generated. Review and push to GitHub when ready.</div>
            <div class="overview-attention-actions">
              <button class="btn btn-primary btn-sm" onclick="switchView('build')">${icon('gitBranch',12)} Review &amp; Push</button>
            </div>
          </div>
        </div>`;
    }
  } else {
    const stagingLive = !!((state.environments || {}).staging || {}).url;
    attentionEl.innerHTML = `
      <div class="overview-attention-card overview-attention-card--success">
        <div class="overview-attention-icon overview-attention-icon--success">${icon('cloudUp', 15)}</div>
        <div class="overview-attention-body">
          <div class="overview-attention-title">${stagingLive ? 'Staging is live' : 'Ready to deploy'}</div>
          <div class="overview-attention-desc">${stagingLive ? 'Your staging environment is live. Promote to production when validated.' : 'Configure your deployment platform and push the first release.'}</div>
          <div class="overview-attention-actions">
            <button class="btn btn-primary btn-sm" onclick="switchView('deploy')">${icon('cloudUp',12)} Open Deploy</button>
          </div>
        </div>
      </div>`;
  }

  // ── Stage matrix ──────────────────────────────────────────────────────────
  const matrixEl = document.getElementById('overview-stage-matrix');
  const runningStage = isRunning ? processing.stage : null;
  matrixEl.innerHTML = `
    <div class="overview-matrix-header">
      <span>Documentation Pipeline</span>
      <span style="font-weight:400;color:var(--text-3)">${totalGenerated}/${totalDocs} docs</span>
    </div>
    ${STAGES.map(s => {
      const st = summary[s.dir] || { generated: 0, reviewed: 0, total: 0 };
      const isThisRunning = runningStage === s.key;
      const isEmpty = st.generated === 0 && !isThisRunning;
      const allReviewed = st.generated > 0 && st.reviewed === st.generated && st.total > 0;
      const needsReview = st.generated > 0 && st.reviewed < st.generated;

      let iconCls, iconContent, nameCls, dotCls;
      if (isThisRunning) {
        iconCls = 'overview-stage-icon--running';
        iconContent = `<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="animation:spin 1.2s linear infinite"><path d="M21 12a9 9 0 11-6.219-8.56"/></svg>`;
        nameCls = ''; dotCls = 'overview-stage-status-dot--partial';
      } else if (allReviewed) {
        iconCls = 'overview-stage-icon--done';
        iconContent = `<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 12.75l6 6 9-13.5"/></svg>`;
        nameCls = ''; dotCls = 'overview-stage-status-dot--done';
      } else if (needsReview) {
        iconCls = 'overview-stage-icon--partial';
        iconContent = `<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"/><path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>`;
        nameCls = ''; dotCls = 'overview-stage-status-dot--needs-review';
      } else {
        iconCls = 'overview-stage-icon--empty';
        iconContent = `<span style="font-size:9px;font-weight:700;opacity:.4">${s.dir.split('-')[0]}</span>`;
        nameCls = 'overview-stage-name--empty'; dotCls = 'overview-stage-status-dot--empty';
      }

      const metaText = isEmpty ? s.desc
        : isThisRunning ? `${processing.file_index || 0}/${processing.file_total || st.total}`
        : allReviewed ? 'reviewed'
        : `${st.reviewed}/${st.generated} reviewed`;

      const progressPct = st.total > 0 ? Math.round((st.reviewed / st.total) * 100) : (isThisRunning ? 50 : 0);
      const progressCls = isThisRunning ? 'running' : allReviewed ? 'done' : needsReview ? 'partial' : 'empty';
      return `
        <div class="overview-stage-row" onclick="switchView('${needsReview || allReviewed ? 'review' : 'generate'}')">
          <div class="overview-stage-icon ${iconCls}">${iconContent}</div>
          <span class="overview-stage-name ${nameCls}">${s.label}</span>
          <div class="overview-stage-progress">
            <div class="overview-stage-progress-fill overview-stage-progress-fill--${progressCls}" style="width:${progressPct}%"></div>
          </div>
          <span class="overview-stage-status-dot ${dotCls}"></span>
        </div>`;
    }).join('')}`;

  // ── Sidebar stats ─────────────────────────────────────────────────────────
  const openIssues = issues.filter(i => i.status === 'open').length;
  const hasBuildFiles = Object.values(buildStepsState).some(s => s.status === 'complete');
  const statsEl = document.getElementById('overview-stats-col');
  const statsData = [
    { num: rawInputs.length, label: 'Input Files',    sub: rawInputs.length === 0 ? 'None yet'        : `${rawInputs.length} ready`,                                          color: rawInputs.length > 0  ? 'var(--text)'    : 'var(--text-3)' },
    { num: totalGenerated,   label: 'Generated',      sub: totalDocs > 0 ? `${totalDocs - totalGenerated} left`         : 'Run pipeline',                                      color: totalGenerated > 0    ? 'var(--primary)' : 'var(--text-3)' },
    { num: totalReviewed,    label: 'Reviewed',       sub: totalGenerated > 0 ? `${Math.round((totalReviewed/totalGenerated)*100)}% done`  : '—',                              color: totalReviewed > 0     ? 'var(--green)'   : 'var(--text-3)' },
    { num: openIssues,       label: 'Open Issues',    sub: openIssues > 0 ? 'Needs action'    : 'All clear',                                                                   color: openIssues > 0        ? 'var(--amber)'   : 'var(--text-3)' },
  ];
  statsEl.innerHTML = `<div class="overview-stat-grid">${statsData.map(s => `
    <div class="overview-stat-tile">
      <div class="overview-stat-num" style="color:${s.color}">${s.num}</div>
      <div class="overview-stat-label">${s.label}</div>
      <div class="overview-stat-sub">${s.sub}</div>
    </div>`).join('')}</div>`;

  // ── Gates sidebar ─────────────────────────────────────────────────────────
  const GATE_LABELS = {
    'context-gate': 'Context', 'prd-gate': 'PRD', 'design-gate': 'Design',
    'architecture-gate': 'Architecture', 'engineering-gate': 'Engineering',
    'qa-gate': 'Quality', 'release-gate': 'Release', 'marketing-gate': 'Marketing',
  };
  const gateEntries = Object.entries(GATE_LABELS);
  const passedCount = gateEntries.filter(([k]) => gates[k] === 'PASSED').length;
  const gatesEl = document.getElementById('overview-gates-col');
  const gateBarPct = gateEntries.length > 0 ? Math.round((passedCount / gateEntries.length) * 100) : 0;
  gatesEl.innerHTML = `
    <div class="overview-gates-card">
      <div class="overview-gates-header">
        <div class="overview-gates-title">
          <span>Gates</span>
          <span style="font-weight:400;color:var(--text-3)">${passedCount}/${gateEntries.length}</span>
        </div>
        <div class="overview-gates-bar">
          <div class="overview-gates-bar-fill" style="width:${gateBarPct}%"></div>
        </div>
      </div>
      ${gateEntries.map(([key, label]) => {
        const passed = gates[key] === 'PASSED';
        return `<div class="overview-gate-row">
          <span class="overview-gate-name">${label}</span>
          <span class="overview-gate-dot overview-gate-dot--${passed ? 'pass' : 'fail'}"></span>
        </div>`;
      }).join('')}
    </div>`;
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

function _initInputEditorEvents() {
  const ta = document.getElementById('input-editor');
  if (!ta || ta._forgeEventsWired) return;
  ta._forgeEventsWired = true;
  ta.addEventListener('input', () => {
    if (!inputFileModified) _setInputUnsaved(true);
    _updateEditorStats();
  });
  ta.addEventListener('keydown', e => {
    if ((e.metaKey || e.ctrlKey) && e.key === 's') {
      e.preventDefault();
      saveCurrentFile();
    }
  });
}

function _setInputUnsaved(dirty) {
  inputFileModified = dirty;
  const dot = document.getElementById('editor-unsaved-dot');
  const lbl = document.getElementById('editor-unsaved-label');
  if (dot) dot.style.display = dirty ? '' : 'none';
  if (lbl) lbl.style.display = dirty ? '' : 'none';
}

function _updateEditorStats() {
  const el = document.getElementById('editor-stats');
  if (!el) return;
  const text = document.getElementById('input-editor')?.value || '';
  const words = text.trim() ? text.trim().split(/\s+/).length : 0;
  const lines = text.split('\n').length;
  el.textContent = `${words} words · ${lines} lines`;
}

function renderInput() {
  _initInputEditorEvents();
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
  // Auto-open first file if none is currently selected
  if (count > 0 && !currentInputFile) {
    openInputFile(rawInputs[0].name);
  }
}

function escHtmlJs(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}

async function openInputFile(name) {
  currentInputFile = name;
  document.getElementById('input-empty-state').style.display = 'none';
  const container = document.getElementById('input-editor-container');
  container.style.display = 'flex';
  const parts = name.split('/');
  document.getElementById('editing-filename').textContent = parts[parts.length - 1];
  const pathEl = document.getElementById('editor-path');
  if (pathEl) pathEl.textContent = parts.length > 1 ? name : '';
  _setInputUnsaved(false);

  renderInput(); // re-render to update active highlight

  try {
    const res = await apiFetch(`/api/raw-input?name=${encodeURIComponent(name)}`);
    const text = await res.text();
    document.getElementById('input-editor').value = text;
    _updateEditorStats();
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
    _setInputUnsaved(false);
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

  // Token meter — total tokens spent generating docs (recorded per stage)
  const _gm = document.getElementById('generate-token-meter');
  if (_gm) {
    const gt = state.generate_tokens || {};
    const tin = gt.total_in || 0, tout = gt.total_out || 0;
    if (tin + tout > 0) {
      _gm.style.cssText = 'margin:10px 0 0;display:flex;align-items:center;gap:10px;font-size:11px;color:var(--text-3);';
      _gm.innerHTML = `<span style="font-weight:600;color:var(--text-2);">Tokens generated:</span>`
        + `<span title="Estimated input tokens">↑ ~${_fmtTokens(tin)} in</span>`
        + `<span title="Estimated output tokens">↓ ~${_fmtTokens(tout)} out</span>`
        + `<span style="color:var(--text-2);font-weight:600;">≈ ${_fmtTokens(tin+tout)} total</span>`
        + `<span style="margin-left:auto;font-size:10px;opacity:0.7;">unchanged stages are cached (0 tokens on re-run)</span>`;
    } else { _gm.innerHTML = ''; }
  }

  // Clear optimistic spinner once server confirms real running state (or after 15 s timeout)
  if (optimisticRunning) {
    if (serverRunning || Date.now() - optimisticRunning.startTime > 15000) {
      optimisticRunning = null;
    }
  }

  const isRunning = serverRunning || !!optimisticRunning;
  const summary = state.stageReviewSummary || {};
  const hasInputs = (state.rawInputs || []).length > 0;

  // ── Tool gate — blocks generation when configured CLI is not installed ─────
  const toolGateEl = document.getElementById('generate-tool-gate');
  const currentTool = state.tool || 'gemini';
  const toolInfo = detectedTools ? detectedTools[currentTool] : null;
  const toolMissing = detectedTools && toolInfo && !toolInfo.installed;

  if (toolGateEl) {
    if (toolMissing) {
      const cmd = toolInfo.install_cmd || '';
      const url = toolInfo.install_url || '';
      toolGateEl.style.display = '';
      toolGateEl.innerHTML = '<div class="tool-gate-card">'
        + '<div class="tool-gate-icon">'
        + '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>'
        + '</div>'
        + '<div class="tool-gate-body">'
        + '<div class="tool-gate-title">' + escapeHtml(toolInfo.label) + ' is not installed</div>'
        + '<div class="tool-gate-desc">Generation requires ' + escapeHtml(toolInfo.label) + ' to be installed on this machine. Install it, then click Refresh and generation will unlock.</div>'
        + (cmd
          ? '<div class="tool-gate-cmd-row"><code class="tool-gate-cmd">' + escapeHtml(cmd) + '</code>'
            + '<button class="btn btn-ghost btn-xs" onclick="copyToClipboard(\'' + cmd.replace(/\\/g,'\\\\').replace(/'/g,"\\'") + '\', this)">' + icon('copy', 11) + ' Copy</button>'
            + '</div>'
          : '')
        + '<div class="tool-gate-actions">'
        + '<button class="btn btn-primary btn-sm" onclick="refreshToolStatus()">'
        + '<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 2v6h-6"/><path d="M3 12a9 9 0 0115-6.7L21 8"/><path d="M3 22v-6h6"/><path d="M21 12a9 9 0 01-15 6.7L3 16"/></svg>'
        + ' Refresh Detection</button>'
        + '<button class="btn btn-ghost btn-sm" onclick="switchView(\'settings\')">'
        + icon('settings', 12) + ' Change Tool</button>'
        + (url ? '<a href="' + escapeHtml(url) + '" target="_blank" class="btn btn-ghost btn-sm">' + icon('link', 12) + ' Install docs</a>' : '')
        + '</div>'
        + '</div>'
        + '</div>';
      // Disable generation while tool is missing
      const genAllBtn = document.getElementById('btn-generate-all');
      if (genAllBtn) genAllBtn.disabled = true;
    } else {
      toolGateEl.style.display = 'none';
    }
  }

  // ── Input gate ────────────────────────────────────────────────────────────
  const gateEl = document.getElementById('generate-gate');
  const generateTopEl = document.querySelector('.generate-top');
  const stageGridEl = document.getElementById('stage-grid');

  if (!hasInputs) {
    gateEl.style.display = '';
    gateEl.innerHTML = `
      <div class="generate-gate-card">
        <div class="generate-gate-icon">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
          </svg>
        </div>
        <div class="generate-gate-body">
          <div class="generate-gate-title">Input documents required</div>
          <div class="generate-gate-desc">Add at least one input document — a product brief, requirements doc, or any raw specification — before running the AI pipeline. Generation needs source material to work from.</div>
          <button class="btn btn-primary btn-sm" onclick="switchView('input')" style="margin-top:10px;width:fit-content;">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v14M5 12h14"/></svg>
            Add input document
          </button>
        </div>
      </div>`;
    generateTopEl.style.display = 'none';
    document.getElementById('btn-generate-all').disabled = true;
    document.getElementById('btn-generate-all').style.display = isRunning ? 'none' : '';
    document.getElementById('btn-stop-generate').style.display = isRunning ? '' : 'none';
    // Render locked stage cards to show the user what they're about to unlock
    stageGridEl.style.opacity = '0.35';
    stageGridEl.style.pointerEvents = 'none';
  } else {
    gateEl.style.display = 'none';
    generateTopEl.style.display = '';
    stageGridEl.style.opacity = '';
    stageGridEl.style.pointerEvents = '';
    document.getElementById('btn-generate-all').disabled = isRunning;
    document.getElementById('btn-generate-all').style.display = isRunning ? 'none' : '';
    document.getElementById('btn-stop-generate').style.display = isRunning ? '' : 'none';
  }

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

  // ── Pipeline summary bar ─────────────────────────────────────────────────
  const totalStages    = STAGES.length;
  const totalGenerated = STAGES.filter(s => (summary[s.dir] || {}).generated > 0).length;
  const totalReviewed  = STAGES.filter(s => {
    const st = summary[s.dir] || {};
    return st.total > 0 && st.reviewed === st.total;
  }).length;
  const genPct = Math.round((totalGenerated / totalStages) * 100);
  const revPct = Math.round((totalReviewed  / totalStages) * 100);

  const summaryEl = document.getElementById('pipeline-summary');
  if (summaryEl && hasInputs) {
    summaryEl.style.display = '';
    summaryEl.innerHTML = `
      <div class="pipeline-summary-row">
        <span class="pipeline-summary-label">Generated</span>
        <div class="pipeline-summary-bar"><div class="pipeline-summary-fill pipeline-summary-fill--generated" style="width:${genPct}%"></div></div>
        <span class="pipeline-summary-count">${totalGenerated} / ${totalStages}</span>
      </div>
      <div class="pipeline-summary-row">
        <span class="pipeline-summary-label">Reviewed</span>
        <div class="pipeline-summary-bar"><div class="pipeline-summary-fill pipeline-summary-fill--reviewed" style="width:${revPct}%"></div></div>
        <span class="pipeline-summary-count">${totalReviewed} / ${totalStages}</span>
      </div>`;
  } else if (summaryEl) {
    summaryEl.style.display = 'none';
  }

  // ── Dynamic subtitle ──────────────────────────────────────────────────────
  const subtitleEl = document.getElementById('generate-subtitle');
  if (subtitleEl) {
    if (isRunning) {
      const stageObj = STAGES.find(s => s.key === processing.stage);
      const lbl = stageObj ? stageObj.label : 'pipeline';
      subtitleEl.textContent = `Generating ${lbl}…`;
    } else if (totalGenerated > 0) {
      const parts = [`${totalStages} stages`, `${totalGenerated} generated`];
      if (totalReviewed > 0) parts.push(`${totalReviewed} reviewed`);
      subtitleEl.textContent = parts.join(' · ');
    } else {
      subtitleEl.textContent = `${totalStages} stages · AI-powered document generation`;
    }
  }

  // ── Status bar ────────────────────────────────────────────────────────────
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
    document.getElementById('generate-status-bar').innerHTML = totalGenerated > 0
      ? `<span style="color:var(--primary);">${icon('check',12)} ${totalGenerated} stage${totalGenerated!==1?'s':''} generated</span><span style="color:var(--text-3);margin-left:8px;">${totalReviewed > 0 ? `${totalReviewed} reviewed · ` : ''}Ready to proceed to Review.</span>`
      : `Run all stages at once or generate individual stages below.`;
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

    const cardClass = isThisRunning ? 'running' : (allReviewed ? 'reviewed' : (needsReview ? 'needs-review' : (hasError ? 'error' : '')));
    const progressColor = allReviewed ? 'green' : (isThisRunning ? 'amber' : '');

    const fileIdx   = isThisRunning ? (processing.file_index || 1) : 0;
    const fileTotal = isThisRunning ? (processing.file_total  || total || 1) : 0;
    const fileName  = isThisRunning ? (processing.file || '') : '';
    const fileBase  = fileName.split('/').pop().replace(/\.md$/, '');
    const filePct   = isThisRunning && fileTotal > 0 ? Math.round(((fileIdx - 1) / fileTotal) * 100) : pct;

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

    const statsLabel = isThisRunning
      ? `${fileIdx} / ${fileTotal} files`
      : needsReview
        ? `${reviewed} / ${total} reviewed`
        : generated > 0
          ? `${generated} / ${total} files`
          : `${total} files`;

    const subtitle = isThisRunning && fileBase
      ? fileBase
      : hasError
        ? (processing.last_error?.file || '').split('/').pop().replace(/\.md$/, '') || 'failed'
        : needsReview
          ? 'Needs review'
          : s.desc;

    const stageNum = String(idx + 1).padStart(2, '0');
    const btnLabel = isThisRunning ? 'Generating…' : (generated > 0 ? 'Regenerate' : 'Generate');

    grid.insertAdjacentHTML('beforeend', `
      <div class="stage-card ${cardClass}" style="${isQueued ? 'opacity:0.4;pointer-events:none' : ''}">
        <div class="stage-card-header">
          <div style="min-width:0;">
            <div class="stage-number">${stageNum}</div>
            <div class="stage-name">${s.label}</div>
            <div class="stage-subtitle" style="${needsReview ? 'color:var(--amber);' : ''}">${subtitle}</div>
          </div>
          <div style="display:flex;flex-direction:column;align-items:flex-end;gap:6px;flex-shrink:0;">
            ${statusBadge}
            <div class="stage-stats">${statsLabel}</div>
          </div>
        </div>
        <div class="progress-bar">
          <div class="progress-fill ${progressColor}" style="width:${Math.max(filePct, pct)}%;${isThisRunning ? 'animation:progress-pulse 1.5s ease-in-out infinite;' : ''}"></div>
        </div>
        <button class="btn btn-secondary btn-sm" ${(isRunning || !hasInputs) ? 'disabled' : ''} onclick="generate('${s.key}')">
          ${icon('sparkles', 12)}
          ${btnLabel}
        </button>
      </div>
    `);
  });
}

async function generate(stage) {
  // Guard: configured CLI must be installed
  const _gTool = state.tool || 'gemini';
  if (detectedTools) {
    const _gInfo = detectedTools[_gTool];
    if (_gInfo && !_gInfo.installed) {
      showToast(_gInfo.label + ' is not installed — go to Settings to install it or choose a different tool', 'error');
      switchView('generate');
      return;
    }
  }

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

async function stopGeneration() {
  const btn = document.getElementById('btn-stop-generate');
  if (btn) { btn.disabled = true; btn.textContent = 'Stopping…'; }
  try {
    await apiFetch('/api/generate/cancel', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' });
    showToast('Generation stopped', 'info');
  } catch (e) {
    showToast('Could not stop generation', 'error');
  } finally {
    if (btn) { btn.disabled = false; }
    loadState();
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

  let totalVisible = 0, totalReviewedVisible = 0;

  // Compute overall progress for the tree header progress bar
  Object.entries(tree).forEach(([dir, files]) => {
    if (activeView.dirs && !activeView.dirs.some(d => dir.startsWith(d))) return;
    files.forEach(f => {
      if (f.size === 0) return;
      totalVisible++;
      if (f.status === 'reviewed') totalReviewedVisible++;
    });
  });
  const progressEl = document.getElementById('review-tree-progress');
  if (progressEl) {
    if (totalVisible > 0) {
      const pct = Math.round((totalReviewedVisible / totalVisible) * 100);
      progressEl.innerHTML = `
        <div class="review-tree-progress-bar"><div class="review-tree-progress-fill" style="width:${pct}%"></div></div>
        <span class="review-tree-progress-label">${totalReviewedVisible} / ${totalVisible}</span>`;
      progressEl.style.display = 'flex';
    } else {
      progressEl.style.display = 'none';
    }
  }

  totalVisible = 0;

  Object.entries(tree).forEach(([dir, files]) => {
    if (activeView.dirs && !activeView.dirs.some(d => dir.startsWith(d))) return;

    const filtered = files.filter(f => {
      if (searchVal && !f.name.toLowerCase().includes(searchVal) && !_fmtFileName(f.name).toLowerCase().includes(searchVal)) return false;
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
    const stageLabel = STAGE_DIR_TO_LABEL[dir] || dir;
    const rev = summary.reviewed || 0;
    const gen = summary.generated || 0;
    const grpPct = gen > 0 ? Math.round((rev / gen) * 100) : 0;
    const grpDone = rev === gen && gen > 0;

    treeEl.insertAdjacentHTML('beforeend', `
      <div class="stage-group">
        <div class="stage-group-header">
          <span>${stageLabel}</span>
          <div class="stage-group-progress">
            <div class="stage-group-progress-bar"><div class="stage-group-progress-fill${grpDone ? ' done' : ''}" style="width:${grpPct}%"></div></div>
            <span class="stage-group-count">${rev}/${gen}</span>
          </div>
        </div>
        ${filtered.map(f => {
          const path = `${dir}/${f.name}`;
          const isActive = currentReviewFile === path;
          const isBeingFixed = fixingFile === path;
          const dotClass = isBeingFixed ? 'fixing' : f.status;
          return `
            <div class="tree-file-item ${isActive ? 'active' : ''}" onclick="openReviewFile('${path}','${f.status}',${f.size},${f.modifiedAt})">
              <span class="tree-file-dot ${dotClass}"></span>
              ${_fmtFileName(f.name)}
            </div>
          `;
        }).join('')}
      </div>
    `);
  });

  if (totalVisible === 0) {
    // Distinguish: tree has files but filters hide them vs. nothing generated at all
    const totalInTree = Object.values(tree).reduce((n, files) => n + files.length, 0);
    if (totalInTree === 0) {
      treeEl.innerHTML = `
        <div class="review-tree-empty">
          <div class="review-tree-empty-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z"/>
            </svg>
          </div>
          <div class="review-tree-empty-title">Nothing generated yet</div>
          <div class="review-tree-empty-desc">Run the AI pipeline first. Documents will appear here for review once generated.</div>
          <button class="btn btn-primary btn-sm" onclick="switchView('generate')" style="margin-top:10px;">Go to Generate</button>
        </div>`;
    } else {
      treeEl.innerHTML = `
        <div class="review-tree-empty">
          <div class="review-tree-empty-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
            </svg>
          </div>
          <div class="review-tree-empty-title">No files match</div>
          <div class="review-tree-empty-desc">Try a different role view or status filter.</div>
          <button class="btn btn-ghost btn-sm" onclick="resetReviewFilters()" style="margin-top:8px;">Clear filters</button>
        </div>`;
    }
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

function resetReviewFilters() {
  reviewViewFilter = 'all';
  reviewStatusFilter = 'all';
  localStorage.setItem('review-view', 'all');
  localStorage.setItem('review-status', 'all');
  document.getElementById('review-search').value = '';
  renderReview();
}

function filterReviewTree(val) {
  renderReview();
}

async function openReviewFile(path, status, size, modifiedAt) {
  currentReviewFile = path;

  // Clear any active version view when switching files
  viewingVersion = null;
  document.getElementById('viewer-version-banner').style.display = 'none';
  _setReviewToggle(status, false);

  const _pathParts = path.split('/');
  const _stageDir  = _pathParts[0] || '';
  const _fileName  = _pathParts.slice(1).join('/');
  const _stageLabel = STAGE_DIR_TO_LABEL[_stageDir] || _stageDir;
  const _statusDot = `<span class="viewer-status-dot ${status}" title="${status.replace('_',' ')}"></span>`;
  document.getElementById('viewer-filename').innerHTML = `
    <div class="viewer-breadcrumb">
      ${_statusDot}
      <span class="viewer-breadcrumb-stage">${_stageLabel}</span>
      <span class="viewer-breadcrumb-sep">›</span>
      <span class="viewer-breadcrumb-file">${_fmtFileName(_fileName)}</span>
    </div>`;
  document.getElementById('btn-review-toggle').style.display = '';
  document.getElementById('viewer-mode-toggle').style.display = '';

  document.getElementById('meta-path').textContent = STAGE_DIR_TO_LABEL[path.split('/')[0]] || path.split('/')[0];
  document.getElementById('meta-status').innerHTML = `<span class="badge badge-${status.replace('_','-')}">${status.replace('_',' ')}</span>`;
  document.getElementById('meta-size').textContent = size > 0 ? `${(size/1024).toFixed(1)} KB` : '0 bytes';
  document.getElementById('meta-modified').textContent = modifiedAt ? new Date(modifiedAt * 1000).toLocaleString() : '—';

  try {
    const res = await apiFetch(`/api/file?path=${encodeURIComponent(path)}`);
    if (res.ok) {
      const text = await res.text();
      if (!text || !text.trim()) {
        document.getElementById('viewer-content').innerHTML = `
          <div class="viewer-empty-state">
            <div class="viewer-empty-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>
              </svg>
            </div>
            <div class="viewer-empty-title">Empty document</div>
            <div class="viewer-empty-desc">This file has no content yet. Run this stage in Generate to produce output.</div>
            <button class="btn btn-primary btn-sm" onclick="switchView('generate')" style="margin-top:12px;">Go to Generate</button>
          </div>`;
        document.getElementById('viewer-raw-pre').textContent = '';
      } else {
        setViewerContent(renderMarkdown(text));
        document.getElementById('viewer-raw-pre').textContent = text;
      }
    } else {
      document.getElementById('viewer-content').innerHTML = `
        <div class="viewer-empty-state viewer-empty-state--warn">
          <div class="viewer-empty-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
          </div>
          <div class="viewer-empty-title">File not found</div>
          <div class="viewer-empty-desc">This file may have been moved or deleted. Try regenerating this stage.</div>
        </div>`;
      document.getElementById('viewer-raw-pre').textContent = '';
    }
  } catch (e) {
    document.getElementById('viewer-content').innerHTML = `
      <div class="viewer-empty-state viewer-empty-state--error">
        <div class="viewer-empty-icon">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
        </div>
        <div class="viewer-empty-title">Failed to load</div>
        <div class="viewer-empty-desc">Could not read this file. Check that the server is running and try again.</div>
      </div>`;
    document.getElementById('viewer-raw-pre').textContent = '';
  }
  // Always open in rendered mode for a fresh file
  setViewerMode('rendered');

  renderReview();
  fetchVersions(path);
}

function _setReviewToggle(status, disabled) {
  const btn = document.getElementById('btn-review-toggle');
  const lbl = document.getElementById('btn-review-toggle-label');
  if (!btn) return;
  const isReviewed = status === 'reviewed';
  btn.className = 'btn btn-sm ' + (isReviewed ? 'btn-review-active' : 'btn-primary');
  if (lbl) lbl.textContent = isReviewed ? 'Reviewed' : 'Mark Reviewed';
  btn.style.opacity = disabled ? '0.3' : '';
  btn.style.pointerEvents = disabled ? 'none' : '';
}

async function toggleReviewStatus() {
  if (!currentReviewFile) return;
  const btn = document.getElementById('btn-review-toggle');
  const isReviewed = btn && btn.classList.contains('btn-review-active');
  const newStatus = isReviewed ? 'needs_review' : 'reviewed';
  try {
    await apiFetch('/api/review', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: currentReviewFile, status: newStatus })
    });
    _setReviewToggle(newStatus, false);
    document.getElementById('meta-status').innerHTML = `<span class="badge badge-${newStatus.replace('_','-')}">${newStatus.replace('_',' ')}</span>`;
    showToast(newStatus === 'reviewed' ? 'Marked as reviewed' : 'Marked for review', 'success');
    loadState();
  } catch (e) {
    showToast('Failed', 'error');
  }
}

async function markFile(status) {
  if (!currentReviewFile) return;
  try {
    await apiFetch('/api/review', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: currentReviewFile, status })
    });
    _setReviewToggle(status, false);
    document.getElementById('meta-status').innerHTML = `<span class="badge badge-${status.replace('_','-')}">${status.replace('_',' ')}</span>`;
    showToast(status === 'reviewed' ? 'Marked as reviewed' : 'Marked for review', 'success');
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

    setViewerContent(renderMarkdown(text));
    document.getElementById('viewer-raw-pre').textContent = text;

    const banner = document.getElementById('viewer-version-banner');
    banner.style.display = 'flex';
    document.getElementById('vb-label').textContent =
      `Viewing version from ${new Date(timestamp).toLocaleString()} — not the current file`;

    // Dim toggle while viewing historic version
    const _btn = document.getElementById('btn-review-toggle');
    if (_btn) { _btn.style.opacity = '0.3'; _btn.style.pointerEvents = 'none'; }

    // Re-render version list to highlight active
    fetchVersions(currentReviewFile);
  } catch(e) {
    showToast('Failed to load version', 'error');
  }
}

function closeVersion() {
  viewingVersion = null;
  document.getElementById('viewer-version-banner').style.display = 'none';
  const _btn = document.getElementById('btn-review-toggle');
  if (_btn) { _btn.style.opacity = ''; _btn.style.pointerEvents = ''; }
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
      setViewerContent(renderMarkdown(raw));
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
  _fixSubmittedAt = Date.now();
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
    _fixSubmittedAt = 0;
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
let buildStepsActivePhaseId = '';  // phase the current buildStepsState was built for
let buildCodePanelStep = null;

async function fetchBuildSteps() {
  try {
    const res = await apiFetch('/api/build-system');
    if (res.ok) {
      const data = await res.json();
      buildStepsState = data.steps || {};
      buildStepsActivePhaseId = data.active_phase_id || '';
      renderBuildSteps();
      // Auto-show progress panel if a step is running and panel is not visible
      if (!_bld.visible) {
        const running = Object.entries(buildStepsState).find(([,v]) => v.status === 'running');
        if (running) showBuildLog(running[0]);
      }
    }
  } catch (e) {}
}

function _fmtTokens(n) {
  if (!n) return '0';
  if (n >= 1000000) return (n/1000000).toFixed(1) + 'M';
  if (n >= 1000) return Math.round(n/1000) + 'k';
  return String(n);
}

function renderBuildSteps() {
  const grid = document.getElementById('build-steps-grid');
  if (!grid) return;
  // Ensure log drawer container exists as a sibling below the grid
  if (!document.getElementById('build-log-drawer-container')) {
    const container = document.createElement('div');
    container.id = 'build-log-drawer-container';
    grid.parentNode.insertBefore(container, grid.nextSibling);
  }
  // Build-total token meter (above the grid) — answers "how much did this cost?"
  let meter = document.getElementById('build-token-meter');
  if (!meter) {
    meter = document.createElement('div');
    meter.id = 'build-token-meter';
    grid.parentNode.insertBefore(meter, grid);
  }
  const _totIn  = Object.values(buildStepsState).reduce((a, v) => a + (v.tokens_in || 0), 0);
  const _totOut = Object.values(buildStepsState).reduce((a, v) => a + (v.tokens_out || 0), 0);
  const _anyCached = Object.values(buildStepsState).some(v => v.cached);
  if (_totIn + _totOut > 0) {
    meter.style.cssText = 'display:flex;align-items:center;gap:10px;margin-bottom:12px;font-size:11px;color:var(--text-3);';
    meter.innerHTML = `
      <span style="font-weight:600;color:var(--text-2);">Tokens this build:</span>
      <span title="Estimated input tokens">↑ ~${_fmtTokens(_totIn)} in</span>
      <span title="Estimated output tokens">↓ ~${_fmtTokens(_totOut)} out</span>
      <span style="color:var(--text-2);font-weight:600;">≈ ${_fmtTokens(_totIn + _totOut)} total</span>
      ${_anyCached ? '<span style="color:var(--green);">· cache hits saved tokens</span>' : ''}
      <span style="margin-left:auto;font-size:10px;color:var(--text-3);opacity:0.7;">estimate (~4 chars/token)</span>`;
  } else {
    meter.innerHTML = '';
    meter.style.marginBottom = '0';
  }
  const isRunning = (state.processing && state.processing.status === 'running');

  // Icon-only SVG buttons (no lucide dependency in dashboard)
  const _iconCode = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>`;

  grid.innerHTML = Object.entries(BUILD_STEPS_META).map(([key, meta]) => {
    const st = buildStepsState[key] || { status: 'idle', files: [] };
    const fileCount = (st.files || []).length;
    const isThisRunning = isRunning && (state.processing.stage === key || state.processing.stage === 'all');
    const canRun = !isRunning;
    const hasProgress = isThisRunning || ['complete', 'error'].includes(st.status);

    // Badge — clickable to open progress panel when applicable
    const badgeClick = hasProgress ? `onclick="showBuildLog('${key}')" style="cursor:pointer;" title="View progress"` : '';
    let badge, subline, actionBtns;

    if (isThisRunning) {
      badge = `<span class="badge" ${badgeClick} style="background:var(--blue-light,#dbeafe);color:var(--blue);gap:5px;cursor:pointer;">
        <span style="display:inline-block;width:7px;height:7px;border:1.5px solid var(--blue);border-top-color:transparent;border-radius:50%;animation:spin 0.7s linear infinite;flex-shrink:0;"></span>Building</span>`;
      subline = `<span style="font-size:11px;color:var(--text-3);">In progress — click badge for details</span>`;
      actionBtns = '';

    } else if (st.status === 'complete') {
      badge = `<span class="badge badge-success" ${badgeClick}>${fileCount} file${fileCount!==1?'s':''}</span>`;
      const _tk = (st.tokens_in || 0) + (st.tokens_out || 0);
      const _tkStr = st.cached
        ? `<span style="color:var(--green);">cached — 0 tokens</span>`
        : (_tk ? `~${_fmtTokens(_tk)} tokens` : 'Generated');
      subline = `<span style="font-size:11px;color:var(--text-3);">${_tkStr}</span>`;
      // Icon-only View Code + text Rebuild
      actionBtns = `
        <button onclick="openBuildCodePanel('${key}')" title="View Code"
          style="display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border:1px solid var(--border);border-radius:6px;background:none;color:var(--text-2);cursor:pointer;">
          ${_iconCode}
        </button>
        <button class="btn btn-secondary btn-sm" onclick="runBuildStep('${key}')" ${canRun?'':'disabled'}>Rebuild</button>`;

    } else if (st.status === 'error') {
      badge = `<span class="badge badge-error" ${badgeClick}>Error</span>`;
      subline = `<span style="font-size:11px;color:var(--red);max-width:130px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${escapeHtml(st.error||'')}">${escapeHtml((st.error||'Failed').substring(0,40))}</span>`;
      actionBtns = `<button class="btn btn-primary btn-sm" onclick="runBuildStep('${key}')" ${canRun?'':'disabled'}>Retry</button>`;

    } else {
      badge = `<span class="badge" style="background:var(--bg-2);color:var(--text-3);">Not started</span>`;
      subline = `<span style="font-size:11px;color:var(--text-3);">${meta.desc}</span>`;
      actionBtns = '';
    }

    const primaryBtn = (st.status !== 'complete' && st.status !== 'error')
      ? `<button class="btn btn-primary btn-sm" onclick="runBuildStep('${key}')" ${canRun?'':'disabled'}>Build</button>`
      : '';

    return `<div class="card" style="padding:14px;display:flex;flex-direction:column;gap:10px;${st.status==='error'?'border-color:var(--red);':st.status==='complete'?'border-color:var(--green);':''}">
      <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;">
        <span style="font-size:12px;font-weight:600;color:var(--text-1);">${meta.label}</span>
        ${badge}
      </div>
      <div style="display:flex;align-items:center;justify-content:space-between;gap:6px;">
        ${subline}
        <div style="display:flex;align-items:center;gap:6px;flex-shrink:0;">
          ${actionBtns}${primaryBtn}
        </div>
      </div>
    </div>`;
  }).join('');
}

// ---- Per-step model tiering (Settings -> AI Runtime) ----------------------
const _BLD_STEP_ORDER = ['backend','frontend','integration','tests','infra'];
const _BLD_STEP_LABELS = {backend:'Backend & API', frontend:'Frontend UI',
  integration:'Integration Layer', tests:'Test Suite', infra:'Infrastructure'};
// Recommended tiering: mechanical steps -> fast model, complex -> default.
const _BLD_FAST_STEPS = ['infra','tests'];
let _stepModelsDraft = {};

// Called by renderToolPicker() when the Settings view renders.
function renderSettingsStepModels() {
  const host = document.getElementById('settings-step-models');
  if (!host) return;
  if (!detectedTools) { fetchToolStatus(false).then(renderSettingsStepModels); return; }
  // Seed the draft from saved state on first render of this Settings visit.
  if (_stepModelsDraft === null || _stepModelsDraft === undefined) _stepModelsDraft = {};
  const gTool  = getValue('settings-tool') || state.tool || 'claude';
  const gModel = getValue('settings-model') || state.model || '';
  const toolOpts = (t) => Object.entries(detectedTools)
    .map(([id,info]) => `<option value="${id}" ${id===t?'selected':''}>${escapeHtml(info.label||id)}</option>`).join('');

  host.innerHTML = _BLD_STEP_ORDER.map(s => {
    const ov = _stepModelsDraft[s] || {};
    const t = ov.tool || gTool;
    const m = ov.model || '';
    const models = (detectedTools[t] || {}).models || [];
    const modelOpts = `<option value="">Default (${escapeHtml(gModel || (detectedTools[t]||{}).default_model || 'global')})</option>` +
      models.map(mo => `<option value="${mo.id}" ${mo.id===m?'selected':''}>${escapeHtml(mo.label||mo.id)}${mo.tier?` · ${mo.tier}`:''}</option>`).join('');
    const custom = !!(ov.tool || ov.model);
    return `<div style="display:flex;align-items:center;gap:6px;padding:6px 0;border-bottom:1px solid var(--border);">
      <span style="flex:0 0 110px;font-size:12px;color:var(--text-1);">${_BLD_STEP_LABELS[s]}</span>
      <select onchange="setStepModel('${s}','tool',this.value)" style="flex:0 0 120px;height:30px;font-size:11px;padding:0 6px;border:1px solid var(--border);border-radius:6px;background:var(--bg);color:var(--text-1);">${toolOpts(t)}</select>
      <select onchange="setStepModel('${s}','model',this.value)" style="flex:1;min-width:0;height:30px;font-size:11px;padding:0 6px;border:1px solid var(--border);border-radius:6px;background:var(--bg);color:var(--text-1);">${modelOpts}</select>
      <span style="flex:0 0 48px;font-size:10px;text-align:right;color:${custom?'var(--accent,#4f46e5)':'var(--text-3)'};">${custom?'custom':'global'}</span>
    </div>`;
  }).join('') + (Object.keys(_stepModelsDraft).length
    ? `<div style="margin-top:8px;"><button class="btn btn-ghost btn-xs" type="button" onclick="clearStepModels()">Reset all to global model</button></div>` : '');
}

function setStepModel(step, field, value) {
  _stepModelsDraft[step] = _stepModelsDraft[step] || {};
  if (value) _stepModelsDraft[step][field] = value;
  else delete _stepModelsDraft[step][field];
  if (field === 'tool') delete _stepModelsDraft[step].model;  // model belongs to a tool
  if (!Object.keys(_stepModelsDraft[step]).length) delete _stepModelsDraft[step];
  renderSettingsStepModels();
}

function applyTieringDefaults() {
  const gTool = getValue('settings-tool') || state.tool || 'claude';
  const fast = (detectedTools[gTool] || {}).fast_model;
  const def  = (detectedTools[gTool] || {}).default_model;
  _stepModelsDraft = {};
  _BLD_STEP_ORDER.forEach(s => {
    const m = _BLD_FAST_STEPS.includes(s) ? fast : def;
    if (m) _stepModelsDraft[s] = { tool: gTool, model: m };
  });
  renderSettingsStepModels();
  showToast('Tiering applied — click Save to persist', 'info');
}

function clearStepModels() { _stepModelsDraft = {}; renderSettingsStepModels(); }

// ---- Per-stage model tiering for the GENERATE pipeline --------------------
const _GEN_STAGE_ORDER = ['context','requirements','design','analysis','architecture',
  'delivery','engineering','qa','operations','release','marketing'];
const _GEN_STAGE_LABELS = {context:'Context', requirements:'Requirements', design:'Design',
  analysis:'Analysis', architecture:'Architecture', delivery:'Delivery', engineering:'Engineering',
  qa:'QA', operations:'Operations', release:'Release', marketing:'Marketing'};
// Conservative tiering: keep the strong model on foundational/high-leverage
// stages; only the lighter, lower-blast-radius stages drop to the fast model.
const _GEN_FAST_STAGES = ['delivery','qa','operations','release','marketing'];
let _genModelsDraft = {};

function renderSettingsGenModels() {
  const host = document.getElementById('settings-gen-models');
  if (!host) return;
  if (!detectedTools) { fetchToolStatus(false).then(renderSettingsGenModels); return; }
  const gTool  = getValue('settings-tool') || state.tool || 'claude';
  const gModel = getValue('settings-model') || state.model || '';
  const toolOpts = (t) => Object.entries(detectedTools)
    .map(([id,info]) => `<option value="${id}" ${id===t?'selected':''}>${escapeHtml(info.label||id)}</option>`).join('');
  host.innerHTML = _GEN_STAGE_ORDER.map(s => {
    const ov = _genModelsDraft[s] || {};
    const t = ov.tool || gTool;
    const m = ov.model || '';
    const models = (detectedTools[t] || {}).models || [];
    const modelOpts = `<option value="">Default (${escapeHtml(gModel || (detectedTools[t]||{}).default_model || 'global')})</option>` +
      models.map(mo => `<option value="${mo.id}" ${mo.id===m?'selected':''}>${escapeHtml(mo.label||mo.id)}${mo.tier?` · ${mo.tier}`:''}</option>`).join('');
    const custom = !!(ov.tool || ov.model);
    return `<div style="display:flex;align-items:center;gap:6px;padding:5px 0;border-bottom:1px solid var(--border);">
      <span style="flex:0 0 96px;font-size:12px;color:var(--text-1);">${_GEN_STAGE_LABELS[s]}</span>
      <select onchange="setGenStageModel('${s}','tool',this.value)" style="flex:0 0 116px;height:28px;font-size:11px;padding:0 5px;border:1px solid var(--border);border-radius:6px;background:var(--bg);color:var(--text-1);">${toolOpts(t)}</select>
      <select onchange="setGenStageModel('${s}','model',this.value)" style="flex:1;min-width:0;height:28px;font-size:11px;padding:0 5px;border:1px solid var(--border);border-radius:6px;background:var(--bg);color:var(--text-1);">${modelOpts}</select>
      <span style="flex:0 0 44px;font-size:10px;text-align:right;color:${custom?'var(--accent,#4f46e5)':'var(--text-3)'};">${custom?'custom':'global'}</span>
    </div>`;
  }).join('') + (Object.keys(_genModelsDraft).length
    ? `<div style="margin-top:8px;"><button class="btn btn-ghost btn-xs" type="button" onclick="clearGenModels()">Reset all to global model</button></div>` : '');
}

function setGenStageModel(stage, field, value) {
  _genModelsDraft[stage] = _genModelsDraft[stage] || {};
  if (value) _genModelsDraft[stage][field] = value;
  else delete _genModelsDraft[stage][field];
  if (field === 'tool') delete _genModelsDraft[stage].model;
  if (!Object.keys(_genModelsDraft[stage]).length) delete _genModelsDraft[stage];
  renderSettingsGenModels();
}

function applyGenTieringDefaults() {
  const gTool = getValue('settings-tool') || state.tool || 'claude';
  const fast = (detectedTools[gTool] || {}).fast_model;
  const def  = (detectedTools[gTool] || {}).default_model;
  _genModelsDraft = {};
  _GEN_STAGE_ORDER.forEach(s => {
    const m = _GEN_FAST_STAGES.includes(s) ? fast : def;
    if (m) _genModelsDraft[s] = { tool: gTool, model: m };
  });
  renderSettingsGenModels();
  showToast('Tiering applied — click Save to persist', 'info');
}

function clearGenModels() { _genModelsDraft = {}; renderSettingsGenModels(); }

// ---- Pre-flight cost preview ----------------------------------------------
async function previewBuildCost() {
  const btn = document.getElementById('btn-build-preview');
  if (btn) { btn.disabled = true; btn.textContent = 'Estimating…'; }
  try {
    const res = await apiFetch('/api/build-preview');
    const d = await res.json();
    _showBuildPreviewModal(d);
  } catch(e) {
    showToast('Preview failed', 'error');
  } finally {
    if (btn) { btn.disabled = false; btn.innerHTML = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg> Preview cost'; }
  }
}

function closeBuildPreview() {
  const el = document.getElementById('build-preview-overlay');
  if (el) el.remove();
}

function _showBuildPreviewModal(d) {
  closeBuildPreview();
  const totalIn = d.projected_input_tokens || 0;
  const totalOut = d.projected_output_tokens || 0;
  const saved = d.cached_input_tokens_saved || 0;
  const willRun = d.will_regenerate || [];
  const cached = d.cache_hits || [];
  const rows = _BLD_STEP_ORDER.map(s => {
    const info = (d.steps || {})[s] || {};
    const hit = info.cache_hit;
    const tk = info.tokens_in_est || 0;
    const status = hit
      ? '<span class="badge badge-success">cached</span>'
      : '<span class="badge" style="background:var(--bg-3);color:var(--text-2);">will run</span>';
    return `<tr style="border-bottom:1px solid var(--border);">
      <td style="padding:8px 6px;font-size:12px;color:var(--text-1);">${_BLD_STEP_LABELS[s]}</td>
      <td style="padding:8px 6px;font-size:11px;color:var(--text-3);font-family:var(--mono);">${escapeHtml(info.model||'—')}</td>
      <td style="padding:8px 6px;font-size:12px;text-align:right;color:var(--text-2);font-variant-numeric:tabular-nums;">${hit?'—':'~'+_fmtTokens(tk)}</td>
      <td style="padding:8px 6px;text-align:right;">${status}</td>
    </tr>`;
  }).join('');

  const overlay = document.createElement('div');
  overlay.id = 'build-preview-overlay';
  overlay.className = 'dialog-overlay';
  overlay.onclick = (e) => { if (e.target === overlay) closeBuildPreview(); };
  overlay.innerHTML = `
    <div class="dialog" style="width:540px;max-width:92vw;">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px;">
        <h3 style="margin:0;">Build cost preview</h3>
        <button class="btn btn-ghost btn-xs" onclick="closeBuildPreview()" aria-label="Close">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
      <div style="font-size:11px;color:var(--text-3);margin-bottom:14px;">Estimated cost and what will regenerate, before you run.</div>
      <table style="width:100%;border-collapse:collapse;margin-bottom:16px;">
        <thead><tr style="border-bottom:1px solid var(--border);">
          <th style="text-align:left;padding:4px 6px;font-size:10px;font-weight:600;color:var(--text-3);text-transform:uppercase;letter-spacing:0.05em;">Step</th>
          <th style="text-align:left;padding:4px 6px;font-size:10px;font-weight:600;color:var(--text-3);text-transform:uppercase;letter-spacing:0.05em;">Model</th>
          <th style="text-align:right;padding:4px 6px;font-size:10px;font-weight:600;color:var(--text-3);text-transform:uppercase;letter-spacing:0.05em;">Input</th>
          <th style="text-align:right;padding:4px 6px;font-size:10px;font-weight:600;color:var(--text-3);text-transform:uppercase;letter-spacing:0.05em;">Status</th>
        </tr></thead>
        <tbody>${rows}</tbody>
      </table>
      <div style="background:var(--bg-2);border:1px solid var(--border);border-radius:10px;padding:14px;font-size:12px;color:var(--text-2);line-height:1.8;">
        <div><b style="color:var(--text-1);">${willRun.length}</b> of 5 steps will regenerate${cached.length?`, <b style="color:var(--green);">${cached.length}</b> cached (skipped)`:''}</div>
        <div>Projected <b style="color:var(--text-1);">~${_fmtTokens(totalIn)}</b> input + <b style="color:var(--text-1);">~${_fmtTokens(totalOut)}</b> output &nbsp;≈&nbsp; <b style="color:var(--text-1);">${_fmtTokens(totalIn+totalOut)}</b> tokens</div>
        ${saved?`<div style="color:var(--green);">Cache saves ~${_fmtTokens(saved)} input tokens this run</div>`:''}
      </div>
      <div class="dialog-actions">
        <button class="btn btn-ghost btn-sm" onclick="closeBuildPreview()">Close</button>
        <button class="btn btn-primary btn-sm" onclick="closeBuildPreview();runBuildStep('all')">Run Build · ~${_fmtTokens(totalIn+totalOut)} tok</button>
      </div>
    </div>`;
  document.body.appendChild(overlay);
}

async function runBuildStep(step, phaseId) {
  try {
    optimisticRunning = { stage: step, startTime: Date.now() };
    renderBuildSteps();
    const body = { step };
    if (phaseId) body.phase_id = phaseId;
    const res = await apiFetch('/api/build-system', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    if (!res.ok) {
      const data = await res.json();
      showToast(data.error || 'Build failed to start', 'error');
      optimisticRunning = null;
    } else {
      // Open the log drawer for the first step that will run
      const firstStep = (step === 'all') ? 'backend' : step;
      showBuildLog(firstStep);
    }
  } catch (e) {
    showToast('Build failed to start', 'error');
    optimisticRunning = null;
  }
}

// ---- Build Progress Panel --------------------------------------------
// Vercel/Railway-style: stage indicators + animated progress bar + time estimates.
// No raw log noise — users need signal, not output.

const _BLD_EST_SECS = { backend: 1080, frontend: 720, integration: 480, tests: 480, infra: 360 };
const _BLD_STAGES = [
  { key: 'preparing',  label: 'Preparing',    detect: c => /\[BUILD\] Running:/.test(c) },
  { key: 'generating', label: 'Generating',   detect: c => /\[BUILD\] Invoking AI/.test(c) },
  { key: 'writing',    label: 'Writing files',detect: c => /\[BUILD\] Written:/.test(c) },
  { key: 'done',       label: 'Done',         detect: c => /\[BUILD\] Done\./.test(c) },
];

let _bld = { visible: false, step: null, content: '', running: false,
             pollTimer: null, tickTimer: null, startTime: null,
             attempt: 1, attemptStart: null };

function showBuildLog(step) {
  // If this step is already being tracked and the panel is visible,
  // just ensure visibility — never reset the timer or content for a
  // step that's already in flight. Doing so causes the timer to restart
  // from zero and progress to jump back to the initial stage percentage.
  const alreadyTracking = (_bld.visible && _bld.step === step && _bld.running);
  if (alreadyTracking) return;

  // Switching to a different step or opening fresh — reset only what's needed
  if (_bld.step !== step) {
    _bld.content = '';
    _bld.startTime = null;  // will be set from server's started_at on first poll
    _bld.attempt = 1;
    _bld.attemptStart = null;
  }
  _bld.step = step;
  _bld.visible = true;
  // running state will be confirmed by first poll; set optimistically
  const st = (buildStepsState[step] || {}).status;
  _bld.running = st === 'running' ||
    !!(state.processing && state.processing.status === 'running' &&
       (state.processing.stage === step || state.processing.stage === 'all'));
  _renderBuildProgress();
  _startBuildLogPoll();
}

function closeBuildLog() {
  _bld.visible = false;
  _stopBuildLogPoll();
  if (_bld.tickTimer) { clearInterval(_bld.tickTimer); _bld.tickTimer = null; }
  const c = document.getElementById('build-log-drawer-container');
  if (c) c.innerHTML = '';
}

function _startBuildLogPoll() {
  _stopBuildLogPoll();
  _pollBuildLog();
  _bld.pollTimer = setInterval(_pollBuildLog, 2500);
}
function _stopBuildLogPoll() {
  if (_bld.pollTimer) { clearInterval(_bld.pollTimer); _bld.pollTimer = null; }
}

async function _pollBuildLog() {
  if (!_bld.visible) return;
  try {
    // ── 1. Get live build-system state ───────────────────────────────────
    const sysRes = await apiFetch('/api/build-system');
    if (!sysRes.ok) return;
    const sysData = await sysRes.json();
    buildStepsState = sysData.steps || {};
    renderBuildSteps();

    const runningEntry = Object.entries(buildStepsState).find(([,v]) => v.status === 'running');

    // ── 2. Step switch: a different step became active ───────────────────
    if (runningEntry && runningEntry[0] !== _bld.step) {
      _bld.step         = runningEntry[0];
      _bld.content      = '';
      _bld.running      = true;
      _bld.startTime    = null;   // will be set from started_at below
      _bld.attempt      = 1;
      _bld.attemptStart = null;
      _renderBuildProgress();
    }

    // ── 3. Nothing running any more — show final state then auto-close ───
    if (!runningEntry && _bld.running) {
      _bld.running = false;
      _updateBldProgress();
      _stopBuildLogPoll();
      setTimeout(() => { if (!_bld.running) closeBuildLog(); }, 4000);
      return;
    }

    // ── 4. Fetch log + started_at for the current step ───────────────────
    if (!_bld.step) return;
    const logRes = await apiFetch('/api/build-log?step=' + _bld.step);
    if (!logRes.ok) return;
    const logData = await logRes.json();

    // The server's started_at is the SINGLE source of truth for the clock.
    // It's fixed for the lifetime of a step, so we set it unconditionally every
    // poll — that makes a stale client-side timestamp (e.g. carried over from a
    // previous step's run) structurally impossible. If a step switch happened,
    // started_at now reflects the NEW step, so the timer self-corrects.
    if (logData.started_at) {
      const serverStart = new Date(logData.started_at).getTime();
      if (!isNaN(serverStart)) {
        // If the authoritative start jumped (new step / new run), reset the
        // per-attempt clock too so genElapsed can't inherit a stale base.
        if (_bld.startTime !== serverStart) _bld.attemptStart = serverStart;
        _bld.startTime = serverStart;
      }
    }

    _bld.content = logData.content || '';
    _bld.running = logData.running;

    // Detect retry attempts from the log. Each retry restarts generation from
    // scratch, so reset the per-attempt clock to keep the progress bar honest.
    const retryM = (_bld.content.match(/\[retry (\d+)\/\d+\]/g) || []);
    let attempt = 1;
    if (retryM.length) {
      const last = retryM[retryM.length - 1].match(/\[retry (\d+)\//);
      attempt = parseInt(last[1], 10);
    }
    if (attempt !== _bld.attempt) {
      _bld.attempt = attempt;
      _bld.attemptStart = Date.now();   // a new attempt just began
    }
    if (_bld.attemptStart === null) _bld.attemptStart = _bld.startTime;

    _updateBldProgress();
  } catch(e) {}
}

function _bldCalc() {
  const c = _bld.content || '';
  const totalElapsed = _bld.startTime ? Math.max(0, Math.floor((Date.now() - _bld.startTime) / 1000)) : 0;
  const attemptBase = _bld.attemptStart || _bld.startTime;
  // genElapsed can NEVER exceed total time since the step started — clamping
  // here means a stale attemptStart (from a prior step) cannot inflate the bar.
  let genElapsed = attemptBase ? Math.floor((Date.now() - attemptBase) / 1000) : 0;
  genElapsed = Math.max(0, Math.min(genElapsed, totalElapsed));
  const est = _BLD_EST_SECS[_bld.step] || 720;

  const isDone  = /\[BUILD\] Done\./.test(c);
  const isError = /rate limited|timed out|ai call failed|FAILED after|\[lock\]/i.test(c);

  // Furthest stage reached
  let si = (_bld.running || c.length) ? 0 : -1;
  for (let i = _BLD_STAGES.length - 1; i >= 0; i--) {
    if (_BLD_STAGES[i].detect(c)) { si = i; break; }
  }

  const writtenCount = (c.match(/\[BUILD\] Written:/g) || []).length;
  const attempt = _bld.attempt || 1;
  const isRetrying = attempt > 1;
  const overEstimate = genElapsed > est;

  // Progress is driven by REAL signals, not just elapsed time:
  //  - "Writing files" stage is the only thing that pushes the bar past 75%,
  //    because it means actual output exists.
  //  - During "Generating", the bar climbs with elapsed-vs-estimate but is
  //    HARD-CAPPED at 75% so it never falsely reads "almost done".
  let pct = 0;
  if (isDone)        pct = 100;
  else if (si === 3) pct = 96;
  else if (si === 2) pct = 78 + Math.min(17, writtenCount);
  else if (si === 1) pct = 12 + Math.min(63, Math.round((genElapsed / est) * 63));
  else if (si === 0) pct = 5;
  else if (_bld.running) pct = 2;

  const remaining = Math.max(0, est - genElapsed);
  return { pct, si, isDone, isError, totalElapsed, genElapsed, remaining,
           writtenCount, attempt, isRetrying, overEstimate };
}

function _fmtSecs(s) {
  if (s <= 0) return '0s';
  return s < 60 ? s + 's' : Math.ceil(s/60) + ' min';
}

// Honest one-line status. Never claims "almost done" on a timer alone.
function _bldStatusMsg(p) {
  if (p.isDone)  return 'Complete';
  if (p.isError) return 'Failed — see Build log';
  if (p.si >= 2) return p.writtenCount ? `Writing files (${p.writtenCount})…` : 'Writing files…';
  if (p.isRetrying && p.si <= 1)
    return `Output incomplete — retrying (attempt ${p.attempt} of 3)…`;
  if (p.si === 1)
    return p.overEstimate
      ? 'Generating — taking longer than usual…'
      : `Generating… ~${_fmtSecs(p.remaining)} left`;
  if (p.si === 0) return 'Preparing…';
  return 'Starting…';
}

function _bldStagePills(p) {
  return _BLD_STAGES.map((s,i) => {
    const done   = p.isDone || i < p.si;
    const active = !p.isDone && i === p.si;
    const col    = done ? '#16a34a' : active ? 'var(--accent,#4f46e5)' : 'var(--text-3,#94a3b8)';
    const w      = (done||active) ? '600' : '400';
    const icon   = done ? '✓' : active ? '●' : '○';
    return `<span style="font-size:11px;color:${col};font-weight:${w};white-space:nowrap;">${icon} ${s.label}</span>`;
  }).join(`<span style="color:var(--border);font-size:10px;padding:0 3px;">—</span>`);
}

function _renderBuildProgress() {
  const c = document.getElementById('build-log-drawer-container');
  if (!c) return;
  if (!_bld.visible) { c.innerHTML = ''; return; }
  const meta = BUILD_STEPS_META[_bld.step] || { label: _bld.step };
  const p = _bldCalc();
  const barCol = p.isError ? 'var(--red,#ef4444)' : p.isDone ? '#16a34a' : 'var(--accent,#4f46e5)';
  const icon = (!p.isDone && !p.isError && _bld.running)
    ? `<span style="display:inline-block;width:14px;height:14px;border:2px solid var(--accent,#4f46e5);border-top-color:transparent;border-radius:50%;animation:spin 0.8s linear infinite;flex-shrink:0;"></span>`
    : p.isDone  ? `<span style="color:#16a34a;font-size:16px;line-height:1;flex-shrink:0;">✓</span>`
    : p.isError ? `<span style="color:var(--red);font-size:16px;line-height:1;flex-shrink:0;">✗</span>`
    : `<span style="display:inline-block;width:14px;height:14px;border:2px solid var(--border);border-radius:50%;flex-shrink:0;"></span>`;
  const elStr = p.totalElapsed ? _fmtSecs(p.totalElapsed) : '';
  const remStr = _bldStatusMsg(p);
  const remCol = p.isError ? 'var(--red)' : (p.isRetrying ? 'var(--accent,#4f46e5)' : 'var(--text-3)');

  c.innerHTML = `<div class="card" style="margin-top:12px;margin-bottom:20px;padding:16px 18px;">
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;">
      <div style="display:flex;align-items:center;gap:10px;">
        ${icon}
        <div>
          <div style="font-size:13px;font-weight:600;color:var(--text-1);">${meta.label}</div>
          <div style="font-size:11px;color:${remCol};margin-top:2px;" id="bld-rem">${remStr}</div>
        </div>
      </div>
      <div style="display:flex;align-items:center;gap:10px;">
        <span id="bld-el" style="font-size:11px;color:var(--text-3);font-variant-numeric:tabular-nums;">${elStr}</span>
        <span id="bld-pct" style="font-size:12px;font-weight:700;color:var(--text-2);min-width:34px;text-align:right;">${p.pct}%</span>
      </div>
    </div>
    <div style="height:6px;background:var(--bg-2,#f1f5f9);border-radius:3px;overflow:hidden;margin-bottom:14px;">
      <div id="bld-bar" style="height:100%;width:${p.pct}%;background:${barCol};border-radius:3px;transition:width 0.6s ease;"></div>
    </div>
    <div id="bld-stg" style="display:flex;align-items:center;gap:4px;flex-wrap:wrap;">${_bldStagePills(p)}</div>
  </div>`;

  if (_bld.tickTimer) clearInterval(_bld.tickTimer);
  _bld.tickTimer = setInterval(() => {
    const el = document.getElementById('bld-el');
    if (!el) { clearInterval(_bld.tickTimer); return; }
    if (_bld.startTime) el.textContent = _fmtSecs(Math.floor((Date.now()-_bld.startTime)/1000));
    if (_bld.running) _updateBldProgress();
  }, 1000);
}

function _updateBldProgress() {
  const bar = document.getElementById('bld-bar');
  if (!bar) { _renderBuildProgress(); return; }
  const p = _bldCalc();
  const barCol = p.isError ? 'var(--red,#ef4444)' : p.isDone ? '#16a34a' : 'var(--accent,#4f46e5)';
  bar.style.width = p.pct + '%';
  bar.style.background = barCol;
  const pctEl = document.getElementById('bld-pct');
  const remEl = document.getElementById('bld-rem');
  const stgEl = document.getElementById('bld-stg');
  if (pctEl) pctEl.textContent = p.pct + '%';
  if (remEl) {
    remEl.textContent = _bldStatusMsg(p);
    remEl.style.color = p.isError ? 'var(--red)' : (p.isRetrying ? 'var(--accent,#4f46e5)' : 'var(--text-3)');
  }
  if (stgEl) stgEl.innerHTML = _bldStagePills(p);
}
// ----------------------------------------------------------------------

async function openBuildCodePanel(step) {
  buildCodePanelStep = step;
  const panel = document.getElementById('build-code-panel');

  // Stamp panel structure if not already present
  if (!document.getElementById('build-file-tree')) {
    panel.innerHTML = `
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
        <span id="build-code-panel-title" style="font-size:13px;font-weight:700;color:var(--text);"></span>
        <button class="btn btn-ghost btn-sm" onclick="closeBuildCodePanel()">Close</button>
      </div>
      <div style="display:flex;gap:12px;height:480px;overflow:hidden;">
        <div id="build-file-tree" style="width:220px;flex-shrink:0;overflow-y:auto;border-right:1px solid var(--border);padding-right:8px;"></div>
        <div style="flex:1;overflow:auto;">
          <pre id="build-file-content" style="margin:0;font-family:var(--mono);font-size:11px;line-height:1.6;color:var(--text-2);white-space:pre;tab-size:2;"></pre>
        </div>
      </div>`;
  }

  panel.style.display = 'block';
  document.getElementById('build-code-panel-title').textContent =
    (BUILD_STEPS_META[step]?.label || step) + ' — Generated Files';
  document.getElementById('build-file-content').textContent = '';

  const files = (buildStepsState[step] || {}).files || [];
  const tree = document.getElementById('build-file-tree');
  if (files.length === 0) {
    tree.innerHTML = '<div style="font-size:11px;color:var(--text-3);padding:8px;">No files yet.</div>';
    return;
  }

  tree.innerHTML = files.map(f => `
    <div class="tree-file"
      onclick="loadBuildFile('${step}','${escapeHtml(f)}',this)"
      style="padding:4px 6px;border-radius:4px;cursor:pointer;font-size:11px;color:var(--text-2);
             white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"
      onmouseover="this.style.background='var(--surface-2)'" onmouseout="this.style.background=''">
      ${escapeHtml(f)}
    </div>`).join('');

  // Auto-load first file
  const firstRow = tree.querySelector('.tree-file');
  if (firstRow) loadBuildFile(step, files[0], firstRow);
}

async function loadBuildFile(step, path, rowEl) {
  // Highlight selected row
  document.querySelectorAll('#build-file-tree .tree-file').forEach(el => {
    el.style.background = '';
    el.style.color = 'var(--text-2)';
    el.style.fontWeight = '';
  });
  if (rowEl) {
    rowEl.style.background = 'rgba(74,222,128,.1)';
    rowEl.style.color = 'var(--primary)';
    rowEl.style.fontWeight = '600';
  }

  const contentEl = document.getElementById('build-file-content');
  if (contentEl) contentEl.textContent = 'Loading…';

  try {
    const res = await apiFetch('/api/build-file?step=' + encodeURIComponent(step) + '&path=' + encodeURIComponent(path));
    if (res.ok) {
      const data = await res.json();
      if (contentEl) contentEl.textContent = data.content;
    } else {
      if (contentEl) contentEl.textContent = 'Error loading file.';
    }
  } catch (e) {
    if (contentEl) contentEl.textContent = 'Error loading file.';
  }
}

function closeBuildCodePanel() {
  const panel = document.getElementById('build-code-panel');
  if (panel) panel.style.display = 'none';
  buildCodePanelStep = null;
}

const BUILD_STATUS_LABELS = {
  merged:     'Merged',
  pr_created: 'PR Open',
  pushed:     'Pushed',
  pushing:    'Pushing…',
  committed:  'Committed',
  branched:   'Branched',
  validating: 'Validating…',
  local:      'Local Build',
  pending:    'Pending',
  error:      'Error',
  cancelled:  'Stopped',
};

// Seconds since last heartbeat before we alert the user
const BUILD_STUCK_WARN_SECS = 30;
const BUILD_STUCK_KILL_SECS = 60;

const BUILD_STEP_ICONS = {
  pr_created: 'checkCircle',
  pushed:     'cloudUp',
  pushing:    'cloudUp',
  committed:  'gitBranch',
  branched:   'gitBranch',
  local:      'server',
  validating: 'clock',
  pending:    'clock',
  error:      'xCircle',
};

// ============================================================
// Local Preview
// ============================================================
let _localRunData = null;
let _localRunPollTimer = null;
let _localRunLogOpen = false;   // persists open/closed state of the output log <details>

async function fetchLocalRun() {
  try {
    const r = await apiFetch('/api/local-run');
    if (!r.ok) return;
    _localRunData = await r.json();
    renderLocalRun();
    // Poll more frequently while starting or running
    const status = _localRunData && _localRunData.status;
    if (status === 'starting' || status === 'running') {
      if (!_localRunPollTimer) {
        _localRunPollTimer = setInterval(fetchLocalRun, 2500);
      }
    } else {
      if (_localRunPollTimer) { clearInterval(_localRunPollTimer); _localRunPollTimer = null; }
    }
  } catch (e) { /* non-fatal */ }
}

function renderLocalRun() {
  const el = document.getElementById('local-preview-section');
  if (!el) return;

  const d = _localRunData;
  const detect = d && d.detect;

  // ── Nothing built yet ───────────────────────────────────────────────────
  if (!detect || !detect.available) {
    el.innerHTML = `
      <div class="local-preview-card local-preview-empty">
        <div class="local-preview-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
        </div>
        <div class="local-preview-empty-body">
          <div class="local-preview-title">Local Preview</div>
          <div class="local-preview-desc">No runnable code found in this project. Build code first using Build All, then run it here.</div>
        </div>
      </div>`;
    return;
  }

  const status   = d.status || 'stopped';
  const method   = detect.method;
  const services = detect.services || [];
  const health   = d.health || {};
  const envWarns = detect.env_warnings || [];
  const blockingErrors = detect.blocking_errors || [];

  // ── Manual mode — show copy-pasteable commands ──────────────────────────
  if (method === 'manual') {
    const cmds = detect.manual_cmds || [];
    const scanRoot = detect.scan_root || '';
    // Display a shortened path (last 3 segments) for the context hint
    const scanParts = scanRoot.replace(/\\/g, '/').split('/').filter(Boolean);
    const scanDisplay = scanParts.length > 3 ? '…/' + scanParts.slice(-3).join('/') : scanRoot;
    el.innerHTML = `
      <div class="local-preview-card">
        <div class="local-preview-header">
          <div style="display:flex;align-items:center;gap:10px;">
            <div class="local-preview-icon-sm">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
            </div>
            <div>
              <div class="local-preview-title">Local Preview</div>
              <div class="local-preview-subtitle">No docker-compose found — run services in your terminal</div>
            </div>
          </div>
          <span class="badge" style="background:var(--bg-2);color:var(--text-3);border:1px solid var(--border);">Manual</span>
        </div>
        ${scanRoot ? `
        <div style="display:flex;align-items:center;gap:6px;padding:6px 12px 2px;font-size:11px;color:var(--text-3);">
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
          <span title="${escapeHtml(scanRoot)}">${escapeHtml(scanDisplay)}</span>
          <button class="btn btn-ghost btn-xs local-preview-copy-btn" style="margin-left:2px;"
            onclick="copyToClipboard(${JSON.stringify(scanRoot)}, this)"
            title="Copy full path">${icon('clipboard', 10)}</button>
        </div>` : ''}
        <div class="local-preview-services-grid">
          ${cmds.map(c => {
            const fullCmd = scanRoot
              ? 'cd ' + scanRoot + '/' + c.dir + ' && ' + c.command
              : 'cd ' + c.dir + ' && ' + c.command;
            return `
            <div class="local-preview-manual-cmd">
              <div class="local-preview-svc-name">
                <span class="local-run-dot local-run-dot--idle"></span>
                ${escapeHtml(c.name)}
                ${c.port ? `<span style="font-size:10px;color:var(--text-3);margin-left:4px;">:${c.port}</span>` : ''}
              </div>
              <div class="local-preview-cmd-block">
                <code>${escapeHtml(fullCmd)}</code>
                <button class="btn btn-ghost btn-xs local-preview-copy-btn"
                  onclick="copyToClipboard(${JSON.stringify(fullCmd)}, this)"
                  title="Copy command">
                  ${icon('clipboard', 11)}
                </button>
              </div>
            </div>`;
          }).join('')}
        </div>
      </div>`;
    return;
  }

  // ── Docker-compose mode ─────────────────────────────────────────────────
  const isRunning  = status === 'running';
  const isStarting = status === 'starting';
  const isError    = status === 'error';
  const isStopping = status === 'stopping';

  const statusBadge = isRunning  ? `<span class="badge-local-run badge-local-run--running">Running</span>`
    : isStarting ? `<span class="badge-local-run badge-local-run--starting">Starting…</span>`
    : isError    ? `<span class="badge-local-run badge-local-run--error">Error</span>`
    : isStopping ? `<span class="badge-local-run badge-local-run--starting">Stopping…</span>`
    : `<span class="badge-local-run">Stopped</span>`;

  const hasPlaceholderWarning = envWarns.length > 0 || (detect.placeholder_count || 0) > 0;
  const cfgEnvBtn = `<button class="btn btn-ghost btn-sm" onclick="openEnvConfigModal(false)" title="Configure environment variables">
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/><path d="M4.93 4.93a10 10 0 0 0 0 14.14"/></svg>
    Env
    ${hasPlaceholderWarning ? `<span class="env-cfg-dot-warn"></span>` : ''}
  </button>`;
  const ctaBtn = (isRunning || isStarting || isStopping)
    ? `<button class="btn btn-sm" style="background:#ef4444;color:#fff;border-color:#ef4444;" onclick="stopLocalRun()">Stop</button>`
    : blockingErrors.length
      ? `<button class="btn btn-primary btn-sm" disabled title="${escapeHtml(blockingErrors[0])}" style="opacity:0.45;cursor:not-allowed;">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
          Run Locally
         </button>`
      : `<button class="btn btn-primary btn-sm" onclick="startLocalRun()">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
          Run Locally
         </button>`;

  const servicesHtml = services.map(svc => {
    const h = health[svc.name] || 'starting';
    const dotCls = isRunning && h === 'healthy' ? 'local-run-dot--healthy'
      : isRunning ? 'local-run-dot--starting' : 'local-run-dot--idle';
    const urlLink = svc.url && isRunning
      ? `<a href="${escapeHtml(svc.url)}" target="_blank" class="local-preview-svc-url">${escapeHtml(svc.url)}</a>`
      : svc.url ? `<span class="local-preview-svc-url-dim">${escapeHtml(svc.url)}</span>` : '';
    return `
      <div class="local-preview-svc-row">
        <span class="local-run-dot ${dotCls}"></span>
        <span class="local-preview-svc-name-label">${escapeHtml(svc.name)}</span>
        ${urlLink}
        ${isRunning && h === 'healthy' ? `<span class="local-preview-health-ok">●&nbsp;Live</span>` : ''}
        ${isRunning && h === 'starting' ? `<span class="local-preview-health-wait">◌&nbsp;Waiting</span>` : ''}
      </div>`;
  }).join('');

  const blockingErrorsHtml = blockingErrors.length ? `
    <div class="local-preview-env-warns" style="background:rgba(239,68,68,0.08);border-color:rgba(239,68,68,0.3);">
      ${blockingErrors.map(e => `
        <div class="local-preview-env-warn-row">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          ${escapeHtml(e)}
        </div>`).join('')}
    </div>` : '';

  const envWarnsHtml = envWarns.length ? `
    <div class="local-preview-env-warns">
      ${envWarns.map(w => `
        <div class="local-preview-env-warn-row">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
          ${escapeHtml(w)}
        </div>`).join('')}
    </div>` : '';

  const errorHtml = isError && d.error
    ? `<div class="local-preview-error">${escapeHtml(d.error)}</div>` : '';

  const logs = (d.log || []);
  const logsHtml = logs.length ? `
    <details id="local-preview-log-details" class="local-preview-log-details"${_localRunLogOpen ? ' open' : ''}>
      <summary style="display:flex;align-items:center;justify-content:space-between;">
        <span>Output log (${logs.length} lines)</span>
        <button id="local-preview-log-copy" class="btn-icon" title="Copy log" style="margin-left:8px;flex-shrink:0;" onclick="event.stopPropagation();event.preventDefault();(function(){var t=document.getElementById('local-preview-log-pre');if(t)navigator.clipboard.writeText(t.textContent).then(function(){var b=document.getElementById('local-preview-log-copy');if(b){b.title='Copied!';setTimeout(function(){b.title='Copy log';},1500);}});})();">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
        </button>
      </summary>
      <pre id="local-preview-log-pre" class="local-preview-log">${escapeHtml(logs.slice(-80).join('\n'))}</pre>
    </details>` : '';

  const startedStr = d.started_at
    ? `Started ${new Date(d.started_at).toLocaleTimeString()}` : '';

  el.innerHTML = `
    <div class="local-preview-card ${isRunning ? 'local-preview-card--running' : isError ? 'local-preview-card--error' : ''}">
      <div class="local-preview-header">
        <div style="display:flex;align-items:center;gap:10px;">
          <div class="local-preview-icon-sm ${isRunning ? 'local-preview-icon-sm--active' : ''}">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
          </div>
          <div>
            <div class="local-preview-title">Local Preview</div>
            <div class="local-preview-subtitle">
              Docker Compose &nbsp;·&nbsp; <code style="font-size:10px;">${escapeHtml(detect.compose_file || '')}</code>
              ${startedStr ? `&nbsp;·&nbsp; ${escapeHtml(startedStr)}` : ''}
            </div>
          </div>
        </div>
        <div style="display:flex;align-items:center;gap:8px;">
          ${statusBadge}
          ${cfgEnvBtn}
          ${ctaBtn}
        </div>
      </div>
      ${blockingErrorsHtml}
      ${envWarnsHtml}
      ${errorHtml}
      <div class="local-preview-services">
        ${servicesHtml || '<div style="font-size:11px;color:var(--text-3);">No port mappings detected in compose file.</div>'}
      </div>
      ${logsHtml}
    </div>`;

  // Persist log open/closed state and scroll-to-bottom across re-renders
  const logDetails = document.getElementById('local-preview-log-details');
  const logPre     = document.getElementById('local-preview-log-pre');

  function _scrollLogToBottom() {
    if (logPre) logPre.scrollTop = logPre.scrollHeight;
  }

  if (logDetails) {
    logDetails.addEventListener('toggle', () => {
      _localRunLogOpen = logDetails.open;
      if (logDetails.open) _scrollLogToBottom();
    });
    // If already open (restored state), scroll to bottom immediately
    if (logDetails.open) _scrollLogToBottom();
  }
}

// ── Environment config modal ──────────────────────────────────────────────────
let _envModalVars = [];
let _envModalEnvLocalPath = '';

async function openEnvConfigModal(startAfter = false) {
  try {
    const r = await apiFetch('/api/local-run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'env_config' }),
    });
    const d = await r.json();
    if (!r.ok) { showToast(d.error || 'Failed to load env config', 'error'); return; }
    _envModalVars = d.vars || [];
    _envModalEnvLocalPath = d.env_local_path || '';
    _renderEnvConfigModal(startAfter);
  } catch (e) {
    showToast('Failed to load environment config', 'error');
  }
}

function _renderEnvConfigModal(startAfter) {
  document.getElementById('env-cfg-overlay')?.remove();

  const phVars   = _envModalVars.filter(v => v.is_placeholder);
  const okVars   = _envModalVars.filter(v => !v.is_placeholder);
  const hasPlaceholders = phVars.length > 0;

  function _varRow(v) {
    const inputType = v.is_secret ? 'password' : 'text';
    const badge = v.is_placeholder
      ? `<span class="env-cfg-badge env-cfg-badge--needs">needs value</span>`
      : `<span class="env-cfg-badge env-cfg-badge--ok">configured</span>`;
    return `
      <div class="env-cfg-row ${v.is_placeholder ? 'env-cfg-row--ph' : ''}">
        <div class="env-cfg-row-header">
          <code class="env-cfg-key">${escapeHtml(v.key)}</code>
          ${badge}
        </div>
        ${v.description ? `<div class="env-cfg-desc">${escapeHtml(v.description)}</div>` : ''}
        <input
          class="input env-cfg-input"
          type="${inputType}"
          data-key="${escapeHtml(v.key)}"
          value="${escapeHtml(v.value || '')}"
          placeholder="${v.is_placeholder ? 'Enter value…' : ''}"
          autocomplete="off"
          spellcheck="false"
        />
      </div>`;
  }

  const overlay = document.createElement('div');
  overlay.id = 'env-cfg-overlay';
  overlay.className = 'dialog-overlay';
  overlay.addEventListener('click', e => { if (e.target === overlay) overlay.remove(); });

  overlay.innerHTML = `
    <div class="env-cfg-modal">
      <div class="env-cfg-header">
        <div>
          <div class="env-cfg-title">Environment Setup</div>
          <div class="env-cfg-subtitle">
            ${hasPlaceholders
              ? `${phVars.length} variable${phVars.length !== 1 ? 's' : ''} need${phVars.length === 1 ? 's' : ''} your credentials before running`
              : 'All variables are configured'}
          </div>
        </div>
        <button class="btn-icon" onclick="document.getElementById('env-cfg-overlay').remove()" title="Close">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>

      <div class="env-cfg-body">
        ${hasPlaceholders ? `
          <div class="env-cfg-section-label">Required — enter your credentials</div>
          ${phVars.map(_varRow).join('')}
        ` : ''}

        ${okVars.length ? `
          <details class="env-cfg-configured-details" ${hasPlaceholders ? '' : 'open'}>
            <summary class="env-cfg-section-label" style="cursor:pointer;user-select:none;list-style:none;display:flex;align-items:center;gap:6px;">
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="transition:transform .15s"><polyline points="9 18 15 12 9 6"/></svg>
              Configured (${okVars.length})
            </summary>
            ${okVars.map(_varRow).join('')}
          </details>
        ` : ''}

        ${_envModalVars.length === 0 ? `
          <div style="color:var(--text-3);font-size:12px;padding:20px 0;text-align:center;">
            No .env.example found — add variables manually below.
          </div>
        ` : ''}
      </div>

      <div class="env-cfg-path" title="${escapeHtml(_envModalEnvLocalPath)}">
        Writes to: <code>${escapeHtml(_envModalEnvLocalPath.split('/').slice(-3).join('/') || _envModalEnvLocalPath)}</code>
      </div>

      <div class="env-cfg-footer">
        <button class="btn btn-ghost btn-sm" onclick="document.getElementById('env-cfg-overlay').remove()">Cancel</button>
        <div style="display:flex;gap:8px;">
          <button class="btn btn-sm" onclick="_saveEnvConfig(false)">Save</button>
          ${startAfter ? `<button class="btn btn-primary btn-sm" onclick="_saveEnvConfig(true)">Save &amp; Run</button>` : ''}
        </div>
      </div>
    </div>`;

  document.body.appendChild(overlay);

  // rotate arrow on details toggle
  overlay.querySelector('.env-cfg-configured-details')?.addEventListener('toggle', e => {
    const arrow = e.target.querySelector('summary svg');
    if (arrow) arrow.style.transform = e.target.open ? 'rotate(90deg)' : '';
  });
}

async function _saveEnvConfig(startAfter) {
  const inputs = document.querySelectorAll('#env-cfg-overlay .env-cfg-input');
  const vars = {};
  inputs.forEach(inp => {
    const key = inp.dataset.key;
    const val = inp.value.trim();
    if (key && val) vars[key] = val;
  });

  try {
    const r = await apiFetch('/api/local-run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'env_save', vars }),
    });
    const d = await r.json();
    if (!r.ok) { showToast(d.error || 'Failed to save', 'error'); return; }
    showToast('Environment saved', 'success');
    document.getElementById('env-cfg-overlay')?.remove();
    await fetchLocalRun();
    if (startAfter) _doStartLocalRun();
  } catch (e) {
    showToast('Save failed: ' + e.message, 'error');
  }
}

async function startLocalRun() {
  // Check placeholder count first — if any, show config modal instead of starting directly
  try {
    const r = await apiFetch('/api/local-run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'env_config' }),
    });
    const d = await r.json();
    if (r.ok && (d.placeholder_count || 0) > 0) {
      _envModalVars = d.vars || [];
      _envModalEnvLocalPath = d.env_local_path || '';
      _renderEnvConfigModal(true);
      return;
    }
  } catch (_) { /* proceed without modal */ }
  _doStartLocalRun();
}

async function _doStartLocalRun() {
  try {
    const r = await apiFetch('/api/local-run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'start' }),
    });
    const d = await r.json();
    if (!r.ok) {
      showToast(d.error || 'Failed to start', 'error');
      return;
    }
    showToast('Local preview starting…', 'info');
    await fetchLocalRun();
  } catch (e) {
    showToast('Start failed: ' + e.message, 'error');
  }
}

async function stopLocalRun() {
  try {
    const r = await apiFetch('/api/local-run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'stop' }),
    });
    if (!r.ok) {
      const d = await r.json();
      showToast(d.error || 'Stop failed', 'error');
      return;
    }
    showToast('Local preview stopped', 'info');
    await fetchLocalRun();
  } catch (e) {
    showToast('Stop failed: ' + e.message, 'error');
  }
}

function renderBuild() {
  fetchBuildSteps();
  syncReviewStatus();
  checkAllPrStatuses();
  fetchLocalRun();
  const git = state.git || {};
  const builds = state.builds || [];

  // ── Compute gate conditions ───────────────────────────────────────────────
  const hasGit      = !!(git.repo_url);
  const hasGenDocs  = Object.values(state.stageReviewSummary || {}).some(s => (s.generated || 0) > 0);
  const hasBuildFiles = Object.values(buildStepsState).some(s => s.status === 'complete');

  // A build step or AI pipeline is actively running — lock Git/PR actions.
  const isBuildRunning = (state.processing && state.processing.status === 'running') || !!optimisticRunning;

  // ── Build System section gate (requires generated docs) ──────────────────
  const buildSysEl = document.getElementById('build-steps-grid');
  const buildAllBtn = document.getElementById('btn-build-all');
  let buildSysGate = document.getElementById('build-system-gate');
  if (!buildSysGate) {
    buildSysGate = document.createElement('div');
    buildSysGate.id = 'build-system-gate';
    buildSysEl.parentNode.insertBefore(buildSysGate, buildSysEl);
  }

  // ── Phase context banner ─────────────────────────────────────────────────
  let phaseBanner = document.getElementById('build-phase-banner');
  if (!phaseBanner) {
    phaseBanner = document.createElement('div');
    phaseBanner.id = 'build-phase-banner';
    buildSysEl.parentNode.insertBefore(phaseBanner, buildSysGate);
  }
  const activePhase = (state.phases || []).find(p => p.id === (state.active_phase_id || ''));
  if (activePhase) {
    phaseBanner.innerHTML = `
      <div style="display:flex;align-items:center;gap:10px;padding:8px 14px;background:rgba(74,222,128,.07);border:1px solid rgba(74,222,128,.2);border-radius:8px;margin-bottom:14px;">
        ${icon('bolt', 13)}
        <span style="font-size:12px;color:var(--text-2);">Building for phase:</span>
        <span style="font-size:12px;font-weight:700;color:var(--primary);">${escapeHtml(activePhase.name)}</span>
        <span style="font-size:11px;color:var(--text-3);margin-left:4px;">— output in <code style="font-size:10px;color:var(--text-2);">15-build/${escapeHtml(activePhase.id)}/</code></span>
      </div>`;
  } else {
    phaseBanner.innerHTML = '';
  }

  if (!hasGenDocs) {
    buildSysGate.innerHTML = `
      <div class="build-gate-card" style="margin-bottom:16px;">
        <div class="build-gate-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z"/>
          </svg>
        </div>
        <div class="build-gate-body">
          <div class="build-gate-title">Generate documentation first</div>
          <div class="build-gate-desc">The build system generates code from your specs. Add inputs and run the AI pipeline before building.</div>
          <div class="build-gate-actions">
            <button class="btn btn-primary btn-sm" onclick="switchView('generate')">Go to Generate</button>
          </div>
        </div>
      </div>`;
    buildSysEl.style.opacity = '0.3';
    buildSysEl.style.pointerEvents = 'none';
    if (buildAllBtn) buildAllBtn.disabled = true;
  } else {
    buildSysGate.innerHTML = '';
    buildSysEl.style.opacity = '';
    buildSysEl.style.pointerEvents = '';
    if (buildAllBtn) buildAllBtn.disabled = isBuildRunning;
  }

  // ── Git & PR section ──────────────────────────────────────────────────────
  const gitPrEl = document.getElementById('git-pr-section');

  // Lock entire Git & PR section while build is running — prevents committing
  // incomplete or mid-write output files.
  if (isBuildRunning) {
    const runningStage = (state.processing && state.processing.stage) || 'build';
    gitPrEl.innerHTML = `
      <div class="build-running-lock">
        <div class="build-running-lock-left">
          <span class="build-running-lock-spinner"></span>
          <div>
            <div class="build-running-lock-title">Build pipeline running</div>
            <div class="build-running-lock-desc">Git actions are locked while <strong>${escapeHtml(runningStage)}</strong> is running. Committing mid-build would capture incomplete output. Actions unlock automatically when the step finishes.</div>
          </div>
        </div>
      </div>`;
    return;
  }

  if (!hasGit && !hasBuildFiles) {
    // Both missing — show a checklist-style gate (GitHub Actions / Vercel pattern)
    gitPrEl.innerHTML = `
      <div class="build-gate-card build-gate-card--checklist" style="margin-bottom:16px;">
        <div class="build-gate-checklist">
          <div class="build-gate-check-item build-gate-check--missing">
            <div class="build-gate-check-icon">
              <svg width="11" height="11" viewBox="0 0 12 12" fill="none"><path d="M1 1l10 10M11 1L1 11" stroke="currentColor" stroke-width="1.75" stroke-linecap="round"/></svg>
            </div>
            <div class="build-gate-check-body">
              <div class="build-gate-check-label">Git repository not configured</div>
              <div class="build-gate-check-hint">Set a repo URL, default branch, and optional PAT in Settings.</div>
            </div>
            <button class="btn btn-ghost btn-xs" onclick="switchView('settings')">Configure</button>
          </div>
          <div class="build-gate-check-item build-gate-check--missing">
            <div class="build-gate-check-icon">
              <svg width="11" height="11" viewBox="0 0 12 12" fill="none"><path d="M1 1l10 10M11 1L1 11" stroke="currentColor" stroke-width="1.75" stroke-linecap="round"/></svg>
            </div>
            <div class="build-gate-check-body">
              <div class="build-gate-check-label">No build files generated yet</div>
              <div class="build-gate-check-hint">Run at least one build step above to produce code files.</div>
            </div>
          </div>
        </div>
        <div class="build-gate-footer">
          <div class="build-gate-footer-text">Both are required before you can review and push to GitHub.</div>
        </div>
      </div>`;
  } else if (!hasGit) {
    gitPrEl.innerHTML = `
      <div class="build-gate-card" style="margin-bottom:16px;">
        <div class="build-gate-icon build-gate-icon--warn">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/>
          </svg>
        </div>
        <div class="build-gate-body">
          <div class="build-gate-title">Git not configured — local builds only</div>
          <div class="build-gate-desc">No remote repository set. You can still commit locally and run validation (syntax check, tests, docker config). Configure a repo to push and open a PR.</div>
          <div class="build-gate-actions">
            <button class="btn btn-secondary btn-sm" onclick="startLocalBuild()">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/></svg>
              Commit &amp; Validate Locally
            </button>
            <button class="btn btn-ghost btn-sm" onclick="switchView('settings')">Configure Git →</button>
          </div>
        </div>
      </div>`;
  } else if (!hasBuildFiles) {
    gitPrEl.innerHTML = `
      <div class="build-gate-card" style="margin-bottom:16px;">
        <div class="build-gate-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>
          </svg>
        </div>
        <div class="build-gate-body">
          <div class="build-gate-title">No build files to push yet</div>
          <div class="build-gate-desc">Run at least one build step above to generate code files. Once files are ready, Review &amp; Push will commit them to your repository.</div>
        </div>
        <div class="build-gate-git-info">
          <span style="color:var(--text-3);font-size:11px;">Repo:</span>
          <code style="font-size:11px;color:var(--text-2);">${escapeHtml(git.repo_url)}</code>
          <span style="color:var(--text-3);font-size:11px;margin-left:8px;">→</span>
          <code style="font-size:11px;color:var(--text-2);">${escapeHtml(git.default_branch || 'main')}</code>
        </div>
      </div>`;
  } else {
    // Both conditions met — show normal git summary + enabled button
    gitPrEl.innerHTML = `
      <div class="card" style="margin-bottom:12px;">
        <div class="card-title" style="display:flex;align-items:center;justify-content:space-between;">
          <span>Git Configuration</span>
          <button class="btn btn-ghost btn-xs" onclick="switchView('settings')">Edit</button>
        </div>
        <div style="display:flex;flex-direction:column;gap:4px;font-size:12px;color:var(--text-2);">
          <div><span style="color:var(--text-3)">Repo:</span> <code style="font-size:11px">${escapeHtml(git.repo_url)}</code></div>
          <div><span style="color:var(--text-3)">Branch prefix:</span> <code style="font-size:11px">${escapeHtml(git.branch_prefix || 'forge')}</code></div>
          <div><span style="color:var(--text-3)">Default branch:</span> <code style="font-size:11px">${escapeHtml(git.default_branch || 'main')}</code></div>
        </div>
      </div>
      <button class="btn btn-secondary" onclick="startReviewAndPush()" id="btn-start-build" style="margin-bottom:16px;">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7z"/><circle cx="12" cy="12" r="3"/></svg>
        Review &amp; Push
      </button>`;
    // Re-attach review status after the button is freshly rendered
    syncReviewStatus();
  }

  const historyEl = document.getElementById('build-history');
  if (builds.length === 0) {
    historyEl.innerHTML = `<div style="font-size:12px;color:var(--text-3);padding:20px 0;text-align:center;">No builds yet. Configure git and run a build step to create your first build.</div>`;
    return;
  }

  // Capture open state before destroying DOM
  historyEl.querySelectorAll('details[data-build-log]').forEach(el => {
    if (el.open) _openBuildLogs.add(el.dataset.buildLog);
    else _openBuildLogs.delete(el.dataset.buildLog);
  });
  historyEl.querySelectorAll('details[data-build-commits]').forEach(el => {
    if (el.open) _openBuildCommits.add(el.dataset.buildCommits);
    else _openBuildCommits.delete(el.dataset.buildCommits);
  });

  historyEl.innerHTML = [...builds].reverse().map(b => {
    const logs = (b.log || []).join('\n');
    const statusLabel = BUILD_STATUS_LABELS[b.status] || b.status;
    // _live is injected by compute_full_state() only for the in-progress entry
    const isLive = !!b._live;
    const isCancelled = b.status === 'cancelled';

    // ── Stuck-detection ──────────────────────────────────────────────────────
    // heartbeat is written every 10 s by the server-side heartbeat ticker.
    // If it goes silent the build thread has likely blocked on a git/network op.
    const heartbeatAge = b.heartbeat
      ? Math.floor((Date.now() - Date.parse(b.heartbeat)) / 1000)
      : null;
    const isStuckWarn  = isLive && !isCancelled && heartbeatAge !== null && heartbeatAge >= BUILD_STUCK_WARN_SECS;
    const isStuckKill  = isLive && !isCancelled && heartbeatAge !== null && heartbeatAge >= BUILD_STUCK_KILL_SECS;

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

    // Live progress pill — suppressed once the build is cancelled/stuck-critical
    const liveProgress = (isLive && !isCancelled) ? `
      <div style="margin-top:8px;padding:8px 10px;background:var(--bg-2);border-radius:6px;font-size:11px;color:var(--text-2);display:flex;align-items:center;gap:8px;">
        <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${isStuckWarn ? '#f59e0b' : 'var(--blue)'};animation:pulse 1.2s ease-in-out infinite;flex-shrink:0;"></span>
        ${statusLabel} — branch <code>${escapeHtml(b.branch)}</code>
        ${heartbeatAge !== null ? `<span style="margin-left:auto;color:var(--text-3);font-size:10px;">${heartbeatAge}s ago</span>` : ''}
      </div>` : '';

    // Stuck banners — escalating from warning → critical Stop
    const stuckBanner = (() => {
      if (!isLive || isCancelled) return '';
      if (isStuckKill) return `
        <div class="build-stuck-critical">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0;color:#f87171"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
          <div style="flex:1;min-width:0;">
            <div style="font-size:12px;font-weight:700;color:#f87171;">Build appears stuck — ${heartbeatAge}s with no activity</div>
            <div style="font-size:11px;color:var(--text-3);margin-top:2px;">The build process may be blocked on a network operation. Stop it and restart when ready.</div>
          </div>
          <div style="display:flex;gap:8px;flex-shrink:0;">
            <button class="btn btn-sm" style="background:#ef4444;color:#fff;border-color:#ef4444;" onclick="stopBuild()">Stop Build</button>
          </div>
        </div>`;
      if (isStuckWarn) return `
        <div class="build-stuck-warn">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0;"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          <span>Taking longer than expected (${heartbeatAge}s since last update)</span>
          <button class="btn btn-ghost btn-xs" style="margin-left:auto;flex-shrink:0;" onclick="stopBuild()">Stop</button>
        </div>`;
      return '';
    })();

    // Restart nudge shown after a manual stop
    const cancelledNudge = (isCancelled && isLive) ? `
      <div style="display:flex;align-items:center;gap:10px;margin-top:8px;padding:10px 12px;background:rgba(248,113,113,.07);border:1px solid rgba(248,113,113,.25);border-radius:6px;font-size:12px;color:var(--text-2);">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#f87171" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0;"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
        <span>Build was stopped. Any partial commits on branch <code>${escapeHtml(b.branch)}</code> are preserved locally.</span>
        <button class="btn btn-secondary btn-xs" style="margin-left:auto;flex-shrink:0;" onclick="restartBuild()">Restart Build</button>
      </div>` : '';

    const copyBtn = `<button class="btn btn-ghost btn-sm" onclick="navigator.clipboard.writeText('${escapeHtml(b.branch)}')" style="margin-left:4px;padding:2px 6px;" title="Copy branch name">${icon('clipboard',11)}</button>`;

    // ── Validation results card ─────────────────────────────────────────────
    const validCard = (() => {
      const v = b.validation;
      if (!v || v.status === 'skipped') return '';
      const vColor = v.status === 'passed' ? 'var(--primary)' : v.status === 'failed' ? '#f87171' : 'var(--text-3)';
      const vBg    = v.status === 'passed' ? 'rgba(74,222,128,.07)' : v.status === 'failed' ? 'rgba(248,113,113,.08)' : 'var(--bg-2)';
      const parts = [];
      const syn = v.syntax || {};
      if (syn.status === 'passed') parts.push(`${icon('checkCircle',11)} ${syn.checked} Python files OK`);
      else if (syn.status === 'failed') parts.push(`${icon('xCircle',11)} Syntax: ${syn.errors.slice(0,1).join('; ')}`);
      const tst = v.tests || {};
      if (tst.status === 'passed')  parts.push(`${icon('checkCircle',11)} ${tst.passed} tests passed`);
      else if (tst.status === 'failed')  parts.push(`${icon('xCircle',11)} ${tst.failed} test(s) failed`);
      else if (tst.status === 'timeout') parts.push(`${icon('clock',11)} Tests timed out`);
      const dkr = v.docker || {};
      if (dkr.status === 'passed') parts.push(`${icon('checkCircle',11)} Docker config OK`);
      else if (dkr.status === 'failed') parts.push(`${icon('xCircle',11)} Docker config invalid`);
      const testOut = tst.output ? `
        <details style="margin-top:6px;"><summary style="font-size:10px;color:var(--text-3);cursor:pointer;">Test output</summary>
          <pre style="margin-top:4px;font-size:10px;color:var(--text-2);background:var(--bg-3,var(--bg-2));padding:8px;border-radius:4px;overflow-x:auto;max-height:200px;">${escapeHtml(tst.output)}</pre>
        </details>` : '';
      const synErrs = syn.errors && syn.errors.length ? `
        <details style="margin-top:6px;"><summary style="font-size:10px;color:var(--text-3);cursor:pointer;">Syntax errors (${syn.errors.length})</summary>
          <pre style="margin-top:4px;font-size:10px;color:#f87171;background:var(--bg-2);padding:8px;border-radius:4px;overflow-x:auto;max-height:120px;">${escapeHtml(syn.errors.join('\n'))}</pre>
        </details>` : '';
      return `
        <div style="padding:8px 12px;background:${vBg};border:1px solid ${vColor};border-radius:6px;margin-top:8px;">
          <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
            <span style="font-size:11px;font-weight:700;color:${vColor};white-space:nowrap;">Validation ${v.status.toUpperCase()}</span>
            <span style="font-size:11px;color:var(--text-2);">${parts.join(' &nbsp;·&nbsp; ') || 'No checks ran'}</span>
          </div>
          ${synErrs}${testOut}
        </div>`;
    })();

    // ── "Push to Git" nudge for local builds once git gets configured ────────
    const localPushNudge = (b.status === 'local' && hasGit) ? `
      <div style="display:flex;align-items:center;gap:8px;padding:8px 12px;background:rgba(74,222,128,.05);border:1px solid rgba(74,222,128,.2);border-radius:6px;margin-top:8px;font-size:11px;color:var(--text-2);">
        ${icon('cloudUp',13)}
        <span>Git is now configured — you can push this local build.</span>
        <button class="btn btn-secondary btn-xs" style="margin-left:auto;" onclick="startReviewAndPush()">Push to Git</button>
      </div>` : '';

    // ── Commit list card ──────────────────────────────────────────────────────
    const commits = b.commits || [];
    const commitCard = commits.length > 0 ? `
      <details data-build-commits="${escapeHtml(b.created_at)}" style="margin-top:8px;"${_openBuildCommits.has(b.created_at) ? ' open' : ''}>
        <summary style="font-size:11px;color:var(--text-3);cursor:pointer;user-select:none;">
          ${icon('gitBranch',11)} ${commits.length} commit${commits.length !== 1 ? 's' : ''}
        </summary>
        <div class="build-commit-list">
          ${commits.map(c => `
            <div class="build-commit-row">
              <code class="build-commit-sha">${escapeHtml(c.sha || '')}</code>
              <span class="build-commit-msg">${escapeHtml(c.message || '')}</span>
            </div>`).join('')}
        </div>
      </details>` : '';

    return `
      <div class="build-history-item" ${isStuckKill ? 'style="border-color:#ef4444"' : isLive ? 'style="border-color:var(--blue)"' : b.status === 'cancelled' ? 'style="border-color:rgba(248,113,113,.3)"' : b.status === 'local' ? 'style="border-color:rgba(74,222,128,.3)"' : ''}>
        <div class="build-history-header">
          <span class="badge badge-${b.status}">${statusLabel}</span>
          <code class="build-branch">${escapeHtml(b.branch)}</code>
          ${copyBtn}
          <span class="build-date" style="margin-left:auto;">${new Date(b.created_at).toLocaleString()}</span>
        </div>
        ${stuckBanner}
        ${liveProgress}
        ${cancelledNudge}
        ${prCard}
        ${validCard}
        ${commitCard}
        ${localPushNudge}
        ${logs ? `<details data-build-log="${escapeHtml(b.created_at)}" style="margin-top:8px;"${_openBuildLogs.has(b.created_at) ? ' open' : ''}><summary style="font-size:11px;color:var(--text-3);cursor:pointer;">Build log (${(b.log||[]).length} lines)</summary><div class="build-log" style="margin-top:4px;">${escapeHtml(logs)}</div></details>` : ''}
      </div>
    `;
  }).join('');

  // Attach toggle listeners so open/closed state is tracked in real time
  historyEl.querySelectorAll('details[data-build-log]').forEach(el => {
    el.addEventListener('toggle', () => {
      if (el.open) _openBuildLogs.add(el.dataset.buildLog);
      else _openBuildLogs.delete(el.dataset.buildLog);
    });
  });
  historyEl.querySelectorAll('details[data-build-commits]').forEach(el => {
    el.addEventListener('toggle', () => {
      if (el.open) _openBuildCommits.add(el.dataset.buildCommits);
      else _openBuildCommits.delete(el.dataset.buildCommits);
    });
  });
}

// ============================================================
// Pre-push review flow
// ============================================================
// Build log / commit details open-state persistence
// Keyed by build `created_at` timestamp string.
// ============================================================
const _openBuildLogs    = new Set();   // build IDs whose log <details> is open
const _openBuildCommits = new Set();   // build IDs whose commits <details> is open

// ============================================================
// Build stuck — stop and restart
// ============================================================
async function stopBuild() {
  try {
    const r = await apiFetch('/api/build', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'cancel' }),
    });
    if (!r.ok) {
      const j = await r.json().catch(() => ({}));
      showToast('Stop failed: ' + (j.error || r.status), 'error');
      return;
    }
    showToast('Build stopped', 'info');
    // Force immediate UI refresh; the progress file will be stamped "cancelled"
    await fetchState();
  } catch (e) {
    showToast('Stop failed: ' + e.message, 'error');
  }
}

async function restartBuild() {
  // Trigger a fresh build — same path as "Commit & Push" in the review panel.
  // The stopped branch is preserved locally; the new run gets a new branch name.
  try {
    const res = await apiFetch('/api/build', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    });
    if (!res.ok) {
      const j = await res.json().catch(() => ({}));
      showToast('Restart failed: ' + (j.error || res.status), 'error');
      return;
    }
    const d = await res.json();
    showToast(`Build restarted: ${d.branch || ''}`, 'info');
    await fetchState();
  } catch (e) {
    showToast('Restart failed: ' + e.message, 'error');
  }
}

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
      _checkedPrUrls.delete(prUrl);
      // Server already transitioned phase to deployed in pr-status handler.
      // Force immediate re-poll so merged badge + phase status appear without waiting.
      loadState();
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

// Local-only build: skip diff review, go straight to commit+validate
async function startLocalBuild() {
  try {
    const res = await apiFetch('/api/build', { method: 'POST', body: JSON.stringify({ action: 'push' }) });
    const d = await res.json();
    if (d.status === 'started') {
      showToast('Local build started — validating generated code…', 'info');
      setTimeout(loadState, 2000);
    } else {
      showToast(d.error || 'Could not start local build', 'error');
    }
  } catch (e) {
    showToast('Local build failed to start', 'error');
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
    approve:            { cls: 'var(--primary)', label: '✅ Approve',             hint: 'No blocking issues found.' },
    approve_with_notes: { cls: '#f59e0b',         label: '⚠️ Approve with Notes', hint: 'Minor issues noted — can proceed.' },
    request_changes:    { cls: 'var(--red)',      label: '❌ Request Changes',      hint: 'Issues must be fixed before merging.' },
    unknown:            { cls: 'var(--text-2)',   label: '? Unknown verdict',       hint: '' },
    error:              { cls: 'var(--red)',      label: '! Error',                hint: '' },
  };
  const v = verdictMap[data.verdict] || verdictMap.unknown;
  const reviewHtml = (data.review || '').replace(/\n/g, '<br>').replace(/`([^`]+)`/g, '<code>$1</code>');

  // Diff viewer — file list with expandable patches
  const diffFiles = data.diff_files || [];
  const diffViewerHtml = diffFiles.length > 0 ? `
    <details style="margin-bottom:14px;">
      <summary style="font-size:12px;font-weight:600;color:var(--text-2);cursor:pointer;margin-bottom:10px;display:flex;align-items:center;gap:6px;">
        ${icon('code', 13)} Code Changes
        <span style="font-size:10px;font-weight:400;color:var(--text-3);margin-left:4px;">${diffFiles.length} file${diffFiles.length > 1 ? 's' : ''}</span>
      </summary>
      <div class="diff-file-list">
        ${diffFiles.map((f, i) => `
          <div class="diff-file-entry">
            <div class="diff-file-header" onclick="toggleDiffFile(${i})">
              <span class="diff-file-path">${escapeHtml(f.path)}</span>
              <span class="diff-stat-add">+${f.additions}</span>
              <span class="diff-stat-del">-${f.deletions}</span>
              <svg class="diff-toggle-icon" id="diff-toggle-${i}" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
            </div>
            <div class="diff-patch-body" id="diff-patch-${i}" style="display:none;">
              <pre class="diff-patch">${_renderDiffPatch(f.patch)}</pre>
            </div>
          </div>`).join('')}
      </div>
    </details>` : '';

  // Human review section
  const hr = data.human_review || {};
  const hrVerdict = hr.verdict || '';
  const hrNotes   = hr.notes   || '';
  const hrDone    = !!(hr.reviewed_at && hrVerdict);
  const humanReviewHtml = `
    <div class="human-review-section">
      <div style="font-size:12px;font-weight:600;color:var(--text-2);margin-bottom:8px;display:flex;align-items:center;gap:6px;">
        ${icon('user', 13)} Your Review
        ${hrDone ? `<span style="font-size:10px;padding:1px 7px;border-radius:10px;background:${hrVerdict === 'approve' ? 'rgba(74,222,128,.12)' : 'rgba(239,68,68,.10)'};color:${hrVerdict === 'approve' ? 'var(--primary)' : 'var(--red)'};">${hrVerdict === 'approve' ? 'Approved' : 'Changes Requested'}</span>` : ''}
      </div>
      <textarea id="human-review-notes" class="human-review-textarea" placeholder="Review notes (required when requesting changes)…">${escapeHtml(hrNotes)}</textarea>
      <div style="display:flex;gap:8px;align-items:center;margin-top:8px;">
        <button class="btn btn-primary btn-sm" onclick="proceedWithPush()">
          ${icon('cloudUp', 12)} ${data.verdict === 'request_changes' ? 'Push Anyway' : 'Approve &amp; Push'}
        </button>
        <button class="btn btn-ghost btn-sm" onclick="saveRequestChanges()" style="color:var(--red);border-color:var(--red-dim,var(--border));">
          ${icon('xCircle', 12)} Request Changes
        </button>
        <button class="btn btn-ghost btn-sm" onclick="cancelReview()">Cancel</button>
        <span style="font-size:11px;color:var(--text-3);margin-left:auto;">${new Date(data.timestamp).toLocaleTimeString()}</span>
      </div>
      ${hrDone && hrVerdict === 'request_changes' ? `<div style="margin-top:8px;font-size:11px;color:var(--red);"><strong>Changes requested</strong> — fix the issues above before pushing.</div>` : ''}
    </div>`;

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
        <summary style="font-size:12px;font-weight:600;color:var(--text-2);cursor:pointer;margin-bottom:8px;">AI review details</summary>
        <div style="font-size:12px;color:var(--text-2);line-height:1.7;padding:10px;background:var(--surface-2);border-radius:6px;max-height:280px;overflow-y:auto;">${reviewHtml}</div>
      </details>
      ${diffViewerHtml}
      ${humanReviewHtml}
    </div>`;
}

function _renderDiffPatch(patch) {
  if (!patch) return '<span style="color:var(--text-3);font-size:11px;">No diff content</span>';
  return patch.split('\n').map(line => {
    if (line.startsWith('@@')) {
      return `<span class="diff-line diff-line-hunk">${escHtml(line)}</span>`;
    } else if (line.startsWith('+')) {
      return `<span class="diff-line diff-line-add">${escHtml(line)}</span>`;
    } else if (line.startsWith('-')) {
      return `<span class="diff-line diff-line-del">${escHtml(line)}</span>`;
    }
    return `<span class="diff-line">${escHtml(line)}</span>`;
  }).join('\n');
}

function toggleDiffFile(i) {
  const body = document.getElementById(`diff-patch-${i}`);
  const icon = document.getElementById(`diff-toggle-${i}`);
  if (!body) return;
  const isOpen = body.style.display !== 'none';
  body.style.display = isOpen ? 'none' : 'block';
  if (icon) icon.style.transform = isOpen ? '' : 'rotate(180deg)';
}

async function saveRequestChanges() {
  const notes = (document.getElementById('human-review-notes') || {}).value || '';
  if (!notes.trim()) {
    showToast('Add review notes before requesting changes', 'error');
    return;
  }
  try {
    await apiFetch('/api/build-review', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'human_review', verdict: 'request_changes', notes })
    });
    showToast('Changes requested — fix issues before pushing', 'info');
    showReviewPanel({ status: 'reviewing' });
    syncReviewStatus();
  } catch (e) {
    showToast('Failed to save review', 'error');
  }
}

async function proceedWithPush() {
  const notes = (document.getElementById('human-review-notes') || {}).value || '';
  const panel = document.getElementById('review-panel');

  // Save human approval audit record before pushing
  try {
    await apiFetch('/api/build-review', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'human_review', verdict: 'approve', notes })
    });
  } catch (e) { /* non-fatal — proceed with push */ }

  if (panel) panel.innerHTML = `<div class="card" style="border-color:var(--blue)"><div style="font-size:13px;color:var(--blue);">${icon('cloudUp',14)} Pushing to GitHub…</div></div>`;

  try {
    const res = await apiFetch('/api/build', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reviewed: true })
    });
    const d = await res.json();
    showToast(`Build started: ${d.branch || ''}`, 'info');
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

let _deployPlatform = 'vercel'; // selected platform for workflow generator

function renderDeploy() {
  const hasBuildFiles = Object.values(buildStepsState).some(s => s.status === 'complete');
  const git = state.git || {};
  const envs = state.environments || {};

  const gateEl = document.getElementById('deploy-gate');
  const bodyEl = document.getElementById('deploy-body');

  if (!hasBuildFiles) {
    gateEl.style.display = '';
    gateEl.innerHTML = `
      <div class="deploy-gate-card">
        <div class="deploy-gate-icon">${icon('lock', 18)}</div>
        <div class="deploy-gate-body">
          <div class="deploy-gate-title">Build required before deploy</div>
          <div class="deploy-gate-desc">Generate your build system files first, then deploy to staging or production. This section unlocks once at least one build step has completed.</div>
          <div style="display:flex;gap:8px">
            <button class="btn btn-primary btn-sm" onclick="switchView('build')">${icon('bolt',12)} Go to Build</button>
          </div>
        </div>
      </div>`;
    bodyEl.style.display = 'none';
    return;
  }

  gateEl.style.display = 'none';
  bodyEl.style.display = '';

  _renderDeployPipeline(envs, git, hasBuildFiles);
  _renderDeployEnvCards(envs, git);
  _renderWorkflowSection(envs);
  refreshSecrets();
}

function _deployPipelineStep(label, state) {
  const cls = `deploy-pipeline-step-icon--${state}`;
  const lblCls = `deploy-pipeline-step-label--${state}`;
  const iconStr = state === 'done'
    ? `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>`
    : state === 'active'
    ? `<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>`
    : `<span style="font-size:10px;font-weight:700;opacity:.5">•••</span>`;
  return `
    <div class="deploy-pipeline-step">
      <div class="deploy-pipeline-step-icon ${cls}">${iconStr}</div>
      <span class="deploy-pipeline-step-label ${lblCls}">${label}</span>
    </div>`;
}

function _renderDeployPipeline(envs, git, hasBuildFiles) {
  const pipelineEl = document.getElementById('deploy-pipeline');
  if (!pipelineEl) return;

  const hasGit = !!(git.repo_url);
  const stagingLive = (envs.staging || {}).status === 'deployed' || !!((envs.staging || {}).url);
  const productionLive = (envs.production || {}).status === 'deployed' || !!((envs.production || {}).url);

  const steps = [
    { label: 'Build Generated', state: hasBuildFiles ? 'done' : 'pending' },
    { label: 'Git Configured', state: hasGit ? 'done' : (hasBuildFiles ? 'active' : 'pending') },
    { label: 'Staging Live', state: stagingLive ? 'done' : (hasGit ? 'active' : 'pending') },
    { label: 'Production Live', state: productionLive ? 'done' : (stagingLive ? 'active' : 'pending') },
  ];

  pipelineEl.innerHTML = steps.map((s, i) =>
    `${_deployPipelineStep(s.label, s.state)}${i < steps.length - 1 ? '<span class="deploy-pipeline-arrow">→</span>' : ''}`
  ).join('');
}

function _renderDeployEnvCards(envs, git) {
  const envsEl = document.getElementById('deploy-envs');
  if (!envsEl) return;

  const platforms = [
    { value: 'vercel',  label: 'Vercel' },
    { value: 'railway', label: 'Railway' },
    { value: 'render',  label: 'Render' },
    { value: 'custom',  label: 'Custom' },
  ];

  const envDefs = [
    {
      key: 'staging',
      label: 'Staging',
      triggerLabel: 'Auto-deploy',
      triggerCls: 'env-trigger-badge--auto',
      desc: 'Pushes to your staging branch deploy automatically via CI/CD.',
      extraClass: '',
    },
    {
      key: 'production',
      label: 'Production',
      triggerLabel: 'Manual promote',
      triggerCls: 'env-trigger-badge--manual',
      desc: 'Forge never manages production secrets. You control the platform directly.',
      extraClass: 'env-card--production',
    },
  ];

  envsEl.innerHTML = envDefs.map(def => {
    const env = envs[def.key] || {};
    const url = env.url || '';
    const branch = env.branch || (def.key === 'staging' ? 'staging' : 'main');
    const status = env.status || 'not_deployed';
    const deployedAt = env.deployed_at ? new Date(env.deployed_at).toLocaleString() : 'Never';
    const sha = env.sha || '';
    const platform = env.platform || '';
    const isLive = status === 'deployed' || !!url;

    const healthDot = isLive
      ? '<span class="env-health-dot env-health-dot--live"></span>'
      : '<span class="env-health-dot env-health-dot--idle"></span>';

    const urlRow = url
      ? `<a href="${escapeHtml(url)}" target="_blank" class="env-url-text">${escapeHtml(url)}</a>`
      : `<span class="env-url-text env-url-text--empty">No URL — configure in Settings</span>`;

    const platformOptions = platforms.map(p =>
      `<option value="${p.value}" ${platform === p.value ? 'selected' : ''}>${p.label}</option>`
    ).join('');

    const statusBadge = isLive
      ? '<span class="badge badge-pushed">Live</span>'
      : '<span class="badge badge-pending">Not Deployed</span>';

    let actions = '';
    if (def.key === 'staging') {
      actions = `
        ${url ? `<a href="${escapeHtml(url)}" target="_blank" class="btn btn-ghost btn-sm">${icon('externalLink',12)} Open</a>` : ''}
        <button class="btn btn-ghost btn-sm" onclick="switchView('settings')">${icon('cog',12)} Configure</button>`;
    } else {
      const stagingEnv = envs.staging || {};
      const stagingReady = (stagingEnv.status === 'deployed' || !!stagingEnv.url);
      actions = `
        <button class="btn btn-primary btn-sm" onclick="openPromoteModal()"
          ${!stagingReady ? 'disabled title="Staging must be live before promoting to production"' : ''}>
          ${icon('arrowUp', 12)} Promote from Staging
        </button>
        ${url ? `<a href="${escapeHtml(url)}" target="_blank" class="btn btn-ghost btn-sm">${icon('externalLink',12)} Open</a>` : ''}`;
    }

    return `
      <div class="env-card ${def.extraClass}">
        <div class="env-header">
          <div class="env-name">${healthDot} ${def.label}</div>
          <span class="env-trigger-badge ${def.triggerCls}">${def.triggerLabel}</span>
        </div>
        <div class="env-url-row">
          ${urlRow}
          ${url ? `<a href="${escapeHtml(url)}" target="_blank" style="color:var(--text-3);flex-shrink:0">${icon('externalLink',11)}</a>` : ''}
        </div>
        <div class="env-field">
          <span class="env-field-key">Status</span>
          <span>${statusBadge}</span>
        </div>
        <div class="env-field">
          <span class="env-field-key">Branch</span>
          <span class="env-field-val">${escapeHtml(branch)}</span>
        </div>
        <div class="env-field">
          <span class="env-field-key">Last Deploy</span>
          <span class="env-field-val">${escapeHtml(deployedAt)}</span>
        </div>
        ${sha ? `<div class="env-field"><span class="env-field-key">SHA</span><span class="env-sha">${escapeHtml(sha.slice(0,8))}</span></div>` : ''}
        <div class="env-platform-row">
          <span class="env-field-key" style="flex-shrink:0">Platform</span>
          <select class="env-platform-select" onchange="saveEnvPlatform('${def.key}', this.value)">
            <option value="">— select —</option>
            ${platformOptions}
          </select>
        </div>
        ${def.key === 'production' ? `<div style="font-size:10px;color:var(--text-3);line-height:1.5;margin-bottom:8px">${def.desc}</div>` : ''}
        <div class="env-actions">${actions}</div>
      </div>`;
  }).join('');
}

function _workflowYaml(platform, stagingBranch, productionBranch) {
  const sb = stagingBranch || 'staging';
  const pb = productionBranch || 'main';
  if (platform === 'vercel') {
    return `name: Deploy to Vercel

on:
  push:
    branches: [${pb}, ${sb}]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: \${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: \${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: \${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: >-
            \${{ github.ref == 'refs/heads/${pb}' && '--prod' || '' }}`;
  }
  if (platform === 'railway') {
    return `name: Deploy to Railway

on:
  push:
    branches: [${pb}, ${sb}]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Railway CLI
        run: npm install -g @railway/cli

      - name: Deploy
        run: railway up --service \${{ secrets.RAILWAY_SERVICE_ID }}
        env:
          RAILWAY_TOKEN: \${{ secrets.RAILWAY_TOKEN }}`;
  }
  if (platform === 'render') {
    return `name: Deploy to Render

on:
  push:
    branches: [${pb}, ${sb}]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Trigger Render deploy
        run: |
          curl -s -X POST \
            -H "Authorization: Bearer \${{ secrets.RENDER_API_KEY }}" \
            "https://api.render.com/v1/services/\${{ secrets.RENDER_SERVICE_ID }}/deploys" \
            -H "Content-Type: application/json" \
            -d '{}'`;
  }
  // custom / docker
  return `name: Build and Deploy

on:
  push:
    branches: [${pb}, ${sb}]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: \${{ github.actor }}
          password: \${{ secrets.GITHUB_TOKEN }}

      - name: Build and push image
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: ghcr.io/\${{ github.repository }}:latest

      # Add your deployment step here (SSH, kubectl, etc.)`;
}

function _renderWorkflowSection(envs) {
  const el = document.getElementById('deploy-workflow-section');
  if (!el) return;

  const stagingBranch = (envs.staging || {}).branch || 'staging';
  const productionBranch = (envs.production || {}).branch || 'main';
  const yaml = _workflowYaml(_deployPlatform, stagingBranch, productionBranch);

  const platforms = [
    { value: 'vercel',  label: 'Vercel' },
    { value: 'railway', label: 'Railway' },
    { value: 'render',  label: 'Render' },
    { value: 'custom',  label: 'Docker / Custom' },
  ];

  el.innerHTML = `
    <div class="deploy-workflow-card" style="margin-top:0;margin-bottom:16px">
      <div class="deploy-workflow-header">
        <div class="deploy-workflow-title">${icon('codeSquare', 14)} CI/CD Workflow File</div>
      </div>
      <div class="deploy-workflow-desc">
        Generate a <code>.github/workflows/deploy.yml</code> file for your target platform.
        Commit it to your repo — GitHub Actions handles the rest automatically on every push.
      </div>
      <div class="deploy-workflow-platform-row">
        ${platforms.map(p => `
          <button class="deploy-platform-btn ${_deployPlatform === p.value ? 'deploy-platform-btn--active' : ''}"
            onclick="setDeployPlatform('${p.value}')">${p.label}</button>
        `).join('')}
      </div>
      <div class="deploy-workflow-preview" id="workflow-yaml-preview">${escapeHtml(yaml)}</div>
      <div class="deploy-workflow-actions">
        <button class="btn btn-primary btn-sm" onclick="downloadWorkflowFile()">
          ${icon('download', 12)} Download deploy.yml
        </button>
        <button class="btn btn-ghost btn-sm" onclick="copyWorkflowFile(this)">
          ${icon('clipboard', 12)} Copy
        </button>
        <span style="font-size:11px;color:var(--text-3)">Place at <code>.github/workflows/deploy.yml</code> in your repo</span>
      </div>
    </div>`;
}

function setDeployPlatform(platform) {
  _deployPlatform = platform;
  const envs = state.environments || {};
  _renderWorkflowSection(envs);
}

function saveEnvPlatform(envKey, platform) {
  const envs = state.environments || {};
  const updated = {
    environments: {
      [envKey]: { ...(envs[envKey] || {}), platform }
    }
  };
  apiFetch('/api/settings', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(updated) })
    .then(() => { if (state.environments) state.environments[envKey] = { ...(state.environments[envKey] || {}), platform }; })
    .catch(() => {});
}

function downloadWorkflowFile() {
  const envs = state.environments || {};
  const yaml = _workflowYaml(_deployPlatform, (envs.staging || {}).branch, (envs.production || {}).branch);
  const blob = new Blob([yaml], { type: 'text/yaml' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'deploy.yml';
  a.click();
  URL.revokeObjectURL(a.href);
}

function copyWorkflowFile(btn) {
  const envs = state.environments || {};
  const yaml = _workflowYaml(_deployPlatform, (envs.staging || {}).branch, (envs.production || {}).branch);
  navigator.clipboard.writeText(yaml).then(() => {
    if (btn) { const orig = btn.innerHTML; btn.innerHTML = `${icon('checkCircle',12)} Copied`; setTimeout(() => { btn.innerHTML = orig; }, 1800); }
  }).catch(() => {});
}

function openPromoteModal() {
  const envs = state.environments || {};
  const staging = envs.staging || {};
  const production = envs.production || {};

  const overlay = document.createElement('div');
  overlay.className = 'promote-modal-overlay';
  overlay.id = 'promote-modal-overlay';
  overlay.innerHTML = `
    <div class="promote-modal">
      <div class="promote-modal-title">${icon('arrowUp', 16)} Promote to Production</div>
      <div class="promote-modal-desc">
        This will push a <code>deploy/production</code> git tag pointing at the current staging commit,
        triggering your production CI/CD workflow.
      </div>
      <div class="promote-modal-diff">
        <div class="promote-modal-diff-row">
          <span style="color:var(--text-2)">Staging SHA</span>
          <span style="color:var(--green)">${staging.sha ? staging.sha.slice(0,12) : 'unknown'}</span>
        </div>
        <div class="promote-modal-diff-row">
          <span style="color:var(--text-2)">Production SHA</span>
          <span style="color:var(--text-3)">${production.sha ? production.sha.slice(0,12) : 'not deployed'}</span>
        </div>
        <div class="promote-modal-diff-row" style="margin-top:8px;padding-top:8px;border-top:1px solid var(--border)">
          <span style="color:var(--text-2)">Staging URL</span>
          <span style="color:var(--blue);font-size:10px">${staging.url || '—'}</span>
        </div>
      </div>
      <div class="promote-modal-actions">
        <button class="btn btn-ghost btn-sm" onclick="closePromoteModal()">Cancel</button>
        <button class="btn btn-primary btn-sm" onclick="confirmPromote()">${icon('arrowUp',12)} Confirm Promote</button>
      </div>
    </div>`;
  overlay.addEventListener('click', e => { if (e.target === overlay) closePromoteModal(); });
  document.body.appendChild(overlay);
}

function closePromoteModal() {
  const el = document.getElementById('promote-modal-overlay');
  if (el) el.remove();
}

function confirmPromote() {
  closePromoteModal();
  showToast('Promote triggered — push a production tag in your git workflow to complete.', 'info');
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

  const phaseMap = Object.fromEntries((state.phases || []).map(p => [p.id, p.name]));

  listEl.innerHTML = [...issues].reverse().map(issue => {
    const iconName = ISSUE_TYPE_ICONS[issue.type] || 'questionCircle';
    const statusCls = issue.status === 'open' ? 'badge-open'
      : issue.status === 'in-progress' ? 'badge-in-progress'
      : 'badge-closed';
    const priorCls = `priority-${issue.priority || 'medium'}`;
    const phaseName = issue.phase_id ? phaseMap[issue.phase_id] : null;

    return `
      <div class="issue-item" id="issue-${issue.id}" onclick="toggleIssue('${issue.id}')">
        <div class="issue-item-header">
          <span class="issue-id">${issue.id}</span>
          <span class="issue-type-icon">${icon(iconName, 14)}</span>
          <span class="issue-title">${escapeHtml(issue.title)}</span>
          ${phaseName ? `<span class="badge badge-phase">${escapeHtml(phaseName)}</span>` : ''}
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
  const phase_id = document.getElementById('new-issue-phase')?.value || '';
  const title = document.getElementById('new-issue-title').value.trim();
  const description = document.getElementById('new-issue-desc').value.trim();
  if (!title) { showToast('Title is required', 'error'); return; }

  try {
    await apiFetch('/api/issue', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type, priority, title, description, ...(phase_id ? { phase_id } : {}) })
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
// Tool detection (shared across Settings, Generate, Overview)
// ============================================================
let detectedTools = null;
let _toolsFetchedAt = 0;
const _TOOLS_TTL_MS = 30000; // re-detect if >30 s old

async function fetchToolStatus(force) {
  const now = Date.now();
  if (!force && detectedTools && (now - _toolsFetchedAt) < _TOOLS_TTL_MS) return;
  try {
    const res = await apiFetch('/api/tools');
    detectedTools = await res.json();
    _toolsFetchedAt = now;
  } catch(e) {}
}

async function refreshToolStatus() {
  const btn = document.getElementById('btn-refresh-tools');
  if (btn) { btn.disabled = true; btn.textContent = 'Detecting…'; }
  await fetchToolStatus(true);
  if (btn) { btn.disabled = false; btn.innerHTML = '<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 2v6h-6"/><path d="M3 12a9 9 0 0115-6.7L21 8"/><path d="M3 22v-6h6"/><path d="M21 12a9 9 0 01-15 6.7L3 16"/></svg> Refresh'; }
  if (currentView === 'settings') renderToolPicker();
  if (currentView === 'generate') renderGenerate();
  if (currentView === 'overview') renderOverview();
}

function _toolReady(toolId) {
  // Returns true when a tool is usable (installed CLI or API-only mode)
  if (!detectedTools) return true; // unknown → optimistic, don't block
  const info = detectedTools[toolId];
  if (!info) return false;
  return info.installed;
}

function copyToClipboard(text, btn) {
  navigator.clipboard.writeText(text).then(function() {
    if (btn) {
      const orig = btn.innerHTML;
      btn.innerHTML = icon('check', 11) + ' Copied';
      btn.classList.add('btn--copied');
      setTimeout(function() { btn.innerHTML = orig; btn.classList.remove('btn--copied'); }, 2000);
    }
  }).catch(function() {
    showToast('Copy failed — select and copy manually', 'error');
  });
}

// ============================================================
// Settings
// ============================================================

function renderToolPicker() {
  const pickerEl = document.getElementById('settings-tool-picker');
  if (!pickerEl) return;

  if (!detectedTools) {
    pickerEl.innerHTML = '<div class="tool-picker-loading">Detecting installed CLIs…</div>';
    fetchToolStatus(false).then(function() { renderToolPicker(); });
    return;
  }

  const currentTool = getValue('settings-tool') || state.tool || 'gemini';

  pickerEl.innerHTML = Object.entries(detectedTools).map(function(_entry) {
    var id = _entry[0], info = _entry[1];
    var isActive = id === currentTool;
    var installed = info.installed;
    var apiOnly = info.api_only;
    var statusText = apiOnly ? 'API key' : (installed ? 'Installed' : 'Not installed');
    var statusCls  = (installed || apiOnly) ? 'tool-option-status--ok' : 'tool-option-status--missing';
    var statusDot  = (installed || apiOnly)
      ? '<svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>'
      : '<svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>';
    return '<div class="tool-option' + (isActive ? ' tool-option--active' : '') + ((!installed && !apiOnly) ? ' tool-option--missing' : '') + '"'
      + ' data-tool="' + id + '" onclick="selectTool(\'' + id + '\')">'
      + '<div class="tool-option-name">' + escapeHtml(info.label) + '</div>'
      + '<div class="tool-option-status ' + statusCls + '">'
      + statusDot + ' ' + statusText
      + '</div>'
      + '</div>';
  }).join('');

  // sync hidden input
  const hidden = document.getElementById('settings-tool');
  if (hidden && !hidden.value) hidden.value = currentTool;

  _updateInstallBanner(currentTool);
  populateModelDropdown(currentTool, state.model || '');
  renderSettingsStepModels();
  renderSettingsGenModels();
}

// Re-map per-step/per-stage overrides from one tool to another, preserving the
// TIER. An override that was the old tool's fast model becomes the new tool's
// fast model; anything that was the old tool's default becomes "Default" (so it
// follows the new global model). Overrides intentionally on a third tool are
// left alone. Mutates the draft in place; the caller persists only on Save.
function _remapDraftToTool(draft, oldTool, newTool) {
  if (!draft || !detectedTools) return;
  const oldInfo = detectedTools[oldTool] || {};
  const newInfo = detectedTools[newTool] || {};
  Object.keys(draft).forEach(function(k) {
    const ov = draft[k] || {};
    if (ov.tool && ov.tool !== oldTool) return;       // intentional cross-tool: leave it
    const wasFast = ov.model && ov.model === oldInfo.fast_model;
    if (wasFast && newInfo.fast_model) {
      draft[k] = { tool: newTool, model: newInfo.fast_model };
    } else {
      // was the strong/default tier -> revert to "Default" (new global model)
      delete draft[k];
    }
  });
}

function selectTool(toolId) {
  const hidden = document.getElementById('settings-tool');
  const oldTool = (hidden && hidden.value) || state.tool || '';
  // When the global tool changes, re-map the tiering drafts to the new tool so
  // the per-step/per-stage rows stop showing the previous tool's models.
  // (Draft only — persisted when the user clicks Save.)
  if (oldTool && oldTool !== toolId) {
    _remapDraftToTool(_stepModelsDraft, oldTool, toolId);
    _remapDraftToTool(_genModelsDraft, oldTool, toolId);
  }
  if (hidden) hidden.value = toolId;
  document.querySelectorAll('.tool-option').forEach(function(el) {
    el.classList.toggle('tool-option--active', el.dataset.tool === toolId);
  });
  _updateInstallBanner(toolId);
  // Default the global model to the new tool's default so "Default" rows resolve sensibly
  populateModelDropdown(toolId, (detectedTools[toolId] || {}).default_model || '');
  renderSettingsStepModels();
  renderSettingsGenModels();
}

function _updateInstallBanner(toolId) {
  const banner = document.getElementById('settings-install-banner');
  if (!banner || !detectedTools) return;
  const info = detectedTools[toolId];
  if (!info || info.installed) { banner.style.display = 'none'; return; }

  if (info.api_only) {
    banner.style.display = '';
    banner.innerHTML = '<div class="install-banner install-banner--info">'
      + '<div class="install-banner-title">' + icon('info', 13) + ' ' + escapeHtml(info.label) + ' uses a direct API key</div>'
      + '<div class="install-banner-body">' + escapeHtml(info.setup_hint || 'Set your API key in your environment') + '.</div>'
      + (info.install_url ? '<div class="install-banner-footer"><a href="' + escapeHtml(info.install_url) + '" target="_blank" class="install-banner-link">Platform docs →</a></div>' : '')
      + '</div>';
    return;
  }

  // CLI not installed
  const cmd = info.install_cmd || '';
  banner.style.display = '';
  banner.innerHTML = '<div class="install-banner">'
    + '<div class="install-banner-title">' + icon('alert', 13) + ' ' + escapeHtml(info.label) + ' is not installed</div>'
    + (cmd ? '<div class="install-banner-cmd-row">'
        + '<code class="install-banner-cmd">' + escapeHtml(cmd) + '</code>'
        + '<button class="btn btn-ghost btn-xs install-banner-copy" onclick="copyToClipboard(\'' + cmd.replace(/'/g, "\\'") + '\', this)">' + icon('copy', 11) + ' Copy</button>'
        + '</div>' : '')
    + '<div class="install-banner-footer">'
    + (info.install_url ? '<a href="' + escapeHtml(info.install_url) + '" target="_blank" class="install-banner-link">Install docs →</a>' : '')
    + '<span class="install-banner-hint">After installing, click Refresh to detect it.</span>'
    + '</div>'
    + '</div>';
}

function populateModelDropdown(tool, currentModel) {
  const sel = document.getElementById('settings-model');
  const hint = document.getElementById('settings-model-hint');
  if (!sel) return;
  const toolInfo = detectedTools ? detectedTools[tool] : null;
  const opts = toolInfo ? toolInfo.models : [];
  sel.innerHTML = opts.map(function(o) {
    return '<option value="' + o.id + '"' + (o.id === currentModel ? ' selected' : '') + '>' + escapeHtml(o.label) + '</option>';
  }).join('');
  if (currentModel && !opts.find(function(o) { return o.id === currentModel; })) {
    sel.insertAdjacentHTML('afterbegin', '<option value="' + escapeHtml(currentModel) + '" selected>' + escapeHtml(currentModel) + '</option>');
  }
  if (hint) {
    const info = toolInfo || {};
    const baseNote = 'Default for every build step and generate stage left on "Default" below.';
    if (info.installed === false && !info.api_only) {
      hint.textContent = '⚠ ' + (info.label || tool) + ' not installed — generation will fail';
      hint.className = 'settings-model-hint settings-model-hint--warn';
    } else {
      hint.textContent = baseNote;
      hint.className = 'settings-model-hint';
    }
  }
}

function renderSettings() {
  const git = state.git || {};
  const envs = state.environments || {};

  setValue('settings-product-name', state.project_name || '');
  const vl = document.getElementById('settings-version-label');
  if (vl) vl.textContent = state.version ? 'v' + state.version : 'v—';

  // Seed hidden tool value from state, then render picker (picker reads it)
  const hidden = document.getElementById('settings-tool');
  if (hidden) hidden.value = state.tool || 'gemini';

  // Seed the per-step + per-stage model drafts from saved state for this visit
  _stepModelsDraft = JSON.parse(JSON.stringify(state.build_step_models || {}));
  _genModelsDraft = JSON.parse(JSON.stringify(state.generate_stage_models || {}));

  if (detectedTools) {
    renderToolPicker();
  } else {
    fetchToolStatus(false).then(function() { renderToolPicker(); });
  }

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
    build_step_models: _stepModelsDraft || {},
    generate_stage_models: _genModelsDraft || {},
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

  if (name === 'knowledge') renderKnowledge();
  // Re-detect tools when user opens Generate or Settings — they may have just installed a CLI
  if (name === 'generate') {
    fetchToolStatus(true).then(function() { renderGenerate(); });
  }
  if (name === 'settings') {
    fetchToolStatus(true).then(function() { renderToolPicker(); });
  }
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
// Phase Timeline
// ============================================================
function renderPhases() {
  const phases = state.phases || [];
  const activeId = state.active_phase_id;
  const el = document.getElementById('phase-timeline');
  if (!el) return;

  // Populate phase dropdown in Issues form
  const phaseSelect = document.getElementById('new-issue-phase');
  if (phaseSelect) {
    const cur = phaseSelect.value;
    phaseSelect.innerHTML = '<option value="">— None —</option>'
      + phases.map(p => `<option value="${p.id}" ${cur === p.id ? 'selected' : ''}>${escapeHtml(p.name)}</option>`).join('');
  }

  if (phases.length === 0) {
    el.innerHTML = `<div class="phase-empty">No phases found. Click <strong>Sync from docs</strong> to extract phases from your delivery documents, or they will be added automatically after generation.</div>`;
    return;
  }

  el.innerHTML = phases.map((p, i) => {
    const isActive = p.id === activeId;
    const statusCls = _phaseStatusCls(p.status);
    const statusLabel = _phaseStatusLabel(p.status, p);

    const prevPhase = i > 0 ? phases[i - 1] : null;
    const prevDone = !prevPhase || ['built','merged','deployed'].includes(prevPhase.status);
    const canActivate = p.status === 'pending' && prevDone;
    const canBuild = p.status === 'in-progress';
    const issueCount = (p.issue_ids || []).length;
    const orderLabel = i === 0 ? 'MVP' : `P${i}`;

    // Deployment URL strip shown when deployed
    const deployUrlHtml = p.deploy_url
      ? `<a class="phase-deploy-url" href="${escapeHtml(p.deploy_url)}" target="_blank" title="${escapeHtml(p.deploy_url)}">
           ${icon('externalLink', 10)} ${escapeHtml(_truncUrl(p.deploy_url))}
         </a>`
      : '';

    return `
      <div class="phase-card ${isActive ? 'phase-card-active' : ''}">
        <div class="phase-card-top">
          <div class="phase-card-order">${orderLabel}</div>
          <div class="phase-card-name">${escapeHtml(p.name)}</div>
          <span class="phase-badge ${statusCls}">${statusLabel}</span>
        </div>
        ${p.description
          ? `<div class="phase-card-desc">${escapeHtml(p.description)}</div>`
          : `<div class="phase-card-desc" style="color:var(--text-3);font-style:italic;">Click for details</div>`
        }
        ${deployUrlHtml}
        <div class="phase-card-meta">
          ${issueCount > 0 ? `<span class="phase-issue-count">${issueCount} issue${issueCount !== 1 ? 's' : ''}</span>` : ''}
        </div>
        <div class="phase-card-actions">
          ${canActivate
            ? `<button class="btn btn-primary btn-xs" onclick="activatePhase('${p.id}')">Start Phase</button>`
            : isActive && canBuild
              ? `<button class="btn btn-primary btn-xs" onclick="runBuildStep('all','${p.id}')" title="Build all steps scoped to this phase">Build Phase</button>
                 <button class="btn btn-ghost btn-xs" onclick="completePhase('${p.id}')" title="Mark built (validates all steps complete)">Mark Built</button>`
              : (p.status === 'built' || p.status === 'merged')
                ? `<button class="btn btn-primary btn-xs" onclick="openDeployDialog('${p.id}')" title="Record live deployment URL">
                     ${icon('cloudUp', 10)} Record Deployment
                   </button>`
                : p.status === 'deployed'
                  ? `<button class="btn btn-ghost btn-xs" onclick="openDeployDialog('${p.id}')" title="Update deployment URL">
                       ${icon('cloudUp', 10)} Update URL
                     </button>`
                  : ''
          }
          <button class="phase-card-details-btn" onclick="showPhaseDrawer('${p.id}')" title="View full phase details">
            ${icon('file', 10)} Details
          </button>
        </div>
      </div>
      ${i < phases.length - 1 ? '<div class="phase-connector"></div>' : ''}
    `;
  }).join('');
}

// ============================================================
// Phase Detail Drawer
// ============================================================

function showPhaseDrawer(phaseId) {
  const phases = (state && state.phases) || [];
  const p = phases.find(x => x.id === phaseId);
  if (!p) return;

  const i = phases.indexOf(p);
  const orderLabel = i === 0 ? 'MVP' : `P${i}`;

  const orderEl = document.getElementById('phase-drawer-order');
  const nameEl  = document.getElementById('phase-drawer-name');
  const badgeEl = document.getElementById('phase-drawer-badge');
  if (orderEl) orderEl.textContent = orderLabel;
  if (nameEl)  nameEl.textContent  = p.name;
  if (badgeEl) { badgeEl.textContent = _phaseStatusLabel(p.status, p); badgeEl.className = `phase-badge ${_phaseStatusCls(p.status)}`; }

  const bodyEl = document.getElementById('phase-drawer-body');
  if (bodyEl) bodyEl.innerHTML = _renderPhaseDrawerBody(p);

  const drawer = document.getElementById('phase-detail-drawer');
  const backdrop = document.getElementById('phase-drawer-backdrop');
  if (drawer) drawer.classList.remove('hidden');
  if (backdrop) backdrop.classList.remove('hidden');
}

function closePhaseDrawer() {
  const drawer = document.getElementById('phase-detail-drawer');
  const backdrop = document.getElementById('phase-drawer-backdrop');
  if (drawer) drawer.classList.add('hidden');
  if (backdrop) backdrop.classList.add('hidden');
}

function _renderPhaseDrawerBody(p) {
  const issues = (state && state.issues) || [];
  const phaseIssues = (p.issue_ids || [])
    .map(id => issues.find(iss => iss.id === id))
    .filter(Boolean);

  let html = '';

  // ── Deployment status card ────────────────────────────────────────────────
  if (p.status === 'deployed' && p.deploy_url) {
    const envLabel = { staging: 'Staging', production: 'Production', preview: 'Preview', local: 'Local / Dev' }[p.deploy_env] || p.deploy_env || 'Production';
    const deployedAt = p.deployed_at ? new Date(p.deployed_at).toLocaleString() : '';
    html += `<div class="phase-deploy-card phase-deploy-card--live">
      <div class="phase-deploy-card-row">
        <span class="phase-deploy-env-badge">${escapeHtml(envLabel)}</span>
        ${p.deployed_by ? `<span class="phase-deploy-meta">by ${escapeHtml(p.deployed_by)}</span>` : ''}
        ${deployedAt ? `<span class="phase-deploy-meta">${deployedAt}</span>` : ''}
      </div>
      <a class="phase-deploy-url-full" href="${escapeHtml(p.deploy_url)}" target="_blank">
        ${icon('externalLink', 11)} ${escapeHtml(p.deploy_url)}
      </a>
      <button class="btn btn-ghost btn-xs" style="margin-top:8px;align-self:flex-start;" onclick="closePhaseDrawer();openDeployDialog('${p.id}')">
        ${icon('cloudUp', 10)} Update URL
      </button>
    </div>`;
  } else if (p.status === 'merged') {
    const _hasPr = !!p.pr_url;
    const _mergeLabel = _hasPr ? 'Merged to mainline' : 'Marked as deployed';
    const _mergeIcon  = _hasPr ? icon('gitBranch', 13) : icon('cloudUp', 13);
    const _mergeHint  = _hasPr
      ? 'Code is in the main branch but not yet running anywhere. Record a deployment URL once it\'s live.'
      : 'Manually marked as deployed. Configure git in Settings to push code and open PRs.';
    html += `<div class="phase-deploy-card phase-deploy-card--merged">
      <div class="phase-deploy-card-row">
        ${_mergeIcon}
        <span style="font-size:12px;font-weight:600;color:var(--purple);">${_mergeLabel}</span>
        ${p.merged_at ? `<span class="phase-deploy-meta">${new Date(p.merged_at).toLocaleString()}</span>` : ''}
      </div>
      <p class="phase-deploy-card-hint">${_mergeHint}</p>
      <button class="btn btn-primary btn-xs" style="align-self:flex-start;" onclick="closePhaseDrawer();openDeployDialog('${p.id}')">
        ${icon('cloudUp', 10)} Record Deployment
      </button>
    </div>`;
  } else if (p.status === 'built') {
    html += `<div class="phase-deploy-card phase-deploy-card--pending">
      <p class="phase-deploy-card-hint">Built and pushed — no deployment recorded yet. Once you push to an environment, record the URL here.</p>
      <button class="btn btn-ghost btn-xs" style="align-self:flex-start;" onclick="closePhaseDrawer();openDeployDialog('${p.id}')">
        ${icon('cloudUp', 10)} Record Deployment
      </button>
    </div>`;
  }

  // ── Source doc reference ──────────────────────────────────────────────────
  if (p.doc_source) {
    html += `<div class="phase-drawer-section">
      <div class="phase-drawer-section-label">Source</div>
      <span class="phase-drawer-source">${escapeHtml(p.doc_source)}</span>
    </div>`;
  }

  // ── Full doc body ─────────────────────────────────────────────────────────
  html += `<div class="phase-drawer-section">
    <div class="phase-drawer-section-label">Deliverables &amp; Scope</div>
    <div class="phase-doc-body">${_renderDocBodyHtml(p.doc_body || '')}</div>
  </div>`;

  // ── Issues ────────────────────────────────────────────────────────────────
  if (phaseIssues.length > 0) {
    const issueRows = phaseIssues.map(iss => {
      const severityCls = iss.severity === 'critical' ? 'issue-sev-critical'
        : iss.severity === 'high' ? 'issue-sev-high'
        : '';
      return `<div class="phase-drawer-issue-row">
        <span class="phase-drawer-issue-id">#${escapeHtml(String(iss.id || ''))}</span>
        <span class="phase-drawer-issue-title">${escapeHtml(iss.title || '')}</span>
        ${iss.severity ? `<span class="issue-badge ${severityCls}">${escapeHtml(iss.severity)}</span>` : ''}
      </div>`;
    }).join('');
    html += `<div class="phase-drawer-section">
      <div class="phase-drawer-section-label">Issues (${phaseIssues.length})</div>
      <div class="phase-drawer-issues">${issueRows}</div>
    </div>`;
  }

  return html;
}

// Lightweight Markdown → safe HTML for doc_body content.
// Handles: headings (## ###), bullets (- * •), bold (**), inline code (`).
// Everything is escaped before inline processing.
function _renderDocBodyHtml(text) {
  if (!text || !text.trim()) {
    return '<p class="phase-doc-body-empty">No content extracted from docs. Use <strong>Sync from docs</strong> after generating delivery documents.</p>';
  }
  const lines = text.split('\n');
  const out = [];
  let inList = false;

  for (let i = 0; i < lines.length; i++) {
    const raw = lines[i];
    const stripped = raw.trim();

    if (!stripped) {
      if (inList) { out.push('</ul>'); inList = false; }
      continue;
    }

    // Headings
    const hm = stripped.match(/^(#{2,4})\s+(.*)/);
    if (hm) {
      if (inList) { out.push('</ul>'); inList = false; }
      const level = Math.min(hm[1].length, 4);
      out.push(`<h${level}>${_inlineMarkdown(hm[2])}</h${level}>`);
      continue;
    }

    // Bullets: - * • or numbered 1.
    const bm = stripped.match(/^(?:[-*•]|\d+\.)\s+(.*)/);
    if (bm) {
      if (!inList) { out.push('<ul>'); inList = true; }
      out.push(`<li>${_inlineMarkdown(bm[1])}</li>`);
      continue;
    }

    // Normal paragraph line
    if (inList) { out.push('</ul>'); inList = false; }
    out.push(`<p>${_inlineMarkdown(stripped)}</p>`);
  }
  if (inList) out.push('</ul>');
  return out.join('');
}

// Process inline Markdown: bold, italic, code, escape HTML
function _inlineMarkdown(text) {
  let s = escapeHtml(text);
  s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  s = s.replace(/(?:\*|_)([^*_]+)(?:\*|_)/g, '<em>$1</em>');
  s = s.replace(/`([^`]+)`/g, '<code>$1</code>');
  return s;
}

// ── Phase status helpers ──────────────────────────────────────────────────────
function _phaseStatusCls(status) {
  return status === 'built'       ? 'phase-built'
    : status === 'merged'         ? 'phase-merged'
    : status === 'deployed'       ? 'phase-deployed'
    : status === 'in-progress'    ? 'phase-active'
    : 'phase-pending';
}

function _phaseStatusLabel(status, phase) {
  if (status === 'merged') {
    // If the phase was merged via an actual PR, say "Merged"; otherwise "Deployed"
    return (phase && phase.pr_url) ? 'Merged' : 'Deployed';
  }
  return status === 'built'       ? 'Built'
    : status === 'deployed'       ? 'Live'
    : status === 'in-progress'    ? 'In Progress'
    : 'Pending';
}

// Truncate long URLs to host + short path for card display
function _truncUrl(url) {
  try {
    const u = new URL(url);
    const path = u.pathname.length > 18 ? u.pathname.slice(0, 16) + '…' : u.pathname;
    return u.host + (path === '/' ? '' : path);
  } catch (_) { return url.slice(0, 32); }
}

// ── Deployment dialog ─────────────────────────────────────────────────────────
let _deployingPhaseId = null;

function openDeployDialog(phaseId) {
  _deployingPhaseId = phaseId;
  const phases = (state && state.phases) || [];
  const p = phases.find(x => x.id === phaseId);

  // Pre-fill if already deployed
  const urlInput = document.getElementById('deploy-url-input');
  const envSelect = document.getElementById('deploy-env-select');
  if (urlInput) urlInput.value = (p && p.deploy_url) || '';
  if (envSelect) envSelect.value = (p && p.deploy_env) || 'staging';

  const dlg = document.getElementById('deploy-dialog');
  if (dlg) {
    dlg.classList.remove('hidden');
    if (urlInput) setTimeout(() => urlInput.focus(), 50);
  }
}

function closeDeployDialog() {
  _deployingPhaseId = null;
  const dlg = document.getElementById('deploy-dialog');
  if (dlg) dlg.classList.add('hidden');
}

async function confirmDeployPhase() {
  const urlInput  = document.getElementById('deploy-url-input');
  const envSelect = document.getElementById('deploy-env-select');
  const url = (urlInput && urlInput.value.trim()) || '';
  const env = (envSelect && envSelect.value) || 'production';

  if (!url) {
    urlInput && urlInput.focus();
    showToast('Paste the live deployment URL to confirm', 'error');
    return;
  }

  const btn = document.getElementById('btn-confirm-deploy');
  if (btn) { btn.disabled = true; btn.textContent = 'Recording…'; }

  try {
    const res = await apiFetch('/api/phases', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'deploy', id: _deployingPhaseId, deploy_url: url, deploy_env: env })
    });
    const data = await res.json();
    if (data.status === 'ok') {
      showToast('Deployment recorded — phase is live ✓', 'success');
      closeDeployDialog();
      loadState();
    } else {
      showToast(data.error || 'Failed to record deployment', 'error');
    }
  } catch (e) {
    showToast('Failed to record deployment', 'error');
  } finally {
    if (btn) { btn.disabled = false; btn.innerHTML = `${icon('cloudUp',12)} Confirm Deployment`; }
  }
}

async function _autoSyncPhases() {
  try {
    const res = await apiFetch('/api/phases', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'sync' })
    });
    const data = await res.json();
    if (data.phases !== undefined) {
      state.phases = data.phases;
      renderPhases();
      showToast(`All files reviewed — ${data.phases.length} phase${data.phases.length !== 1 ? 's' : ''} synced from docs`, 'success');
    }
  } catch (e) { /* non-fatal — phases can be synced manually */ }
}

async function syncPhases() {
  const btn = document.getElementById('btn-sync-phases');
  if (btn) btn.disabled = true;
  try {
    const res = await apiFetch('/api/phases', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'sync' })
    });
    const data = await res.json();
    if (data.phases !== undefined) {
      state.phases = data.phases;
      renderPhases();
      showToast(`${data.phases.length} phase${data.phases.length !== 1 ? 's' : ''} synced`, 'success');
    } else {
      showToast(data.error || 'Sync failed', 'error');
    }
  } catch (e) {
    showToast('Sync failed', 'error');
  } finally {
    if (btn) btn.disabled = false;
  }
}

async function activatePhase(id) {
  try {
    const res = await apiFetch('/api/phases', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'activate', id })
    });
    const data = await res.json();
    if (data.status === 'ok') {
      showToast('Phase activated', 'success');
      loadState();
    } else {
      showToast(data.error || 'Cannot activate phase', 'error');
    }
  } catch (e) {
    showToast('Failed to activate phase', 'error');
  }
}

async function completePhase(id, force = false) {
  try {
    const res = await apiFetch('/api/phases', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'complete', id, ...(force ? { force: true } : {}) })
    });
    const data = await res.json();
    if (data.status === 'ok') {
      showToast('Phase marked as built', 'success');
      loadState();
    } else if (data.incomplete_steps && !force) {
      const steps = data.incomplete_steps.join(', ');
      if (confirm(`Build steps not complete for this phase: ${steps}.\n\nMark built anyway?`)) {
        completePhase(id, true);
      }
    } else {
      showToast(data.error || 'Failed', 'error');
    }
  } catch (e) {
    showToast('Failed to update phase', 'error');
  }
}

async function deployPhase(id) {
  try {
    const res = await apiFetch('/api/phases', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'deploy', id })
    });
    const data = await res.json();
    if (data.status === 'ok') {
      showToast('Phase marked as deployed', 'success');
      loadState();
    } else {
      showToast(data.error || 'Failed to mark deployed', 'error');
    }
  } catch (e) {
    showToast('Failed to deploy phase', 'error');
  }
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
    document.getElementById('viewer-content').innerHTML = VIEWER_DEFAULT_HTML;
    document.getElementById('viewer-raw-pre').textContent = '';
    document.getElementById('viewer-filename').innerHTML = '<span style="font-size:12px;color:var(--text-3);">Select a document to review</span>';
    document.getElementById('btn-review-toggle').style.display = 'none';
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

// Set initial viewer empty state on load
const _vc = document.getElementById('viewer-content');
if (_vc && !_vc.innerHTML.trim()) _vc.innerHTML = VIEWER_DEFAULT_HTML;

startPolling();

// ============================================================
// Electron update banner (Forge OS desktop only)
// ============================================================
function updateBannerInstall() {
  if (window.forgeElectron) window.forgeElectron.installUpdate();
}
function updateBannerDismiss() {
  const el = document.getElementById('update-banner');
  if (el) el.style.display = 'none';
  if (window.forgeElectron) window.forgeElectron.dismissUpdate();
}

if (window.forgeElectron) {
  window.forgeElectron.onUpdateReady(({ version }) => {
    const banner = document.getElementById('update-banner');
    const verEl  = document.getElementById('update-banner-version');
    if (!banner) return;
    if (verEl) verEl.textContent = version;
    banner.style.display = 'flex';
  });
  window.forgeElectron.onUpdateCleared(() => {
    const banner = document.getElementById('update-banner');
    if (banner) banner.style.display = 'none';
  });
}
