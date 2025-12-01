"""
Web UI で利用する在留期間更新のデータセットをまとめたモジュール。

身分・状況・奨学金区分ごとに必要書類を整理し、Flask アプリなどの
Web システムからインポートして利用します。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

COMMON_REQUIREMENTS: List[str] = [
    "在留期間更新許可申請書（申請人等作成用の3枚 + 所属機関等作成用の2枚）",
    "提出書類一覧表、各種類確認書（両方提出必須。2025年1月申請分から提出が必須）",
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
            label="前学期も同じ身分で正規生として在籍",
            requirements=[
                "成績証明書（証明書自動発行機で発行）",
                "在学証明書（証明書自動発行機で発行）",
            ],
        ),
        Scenario(
            label="前学期とは異なる身分で正規生として在籍（学部生→修士、修士→博士等）",
            requirements=[
                "成績証明書（証明書自動発行機で発行）",
                "在学証明書（証明書自動発行で発行）",
                "修了証明書（旧所属の支援室で発行）",
            ],
        ),
        Scenario(
            label="前学期、研究生として在籍",
            requirements=[
                "在学証明書（証明書自動発行機で発行）",
                "外国人研究生証明書(別紙様式５)（旧所属の支援室で発行）",
            ],
        ),
        Scenario(
            label="前学期、日本語学校に在籍",
            requirements=[
                "在籍証明書（証明書自動発行機で発行）",
                "成績証明書（日本語学校が発行）",
                "出席・卒業証明書（日本語学校が発行）",
            ],
        ),
        Scenario(
            label="前学期、他大学に在籍",
            requirements=[
                "在籍証明書（証明書自動発行機で発行）",
                "成績証明書（他大学が発行）",
                "卒業証明書（他大学が発行）",
            ],
        ),
    ],
    "研究生": [
        Scenario(
            label="前学期も研究生として在籍",
            requirements=[
                "外国人研究生証明書(別紙様式５)（所属の支援室で発行）",
            ],
        ),
        Scenario(
            label="前学期、日本語学校に在籍",
            requirements=[
                "外国人研究生証明書(別紙様式５)（所属の支援室で発行）",
                "成績証明書（日本語学校が発行）",
                "出席・卒業証明書（日本語学校が発行）",
            ],
        ),
        Scenario(
            label="前学期、他大学に在籍",
            requirements=[
                "外国人研究生証明書(別紙様式５)（所属の支援室で発行）",
                "成績証明書（他大学が発行）",
                "卒業証明書（他大学が発行）",
            ],
        ),
        Scenario(
            label="前学期、3+1特別聴講生(C)として在籍（9月で在留期限が切れる場合）",
            requirements=[
                "外国人研究生証明書(別紙様式５)（所属の支援室で発行）",
                "成績証明書（3+1プログラムの成績）",
            ],
        ),
        Scenario(
            label="前学期、正規生として在籍",
            requirements=[
                "外国人研究生証明書(別紙様式５)（所属の支援室で発行）",
                "成績証明書（旧所属の支援室で発行）",
                "修了証明書（旧所属の支援室で発行）",
            ],
        ),
    ],
    "特別聴講学生": [
        Scenario(
            label="前学期、他大学に在籍",
            requirements=[
                "在学証明書（所属の支援室で発行）",
                "成績証明書（他大学が発行）",
                "卒業証明書（他大学が発行）",
            ],
        ),
        Scenario(
            label="前学期、本学の特別聴講生として在籍",
            requirements=[
                "在学証明書（所属の支援室で発行）",
                "成績証明書（所属の支援室で発行）",
            ],
        ),
    ],
}


STATUS_OPTIONAL_RULES: Dict[str, List[Scenario]] = {
    "正規生": [],
    "研究生": [],
}


SCENARIO_OPTIONAL_RULES: Dict[str, Dict[str, List[Scenario]]] = {}


SCHOLARSHIP_RULES: Dict[str, List[str]] = {
    "国費留学生": ["日本政府奨学金受給証明書（留学交流グループで発行）"],
    "日韓共同理工系学部留学生": ["日韓共同理工系学部留学生奨学金証明書（留学交流グループで発行）"],
    "日本政府以外の給付型の奨学金受給学生": ["奨学金証明書（コピー）"],
    "日本政府以外の貸与型の奨学金受給学生": ["留学生の母国語および日本語で作成された契約書等"],
}


SCHOLARSHIP_STATUS_RULES: Dict[str, List[str]] = {
    "前回申請以降に新たに奨学金を受給": [
        "奨学金決定通知書（財団等が発行。作成できない場合は大学が発行した証明書）",
        "通帳の写し（奨学金の入金が確認できるページ）",
    ],
    "前回申請時に奨学金証明書を提出済み": [
        "通帳の写し（奨学金の入金が確認できるページ）",
    ],
    "前回申請から奨学金を受給していない": [
        "前回の在留申請以降に奨学金の給付がない場合は、奨学金関連書類の提出は不要です。",
    ],
}


def get_requirements(
    status: str,
    scenario_label: str,
    scholarship: Optional[str],
    scholarship_status: Optional[str] = None,
) -> List[str]:
    """指定された条件に一致する必要書類を返します。"""

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

    if scholarship_status:
        requirements.extend(
            SCHOLARSHIP_STATUS_RULES.get(
                scholarship_status,
                [
                    f"奨学金状況 '{scholarship_status}' は登録されていません。",
                ],
            )
        )

    return requirements
