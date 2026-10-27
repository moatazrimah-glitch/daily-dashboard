# Daily Dashboard — GitHub Actions + Pages edition

Your daily dashboard, built automatically on GitHub's servers and published to a
permanent public URL — no computer of yours needs to be on.

## What this gives you

- **A live URL** (e.g. `https://<your-username>.github.io/daily-dashboard/`) you can open on any device, every day.
- **A fully automatic daily edition** at 10:00 Morocco time: Morocco & world politics (Morocco World News, The Guardian, BBC), science (BBC Science, ScienceDaily), philosophy (Daily Nous), Marrakech weather (wttr.in), and a rotating philosophy quote of the day with an explanation.
- **An automatic archive**: each day's edition is saved to `site/archive/YYYY-MM-DD.html`, and the git history becomes a permanent day-by-day record.
- **Free forever** on a public repository.

## Honest limitation

This auto-edition lists the *latest* headlines from your feeds. The AI-curated
version (where ZCode picks the 3 most important science stories and writes the
quote explanation) still arrives in your ZCode chat at 10:00. The two complement
each other: GitHub guarantees the dashboard even when the chat is closed.

## One-time setup (5 minutes)

From this folder, with the [GitHub CLI](https://cli.github.com/) installed and logged in (`gh auth login`):

```bash
git init
git add -A
git commit -m "Daily dashboard"
gh repo create daily-dashboard --public --source=. --push
```

Then open the repo on GitHub → **Actions** tab → **Daily dashboard** → **Run workflow**
(run it once manually so Pages is enabled and the first edition is published).

That's it — the site goes live and redeploys itself every day.

No GitHub CLI? Create the repo manually on github.com, then:

```bash
git init
git add -A
git commit -m "Daily dashboard"
git branch -M main
git remote add origin https://github.com/<your-username>/daily-dashboard.git
git push -u origin main
```

## Customizing

- **Sources:** edit the `GROUPS` list at the top of `scripts/build_dashboard.py` — any RSS feed works.
- **Quotes:** add or edit entries in `quotes.json` (they rotate by day of year).
- **Schedule:** edit the `cron` line in `.github/workflows/daily.yml` (UTC — Morocco is UTC+1, so 10:00 local = `0 9 * * *`). Note GitHub may delay scheduled runs by 15–30 minutes on busy minutes.
