#!/usr/bin/env python3
"""
Job Scanner - 扫描待处理职位
目前版本: 扫描 03-待处理 目录下的 JD 文件
"""

import json
import sys
from pathlib import Path

CV_DIR = Path("/Users/drs/Documents/Obsidian-Vault/9_CV")
PENDING_DIR = CV_DIR / "03-待处理"
OUTPUT_DIR = CV_DIR / "03-生成中"
ARCHIVE_DIR = CV_DIR / "04_OUTPUT"


def _get_company_prefix(jd_file_stem):
    """从 JD 文件名提取公司名前缀，用于去重比对"""
    return jd_file_stem.split("-")[0] if "-" in jd_file_stem else jd_file_stem


def _is_duplicate(company_prefix):
    """检查 04_OUTPUT 是否已有该公司简历（公司名前缀匹配）"""
    if not ARCHIVE_DIR.exists():
        return False
    for d in ARCHIVE_DIR.iterdir():
        if d.is_dir():
            dup_prefix = _get_company_prefix(d.name)
            if dup_prefix.lower() == company_prefix.lower():
                return True
    return False


def scan_jobs():
    """扫描待处理目录，返回 JD 列表（排除已处理过的）"""
    if not PENDING_DIR.exists():
        print("[]")
        return []

    jobs = []
    for jd_file in PENDING_DIR.glob("*.md"):
        # 跳过 README 等非 JD 文件
        if jd_file.name.startswith("README"):
            continue
        if jd_file.stem.startswith("."):
            continue

        company_prefix = _get_company_prefix(jd_file.stem)

        # 去重：04_OUTPUT 中已有该公司简历则跳过
        if _is_duplicate(company_prefix):
            print(f"[去重] {company_prefix} 已存在于 04_OUTPUT，跳过")
            continue

        # 生成输出目录
        output_subdir = OUTPUT_DIR / jd_file.stem
        output_subdir.mkdir(parents=True, exist_ok=True)

        jobs.append({
            "jd_path": str(jd_file),
            "company": company_prefix,
            "title": jd_file.stem,
            "output_dir": str(output_subdir)
        })

    return jobs


def main():
    jobs = scan_jobs()
    # 输出 JSON 供 pipeline-runner.py 读取
    print(json.dumps(jobs, ensure_ascii=False))


if __name__ == "__main__":
    main()