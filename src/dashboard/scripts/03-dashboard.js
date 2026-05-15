// Monaco Editor
let monacoLoaded = false;
let monacoEditor = null;
let cemCurrentStep = null;
let cemActiveFile = null;

const LANG_MAP = {
  py:'python', ts:'typescript', tsx:'typescript', js:'javascript', jsx:'javascript',
  json:'json', yaml:'yaml', yml:'yaml', md:'markdown', sh:'shell', bash:'shell',
  css:'css', html:'html', xml:'xml', sql:'sql', tf:'hcl', toml:'ini', ini:'ini',
  env:'ini', txt:'plaintext', dockerfile:'dockerfile', makefile:'makefile',
};
const FILE_ICONS = {
  py:'PY', ts:'TS', tsx:'TSX', js:'JS', jsx:'JSX', json:'{}', md:'MD',
  yml:'YML', yaml:'YML', sh:'SH', css:'CSS', html:'HTML', tf:'TF', sql:'SQL',
  dockerfile:'DOCKER', makefile:'MAKE',
};

function detectLang(name) {
  const base = name.split('/').pop().toLowerCase();
  if (base === 'dockerfile') return 'dockerfile';
  if (base === 'makefile') return 'makefile';
  if (base.startsWith('.env')) return 'ini';
  return LANG_MAP[base.split('.').pop()] || 'plaintext';
}

function fileIcon(name) {
  const ext = name.split('.').pop().toLowerCase();
  return FILE_ICONS[ext] || '·';
}

function ensureMonaco(cb) {
  if (monacoLoaded) { cb(); return; }
  require.config({ paths: { vs: 'https://cdn.jsdelivr.net/npm/monaco-editor@0.52.0/min/vs' } });
  require(['vs/editor/editor.main'], function() { monacoLoaded = true; cb(); });
}

function openCodeEditor(step) {
  cemCurrentStep = step;
  cemActiveFile = null;
  const modal = document.getElementById('code-editor-modal');
  modal.style.display = 'flex';
  document.getElementById('cem-step-label').textContent = BUILD_STEPS_META[step]?.label || step;
  renderCemTabs(step);
  renderCemTree(step);
  ensureMonaco(() => {
    if (!monacoEditor) {
      monacoEditor = monaco.editor.create(document.getElementById('cem-monaco-container'), {
        value: '', language: 'plaintext', theme: 'vs-dark', readOnly: true,
        fontSize: 13, lineHeight: 20, minimap: { enabled: true },
        scrollBeyondLastLine: false, wordWrap: 'off', automaticLayout: true,
        folding: true, renderLineHighlight: 'line', smoothScrolling: true,
      });
    }
    const files = (buildStepsState[step] || {}).files || [];
    if (files.length > 0) loadCemFile(step, files[0]);
  });
}

function closeCodeEditor() {
  document.getElementById('code-editor-modal').style.display = 'none';
}

function renderCemTabs(active) {
  document.getElementById('cem-step-tabs').innerHTML = Object.entries(BUILD_STEPS_META).map(([k, m]) => {
    const st = buildStepsState[k] || {};
    if (st.status !== 'complete') return '';
    const on = k === active;
    return `<button onclick="switchCemStep('${k}')" style="font-size:10px;padding:2px 8px;border-radius:3px;border:none;cursor:pointer;background:${on?'#007acc':'#3a3a3a'};color:${on?'#fff':'#ccc'};">${m.label}</button>`;
  }).join('');
}

function switchCemStep(step) {
  cemCurrentStep = step;
  cemActiveFile = null;
  document.getElementById('cem-step-label').textContent = BUILD_STEPS_META[step]?.label || step;
  renderCemTabs(step);
  renderCemTree(step);
  const files = (buildStepsState[step] || {}).files || [];
  if (files.length > 0) loadCemFile(step, files[0]);
}

function renderCemTree(step) {
  const files = (buildStepsState[step] || {}).files || [];
  const groups = {};
  files.forEach(f => {
    const parts = f.replace(/\\/g, '/').split('/');
    const dir = parts.length > 1 ? parts.slice(0, -1).join('/') : '';
    if (!groups[dir]) groups[dir] = [];
    groups[dir].push({ full: f, name: parts[parts.length - 1] });
  });
  document.getElementById('cem-file-tree').innerHTML = Object.entries(groups).map(([dir, items]) => {
    const hdr = dir ? `<div style="padding:5px 12px 2px;font-size:10px;color:#666;text-transform:uppercase;letter-spacing:.05em;">${dir}</div>` : '';
    return hdr + items.map(({ full, name }) => {
      const active = full === cemActiveFile;
      const indent = dir ? '20px' : '12px';
      return `<div onclick="loadCemFile('${step}','${full.replace(/\\/g,'\\\\').replace(/'/g,"\\'")}','${name.replace(/'/g,"\\'")}')"
        title="${full}"
        style="padding:4px 12px 4px ${indent};font-size:12px;cursor:pointer;display:flex;align-items:center;gap:6px;
          white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
          background:${active?'rgba(0,122,204,0.25)':'transparent'};
          color:${active?'#cce6ff':'#ccc'};
          border-left:2px solid ${active?'#007acc':'transparent'};"
        onmouseover="if(this.style.borderLeftColor!=='rgb(0, 122, 204)')this.style.background='rgba(255,255,255,0.05)'"
        onmouseout="if(this.style.borderLeftColor!=='rgb(0, 122, 204)')this.style.background='transparent'">
        <span style="font-size:10px;opacity:0.6;">${fileIcon(name)}</span>${name}
      </div>`;
    }).join('');
  }).join('');
}

async function loadCemFile(step, path, displayName) {
  cemActiveFile = path;
  renderCemTree(step);
  const name = displayName || path.split('/').pop();
  const lang = detectLang(name);
  document.getElementById('cem-file-label').textContent = name;
  document.getElementById('cem-lang-badge').textContent = lang;
  document.getElementById('cem-status-step').textContent = BUILD_STEPS_META[step]?.label || step;
  document.getElementById('cem-status-file').textContent = path;
  const loading = document.getElementById('cem-loading');
  loading.style.display = 'flex';
  try {
    const res = await fetch('/api/build-file?step=' + encodeURIComponent(step) + '&path=' + encodeURIComponent(path));
    const data = await res.json();
    const content = data.content || '';
    if (monacoEditor) {
      const old = monacoEditor.getModel();
      monacoEditor.setModel(monaco.editor.createModel(content, lang));
      if (old) old.dispose();
      monacoEditor.setScrollPosition({ scrollTop: 0, scrollLeft: 0 });
      document.getElementById('cem-status-lines').textContent = content.split('\n').length + ' lines';
    }
  } catch(e) {
    if (monacoEditor) {
      const old = monacoEditor.getModel();
      monacoEditor.setModel(monaco.editor.createModel('// Error loading file', 'plaintext'));
      if (old) old.dispose();
    }
  } finally {
    loading.style.display = 'none';
  }
}

// Override stub from renderBuild JS
function openBuildCodePanel(step) {
  fetchBuildSteps().then(() => openCodeEditor(step));
}
