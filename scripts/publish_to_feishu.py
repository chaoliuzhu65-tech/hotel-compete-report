#!/usr/bin/env python3
"""
publish_to_feishu.py - 将生成的Markdown报告批量发布到飞书云文档
用法:
python scripts/publish_to_feishu.py --input test_output/README.md --folder-token <folder_token>

说明:
- 读取README.md中的报告列表
- 逐个读取Markdown文件，创建为飞书云文档
- 在指定飞书云文件夹中创建，不会覆盖原有文件（同名会创建新版本）
- 需要飞书API授权，通过环境变量 FEISHU_APP_ID FEISHU_APP_SECRET 读取
"""

import os
import sys
import argparse
import re
from typing import List, Dict

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from feishu_sdk.client import FeishuClient

def parse_readme(readme_path: str) -> List[Dict]:
    """解析README.md获取所有报告"""
    results = []
    with open(readme_path, "r", encoding="utf-8") as f:
        for line in f:
            # 匹配 "- [酒店名](md_path) → [HTML版本](html_path) 推荐价格 ¥xxx"
            m = re.match(r'^- \[(.*?)\]\((.*?)\).*¥(\d+)', line.strip())
            if m:
                name = m.group(1)
                md_path = m.group(2)
                price = int(m.group(3))
                results.append({
                    "name": name,
                    "md_path": os.path.join(os.path.dirname(readme_path), md_path),
                    "recommended_price": price
                })
    return results

def read_markdown(md_path: str) -> str:
    """读取Markdown内容"""
    with open(md_path, "r", encoding="utf-8") as f:
        return f.read()

def main():
    parser = argparse.ArgumentParser(description="批量发布报告到飞书云文档")
    parser.add_argument("--input", "-i", required=True, help="README.md 文件路径")
    parser.add_argument("--folder-token", "-f", required=False, help="飞书云文件夹token（可选，不传则放根目录）")
    args = parser.parse_args()

    # 读取飞书凭证
    app_id = os.environ.get("FEISHU_APP_ID")
    app_secret = os.environ.get("FEISHU_APP_SECRET")
    if not app_id or not app_secret:
        print("❌ 请设置环境变量 FEISHU_APP_ID 和 FEISHU_APP_SECRET")
        sys.exit(1)

    # 解析报告列表
    reports = parse_readme(args.input)
    print(f"📋 找到 {len(reports)} 份报告准备发布")

    # 初始化飞书客户端
    client = FeishuClient(app_id, app_secret)

    # 逐个发布
    created_urls = []
    for i, report in enumerate(reports):
        print(f"\n🚀 发布 ({i+1}/{len(reports)}): {report['name']}")
        content = read_markdown(report["md_path"])
        title = f"{report['name']} 竞品价格分析报告"

        try:
            result = client.create_doc(
                title=title,
                markdown=content,
                folder_token=args.folder_token
            )
            url = result.get("url")
            print(f"   ✅ 成功: {url}")
            created_urls.append({
                "name": report['name'],
                "url": url
            })
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            continue

    # 输出汇总
    print("\n" + "="*60)
    print(f"✅ 发布完成！共成功 {len(created_urls)}/{len(reports)} 份")
    print("\n📋 发布结果：")
    for item in created_urls:
        print(f"- {item['name']}: {item['url']}")
    print("="*60)

if __name__ == "__main__":
    main()
