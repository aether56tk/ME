# ClinicCraft

A lightweight static landing page for presentation design, document/report formatting, editable educational templates, research support, and educational digital-safety resources.

## Customer contact
Official customer-facing email: `cliniccraft.studio@gmail.com`. Confirm the Gmail account is successfully created and accessible before promoting it.

## Live form setup
The contact form uses Supabase project `xbyzcyzpszkpapfilzoj` and the public publishable key in `index.html`. This key is designed for browser use; row-level security on `public.enquiries` permits public INSERT only. Never place a Supabase service-role/secret key in this repository.

## Source files
- `ClinicCraft.html` — named copy of the website source.
- `index.html` — kept in place as the GitHub Pages entry point so the existing `/ME/ClinicCraft/` URL continues to work.

## Publish
This folder can be served as a static website. For GitHub Pages from the parent `ME` repository, enable Pages and serve the repository root; then this page is available at `/ME/ClinicCraft/` if Pages is already configured for that repo.

## Privacy
The form collects name, email, service, and message. Do not ask visitors to send patient-identifiable data, medical records, credentials, or confidential security information. Add and test a dedicated contact email and an appropriate privacy notice before promoting the site.

## Status
Database table and insert-only RLS policy created. A real public form submission still needs to be tested in the live site before accepting client enquiries. Hosting status depends on GitHub Pages configuration.
