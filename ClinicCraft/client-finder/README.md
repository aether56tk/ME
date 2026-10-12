# ClinicCraft Automated Client Acquisition (MVP)

Free-first lead discovery and a controlled outreach queue. No real email is sent by default; review and approve the first batch first.

## Current automation
- Daily GitHub Actions discovery at 08:00 IST.
- Reads a small set of public Google News and Reddit RSS search feeds.
- Filters and deduplicates results into a daily Markdown digest.
- Provides a CSV review queue and a draft preview tool.
- Sender requires manual invocation, ENABLE_EMAIL_SENDING=true, configured SMTP credentials, and approved rows.
- Sending cap is at most 20 per UTC day.

## Limitations
RSS results can be irrelevant, stale, blocked, or incomplete. This tool does not verify a client or guarantee a job remains open. It does not bulk-harvest personal addresses, send DMs, or automatically send emails in GitHub Actions.

## Run discovery
1. Open https://github.com/aether56tk/ME/actions/workflows/cliniccraft-client-finder.yml
2. Enable GitHub Actions if asked.
3. Click Run workflow.
4. Review ClinicCraft/LATEST_CLIENT_LEADS.md.

## Prepare the first batch
1. Open ClinicCraft/client-finder/data/outreach_queue.csv.
2. Add only individually relevant prospects with a publicly supplied business contact address.
3. Add a specific source_url, why_relevant, and the matching service.
4. Set contact_basis to public_request, explicit_permission, or existing_business_relationship only when genuinely accurate.
5. Set approved=yes only after reviewing the exact recipient and message.
6. Preview locally with: python ClinicCraft/client-finder/outreach.py --drafts

## Email sending is intentionally off
Sending requires ALL of these:
- Manually run python ClinicCraft/client-finder/outreach.py --send.
- Set ENABLE_EMAIL_SENDING=true in that environment.
- Configure SMTP_USERNAME and SMTP_APP_PASSWORD as environment variables, preferably repository secrets. Never commit credentials.
- Lead has approved=yes, valid email, source URL, relevance reason, and supported contact basis.
- No opt-out, bounce, reply, prior send, or suppression record.
- Daily cap not reached.

For Gmail SMTP, use a dedicated account, 2-Step Verification, and an app password where supported. Never store passwords in source code or CSV. The repository currently has no email credentials and this workflow has no sending step.

## Replies, bounces, and opt-outs
This version does not automatically read Gmail replies or bounce notifications. Update the queue promptly:
- replied=yes after any reply; pause further contact for manual review.
- opt_out=yes after unsubscribe/refusal and add the address to the suppression list.
- bounced=yes after a hard bounce and suppress the address.
- Never send follow-ups to a suppressed address.
Only one message per unique lead/email is sent by this prototype; automatic follow-ups are not enabled.

## Service details
- PowerPoint cleanup: from ₹299 (up to 10 slides)
- Document/report layout: from ₹249
- Editable clinic/education templates: from ₹499
- Email: cliniccraft.studio@gmail.com
- Website: https://aether56tk.github.io/ME/ClinicCraft/

## Safety
Contact only relevant prospects through a channel where outreach is permitted. Do not send bulk unsolicited email, ignore opt-outs, or continue after a refusal. Respect applicable privacy, anti-spam, and platform rules. Never pay fees to get a job or share patient-identifiable information.
