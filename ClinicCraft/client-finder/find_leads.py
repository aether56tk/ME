#!/usr/bin/env python3
"""Build a daily ClinicCraft prospect digest from public RSS search feeds.

This is a lead-discovery aid, not a verified job board. Every result must be
checked manually before applying or contacting anyone. No outreach is sent.
"""
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import quote
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET
from pathlib import Path
import html
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports"
OUT.mkdir(parents=True, exist_ok=True)
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")

QUERIES = [
    ('Google News: presentation / PowerPoint hiring',
     'https://news.google.com/rss/search?q=' + quote('(freelance OR hiring OR "looking for") (PowerPoint OR presentation designer OR slide design) when:7d') + '&hl=en-IN&gl=IN&ceid=IN:en'),
    ('Google News: document / report formatting',
     'https://news.google.com/rss/search?q=' + quote('(freelance OR hiring OR "looking for") ("document formatting" OR "report formatting" OR "thesis formatting") when:7d') + '&hl=en-IN&gl=IN&ceid=IN:en'),
    ('Reddit: PowerPoint and slide design requests',
     'https://www.reddit.com/search.rss?q=' + quote('(hiring OR looking for OR need) (PowerPoint OR slides OR presentation design)') + '&sort=new&t=week'),
    ('Reddit: document formatting requests',
     'https://www.reddit.com/search.rss?q=' + quote('(hiring OR looking for OR need) ("document formatting" OR "report formatting" OR "Canva presentation")') + '&sort=new&t=week'),
]

POSITIVE = re.compile(r'\b(hiring|hire|looking for|need help|freelance|paid|budget|designer|formatting|presentation|powerpoint|slides|deck|report|document|startup|founder|contract|project)\b', re.I)
NEGATIVE = re.compile(r'\b(crypto giveaway|course sale|buy my course|unpaid internship|job training fee|registration fee)\b', re.I)

def clean(value):
    return re.sub(r'\s+', ' ', html.unescape(value or '')).strip()

def fetch(url):
    req = Request(url, headers={'User-Agent': 'ClinicCraftClientFinder/1.0 (public RSS reader)'})
    with urlopen(req, timeout=20) as response:
        return response.read()

def main():
    items = []
    errors = []
    for label, url in QUERIES:
        try:
            root = ET.fromstring(fetch(url))
            for node in root.findall('.//item'):
                title = clean(node.findtext('title'))
                link = clean(node.findtext('link'))
                desc = clean(node.findtext('description'))
                pub = clean(node.findtext('pubDate'))
                if not title or not link or NEGATIVE.search(title + ' ' + desc):
                    continue
                if not POSITIVE.search(title + ' ' + desc):
                    continue
                try:
                    dt = parsedate_to_datetime(pub).astimezone(timezone.utc)
                    if (datetime.now(timezone.utc) - dt).days > 8:
                        continue
                    date = dt.strftime('%Y-%m-%d')
                except Exception:
                    date = 'Date not parsed — verify on source'
                items.append({'title': title, 'url': link, 'desc': desc[:500], 'date': date, 'source': label})
        except Exception as exc:
            errors.append(f'{label}: {type(exc).__name__}: {exc}')

    deduped = {}
    for item in items:
        deduped[item['url']] = item
    items = sorted(deduped.values(), key=lambda x: (x['date'], x['title']), reverse=True)

    lines = [
        f'# ClinicCraft Client Finder — {TODAY}', '',
        '> Automated discovery only. These are unverified search results, not confirmed clients or guaranteed-open jobs.',
        '> Verify the original post, budget, date, eligibility, and payment terms before applying. No messages or applications are sent automatically.', '',
        f'**Results:** {len(items)} unique links', '',
    ]
    if not items:
        lines += ['No matching results were found in the feeds today. This does not mean no jobs exist; RSS coverage is limited.', '']
    for i, item in enumerate(items, 1):
        lines += [
            f'## {i}. [{item["title"]}]({item["url"]})',
            f'- **Feed:** {item["source"]}',
            f'- **Date:** {item["date"]}',
            f'- **Snippet:** {item["desc"] or "No useful snippet returned; open the original post."}',
            '- **Status:** Unverified — open the original listing and confirm it is still accepting applicants.',
            '- **Next step:** Check fit and payment terms; then send a personalised pitch manually.',
            '',
        ]
    if errors:
        lines += ['## Feed errors', 'Some feeds could not be read today:', '']
        lines += [f'- {e}' for e in errors]
        lines += ['']
    lines += [
        '## ClinicCraft offer reference', '',
        '- PowerPoint cleanup: from ₹299 for up to 10 slides',
        '- Document/report layout: from ₹249',
        '- Editable clinic/education templates: from ₹499',
        '- Email: cliniccraft.studio@gmail.com',
        '- Website: https://aether56tk.github.io/ME/ClinicCraft/',
        '',
        '## Safety checks', '',
        '- Never pay registration, training, security-deposit, or release fees to get a job.',
        '- Keep payment and scope in writing; avoid doing large unpaid tests.',
        '- Do not send patient-identifiable or confidential clinical information.',
        '- Do not spam. Personalise each application and respect platform rules.',
        '',
    ]
    (OUT / f'{TODAY}.md').write_text('\n'.join(lines), encoding='utf-8')
    # Keep a stable latest report for easy access.
    (ROOT / 'LATEST_CLIENT_LEADS.md').write_text('\n'.join(lines), encoding='utf-8')
    print(f'Wrote {len(items)} leads to reports/{TODAY}.md')

if __name__ == '__main__':
    main()
