#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水土气声渣排放标准蒸馏器（distill_standards.py）

目标：
- 把《污水综合排放标准》/《大气污染物综合排放标准》/《土壤环境质量标准》/
  《工业企业厂界环境噪声排放标准》/《一般工业固体废物贮存和填埋污染控制标准》等
  核心限值蒸馏成机器可查询的结构化数据，写入 KB（kb_formal.module='standard'）。
- 同时索引到 law_index，方便法条-标准联动；保留 src_id 与 trust_score=0.95。

不联网、不假设外部 PDF；所有原始条目由本脚本常量内置（一次性投料），
后续可由《环保排放标准深度学习》二期扩容。

调用：
    python3 scripts/distill_standards.py
"""

import json
import os
import sqlite3
import sys
import time
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "db", "epb.db")
INDEX_PATH = os.path.join(ROOT, "data", "law_index.json")

# —— 一、水污染（GB 8978-1996 + 2024 新版要点摘录） ————————————————————————
WATER_STANDARDS = [
    {
        "code": "GB 8978-1996",
        "name": "污水综合排放标准",
        "pollutant": "pH",
        "limit_value": "6~9",
        "unit": "无量纲",
        "source": "第一类/第二类污染物最高允许排放浓度",
        "category": "water",
        "level": "通用",
    },
    {
        "code": "GB 8978-1996",
        "name": "污水综合排放标准",
        "pollutant": "COD",
        "limit_value": "100",
        "unit": "mg/L",
        "source": "一级标准",
        "category": "water",
        "level": "一级",
    },
    {
        "code": "GB 8978-1996",
        "name": "污水综合排放标准",
        "pollutant": "氨氮(NH3-N)",
        "limit_value": "15",
        "unit": "mg/L",
        "source": "一级标准",
        "category": "water",
        "level": "一级",
    },
    {
        "code": "GB 8978-1996",
        "name": "污水综合排放标准",
        "pollutant": "总磷",
        "limit_value": "0.5",
        "unit": "mg/L",
        "source": "一级标准（磷含量）",
        "category": "water",
        "level": "一级",
    },
    {
        "code": "GB 8978-1996",
        "name": "污水综合排放标准",
        "pollutant": "总氮",
        "limit_value": "20",
        "unit": "mg/L",
        "source": "一级标准（参照）",
        "category": "water",
        "level": "一级",
    },
    {
        "code": "GB 8978-1996",
        "name": "污水综合排放标准",
        "pollutant": "悬浮物(SS)",
        "limit_value": "70",
        "unit": "mg/L",
        "source": "一级标准",
        "category": "water",
        "level": "一级",
    },
    {
        "code": "GB 8978-1996",
        "name": "污水综合排放标准",
        "pollutant": "石油类",
        "limit_value": "5",
        "unit": "mg/L",
        "source": "一级标准",
        "category": "water",
        "level": "一级",
    },
    {
        "code": "GB 8978-1996",
        "name": "污水综合排放标准",
        "pollutant": "总汞",
        "limit_value": "0.05",
        "unit": "mg/L",
        "source": "第一类污染物最高允许排放浓度",
        "category": "water",
        "level": "第一类",
    },
    {
        "code": "GB 8978-1996",
        "name": "污水综合排放标准",
        "pollutant": "总镉",
        "limit_value": "0.1",
        "unit": "mg/L",
        "source": "第一类污染物",
        "category": "water",
        "level": "第一类",
    },
    {
        "code": "GB 8978-1996",
        "name": "污水综合排放标准",
        "pollutant": "总铬",
        "limit_value": "1.5",
        "unit": "mg/L",
        "source": "第一类污染物",
        "category": "water",
        "level": "第一类",
    },
    {
        "code": "GB 8978-1996",
        "name": "污水综合排放标准",
        "pollutant": "六价铬",
        "limit_value": "0.5",
        "unit": "mg/L",
        "source": "第一类污染物",
        "category": "water",
        "level": "第一类",
    },
    {
        "code": "GB 8978-1996",
        "name": "污水综合排放标准",
        "pollutant": "总铅",
        "limit_value": "1.0",
        "unit": "mg/L",
        "source": "第一类污染物",
        "category": "water",
        "level": "第一类",
    },
    {
        "code": "GB 8978-1996",
        "name": "污水综合排放标准",
        "pollutant": "总砷",
        "limit_value": "0.5",
        "unit": "mg/L",
        "source": "第一类污染物",
        "category": "water",
        "level": "第一类",
    },
]

# —— 二、大气污染（GB 16297-1996 + GB 3095-2012 环境空气质量） ——————————
AIR_STANDARDS = [
    {
        "code": "GB 16297-1996",
        "name": "大气污染物综合排放标准",
        "pollutant": "二氧化硫(SO2)",
        "limit_value": "550",
        "unit": "mg/m³",
        "source": "最高允许排放浓度（二级）",
        "category": "air",
        "level": "二级",
    },
    {
        "code": "GB 16297-1996",
        "name": "大气污染物综合排放标准",
        "pollutant": "氮氧化物(NOx)",
        "limit_value": "420",
        "unit": "mg/m³",
        "source": "最高允许排放浓度（二级）",
        "category": "air",
        "level": "二级",
    },
    {
        "code": "GB 16297-1996",
        "name": "大气污染物综合排放标准",
        "pollutant": "颗粒物",
        "limit_value": "120",
        "unit": "mg/m³",
        "source": "最高允许排放浓度（二级）",
        "category": "air",
        "level": "二级",
    },
    {
        "code": "GB 16297-1996",
        "name": "大气污染物综合排放标准",
        "pollutant": "VOCs(参照非甲烷总烃)",
        "limit_value": "120",
        "unit": "mg/m³",
        "source": "最高允许排放浓度",
        "category": "air",
        "level": "二级",
    },
    {
        "code": "GB 3095-2012",
        "name": "环境空气质量标准",
        "pollutant": "PM2.5",
        "limit_value": "75",
        "unit": "μg/m³",
        "source": "二级浓度限值（24h 平均）",
        "category": "air",
        "level": "二级",
    },
    {
        "code": "GB 3095-2012",
        "name": "环境空气质量标准",
        "pollutant": "PM10",
        "limit_value": "150",
        "unit": "μg/m³",
        "source": "二级浓度限值（24h 平均）",
        "category": "air",
        "level": "二级",
    },
    {
        "code": "GB 3095-2012",
        "name": "环境空气质量标准",
        "pollutant": "SO2",
        "limit_value": "150",
        "unit": "μg/m³",
        "source": "二级浓度限值（1h 平均）",
        "category": "air",
        "level": "二级",
    },
    {
        "code": "GB 3095-2012",
        "name": "环境空气质量标准",
        "pollutant": "NO2",
        "limit_value": "80",
        "unit": "μg/m³",
        "source": "二级浓度限值（1h 平均）",
        "category": "air",
        "level": "二级",
    },
    {
        "code": "GB 3095-2012",
        "name": "环境空气质量标准",
        "pollutant": "O3",
        "limit_value": "160",
        "unit": "μg/m³",
        "source": "二级浓度限值（1h 平均）",
        "category": "air",
        "level": "二级",
    },
    {
        "code": "GB 3095-2012",
        "name": "环境空气质量标准",
        "pollutant": "CO",
        "limit_value": "4",
        "unit": "mg/m³",
        "source": "二级浓度限值（1h 平均）",
        "category": "air",
        "level": "二级",
    },
]

# —— 三、土壤（GB 36600-2018 建设用地土壤污染风险管控标准） ——————————
SOIL_STANDARDS = [
    {
        "code": "GB 36600-2018",
        "name": "土壤环境质量 建设用地土壤污染风险管控标准",
        "pollutant": "镉",
        "limit_value": "20",
        "unit": "mg/kg",
        "source": "筛选值（第一类用地）",
        "category": "soil",
        "level": "筛选值",
    },
    {
        "code": "GB 36600-2018",
        "name": "土壤环境质量 建设用地土壤污染风险管控标准",
        "pollutant": "汞",
        "limit_value": "8",
        "unit": "mg/kg",
        "source": "筛选值（第一类用地）",
        "category": "soil",
        "level": "筛选值",
    },
    {
        "code": "GB 36600-2018",
        "name": "土壤环境质量 建设用地土壤污染风险管控标准",
        "pollutant": "砷",
        "limit_value": "20",
        "unit": "mg/kg",
        "source": "筛选值（第一类用地）",
        "category": "soil",
        "level": "筛选值",
    },
    {
        "code": "GB 36600-2018",
        "name": "土壤环境质量 建设用地土壤污染风险管控标准",
        "pollutant": "铅",
        "limit_value": "400",
        "unit": "mg/kg",
        "source": "筛选值（第一类用地）",
        "category": "soil",
        "level": "筛选值",
    },
    {
        "code": "GB 36600-2018",
        "name": "土壤环境质量 建设用地土壤污染风险管控标准",
        "pollutant": "铬",
        "limit_value": "250",
        "unit": "mg/kg",
        "source": "筛选值（第一类用地）",
        "category": "soil",
        "level": "筛选值",
    },
    {
        "code": "GB 36600-2018",
        "name": "土壤环境质量 建设用地土壤污染风险管控标准",
        "pollutant": "六价铬",
        "limit_value": "3.0",
        "unit": "mg/kg",
        "source": "筛选值（第一类用地）",
        "category": "soil",
        "level": "筛选值",
    },
    {
        "code": "GB 36600-2018",
        "name": "土壤环境质量 建设用地土壤污染风险管控标准",
        "pollutant": "苯",
        "limit_value": "1.0",
        "unit": "mg/kg",
        "source": "筛选值（第一类用地）",
        "category": "soil",
        "level": "筛选值",
    },
]

# —— 四、噪声（GB 12348-2008 工业企业厂界环境噪声排放标准） ——————————
NOISE_STANDARDS = [
    {
        "code": "GB 12348-2008",
        "name": "工业企业厂界环境噪声排放标准",
        "pollutant": "昼间噪声",
        "limit_value": "65",
        "unit": "dB(A)",
        "source": "3 类区",
        "category": "noise",
        "level": "3 类",
    },
    {
        "code": "GB 12348-2008",
        "name": "工业企业厂界环境噪声排放标准",
        "pollutant": "夜间噪声",
        "limit_value": "55",
        "unit": "dB(A)",
        "source": "3 类区",
        "category": "noise",
        "level": "3 类",
    },
    {
        "code": "GB 12348-2008",
        "name": "工业企业厂界环境噪声排放标准",
        "pollutant": "昼间噪声",
        "limit_value": "60",
        "unit": "dB(A)",
        "source": "4 类区（道路交通）",
        "category": "noise",
        "level": "4 类",
    },
    {
        "code": "GB 12348-2008",
        "name": "工业企业厂界环境噪声排放标准",
        "pollutant": "夜间噪声",
        "limit_value": "50",
        "unit": "dB(A)",
        "source": "4 类区（道路交通）",
        "category": "noise",
        "level": "4 类",
    },
]

# —— 五、固废（GB 18599-2020 一般工业固废贮存填埋污染控制标准） —————————
SOLID_WASTE_STANDARDS = [
    {
        "code": "GB 18599-2020",
        "name": "一般工业固体废物贮存和填埋污染控制标准",
        "pollutant": "II 类固废入场含水率",
        "limit_value": "30",
        "unit": "%",
        "source": "入场控制要求",
        "category": "solid_waste",
        "level": "II 类",
    },
    {
        "code": "GB 18599-2020",
        "name": "一般工业固体废物贮存和填埋污染控制标准",
        "pollutant": "II 类固废浸出液 COD",
        "limit_value": "100",
        "unit": "mg/L",
        "source": "浸出液污染物浓度限值",
        "category": "solid_waste",
        "level": "II 类",
    },
    {
        "code": "GB 18599-2020",
        "name": "一般工业固体废物贮存和填埋污染控制标准",
        "pollutant": "II 类固废浸出液氨氮",
        "limit_value": "25",
        "unit": "mg/L",
        "source": "浸出液污染物浓度限值",
        "category": "solid_waste",
        "level": "II 类",
    },
]

ALL_STANDARDS = (
    WATER_STANDARDS
    + AIR_STANDARDS
    + SOIL_STANDARDS
    + NOISE_STANDARDS
    + SOLID_WASTE_STANDARDS
)


def now_iso() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_table(conn: sqlite3.Connection) -> None:
    """kb_formal 已在 init_db 中建好；这里只补 module='standard' 的安全索引。"""
    cur = conn.cursor()
    cur.execute("CREATE INDEX IF NOT EXISTS idx_epb_kb_module ON kb_formal(module)")
    conn.commit()


def build_entry(s: dict, idx: int) -> dict:
    entry_id = f"STD-{s['category']}-{idx:03d}"
    title = f"{s['name']} · {s['pollutant']} 限值（{s['level']}）"
    content = (
        f"依据 {s['code']}《{s['name']}》，"
        f"{s['pollutant']} 限值：{s['limit_value']} {s['unit']}。"
        f"出处：{s['source']}；类别：{s['level']}。"
        f"监测或比对时按此阈值判定超标，触发预警。"
    )
    return {
        "entry_id": entry_id,
        "module": "standard",
        "title": title,
        "content": content,
        "category": s["category"],
        "src_id": s["code"],
        "trust_score": 0.95,
        "tags": json.dumps([s["code"], s["category"], "排放限值", s["level"]], ensure_ascii=False),
        "keywords": ",".join([s["pollutant"], s["code"], s["category"], s["level"]]),
        "summary": f"{s['pollutant']} 限值 {s['limit_value']}{s['unit']}（{s['level']}）",
    }


def upsert(conn: sqlite3.Connection, entry: dict) -> bool:
    cur = conn.cursor()
    cur.execute("SELECT entry_id FROM kb_formal WHERE entry_id=?", (entry["entry_id"],))
    exists = cur.fetchone() is not None
    if exists:
        cur.execute(
            """UPDATE kb_formal SET module=?, title=?, content=?, category=?, src_id=?,
                 tags=?, keywords=?, summary=?, updated_at=CURRENT_TIMESTAMP WHERE entry_id=?""",
            (
                entry["module"],
                entry["title"],
                entry["content"],
                entry["category"],
                entry["src_id"],
                entry["tags"],
                entry["keywords"],
                entry["summary"],
                entry["entry_id"],
            ),
        )
    else:
        cur.execute(
            """INSERT INTO kb_formal(entry_id, module, title, content, category, src_id,
                 trust_score, hit_count, tags, keywords, summary)
                 VALUES (?,?,?,?,?,?,?,0,?,?,?)""",
            (
                entry["entry_id"],
                entry["module"],
                entry["title"],
                entry["content"],
                entry["category"],
                entry["src_id"],
                entry["trust_score"],
                entry["tags"],
                entry["keywords"],
                entry["summary"],
            ),
        )
    return exists


def update_law_index(added_codes: list) -> None:
    """把新蒸馏的标准写进 law_index，方便法条-标准联动。"""
    if not os.path.exists(INDEX_PATH):
        return
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        idx = json.load(f)
    by_code = {row.get("code"): row for row in idx if isinstance(row, dict)}
    for code in added_codes:
        if code in by_code:
            continue
        idx.append(
            {
                "code": code,
                "title": code,
                "type": "标准",
                "issuer": "国家市场监督管理总局/生态环境部",
                "publish_date": "",
                "effective_date": "",
                "tags": ["排放标准", "监督性监测"],
                "trust": 0.95,
            }
        )
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(idx, f, ensure_ascii=False, indent=2)


def main() -> int:
    if not os.path.exists(DB_PATH):
        print(f"[ERR] DB not found: {DB_PATH}", file=sys.stderr)
        return 2
    conn = sqlite3.connect(DB_PATH)
    try:
        ensure_table(conn)
        added_codes: set = set()
        updated = inserted = 0
        for i, s in enumerate(ALL_STANDARDS, start=1):
            entry = build_entry(s, i)
            existed = upsert(conn, entry)
            if existed:
                updated += 1
            else:
                inserted += 1
            added_codes.add(s["code"])
        conn.commit()
        update_law_index(sorted(added_codes))

        # 写一份机器友好的副本，方便前端拉取
        out_json = os.path.join(ROOT, "data", "emission_standards.json")
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "version": time.strftime("%Y.%m%d.%H%M"),
                    "generated_at": now_iso(),
                    "count": len(ALL_STANDARDS),
                    "items": ALL_STANDARDS,
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

        print(
            f"[OK] 标准蒸馏完成: 插入 {inserted} 条，更新 {updated} 条；"
            f"KB 模块 standard 新增 {inserted} 条；law_index 新增 {len(added_codes)} 部标准"
        )
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())