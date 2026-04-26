#!/usr/bin/env python3
"""
Job Scorer - 给 JD 评分
低于 60 分的职位不生成简历
"""

import json
import sys
import re
import argparse
from pathlib import Path


def score_jd(jd_path):
    """简单评分：基于关键词匹配"""
    jd_text = Path(jd_path).read_text(encoding='utf-8').lower()

    # 关键词池
    good_keywords = [
        "producer", "production", "executive", "director", "lead", "manager",
        "film", "commercial", "campaign", "content", "creative",
        "experience", "team", "client", "brand",
        "global", "international", "multi", "cross",
        "budget", "revenue", "p&l", "finance",
        "festival", "award", "sundance", "berlinale", "cannes",
        "ai", "ml", "machine learning", "tech",
    ]

    bad_keywords = [
        "intern", "junior", "entry", "unpaid",
    ]

    score = 50  # 基础分

    for kw in good_keywords:
        if kw in jd_text:
            score += 2

    for kw in bad_keywords:
        if kw in jd_text:
            score -= 5

    return min(100, max(0, score))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--jd", required=True)
    args = parser.parse_args()

    score = score_jd(args.jd)
    result = {"score": score, "jd": args.jd}
    print(json.dumps(result))


if __name__ == "__main__":
    main()