#!/usr/bin/env python3
"""
generate-cv.py - 简历生成工具 v7.0
读 analysis.json，6 分支系统，DRS Films 从 JSON 读取，Profile 4 条结构（2 固定 + 2 LLM 动态）
"""

import json
import os
import argparse
import requests
from pathlib import Path
from datetime import datetime

BASE = Path('/Users/drs/Documents/Obsidian-Vault/9_CV')
DRS_FILMS_JSON = BASE / '04-经验库' / 'drs-films-current.json'

API_URL = "https://gpt-agent.cc/v1/chat/completions"
API_KEY = "sk-nrzn3BklQq52gemUnVizNQ3JDGjWu10vQTW0uQmMJO3zgHNx"

# --- Fixed Profile sentences ---
PROFILE_SENTENCE_1 = (
    "Film and commercial producer with 15+ years of production experience, "
    "now building at the intersection of traditional craft and AI-native systems."
)
PROFILE_SENTENCE_2 = (
    "Led production on Final Frontier, an $8M+ feature-length documentary with "
    "global distribution (Sundance, Berlinale, over 30 international festivals); "
    "managed end-to-end production across commercial, documentary, and narrative formats."
)

# --- Fixed 6 Core Competencies ---
CORE_COMPETENCIES = [
    "AI-Native Production Systems",
    "Multi-Agent Workflow Architecture",
    "End-to-End Film & Commercial Production",
    "Cross-Platform Content Distribution",
    "International Co-Production & Festival Strategy",
    "Budget & Timeline Management ($1M–$10M+)",
]

# --- Fallback sentences for when LLM fails ---
FALLBACK_SENTENCE_3 = {
    "ai_research": "Brings systems-level thinking to AI production workflows, with hands-on experience deploying multi-agent architectures for real creative outputs.",
    "gaming": "Applies AI-native production methods to interactive and gaming contexts, bridging generative tools with narrative production logic.",
    "production_ops": "Integrates AI workflow automation into production operations, reducing manual overhead while maintaining editorial quality standards.",
    "agency_pr": "Leverages AI content distribution systems to scale campaign outputs across platforms without proportional increase in production overhead.",
    "film": "Combines traditional film production discipline with AI-native creative tools, maintaining craft standards across both analog and generative workflows.",
    "general": "Builds AI-augmented production systems that combine generative tooling with production craft for scalable, high-quality creative output.",
}

FALLBACK_SENTENCE_4 = {
    "ai_research": "Production experience managing complex multi-stakeholder projects provides the operational rigor that pure research environments often lack.",
    "gaming": "Cross-format production background (documentary, commercial, narrative) translates directly to managing complex, multi-asset gaming content pipelines.",
    "production_ops": "End-to-end production management experience across budgets, timelines, and international co-productions maps directly to broadcast and streaming operations roles.",
    "agency_pr": "Commercial production background managing client relationships, deliverables, and creative approvals mirrors the agency-client workflow.",
    "film": "Festival circuit experience (Sundance, Berlinale, 30+ international) and distribution background provides direct relevance to independent film and acquisitions contexts.",
    "general": "15+ years managing productions across documentary, commercial, and narrative formats provides a versatile operational foundation for complex creative projects.",
}

# --- Fixed core expertise and tools ---
CORE_EXPERTISE = (
    "Global Financing & Co-Production, Chain of Title & Legal Delivery, "
    "Technical Post & 4.5K Mastering, AI Tool Integration, "
    "Cross-Functional Leadership, Integrated Campaign Delivery, "
    "Vendor & Talent Procurement, SOW & Margin Optimization"
)

TOOLS_SOFTWARE = (
    "Movie Magic Budgeting & Scheduling, Jira (Power User), Asana, Monday.com, "
    "frame.io, Adobe Creative Suite, Openclaw, Google Gemini, Midjourney, "
    "Runway, Higgsfield, Veo, ElevenLabs"
)


def load_database():
    with open(BASE / 'Database' / 'experience-bank-final.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def load_drs_films():
    with open(DRS_FILMS_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_drs_bullets(job_type, drs_data):
    """Select and order DRS Films bullets based on job_type."""
    ids = drs_data["selection_rules"].get(job_type, drs_data["selection_rules"]["general"])
    bullet_map = {b["id"]: b["text"] for b in drs_data["bullets"]["default"]}
    return [bullet_map[bid] for bid in ids if bid in bullet_map]


def parse_analysis_json(analysis_path):
    """读取 analysis.json"""
    with open(analysis_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Also try to get the original JD text if available
    jd_text = data.get('jd_text', '')

    return {
        'job_branch': data['job_analysis']['branch'],
        'key_bullets': data['recommendations']['key_bullets'],
        'jd_text': jd_text,
    }


def generate_dynamic_profile_sentence(job_type, jd_text, sentence_num):
    """
    Use LLM to generate Profile sentence 3 or 4.
    Returns (sentence, used_fallback: bool)
    """
    if sentence_num == 3:
        instruction = f"""You are writing sentence 3 of a resume profile.

RULES:
- Max 35 words
- Start with a verb or noun, never "I"
- One concrete idea per sentence, no list-packing
- Mirror the JD's language, not generic AI buzzwords
- No phrases like "passionate about", "leverage", "synergy"

GOOD EXAMPLES (sentence 3):
[ai_research] "Deployed multi-agent production systems that generate, evaluate, and distribute AI-native video at scale — directly applicable to productionizing generative video and multimodal content pipelines."
[agency_pr] "Built AI systems that accelerate awards-season asset production, media-targeted packaging, and multi-platform campaign distribution — reducing turnaround from days to hours."
[production_ops] "Builds multi-agent systems and AI video workflows that streamline show scheduling, crew coordination, vendor tracking, and live-stream production support across complex venue operations."

BAD EXAMPLES (do not write like this):
- "Built multi-agent AI video pipelines and automated creative workflows that mirror DeepMind's need for scalable generative video systems, multimodal content tooling, and production-ready integration..." [too long, keyword-stuffing]
- "From Sundance/Berlinale festival launches to an $8M+ feature documentary..." [repeats S2 content]

Job type: {job_type}
Job description: {jd_text[:600]}

Write ONE sentence only. Output the sentence directly, no quotes, no explanation."""
    else:
        instruction = f"""You are writing sentence 4 of a resume profile.

RULES:
- Max 35 words
- Start with a verb or noun, never "I"
- One concrete idea per sentence, no list-packing
- Mirror the JD's language, not generic AI buzzwords
- No phrases like "passionate about", "leverage", "synergy"
- Do NOT repeat what sentence 2 already said about Final Frontier

GOOD EXAMPLES (sentence 4):
[ai_research] "Production background in high-stakes, multi-stakeholder projects — Sundance, Berlinale, international co-productions — provides the evaluation rigor and cross-functional coordination that research-to-product pipelines require."
[agency_pr] "Film-release production background — managing talent, studios, deadlines, and deliverables across formats — maps directly to the client-facing, deadline-driven workflow of entertainment PR."
[production_ops] "End-to-end production management across $8M+ budgets, international logistics, and broadcast-ready delivery provides direct operational fluency for large-scale live event and venue production."

BAD EXAMPLES (do not write like this):
- "Built multi-agent AI video pipelines and automated creative workflows that mirror DeepMind's need for scalable generative video systems, multimodal content tooling, and production-ready integration..." [too long, keyword-stuffing]
- "From Sundance/Berlinale festival launches to an $8M+ feature documentary..." [repeats S2 content]

Job type: {job_type}
Job description: {jd_text[:600]}

Write ONE sentence only. Output the sentence directly, no quotes, no explanation."""

    try:
        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "claude-opus-4-6",
                "max_tokens": 200,
                "messages": [{"role": "user", "content": instruction}],
            },
            timeout=30,
        )
        response.raise_for_status()
        msg = response.json()["choices"][0]["message"]
        # qwen3 thinking model may put content in reasoning field
        text = (msg.get("content") or "").strip()
        if not text:
            reasoning = (msg.get("reasoning") or "").strip()
            if reasoning:
                # Strategy 1: find quoted sentence in reasoning
                import re
                quoted = re.findall(r'["\u201c]([A-Z][^"\u201d]{20,})["\u201d]', reasoning)
                if quoted:
                    text = quoted[-1].strip()
                else:
                    # Strategy 2: find last complete sentence (starts uppercase, ends with period)
                    sentences = re.findall(r'([A-Z][^.!?\n]{15,}[.!?])', reasoning)
                    if sentences:
                        text = sentences[-1].strip()
                    else:
                        # Strategy 3: last non-empty line
                        lines = [l.strip() for l in reasoning.split("\n") if l.strip() and len(l.strip()) > 15]
                        if lines:
                            text = lines[-1]
        # Clean up any quotes the model might add
        text = text.strip('"').strip("'").strip('*')
        if len(text) > 10:
            return text, False
    except Exception as e:
        print(f"⚠️ LLM call failed for sentence {sentence_num}: {e}")

    # Fallback
    fallback_map = FALLBACK_SENTENCE_3 if sentence_num == 3 else FALLBACK_SENTENCE_4
    return fallback_map.get(job_type, fallback_map["general"]), True


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


def drs_bullets_html(bullet_texts):
    """Generate HTML for DRS Films bullets."""
    return '\n'.join([
        f'                    <li>{text}</li>'
        for text in bullet_texts
    ])


def fill_template(template, analysis, db):
    job_type = analysis['job_branch']
    jd_text = analysis.get('jd_text', '')

    # --- Profile: 2 fixed + 2 dynamic ---
    sentence_3, fallback_3 = generate_dynamic_profile_sentence(job_type, jd_text, 3)
    sentence_4, fallback_4 = generate_dynamic_profile_sentence(job_type, jd_text, 4)

    fallback_warnings = []
    if fallback_3:
        fallback_warnings.append("条3")
    if fallback_4:
        fallback_warnings.append("条4")

    # --- DRS Films ---
    drs_data = load_drs_films()
    drs_bullet_texts = get_drs_bullets(job_type, drs_data)

    subtitle = 'Executive Producer | Global Creative Operations'

    # --- Experience entries (from experience-bank, DRS Films handled separately) ---
    exps = db.get('experiences', [])
    while len(exps) < 6:
        exps.append({'title': '', 'company': '', 'period': '', 'master_bullets': [], 'extra_bullets': []})

    replacements = {
        '{{HEADER_SUBTITLE}}': subtitle,
        # Profile 4 sentences
        '{{PROFILE_SENTENCE_1}}': PROFILE_SENTENCE_1,
        '{{PROFILE_SENTENCE_2}}': PROFILE_SENTENCE_2,
        '{{PROFILE_SENTENCE_3}}': sentence_3,
        '{{PROFILE_SENTENCE_4}}': sentence_4,
        # 6 Competencies (fixed)
        '{{COMPETENCY_1}}': CORE_COMPETENCIES[0],
        '{{COMPETENCY_2}}': CORE_COMPETENCIES[1],
        '{{COMPETENCY_3}}': CORE_COMPETENCIES[2],
        '{{COMPETENCY_4}}': CORE_COMPETENCIES[3],
        '{{COMPETENCY_5}}': CORE_COMPETENCIES[4],
        '{{COMPETENCY_6}}': CORE_COMPETENCIES[5],
        # Skills
        '{{CORE_EXPERTISE}}': CORE_EXPERTISE,
        '{{TOOLS_SOFTWARE}}': TOOLS_SOFTWARE,
        # DRS Films entry (always first)
        '{{DRS_TITLE}}': drs_data['role'],
        '{{DRS_DATE}}': drs_data['period'],
        '{{DRS_COMPANY}}': f"{drs_data['company']} | {drs_data['location']}",
        '{{DRS_BULLETS}}': drs_bullets_html(drs_bullet_texts),
    }

    # --- Other job entries ---
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
Job Branch: {job_type}
DRS Films Version: {drs_data["version"]}
DRS Bullets: {", ".join(drs_data["selection_rules"].get(job_type, drs_data["selection_rules"]["general"]))}
Profile S3 Fallback: {fallback_3}
Profile S4 Fallback: {fallback_4}
Database: experience-bank-final.json
Template: resume-template-master-locked.html
-->
'''

    for old, new in replacements.items():
        template = template.replace(old, new)

    return template, fallback_warnings


def main():
    parser = argparse.ArgumentParser(description='Generate CV v7.0 — DRS Films JSON + dynamic Profile')
    parser.add_argument('--analysis', '-a', required=True, help='Path to analysis.json')
    parser.add_argument('--output', '-o', required=True, help='Output directory')
    args = parser.parse_args()

    analysis_path = Path(args.analysis)
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("📊 Loading database...")
    db = load_database()

    print("📄 Loading DRS Films data...")
    drs_data = load_drs_films()
    print(f"   DRS Films v{drs_data['version']}: {len(drs_data['bullets']['default'])} bullets, {len(drs_data['selection_rules'])} rules")

    print("🔍 Parsing analysis...")
    analysis = parse_analysis_json(analysis_path)
    job_type = analysis['job_branch']
    print(f"   Branch: {job_type}")

    print("🎨 Generating Profile sentences 3 & 4 via LLM...")
    template_path = BASE / '01-MASTER' / 'resume-template-master-locked.html'
    template = template_path.read_text(encoding='utf-8')
    result, fallback_warnings = fill_template(template, analysis, db)

    out_file = out_dir / 'resume.html'
    out_file.write_text(result, encoding='utf-8')

    # Summary
    drs_ids = drs_data["selection_rules"].get(job_type, drs_data["selection_rules"]["general"])
    summary_text = f"""# 生成摘要

- 时间: {datetime.now().isoformat()}
- Job Branch: {job_type}
- Template: {template_path.name}
- Database: experience-bank-final.json
- DRS Films Version: {drs_data['version']}
- DRS Bullets Selected: {', '.join(drs_ids)}
- Profile S3 Fallback: {'Yes' if fallback_warnings and '条3' in fallback_warnings else 'No'}
- Profile S4 Fallback: {'Yes' if fallback_warnings and '条4' in fallback_warnings else 'No'}
- Positions: {len(db.get('experiences', []))} + DRS Films
"""

    summary = out_dir / 'generation-summary.md'
    summary.write_text(summary_text, encoding='utf-8')

    print(f"✅ Resume generated: {out_file}")
    print(f"✅ Summary generated: {summary}")
    print(f"📋 Job Branch: {job_type}")
    print(f"🏢 DRS Films bullets: {', '.join(drs_ids)}")
    print(f"🎯 Key Bullets: {', '.join(analysis['key_bullets'])}")

    if fallback_warnings:
        warning = f"⚠️ Profile 动态生成失败（{'、'.join(fallback_warnings)}），已使用备用文案 [{job_type}]"
        print(warning)
        return warning  # For pipeline-runner to forward to Discord

    return None


if __name__ == '__main__':
    main()
