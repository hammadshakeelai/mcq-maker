# Deploying the demo site

The live demo is the static site in [`web/`](web/): a landing page
(`index.html`), the built sample quiz (`quiz.html`), and the banner
(`banner.svg`). It is **100% static** — no server, no backend, no env vars.

## TL;DR — for a future Claude (self-setup)

Everything needed is already in the repo. To (re)deploy:

1. **Rebuild the site** (regenerates `web/quiz.html` from the sample set and
   copies the banner):

   ```bash
   python scripts/build_site.py
   ```

2. **Deploy.** Either:
   - **Vercel MCP tool** — call `deploy_to_vercel` (deploys the current
     project per [`vercel.json`](vercel.json)). This is the easiest path when
     running inside Claude with the Vercel connector enabled.
   - **Vercel CLI** — `npx vercel deploy --prod` from the repo root.
   - **Vercel dashboard / Git** — import `hammadshakeelai/mcq-maker`; the
     committed `vercel.json` configures everything (no settings to fill in).

No account secrets are stored in the repo. The Vercel project, if created via
the MCP tool or CLI, links itself in `.vercel/` (git-ignored).

## How `vercel.json` is set up

```jsonc
{
  "buildCommand": "python3 scripts/build_site.py || true", // regenerate if Python is present
  "outputDirectory": "web",                                // serve the static site
  "framework": null,                                       // plain static, no framework
  "cleanUrls": true                                        // /quiz instead of /quiz.html
}
```

`web/` is **committed pre-built**, so the deploy works even if the build step
is skipped — the `|| true` means a missing/failed Python step still serves the
committed `web/` as-is.

## Local preview

```bash
python scripts/build_site.py
cd web && python -m http.server 8765 --bind 127.0.0.1
# open http://127.0.0.1:8765/
```

## Updating the demo

The demo quiz comes from
`.claude/skills/mcq-maker/examples/sample_questions.json`. Change those
questions (or the quiz template / banner), then re-run
`python scripts/build_site.py` and redeploy.
