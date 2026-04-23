# 06-CAREER-OPS - career-ops 输出目录

## 说明
career-ops 系统生成的评估报告、定制简历 PDF、以及中间文件存放位置。

## 子目录
- `reports/` - JD 评估报告（A-F 评分）
- `output/` - 生成的 ATS 优化 PDF 简历
- `temp/` - 临时文件

## 与 career-ops 的关系
- career-ops 主目录: `/Users/drs/career-ops/`
- 简历源文件: `/Users/drs/career-ops/cv.md`
- 此目录存放: 评估结果 + 定制简历

## 工作流
1. 扫描门户 → 发现职位
2. 评估 JD → 生成报告 (reports/)
3. 定制简历 → 生成 PDF (output/)
4. 投递 → 记录到 CV_inventory/
