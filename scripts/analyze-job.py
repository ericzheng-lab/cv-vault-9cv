#!/usr/bin/env python3
"""
analyze-job.py - 岗位分析工具
AI 驱动的 JD 分析，提供策略建议供人工确认

Usage:
    python3 analyze-job.py --job /path/to/jd.md
    python3 analyze-job.py --job jd.md --output analysis.md
"""

import json
import re
import argparse
from pathlib import Path
from datetime import datetime

def load_database():
    """加载个人经历数据库"""
    db_path = Path('/Users/drs/Documents/Obsidian-Vault/9_CV/Database/Eric-Database.json')
    with open(db_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_jd_keywords(content):
    """提取 JD 关键词"""
    # 清理文本
    text = re.sub(r'[^\w\s]', ' ', content.lower())
    words = text.split()
    
    # 关键词映射
    keyword_categories = {
        'film': ['film', 'movie', 'cinema', 'director', 'producer', 'production', 'sundance', 'festival'],
        'streaming': ['streaming', 'netflix', 'platform', 'original', 'content', 'series'],
        'gaming': ['game', 'gaming', 'interactive', 'virtual', 'metaverse'],
        'commercial': ['commercial', 'brand', 'campaign', 'advertising', 'marketing'],
        'leadership': ['lead', 'manage', 'team', 'director', 'head', 'vp'],
        'operations': ['operations', 'workflow', 'process', 'efficiency', 'scale'],
        'international': ['global', 'international', 'cross-border', 'multi-cultural'],
        'tech': ['tech', 'digital', 'ai', 'data', 'analytics', 'software', 'machine learning', 'ml', 'generative', 'genai'],
        'ai_tools': ['openclaw', 'gemini', 'midjourney', 'runway', 'ai tool', 'automation'],
        'creative': ['creative', 'vision', 'artistic', 'aesthetic', 'storytelling'],
        'business': ['business', 'strategy', 'growth', 'revenue', 'p&l', 'budget'],
        'research': ['research', 'technical', 'scientific', 'experiment', 'lab']
    }
    
    found_categories = {}
    for category, keywords in keyword_categories.items():
        count = sum(1 for word in words if any(kw in word for kw in keywords))
        if count > 0:
            found_categories[category] = count
    
    return found_categories

def analyze_job_type(categories):
    """分析岗位类型"""
    
    # 检测 AI + 影视交叉岗位
    tech_score = categories.get('tech', 0) + categories.get('ai_tools', 0) + categories.get('research', 0)
    film_score = categories.get('film', 0) + categories.get('creative', 0)
    
    # 如果 tech 和 film 都很高，判定为 ai_film_hybrid
    if tech_score >= 15 and film_score >= 10:
        return ('ai_film_hybrid', tech_score + film_score)
    
    scores = {
        'film_production': categories.get('film', 0) + categories.get('creative', 0) * 0.5,
        'streaming_content': categories.get('streaming', 0) + categories.get('content', 0),
        'gaming_interactive': categories.get('gaming', 0) + categories.get('tech', 0) * 0.5,
        'commercial_agency': categories.get('commercial', 0) + categories.get('brand', 0),
        'operations_management': categories.get('operations', 0) + categories.get('leadership', 0),
        'business_strategy': categories.get('business', 0) + categories.get('strategy', 0),
        'ai_research': categories.get('tech', 0) + categories.get('research', 0) * 2
    }
    
    sorted_types = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_types[0] if sorted_types[0][1] > 0 else ('general', 0)

def match_experiences(database, categories, top_n=5):
    """匹配最相关的经历"""
    matches = []
    
    for exp in database.get('experiences', []):
        for bullet in exp.get('bullets', []):
            bullet_tags = set(bullet.get('tags', []))
            category_tags = set(categories.keys())
            
            # 计算匹配度
            overlap = bullet_tags & category_tags
            score = len(overlap)
            
            if score > 0:
                matches.append({
                    'id': bullet['id'],
                    'company': exp['company'],
                    'title': bullet['title'],
                    'text': bullet['text'][:150] + '...' if len(bullet['text']) > 150 else bullet['text'],
                    'tags': list(bullet_tags),
                    'match_score': score,
                    'matched_tags': list(overlap)
                })
    
    # 按匹配度排序
    matches.sort(key=lambda x: x['match_score'], reverse=True)
    return matches[:top_n]

def match_projects(database, categories, top_n=3):
    """匹配最相关的项目"""
    matches = []
    
    for proj in database.get('projects', []):
        proj_tags = set(proj.get('tags', []))
        category_tags = set(categories.keys())
        
        overlap = proj_tags & category_tags
        score = len(overlap)
        
        if score > 0:
            matches.append({
                'id': proj['id'],
                'title': proj['title'],
                'client': proj.get('client'),
                'budget': proj.get('budget'),
                'tags': list(proj_tags),
                'match_score': score,
                'matched_tags': list(overlap)
            })
    
    matches.sort(key=lambda x: x['match_score'], reverse=True)
    return matches[:top_n]

def generate_strategy(job_type, categories, matches):
    """生成策略建议"""
    strategies = {
        'ai_film_hybrid': {
            'emphasize': ['AI 工具经验 (Openclaw, Gemini, Midjourney, Runway)', '技术-创意桥梁能力', '研究环境制作经验'],
            'downplay': ['纯传统影视制作'],
            'add': ['生成式 AI 工具', '技术团队协作者', '创新实验精神']
        },
        'ai_research': {
            'emphasize': ['AI 工具与自动化', '技术研究背景', '实验性项目'],
            'downplay': ['纯商业执行'],
            'add': ['学术严谨性', '前沿技术敏感度']
        },
        'film_production': {
            'emphasize': ['Sundance/Berlinale 经历', '独立电影制作', '国际合拍'],
            'downplay': ['纯商业广告经验'],
            'add': ['艺术视野', '导演协作', '电影节策略']
        },
        'streaming_content': {
            'emphasize': ['原创 IP 开发', '系列内容制作', '数据驱动决策'],
            'downplay': ['单一项目经验'],
            'add': ['平台思维', '观众洞察', '内容策略']
        },
        'gaming_interactive': {
            'emphasize': ['腾讯/米哈游项目', 'CG 动画', '游戏营销'],
            'downplay': ['传统电影制作'],
            'add': ['互动叙事', '玩家社区', '技术趋势']
        },
        'commercial_agency': {
            'emphasize': ['品牌客户经验', 'Final Frontier', '高预算项目'],
            'downplay': ['独立电影'],
            'add': ['客户管理', '商业思维', '快速交付']
        },
        'operations_management': {
            'emphasize': ['团队管理', '流程优化', '跨地域协调'],
            'downplay': ['纯创意角色'],
            'add': ['领导力', '效率提升', '规模化']
        },
        'business_strategy': {
            'emphasize': ['EMBA', '创始人经验', '商业成果'],
            'downplay': ['执行层面细节'],
            'add': ['战略思维', '增长驱动', '投资回报']
        }
    }
    
    return strategies.get(job_type[0], {
        'emphasize': ['综合制作经验', '跨境能力'],
        'downplay': [],
        'add': ['灵活性', '学习能力']
    })

def generate_analysis_report(jd_content, database):
    """生成完整的分析报告"""
    # 提取关键词
    categories = extract_jd_keywords(jd_content)
    
    # 分析岗位类型
    job_type = analyze_job_type(categories)
    
    # 匹配经历
    exp_matches = match_experiences(database, categories)
    
    # 匹配项目
    proj_matches = match_projects(database, categories)
    
    # 生成策略
    strategy = generate_strategy(job_type, categories, exp_matches)
    
    return {
        'meta': {
            'generated_at': datetime.now().isoformat(),
            'job_type': job_type[0],
            'job_type_score': job_type[1]
        },
        'jd_analysis': {
            'categories': categories,
            'primary_type': job_type[0],
            'type_confidence': job_type[1]
        },
        'matched_experiences': exp_matches,
        'matched_projects': proj_matches,
        'strategy': strategy,
        'recommendations': {
            'summary_focus': strategy['emphasize'][:2],
            'key_bullets': [m['id'] for m in exp_matches[:4]],
            'projects_to_highlight': [p['id'] for p in proj_matches[:2]],
            'skills_to_prioritize': list(categories.keys())[:3]
        }
    }

def format_markdown_report(analysis):
    """格式化为 Markdown 报告"""
    md = f"""# 岗位分析报告

> 生成时间: {analysis['meta']['generated_at']}

---

## 📊 岗位类型判断

**主要类型**: {analysis['jd_analysis']['primary_type'].replace('_', ' ').title()}
**置信度**: {analysis['jd_analysis']['type_confidence']}/10

### 关键词分布

"""
    
    for cat, count in sorted(analysis['jd_analysis']['categories'].items(), key=lambda x: x[1], reverse=True):
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

## 💼 推荐经历 (Top 5)

"""
    
    for i, exp in enumerate(analysis['matched_experiences'], 1):
        md += f"""### {i}. {exp['company']} - {exp['title']}
- **匹配度**: {exp['match_score']}/10
- **匹配标签**: {', '.join(exp['matched_tags'])}
- **内容**: {exp['text']}
- **ID**: `{exp['id']}`

"""
    
    md += """---

## 🎬 推荐项目 (Top 3)

"""
    
    for i, proj in enumerate(analysis['matched_projects'], 1):
        md += f"""### {i}. {proj['title']}
- **匹配度**: {proj['match_score']}/10
- **客户**: {proj['client'] or 'N/A'}
- **预算**: {proj['budget'] or 'N/A'}
- **匹配标签**: {', '.join(proj['matched_tags'])}
- **ID**: `{proj['id']}`

"""
    
    md += f"""---

## ✅ 执行清单

### Summary 重写方向
{chr(10).join(f"- {s}" for s in analysis['recommendations']['summary_focus'])}

### 必用 Bullets
{chr(10).join(f"- [ ] `{b}`" for b in analysis['recommendations']['key_bullets'])}

### 优先展示项目
{chr(10).join(f"- [ ] `{p}`" for p in analysis['recommendations']['projects_to_highlight'])}

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
    
    # 读取 JD
    jd_path = Path(args.job)
    if not jd_path.exists():
        print(f"❌ Error: JD file not found: {jd_path}")
        return 1
    
    jd_content = jd_path.read_text(encoding='utf-8')
    print(f"📖 Reading JD: {jd_path}")
    
    # 加载数据库
    print("📊 Loading database...")
    database = load_database()
    
    # 生成分析
    print("🔍 Analyzing...")
    analysis = generate_analysis_report(jd_content, database)
    
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
