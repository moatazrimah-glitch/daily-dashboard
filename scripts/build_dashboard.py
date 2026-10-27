#!/usr/bin/env python3
"""Builds the daily dashboard from live feeds. Python stdlib only, no dependencies."""
import datetime as dt
import html
import json
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

# Each group becomes a dashboard section. Edit this list to change sources.
GROUPS = [
    ("Politics — Morocco", [
        ("Morocco World News", "https://www.moroccoworldnews.com/feed", 4),
    ]),
    ("Politics — World", [
        ("The Guardian", "https://www.theguardian.com/world/rss", 3),
        ("BBC", "https://feeds.bbci.co.uk/news/world/rss.xml", 3),
    ]),
    ("Science — latest", [
        ("BBC Science", "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml", 3),
        ("ScienceDaily", "https://www.sciencedaily.com/rss/all.xml", 3),
    ]),
    ("Philosophy", [
        ("Daily Nous", "https://dailynous.com/feed/", 3),
    ]),
]


def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "daily-dashboard-bot/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def parse_feed(raw):
    root = ET.fromstring(raw)
    items = []
    for node in root.iter():
        if node.tag.split("}")[-1] == "item":  # RSS 2.0
            title = link = ""
            for child in node:
                tag = child.tag.split("}")[-1]
                if tag == "title" and child.text and not title:
                    title = child.text.strip()
                elif tag == "link" and child.text and not link:
                    link = child.text.strip()
            if title:
                items.append({"title": title, "link": link})
    if not items:  # Atom fallback
        for node in root.iter():
            if node.tag.split("}")[-1] == "entry":
                title, link = "", ""
                for child in node:
                    tag = child.tag.split("}")[-1]
                    if tag == "title" and child.text and not title:
                        title = child.text.strip()
                    elif tag == "link" and not link:
                        link = child.attrib.get("href", "")
                if title:
                    items.append({"title": title, "link": link})
    return items


def get_weather():
    try:
        data = json.loads(fetch("https://wttr.in/Marrakech?format=j1"))
        cur = data["current_condition"][0]
        astro = data["weather"][0]["astronomy"][0]
        return {
            "temp": cur["temp_C"],
            "feels": cur["FeelsLikeC"],
            "desc": cur["weatherDesc"][0]["value"],
            "humidity": cur["humidity"],
            "wind": f'{cur["windspeedKmph"]} km/h {cur["winddir16Point"]}',
            "sunrise": astro["sunrise"],
            "sunset": astro["sunset"],
        }
    except Exception:
        return None


def get_quote():
    quotes = json.loads((ROOT / "quotes.json").read_text(encoding="utf-8"))
    return quotes[dt.date.today().timetuple().tm_yday % len(quotes)]


def esc(s):
    return html.escape(s or "")


CSS = """
  :root {
    color-scheme: light dark;
    --bg: #f6f7f9; --panel: #ffffff; --border: rgba(15, 23, 42, .09);
    --text: #1a2230; --muted: #5b6572; --accent: #2563eb;
    --quote-bg: rgba(120, 100, 60, .07);
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #12151a; --panel: #1b2027; --border: rgba(255, 255, 255, .09);
      --text: #e8eaed; --muted: #9aa4b1; --accent: #60a5fa;
      --quote-bg: rgba(220, 190, 130, .08);
    }
  }
  * { box-sizing: border-box; }
  body { margin: 0; font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: var(--bg); color: var(--text); }
  .wrap { max-width: 960px; margin: 0 auto; padding: 36px 20px 48px; }
  .kicker { font-size: 12px; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }
  header h1 { font-size: 26px; margin: 4px 0 6px; }
  .edition { color: var(--muted); font-size: 14px; }
  .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin: 26px 0 18px; }
  .stat { background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 14px 16px; }
  .stat .label { font-size: 11.5px; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); }
  .stat .value { font-size: 26px; font-weight: 600; margin-top: 4px; font-variant-numeric: tabular-nums; }
  .stat .context { font-size: 12px; color: var(--muted); margin-top: 2px; }
  section { background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 20px 22px; margin: 0 0 16px; }
  section h2 { font-size: 15px; margin: 0 0 4px; }
  section .sub { font-size: 13px; color: var(--muted); margin: 0 0 12px; }
  ul.headlines { list-style: none; margin: 0; padding: 0; }
  ul.headlines li { padding: 9px 0; border-top: 1px solid var(--border); font-size: 14.5px; line-height: 1.5; }
  ul.headlines li:first-child { border-top: 0; }
  ul.headlines a { color: var(--accent); text-decoration: none; }
  ul.headlines a:hover { text-decoration: underline; }
  .src { font-size: 12px; color: var(--muted); }
  h3.group { font-size: 12px; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); margin: 16px 0 2px; }
  h3.group:first-of-type { margin-top: 0; }
  .quotebox { background: var(--quote-bg); border-radius: 10px; padding: 16px 18px; margin-top: 6px; }
  .quotebox .quote { margin: 0 0 8px; font-family: Georgia, "Times New Roman", serif; font-style: italic; font-size: 18px; line-height: 1.55; }
  .quotebox .author { font-size: 13px; color: var(--muted); margin-bottom: 10px; }
  .quotebox .meaning { font-size: 14px; line-height: 1.55; margin: 0; }
  ul.history { list-style: none; margin: 0; padding: 0; font-size: 13.5px; }
  ul.history li { padding: 8px 0; border-top: 1px solid var(--border); color: var(--muted); }
  ul.history li:first-child { border-top: 0; color: var(--text); }
  ul.history b { font-variant-numeric: tabular-nums; }
  .note { font-size: 12.5px; color: var(--muted); text-align: center; margin-top: 28px; }
"""


def feed_list_html(label, url, items):
    src = ' — <span class="src">via <a href="{}">{}</a></span>'.format(esc(url), esc(label))
    if not items:
        return "<li>Feed unavailable today." + src + "</li>"
    lines = []
    for it in items:
        title = esc(it["title"])
        body = '<a href="{}">{}</a>'.format(esc(it["link"]), title) if it["link"] else title
        lines.append("<li>" + body + src + "</li>")
    return "\n".join(lines)


def render(date_str, groups_data, weather, quote, total, science_count, history):
    temp_stat, weather_line = "—", "Weather unavailable today."
    if weather:
        temp_stat = esc(weather["temp"]) + "°C"
        weather_line = (
            esc(weather["temp"]) + "°C (feels like " + esc(weather["feels"]) + "°C) · "
            + esc(weather["desc"]) + " · Humidity " + esc(weather["humidity"]) + "% · Wind "
            + esc(weather["wind"]) + " · Sunrise " + esc(weather["sunrise"]) + " · Sunset "
            + esc(weather["sunset"]) + "."
        )

    sections = []
    for label, feeds in groups_data:
        blocks = []
        for feed_label, feed_url, items in feeds:
            blocks.append(
                "<h3 class=\"group\">" + esc(feed_label) + "</h3>\n<ul class=\"headlines\">"
                + feed_list_html(feed_label, feed_url, items) + "</ul>"
            )
        sections.append(
            "<section>\n<h2>" + esc(label) + "</h2>\n<p class=\"sub\">Latest from the live feed, collected today.</p>\n"
            + "\n".join(blocks) + "\n</section>"
        )

    quote_block = (
        '<section>\n<h2>Philosophy quote of the day</h2>\n<p class="sub">One quote to learn about, every day.</p>\n'
        '<div class="quotebox">\n<p class="quote">&ldquo;' + esc(quote["text"]) + '&rdquo;</p>\n'
        '<div class="author">— ' + esc(quote["author"]) + ", " + esc(quote["source"]) + '</div>\n'
        '<p class="meaning">' + esc(quote["meaning"]) + "</p>\n</div>\n</section>"
    )

    history_html = "\n".join("<li>" + esc(h) + "</li>" for h in history)

    page = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Daily Dashboard</title>
<style>""" + CSS + """</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="kicker">Daily dashboard report</div>
    <h1>Daily Dashboard</h1>
    <div class="edition">""" + esc(date_str) + """ · Morocco &amp; world politics, science &amp; philosophy, Marrakech weather · built automatically on GitHub Pages</div>
  </header>

  <div class="stats">
    <div class="stat"><div class="label">Marrakech now</div><div class="value">""" + temp_stat + """</div><div class="context">""" + (esc(weather["desc"]) if weather else "n/a") + """</div></div>
    <div class="stat"><div class="label">News items</div><div class="value">""" + str(total) + """</div><div class="context">collected this run</div></div>
    <div class="stat"><div class="label">Science stories</div><div class="value">""" + str(science_count) + """</div><div class="context">latest published</div></div>
    <div class="stat"><div class="label">Quote of the day</div><div class="value">&#10003;</div><div class="context">""" + esc(quote["author"]) + """</div></div>
  </div>

  """ + "\n".join(sections) + """

  <section>
    <h2>Marrakech weather</h2>
    <p class="sub">Live conditions at build time.</p>
    <ul class="headlines"><li>""" + weather_line + """ <span class="src">— <a href="https://wttr.in/Marrakech">wttr.in</a></span></li></ul>
  </section>

  """ + quote_block + """

  <section>
    <h2>History</h2>
    <p class="sub">One line per daily edition, most recent first (last 7 kept).</p>
    <ul class="history">""" + history_html + """</ul>
  </section>

  <div class="note">Built automatically by GitHub Actions · runs daily at 10:00 Morocco time · every edition is also kept in the archive and in the git history</div>
</div>
</body>
</html>
"""
    return page


def main():
    today = dt.date.today()
    date_str = today.strftime("%A, %B %d, %Y")

    groups_data, total, science_count = [], 0, 0
    for label, feeds in GROUPS:
        resolved = []
        for feed_label, feed_url, n in feeds:
            try:
                items = parse_feed(fetch(feed_url))[:n]
            except Exception:
                items = []
            total += len(items)
            if label.startswith("Science"):
                science_count += len(items)
            resolved.append((feed_label, feed_url, items))
        groups_data.append((label, resolved))

    weather = get_weather()
    quote = get_quote()

    hist_path = SITE / "history.json"
    history = []
    if hist_path.exists():
        try:
            history = json.loads(hist_path.read_text(encoding="utf-8"))
        except Exception:
            history = []
    summary = today.isoformat() + " — " + str(total) + " items collected"
    if weather:
        summary += ", Marrakech " + weather["temp"] + "°C " + weather["desc"].lower()
    else:
        summary += ", weather unavailable"
    history.insert(0, summary)
    history = history[:7]

    page = render(date_str, groups_data, weather, quote, total, science_count, history)

    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / "index.html").write_text(page, encoding="utf-8")
    (SITE / "history.json").write_text(json.dumps(history, indent=2), encoding="utf-8")
    (SITE / "archive").mkdir(exist_ok=True)
    (SITE / "archive" / (today.isoformat() + ".html")).write_text(page, encoding="utf-8")
    print("Built edition for", today.isoformat(), "-", total, "items")


if __name__ == "__main__":
    main()
