#!/usr/bin/env python3
"""
merge-materials-into-canonical.py
将现有数据库素材归并到 6 个 canonical 职位下。
"""

import json
from pathlib import Path
from datetime import datetime

CANONICAL = Path('/Users/drs/Documents/Obsidian-Vault/9_CV/Database/canonical-experiences.json')
LEGACY = Path('/Users/drs/Documents/Obsidian-Vault/9_CV/Database/Eric-Database.json')
OUT = Path('/Users/drs/Documents/Obsidian-Vault/9_CV/Database/experience-bank.json')
REPORT = Path('/Users/drs/Documents/Obsidian-Vault/9_CV/Database/experience-bank.md')


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def normalize(s: str):
    return s.lower().replace('&', 'and').replace('  ', ' ').strip()


def map_legacy_to_canonical(legacy_exp, canonical_exps):
    title = normalize(legacy_exp['title'])
    company = normalize(legacy_exp['company'])

    for c in canonical_exps:
        ctitle = normalize(c['title'])
        ccompany = normalize(c['company'])

        if 'first light' in company and 'first light' in ccompany:
            return c['id']
        if 'final frontier' in company and 'final frontier' in ccompany:
            # legacy 的 Final Frontier 需要按内容再拆；先优先挂到 Strategic EP，后续人工再细调
            if 'executive producer' in title and 'strategic' in ctitle:
                return c['id']
            if 'lead producer' in ctitle:
                return c['id']
            return c['id']
        if any(k in company for k in ['kersound', 'ker sound', "d'ele", 'independent']):
            # legacy 把 KerSound / D'ELE / Independent 合并了，先挂到最早职位池，后续可再拆
            if 'ker sound' in ccompany:
                return c['id']
        if 'ik design' in company and 'ik design' in ccompany:
            return c['id']
        if "d'ele" in company and "d'ele" in ccompany:
            return c['id']
    return None


def bullet_key(b):
    return (b.get('title', '').strip().lower(), b.get('text', '').strip().lower())


def main():
    canonical = load_json(CANONICAL)
    legacy = load_json(LEGACY)

    bank = {
        'meta': {
            'version': '1.0',
            'generated_at': datetime.now().isoformat(),
            'source': ['canonical-experiences.json', 'Eric-Database.json'],
        },
        'experiences': []
    }

    # 初始化 experience bank
    exp_index = {}
    for exp in canonical['experiences']:
        item = {
            'id': exp['id'],
            'company': exp['company'],
            'title': exp['title'],
            'period': exp['period'],
            'location': exp['location'],
            'type': exp['type'],
            'master_bullets': exp['bullets'],
            'extra_bullets': [],
            'all_bullets': list(exp['bullets']),
        }
        bank['experiences'].append(item)
        exp_index[exp['id']] = item

    # 合并 legacy bullets
    for lexp in legacy.get('experiences', []):
        target_id = map_legacy_to_canonical(lexp, canonical['experiences'])
        if not target_id:
            continue
        target = exp_index[target_id]
        existing = {bullet_key(b) for b in target['all_bullets']}
        for b in lexp.get('bullets', []):
            key = bullet_key(b)
            if key not in existing:
                new_b = dict(b)
                new_b['source'] = 'legacy'
                target['extra_bullets'].append(new_b)
                target['all_bullets'].append(new_b)
                existing.add(key)

    # 汇总 meta
    bank['meta']['experience_count'] = len(bank['experiences'])
    bank['meta']['master_bullet_count'] = sum(len(e['master_bullets']) for e in bank['experiences'])
    bank['meta']['extra_bullet_count'] = sum(len(e['extra_bullets']) for e in bank['experiences'])
    bank['meta']['total_bullet_count'] = sum(len(e['all_bullets']) for e in bank['experiences'])

    OUT.write_text(json.dumps(bank, indent=2, ensure_ascii=False), encoding='utf-8')

    # Markdown 报告
    lines = [
        '# Experience Bank',
        '',
        f'> Generated: {bank["meta"]["generated_at"]}',
        '',
        f'- **Experience count**: {bank["meta"]["experience_count"]}',
        f'- **Master bullets**: {bank["meta"]["master_bullet_count"]}',
        f'- **Extra bullets**: {bank["meta"]["extra_bullet_count"]}',
        f'- **Total bullets**: {bank["meta"]["total_bullet_count"]}',
        '',
    ]
    for exp in bank['experiences']:
        lines.append(f'## {exp["title"]} — {exp["company"]}')
        lines.append(f'- **Period**: {exp["period"]}')
        lines.append(f'- **Master bullets**: {len(exp["master_bullets"])}')
        lines.append(f'- **Extra bullets**: {len(exp["extra_bullets"])}')
        lines.append(f'- **Total bullets**: {len(exp["all_bullets"])}')
        if exp['extra_bullets']:
            lines.append('- **Added from legacy:**')
            for b in exp['extra_bullets']:
                lines.append(f'  - {b.get("title", "")} {b.get("text", "")[:120]}')
        lines.append('')

    REPORT.write_text('\n'.join(lines), encoding='utf-8')
    print(f'✅ Wrote {OUT}')
    print(f'✅ Wrote {REPORT}')
    print('Summary:')
    print(json.dumps(bank['meta'], indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
