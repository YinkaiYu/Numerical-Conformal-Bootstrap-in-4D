# parameter_driven_ipo_case_generator.py
# 参数驱动的IPO案例生成器 + LLM智能审核

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

try:
    import pandas as pd
except Exception:  # pragma: no cover - 环境缺少pandas时的兼容处理
    pd = None
try:
    import openai
except Exception:  # pragma: no cover - 环境缺少openai时的兼容处理
    openai = None


class ParameterDrivenIPOGenerator:
    """根据参数生成IPO时间规划表并调用LLM审核"""

    def __init__(self):
        self.base_templates = self._load_base_templates()
        self.variation_rules = self._load_variation_rules()
        self.parameter_schema = self._load_parameter_schema()
        self.llm_client = self._init_llm_client()

    # ------------------------------------------------------------------
    # 初始化与配置
    # ------------------------------------------------------------------
    def _init_llm_client(self):
        if openai and "OPENAI_API_KEY" in os.environ:
            return openai.OpenAI()
        print("⚠️ 警告: 未设置OPENAI_API_KEY或缺少openai库，将跳过LLM审核功能")
        return None

    def _load_parameter_schema(self) -> Dict:
        """加载参数配置架构，新增关键时间节点"""
        return {
            "required_params": {
                "project_profile": {
                    "project_start_date": {
                        "question": "项目启动日期",
                        "type": "date",
                        "format": "YYYY年M月D日当周",
                        "default": "2025年8月4日当周",
                    },
                    "sponsor_agreement_date": {
                        "question": "递交保荐人协议时间",
                        "type": "date",
                        "format": "YYYY年M月D日当周",
                        "default": "2025年8月18日当周",
                    },
                    "equity_reform_base_date": {
                        "question": "股改基准日",
                        "type": "date",
                        "format": "YYYY年M月D日当周",
                        "default": "2025年8月18日当周",
                    },
                    "equity_reform_completion_date": {
                        "question": "股改完成时间",
                        "type": "date",
                        "format": "YYYY年M月D日当周",
                        "default": "2025年10月13日当周",
                    },
                    "a1_submission_date": {
                        "question": "递交A1时间",
                        "type": "date",
                        "format": "YYYY年M月D日当周",
                        "default": "2026年1月12日当周",
                    },
                    "performance_period": {
                        "question": "业绩期时间范围",
                        "type": "string",
                        "default": "2023-2025年",
                    },
                    "project_pace": {
                        "question": "项目节奏",
                        "type": "radio",
                        "options": ["急速推进 (Aggressive)", "标准节奏 (Standard)", "稳健保守 (Cautious)"],
                        "default": "标准节奏 (Standard)",
                    },
                    "listing_board_hk": {
                        "question": "上市板块",
                        "type": "radio",
                        "options": ["主板", "GEM"],
                        "default": "主板",
                    },
                },
                "corporate_profile": {
                    "current_structure": {
                        "question": "公司当前的法律架构",
                        "type": "select",
                        "options": [
                            "境内有限责任公司 (需股改)",
                            "已是境内股份有限公司",
                            "红筹/VIE架构 (已搭建)",
                            "红筹/VIE架构 (需搭建)",
                        ],
                        "default": "境内有限责任公司 (需股改)",
                    },
                    "ipo_readiness": {
                        "question": "IPO准备程度",
                        "type": "multiselect",
                        "options": [
                            "核心中介机构已选聘",
                            "初步的财务梳理/预审",
                            "公司治理结构初步规范",
                            "募投项目已有初步规划",
                            "几乎未开始",
                        ],
                    },
                },
                "financial_profile": {
                    "a1_filing_financials": {
                        "question": "A1包含财务报表期数",
                        "type": "select",
                        "options": [
                            "最近两个完整财年 + 最近一期中期",
                            "最近三个完整财年",
                            "最近三个完整财年 + 最近一期中期",
                        ],
                        "default": "最近三个完整财年",
                    }
                },
                "operational_flags": {
                    "optional_modules": {
                        "question": "专项工作",
                        "type": "multiselect",
                        "options": [
                            "物业/资产评估",
                            "与联交所的上市前沟通",
                            "数据安全与网络安全专项尽调",
                            "员工期权(ESOP)梳理",
                            "IT系统核查",
                            "无",
                        ],
                        "default": [],
                    }
                }
            }
        }

    def _load_base_templates(self) -> Dict:
        """仅保留核心任务及与新增时间节点相关的任务"""
        return {
            "core_tasks": [
                {"工作条线": "项目管理", "任务": "召开项目启动会", "牵头方": "全体", "周偏移": 0},
                {"工作条线": "境内外监管审批", "任务": "定稿保荐人及整体协调人委任函并呈交联交所", "牵头方": "保荐人", "周偏移": 2},
                {"工作条线": "境内外监管审批", "任务": "向联交所递交A1申请", "牵头方": "各方", "周偏移": 23},
            ],
            "equity_reform_tasks": [
                {"工作条线": "股改", "任务": "作出确定股改基准日、股权激励等决议", "牵头方": "公司、公司境内律师", "周偏移": 2},
                {"工作条线": "股改", "任务": "完成股改工作（召开创立大会）", "牵头方": "公司、公司境内律师", "周偏移": 10},
            ],
        }

    def _load_variation_rules(self) -> Dict:
        return {
            "company_structure": {
                "境内有限责任公司 (需股改)": {"add_modules": ["equity_reform_tasks"], "complexity_modifier": 1.1},
                "已是境内股份有限公司": {"add_modules": [], "complexity_modifier": 0.8},
                "红筹/VIE架构 (已搭建)": {"add_modules": [], "complexity_modifier": 0.9},
                "红筹/VIE架构 (需搭建)": {"add_modules": [], "complexity_modifier": 1.3},
            },
            "project_pace": {
                "急速推进 (Aggressive)": {"time_compression": 0.85, "risk_level": "高"},
                "标准节奏 (Standard)": {"time_compression": 1.0, "risk_level": "中"},
                "稳健保守 (Cautious)": {"time_compression": 1.15, "risk_level": "低"},
            },
            "listing_board_hk": {
                "主板": {"description": "主板"},
                "GEM": {"description": "GEM"},
            },
            "a1_filing_financials": {
                "最近两个完整财年 + 最近一期中期": {"audit_complexity": 0.8},
                "最近三个完整财年": {"audit_complexity": 1.0},
                "最近三个完整财年 + 最近一期中期": {"audit_complexity": 1.2},
            },
            "ipo_readiness": {
                "高准备度": {"preparation_factor": 0.9},
                "中等准备度": {"preparation_factor": 1.0},
                "低准备度": {"preparation_factor": 1.2},
            },
        }

    # ------------------------------------------------------------------
    # 工具函数
    # ------------------------------------------------------------------
    def _parse_date(self, date_str: str) -> datetime:
        if "当周" in date_str:
            date_part = date_str.replace("当周", "").replace("年", "-").replace("月", "-").replace("日", "")
            return datetime.strptime(date_part, "%Y-%m-%d")
        return datetime.strptime(date_str, "%Y-%m-%d")

    def _format_date(self, date: datetime) -> str:
        return f"{date.year}年{date.month}月{date.day}日当周"

    def _determine_ipo_readiness_level(self, readiness_list: List[str]) -> str:
        if "几乎未开始" in readiness_list:
            return "低准备度"
        elif len([r for r in readiness_list if r != "几乎未开始"]) >= 3:
            return "高准备度"
        return "中等准备度"

    # ------------------------------------------------------------------
    # 核心时间线生成逻辑
    # ------------------------------------------------------------------
    def generate_case_timeline(self, case_params: Dict) -> Tuple[List[Dict], Dict, Dict]:
        print(f"🚀 正在生成 {case_params.get('case_name', '未命名案例')} 的时间规划...")
        project_start_date = self._parse_date(case_params["project_start_date"])
        sponsor_agreement_date = self._parse_date(case_params["sponsor_agreement_date"])
        equity_base_date = self._parse_date(case_params["equity_reform_base_date"])
        equity_completion_date = self._parse_date(case_params["equity_reform_completion_date"])
        a1_date = self._parse_date(case_params["a1_submission_date"])
        company_structure = case_params.get("current_structure", "境内有限责任公司 (需股改)")
        project_pace = case_params.get("project_pace", "标准节奏 (Standard)")
        listing_board = case_params.get("listing_board_hk", "主板")
        optional_modules = case_params.get("optional_modules", [])
        if "无" in optional_modules:
            optional_modules = []
        ipo_readiness = case_params.get("ipo_readiness", [])
        a1_financials = case_params.get("a1_filing_financials", "最近三个完整财年")
        structure_rules = self.variation_rules["company_structure"][company_structure]
        pace_rules = self.variation_rules["project_pace"][project_pace]
        financial_rules = self.variation_rules["a1_filing_financials"][a1_financials]
        readiness_level = self._determine_ipo_readiness_level(ipo_readiness)
        readiness_rules = self.variation_rules["ipo_readiness"][readiness_level]
        time_factor = pace_rules["time_compression"] * readiness_rules["preparation_factor"]
        complexity_factor = structure_rules["complexity_modifier"] * financial_rules["audit_complexity"]
        tasks = []
        tasks.extend(self.base_templates["core_tasks"])
        for mod in structure_rules["add_modules"]:
            tasks.extend(self.base_templates.get(mod, []))
        timeline = []
        for t in tasks:
            week_offset = max(0, int(t["周偏移"] * time_factor))
            date = project_start_date + timedelta(weeks=week_offset)
            if t["任务"].startswith("定稿保荐人"):
                date = sponsor_agreement_date
            if t["任务"].startswith("作出确定股改基准日"):
                date = equity_base_date
            if t["任务"].startswith("完成股改工作"):
                date = equity_completion_date
            if t["任务"].startswith("向联交所递交A1申请"):
                date = a1_date
            timeline.append({
                "日期": self._format_date(date),
                "工作条线": t["工作条线"],
                "主要任务": t["任务"],
                "牵头方": t["牵头方"],
                "sort_date": date,
            })
        timeline.sort(key=lambda x: x["sort_date"])
        for item in timeline:
            item.pop("sort_date")
        review = self._call_llm_for_review(timeline, case_params)
        report = {
            "案例名称": case_params.get("case_name"),
            "项目参数": case_params,
            "案例特征": {
                "总任务数": len(timeline),
                "公司架构": company_structure,
                "项目节奏": project_pace,
                "上市板块": listing_board,
                "财务报表期数": a1_financials,
                "IPO准备度": readiness_level,
                "复杂度系数": complexity_factor,
                "时间调整系数": time_factor,
            },
            "LLM审核结果": review,
        }
        print(f"✅ {case_params.get('case_name')} 生成完成: {len(timeline)}个任务")
        return timeline, report, review

    # ------------------------------------------------------------------
    # LLM审核与评分（简化实现）
    # ------------------------------------------------------------------
    def _call_llm_for_review(self, timeline: List[Dict], params: Dict) -> Dict:
        if not self.llm_client:
            return {"review_passed": True, "summary": "LLM未启用"}
        try:
            response = self.llm_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "你是一位IPO项目管理专家"},
                    {"role": "user", "content": json.dumps(timeline, ensure_ascii=False)[:4000]},
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"review_passed": True, "summary": f"LLM调用失败: {e}"}

    # ------------------------------------------------------------------
    # 预定义案例与交互
    # ------------------------------------------------------------------
    def generate_predefined_cases(self) -> Dict[str, Tuple[List[Dict], Dict, Dict]]:
        cases = {
            "Case1": {
                "case_name": "Case1 - 标准股改项目",
                "project_start_date": "2025年8月4日当周",
                "sponsor_agreement_date": "2025年8月18日当周",
                "equity_reform_base_date": "2025年8月18日当周",
                "equity_reform_completion_date": "2025年10月13日当周",
                "a1_submission_date": "2026年1月12日当周",
                "performance_period": "2023-2025年",
                "current_structure": "境内有限责任公司 (需股改)",
                "project_pace": "标准节奏 (Standard)",
                "listing_board_hk": "主板",
                "a1_filing_financials": "最近三个完整财年",
                "ipo_readiness": ["初步的财务梳理/预审"],
                "optional_modules": [],
            }
        }
        result = {}
        for k, cfg in cases.items():
            result[k] = self.generate_case_timeline(cfg)
        return result


def main():
    gen = ParameterDrivenIPOGenerator()
    cases = gen.generate_predefined_cases()
    for cid, (timeline, report, review) in cases.items():
        if pd is not None:
            df = pd.DataFrame(timeline)
            print(f"\n{cid} 前几行:\n", df.head())
        else:
            print(f"\n{cid} 前几行:\n", timeline[:5])
    return gen


if __name__ == "__main__":
    main()
