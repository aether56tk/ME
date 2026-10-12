# ClinicCraft Client Finder

A free daily lead-discovery workflow for ClinicCraft.

## What it does
- Runs at 08:00 India Standard Time.
- Reads public Google News and Reddit RSS search feeds.
- Filters and deduplicates possible PowerPoint, presentation, and document-formatting leads.
- Saves a dated Markdown report under reports/ and updates ../LATEST_CLIENT_LEADS.md.
- Can also be started manually from the GitHub Actions tab.

## Run it
1. Open the Actions tab in the aether56tk/ME repository.
2. Enable Actions if GitHub asks you to.
3. Select ClinicCraft Daily Client Finder.
4. Choose Run workflow.
5. When it completes, open ClinicCraft/LATEST_CLIENT_LEADS.md.

## Limitations
This is an early version. RSS search is limited and results may be stale, irrelevant, or unavailable. It does not verify clients, confirm that a job is open, or guarantee payment. It never sends emails, DMs, or applications. Check each original post and contact the prospect manually.

No paid API key is required. Do not add passwords, tokens, or private keys to source files. Never pay a registration fee or deposit to obtain a job.
