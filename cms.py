#!/usr/bin/env python3
import os
import subprocess
from datetime import date, timedelta
from pathlib import Path
from flask import Flask, request, redirect, url_for, render_template_string

BLOG_DIR  = Path(__file__).parent
CONTENT   = BLOG_DIR / "content"
POSTS_DIR = CONTENT / "posts"

app = Flask(__name__)

# ── helpers ────────────────────────────────────────────────────────────────────

def shell(cmd):
    env = {**os.environ, "PATH": str(Path.home() / "bin") + ":" + os.environ.get("PATH", "")}
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env, cwd=str(BLOG_DIR))
    return r.returncode == 0, (r.stdout + r.stderr).strip()

def git_push(msg):
    return shell(f'git add content/ && git commit -m "{msg}" && git push')

def parse_md(path):
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    meta, body, fm = {}, [], 0
    for line in lines:
        if line.strip() == "---":
            fm += 1; continue
        if fm < 2:
            if ":" in line:
                k, _, v = line.partition(":")
                meta[k.strip()] = v.strip().strip('"')
        else:
            body.append(line)
    return meta, "\n".join(body).strip()

def make_fm(title, tags, desc, dt, draft):
    tl = ", ".join(f'"{t.strip()}"' for t in tags.split(",") if t.strip())
    return f'---\ntitle: "{title}"\ndate: {dt}\ndraft: {draft}\ntags: [{tl}]\ndescription: "{desc}"\n---\n'

def all_posts():
    out = []
    for f in sorted(POSTS_DIR.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True):
        m, _ = parse_md(f)
        out.append({"file": f.name, "title": m.get("title", f.stem),
                    "date": m.get("date",""), "tags": m.get("tags",""),
                    "draft": m.get("draft","false") == "true"})
    return out

def all_pages():
    out = []
    for f in sorted(CONTENT.glob("*.md"), key=lambda x: x.name):
        m, _ = parse_md(f)
        out.append({"file": f.name, "title": m.get("title", f.stem)})
    return out

# ── base template ───────────────────────────────────────────────────────────────

BASE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ title }} — TruePositive CMS</title>
<style>
:root {
  --bg:      #0d1117;
  --bg2:     #161b22;
  --bg3:     #21262d;
  --border:  #30363d;
  --text:    #c9d1d9;
  --muted:   #8b949e;
  --accent:  #58a6ff;
  --green:   #238636;
  --blue:    #1f6feb;
  --red:     #da3633;
  --yellow:  #e3b341;
  --white:   #f0f6fc;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; display: flex; min-height: 100vh; }

/* sidebar */
.sidebar {
  width: 220px; min-height: 100vh; background: var(--bg2);
  border-right: 1px solid var(--border); display: flex; flex-direction: column;
  position: fixed; top: 0; left: 0; bottom: 0;
}
.sidebar-logo {
  padding: 20px 18px 16px;
  border-bottom: 1px solid var(--border);
  font-size: 14px; font-weight: 700; color: var(--white); letter-spacing: .5px;
}
.sidebar-logo span { color: var(--accent); }
.sidebar-logo small { display: block; font-size: 10px; font-weight: 400; color: var(--muted); margin-top: 3px; letter-spacing: 1px; text-transform: uppercase; }
.nav { padding: 12px 10px; flex: 1; }
.nav-section { font-size: 10px; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; padding: 8px 8px 4px; }
.nav a {
  display: flex; align-items: center; gap: 9px; padding: 8px 10px;
  border-radius: 6px; font-size: 13px; color: var(--text); text-decoration: none;
  margin-bottom: 2px; transition: background .12s;
}
.nav a:hover { background: var(--bg3); color: var(--white); }
.nav a.active { background: var(--blue)22; color: var(--accent); font-weight: 500; }
.nav a svg { flex-shrink: 0; opacity: .7; }
.sidebar-footer { padding: 14px 18px; border-top: 1px solid var(--border); font-size: 11px; color: var(--muted); }
.sidebar-footer a { color: var(--accent); text-decoration: none; font-size: 11px; }

/* main */
.main { margin-left: 220px; flex: 1; display: flex; flex-direction: column; }
.topbar {
  background: var(--bg2); border-bottom: 1px solid var(--border);
  padding: 0 28px; height: 52px; display: flex; align-items: center; justify-content: space-between;
  position: sticky; top: 0; z-index: 10;
}
.topbar h1 { font-size: 16px; color: var(--white); font-weight: 600; }
.content { padding: 28px; }

/* buttons */
.btn { display: inline-flex; align-items: center; gap: 6px; padding: 7px 14px; border-radius: 6px; font-size: 13px; font-weight: 500; cursor: pointer; border: 1px solid transparent; text-decoration: none; transition: opacity .15s, background .15s; white-space: nowrap; }
.btn:hover { opacity: .85; }
.btn-primary { background: var(--green); color: #fff; border-color: #2ea04388; }
.btn-blue    { background: var(--blue);  color: #fff; }
.btn-gray    { background: var(--bg3);   color: var(--text); border-color: var(--border); }
.btn-danger  { background: transparent;  color: var(--red);  border-color: var(--red)66; }
.btn-danger:hover { background: var(--red)18; opacity: 1; }
.btn-sm { padding: 5px 11px; font-size: 12px; }

/* flash */
.flash { padding: 11px 16px; border-radius: 7px; margin-bottom: 20px; font-size: 13px; display: flex; align-items: center; gap: 8px; }
.flash-ok  { background: #0d442918; border: 1px solid var(--green)66; color: #3fb950; }
.flash-err { background: var(--red)18; border: 1px solid var(--red)66; color: #f85149; }

/* post list table */
.posts-table { width: 100%; border-collapse: collapse; }
.posts-table th { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: .5px; color: var(--muted); padding: 0 12px 10px; text-align: left; border-bottom: 1px solid var(--border); }
.posts-table td { padding: 13px 12px; border-bottom: 1px solid var(--border)88; vertical-align: middle; }
.posts-table tr:hover td { background: var(--bg2); }
.post-title { font-size: 14px; color: var(--white); font-weight: 500; }
.post-date  { font-size: 12px; color: var(--muted); }
.post-acts  { display: flex; gap: 6px; justify-content: flex-end; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 20px; font-size: 11px; font-weight: 500; }
.badge-tag   { background: var(--blue)18; color: var(--accent); border: 1px solid var(--blue)33; margin-right: 3px; }
.badge-draft { background: var(--yellow)18; color: var(--yellow); border: 1px solid var(--yellow)33; }
.badge-live  { background: var(--green)18; color: #3fb950; border: 1px solid var(--green)33; }

/* empty state */
.empty { text-align: center; padding: 60px 20px; color: var(--muted); }
.empty svg { opacity: .3; margin-bottom: 12px; }
.empty p { font-size: 14px; margin-bottom: 16px; }

/* pages grid */
.pages-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; }
.page-card {
  background: var(--bg2); border: 1px solid var(--border); border-radius: 8px;
  padding: 18px; display: flex; flex-direction: column; gap: 12px;
  transition: border-color .15s;
}
.page-card:hover { border-color: var(--accent)44; }
.page-card-title { font-size: 15px; color: var(--white); font-weight: 600; }
.page-card-file  { font-size: 11px; color: var(--muted); font-family: monospace; }

/* editor layout */
.editor-layout { display: flex; gap: 20px; align-items: flex-start; }
.editor-main { flex: 1; min-width: 0; }
.editor-sidebar {
  width: 260px; flex-shrink: 0; background: var(--bg2);
  border: 1px solid var(--border); border-radius: 8px; padding: 18px;
  position: sticky; top: 72px;
}
.editor-sidebar h3 { font-size: 12px; text-transform: uppercase; letter-spacing: .5px; color: var(--muted); margin-bottom: 14px; }
.field { margin-bottom: 14px; }
.field label { display: block; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: .5px; color: var(--muted); margin-bottom: 5px; }
.field input, .field textarea {
  width: 100%; background: var(--bg); border: 1px solid var(--border);
  border-radius: 6px; color: var(--text); padding: 8px 10px;
  font-size: 13px; font-family: inherit; outline: none; transition: border-color .15s;
}
.field input:focus, .field textarea:focus { border-color: var(--accent); }
.toggle-wrap { display: flex; align-items: center; gap: 8px; padding: 8px 0; }
.toggle-wrap label { font-size: 13px; color: var(--text); cursor: pointer; margin: 0; text-transform: none; letter-spacing: 0; font-weight: 400; }
.sidebar-actions { display: flex; flex-direction: column; gap: 8px; padding-top: 14px; border-top: 1px solid var(--border); margin-top: 14px; }

/* markdown editor */
.md-editor-wrap { border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
.md-toolbar {
  background: var(--bg2); border-bottom: 1px solid var(--border);
  padding: 8px 12px; display: flex; gap: 4px; flex-wrap: wrap;
}
.md-toolbar button {
  background: none; border: 1px solid transparent; color: var(--muted);
  padding: 4px 9px; border-radius: 4px; font-size: 12px; cursor: pointer;
  transition: all .12s;
}
.md-toolbar button:hover { background: var(--bg3); border-color: var(--border); color: var(--text); }
.md-toolbar .sep { width: 1px; background: var(--border); margin: 0 4px; }
.md-panes { display: grid; grid-template-columns: 1fr 1fr; }
.md-pane-label {
  font-size: 10px; text-transform: uppercase; letter-spacing: 1px; color: var(--muted);
  padding: 6px 12px; background: var(--bg2); border-bottom: 1px solid var(--border);
}
.md-pane-label:last-of-type { border-left: 1px solid var(--border); }
#editor-ta {
  width: 100%; height: 520px; background: var(--bg); border: none;
  border-right: 1px solid var(--border); color: var(--text);
  padding: 14px; font-family: 'Courier New', monospace; font-size: 13px;
  line-height: 1.7; resize: none; outline: none;
}
.md-preview {
  height: 520px; padding: 14px; overflow-y: auto; font-size: 14px; line-height: 1.75;
  background: var(--bg);
}
.md-preview h1,.md-preview h2,.md-preview h3,.md-preview h4 { color: var(--white); margin: 14px 0 6px; }
.md-preview p { margin-bottom: 10px; }
.md-preview code { background: var(--bg3); padding: 2px 6px; border-radius: 4px; font-size: 12px; font-family: monospace; }
.md-preview pre { background: var(--bg3); padding: 14px; border-radius: 6px; overflow-x: auto; margin: 10px 0; }
.md-preview pre code { background: none; padding: 0; font-size: 12px; }
.md-preview a { color: var(--accent); }
.md-preview ul,.md-preview ol { padding-left: 20px; margin-bottom: 10px; }
.md-preview blockquote { border-left: 3px solid var(--border); padding-left: 14px; color: var(--muted); margin: 10px 0; }
.md-preview table { border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 13px; }
.md-preview th,.md-preview td { border: 1px solid var(--border); padding: 7px 10px; }
.md-preview th { background: var(--bg2); color: var(--white); }
.md-preview hr { border: none; border-top: 1px solid var(--border); margin: 16px 0; }
</style>
</head>
<body>

<aside class="sidebar">
  <div class="sidebar-logo">
    ~/<span>truepositive</span><br>
    <small>cms</small>
  </div>
  <nav class="nav">
    <div class="nav-section">Content</div>
    <a href="{{ url_for('posts') }}" class="{{ 'active' if active == 'posts' }}">
      <svg width="15" height="15" viewBox="0 0 16 16" fill="currentColor"><path d="M2 2.5A2.5 2.5 0 0 1 4.5 0h7A2.5 2.5 0 0 1 14 2.5v11a2.5 2.5 0 0 1-2.5 2.5H4.5A2.5 2.5 0 0 1 2 13.5Zm2.5-1a1 1 0 0 0-1 1v11a1 1 0 0 0 1 1h7a1 1 0 0 0 1-1v-11a1 1 0 0 0-1-1Z"/></svg>
      Posts
    </a>
    <a href="{{ url_for('pages') }}" class="{{ 'active' if active == 'pages' }}">
      <svg width="15" height="15" viewBox="0 0 16 16" fill="currentColor"><path d="M1 2.75A.75.75 0 0 1 1.75 2h12.5a.75.75 0 0 1 0 1.5H1.75A.75.75 0 0 1 1 2.75Zm0 5A.75.75 0 0 1 1.75 7h12.5a.75.75 0 0 1 0 1.5H1.75A.75.75 0 0 1 1 7.75Zm0 5a.75.75 0 0 1 .75-.75h6.5a.75.75 0 0 1 0 1.5h-6.5a.75.75 0 0 1-.75-.75Z"/></svg>
      Pages
    </a>
    <div class="nav-section" style="margin-top:12px">Site</div>
    <a href="https://truepositive.me" target="_blank">
      <svg width="15" height="15" viewBox="0 0 16 16" fill="currentColor"><path d="M8 0a8 8 0 1 0 0 16A8 8 0 0 0 8 0ZM1.5 8a6.5 6.5 0 1 1 13 0 6.5 6.5 0 0 1-13 0Z"/><path d="M8 5.5A2.5 2.5 0 1 0 8 10.5 2.5 2.5 0 0 0 8 5.5Z"/></svg>
      View Blog
    </a>
  </nav>
  <div class="sidebar-footer">TruePositive CMS</div>
</aside>

<div class="main">
  <div class="topbar">
    <h1>{{ title }}</h1>
    <div style="display:flex;gap:8px">{{ topbar_actions | safe }}</div>
  </div>
  <div class="content">
    {% if flash %}
    <div class="flash {{ 'flash-ok' if flash[0]=='ok' else 'flash-err' }}">
      {{ flash[1] }}
    </div>
    {% endif %}
    {{ body | safe }}
  </div>
</div>

<script>
function mdRender(s) {
  return s
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/```[\w]*\n?([\s\S]*?)```/g,(_,c)=>`<pre><code>${c.trim()}</code></pre>`)
    .replace(/`([^`\n]+)`/g,'<code>$1</code>')
    .replace(/^#{4} (.+)$/gm,'<h4>$1</h4>').replace(/^#{3} (.+)$/gm,'<h3>$1</h3>')
    .replace(/^#{2} (.+)$/gm,'<h2>$1</h2>').replace(/^# (.+)$/gm,'<h1>$1</h1>')
    .replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>').replace(/\*(.+?)\*/g,'<em>$1</em>')
    .replace(/^---$/gm,'<hr>')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g,'<a href="$2">$1</a>')
    .replace(/^&gt; (.+)$/gm,'<blockquote>$1</blockquote>')
    .replace(/^\| (.+)$/gm,(_,row)=>{
      if(row.replace(/[-| ]/g,'').trim()==='') return '';
      return '<tr>'+row.split(' | ').map(c=>`<td>${c.trim()}</td>`).join('')+'</tr>';
    })
    .replace(/(<tr>[\s\S]*?<\/tr>\n?)+/g,m=>`<table>${m}</table>`)
    .replace(/^[-*] (.+)$/gm,'<li>$1</li>')
    .replace(/(<li>.*\n?)+/g,m=>`<ul>${m}</ul>`)
    .replace(/\n{2,}/g,'</p><p>');
}
function updatePreview() {
  const ta = document.getElementById('editor-ta');
  const pr = document.getElementById('md-preview');
  if (ta && pr) pr.innerHTML = '<p>' + mdRender(ta.value) + '</p>';
}
function ins(b, a, ph) {
  const ta = document.getElementById('editor-ta');
  const s = ta.selectionStart, e = ta.selectionEnd;
  const sel = ta.value.substring(s,e) || ph || 'text';
  ta.value = ta.value.substring(0,s) + b + sel + a + ta.value.substring(e);
  ta.setSelectionRange(s+b.length+sel.length+a.length, s+b.length+sel.length+a.length);
  ta.focus(); updatePreview();
}
document.addEventListener('DOMContentLoaded', updatePreview);
</script>
</body>
</html>"""

def render(title, body, active="posts", topbar_actions="", flash=None):
    return render_template_string(BASE,
        title=title, body=body, active=active,
        topbar_actions=topbar_actions, flash=flash)

# ── routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def posts():
    flash = request.args.get("flash")
    ftype = request.args.get("ft", "ok")
    items = all_posts()

    rows = ""
    for p in items:
        tags = "".join(f'<span class="badge badge-tag">{t.strip()}</span>'
                       for t in p["tags"].strip("[]").replace('"','').split(",") if t.strip())
        status = '<span class="badge badge-draft">Draft</span>' if p["draft"] else '<span class="badge badge-live">Live</span>'
        rows += f"""<tr>
          <td>
            <div class="post-title">{p['title']}</div>
            <div class="post-date">{p['date']}</div>
          </td>
          <td>{tags}</td>
          <td>{status}</td>
          <td>
            <div class="post-acts">
              <a href="/edit-post?file={p['file']}" class="btn btn-gray btn-sm">Edit</a>
              <a href="/delete-post?file={p['file']}" class="btn btn-danger btn-sm"
                 onclick="return confirm('Delete this post?')">Delete</a>
            </div>
          </td>
        </tr>"""

    if not rows:
        body = """<div class="empty">
          <p>No posts yet. Write your first one!</p>
          <a href="/new-post" class="btn btn-primary">+ New Post</a>
        </div>"""
    else:
        body = f"""<table class="posts-table">
          <thead><tr>
            <th>Title</th><th>Tags</th><th>Status</th><th></th>
          </tr></thead>
          <tbody>{rows}</tbody>
        </table>"""

    return render("Posts", body, "posts",
                  topbar_actions='<a href="/new-post" class="btn btn-primary">+ New Post</a>',
                  flash=(ftype, flash) if flash else None)

@app.route("/pages")
def pages():
    flash = request.args.get("flash")
    ftype = request.args.get("ft", "ok")
    items = all_pages()

    cards = "".join(f"""<div class="page-card">
      <div>
        <div class="page-card-title">{p['title']}</div>
        <div class="page-card-file">{p['file']}</div>
      </div>
      <a href="/edit-page?file={p['file']}" class="btn btn-gray btn-sm">Edit</a>
    </div>""" for p in items)

    body = f'<div class="pages-grid">{cards}</div>'
    return render("Pages", body, "pages", flash=(ftype, flash) if flash else None)

@app.route("/new-post")
def new_post():
    today = (date.today() - timedelta(days=1)).isoformat()
    return render("New Post", editor_form(), "posts",
                  topbar_actions=f'<a href="/" class="btn btn-gray">Cancel</a>')

@app.route("/edit-post")
def edit_post():
    f = request.args.get("file","")
    fp = POSTS_DIR / f
    if not fp.exists(): return redirect("/")
    meta, content = parse_md(fp)
    return render("Edit Post", editor_form(meta=meta, content=content, filename=f), "posts",
                  topbar_actions='<a href="/" class="btn btn-gray">Cancel</a>')

@app.route("/edit-page")
def edit_page_get():
    f = request.args.get("file","")
    fp = CONTENT / f
    if not fp.exists(): return redirect("/pages")
    raw = fp.read_text(encoding="utf-8")
    return render(f"Edit — {f}", page_editor_form(f, raw), "pages",
                  topbar_actions='<a href="/pages" class="btn btn-gray">Cancel</a>')

@app.route("/save-post", methods=["POST"])
def save_post():
    title    = request.form.get("title","")
    tags     = request.form.get("tags","")
    desc     = request.form.get("description","")
    dt       = request.form.get("date", (date.today()-timedelta(days=1)).isoformat())
    content  = request.form.get("content","")
    draft    = request.form.get("draft","false")
    action   = request.form.get("action","save")
    filename = request.form.get("filename","")

    if not filename:
        slug = "".join(c if c.isalnum() or c=="-" else "-" for c in title.lower().replace(" ","-")).strip("-")
        filename = f"{slug}.md"

    fm = make_fm(title, tags, desc, dt, draft)
    (POSTS_DIR / filename).write_text(fm + "\n" + content, encoding="utf-8")

    if action == "publish":
        verb = "update" if request.form.get("filename") else "add"
        ok, out = git_push(f"{verb}: {title}")
        ft = "ok" if ok else "err"
        msg = f"Published: {title}" if ok else f"Saved locally — push failed: {out[:120]}"
    else:
        ft, msg = "ok", f"Saved locally: {filename}"

    return redirect(f"/?flash={msg}&ft={ft}")

@app.route("/save-page", methods=["POST"])
def save_page():
    filename = request.form.get("filename","")
    content  = request.form.get("content","")
    action   = request.form.get("action","save")
    (CONTENT / filename).write_text(content, encoding="utf-8")

    if action == "publish":
        ok, out = git_push(f"update: {filename}")
        ft  = "ok" if ok else "err"
        msg = f"Published: {filename}" if ok else f"Saved locally — push failed: {out[:120]}"
    else:
        ft, msg = "ok", f"Saved locally: {filename}"

    return redirect(f"/pages?flash={msg}&ft={ft}")

@app.route("/delete-post")
def delete_post():
    f = request.args.get("file","")
    fp = POSTS_DIR / f
    if fp.exists():
        fp.unlink()
        ok, _ = git_push(f"delete: {f}")
        ft  = "ok" if ok else "err"
        msg = f"Deleted: {f}" if ok else f"Deleted locally: {f} (push failed)"
    else:
        ft, msg = "err", "File not found"
    return redirect(f"/?flash={msg}&ft={ft}")

# ── form builders ───────────────────────────────────────────────────────────────

def editor_form(meta=None, content="", filename=""):
    meta = meta or {}
    today = (date.today() - timedelta(days=1)).isoformat()
    title  = meta.get("title","").strip('"')
    tags   = meta.get("tags","").strip("[]").replace('"','')
    desc   = meta.get("description","").strip('"')
    dt     = meta.get("date", today)
    draft  = "checked" if meta.get("draft","false") == "true" else ""
    fn     = f'<input type="hidden" name="filename" value="{filename}">' if filename else ""
    safe_c = content.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

    return f"""<form method="POST" action="/save-post">
  {fn}
  <div class="editor-layout">
    <div class="editor-main">
      <div class="field" style="margin-bottom:14px">
        <label>Title</label>
        <input type="text" name="title" value="{title}" placeholder="Post title..." required
               style="font-size:18px;padding:10px 14px;font-weight:600;">
      </div>
      <div class="md-editor-wrap">
        <div class="md-toolbar">
          <button type="button" onclick="ins('**','**','bold')"><b>B</b></button>
          <button type="button" onclick="ins('*','*','italic')"><i>I</i></button>
          <div class="sep"></div>
          <button type="button" onclick="ins('## ','','Heading')">H2</button>
          <button type="button" onclick="ins('### ','','Heading')">H3</button>
          <div class="sep"></div>
          <button type="button" onclick="ins('`','`','code')">code</button>
          <button type="button" onclick="ins('```\\n','\\n```','block')">&#123;&#125;</button>
          <div class="sep"></div>
          <button type="button" onclick="ins('- ','','item')">― list</button>
          <button type="button" onclick="ins('[','](url)','link')">link</button>
          <button type="button" onclick="ins('| Col | Col |\\n|---|---|\\n| ','| |','val')">table</button>
          <button type="button" onclick="ins('> ','','quote')">quote</button>
          <button type="button" onclick="ins('---\\n','','')">hr</button>
        </div>
        <div class="md-pane-label">Markdown</div>
        <div class="md-pane-label" style="border-left:1px solid var(--border)">Preview</div>
        <div class="md-panes">
          <textarea id="editor-ta" name="content" oninput="updatePreview()">{safe_c}</textarea>
          <div class="md-preview" id="md-preview"></div>
        </div>
      </div>
    </div>

    <div class="editor-sidebar">
      <h3>Post Settings</h3>
      <div class="field">
        <label>Date</label>
        <input type="date" name="date" value="{dt}">
      </div>
      <div class="field">
        <label>Tags <span style="font-weight:400;text-transform:none;letter-spacing:0">(comma separated)</span></label>
        <input type="text" name="tags" value="{tags}" placeholder="cve, dfir, research">
      </div>
      <div class="field">
        <label>Description</label>
        <textarea name="description" rows="3" placeholder="Short summary for post list...">{desc}</textarea>
      </div>
      <div class="toggle-wrap">
        <input type="checkbox" name="draft" id="draft-cb" value="true" {draft} style="width:auto">
        <label for="draft-cb">Save as draft</label>
      </div>
      <div class="sidebar-actions">
        <button type="submit" name="action" value="publish" class="btn btn-primary" style="justify-content:center">
          Save &amp; Publish
        </button>
        <button type="submit" name="action" value="save" class="btn btn-gray" style="justify-content:center">
          Save Only
        </button>
      </div>
    </div>
  </div>
</form>"""

def page_editor_form(filename, raw):
    safe = raw.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
    return f"""<form method="POST" action="/save-page">
  <input type="hidden" name="filename" value="{filename}">
  <div class="editor-layout">
    <div class="editor-main">
      <div class="md-editor-wrap">
        <div class="md-toolbar">
          <button type="button" onclick="ins('**','**','bold')"><b>B</b></button>
          <button type="button" onclick="ins('*','*','italic')"><i>I</i></button>
          <div class="sep"></div>
          <button type="button" onclick="ins('## ','','Heading')">H2</button>
          <button type="button" onclick="ins('### ','','Heading')">H3</button>
          <div class="sep"></div>
          <button type="button" onclick="ins('`','`','code')">code</button>
          <button type="button" onclick="ins('```\\n','\\n```','block')">&#123;&#125;</button>
          <div class="sep"></div>
          <button type="button" onclick="ins('- ','','item')">― list</button>
          <button type="button" onclick="ins('[','](url)','link')">link</button>
        </div>
        <div class="md-pane-label">Raw Content</div>
        <div class="md-pane-label" style="border-left:1px solid var(--border)">Preview</div>
        <div class="md-panes">
          <textarea id="editor-ta" name="content" oninput="updatePreview()">{safe}</textarea>
          <div class="md-preview" id="md-preview"></div>
        </div>
      </div>
    </div>
    <div class="editor-sidebar">
      <h3>Page Settings</h3>
      <div style="font-size:12px;color:var(--muted);margin-bottom:14px">
        Editing raw frontmatter + content.<br>Be careful with the <code>---</code> block.
      </div>
      <div class="sidebar-actions" style="padding-top:0;border-top:none;margin-top:0">
        <button type="submit" name="action" value="publish" class="btn btn-primary" style="justify-content:center">
          Save &amp; Publish
        </button>
        <button type="submit" name="action" value="save" class="btn btn-gray" style="justify-content:center">
          Save Only
        </button>
      </div>
    </div>
  </div>
</form>"""

if __name__ == "__main__":
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n  TruePositive CMS  →  http://0.0.0.0:5000\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
