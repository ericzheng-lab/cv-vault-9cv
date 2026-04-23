#!/usr/bin/env python3
"""
analyze-cv-inventory.py - 分析 CV_inventory 中的所有历史简历
提取差异化内容，建立岗位类型映射

Usage:
    python3 analyze-cv-inventory.py
"""

import json
import re
from pathlib import Path
from datetime import datetime

def extract_text_from_html(html_path):
    """从 HTML 提取文本内容"""
    try:
        content = html_path.read_text(encoding='utf-8')
        # 移除 script 和 style
        content = re.sub(r'\u003cscript[^\u003e]*\u003e[\s\S]*?\u003c/script\u003e', '', content)
        content = re.sub(r'\u003cstyle[^\u003e]*\u003e[\s\S]*?\u003c/style\u003e', '', content)
        # 移除 HTML 标签
        content = re.sub(r'\u003c[^\u003e]+\u003e', ' ', content)
        # 清理空白
        content = ' '.join(content.split())
        return content
    except Exception as e:
        print(f"  Error reading {html_path}: {e}")
        return ""

def parse_cv_content(text, company, position):
    """解析简历内容，提取关键部分"""
    
    result = {
        'company': company,
        'position': position,
        'summary': '',
        'competencies': [],
        'experiences': [],
        'job_type': infer_job_type(company, position, text)
    }
    
    # 提取 Summary（通常在开头）
    summary_patterns = [
        r'Professional Summary[:\s]+(.+?)(?=Core Competencies|Professional Experience|$)',
        r'Executive Profile[:\s]+(.+?)(?=Core Competencies|Professional Experience|$)',
        r'Award-winning.+?experience.+?(?=Core Competencies|Professional Experience|$)'
    ]
    
    for pattern in summary_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            result['summary'] = match.group(1).strip()[:500]
            break
    
    # 提取 Competencies
    comp_patterns = [
        r'Core Competencies[:\s]+(.+?)(?=Professional Experience|$)',
        r'Key Skills[:\s]+(.+?)(?=Professional Experience|$)'
    ]
    
    for pattern in comp_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            comp_text = match.group(1)
            # 分割成列表
            comps = re.split(r'[,;•|\n]', comp_text)
            result['competencies'] = [c.strip() for c in comps if len(c.strip()) > 3 and len(c.strip()) < 100][:9]
            break
    
    # 提取关键 bullets（带关键词的）
    bullet_pattern = r'([A-Z][^.:]{3,50}):\s*([^\n]+)'
    bullets = re.findall(bullet_pattern, text)
    
    for title, content in bullets[:10]:
        if len(content.strip()) > 20:
            result['experiences'].append({
                'title': title.strip(),
                'content': content.strip()[:300]
            })
    
    return result

def infer_job_type(company, position, text):
    """推断岗位类型"""
    text_lower = (company + ' ' + position + ' ' + text).lower()
    
    scores = {
        'tech_ai': len(re.findall(r'ai|machine learning|generative|tech|google|amazon|anthropic', text_lower)),
        'gaming': len(re.findall(r'game|gaming|riot|tencent|mihoyo|nintendo', text_lower)),
        'streaming': len(re.findall(r'streaming|netflix|platform|content', text_lower)),
        'film': len(re.findall(r'film|cinema|sundance|berlinale|festival', text_lower)),
        'agency': len(re.findall(r'agency|campaign|brand|wpp|publicis', text_lower)),
        'museum_cultural': len(re.findall(r'museum|cultural|art|brooklyn', text_lower)),
        'luxury': len(re.findall(r'luxury|fashion|ralph lauren|beauty', text_lower))
    }
    
    return max(scores, key=scores.get) if max(scores.values()) > 0 else 'general'

def analyze_cv_inventory():
    """分析 CV_inventory 目录"""
    
    inventory_dir = Path('/Users/drs/Documents/Obsidian-Vault/9_CV/CV_inventory')
    results = []
    
    print("🔍 Scanning CV_inventory...")
    
    # 遍历所有子目录
    for item in inventory_dir.rglob('*'):
        if item.is_file() and item.suffix.lower() in ['.html', '.pdf', '.md']:
            # 跳过 OLD 目录和系统文件
            if 'OLD' in str(item) or item.name.startswith('.') or item.name.startswith('_'):
                continue
            
            # 提取公司和职位信息
            relative_path = item.relative_to(inventory_dir)
            parts = relative_path.parts
            
            company = parts[0] if len(parts) > 1 else 'Unknown'
            
            # 从文件名提取职位
            filename = item.stem
            position = extract_position_from_filename(filename)
            
            print(f"\n📄 {company} / {position}")
            print(f"   File: {item.name}")
            
            # 只处理 HTML 文件（PDF 需要额外工具）
            if item.suffix.lower() == '.html':
                text = extract_text_from_html(item)
                if text:
                    cv_data = parse_cv_content(text, company, position)
                    results.append(cv_data)
                    print(f"   Type: {cv_data['job_type']}")
                    print(f"   Summary: {cv_data['summary'][:80]}...")
                    print(f"   Competencies: {len(cv_data['competencies'])}")
    
    return results

def extract_position_from_filename(filename):
    """从文件名提取职位"""
    # 移除 Eric-Zheng 前缀和后缀
    name = filename.replace('Eric-Zheng_', '').replace('_2026', '').replace('_2025', '')
    name = re.sub(r'[-_]', ' ', name)
    
    # 提取职位关键词
    positions = [
        'Executive Producer', 'Senior Producer', 'Creative Producer',
        'Project Manager', 'Post Production Supervisor', 'Integrated Producer',
        'Senior Creative Producer', 'Producer'
    ]
    
    for pos in positions:
        if pos.lower() in name.lower():
            return pos
    
    return name[:50]

def generate_insights(results):
    """生成洞察报告"""
    
    insights = {
        'total_cvs': len(results),
        'job_types': {},
        'companies': {},
        'common_competencies': {},
        'summaries_by_type': {}
    }
    
    for cv in results:
        # 统计岗位类型
        job_type = cv['job_type']
        insights['job_types'][job_type] = insights['job_types'].get(job_type, 0) + 1
        
        # 统计公司
        company = cv['company']
        insights['companies'][company] = insights['companies'].get(company, 0) + 1
        
        # 统计 competencies
        for comp in cv['competencies']:
            insights['common_competencies'][comp] = insights['common_competencies'].get(comp, 0) + 1
        
        # 按类型分组 summaries
        if cv['summary']:
            if job_type not in insights['summaries_by_type']:
                insights['summaries_by_type'][job_type] = []
            insights['summaries_by_type'][job_type].append(cv['summary'])
    
    return insights

def save_to_database(results, insights):
    """保存到 database"""
    
    output_dir = Path('/Users/drs/Documents/Obsidian-Vault/9_CV/Database')
    output_dir.mkdir(exist_ok=True)
    
    # 保存分析结果
    cv_archive = {
        'meta': {
            'generated_at': datetime.now().isoformat(),
            'total_cvs': len(results),
            'source': 'CV_inventory'
        },
        'cv_versions': results,
        'insights': insights
    }
    
    output_path = output_dir / 'cv-archive.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cv_archive, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Archive saved to: {output_path}")
    
    # 生成 Markdown 报告
    report = generate_markdown_report(insights)
    report_path = output_dir / 'cv-inventory-analysis.md'
    report_path.write_text(report, encoding='utf-8')
    print(f"✅ Report saved to: {report_path}")

def generate_markdown_report(insights):
    """生成 Markdown 分析报告"""
    
    report = f"""# CV Inventory 分析报告

> 生成时间: {datetime.now().isoformat()}

## 概览

- **总简历数**: {insights['total_cvs']}
- **覆盖公司数**: {len(insights['companies'])}
- **岗位类型数**: {len(insights['job_types'])}

## 岗位类型分布

"""
    
    for job_type, count in sorted(insights['job_types'].items(), key=lambda x: x[1], reverse=True):
        report += f"- **{job_type}**: {count} 份\n"
    
    report += "\n## 目标公司分布\n\n"
    for company, count in sorted(insights['companies'].items(), key=lambda x: x[1], reverse=True):
        report += f"- **{company}**: {count} 份\n"
    
    report += "\n## 高频 Competencies\n\n"
    top_comps = sorted(insights['common_competencies'].items(), key=lambda x: x[1], reverse=True)[:15]
    for comp, count in top_comps:
        report += f"- {comp} ({count} 次)\n"
    
    report += "\n## 按岗位类型的 Summary 示例\n\n"
    for job_type, summaries in insights['summaries_by_type'].items():
        if summaries:
            report += f"### {job_type}\n\n"
            report += f"```\n{summaries[0][:300]}...\n```\n\n"
    
    report += """\n## 使用建议\n
### Tech/AI 岗位
- 强调: AI 工具经验、技术-创意桥梁、研究环境
- 关键词: Openclaw, Gemini, Midjourney, generative AI

### Gaming 岗位
- 强调: 游戏项目经验、CG 动画、玩家社区
- 关键词: Tencent, Riot Games, miHoYo, interactive

### Film 岗位
- 强调: Sundance/Berlinale、国际合拍、艺术视野
- 关键词: festival, co-production, director collaboration

### Agency 岗位
- 强调: 品牌客户、高预算项目、快速交付
- 关键词: campaign, client management, margin optimization

### Luxury 岗位
- 强调: 高端品牌经验、审美、细节把控
- 关键词: luxury, fashion, craftsmanship
"""
    
    return report

def main():
    print("=" * 60)
    print("CV Inventory 分析工具")
    print("=" * 60)
    
    # 分析所有简历
    results = analyze_cv_inventory()
    
    if not results:
        print("\n❌ 没有找到可分析的简历文件")
        return 1
    
    print(f"\n📊 分析了 {len(results)} 份简历")
    
    # 生成洞察
    print("\n🔍 生成洞察...")
    insights = generate_insights(results)
    
    # 保存到 database
    print("\n💾 保存到 database...")
    save_to_database(results, insights)
    
    print("\n✅ 完成!")
    return 0

if __name__ == '__main__':
    exit(main())
