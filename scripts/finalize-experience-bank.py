#!/usr/bin/env python3
"""
finalize-experience-bank.py
最后一轮清洗：
1. 清除误挂到 experience 下的 skills/client roster bullets
2. 输出 final experience bank / project bank
3. 生成简历工作流可直接调用的最终结构
"""

import json
from pathlib import Path
from datetime import datetime

EXP_SRC = Path('/Users/drs/Documents/Obsidian-Vault/9_CV/Database/experience-bank-refined-v2.json')
PROJECT_SRC = Path('/Users/drs/Documents/Obsidian-Vault/9_CV/Database/project-like-bullets.json')
FINAL_EXP = Path('/Users/drs/Documents/Obsidian-Vault/9_CV/Database/experience-bank-final.json')
FINAL_PROJECT = Path('/Users/drs/Documents/Obsidian-Vault/9_CV/Database/project-bank-final.json')
FINAL_REPORT = Path('/Users/drs/Documents/Obsidian-Vault/9_CV/Database/final-database-summary.md')


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def key_of(b):
    return ((b.get('title') or '').strip().lower(), (b.get('text') or '').strip().lower())


def dedupe(items):
    seen = set()
    out = []
    for item in items:
        k = key_of(item)
        if k in seen:
            continue
        seen.add(k)
        out.append(item)
    return out


def is_non_experience_bullet(b):
    title = (b.get('title') or '').strip().lower()
    text = (b.get('text') or '').strip().lower()
    blob = title + ' ' + text

    bad_titles = {
        'production & operations',
        'commercial & legal',
        'risk & gov relations',
        'tools & software',
        'project management',
        'finance & erp',
        'creative & post-production',
        'ai integration',
        'gaming & tech',
        'luxury, fashion & beauty',
        'fmcg & lifestyle',
        'agencies',
        'languages',
    }
    if title in bad_titles:
        return True

    bad_markers = [
        'global workstream operations',
        'integrated campaign delivery',
        'entertainment law',
        'monday.com, trello, asana',
        'adobe creative suite',
        'openclaw, google gemini, midjourney',
        'riot games (_league of legends mobile_)',
        "l'oreal, estée lauder, cartier, coach",
        'akqa, bbh, vmly&r',
        'native',
        'full professional/academic proficiency',
    ]
    return any(marker in blob for marker in bad_markers)


def shorten(text, n=220):
    text = ' '.join((text or '').split())
    return text if len(text) <= n else text[:n].rstrip() + '...'


def main():
    exp = load_json(EXP_SRC)
    projects = load_json(PROJECT_SRC)

    removed = []
    for e in exp['experiences']:
        kept = []
        for b in e.get('all_bullets', []):
            if is_non_experience_bullet(b):
                removed.append({
                    'experience': e['title'],
                    'company': e['company'],
                    'title': b.get('title'),
                    'text': b.get('text'),
                })
            else:
                kept.append(b)
        e['all_bullets'] = dedupe(kept)
        master_keys = {key_of(b) for b in e.get('master_bullets', [])}
        e['extra_bullets'] = [b for b in e['all_bullets'] if key_of(b) not in master_keys]

    exp['meta']['finalized_at'] = datetime.now().isoformat()
    exp['meta']['removed_non_experience_bullets'] = len(removed)
    exp['meta']['total_bullet_count'] = sum(len(e.get('all_bullets', [])) for e in exp['experiences'])

    project_bank = {
        'meta': {
            'version': '1.0',
            'generated_at': datetime.now().isoformat(),
            'source': [str(PROJECT_SRC)],
            'count': len(projects.get('bullets', []))
        },
        'project_like_bullets': projects.get('bullets', [])
    }

    FINAL_EXP.write_text(json.dumps(exp, indent=2, ensure_ascii=False), encoding='utf-8')
    FINAL_PROJECT.write_text(json.dumps(project_bank, indent=2, ensure_ascii=False), encoding='utf-8')

    lines = [
        '# Final Database Summary',
        '',
        f"> Generated: {datetime.now().isoformat()}",
        '',
        '## Final Experience Bank',
        f"- **Experience count**: {len(exp['experiences'])}",
        f"- **Total bullets**: {exp['meta']['total_bullet_count']}",
        f"- **Removed non-experience bullets**: {len(removed)}",
        '',
    ]
    for e in exp['experiences']:
        lines.append(f"### {e['title']} — {e['company']}")
        lines.append(f"- **Period**: {e['period']}")
        lines.append(f"- **Master bullets**: {len(e.get('master_bullets', []))}")
        lines.append(f"- **Extra bullets**: {len(e.get('extra_bullets', []))}")
        lines.append(f"- **Total bullets**: {len(e.get('all_bullets', []))}")
        for b in e.get('all_bullets', [])[:8]:
            lines.append(f"  - **{b.get('title','')}** {shorten(b.get('text',''))}")
        lines.append('')

    lines += [
        '## Final Project Bank',
        f"- **Project-like bullet count**: {len(projects.get('bullets', []))}",
        '',
        '## Removed Non-Experience Bullets',
    ]
    for r in removed[:20]:
        lines.append(f"- {r['experience']} / **{r['title']}** {shorten(r['text'], 120)}")
    if len(removed) > 20:
        lines.append(f"- ... and {len(removed)-20} more")

    FINAL_REPORT.write_text('\n'.join(lines), encoding='utf-8')

    print(f'✅ Wrote {FINAL_EXP}')
    print(f'✅ Wrote {FINAL_PROJECT}')
    print(f'✅ Wrote {FINAL_REPORT}')
    for e in exp['experiences']:
        print(f"- {e['title']} | total={len(e.get('all_bullets', []))} | extra={len(e.get('extra_bullets', []))}")
    print(f"Removed non-experience bullets: {len(removed)}")


if __name__ == '__main__':
    main()
