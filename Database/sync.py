#!/usr/bin/env python3
"""
sync.py - CV Database Sync Tool
将 Markdown 格式的个人经历数据库同步为结构化 JSON

Usage:
    python sync.py                    # 同步并生成 JSON
    python sync.py --check            # 只检查，不生成
    python sync.py --verbose          # 显示详细信息
"""

import json
import re
import argparse
from pathlib import Path
from datetime import datetime

def parse_work_experience(content):
    """解析工作经历部分"""
    experiences = []
    
    # 匹配每个职位块 - 更宽松的模式
    pattern = r'\*\*([^*]+?)\*\*\s+_([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^_]+)_'
    positions = list(re.finditer(pattern, content))
    
    for i, pos in enumerate(positions):
        title = pos.group(1).strip()
        company = pos.group(2).strip()
        location = pos.group(3).strip()
        period = pos.group(4).strip()
        
        # 提取该职位下的 bullets - 从当前位置到下一个职位或项目部分
        start_pos = pos.end()
        if i + 1 < len(positions):
            end_pos = positions[i + 1].start()
        else:
            # 找下一个主要部分
            next_section = content.find('##', start_pos)
            end_pos = next_section if next_section > 0 else len(content)
        
        section = content[start_pos:end_pos]
        
        bullets = []
        # 匹配 - **Title**: Content 格式
        bullet_pattern = r'-\s+\*\*([^*]+)\*\*[:\s]+(.+?)(?=\n-|\n##|$)'
        for bullet in re.finditer(bullet_pattern, section, re.DOTALL):
            bullet_title = bullet.group(1).strip()
            bullet_text = bullet.group(2).strip()
            # 清理换行和多余空格
            bullet_text = ' '.join(bullet_text.split())
            
            # 生成 ID
            bullet_id = f"{company.lower().replace(' ', '-')[:3]}-{len(bullets)+1}"
            
            # 提取标签
            tags = extract_tags(bullet_title + ' ' + bullet_text)
            
            # 提取 metrics
            metrics = extract_metrics(bullet_text)
            
            bullets.append({
                "id": bullet_id,
                "title": bullet_title,
                "text": bullet_text,
                "tags": tags,
                "metrics": metrics
            })
        
        exp_id = f"{company.lower().replace(' ', '-')[:3]}-{period.replace(' ', '').replace('—', '-')}"
        
        experiences.append({
            "id": exp_id,
            "company": company,
            "title": title,
            "period": period,
            "location": location,
            "type": infer_type(company, title),
            "bullets": bullets
        })
    
    return experiences

def parse_projects(content):
    """解析项目案例部分"""
    projects = []
    
    # 匹配每个项目块
    pattern = r'\*\*\d+\.\s+(.+?)\*\*\s*\n\*\s+\*\*When:\*\*\s*(.+?)\n\*\s+\*\*What:\*\*(.+?)(?=\n\*\s+\*\*Why|$)'
    
    for proj in re.finditer(pattern, content, re.DOTALL):
        title = proj.group(1).strip()
        when = proj.group(2).strip()
        what = proj.group(3).strip()
        
        # 提取项目详情
        proj_section = content[proj.start():proj.end() + 1000]
        
        # 提取 budget
        budget_match = re.search(r'Budget:\s*([^\n]+)', proj_section)
        budget = budget_match.group(1).strip() if budget_match else None
        
        # 提取 client
        client_match = re.search(r'Client:\s*([^\n]+)', what)
        client = client_match.group(1).strip() if client_match else None
        
        # 生成 ID
        proj_id = title.lower().replace(' ', '-')[:20].replace('"', '')
        
        # 提取 tags
        tags = extract_tags(title + ' ' + what)
        
        projects.append({
            "id": proj_id,
            "title": title.replace('"', ''),
            "when": when,
            "client": client,
            "budget": budget,
            "tags": tags
        })
    
    return projects

def parse_skills(content):
    """解析技能部分"""
    skills = {
        "production": [],
        "commercial": [],
        "risk_gov": [],
        "tools": [],
        "languages": []
    }
    
    # 提取 Core Capabilities
    core_pattern = r'\*\*Core Capabilities:\*\*\s*\n(.+?)(?=\*\*Tools|$)'
    core_match = re.search(core_pattern, content, re.DOTALL)
    if core_match:
        core_text = core_match.group(1)
        # 按类别分割
        for line in core_text.split('\n'):
            if 'Production' in line:
                skills["production"] = [s.strip() for s in line.split(':')[1].split(',') if s.strip()]
            elif 'Commercial' in line:
                skills["commercial"] = [s.strip() for s in line.split(':')[1].split(',') if s.strip()]
            elif 'Risk' in line:
                skills["risk_gov"] = [s.strip() for s in line.split(':')[1].split(',') if s.strip()]
    
    # 提取 Tools
    tools_pattern = r'\*\*Tools \& Software:\*\*\s*\n(.+?)(?=\*\*Languages|$)'
    tools_match = re.search(tools_pattern, content, re.DOTALL)
    if tools_match:
        tools_text = tools_match.group(1)
        for line in tools_text.split('\n'):
            if ':' in line:
                tools = [s.strip() for s in line.split(':')[1].split(',') if s.strip()]
                skills["tools"].extend(tools)
    
    # 提取 Languages
    lang_pattern = r'\*\*Languages:\*\*\s*\n(.+?)(?=\*\*|$)'
    lang_match = re.search(lang_pattern, content, re.DOTALL)
    if lang_match:
        lang_text = lang_match.group(1)
        for line in lang_text.split('\n'):
            if ':' in line:
                lang = line.split(':')[0].replace('*', '').strip()
                level = line.split(':')[1].strip()
                skills["languages"].append(f"{lang} ({level})")
    
    return skills

def parse_clients(content):
    """解析客户列表"""
    clients = {}
    
    pattern = r'-\s+\*\*(.+?)\*\*\s*:\s*(.+)'
    for match in re.finditer(pattern, content):
        category = match.group(1).strip().lower().replace(' ', '_')
        client_list = [c.strip() for c in match.group(2).split(',')]
        clients[category] = client_list
    
    return clients

def extract_tags(text):
    """基于关键词提取标签"""
    tag_keywords = {
        "film": ["film", "movie", "cinema", "festival", "sundance", "berlinale"],
        "financing": ["financing", "budget", "fund", "investment", "$"],
        "legal": ["legal", "contract", "law", "ip", "copyright"],
        "international": ["international", "global", "co-production", "china", "france", "denmark"],
        "post_production": ["post-production", "dcp", "mastering", "qc"],
        "gaming": ["game", "gaming", "tencent", "riot", "mihoyo"],
        "commercial": ["commercial", "campaign", "brand", "tvc"],
        "leadership": ["lead", "managed", "team", "mentor"],
        "operations": ["operations", "erp", "workflow", "infrastructure"],
        "cg_animation": ["cg", "animation", "3d", "vfx"],
        "ai": ["ai", "openclaw", "gemini", "midjourney"]
    }
    
    text_lower = text.lower()
    tags = []
    
    for tag, keywords in tag_keywords.items():
        if any(kw in text_lower for kw in keywords):
            tags.append(tag)
    
    return tags

def extract_metrics(text):
    """提取量化指标"""
    metrics = []
    
    # 匹配金额
    money_pattern = r'\$[\d,.]+[KM]?|\d+\s*(?:Million|K)'
    for match in re.finditer(money_pattern, text):
        metrics.append(match.group())
    
    # 匹配百分比
    percent_pattern = r'\d+%'
    for match in re.finditer(percent_pattern, text):
        metrics.append(match.group())
    
    # 匹配时间
    time_pattern = r'\d+\s*(?:years?|months?)'
    for match in re.finditer(time_pattern, text, re.IGNORECASE):
        metrics.append(match.group())
    
    return metrics if metrics else None

def infer_type(company, title):
    """推断经历类型"""
    text = (company + ' ' + title).lower()
    
    if any(kw in text for kw in ['film', 'producer', 'director', 'sundance']):
        return 'film'
    elif any(kw in text for kw in ['agency', 'frontier', 'akqa', 'bbh']):
        return 'agency'
    elif any(kw in text for kw in ['brand', 'luxury', 'fashion']):
        return 'brand'
    else:
        return 'other'

def main():
    parser = argparse.ArgumentParser(description='Sync CV Database')
    parser.add_argument('--check', action='store_true', help='只检查，不生成')
    parser.add_argument('--verbose', '-v', action='store_true', help='显示详细信息')
    args = parser.parse_args()
    
    # 路径
    base_dir = Path('/Users/drs/Documents/Obsidian-Vault/9_CV/Database')
    md_file = base_dir / 'Eric-Database.md'
    json_file = base_dir / 'Eric-Database.json'
    
    if not md_file.exists():
        print(f"❌ 错误: 找不到 {md_file}")
        return 1
    
    # 读取 Markdown
    print(f"📖 读取 {md_file}...")
    content = md_file.read_text(encoding='utf-8')
    
    # 解析各部分
    print("🔍 解析数据...")
    
    experiences = parse_work_experience(content)
    print(f"  ✓ 工作经历: {len(experiences)} 个职位")
    
    projects = parse_projects(content)
    print(f"  ✓ 项目案例: {len(projects)} 个项目")
    
    skills = parse_skills(content)
    print(f"  ✓ 技能: {sum(len(v) for v in skills.values())} 项")
    
    clients = parse_clients(content)
    print(f"  ✓ 客户: {sum(len(v) for v in clients.values())} 个")
    
    # 构建完整数据结构
    database = {
        "meta": {
            "version": "1.0",
            "last_sync": datetime.now().isoformat(),
            "source": "Eric-Database.md"
        },
        "experiences": experiences,
        "projects": projects,
        "skills": skills,
        "clients": clients
    }
    
    if args.check:
        print("\n✅ 检查完成，数据解析正常")
        if args.verbose:
            print(f"\n详细统计:")
            total_bullets = sum(len(e['bullets']) for e in experiences)
            print(f"  - Bullets 总数: {total_bullets}")
            unique_tags = set()
            for e in experiences:
                for b in e.get('bullets', []):
                    unique_tags.update(b.get('tags', []))
            print(f"  - 唯一标签: {len(unique_tags)}")
        return 0
    
    # 生成 JSON
    print(f"\n💾 生成 {json_file}...")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 同步完成!")
    print(f"\n统计:")
    print(f"  📄 Markdown: {md_file.stat().st_size:,} bytes")
    print(f"  📊 JSON: {json_file.stat().st_size:,} bytes")
    print(f"  📝 Bullets: {sum(len(e['bullets']) for e in experiences)}")
    
    return 0

if __name__ == '__main__':
    exit(main())
