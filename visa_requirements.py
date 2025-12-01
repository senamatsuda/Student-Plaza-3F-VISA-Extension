"""
在留期間更新に必要な書類を学生の身分と奨学金状況に応じて案内するシンプルなCLIツール。

使い方:
    python visa_requirements.py --status 正規生 --scenario 現学年・前学期在籍 --scholarship 国費留学生
引数を省略すると、対話式で選択肢を確認しながら入力できます。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


COMMON_REQUIREMENTS: List[str] = [
    "在留期間更新許可申請書（申請人等作成用の3枚 + 所属機関等作成用の2枚）",
    "提出書類一覧表、各在学証明書（両方提出必須。2025年1月申請分から提出が必須）",
    "成績証明書、在学証明書等（証明書のコピーはマスキングせずに提出）",
    "パスポート、在留カード（原本を持参・提示してください）",
    "6,000円分の収入印紙",
]


@dataclass
class Scenario:
    label: str
    requirements: List[str]


STATUS_RULES: Dict[str, List[Scenario]] = {
    "正規生": [
        Scenario(
            label="現学年・前学期在籍",
            requirements=[
                "外国人登録証明書（原本）",
                "成績証明書（前年度または前学期のもの）",
                "在学証明書（在籍期間の記載があるもの）",
            ],
        ),
        Scenario(
            label="前学期未履修（未受験）",
            requirements=[
                "外国人登録証明書（原本）",
                "経費支弁証明書（次のいずれか: 送金証明書／預金残高証明書／授業料免除許可書／奨学金受給証明書〈日本語訳付き〉）",
            ],
        ),
        Scenario(
            label="途中退学（日本語学校から転校）",
            requirements=[
                "外国人登録証明書（原本）",
                "退学証明書（日本語学校からのもの）",
                "在籍証明書（元学校。期間の記載があるもの）",
                "大学進学予定証明書（在学予定校）",
            ],
        ),
    ],
    "研究生": [
        Scenario(
            label="前学期も研究生として在籍",
            requirements=[
                "外国人登録証明書（原本または在留カードの両面コピー。所属学部等の支援室で発行）",
                "前学期の成績証明書（所属の支援室で発行）",
            ],
        ),
        Scenario(
            label="前学期に日本語学校へ在籍",
            requirements=[
                "外国人登録証明書（原本）",
                "日本語学校の在学証明書・成績証明書・出席／在籍証明書（日本語学校で発行）",
            ],
        ),
        Scenario(
            label="前学期に3科目以上を履修（10単位程度）",
            requirements=[
                "外国人登録証明書（原本）",
                "成績証明書（所属の支援室で発行）",
                "在学証明書（所属学部の支援室で発行）",
                "聴講・科目等履修に関する証明書（授業担当者の署名が入ったもの）",
            ],
        ),
    ],
    "特別聴講学生": [
        Scenario(
            label="大学院等へ進学予定（合格済）",
            requirements=[
                "合格通知書のコピーを提出してください",
                "前学期に履修がない場合: 経費支弁証明書（送金証明書など）",
            ],
        ),
        Scenario(
            label="前学期に履修あり",
            requirements=[
                "外国人登録証明書（原本）",
                "成績証明書（前学期のもの）",
                "在学証明書（所属の支援室で発行）",
            ],
        ),
    ],
}


STATUS_OPTIONAL_RULES: Dict[str, List[Scenario]] = {
    "正規生": [
        Scenario(label="標準修業年限を超えて研究する", requirements=["RULE"]),
        Scenario(label="これから進学予定", requirements=["RULE"]),
    ],
    "研究生": [
        Scenario(label="1年以上研究生を続けている", requirements=["RULE"]),
        Scenario(label="大学院進学予定", requirements=["RULE"]),
        Scenario(label="研究継続予定", requirements=["RULE"]),
    ],
}


SCENARIO_OPTIONAL_RULES: Dict[str, Dict[str, List[Scenario]]] = {
    "研究生": {
        "前学期に3科目以上を履修（10単位程度）": [
            Scenario(label="これから研究生になる方", requirements=["RULE"])
        ],
    }
}


SCHOLARSHIP_RULES: Dict[str, List[str]] = {
    "国費留学生": [
        "日本政府奨学金受給証明書（留学交流グループで発行）",
    ],
    "日本政府以外の奨学金受給学生": [
        "奨学金受給証明書（原本。奨学金支援センターなどで発行）",
    ],
    "予約採用奨学金（決定済み）": [
        "自費外国人留学生申請者: 申請用紙（奨学金支援センターで配布）",
        "推薦者記入用: 外国人留学生奨学金受給予定証明書（授業担当教員記入）",
    ],
    "予約採用奨学金（未決定・受給予定なし）": [
        "予約採用内定奨学金がない場合は提出不要です",
    ],
    "奨学金なし": [],
}


def list_options(options: Dict[str, List[Scenario]]) -> str:
    lines: List[str] = []
    for key, scenarios in options.items():
        lines.append(f"{key}:")
        for scenario in scenarios:
            lines.append(f"  - {scenario.label}")
    return "\n".join(lines)


def get_requirements(status: str, scenario_label: str, scholarship: Optional[str]) -> List[str]:
    if status not in STATUS_RULES:
        raise ValueError(f"未対応の身分です: {status}")

    scenarios = STATUS_RULES[status]
    scenario: Optional[Scenario] = next(
        (sc for sc in scenarios if sc.label == scenario_label), None
    )
    if scenario is None:
        valid = ", ".join(sc.label for sc in scenarios)
        raise ValueError(f"シナリオが一致しません: {scenario_label}。候補: {valid}")

    requirements: List[str] = [*COMMON_REQUIREMENTS, *scenario.requirements]

    if scholarship:
        scholarship_requirements = SCHOLARSHIP_RULES.get(
            scholarship, [f"奨学金区分 '{scholarship}' は登録されていません。"]
        )
        requirements.extend(scholarship_requirements)

    return requirements


def interactive_prompt() -> None:
    print("学生の身分を選んでください:")
    for idx, status in enumerate(STATUS_RULES.keys(), start=1):
        print(f"  {idx}. {status}")
    status_choice = input("番号を入力: ").strip()
    status_values = list(STATUS_RULES.keys())
    try:
        status = status_values[int(status_choice) - 1]
    except (ValueError, IndexError):
        raise SystemExit("正しい番号を入力してください。")

    print("\n該当する状況を選んでください:")
    for idx, scenario in enumerate(STATUS_RULES[status], start=1):
        print(f"  {idx}. {scenario.label}")
    scenario_choice = input("番号を入力: ").strip()
    try:
        scenario_label = STATUS_RULES[status][int(scenario_choice) - 1].label
    except (ValueError, IndexError):
        raise SystemExit("正しい番号を入力してください。")

    print("\n奨学金区分を選んでください（該当なしの場合は未入力でEnter）:")
    for idx, scholarship in enumerate(SCHOLARSHIP_RULES.keys(), start=1):
        print(f"  {idx}. {scholarship}")
    scholarship_choice = input("番号を入力（スキップ可）: ").strip()
    scholarship = None
    if scholarship_choice:
        try:
            scholarship = list(SCHOLARSHIP_RULES.keys())[int(scholarship_choice) - 1]
        except (ValueError, IndexError):
            raise SystemExit("正しい番号を入力してください。")

    requirements = get_requirements(status, scenario_label, scholarship)
    print("\n必要な書類一覧:")
    for item in requirements:
        print(f"- {item}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="在留期間更新に必要な書類を表示します。",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--status", help="学生の身分 (例: 正規生, 研究生, 特別聴講学生)")
    parser.add_argument("--scenario", help="該当する状況ラベル")
    parser.add_argument(
        "--scholarship",
        help="奨学金区分 (例: 国費留学生, 日本政府以外の奨学金受給学生, 予約採用奨学金（決定済み）, 奨学金なし)",
    )

    args = parser.parse_args()

    if args.status and args.scenario:
        requirements = get_requirements(args.status, args.scenario, args.scholarship)
        for item in requirements:
            print(f"- {item}")
    else:
        interactive_prompt()
