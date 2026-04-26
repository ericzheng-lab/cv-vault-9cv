#!/usr/bin/env python3
"""
Career-Ops Pipeline Runner
每天 7:00 自动触发，或手动执行
"""

import subprocess
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

SCRIPTS_DIR = Path("/Users/drs/Documents/Obsidian-Vault/9_CV/scripts")
CV_DIR = Path("/Users/drs/Documents/Obsidian-Vault/9_CV")
PENDING_DIR = CV_DIR / "03-生成中"
LOG_DIR = CV_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

MAX_PER_RUN = 3


def load_config():
    """从环境变量或配置文件加载 webhook"""
    webhook = os.environ.get("DISCORD_CAREER_WEBHOOK")
    if not webhook:
        config_file = Path.home() / ".oss-config.env"
        if config_file.exists():
            for line in config_file.read_text().splitlines():
                if line.startswith("DISCORD_CAREER_WEBHOOK="):
                    webhook = line.split("=", 1)[1].strip()
                    break
    return webhook


def run_step(cmd, label, extract_json=False):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {label}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=SCRIPTS_DIR)
    if result.returncode != 0:
        print(f"ERROR: {result.stderr}")
        return None
    output = result.stdout.strip() if result.stdout else result.stderr.strip()
    if extract_json:
        lines = output.split('\n')
        json_lines = []
        in_json = False
        for line in lines:
            if line.startswith('{'):
                in_json = True
            if in_json:
                json_lines.append(line)
        output = '\n'.join(json_lines)
    return output


def notify_discord(drafts):
    """发送 Discord 通知"""
    webhook = load_config()
    if not webhook:
        print("没有配置 DISCORD_CAREER_WEBHOOK，跳过通知")
        return

    if not drafts:
        return

    lines = [f"Career-Ops Pipeline 新草稿 ({len(drafts)}份)"]
    for d in drafts:
        lines.append(
            f"• {d['company']} | {d['title']} | {d['branch']} | {d['score']}分"
        )
    lines.append(f"路径：03-生成中/")

    message = "\n".join(lines)
    payload = json.dumps({"content": message}).encode()

    try:
        req = urllib.request.Request(
            webhook,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
        )
        urllib.request.urlopen(req)
        print("Discord 通知已发送")
    except urllib.error.URLError as e:
        print(f"通知发送失败: {e}")


def main():
    log_file = LOG_DIR / f"pipeline-{datetime.now().strftime('%Y%m%d')}.log"
    print(f"=== Career-Ops Pipeline 启动 {datetime.now().isoformat()} ===")

    # 扫描
    run_step(
        [sys.executable, str(SCRIPTS_DIR / "job-scanner.py")],
        "扫描新职位"
    )

    # 检查待处理列表
    pending_file = SCRIPTS_DIR / "pending-jobs.json"
    if not pending_file.exists():
        print("没有新职位，退出")
        return

    with open(pending_file) as f:
        pending = json.load(f)[:MAX_PER_RUN]

    drafts = []
    for job in pending:
        jd_path = job["jd_path"]
        output_dir = job["output_dir"]

        # 评分
        score_out = run_step(
            [sys.executable, str(SCRIPTS_DIR / "job-scorer.py"), "--jd", jd_path],
            f"评分: {job['company']}"
        )
        if not score_out:
            continue
        try:
            score = json.loads(score_out).get("score", 0)
        except json.JSONDecodeError:
            score = 0
        if score < 60:
            print(f"低于阈值({score}分)，跳过")
            continue

        # 分析
        analysis_path = Path(output_dir) / "analysis.json"
        analysis_out = run_step(
            [sys.executable, str(SCRIPTS_DIR / "analyze-job.py"),
             "--job", jd_path, "--json"],
            f"分析: {job['company']}",
            extract_json=True
        )
        # 写入 JSON 文件
        if analysis_out:
            analysis_path.write_text(analysis_out, encoding='utf-8')
        else:
            print(f"WARNING: analysis output empty for {job['company']}")
            continue

        # 生成简历
        run_step(
            [sys.executable, str(SCRIPTS_DIR / "generate-cv.py"),
             "--analysis", str(analysis_path),
             "--output", output_dir],
            f"生成简历: {job['company']}"
        )

        # 读取分支信息用于通知
        try:
            with open(analysis_path) as f:
                analysis = json.load(f)
            branch = analysis.get("job_analysis", {}).get("branch", "unknown")
        except (json.JSONDecodeError, FileNotFoundError):
            branch = "unknown"

        drafts.append({
            "company": job["company"],
            "title": job["title"],
            "branch": branch,
            "score": score
        })

    # 清理本次未达标的空 output_dir（来自 pending-jobs.json 的条目）
    cleaned = []
    for job in pending:
        output_dir = Path(job["output_dir"])
        if output_dir.exists() and not any(output_dir.iterdir()):
            output_dir.rmdir()
            cleaned.append(output_dir.name)
    if cleaned:
        print(f"[清理] 已删除空目录: {', '.join(cleaned)}")

    # 发通知
    if drafts:
        notify_discord(drafts)
        print(f"完成，共 {len(drafts)} 份草稿")
    else:
        print("本次没有达标职位")


if __name__ == "__main__":
    main()