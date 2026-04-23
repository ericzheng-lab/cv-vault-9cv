#!/usr/bin/env python3
"""
refine-experience-bank-round2.py
第二轮精细拆分：
1. 把项目案例型 bullets 从职位池中剥离
2. 继续把 Final Frontier 中的早期/错位内容拆到其他职位
3. 生成更干净的 experience bank
"""

import json
from pathlib import Path
from datetime import datetime

SRC = Path('/Users/drs/Documents/Obsidian-Vault/9_CV/Database/experience-bank-refined.json')
OUT = Path('/Users/drs/Documents/Obsidian-Vault/9_CV/Database/experience-bank-refined-v2.json')
REPORT = Path('/Users/drs/Documents/Obsidian-Vault/9_CV/Database/experience-bank-refined-v2.md')
PROJECT_OUT = Path('/Users/drs/Documents/Obsidian-Vault/9_CV/Database/project-like-bullets.json')


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def key_of(b):
    return ((b.get('title') or '').strip().lower(), (b.get('text') or '').strip().lower())


def dedupe(bullets):
    seen = set()
    out = []
    for b in bullets:
        k = key_of(b)
        if k in seen:
            continue
        seen.add(k)
        out.append(b)
    return out


def match_any(text, patterns):
    t = text.lower()
    return any(p in t for p in patterns)


def classify_bullet(title, text):
    t = (title + ' ' + text).lower()

    # 明显的项目案例字段
    if match_any(t, ['when:', 'what/client:', 'why & how:', 'scope:', 'ownership:', 'business impact:']):
        return 'project_case'

    # 具体项目名
    project_names = [
        'brief history of a family', 'dungeon & fighter', 'dnf', 'honor of kings',
        'zenless zone zero', 'zzz', 'nike x akqa', 'sportschella', 'naraka',
        '3irobotix', 'bmw', 'estée lauder', 'this timeworn land'
    ]
    if match_any(t, project_names):
        return 'project_case'

    # Lead Producer 线索
    if match_any(t, ['10+ premium integrated campaigns', 'cycle time', 'jira/asana', 'pop mart', 'throughput', 'efficiency']):
        return 'lead_producer'

    # IK DESIGN 线索
    if match_any(t, ['physical activations', 'fabrication pipelines', 'material sourcing', 'retail and event spaces', 'spatial design']):
        return 'ik_design'

    # D'ELE 线索
    if match_any(t, ['1.5m+ revenue', 'content division', 'client billing visibility', 'vendor compliance protocols', 'year one']):
        return 'dele'

    # Ker Sound / early production 线索
    if match_any(t, ['aaa asset delivery', 'monster hunter online', 'localized assets', 'end of summer', 'busan', 'coach', 'huawei', 'bilingual coordination', 'on-set logistics']):
        return 'ker_sound'

    # Strategic EP 线索
    if match_any(t, ['dtc revenue transformation', 's-tier ip portfolio ownership', 'global studio orchestration', 'le cube', 'riot games', 'mihoyo', 'tencent']) :
        return 'strategic_ep'

    # First Light 线索
    if match_any(t, ['dragon mark', 'chain of title', 'prores 4444', 'dcp', 'censorship', 'doha film institute', 'torinofilmlab', 'cnc world cinema fund']):
        return 'first_light'

    return 'unknown'


def main():
    data = load_json(SRC)

    exp_map = {e['title']: e for e in data['experiences']}
    ff_ep = exp_map['Executive Producer (Strategic Project Lead)']
    ff_lp = exp_map['Lead Producer']
    ik = exp_map['Project Lead (Experiential Production)']
    dele = exp_map['Head of Production Operations']
    ker = exp_map['Studio Operations Manager']
    flf = exp_map['Founder & Executive Producer']

    project_like = []
    new_ff_ep = []

    moved = {
        'to_project_pool': 0,
        'to_lead_producer': 0,
        'to_ik_design': 0,
        'to_dele': 0,
        'to_ker_sound': 0,
        'to_first_light': 0,
        'kept_strategic_ep': 0,
        'unknown_kept_ff': 0,
    }

    for b in ff_ep.get('all_bullets', []):
        cls = classify_bullet(b.get('title', ''), b.get('text', ''))
        if cls == 'project_case':
            bb = dict(b)
            bb['bucket'] = 'project_case'
            project_like.append(bb)
            moved['to_project_pool'] += 1
        elif cls == 'lead_producer':
            ff_lp['all_bullets'].append(b)
            moved['to_lead_producer'] += 1
        elif cls == 'ik_design':
            ik['all_bullets'].append(b)
            moved['to_ik_design'] += 1
        elif cls == 'dele':
            dele['all_bullets'].append(b)
            moved['to_dele'] += 1
        elif cls == 'ker_sound':
            ker['all_bullets'].append(b)
            moved['to_ker_sound'] += 1
        elif cls == 'first_light':
            flf['all_bullets'].append(b)
            moved['to_first_light'] += 1
        elif cls == 'strategic_ep':
            new_ff_ep.append(b)
            moved['kept_strategic_ep'] += 1
        else:
            new_ff_ep.append(b)
            moved['unknown_kept_ff'] += 1

    ff_ep['all_bullets'] = new_ff_ep

    # dedupe all
    for e in data['experiences']:
        e['all_bullets'] = dedupe(e.get('all_bullets', []))
        master_keys = {key_of(b) for b in e.get('master_bullets', [])}
        e['extra_bullets'] = [b for b in e['all_bullets'] if key_of(b) not in master_keys]

    data['meta']['refined_round2_at'] = datetime.now().isoformat()
    data['meta']['round2_moves'] = moved
    data['meta']['total_bullet_count'] = sum(len(e.get('all_bullets', [])) for e in data['experiences'])

    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    PROJECT_OUT.write_text(json.dumps({
        'generated_at': datetime.now().isoformat(),
        'count': len(project_like),
        'bullets': dedupe(project_like)
    }, indent=2, ensure_ascii=False), encoding='utf-8')

    lines = [
        '# Refined Experience Bank v2',
        '',
        f"> Refined round 2: {data['meta']['refined_round2_at']}",
        '',
        '## Move Summary',
    ]
    for k, v in moved.items():
        lines.append(f'- **{k}**: {v}')
    lines.append('')
    lines.append(f'- **project_like_bullets**: {len(project_like)}')
    lines.append('')
    for e in data['experiences']:
        lines.append(f"## {e['title']} — {e['company']}")
        lines.append(f"- **Total bullets**: {len(e.get('all_bullets', []))}")
        lines.append(f"- **Master bullets**: {len(e.get('master_bullets', []))}")
        lines.append(f"- **Extra bullets**: {len(e.get('extra_bullets', []))}")
        for b in e.get('all_bullets', [])[:8]:
            lines.append(f"  - {b.get('title','')} {b.get('text','')[:100]}")
        lines.append('')
    REPORT.write_text('\n'.join(lines), encoding='utf-8')

    print(f'✅ Wrote {OUT}')
    print(f'✅ Wrote {REPORT}')
    print(f'✅ Wrote {PROJECT_OUT}')
    for e in data['experiences']:
        print(f"- {e['title']} | total={len(e.get('all_bullets', []))} | extra={len(e.get('extra_bullets', []))}")
    print('Moves:', json.dumps(moved, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
