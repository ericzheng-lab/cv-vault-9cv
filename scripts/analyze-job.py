#!/usr/bin/env python3
"""
analyze-job.py - 岗位分析工具 v2.0
AI 驱动的 JD 分析，输出结构化 JSON 供 generate-cv.py 使用

Usage:
    python3 analyze-job.py --job /path/to/jd.md
    python3 analyze-job.py --job jd.md --output analysis.md
    python3 analyze-job.py --job jd.md --json
"""

import json
import re
import argparse
import requests
from pathlib import Path
from datetime import datetime

BASE = Path('/Users/drs/Documents/Obsidian-Vault/9_CV')


def load_database():
    """加载 experience-bank-final.json（与 generate-cv.py 一致）"""
    db_path = BASE / 'Database' / 'experience-bank-final.json'
    with open(db_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_jd_keywords(content):
    """提取 JD 关键词"""
    text = re.sub(r'[^\w\s]', ' ', content.lower())
    words = text.split()

    keyword_categories = {
        'film': ['film', 'movie', 'cinema', 'director', 'producer', 'production', 'sundance', 'festival', 'berlinale', 'cannes', 'tiff'],
        'streaming': ['streaming', 'netflix', 'platform', 'original', 'content', 'series', 'tv'],
        'gaming': ['game', 'gaming', 'interactive', 'virtual', 'metaverse', 'esports', 'player'],
        'commercial': ['commercial', 'brand', 'campaign', 'advertising', 'marketing', 'client', 'agency', 'pr', 'public relations'],
        'leadership': ['lead', 'manage', 'team', 'director', 'head', 'vp', 'executive', 'supervisor'],
        'operations': ['operations', 'workflow', 'process', 'efficiency', 'scale', 'pipeline', 'manage', 'oversee', 'lead', 'logistics', 'scheduling', 'optimize', 'execution', 'planning', 'coordination', 'resource', 'timeline', 'milestone', 'deliverable', 'stakeholder'],
        'international': ['global', 'international', 'cross-border', 'multi-cultural', 'cross-cultural'],
        'tech': ['tech', 'digital', 'ai', 'data', 'analytics', 'software', 'machine learning', 'ml', 'generative', 'genai', 'artificial intelligence'],
        'ai_tools': ['openclaw', 'gemini', 'midjourney', 'runway', 'ai tool', 'automation', 'veo', 'higgsfield'],
        'creative': ['creative', 'vision', 'artistic', 'aesthetic', 'storytelling', 'narrative'],
        'business': ['business', 'strategy', 'growth', 'revenue', 'p&l', 'budget', 'finance'],
        'research': ['research', 'technical', 'scientific', 'experiment', 'lab', 'rd', 'r&d'],
        'media': ['media', 'press', 'journalist', 'publicity', 'outreach', 'communications'],
        'awards': ['award', 'festival strategy', 'fyc', 'campaign', 'prestige', 'academy'],
    }

    found_categories = {}
    for category, keywords in keyword_categories.items():
        count = sum(1 for word in words if any(kw in word for kw in keywords))
        if count > 0:
            found_categories[category] = count

    return found_categories


def analyze_job_branch_llm(jd_text):
    """
    使用 LLM 分析岗位分支（6 分支系统）
    调用上游 API
    """
    prompt = """You are a job classification expert. Read this job description and classify it into exactly one branch: ai_research, gaming, production_ops, agency_pr, film, general.

将职位严格分类为以下六个分支之一。每个分支有排他性特征，必须符合才能归入。

- ai_research：JD 明确涉及 AI/ML 技术研发、模型训练、算法研究；公司主营业务是科技/AI，不是内容公司。
- gaming：公司核心业务是游戏（电子游戏、电竞），不是泛指 entertainment。
- production_ops：电视台、流媒体平台的节目制作运营管理（如 ABC、Netflix、Hulu 内部制作部门），或大型场馆/现场娱乐的制作运营（如 MSG、Live Nation）；涉及 show production、broadcast operations、live event production management 等。
- agency_pr：PR 公关机构或品牌代理；涉及 media relations、client management、press campaigns、awards campaigns、influencer relations。
- film：独立电影行业，电影节，艺术影院发行；不是电视，不是流媒体内容运营。
- general：以上均不符合时使用此兜底。不确定时不走 production_ops，走 general。

重要规则：
- production_ops 不是通用娱乐行业兜底，只适用于电视/流媒体内容制作运营。
- "entertainment company"本身不触发 production_ops，需要有具体的 show production / broadcast 关键词。
- 宁可走 general，不要错走 production_ops。

Return ONLY valid JSON, no other text:
{"branch": "...", "confidence": 0-100, "reason": "one sentence"}

Job Description:
""" + jd_text[:1500]

    try:
        response = requests.post(
            "https://gpt-agent.cc/v1/chat/completions",
            headers={
                "Authorization": "Bearer sk-nrzn3BklQq52gemUnVizNQ3JDGjWu10vQTW0uQmMJO3zgHNx",
                "Content-Type": "application/json"
            },
            json={
                "model": "qwen3.6-plus",
                "max_tokens": 2000,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=60
        )
        text = response.json()["choices"][0]["message"]["content"]
        parsed = json.loads(text)
        branch = parsed.get("branch", "general")
        confidence = parsed.get("confidence", 50)
        reason = parsed.get("reason", "LLM classification")
        return (branch, confidence, reason)
    except Exception as e:
        print(f"⚠️ LLM classification failed: {e}, falling back to keyword-based")
        return ("general", 0, f"Error: {e}")


def get_all_bullets(db):
    """获取 experience-bank 中所有 bullet，用于匹配"""
    all_bullets = []
    for exp in db.get('experiences', []):
        company = exp.get('company', '')
        title = exp.get('title', '')
        for bullet in exp.get('master_bullets', []):
            all_bullets.append({
                'id': bullet['id'],
                'company': company,
                'title': bullet.get('title', ''),
                'text': bullet.get('text', ''),
                'tags': bullet.get('tags', []),
                'metrics': bullet.get('metrics'),
                'exp_title': title,
            })
        for bullet in exp.get('extra_bullets', []):
            all_bullets.append({
                'id': bullet['id'],
                'company': company,
                'title': bullet.get('title', ''),
                'text': bullet.get('text', ''),
                'tags': bullet.get('tags', []),
                'metrics': bullet.get('metrics'),
                'exp_title': title,
            })
    return all_bullets


def match_bullets(all_bullets, categories, top_n=5):
    """匹配最相关的 bullet（基于 tags 重叠）"""
    matches = []
    category_tags = set(categories.keys())

    for bullet in all_bullets:
        bullet_tags = set(bullet.get('tags', []))
        overlap = bullet_tags & category_tags
        score = len(overlap)

        # 加分项
        if bullet.get('metrics'):
            score += 1

        if score > 0:
            matches.append({
                'id': bullet['id'],
                'company': bullet['company'],
                'exp_title': bullet['exp_title'],
                'title': bullet['title'],
                'text': bullet['text'][:150] + '...' if len(bullet['text']) > 150 else bullet['text'],
                'tags': list(bullet_tags),
                'match_score': score,
                'matched_tags': list(overlap),
            })

    matches.sort(key=lambda x: x['match_score'], reverse=True)
    return matches[:top_n]


def generate_strategy(branch_id):
    """生成策略建议"""
    strategies = {
        'ai_research': {
            'emphasize': ['AI 工具经验 (Openclaw, Gemini, Midjourney, Runway)', '技术-创意桥梁能力', '研究环境制作经验'],
            'downplay': ['纯传统影视制作'],
            'add': ['生成式 AI 工具', '技术团队协作者', '创新实验精神']
        },
        'gaming': {
            'emphasize': ['腾讯/米哈游项目', 'CG 动画', '游戏营销'],
            'downplay': ['传统电影制作'],
            'add': ['互动叙事', '玩家社区', '技术趋势']
        },
        'production_ops': {
            'emphasize': ['团队管理', '流程优化', '跨地域协调', '运营效率'],
            'downplay': ['纯创意角色'],
            'add': ['领导力', '效率提升', '规模化', '运营卓越']
        },
        'agency_pr': {
            'emphasize': ['品牌客户经验', 'Final Frontier', '高预算项目', '媒体关系', '电影节策略'],
            'downplay': ['纯技术执行'],
            'add': ['客户管理', '商业思维', '快速交付', '公关策略', '跨文化传播']
        },
        'film': {
            'emphasize': ['Sundance/Berlinale 经历', '独立电影制作', '国际合拍', '电影节策略'],
            'downplay': ['纯商业广告经验'],
            'add': ['艺术视野', '导演协作', '电影节策略', '奖项 campaign']
        },
        'general': {
            'emphasize': ['综合制作经验', '跨境能力', '多格式内容'],
            'downplay': [],
            'add': ['灵活性', '学习能力', '适应性强']
        }
    }

    return strategies.get(branch_id, strategies['general'])


def generate_analysis_report(jd_content, db):
    """生成完整的分析报告"""
    categories = extract_jd_keywords(jd_content)
    branch = analyze_job_branch_llm(jd_content)
    all_bullets = get_all_bullets(db)
    bullet_matches = match_bullets(all_bullets, categories)
    strategy = generate_strategy(branch[0])

    return {
        'meta': {
            'generated_at': datetime.now().isoformat(),
            'version': '2.0',
        },
        'job_analysis': {
            'branch': branch[0],
            'branch_name': branch[2],
            'branch_score': branch[1],
            'categories': categories,
        },
        'jd_text': jd_content[:1500],
        'matched_bullets': bullet_matches,
        'strategy': strategy,
        'recommendations': {
            'summary_focus': strategy['emphasize'][:2],
            'key_bullets': [m['id'] for m in bullet_matches[:4]],
            'skills_to_prioritize': list(categories.keys())[:3]
        }
    }


def format_markdown_report(analysis):
    """格式化为 Markdown 报告"""
    md = f"""# 岗位分析报告

> 生成时间: {analysis['meta']['generated_at']}
> 版本: {analysis['meta']['version']}

---

## 📊 岗位类型判断

**分支**: {analysis['job_analysis']['branch']}
**分支名称**: {analysis['job_analysis']['branch_name']}
**置信度**: {analysis['job_analysis']['branch_score']:.1f}

### 关键词分布

"""

    for cat, count in sorted(analysis['job_analysis']['categories'].items(), key=lambda x: x[1], reverse=True):
        md += f"- **{cat}**: {count} 次\n"

    md += f"""

---

## 🎯 策略建议

### 强调

"""
    for item in analysis['strategy']['emphasize']:
        md += f"- [ ] {item}\n"

    md += "\n### 弱化\n\n"
    for item in analysis['strategy']['downplay']:
        md += f"- [ ] {item}\n"

    md += "\n### 补充\n\n"
    for item in analysis['strategy']['add']:
        md += f"- [ ] {item}\n"

    md += """

---

## 💼 推荐 Bullets (Top 5)

"""

    for i, bullet in enumerate(analysis['matched_bullets'], 1):
        md += f"""### {i}. {bullet['company']} - {bullet['title']}
- **匹配度**: {bullet['match_score']}/10
- **匹配标签**: {', '.join(bullet['matched_tags'])}
- **内容**: {bullet['text']}
- **ID**: `{bullet['id']}`

"""

    md += f"""---

## ✅ 执行清单

### Summary 重写方向
{chr(10).join(f"- {s}" for s in analysis['recommendations']['summary_focus'])}

### 必用 Bullets
{chr(10).join(f"- [ ] `{b}`" for b in analysis['recommendations']['key_bullets'])}

### 技能排序优先
{chr(10).join(f"- {s}" for s in analysis['recommendations']['skills_to_prioritize'])}

---

## 📝 人工调整区

### 我的调整
- [ ] 添加额外经历:
- [ ] 删除推荐经历:
- [ ] 修改策略:
- [ ] 其他:

### 最终确认
- [ ] 分析准确
- [ ] 策略可执行
- [ ] 开始生成简历

"""

    return md


def main():
    parser = argparse.ArgumentParser(description='Analyze job description')
    parser.add_argument('--job', '-j', required=True, help='Path to JD markdown file')
    parser.add_argument('--output', '-o', help='Output markdown file (default: print to stdout)')
    parser.add_argument('--json', action='store_true', help='Output JSON instead of markdown')
    args = parser.parse_args()

    jd_path = Path(args.job)
    if not jd_path.exists():
        print(f"❌ Error: JD file not found: {jd_path}")
        return 1

    jd_content = jd_path.read_text(encoding='utf-8')
    print(f"📖 Reading JD: {jd_path}")

    print("📊 Loading database...")
    db = load_database()

    print("🔍 Analyzing...")
    analysis = generate_analysis_report(jd_content, db)

    # 输出
    if args.json:
        output = json.dumps(analysis, indent=2, ensure_ascii=False)
    else:
        output = format_markdown_report(analysis)

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(output, encoding='utf-8')
        print(f"✅ Analysis saved to: {output_path}")
    else:
        print(output)

    return 0


if __name__ == '__main__':
    exit(main())
