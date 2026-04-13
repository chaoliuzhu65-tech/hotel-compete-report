#!/usr/bin/env python3
"""Test grouping logic to verify it works with foreign brands and different price tiers"""

import sys
sys.path.insert(0, '..')
from core.competitor_filter_v2 import HotelPOI, filter_competitors_grouped, FilterConfig, CompetitorScore

# 模拟：目标酒店
target = HotelPOI(
    name="天津瑞湾开元名都大酒店",
    location="117.710212,39.000893",
    star="五星级/豪华型",
    brand="开元名都",
    price=443
)

# 模拟：包含外资高端品牌和不同价位的竞品
candidates = [
    # 外资高端，价格高于1.3×目标
    HotelPOI(name="天津滨海洲际酒店", location="", star="五星级", brand="洲际", price=600, distance_km=3.0),
    HotelPOI(name="天津泰达万豪酒店", location="", star="五星级", brand="万豪", price=650, distance_km=4.5),
    # 外资中端，价格在区间内
    HotelPOI(name="天津希尔顿欢朋", location="", star="四星级", brand="希尔顿", price=350, distance_km=4.0),
    # 内资低价位（低于0.7×）
    HotelPOI(name="如家快捷", location="", star="经济型", brand="如家", price=200, distance_km=2.0),
    HotelPOI(name="7天连锁", location="", star="经济型", brand="7天", price=180, distance_km=2.5),
    # 内资中价位
    HotelPOI(name="天津瑞湾开元大酒店", location="", star="五星级", brand="开元", price=420, distance_km=0.0),
    # 内资高价位
    HotelPOI(name="天津某某豪华酒店", location="", star="超五星级", brand="本地", price=700, distance_km=3.5),
]

# 测试分组
config = FilterConfig(max_distance_km=5)
grouped = filter_competitors_grouped(candidates, target, 443, config=config)

print(f"=== 测试分组结果 ===")
print(f"强相关竞品: {len(grouped.strong_relevant)}")
print(f"外资品牌: {len(grouped.foreign_brands)}, 内资品牌: {len(grouped.domestic_brands)}")
print(f"价格区间: low={len(grouped.by_price_tier['low'])}, mid={len(grouped.by_price_tier['mid'])}, high={len(grouped.by_price_tier['high'])}")

print("\n外资品牌列表:")
for s in grouped.foreign_brands:
    print(f"  - {s.hotel.name}, 价格={s.hotel.price}, 得分={s.total_score}")

print("\n低价位列表:")
for s in grouped.by_price_tier['low']:
    print(f"  - {s.hotel.name}, 价格={s.hotel.price}")

print("\n高价位列表:")
for s in grouped.by_price_tier['high']:
    print(f"  - {s.hotel.name}, 价格={s.hotel.price}")
