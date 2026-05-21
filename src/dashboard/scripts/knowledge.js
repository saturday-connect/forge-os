// ============================================================
// Knowledge Base view
// ============================================================

// Thin wrapper: knowledge.js uses api(url, method, body) → Promise<parsed JSON>
// The rest of the app exposes apiFetch(url, options) → Promise<Response>.
function api(url, method, body) {
  var opts = { method: method || 'GET' };
  if (body !== undefined) {
    opts.headers = { 'Content-Type': 'application/json' };
    opts.body = JSON.stringify(body);
  }
  return apiFetch(url, opts).then(function(r) { return r.json(); });
}

var _kbState = null;
var _kbPolling = null;

function renderKnowledge() {
  api('/api/knowledge').then(function(d) {
    _kbState = d;
    _renderKBConfigure(d);
    _renderKBPipeline(d);
    _renderKBActivity(d);
    _startKBPoll();
  }).catch(function(e) {
    var el = document.getElementById('kb-view-body');
    if (el) el.innerHTML = '<div class="kb-error">Failed to load knowledge base status: ' + escapeHtml(String(e)) + '</div>';
  });
}

function refreshKnowledge() {
  renderKnowledge();
}

function _startKBPoll() {
  if (_kbPolling) return;
  var busy = _kbIsBusy(_kbState);
  if (!busy) return;
  _kbPolling = setInterval(function() {
    api('/api/knowledge').then(function(d) {
      _kbState = d;
      _renderKBPipeline(d);
      _renderKBActivity(d);
      if (!_kbIsBusy(d)) {
        clearInterval(_kbPolling);
        _kbPolling = null;
      }
    }).catch(function() {});
  }, 3000);
}

function _kbIsBusy(d) {
  if (!d) return false;
  var st = d.status || {};
  var exports = (st.exports || []);
  var distills = (st.distillations || []);
  return exports.some(function(e) { return e.status === 'exporting'; }) ||
         distills.some(function(e) { return e.status === 'distilling'; });
}

function _renderKBConfigure(d) {
  var el = document.getElementById('kb-configure-section');
  if (!el) return;
  var cfg = d.config || {};
  var repoOwner = cfg.repo_owner || '';
  var repoName  = cfg.repo_name  || '';
  var branch    = cfg.branch     || 'main';
  var configured = !!(repoOwner && repoName);
  el.innerHTML = [
    '<div class="kb-section">',
    '  <div class="kb-section-title">Repository Configuration</div>',
    '  <div class="kb-config-row">',
    '    <div class="kb-config-field">',
    '      <label class="kb-label">Owner / Org</label>',
    '      <input class="input" id="kb-repo-owner" type="text" placeholder="saturday-connect" value="' + escapeHtml(repoOwner) + '">',
    '    </div>',
    '    <div class="kb-config-field">',
    '      <label class="kb-label">Repository</label>',
    '      <input class="input" id="kb-repo-name" type="text" placeholder="forge-knowledge" value="' + escapeHtml(repoName) + '">',
    '    </div>',
    '    <div class="kb-config-field" style="max-width:140px">',
    '      <label class="kb-label">Default Branch</label>',
    '      <input class="input" id="kb-branch" type="text" placeholder="main" value="' + escapeHtml(branch) + '">',
    '    </div>',
    '    <div class="kb-config-field kb-config-btn-col">',
    '      <label class="kb-label">&nbsp;</label>',
    '      <button class="btn btn-primary btn-sm" onclick="saveKBConfig()">' + icon('check', 12) + ' Save</button>',
    '    </div>',
    '  </div>',
    configured ? (
      '  <div class="kb-config-status">' + icon('check', 12) +
      ' <a href="https://github.com/' + escapeHtml(repoOwner) + '/' + escapeHtml(repoName) + '" target="_blank">' +
      escapeHtml(repoOwner) + '/' + escapeHtml(repoName) + '</a></div>'
    ) : '  <div class="kb-config-status kb-config-status--warn">' + icon('alert', 12) + ' Not configured — enter repo details above</div>',
    '</div>',
  ].join('\n');
}

function saveKBConfig() {
  var owner  = (document.getElementById('kb-repo-owner') || {}).value || '';
  var name   = (document.getElementById('kb-repo-name')  || {}).value || '';
  var branch = (document.getElementById('kb-branch')     || {}).value || 'main';
  if (!owner.trim() || !name.trim()) { showToast('Owner and repository name are required', 'error'); return; }
  api('/api/knowledge/configure', 'POST', { repo_owner: owner.trim(), repo_name: name.trim(), branch: branch.trim() })
    .then(function() { showToast('Knowledge base configured', 'success'); renderKnowledge(); })
    .catch(function(e) { showToast('Save failed: ' + e.message, 'error'); });
}

function _renderKBPipeline(d) {
  var el = document.getElementById('kb-pipeline-section');
  if (!el) return;
  var cfg = d.config || {};
  var configured = !!(cfg.repo_owner && cfg.repo_name);
  var docCount = d.reviewed_doc_count || 0;
  var docs = d.reviewed_docs || [];
  var st = d.status || {};
  var exports = st.exports || [];
  var distills = st.distillations || [];
  var exporting  = exports.some(function(e) { return e.status === 'exporting'; });
  var distilling = distills.some(function(e) { return e.status === 'distilling'; });
  var cfg2 = _kbState && _kbState.config ? _kbState.config : {};
  var ref = cfg2.ref || '';
  var lastSynced = cfg2.last_synced || '';

  // Group docs by stage prefix
  var byStage = {};
  docs.forEach(function(doc) {
    var parts = doc.rel.split('/');
    var stage = parts[0] || 'other';
    byStage[stage] = byStage[stage] || [];
    byStage[stage].push(doc);
  });
  var docListHtml = '';
  if (docs.length > 0) {
    docListHtml = Object.keys(byStage).sort().map(function(stage) {
      var stageDocs = byStage[stage];
      return '<div class="kb-stage-group">' +
        '<div class="kb-stage-label">' + escapeHtml(stage) + '</div>' +
        stageDocs.map(function(doc) {
          var fname = doc.rel.split('/').pop();
          return '<div class="kb-doc-item">' + icon('file', 11) + ' ' + escapeHtml(fname) + '</div>';
        }).join('') +
        '</div>';
    }).join('');
  }

  el.innerHTML = [
    '<div class="kb-pipeline-grid">',

    // Export card
    '<div class="kb-card">',
    '  <div class="kb-card-header">',
    '    <div class="kb-card-title">' + icon('upload', 14) + ' Export Project Docs</div>',
    '    <div class="kb-card-badge ' + (docCount > 0 ? 'kb-badge-green' : 'kb-badge-dim') + '">' + docCount + ' reviewed</div>',
    '  </div>',
    '  <div class="kb-card-desc">Push reviewed documents to <code>projects/&lt;slug&gt;/</code> in the KB repo and open a PR for project-owner review.</div>',
    docCount > 0 ? ('<div class="kb-doc-list">' + docListHtml + '</div>') : '',
    '  <div class="kb-card-footer">',
    '    <button class="btn btn-primary btn-sm" id="btn-kb-export" onclick="exportToKB()" ' +
      (!configured || docCount === 0 || exporting ? 'disabled' : '') + '>',
    exporting ? (icon('spinner', 12) + ' Exporting…') : (icon('upload', 12) + ' Export to KB'),
    '    </button>',
    !configured ? '<span class="kb-card-hint">Configure KB repo first</span>' :
      docCount === 0 ? '<span class="kb-card-hint">No reviewed docs yet — review documents first</span>' : '',
    '  </div>',
    '</div>',

    // Distill card
    '<div class="kb-card">',
    '  <div class="kb-card-header">',
    '    <div class="kb-card-title">' + icon('sparkles', 14) + ' Distill Global Learnings</div>',
    '    <div class="kb-card-badge ' + (docCount > 0 ? 'kb-badge-purple' : 'kb-badge-dim') + '">AI</div>',
    '  </div>',
    '  <div class="kb-card-desc">AI extracts reusable patterns, decisions, and learnings from reviewed docs and opens a <strong>draft PR</strong> to <code>global/</code> for curator review.</div>',
    '  <div class="kb-distill-targets">',
    '    <div class="kb-distill-target"><code>global/patterns/</code><span>Reusable architecture patterns</span></div>',
    '    <div class="kb-distill-target"><code>global/decisions/</code><span>ADR-style decision records</span></div>',
    '    <div class="kb-distill-target"><code>global/learnings/</code><span>Cross-project failure modes</span></div>',
    '  </div>',
    '  <div class="kb-card-footer">',
    '    <button class="btn btn-secondary btn-sm" id="btn-kb-distill" onclick="distillToKB()" ' +
      (!configured || docCount === 0 || distilling ? 'disabled' : '') + '>',
    distilling ? (icon('spinner', 12) + ' Distilling…') : (icon('sparkles', 12) + ' Distill & Propose PR'),
    '    </button>',
    !configured ? '<span class="kb-card-hint">Configure KB repo first</span>' :
      docCount === 0 ? '<span class="kb-card-hint">No reviewed docs yet</span>' : '',
    '  </div>',
    '</div>',

    // Sync card
    '<div class="kb-card">',
    '  <div class="kb-card-header">',
    '    <div class="kb-card-title">' + icon('pin', 14) + ' Pinned Knowledge Ref</div>',
    ref ? '<div class="kb-card-badge kb-badge-dim"><code>' + escapeHtml(ref.slice(0, 7)) + '</code></div>' : '',
    '  </div>',
    '  <div class="kb-card-desc">Pin a specific KB commit SHA so generation uses a stable, auditable knowledge snapshot. Bump explicitly when you want new knowledge to take effect.</div>',
    '  <div class="kb-sync-row">',
    '    <input class="input" id="kb-ref-input" type="text" placeholder="Commit SHA (e.g. a3f8c12)" value="' + escapeHtml(ref) + '" style="font-family:var(--mono);font-size:12px;">',
    '    <button class="btn btn-ghost btn-sm" onclick="syncKBRef()">' + icon('check', 12) + ' Pin Ref</button>',
    '  </div>',
    lastSynced ? '<div class="kb-sync-hint">Last synced: ' + new Date(lastSynced).toLocaleString() + '</div>' : '',
    '</div>',

    '</div>',
  ].join('\n');
}

function exportToKB() {
  var btn = document.getElementById('btn-kb-export');
  if (btn) { btn.disabled = true; btn.innerHTML = icon('spinner', 12) + ' Exporting…'; }
  api('/api/knowledge/export', 'POST', {})
    .then(function(d) {
      showToast('Export started — ' + (d.doc_count || 0) + ' docs', 'success');
      _kbPolling = null;
      setTimeout(function() { renderKnowledge(); }, 1500);
    })
    .catch(function(e) {
      showToast('Export failed: ' + e.message, 'error');
      renderKnowledge();
    });
}

function distillToKB() {
  var btn = document.getElementById('btn-kb-distill');
  if (btn) { btn.disabled = true; btn.innerHTML = icon('spinner', 12) + ' Distilling…'; }
  api('/api/knowledge/distill', 'POST', {})
    .then(function(d) {
      showToast('Distillation started — ' + (d.doc_count || 0) + ' docs being analysed', 'success');
      _kbPolling = null;
      setTimeout(function() { renderKnowledge(); }, 1500);
    })
    .catch(function(e) {
      showToast('Distillation failed: ' + e.message, 'error');
      renderKnowledge();
    });
}

function syncKBRef() {
  var ref = (document.getElementById('kb-ref-input') || {}).value || '';
  if (!ref.trim()) { showToast('Enter a commit SHA', 'error'); return; }
  api('/api/knowledge/sync', 'POST', { ref: ref.trim() })
    .then(function() { showToast('Knowledge ref pinned to ' + ref.slice(0, 7), 'success'); renderKnowledge(); })
    .catch(function(e) { showToast('Sync failed: ' + e.message, 'error'); });
}

function _renderKBActivity(d) {
  var el = document.getElementById('kb-activity-section');
  if (!el) return;
  var st = d.status || {};
  var exports = (st.exports || []).slice(0, 5);
  var distills = (st.distillations || []).slice(0, 5);
  if (!exports.length && !distills.length) {
    el.innerHTML = '';
    return;
  }
  var rows = [];
  exports.forEach(function(e) {
    rows.push({ type: 'export', id: e.id, status: e.status, doc_count: e.doc_count,
                pr_url: e.pr_url, error: e.error, created_at: e.created_at });
  });
  distills.forEach(function(e) {
    rows.push({ type: 'distill', id: e.id, status: e.status, doc_count: e.doc_count,
                pr_url: e.pr_url, error: e.error, created_at: e.created_at });
  });
  rows.sort(function(a, b) { return b.id.localeCompare(a.id); });
  rows = rows.slice(0, 8);

  el.innerHTML = [
    '<div class="kb-section">',
    '  <div class="kb-section-title">Activity</div>',
    '  <div class="kb-activity-list">',
    rows.map(function(r) {
      var statusCls = r.status === 'done' ? 'kb-activity-status--done'
        : r.status === 'error' ? 'kb-activity-status--error'
        : 'kb-activity-status--busy';
      var statusLabel = r.status === 'done' ? 'Done'
        : r.status === 'error' ? 'Error'
        : r.status === 'exporting' ? 'Exporting…'
        : r.status === 'distilling' ? 'Distilling…'
        : r.status;
      var typeLabel = r.type === 'export' ? 'Export' : 'Distill';
      var typeIcon = r.type === 'export' ? icon('upload', 11) : icon('sparkles', 11);
      var ts = r.created_at ? new Date(r.created_at).toLocaleString() : r.id;
      return [
        '<div class="kb-activity-row">',
        '  <span class="kb-activity-type">' + typeIcon + ' ' + typeLabel + '</span>',
        '  <span class="kb-activity-ts">' + ts + '</span>',
        '  <span class="kb-activity-docs">' + (r.doc_count || 0) + ' docs</span>',
        '  <span class="kb-activity-status ' + statusCls + '">' + statusLabel + '</span>',
        r.pr_url ? '  <a class="kb-activity-pr" href="' + escapeHtml(r.pr_url) + '" target="_blank">' + icon('link', 11) + ' PR</a>' : '',
        r.error ? '  <span class="kb-activity-error" title="' + escapeHtml(r.error) + '">' + icon('alert', 11) + ' ' + escapeHtml(r.error.slice(0, 60)) + '</span>' : '',
        '</div>',
      ].join('');
    }).join(''),
    '  </div>',
    '</div>',
  ].join('\n');
}

// icon() helper used inline — reuse the one from app.js (already global)
