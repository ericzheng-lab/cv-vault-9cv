#!/usr/bin/env python3
"""
rebuild-canonical-experiences.py
从 MASTER 简历重建 canonical work experience 数据库。
"""

import json
import re
from pathlib import Path
from datetime import datetime

MASTER = Path('/Users/drs/Documents/Obsidian-Vault/9_CV/01-MASTER/resume-master.html')
OUT = Path('/Users/drs/Documents/Obsidian-Vault/9_CV/Database/canonical-experiences.json')
REPORT = Path('/Users/drs/Documents/Obsidian-Vault/9_CV/Database/canonical-experiences.md')


def infer_tags(text: str):
    t = text.lower()
    tags = []
    mapping = {
        'film': ['film', 'sundance', 'berlinale', 'theatrical', 'cinematic'],
        'financing': ['financing', 'budget', 'revenue', '$', 'grant', 'fund'],
        'legal': ['legal', 'chain of title', 'compliance', 'contracts'],
        'international': ['international', 'global', 'cross-timezone', 'european', 'territories'],
        'post_production': ['post', 'mastering', 'dcp', '4.5k', 'prores'],
        'gaming': ['gaming', 'riot', 'tencent', 'mihoyo', 'aaa'],
        'commercial': ['brand', 'campaign', 'client', 'agency', 'dtc'],
        'operations': ['operations', 'workflow', 'throughput', 'efficiency', 'scaling'],
        'leadership': ['led', 'directed', 'mentored', 'managed', 'ownership'],
        'experiential': ['physical activations', 'retail', 'event spaces', 'fabrication'],
        'audio': ['sound studios', 'localized assets', 'audio'],
    }
    for tag, kws in mapping.items():
        if any(k in t for k in kws):
            tags.append(tag)
    return tags or ['general']


def extract_metrics(text: str):
    metrics = re.findall(r'\$[\d\.]+[MK]?\+?|€\d+[kK]?|\d+\+|\d+%', text)
    return metrics or None


def parse_master(html: str):
    pattern = re.compile(
        r'<div class="job-entry">\s*'
        r'<div class="job-header-row">\s*'
        r'<div class="role-title">(.*?)</div>\s*'
        r'<div class="date-range">(.*?)</div>\s*'
        r'</div>\s*'
        r'<div class="company-row">\s*<span class="company-name">(.*?)</span>\s*</div>\s*'
        r'<ul class="exp-list">(.*?)</ul>',
        re.S,
    )
    items = []
    for idx, m in enumerate(pattern.finditer(html), start=1):
        title = re.sub(r'\s+', ' ', m.group(1)).strip()
        period = re.sub(r'\s+', ' ', m.group(2)).strip()
        company_loc = re.sub(r'\s+', ' ', m.group(3)).strip()
        bullets_html = m.group(4)
        if '|' in company_loc:
            company, location = [x.strip() for x in company_loc.split('|', 1)]
        else:
            company, location = company_loc, ''

        bullet_matches = re.findall(r'<li><strong>(.*?)</strong>(.*?)</li>', bullets_html, re.S)
        bullets = []
        for bidx, (btitle, btext) in enumerate(bullet_matches, start=1):
            btitle = re.sub(r'\s+', ' ', btitle).strip()
            btext = re.sub(r'<.*?>', '', btext)
            btext = re.sub(r'\s+', ' ', btext).strip()
            bullets.append({
                'id': f'exp-{idx:02d}-{bidx:02d}',
                'title': btitle,
                'text': btext,
                'tags': infer_tags(btitle + ' ' + btext),
                'metrics': extract_metrics(btext),
            })

        items.append({
            'id': f'exp-{idx:02d}',
            'company': company,
            'title': title,
            'period': period,
            'location': location,
            'type': infer_tags(title + ' ' + company)[0],
            'bullets': bullets,
            'source': 'resume-master.html'
        })
    return items


def main():
    html = MASTER.read_text(encoding='utf-8', errors='ignore')
    experiences = parse_master(html)
    data = {
        'meta': {
            'version': '1.0',
            'generated_at': datetime.now().isoformat(),
            'source': str(MASTER),
            'canonical': True,
            'experience_count': len(experiences),
            'bullet_count': sum(len(e['bullets']) for e in experiences),
        },
        'experiences': experiences,
    }
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')

    md = [
        '# Canonical Work Experiences',
        '',
        f'> Generated: {data["meta"]["generated_at"]}',
        '',
        f'- **Experience count**: {data["meta"]["experience_count"]}',
        f'- **Bullet count**: {data["meta"]["bullet_count"]}',
        '',
    ]
    for exp in experiences:
        md.append(f'## {exp["title"]} — {exp["company"]}')
        md.append(f'- **Period**: {exp["period"]}')
        md.append(f'- **Location**: {exp["location"]}')
        md.append(f'- **Bullets**: {len(exp["bullets"])}')
        for b in exp['bullets']:
            md.append(f'  - `{b["id"]}` **{b["title"]}** {b["text"]}')
        md.append('')
    REPORT.write_text('\n'.join(md), encoding='utf-8')
    print(f'✅ Wrote {OUT}')
    print(f'✅ Wrote {REPORT}')


if __name__ == '__main__':
    main()
