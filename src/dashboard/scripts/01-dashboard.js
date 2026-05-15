function parseMarkdown(src) {
  var e = function(s) {
    return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  };
  var inline = function(s) {
    s = e(s);
    s = s.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');
    s = s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    s = s.replace(/__(.+?)__/g, '<strong>$1</strong>');
    s = s.replace(/\*([^*\n]+?)\*/g, '<em>$1</em>');
    s = s.replace(/_([^_\n]+?)_/g, '<em>$1</em>');
    s = s.replace(/~~(.+?)~~/g, '<del>$1</del>');
    s = s.replace(/`([^`]+)`/g, '<code>$1</code>');
    s = s.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
    return s;
  };
  var lines = src.replace(/\r\n/g, '\n').split('\n');
  var out = '';
  var i = 0;
  var inCode = false, codeLang = '', codeLines = [];
  var inUL = false, inOL = false;
  var para = [];

  function flushPara() {
    if (para.length) { out += '<p>' + inline(para.join(' ')) + '</p>\n'; para = []; }
  }
  function closeList() {
    if (inUL) { out += '</ul>\n'; inUL = false; }
    if (inOL) { out += '</ol>\n'; inOL = false; }
  }

  while (i < lines.length) {
    var line = lines[i]; i++;

    // fenced code block
    if (/^`{3}/.test(line)) {
      if (!inCode) {
        flushPara(); closeList();
        codeLang = line.slice(3).trim() || 'code';
        codeLines = []; inCode = true;
      } else {
        var codeHtml = e(codeLines.join('\n'));
        out += '<div class="md-code-block"><div class="md-code-header"><span class="md-code-lang">' + e(codeLang) + '</span></div><pre class="md-code-pre"><code>' + codeHtml + '</code></pre></div>\n';
        inCode = false;
      }
      continue;
    }
    if (inCode) { codeLines.push(line); continue; }

    // heading
    var hm = line.match(/^(#{1,6})\s+(.*)/);
    if (hm) {
      flushPara(); closeList();
      var hl = hm[1].length;
      out += '<h' + hl + '>' + inline(hm[2].trim()) + '</h' + hl + '>\n';
      continue;
    }

    // hr
    if (/^(\*{3,}|-{3,}|_{3,})\s*$/.test(line)) {
      flushPara(); closeList();
      out += '<hr>\n'; continue;
    }

    // blockquote
    if (/^>\s/.test(line)) {
      flushPara(); closeList();
      out += '<blockquote><p>' + inline(line.replace(/^>\s*/, '')) + '</p></blockquote>\n';
      continue;
    }

    // unordered list
    var ulm = line.match(/^[ \t]*[-*+]\s+(.*)/);
    if (ulm) {
      flushPara();
      if (inOL) { out += '</ol>\n'; inOL = false; }
      if (!inUL) { out += '<ul>\n'; inUL = true; }
      out += '<li>' + inline(ulm[1]) + '</li>\n';
      continue;
    }

    // ordered list
    var olm = line.match(/^\d+\.\s+(.*)/);
    if (olm) {
      flushPara();
      if (inUL) { out += '</ul>\n'; inUL = false; }
      if (!inOL) { out += '<ol>\n'; inOL = true; }
      out += '<li>' + inline(olm[1]) + '</li>\n';
      continue;
    }

    // table row
    if (/^\|/.test(line)) {
      flushPara(); closeList();
      // separator row — skip
      if (/^\|[\s:|:-]+\|/.test(line)) { continue; }
      var cells = line.replace(/^\||\|$/g, '').split('|');
      // peek back — if previous output ended with </thead> we're in body, else header
      var tag = out.endsWith('</thead>\n') ? 'td' : 'th';
      if (tag === 'th' && !out.endsWith('</table>\n')) {
        out += '<table>\n<thead>\n';
      } else if (tag === 'td' && out.endsWith('</thead>\n')) {
        out += '<tbody>\n';
      }
      out += '<tr>' + cells.map(function(c) { return '<' + tag + '>' + inline(c.trim()) + '</' + tag + '>'; }).join('') + '</tr>\n';
      if (tag === 'th') out += '</thead>\n';
      continue;
    }
    // close table
    if (out.includes('<tbody>') && !out.endsWith('</table>\n') && line.trim() === '') {
      out += '</tbody></table>\n';
    }

    // blank line
    if (line.trim() === '') {
      flushPara(); closeList(); continue;
    }

    // paragraph accumulation
    closeList();
    para.push(line.trim());
  }

  flushPara(); closeList();
  if (inCode) {
    out += '<pre class="md-code-pre"><code>' + e(codeLines.join('\n')) + '</code></pre>\n';
  }
  return out;
}
