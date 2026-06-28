#!/usr/bin/env python3
import http.server
import os
import subprocess
import urllib.parse
from datetime import date, timedelta
from pathlib import Path

BLOG_DIR  = Path(__file__).parent
CONTENT   = BLOG_DIR / "content"
POSTS_DIR = CONTENT / "posts"
PORT = 5000

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: #0d1117; color: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
a { color: #58a6ff; text-decoration: none; }
a:hover { text-decoration: underline; }

.topbar {
    background: #161b22; border-bottom: 1px solid #30363d;
    padding: 12px 24px; display: flex; align-items: center; justify-content: space-between;
}
.topbar .logo { font-size: 16px; font-weight: 600; color: #f0f6fc; letter-spacing: 1px; }
.topbar .logo span { color: #58a6ff; }
.topbar-nav { display: flex; gap: 8px; align-items: center; }

.container { max-width: 1020px; margin: 0 auto; padding: 32px 24px; }
h1 { font-size: 22px; color: #f0f6fc; margin-bottom: 24px; }
h2 { font-size: 15px; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; margin: 28px 0 12px; }

.btn {
    display: inline-block; padding: 7px 16px; border-radius: 6px;
    font-size: 13px; font-weight: 500; cursor: pointer; border: none; transition: opacity .15s;
}
.btn:hover { opacity: .82; }
.btn-primary { background: #238636; color: #fff; }
.btn-blue    { background: #1f6feb; color: #fff; }
.btn-gray    { background: #21262d; color: #c9d1d9; border: 1px solid #30363d; }
.btn-red     { background: #6e1313; color: #fca5a5; border: 1px solid #b91c1c; }

.list { list-style: none; }
.list li {
    display: flex; align-items: center; justify-content: space-between;
    padding: 13px 16px; border: 1px solid #30363d; border-radius: 8px;
    margin-bottom: 8px; background: #161b22; transition: border-color .15s;
}
.list li:hover { border-color: #58a6ff33; }
.list .title  { font-size: 14px; color: #f0f6fc; }
.list .meta   { font-size: 12px; color: #8b949e; margin-top: 3px; }
.list .acts   { display: flex; gap: 6px; flex-shrink: 0; }

.tag { display: inline-block; background: #1f6feb18; color: #58a6ff;
       border: 1px solid #1f6feb33; padding: 1px 7px; border-radius: 20px;
       font-size: 11px; margin-right: 3px; }
.tag-draft { background: #e3b34118; color: #e3b341; border-color: #e3b34133; }

.form-group { margin-bottom: 16px; }
label { display: block; font-size: 12px; color: #8b949e; margin-bottom: 5px; font-weight: 600; text-transform: uppercase; letter-spacing: .5px; }
input[type=text], input[type=date], textarea {
    width: 100%; background: #010409; border: 1px solid #30363d; border-radius: 6px;
    color: #c9d1d9; padding: 9px 12px; font-size: 14px; font-family: inherit;
    outline: none; transition: border-color .15s;
}
input:focus, textarea:focus { border-color: #58a6ff; }

.row2 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.row3 { display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 14px; }

.editor-wrap { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.editor-wrap textarea {
    height: 460px; resize: none;
    font-family: 'Courier New', monospace; font-size: 13px; line-height: 1.65;
}
.preview-box {
    background: #010409; border: 1px solid #30363d; border-radius: 6px;
    padding: 14px 16px; height: 460px; overflow-y: auto;
    font-size: 14px; line-height: 1.75;
}
.preview-box h1,.preview-box h2,.preview-box h3 { color: #f0f6fc; margin: 14px 0 6px; }
.preview-box p { margin-bottom: 10px; }
.preview-box code { background: #21262d; padding: 2px 6px; border-radius: 4px; font-size: 12px; font-family: monospace; }
.preview-box pre { background: #21262d; padding: 12px; border-radius: 6px; overflow-x: auto; margin: 10px 0; }
.preview-box pre code { background: none; padding: 0; }
.preview-box a { color: #58a6ff; }
.preview-box ul { padding-left: 20px; margin-bottom: 10px; }
.preview-box table { border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 13px; }
.preview-box th, .preview-box td { border: 1px solid #30363d; padding: 6px 10px; }
.preview-box th { background: #21262d; }
.preview-box blockquote { border-left: 3px solid #30363d; padding-left: 12px; color: #8b949e; margin: 10px 0; }

.toolbar { display: flex; gap: 5px; margin-bottom: 6px; flex-wrap: wrap; }
.toolbar button {
    background: #21262d; border: 1px solid #30363d; color: #c9d1d9;
    padding: 4px 10px; border-radius: 4px; font-size: 12px; cursor: pointer;
}
.toolbar button:hover { background: #30363d; }

.pane-label { font-size: 11px; color: #8b949e; margin-bottom: 5px; text-transform: uppercase; letter-spacing: .5px; }

.actions-bar {
    display: flex; gap: 10px; margin-top: 22px;
    padding-top: 20px; border-top: 1px solid #30363d; align-items: center;
}
.actions-bar .spacer { flex: 1; }

.flash { padding: 11px 16px; border-radius: 6px; margin-bottom: 20px; font-size: 13px; }
.flash.ok  { background: #0d4429; border: 1px solid #238636; color: #3fb950; }
.flash.err { background: #4a0d0d; border: 1px solid #b91c1c; color: #f85149; }

.page-editor textarea {
    height: 560px; font-family: 'Courier New', monospace; font-size: 13px;
    line-height: 1.65; resize: none;
}
"""

JS = r"""
function mdPreview(src) {
    let s = src
        .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
        .replace(/```[\w]*\n?([\s\S]*?)```/g, (_, c) => `<pre><code>${c.trim()}</code></pre>`)
        .replace(/`([^`\n]+)`/g, '<code>$1</code>')
        .replace(/^#{4} (.+)$/gm, '<h4>$1</h4>')
        .replace(/^#{3} (.+)$/gm, '<h3>$1</h3>')
        .replace(/^#{2} (.+)$/gm, '<h2>$1</h2>')
        .replace(/^# (.+)$/gm,   '<h1>$1</h1>')
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>')
        .replace(/^&gt; (.+)$/gm, '<blockquote>$1</blockquote>')
        .replace(/^\| (.+)$/gm, (_, row) => {
            if (row.replace(/[-| ]/g,'').trim() === '') return '';
            const cells = row.split(' | ').map(c => `<td>${c.trim()}</td>`).join('');
            return `<tr>${cells}</tr>`;
        })
        .replace(/(<tr>[\s\S]*?<\/tr>(\n|$))+/g, m => `<table>${m}</table>`)
        .replace(/^[-*] (.+)$/gm, '<li>$1</li>')
        .replace(/(<li>[\s\S]*?<\/li>(\n|$))+/g, m => `<ul>${m}</ul>`)
        .replace(/\n{2,}/g, '\n</p><p>\n')
        ;
    return '<p>' + s + '</p>';
}

function updatePreview() {
    const el = document.getElementById('content');
    const pr = document.getElementById('preview');
    if (el && pr) pr.innerHTML = mdPreview(el.value);
}

function insert(before, after, placeholder) {
    const ta = document.getElementById('content');
    const s = ta.selectionStart, e = ta.selectionEnd;
    const sel = ta.value.substring(s, e) || placeholder || 'text';
    ta.value = ta.value.substring(0, s) + before + sel + after + ta.value.substring(e);
    const pos = s + before.length + sel.length + after.length;
    ta.setSelectionRange(pos, pos);
    ta.focus();
    updatePreview();
}

document.addEventListener('DOMContentLoaded', updatePreview);
"""

def shell(cmd):
    env = {**os.environ, "GIT_SSH_COMMAND": "ssh -o StrictHostKeyChecking=no",
           "PATH": str(Path.home() / "bin") + ":" + os.environ.get("PATH", "")}
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env, cwd=str(BLOG_DIR))
    return r.returncode == 0, (r.stdout + r.stderr).strip()

def git_push(msg):
    return shell(f'git add content/ && git commit -m "{msg}" && git push')

def read_frontmatter(path):
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    meta, body, fm = {}, [], 0
    for line in lines:
        if line.strip() == "---":
            fm += 1
            continue
        if fm < 2:
            if ":" in line:
                k, _, v = line.partition(":")
                meta[k.strip()] = v.strip().strip('"')
        else:
            body.append(line)
    return meta, "\n".join(body).strip()

def list_pages():
    pages = []
    for f in sorted(CONTENT.glob("*.md"), key=lambda x: x.name):
        meta, _ = read_frontmatter(f)
        pages.append({"file": f.name, "path": str(f.relative_to(CONTENT)),
                      "title": meta.get("title", f.stem)})
    return pages

def list_posts():
    posts = []
    for f in sorted(POSTS_DIR.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True):
        meta, _ = read_frontmatter(f)
        posts.append({"file": f.name, "title": meta.get("title", f.stem),
                      "date": meta.get("date",""), "tags": meta.get("tags",""),
                      "draft": meta.get("draft","false")})
    return posts

def wrap(title, body, flash=None, active="posts"):
    fhtml = ""
    if flash:
        cls = "ok" if flash[0] == "ok" else "err"
        fhtml = f'<div class="flash {cls}">{flash[1]}</div>'
    nav_posts = "btn btn-primary" if active == "posts" else "btn btn-gray"
    nav_pages = "btn btn-primary" if active == "pages" else "btn btn-gray"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — TruePositive CMS</title>
<style>{CSS}</style>
</head>
<body>
<div class="topbar">
  <div class="logo">~/<span>truepositive</span> cms</div>
  <div class="topbar-nav">
    <a href="/" class="{nav_posts}">Posts</a>
    <a href="/pages" class="{nav_pages}">Pages</a>
  </div>
</div>
<div class="container">
{fhtml}
{body}
</div>
<script>{JS}</script>
</body>
</html>"""

def index_page(flash=None):
    posts = list_posts()
    rows = ""
    for p in posts:
        tags = ""
        for t in p["tags"].strip("[]").replace('"','').split(","):
            t = t.strip()
            if t: tags += f'<span class="tag">{t}</span>'
        draft = '<span class="tag tag-draft">draft</span>' if p["draft"] == "true" else ""
        rows += f"""<li>
          <div>
            <div class="title">{p['title']} {draft}</div>
            <div class="meta">{p['date']} &nbsp; {tags}</div>
          </div>
          <div class="acts">
            <a href="/edit-post?file={p['file']}" class="btn btn-gray">Edit</a>
            <a href="/delete?file={p['file']}" class="btn btn-red"
               onclick="return confirm('Delete this post?')">Delete</a>
          </div>
        </li>"""
    if not rows:
        rows = '<li style="justify-content:center;color:#8b949e;border:none">No posts yet.</li>'
    body = f"""
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px">
      <h1>Posts</h1>
      <a href="/new-post" class="btn btn-primary">+ New Post</a>
    </div>
    <ul class="list">{rows}</ul>"""
    return wrap("Posts", body, flash, "posts")

def pages_page(flash=None):
    pages = list_pages()
    rows = ""
    for p in pages:
        rows += f"""<li>
          <div><div class="title">{p['title']}</div>
          <div class="meta">{p['path']}</div></div>
          <div class="acts">
            <a href="/edit-page?file={p['file']}" class="btn btn-gray">Edit</a>
          </div>
        </li>"""
    body = f"""
    <div style="margin-bottom:20px"><h1>Pages</h1></div>
    <ul class="list">{rows}</ul>"""
    return wrap("Pages", body, flash, "pages")

def post_form(meta=None, content="", filename="", flash=None):
    meta = meta or {}
    today = (date.today() - timedelta(days=1)).isoformat()
    title  = meta.get("title","").strip('"')
    tags   = meta.get("tags","").strip("[]").replace('"','')
    desc   = meta.get("description","").strip('"')
    dt     = meta.get("date", today)
    draft  = "checked" if meta.get("draft","false") == "true" else ""
    h      = "Edit Post" if filename else "New Post"
    fn     = f'<input type="hidden" name="filename" value="{filename}">' if filename else ""
    safe_content = content.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

    body = f"""
    <h1>{h}</h1>
    <form method="POST" action="/save-post">
      {fn}
      <div class="row3">
        <div class="form-group">
          <label>Title</label>
          <input type="text" name="title" value="{title}" placeholder="Post title" required>
        </div>
        <div class="form-group">
          <label>Date</label>
          <input type="date" name="date" value="{dt}">
        </div>
        <div class="form-group">
          <label>Tags</label>
          <input type="text" name="tags" value="{tags}" placeholder="cve, dfir">
        </div>
      </div>
      <div class="form-group">
        <label>Description</label>
        <input type="text" name="description" value="{desc}" placeholder="Short summary">
      </div>
      <div class="form-group">
        <label>Content</label>
        <div class="toolbar">
          <button type="button" onclick="insert('**','**')"><b>B</b></button>
          <button type="button" onclick="insert('*','*')"><i>I</i></button>
          <button type="button" onclick="insert('`','`','code')">code</button>
          <button type="button" onclick="insert('```\\n','\\n```','code block')">block</button>
          <button type="button" onclick="insert('## ','','Heading')">H2</button>
          <button type="button" onclick="insert('### ','','Heading')">H3</button>
          <button type="button" onclick="insert('- ','','item')">list</button>
          <button type="button" onclick="insert('[','](url)','link text')">link</button>
          <button type="button" onclick="insert('| Col1 | Col2 |\\n|---|---|\\n| ','| |\\n','val')">table</button>
          <button type="button" onclick="insert('> ','','quote')">quote</button>
        </div>
        <div class="editor-wrap">
          <div>
            <div class="pane-label">Markdown</div>
            <textarea id="content" name="content" oninput="updatePreview()">{safe_content}</textarea>
          </div>
          <div>
            <div class="pane-label">Preview</div>
            <div class="preview-box" id="preview"></div>
          </div>
        </div>
      </div>
      <div class="form-group" style="display:flex;align-items:center;gap:8px">
        <input type="checkbox" name="draft" id="draft" value="true" {draft} style="width:auto">
        <label for="draft" style="margin:0;cursor:pointer;text-transform:none;letter-spacing:0;font-size:13px">Save as draft</label>
      </div>
      <div class="actions-bar">
        <button type="submit" name="action" value="publish" class="btn btn-primary">Save &amp; Publish</button>
        <button type="submit" name="action" value="save"    class="btn btn-blue">Save Only</button>
        <div class="spacer"></div>
        <a href="/" class="btn btn-gray">Cancel</a>
      </div>
    </form>"""
    return wrap(h, body, flash, "posts")

def page_form(filename, flash=None):
    fpath = CONTENT / filename
    raw   = fpath.read_text(encoding="utf-8")
    safe  = raw.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
    body  = f"""
    <h1>Edit Page — {filename}</h1>
    <form method="POST" action="/save-page" class="page-editor">
      <input type="hidden" name="filename" value="{filename}">
      <div class="form-group">
        <label>Raw Content (frontmatter + markdown)</label>
        <div class="editor-wrap">
          <div>
            <div class="pane-label">Markdown</div>
            <textarea id="content" name="content" oninput="updatePreview()">{safe}</textarea>
          </div>
          <div>
            <div class="pane-label">Preview</div>
            <div class="preview-box" id="preview"></div>
          </div>
        </div>
      </div>
      <div class="actions-bar">
        <button type="submit" name="action" value="publish" class="btn btn-primary">Save &amp; Publish</button>
        <button type="submit" name="action" value="save"    class="btn btn-blue">Save Only</button>
        <div class="spacer"></div>
        <a href="/pages" class="btn btn-gray">Cancel</a>
      </div>
    </form>"""
    return wrap(f"Edit {filename}", body, flash, "pages")

def make_frontmatter(title, tags, desc, dt, draft):
    tag_list = ", ".join(f'"{t.strip()}"' for t in tags.split(",") if t.strip())
    return f'---\ntitle: "{title}"\ndate: {dt}\ndraft: {draft}\ntags: [{tag_list}]\ndescription: "{desc}"\n---\n'

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def respond(self, html, code=200):
        b = html.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", len(b))
        self.end_headers()
        self.wfile.write(b)

    def redir(self, url):
        self.send_response(302)
        self.send_header("Location", url)
        self.end_headers()

    def do_GET(self):
        p = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(p.query)
        path = p.path

        if path == "/":
            self.respond(index_page())
        elif path == "/pages":
            self.respond(pages_page())
        elif path == "/new-post":
            self.respond(post_form())
        elif path == "/edit-post":
            f = q.get("file",[""])[0]
            fp = POSTS_DIR / f
            if not fp.exists(): self.redir("/"); return
            meta, content = read_frontmatter(fp)
            self.respond(post_form(meta=meta, content=content, filename=f))
        elif path == "/edit-page":
            f = q.get("file",[""])[0]
            fp = CONTENT / f
            if not fp.exists(): self.redir("/pages"); return
            self.respond(page_form(f))
        elif path == "/delete":
            f = q.get("file",[""])[0]
            fp = POSTS_DIR / f
            if fp.exists():
                fp.unlink()
                ok, _ = git_push(f"delete: {f}")
                msg = ("ok", f"Deleted and published: {f}") if ok else ("err", f"Deleted locally: {f} (push failed)")
            else:
                msg = ("err", "File not found")
            self.respond(index_page(flash=msg))
        else:
            self.respond("<h1>404</h1>", 404)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body   = urllib.parse.parse_qs(self.rfile.read(length).decode(errors="replace"))
        def g(k, d=""): return body.get(k, [d])[0]

        path = urllib.parse.urlparse(self.path).path

        if path == "/save-post":
            title    = g("title")
            tags     = g("tags")
            desc     = g("description")
            dt       = g("date", (date.today() - timedelta(days=1)).isoformat())
            content  = g("content")
            draft    = g("draft", "false")
            action   = g("action", "save")
            filename = g("filename")

            if not filename:
                slug = "".join(c if c.isalnum() or c=="-" else "-"
                               for c in title.lower().replace(" ","-"))
                slug = slug.strip("-")
                filename = f"{slug}.md"

            fm = make_frontmatter(title, tags, desc, dt, draft)
            (POSTS_DIR / filename).write_text(fm + "\n" + content, encoding="utf-8")

            if action == "publish":
                verb = "update" if g("filename") else "add"
                ok, out = git_push(f"{verb}: {title}")
                if ok:
                    self.respond(index_page(flash=("ok", f"Published: {title}")))
                else:
                    meta, c = read_frontmatter(POSTS_DIR / filename)
                    self.respond(post_form(meta=meta, content=c, filename=filename,
                                          flash=("err", f"Saved locally — git push failed: {out}")))
            else:
                self.respond(index_page(flash=("ok", f"Saved locally: {filename}")))

        elif path == "/save-page":
            filename = g("filename")
            content  = g("content")
            action   = g("action", "save")
            (CONTENT / filename).write_text(content, encoding="utf-8")

            if action == "publish":
                ok, out = git_push(f"update: {filename}")
                if ok:
                    self.respond(pages_page(flash=("ok", f"Published: {filename}")))
                else:
                    self.respond(page_form(filename, flash=("err", f"Saved locally — git push failed: {out}")))
            else:
                self.respond(pages_page(flash=("ok", f"Saved locally: {filename}")))
        else:
            self.redir("/")

if __name__ == "__main__":
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n  TruePositive CMS  →  http://localhost:{PORT}\n")
    http.server.HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
