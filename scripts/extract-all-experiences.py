#!/usr/bin/env python3
"""
extract-all-experiences.py - 从所有历史简历中提取完整工作经历
确保 100% 覆盖所有职位和 bullets

Usage:
    python3 extract-all-experiences.py
"""

import json
import re
from pathlib import Path
from datetime import datetime

def extract_from_master():
    """从 MASTER 简历提取完整经历"""
    master_path = Path('/Users/drs/Documents/Obsidian-Vault/9_CV/01-MASTER/resume-master.html')
    content = master_path.read_text(encoding='utf-8')
    
    experiences = []
    
    # 匹配每个 job-entry
    job_pattern = r'\u003cdiv class="job-entry"\u003e(.*?)\u003c/div\u003e\s*\u003c/div\u003e'
    jobs = re.findall(job_pattern, content, re.DOTALL)
    
    for job in jobs:
        # 提取职位信息
        title_match = re.search(r'\u003cdiv class="role-title"\u003e(.+?)\u003c/div\u003e', job)
        company_match = re.search(r'\u003cspan class="company-name"\u003e(.+?)\u003c/span\u003e', job)
        date_match = re.search(r'\u003cdiv class="date-range"\u003e(.+?)\u003c/div\u003e', job)
        
        if title_match and company_match:
            title = title_match.group(1).strip()
            company = company_match.group(1).split('|')[0].strip()
            period = date_match.group(1).strip() if date_match else ""
            
            # 提取 bullets
            bullets = []
            bullet_pattern = r'\u003cli\u003e\u003cstrong\u003e(.+?)\u003c/strong\u003e(.+?)\u003c/li\u003e'
            for bullet_title, bullet_text in re.findall(bullet_pattern, job, re.DOTALL):
                bullets.append({
                    'title': bullet_title.strip(),
                    'text': bullet_text.strip().replace('\n', ' ')
                })
            
            experiences.append({
                'company': company,
                'title': title,
                'period': period,
                'bullets': bullets,
                'source': 'MASTER'
            })
    
    return experiences

def extract_from_database():
    """从当前 database 提取"""
    db_path = Path('/Users/drs/Documents/Obsidian-Vault/9_CV/Database/Eric-Database.json')
    
    if not db_path.exists():
        return []
    
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    experiences = []
    for exp in data.get('experiences', []):
        experiences.append({
            'company': exp['company'],
            'title': exp['title'],
            'period': exp['period'],
            'location': exp.get('location', ''),
            'bullets': [{'title': b['title'], 'text': b['text']} for b in exp.get('bullets', [])],
            'source': 'DATABASE'
        })
    
    return experiences

def extract_from_cv_inventory():
    """从 CV Inventory 的所有 HTML 文件提取"""
    inventory_dir = Path('/Users/drs/Documents/Obsidian-Vault/9_CV/CV_inventory')
    
    all_experiences = []
    
    for html_file in inventory_dir.rglob('*.html'):
        if 'OLD' in str(html_file) or 'cover' in html_file.name.lower():
            continue
        
        try:
            content = html_file.read_text(encoding='utf-8')
            
            # 移除 script/style
            content = re.sub(r'\u003cscript[^\u003e]*\u003e[\s\S]*?\u003c/script\u003e', '', content)
            content = re.sub(r'\u003cstyle[^\u003e]*\u003e[\s\S]*?\u003c/style\u003e', '', content)
            
            # 尝试提取工作经历
            experiences = parse_experiences_from_text(content, html_file.name)
            
            if experiences:
                all_experiences.extend(experiences)
                
        except Exception as e:
            print(f"  Error processing {html_file}: {e}")
    
    return all_experiences

def parse_experiences_from_text(text, filename):
    """从文本解析工作经历"""
    experiences = []
    
    # 模式 1: 职位标题 + 公司 + 日期
    # 例如: "Executive Producer | Final Frontier | 2019-2024"
    job_headers = re.findall(
        r'([A-Z][a-zA-Z\s]+(?:Producer|Manager|Director|Lead))\s*[,|\|]\s*([^|,]+)\s*[,|\|]\s*(\d{4}\s*[–-]\s*(?:\d{4}|Present|Current))',
        text
    )
    
    for title, company, period in job_headers:
        # 提取该职位下的 bullets
        bullets = extract_bullets_near_text(text, company)
        
        experiences.append({
            'company': company.strip(),
            'title': title.strip(),
            'period': period.strip(),
            'bullets': bullets,
            'source': f'CV_Inventory:{filename}'
        })
    
    return experiences

def extract_bullets_near_text(text, company_name):
    """提取公司名附近的 bullets"""
    bullets = []
    
    # 找到公司名位置
    pos = text.find(company_name)
    if pos == -1:
        return bullets
    
    # 提取后面 2000 字符内的 bullets
    section = text[pos:pos+2000]
    
    # 匹配 bullet 模式
    bullet_patterns = [
        r'•\s*([^•\n]{20,200})',
        r'-\s*([^-\n]{20,200})',
        r'\u003cli\u003e\u003cstrong\u003e([^\u003c]+)\u003c/strong\u003e:?\s*([^\u003c]+)\u003c/li\u003e'
    ]
    
    for pattern in bullet_patterns:
        matches = re.findall(pattern, section)
        for match in matches:
            if isinstance(match, tuple):
                title, content = match
                bullets.append({
                    'title': title.strip(),
                    'text': content.strip()
                })
            else:
                text_content = match.strip()
                if ':' in text_content:
                    parts = text_content.split(':', 1)
                    bullets.append({
                        'title': parts[0].strip(),
                        'text': parts[1].strip()
                    })
                else:
                    bullets.append({
                        'title': 'Achievement',
                        'text': text_content
                    })
    
    return bullets[:5]  # 最多 5 个

def merge_experiences(sources):
    """合并所有来源的经历，去重"""
    
    merged = {}
    
    for source_list in sources:
        for exp in source_list:
            key = f"{exp['company']}_{exp['period']}"
            
            if key not in merged:
                merged[key] = exp
            else:
                # 合并 bullets，去重
                existing_titles = {b['title'] for b in merged[key]['bullets']}
                for bullet in exp['bullets']:
                    if bullet['title'] not in existing_titles:
                        merged[key]['bullets'].append(bullet)
                        existing_titles.add(bullet['title'])
                
                # 记录多个来源
                if 'sources' not in merged[key]:
                    merged[key]['sources'] = [merged[key]['source']]
                merged[key]['sources'].append(exp.get('source', 'unknown'))
    
    return list(merged.values())

def generate_complete_database(merged_experiences):
    """生成完整的 database"""
    
    # 按时间排序
    def sort_key(exp):
        period = exp.get('period', '')
        # 提取结束年份
        years = re.findall(r'\d{4}', period)
        if years:
            return -int(years[-1])  # 降序
        return 0
    
    sorted_experiences = sorted(merged_experiences, key=sort_key)
    
    # 构建 database 结构
    database = {
        "meta": {
            "version": "2.0",
            "last_sync": datetime.now().isoformat(),
            "source": "MASTER + DATABASE + CV_Inventory",
            "total_experiences": len(sorted_experiences),
            "total_bullets": sum(len(e['bullets']) for e in sorted_experiences)
        },
        "experiences": []
    }
    
    for idx, exp in enumerate(sorted_experiences, 1):
        exp_data = {
            "id": f"exp-{idx:02d}",
            "company": exp['company'],
            "title": exp['title'],
            "period": exp['period'],
            "location": exp.get('location', 'Shanghai / Global'),
            "type": infer_experience_type(exp),
            "bullets": []
        }
        
        for bidx, bullet in enumerate(exp['bullets'], 1):
            exp_data["bullets"].append({
                "id": f"exp-{idx:02d}-{bidx}",
                "title": bullet['title'],
                "text": bullet['text'],
                "tags": infer_bullet_tags(bullet['title'] + ' ' + bullet['text']),
                "metrics": extract_metrics(bullet['text'])
            })
        
        database["experiences"].append(exp_data)
    
    return database

def infer_experience_type(exp):
    """推断经历类型"""
    text = (exp['company'] + ' ' + exp['title']).lower()
    
    if any(k in text for k in ['film', 'sundance', 'cinema']):
        return 'film'
    elif any(k in text for k in ['agency', 'frontier', 'wpp']):
        return 'agency'
    elif any(k in text for k in ['design', 'studio']):
        return 'studio'
    else:
        return 'production'

def infer_bullet_tags(text):
    """推断 bullet 标签"""
    text_lower = text.lower()
    tags = []
    
    tag_keywords = {
        'film': ['film', 'movie', 'cinema', 'sundance'],
        'financing': ['financ', 'budget', 'fund', '$', 'million'],
        'legal': ['legal', 'contract', 'law', 'compliance'],
        'international': ['international', 'global', 'cross-border', 'china', 'france'],
        'post_production': ['post', 'mastering', 'dcp', 'qc'],
        'leadership': ['lead', 'manage', 'team', 'mentor'],
        'operations': ['operation', 'erp', 'workflow', 'infrastructure'],
        'gaming': ['game', 'gaming', 'tencent', 'riot'],
        'commercial': ['commercial', 'brand', 'campaign'],
        'ai': ['ai', 'openclaw', 'gemini', 'midjourney']
    }
    
    for tag, keywords in tag_keywords.items():
        if any(kw in text_lower for kw in keywords):
            tags.append(tag)
    
    return tags if tags else ['general']

def extract_metrics(text):
    """提取量化指标"""
    metrics = []
    
    # 金额
    money_pattern = r'\$[\d,.]+[KMB]?|\d+\s*(?:million|k)'
    for match in re.finditer(money_pattern, text, re.IGNORECASE):
        metrics.append(match.group())
    
    # 百分比
    percent_pattern = r'\d+%'
    for match in re.finditer(percent_pattern, text):
        metrics.append(match.group())
    
    # 年份
    year_pattern = r'\d{4}'
    years = re.findall(year_pattern, text)
    if years:
        metrics.extend(years[:2])
    
    return list(set(metrics)) if metrics else None

def main():
    print("=" * 70)
    print("完整工作经历提取工具")
    print("=" * 70)
    
    # 1. 从 MASTER 提取
    print("\n📄 从 MASTER 简历提取...")
    master_exps = extract_from_master()
    print(f"   找到 {len(master_exps)} 个职位")
    
    # 2. 从当前 database 提取
    print("\n📊 从当前 database 提取...")
    db_exps = extract_from_database()
    print(f"   找到 {len(db_exps)} 个职位")
    
    # 3. 从 CV Inventory 提取
    print("\n📁 从 CV Inventory 提取...")
    inventory_exps = extract_from_cv_inventory()
    print(f"   找到 {len(inventory_exps)} 个职位记录")
    
    # 4. 合并去重
    print("\n🔀 合并所有来源...")
    all_sources = [master_exps, db_exps, inventory_exps]
    merged = merge_experiences(all_sources)
    print(f"   合并后: {len(merged)} 个唯一职位")
    
    # 5. 生成完整 database
    print("\n💾 生成完整 database...")
    complete_db = generate_complete_database(merged)
    
    # 6. 保存
    output_path = Path('/Users/drs/Documents/Obsidian-Vault/9_CV/Database/Eric-Database-complete.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(complete_db, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 完整 database 已保存: {output_path}")
    print(f"\n统计:")
    print(f"  - 职位数: {complete_db['meta']['total_experiences']}")
    print(f"  - Bullets 总数: {complete_db['meta']['total_bullets']}")
    print(f"  - 平均每职位: {complete_db['meta']['total_bullets'] / complete_db['meta']['total_experiences']:.1f} bullets")
    
    # 7. 生成报告
    report = f"""# 完整工作经历提取报告

> 生成时间: {datetime.now().isoformat()}

## 数据来源
- MASTER 简历: {len(master_exps)} 个职位
- 当前 Database: {len(db_exps)} 个职位
- CV Inventory: {len(inventory_exps)} 个职位记录
- **合并去重后: {len(merged)} 个唯一职位**

## 完整职位列表

"""
    
    for exp in complete_db['experiences']:
        report += f"### {exp['company']} - {exp['title']}\n"
        report += f"- **时间**: {exp['period']}\n"
        report += f"- **类型**: {exp['type']}\n"
        report += f"- **Bullets**: {len(exp['bullets'])}\n"
        for bullet in exp['bullets'][:3]:  # 只显示前3个
            report += f"  - {bullet['title']}\n"
        report += "\n"
    
    report_path = Path('/Users/drs/Documents/Obsidian-Vault/9_CV/Database/complete-experiences-report.md')
    report_path.write_text(report, encoding='utf-8')
    print(f"✅ 报告已保存: {report_path}")
    
    return 0

if __name__ == '__main__':
    exit(main())
