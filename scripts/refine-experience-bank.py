#!/usr/bin/env python3
"""
refine-experience-bank.py
将 experience-bank 中粗归并的素材，按 6 个真实职位进一步精细拆分。
"""

import json
from pathlib import Path
from datetime import datetime

SRC = Path('/Users/drs/Documents/Obsidian-Vault/9_CV/Database/experience-bank.json')
OUT = Path('/Users/drs/Documents/Obsidian-Vault/9_CV/Database/experience-bank-refined.json')
REPORT = Path('/Users/drs/Documents/Obsidian-Vault/9_CV/Database/experience-bank-refined.md')


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def move_matching_bullets(source_exp, target_exp, rules):
    kept = []
    moved = []
    for b in source_exp.get('all_bullets', []):
        text = (b.get('title', '') + ' ' + b.get('text', '')).lower()
        if any(rule(text) for rule in rules):
            moved.append(b)
        else:
            kept.append(b)
    source_exp['all_bullets'] = dedupe_bullets(kept)
    target_exp['all_bullets'] = dedupe_bullets(target_exp.get('all_bullets', []) + moved)
    return len(moved)


def dedupe_bullets(bullets):
    seen = set()
    out = []
    for b in bullets:
        key = ((b.get('title') or '').strip().lower(), (b.get('text') or '').strip().lower())
        if key in seen:
            continue
        seen.add(key)
        out.append(b)
    return out


def main():
    data = load_json(SRC)
    exps = {e['id']: e for e in data['experiences']}

    # 找到 6 个 canonical 职位
    flf = next(e for e in data['experiences'] if e['company'] == 'First Light Films')
    ff_ep = next(e for e in data['experiences'] if e['title'] == 'Executive Producer (Strategic Project Lead)')
    ff_lp = next(e for e in data['experiences'] if e['title'] == 'Lead Producer')
    ik = next(e for e in data['experiences'] if e['company'].startswith('IK DESIGN'))
    dele = next(e for e in data['experiences'] if e['company'].startswith("D'ELE"))
    ker = next(e for e in data['experiences'] if e['company'].startswith('Ker Sound'))

    # 规则：从 Final Frontier Strategic EP 里拆分素材
    lead_rules = [
        lambda t: '10+' in t,
        lambda t: 'jira' in t or 'asana' in t,
        lambda t: 'cycle time' in t or 'throughput' in t or 'efficiency' in t,
        lambda t: 'pop mart' in t,
        lambda t: 'lead producer' in t,
    ]
    ik_rules = [
        lambda t: 'physical activations' in t,
        lambda t: 'fabrication' in t,
        lambda t: 'retail' in t,
        lambda t: 'event spaces' in t,
        lambda t: 'ik design' in t,
        lambda t: 'spatial design' in t,
    ]
    dele_rules = [
        lambda t: '1.5m' in t or '$1.5m' in t,
        lambda t: 'content division' in t,
        lambda t: 'client billing' in t,
        lambda t: 'vendor compliance protocols' in t,
        lambda t: "d'ele" in t,
        lambda t: 'head of production operations' in t,
    ]
    ker_rules = [
        lambda t: 'aaa asset delivery' in t,
        lambda t: 'monster hunter' in t,
        lambda t: 'localized assets' in t,
        lambda t: 'studio operations manager' in t,
        lambda t: 'kersound' in t or 'ker sound' in t,
        lambda t: 'end of summer' in t,
        lambda t: 'busan' in t,
        lambda t: 'tvc campaigns' in t,
        lambda t: 'coach' in t or 'huawei' in t,
    ]

    moved_counts = {
        'to_lead_producer': move_matching_bullets(ff_ep, ff_lp, lead_rules),
        'to_ik_design': move_matching_bullets(ff_ep, ik, ik_rules),
        'to_dele': move_matching_bullets(ff_ep, dele, dele_rules),
        'to_ker_sound': move_matching_bullets(ff_ep, ker, ker_rules),
    }

    # 重算 master/extra 显示字段
    for e in data['experiences']:
        master_keys = {
            ((b.get('title') or '').strip().lower(), (b.get('text') or '').strip().lower())
            for b in e.get('master_bullets', [])
        }
        extra = []
        for b in e.get('all_bullets', []):
            key = ((b.get('title') or '').strip().lower(), (b.get('text') or '').strip().lower())
            if key not in master_keys:
                extra.append(b)
        e['extra_bullets'] = extra

    data['meta']['refined_at'] = datetime.now().isoformat()
    data['meta']['moved_counts'] = moved_counts
    data['meta']['total_bullet_count'] = sum(len(e.get('all_bullets', [])) for e in data['experiences'])

    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')

    lines = [
        '# Refined Experience Bank',
        '',
        f"> Refined: {data['meta']['refined_at']}",
        '',
        '## Move Summary',
    ]
    for k, v in moved_counts.items():
        lines.append(f'- **{k}**: {v}')
    lines.append('')
    lines.append('## Experience Buckets')
    lines.append('')
    for e in data['experiences']:
        lines.append(f"### {e['title']} — {e['company']}")
        lines.append(f"- **Total bullets**: {len(e.get('all_bullets', []))}")
        lines.append(f"- **Master bullets**: {len(e.get('master_bullets', []))}")
        lines.append(f"- **Extra bullets**: {len(e.get('extra_bullets', []))}")
        for b in e.get('all_bullets', [])[:6]:
            lines.append(f"  - {b.get('title','')} {b.get('text','')[:100]}")
        lines.append('')
    REPORT.write_text('\n'.join(lines), encoding='utf-8')

    print(f'✅ Wrote {OUT}')
    print(f'✅ Wrote {REPORT}')
    for e in data['experiences']:
        print(f"- {e['title']} | total={len(e.get('all_bullets', []))} | extra={len(e.get('extra_bullets', []))}")


if __name__ == '__main__':
    main()
