# ClinicCraft

A lightweight static landing page for affordable presentation formatting, document/report layout, editable educational templates, and healthcare digital-safety awareness materials.

## Live form setup
The contact form uses Supabase project `xbyzcyzpszkpapfilzoj` and the public publishable key in `index.html`. This key is designed for browser use; row-level security on `public.enquiries` permits public INSERT only. Never place a Supabase service-role/secret key in this repository.

## Publish
This folder can be served as a static website. For GitHub Pages from the parent `ME` repository, enable Pages and serve the repository root; then this page is available at `/ME/ClinicCraft/` if Pages is already configured for that repo.

## Privacy
The form collects name, email, service, and message. Do not ask visitors to send patient-identifiable data, medical records, credentials, or confidential security information. Add a contact email and an appropriate privacy notice before promoting the site.

## Status
Database table and insert-only RLS policy created. Verify a real test submission in Supabase Table Editor before accepting client enquiries. Hosting status depends on GitHub Pages configuration.
