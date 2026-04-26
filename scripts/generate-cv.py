#!/usr/bin/env python3
"""
generate-cv.py - 简历生成工具 v6.0
读 analysis.json，6 分支系统，生成定制 HTML 简历
"""

import json
import argparse
from pathlib import Path
from datetime import datetime

BASE = Path('/Users/drs/Documents/Obsidian-Vault/9_CV')


def load_database():
    with open(BASE / 'Database' / 'experience-bank-final.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def parse_analysis_json(analysis_path):
    """读取 analysis.json"""
    with open(analysis_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return {
        'job_branch': data['job_analysis']['branch'],
        'key_bullets': data['recommendations']['key_bullets'],
    }


def generate_dynamic_content(job_branch):
    """6 分支动态内容生成"""

    if job_branch == 'ai_research':
        profile = [
            ('AI-Creative Bridge', 'Award-winning Executive Producer with 15+ years at the intersection of cinematic storytelling and emerging technology. Produced Sundance and Berlinale-selected features while pioneering AI-powered production workflows.'),
            ('Technical Production Expertise', 'Hands-on experience with generative AI tools (Openclaw, Gemini, Midjourney, Runway, Higgsfield, Veo) and ML-integrated pipelines. Proven ability to translate cutting-edge AI capabilities into professional film, TV, and VFX workflows.'),
            ('Global Operations', 'Managed $2.5M+ budgets across international co-productions (China, France, Denmark, Qatar), navigating complex legal, censorship, and technical delivery requirements for Tier-1 theatrical and streaming platforms.')
        ]
        competencies = [
            'AI & Generative Media Tools',
            'Technical-Creative Translation',
            'Research Environment Production',
            'Global Co-Production & Financing',
            'Award-Winning Content Development',
            'Cross-Functional Team Leadership',
            'Emerging Technology Integration',
            'International Legal & Censorship',
            'Executive Production Leadership'
        ]
        core_expertise = 'Global Financing & Co-Production, Chain of Title & Legal Delivery, Technical Post & 4.5K Mastering, AI Tool Integration, Cross-Functional Leadership, Integrated Campaign Delivery, Vendor & Talent Procurement, SOW & Margin Optimization'
        tools_software = 'Movie Magic Budgeting & Scheduling, Jira (Power User), Asana, Monday.com, frame.io, Adobe Creative Suite, Openclaw, Google Gemini, Midjourney, Runway, Higgsfield, Veo'

    elif job_branch == 'gaming':
        profile = [
            ('S-Tier Gaming Production', 'Executive Producer with extensive experience leading high-end CG and animation for top-tier gaming IP including Riot Games, Tencent, miHoYo, and NetEase.'),
            ('Global Studio Orchestration', 'Directed multi-region vendor ecosystems across Europe, South America, and Asia, bridging creative ambition with production discipline for high-pressure game marketing campaigns.'),
            ('Commercial-Technical Leadership', 'Owned complex scoping, budget, and delivery for premium game campaigns, aligning client expectations with studio execution across CG, animation, and post pipelines.')
        ]
        competencies = [
            'Gaming & CG Animation',
            'Global Vendor Management',
            'Cross-Regional Production Leadership',
            'High-End Campaign Delivery',
            'Budgeting & SOW Negotiation',
            'Creative-Technical Translation',
            'Post & Asset Pipeline Oversight',
            'Client Relationship Management',
            'Executive Production Leadership'
        ]
        core_expertise = 'Gaming IP Production, CG Animation Pipeline, Global Vendor Orchestration, Budgeting & P&L Management, Cross-Functional Leadership, Integrated Campaign Delivery, Technical Post Oversight, Client Relationship Strategy'
        tools_software = 'Jira, Asana, Monday.com, SyncSketch, frame.io, Adobe Creative Suite, Movie Magic Budgeting, Unreal Engine (familiar), Various AI Tools'

    elif job_branch == 'production_ops':
        profile = [
            ('Operations-Focused Production Leader', 'Executive Producer with deep expertise in production operations, workflow optimization, and cross-functional team leadership. Proven track record scaling creative operations for high-volume, multi-territory content pipelines.'),
            ('Process & Pipeline Architecture', 'Engineered standardized production workflows across live-action, animation, and VFX. Implemented project management systems (Jira, Asana, Monday.com) that increased team efficiency and reduced delivery variance.'),
            ('Global Resource Coordination', 'Managed distributed production teams across multiple time zones, orchestrating vendors, freelancers, and internal resources to deliver complex projects on scope, on time, and on budget.')
        ]
        competencies = [
            'Production Operations & Workflow',
            'Team Leadership & Development',
            'Process Optimization & Scaling',
            'Budgeting & P&L Management ($6M+)',
            'Cross-Functional Coordination',
            'Vendor & Talent Procurement',
            'Project Management Systems',
            'Risk Mitigation & QC',
            'Executive Production Leadership'
        ]
        core_expertise = 'Production Operations, Workflow Architecture, Team Leadership, Budgeting & P&L Management, Cross-Functional Coordination, Vendor Management, Process Optimization, Risk Mitigation, Quality Control'
        tools_software = 'Jira (Power User), Asana, Monday.com, Movie Magic Budgeting & Scheduling, frame.io, Adobe Creative Suite, ERP/Financial Workflows, Microsoft Office Suite'

    elif job_branch == 'agency_pr':
        profile = [
            ('Festival Strategy & Awards Campaign', 'Film producer and creative executive with 10+ years orchestrating award-winning content from concept to global release. Dual-selected at Sundance Film Festival and Berlinale, with deep fluency in festival strategy, awards campaigns, and prestige press positioning.'),
            ('Client Leadership & Team Development', 'Seasoned production leader and client partner who has managed multi-million-dollar campaigns for global brands (Nike, Tencent, L\'Oréal) while building and mentoring high-performing teams. Adept at navigating complex client relationships and delivering on scope, time, and budget.'),
            ('Media Relations & Cross-Cultural Storytelling', 'Bilingual entertainment strategist with a cultivated network spanning US, European, and Chinese media landscapes. Experience managing international press campaigns, coordinating red-carpet events, and leveraging press relationships for maximum impact.')
        ]
        competencies = [
            'PR Campaign Strategy',
            'Film Festival Strategy',
            'Client Relations & Account Management',
            'Media Outreach & Press Relations',
            'Award Season Campaigning',
            'Brand Partnerships & Co-Marketing',
            'Talent & Team Management',
            'Content Strategy & Narrative',
            'Creative Direction & Innovation'
        ]
        core_expertise = 'PR Campaign Strategy, Film Festival Strategy, Client Relations, Media Outreach, Award Season Campaigning, Brand Partnerships, Talent Management, Content Strategy, Creative Direction, Cross-Cultural Communications'
        tools_software = 'Jira, Asana, Monday.com, Adobe Creative Suite, Cision (familiar), Muck Rack (familiar), Microsoft Office Suite, Google Workspace, Social Media Management Tools'

    elif job_branch == 'film':
        profile = [
            ('Founder-Minded Builder & Operator', 'EMBA-educated Executive Producer with 15+ years of experience specialized in architecting 0-to-1 creative engines. Proven ownership in orchestrating $6M+ global portfolios and securing $2.5M+ in production financing through prestige international backing.'),
            ('Multi-Format Pipeline Architecture', 'Engineered and scaled complex production workflows across live-action features, high-fidelity 3D animation, and VFX. Successfully translated the artistic rigor of international cinema into synchronized global delivery engines.'),
            ('Global Compliance & Technical Delivery', 'Architected cross-border legal and financial frameworks, taking extreme ownership of multi-territory Chain of Title compliance. Directed global post-production pipelines to meet Tier-1 theatrical and digital delivery standards.')
        ]
        competencies = [
            'Global Financing & Co-Production',
            'Chain of Title & Legal Delivery',
            'Technical Post & 4.5K Mastering',
            'Festival Strategy & Awards Campaigns',
            'Budgeting & P&L Management ($6M+)',
            'Regulatory Affairs & Gov. Grants',
            'Creative Workflow Optimization',
            'Vendor & Talent Procurement',
            'SOW & Margin Optimization'
        ]
        core_expertise = 'Global Financing & Co-Production, Chain of Title & Legal Delivery, Technical Post & 4.5K Mastering, Festival Strategy, Budgeting & P&L Management, Cross-Functional Leadership, Integrated Campaign Delivery, Vendor & Talent Procurement, SOW & Margin Optimization'
        tools_software = 'Movie Magic Budgeting & Scheduling, Jira (Power User), Asana, Monday.com, frame.io, Adobe Creative Suite, ERP/Financial Workflows'

    else:  # general
        profile = [
            ('Founder-Minded Builder & Operator', 'EMBA-educated Executive Producer with 15+ years of experience specialized in architecting 0-to-1 creative engines. Proven ownership in orchestrating $6M+ global portfolios and securing $2.5M+ in production financing through prestige international backing.'),
            ('Multi-Format Pipeline Architecture', 'Engineered and scaled complex production workflows across live-action features, high-fidelity 3D animation, and VFX. Successfully translated the artistic rigor of international cinema into synchronized global delivery engines.'),
            ('Global Compliance & Technical Delivery', 'Architected cross-border legal and financial frameworks, taking extreme ownership of multi-territory Chain of Title compliance. Directed global post-production pipelines to meet Tier-1 theatrical and digital delivery standards.')
        ]
        competencies = [
            'Global Financing & Co-Production',
            'Chain of Title & Legal Delivery',
            'Technical Post & 4.5K Mastering',
            'S-Tier Game IP & CG Animation',
            'Budgeting & P&L Management ($6M+)',
            'Regulatory Affairs & Gov. Grants',
            'Creative Workflow Optimization',
            'Vendor & Talent Procurement',
            'SOW & Margin Optimization'
        ]
        core_expertise = 'Global Financing & Co-Production, Chain of Title & Legal Delivery, Technical Post & 4.5K Mastering, Budgeting & P&L Management, Cross-Functional Leadership, Integrated Campaign Delivery, Vendor & Talent Procurement, SOW & Margin Optimization'
        tools_software = 'Movie Magic Budgeting & Scheduling, Jira (Power User), Asana, Monday.com, frame.io, Adobe Creative Suite, ERP/Financial Workflows'

    return profile, competencies, core_expertise, tools_software


def score_bullet(bullet, recommended_ids):
    """评分：推荐 ID 匹配得高分"""
    score = 0
    if bullet.get('id') in recommended_ids:
        score += 100
    score += len(bullet.get('tags', [])) * 2
    if bullet.get('metrics'):
        score += 3
    return score


def select_bullets(exp, recommended_ids, max_bullets=3):
    """从经历中选择最相关的 bullets"""
    candidates = exp.get('master_bullets', []) + exp.get('extra_bullets', [])
    ranked = sorted(candidates, key=lambda b: score_bullet(b, recommended_ids), reverse=True)
    selected = []
    seen = set()
    for b in ranked:
        key = ((b.get('title') or '').strip().lower(), (b.get('text') or '').strip().lower())
        if key in seen:
            continue
        seen.add(key)
        selected.append(b)
        if len(selected) >= max_bullets:
            break
    return selected


def bullets_html(exp, recommended_ids, max_bullets=3):
    selected = select_bullets(exp, recommended_ids, max_bullets)
    return '\n'.join([
        f'                    <li><strong>{b.get("title", "")}</strong> {b.get("text", "")}</li>'
        for b in selected
    ])


def fill_template(template, analysis, db):
    profile, competencies, core_expertise, tools_software = generate_dynamic_content(analysis['job_branch'])

    subtitle = 'Executive Producer | Global Creative Operations'

    exps = db.get('experiences', [])
    while len(exps) < 6:
        exps.append({'title': '', 'company': '', 'period': '', 'master_bullets': [], 'extra_bullets': []})

    replacements = {
        '{{HEADER_SUBTITLE}}': subtitle,
        '{{PROFILE_LABEL_1}}': profile[0][0],
        '{{PROFILE_TEXT_1}}': profile[0][1],
        '{{PROFILE_LABEL_2}}': profile[1][0],
        '{{PROFILE_TEXT_2}}': profile[1][1],
        '{{PROFILE_LABEL_3}}': profile[2][0],
        '{{PROFILE_TEXT_3}}': profile[2][1],
        '{{COMPETENCY_1}}': competencies[0],
        '{{COMPETENCY_2}}': competencies[1],
        '{{COMPETENCY_3}}': competencies[2],
        '{{COMPETENCY_4}}': competencies[3],
        '{{COMPETENCY_5}}': competencies[4],
        '{{COMPETENCY_6}}': competencies[5],
        '{{COMPETENCY_7}}': competencies[6],
        '{{COMPETENCY_8}}': competencies[7],
        '{{COMPETENCY_9}}': competencies[8],
        '{{CORE_EXPERTISE}}': core_expertise,
        '{{TOOLS_SOFTWARE}}': tools_software,
    }

    for i, exp in enumerate(exps[:6], start=1):
        replacements[f'{{{{JOB{i}_TITLE}}}}'] = exp.get('title', '')
        replacements[f'{{{{JOB{i}_DATE}}}}'] = exp.get('period', '')
        company_line = exp.get('company', '')
        if exp.get('location'):
            company_line = f"{company_line} | {exp.get('location')}"
        replacements[f'{{{{JOB{i}_COMPANY}}}}'] = company_line
        replacements[f'{{{{JOB{i}_BULLETS}}}}'] = bullets_html(exp, analysis['key_bullets'], 3)
        if i == 1:
            replacements['{{JOB1_ACHIEVEMENT_BLOCK}}'] = '''            <div class="key-achievement">
                <div class="key-achievement-title"><strong>Key Achievement: Produced Feature Film - "Brief History of A Family" (<a href="https://www.imdb.com/title/tt26749327/" target="_blank">IMDB</a>)</strong></div>
                <ul class="key-achievement-list">
                    <li>First Chinese debut since 2006 to sweep both <strong>Sundance (World Competition)</strong> and <strong>Berlinale (Panorama)</strong>. Secured theatrical distribution in 60+ territories with <strong>92% Rotten Tomatoes</strong> and Metascore 80.</li>
                </ul>
            </div>'''
        else:
            replacements[f'{{{{JOB{i}_ACHIEVEMENT_BLOCK}}}}'] = ''

    replacements['{{GENERATION_INFO}}'] = f'''
<!-- 
Generated: {datetime.now().isoformat()}
Job Branch: {analysis['job_branch']}
Database: experience-bank-final.json
Template: resume-template-master-locked.html
-->
'''

    for old, new in replacements.items():
        template = template.replace(old, new)
    return template


def main():
    parser = argparse.ArgumentParser(description='Generate CV from master-locked template')
    parser.add_argument('--analysis', '-a', required=True, help='Path to analysis.json')
    parser.add_argument('--output', '-o', required=True, help='Output directory')
    args = parser.parse_args()

    analysis_path = Path(args.analysis)
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    db = load_database()
    analysis = parse_analysis_json(analysis_path)
    template_path = BASE / '01-MASTER' / 'resume-template-master-locked.html'
    template = template_path.read_text(encoding='utf-8')
    result = fill_template(template, analysis, db)

    out_file = out_dir / 'resume.html'
    out_file.write_text(result, encoding='utf-8')

    summary = out_dir / 'generation-summary.md'
    summary.write_text(
        f"# 生成摘要\n\n- 时间: {datetime.now().isoformat()}\n- Job Branch: {analysis['job_branch']}\n- Template: {template_path.name}\n- Database: experience-bank-final.json\n- Positions: {len(db.get('experiences', []))}\n",
        encoding='utf-8'
    )

    print(f"✅ Resume generated: {out_file}")
    print(f"✅ Summary generated: {summary}")
    print(f"📋 Job Branch: {analysis['job_branch']}")
    print(f"🎯 Key Bullets: {', '.join(analysis['key_bullets'])}")


if __name__ == '__main__':
    main()
