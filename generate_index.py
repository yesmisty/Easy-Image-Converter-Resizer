#!/usr/bin/env python3
"""
generate_index.py
Scan the ./blogs/ folder and regenerate blogs.html (newest-first) and sitemap.xml.
Usage (non-coder friendly):
1. Place this script at your site's root (same level as /blogs and /assets).
2. Run: python3 generate_index.py
3. It will overwrite blogs.html and sitemap.xml based on files in /blogs.
Notes:
- The script tries to extract title (<h1>) and date (JSON-LD datePublished or date in meta or file mtime).
- If no date found, file modification time is used.
- Preview images referenced in each blog are left unchanged (the blogs' own OG tags should point to /assets/blog-previews/...).
"""
import os, re, json, datetime
from pathlib import Path
ROOT = Path(__file__).parent.resolve()
BLOGS_DIR = ROOT / "blogs"
OUTPUT_BLOGS_HTML = ROOT / "blogs.html"
OUTPUT_SITEMAP = ROOT / "sitemap.xml"

def extract_title_and_date(html_text, default_date):
    # naive extraction: h1 content as title
    title_match = re.search(r"<h1[^>]*>(.*?)</h1>", html_text, re.S|re.I)
    title = title_match.group(1).strip() if title_match else "Untitled"
    # try to find JSON-LD with datePublished
    ld_match = re.search(r"<script[^>]*type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>", html_text, re.S|re.I)
    date = None
    if ld_match:
        try:
            ld = json.loads(ld_match.group(1))
            date = ld.get("datePublished") or ld.get("dateModified")
        except Exception:
            date = None
    # fallback: meta name="date" or meta property
    if not date:
        m = re.search(r'<meta[^>]+name=["\']?date["\']?[^>]+content=["\']([^"\']+)["\']', html_text, re.I)
        if m:
            date = m.group(1)
    # final fallback: default_date (file mtime)
    if not date:
        date = default_date.isoformat()
    return title, date

def read_blog_files():
    posts = []
    for f in BLOGS_DIR.glob("*.html"):
        text = f.read_text(encoding="utf-8", errors="ignore")
        mtime = datetime.datetime.fromtimestamp(f.stat().st_mtime).date()
        title, date = extract_title_and_date(text, mtime)
        # normalize date to ISO if possible
        try:
            parsed = datetime.date.fromisoformat(date)
            date_iso = parsed.isoformat()
        except Exception:
            date_iso = date
        posts.append({"path": f, "title": title, "date": date_iso})
    return posts

def generate_blogs_html(posts):
    posts_sorted = sorted(posts, key=lambda p: p["date"], reverse=True)
    parts = ['<!doctype html>','<html lang="en">','<head><meta charset="utf-8"><title>Blogs — EasyImageCR</title><link rel="stylesheet" href="/assets/styles.css"><link rel="stylesheet" href="/assets/blog.css"></head>','<body>','  <main style="max-width:1000px;margin:28px auto;padding:16px;">','    <h1>Blogs</h1>','    <section id="posts">']
    for p in posts_sorted:
        slug = p["path"].name
        parts.append(f'      <article>')
        parts.append(f'        <h2><a href="/blogs/{slug}">{p["title"]}</a></h2>')
        parts.append(f'        <div style="color:#666;font-size:14px">{p["date"]}</div>')
        parts.append(f'        <p style="color:#333">Glimpse: Add a 2–3 line summary here describing whether readers should click.</p>')
        parts.append(f'      </article>')
    parts.extend(['    </section>','  </main>','</body>','</html>'])
    OUTPUT_BLOGS_HTML.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {OUTPUT_BLOGS_HTML} with {len(posts_sorted)} posts.")

def generate_sitemap(posts):
    now = datetime.date.today().isoformat()
    lines = ['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    lines.append(f'  <url><loc>https://easyimagecr.in/</loc><lastmod>{now}</lastmod><changefreq>monthly</changefreq><priority>1.0</priority></url>')
    for p in posts:
        url = f'https://easyimagecr.in/blogs/{p["path"].name}'
        lines.append(f'  <url><loc>{url}</loc><lastmod>{p["date"]}</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>')
    lines.append(f'  <url><loc>https://easyimagecr.in/blogs.html</loc><lastmod>{now}</lastmod><changefreq>weekly</changefreq><priority>0.9</priority></url>')
    lines.append("</urlset>")
    OUTPUT_SITEMAP.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUTPUT_SITEMAP} with {len(posts)} posts.")

def main():
    posts = read_blog_files()
    if not posts:
        print("No blog HTML files found in ./blogs. Create .html files there and run again.")
        return
    generate_blogs_html(posts)
    generate_sitemap(posts)

if __name__ == '__main__':
    main()
