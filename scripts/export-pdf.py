#!/usr/bin/env python3
"""
export-pdf.py - PDF 导出工具
使用 Playwright 将 HTML 简历导出为 PDF

Usage:
    python3 export-pdf.py --html ./netflix/resume.html --output ./netflix/resume.pdf
    python3 export-pdf.py --html ./netflix/resume.html  # 自动推断输出路径
"""

import argparse
import asyncio
from pathlib import Path
from datetime import datetime

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("❌ Error: playwright not installed")
    print("Install with: pip install playwright")
    print("Then run: playwright install chromium")
    exit(1)

async def export_pdf(html_path, output_path, options=None):
    """使用 Playwright 导出 PDF"""
    
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # 加载 HTML
        await page.goto(f'file://{html_path.absolute()}')
        
        # 等待页面加载完成
        await page.wait_for_load_state('networkidle')
        
        # 默认选项
        pdf_options = {
            'format': 'A4',
            'print_background': True,
            'margin': {
                'top': '0mm',
                'right': '0mm', 
                'bottom': '0mm',
                'left': '0mm'
            }
        }
        
        # 合并自定义选项
        if options:
            pdf_options.update(options)
        
        # 导出 PDF
        await page.pdf(path=str(output_path), **pdf_options)
        
        await browser.close()
        
        return output_path

def check_page_count(html_path):
    """检查 HTML 页数（简单估算）"""
    content = html_path.read_text(encoding='utf-8')
    
    # 计算大致字符数
    text_content = len(content)
    
    # A4 页面大约能容纳 3000-4000 字符（取决于格式）
    estimated_pages = max(1, text_content // 3500)
    
    return estimated_pages

def main():
    parser = argparse.ArgumentParser(description='Export HTML resume to PDF')
    parser.add_argument('--html', '-i', required=True, help='Input HTML file')
    parser.add_argument('--output', '-o', help='Output PDF file (default: same name as input)')
    parser.add_argument('--format', '-f', default='A4', help='Paper format (A4, Letter)')
    parser.add_argument('--check-only', action='store_true', help='Only check page count, no export')
    args = parser.parse_args()
    
    html_path = Path(args.html)
    
    if not html_path.exists():
        print(f"❌ Error: HTML file not found: {html_path}")
        return 1
    
    # 检查页数
    estimated_pages = check_page_count(html_path)
    print(f"📄 Estimated pages: {estimated_pages}")
    
    if estimated_pages > 1:
        print("⚠️  Warning: Resume may exceed 1 page")
        print("   Consider:")
        print("   - Reducing bullet points")
        print("   - Shortening descriptions")
        print("   - Removing older experiences")
    
    if args.check_only:
        return 0
    
    # 确定输出路径
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = html_path.with_suffix('.pdf')
    
    # 导出选项
    pdf_options = {
        'format': args.format,
    }
    
    print(f"🚀 Exporting PDF...")
    print(f"   Input: {html_path}")
    print(f"   Output: {output_path}")
    print(f"   Format: {args.format}")
    
    try:
        # 运行异步导出
        asyncio.run(export_pdf(html_path, output_path, pdf_options))
        
        # 检查文件大小
        file_size = output_path.stat().st_size
        print(f"✅ PDF exported successfully!")
        print(f"   Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        print(f"   Path: {output_path.absolute()}")
        
        # 生成记录
        record = f"""# PDF Export Record

**Time**: {datetime.now().isoformat()}
**Source**: {html_path}
**Output**: {output_path}
**Format**: {args.format}
**Estimated Pages**: {estimated_pages}
**File Size**: {file_size:,} bytes

## Status
✅ Export successful
"""
        
        record_path = output_path.parent / 'pdf-export-record.md'
        record_path.write_text(record, encoding='utf-8')
        
        return 0
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        return 1

if __name__ == '__main__':
    exit(main())
