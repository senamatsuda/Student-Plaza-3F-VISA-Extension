"""簡易Web UI: 身分と状況を選択して必要書類を確認できます。"""

from __future__ import annotations

import argparse
import json
from typing import Dict, List

from flask import Flask, Response, render_template_string

from visa_requirements import (
    COMMON_REQUIREMENTS,
    SCHOLARSHIP_RULES,
    SCHOLARSHIP_STATUS_RULES,
    SCENARIO_OPTIONAL_RULES,
    STATUS_OPTIONAL_RULES,
    STATUS_RULES,
)

app = Flask(__name__)


def build_status_payload() -> Dict[str, List[Dict[str, List[str]]]]:
    """シリアライズしやすい形で身分・状況データを返す。"""

    return {
        status: [{"label": sc.label, "requirements": sc.requirements} for sc in scenarios]
        for status, scenarios in STATUS_RULES.items()
    }


def build_optional_payload(
    optional_rules: Dict[str, List]
) -> Dict[str, List[Dict[str, List[str]]]]:
    return {
        status: [
            {"label": option.label, "requirements": option.requirements}
            for option in options
        ]
        for status, options in optional_rules.items()
    }


@app.route("/")
def index() -> Response:
    status_payload = build_status_payload()
    status_json = json.dumps(status_payload, ensure_ascii=False)
    status_optional_json = json.dumps(
        build_optional_payload(STATUS_OPTIONAL_RULES), ensure_ascii=False
    )
    scenario_optional_json = json.dumps(
        {
            status: {
                scenario: [
                    {"label": sc.label, "requirements": sc.requirements}
                    for sc in options
                ]
                for scenario, options in scenario_options.items()
            }
            for status, scenario_options in SCENARIO_OPTIONAL_RULES.items()
        },
        ensure_ascii=False,
    )
    scholarship_json = json.dumps(SCHOLARSHIP_RULES, ensure_ascii=False)
    scholarship_status_json = json.dumps(
        SCHOLARSHIP_STATUS_RULES, ensure_ascii=False
    )
    common_json = json.dumps(COMMON_REQUIREMENTS, ensure_ascii=False)

    return render_template_string(
        INDEX_HTML,
        status_json=status_json,
        status_optional_json=status_optional_json,
        scenario_optional_json=scenario_optional_json,
        scholarship_json=scholarship_json,
        scholarship_status_json=scholarship_status_json,
        common_json=common_json,
    )


INDEX_HTML = """
<!doctype html>
<html lang=\"ja\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>在留期間更新 必要書類ナビ</title>
  <style>
    :root { color-scheme: light; }
    body { font-family: system-ui, -apple-system, sans-serif; margin: 2rem; line-height: 1.6; }
    h1 { font-size: 1.6rem; margin-bottom: 0.2rem; }
    .card { max-width: 720px; padding: 1.25rem 1.5rem; border: 1px solid #ddd; border-radius: 12px; box-shadow: 0 6px 20px rgba(0,0,0,0.05); }
    label { display: block; font-weight: 600; margin-top: 1rem; margin-bottom: 0.3rem; }
    select { width: 100%; padding: 0.5rem; font-size: 1rem; border-radius: 6px; border: 1px solid #ccc; }
    button { margin-top: 1rem; padding: 0.65rem 1rem; font-size: 1rem; border-radius: 8px; border: 0; background: #0069d9; color: #fff; cursor: pointer; }
    button:disabled { background: #9ab9e8; cursor: not-allowed; }
    .scenario-pill { background: #f4f7fb; border: 1px solid #d5e1f3; border-radius: 999px; padding: 0.35rem 0.75rem; cursor: pointer; margin-top: 0; }
    .scenario-pill.selected { background: #dbe7ff; border-color: #7da3f9; }
    ul { padding-left: 1.2rem; }
    .muted { color: #555; }
    .hidden { display: none; }
  </style>
</head>
<body>
  <div class=\"card\">
    <h1>在留期間更新に必要な書類</h1>
    <p class=\"muted\">身分・状況・奨学金区分を選ぶと、提出が必要な書類が表示されます。</p>

    <label for=\"status\">身分</label>
    <select id=\"status\">
      <option value=\"\">選択してください</option>
    </select>

    <label for=\"scenario\">状況</label>
    <div id=\"scenario-list\" aria-label=\"状況\" style=\"display: flex; flex-wrap: wrap; gap: 0.5rem;\"></div>

    <div id=\"options\" style=\"margin-top: 0.6rem;\"></div>

  <label for=\"scholarship\">奨学金区分（任意）</label>
  <select id=\"scholarship\">
    <option value=\"\">選択なし</option>
  </select>

  <div id=\"scholarship-status-group\" class=\"hidden\" style=\"margin-top: 0.6rem;\">
    <label for=\"scholarship-status\">奨学金の状況（任意）</label>
    <select id=\"scholarship-status\" disabled>
      <option value=\"\">奨学金区分を先に選んでください</option>
    </select>
  </div>

  <button id=\"show\" disabled>必要書類を表示</button>

    <div id=\"results\" style=\"margin-top: 1.4rem;\"></div>
  </div>

  <script>
    const statusData = {{ status_json | safe }};
    const scholarshipData = {{ scholarship_json | safe }};
    const scholarshipStatusData = {{ scholarship_status_json | safe }};
    const commonRequirements = {{ common_json | safe }};
    const statusOptionalData = {{ status_optional_json | safe }};
    const scenarioOptionalData = {{ scenario_optional_json | safe }};
    const ADVANCEMENT_NOTICE =
      '注意:これから進学予定の場合、所属機関等作成用の2枚はこれから入学する予定の支援室に発行してもらう必要があります。<br />そのため、入学手続き期間内に入学料を納めてから、支援室に発行を依頼してください。';
    const nonGovScholarships = [
      "日本政府以外の給付型の奨学金受給学生",
      "日本政府以外の貸与型の奨学金受給学生",
    ];

    const statusSelect = document.getElementById('status');
    const scenarioList = document.getElementById('scenario-list');
    const scholarshipSelect = document.getElementById('scholarship');
    const scholarshipStatusGroup = document.getElementById('scholarship-status-group');
    const scholarshipStatusSelect = document.getElementById('scholarship-status');
    const showButton = document.getElementById('show');
    const results = document.getElementById('results');
    const optionsContainer = document.getElementById('options');

    function populateStatuses() {
      Object.keys(statusData).forEach((status) => {
        const option = document.createElement('option');
        option.value = status;
        option.textContent = status;
        statusSelect.appendChild(option);
      });
    }

    function populateScholarships() {
      Object.keys(scholarshipData).forEach((key) => {
        const option = document.createElement('option');
        option.value = key;
        option.textContent = key;
        scholarshipSelect.appendChild(option);
      });
    }

    function populateScholarshipStatuses() {
      Object.keys(scholarshipStatusData).forEach((key) => {
        const option = document.createElement('option');
        option.value = key;
        option.textContent = key;
        scholarshipStatusSelect.appendChild(option);
      });
    }

    let selectedScenarios = new Set();

    function renderOptions() {
      optionsContainer.innerHTML = '';
      const status = statusSelect.value;
      if (!status) return;

      const optionItems = [];
      if (statusOptionalData[status]) {
        optionItems.push(...statusOptionalData[status]);
      }

      const scenarioOptions = scenarioOptionalData[status] || {};
      selectedScenarios.forEach((scenarioLabel) => {
        if (scenarioOptions[scenarioLabel]) {
          optionItems.push(...scenarioOptions[scenarioLabel]);
        }
      });

      const uniqueItems = new Map();
      optionItems.forEach((item) => {
        if (!uniqueItems.has(item.label)) {
          uniqueItems.set(item.label, item);
        }
      });

      const dedupedItems = Array.from(uniqueItems.values());

      if (!dedupedItems.length) return;

      const wrapper = document.createElement('div');
      const description = document.createElement('div');
      description.textContent = '該当する場合はチェックを入れてください';
      description.style.fontWeight = '600';
      description.style.marginBottom = '0.35rem';
      wrapper.appendChild(description);

      dedupedItems.forEach((item, idx) => {
        const label = document.createElement('label');
        label.style.fontWeight = '500';
        label.style.display = 'flex';
        label.style.alignItems = 'center';
        label.style.gap = '0.4rem';
        label.style.marginBottom = '0.25rem';

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = `option-${idx}`;
        checkbox.dataset.requirements = JSON.stringify(item.requirements || []);
        checkbox.dataset.label = item.label;
        checkbox.addEventListener('change', showRequirements);

        const text = document.createElement('span');
        text.textContent = item.label;

        label.appendChild(checkbox);
        label.appendChild(text);
        wrapper.appendChild(label);
      });

      optionsContainer.appendChild(wrapper);
    }

    function resetScenarioSelection() {
      selectedScenarios = new Set();
    }

    function updateShowButtonState() {
      showButton.disabled = !statusSelect.value || selectedScenarios.size === 0;
    }

    function toggleScenarioSelection(label, button, event) {
      if (event && event.detail > 1) {
        return;
      }

      if (selectedScenarios.has(label)) {
        selectedScenarios.delete(label);
        button.classList.remove('selected');
        button.setAttribute('aria-pressed', 'false');
      } else {
        selectedScenarios.add(label);
        button.classList.add('selected');
        button.setAttribute('aria-pressed', 'true');
      }

      updateShowButtonState();
      renderOptions();
      showRequirements();
    }

    function renderScenarios() {
      const status = statusSelect.value;
      scenarioList.innerHTML = '';
      resetScenarioSelection();
      updateShowButtonState();
      renderOptions();

      if (!status) {
        const placeholder = document.createElement('span');
        placeholder.textContent = '身分を先に選んでください';
        placeholder.classList.add('muted');
        scenarioList.appendChild(placeholder);
        return;
      }

      statusData[status].forEach((scenario) => {
        const button = document.createElement('button');
        button.type = 'button';
        button.textContent = scenario.label;
        button.className = 'scenario-pill';
        button.setAttribute('aria-pressed', 'false');
        button.addEventListener('click', (event) =>
          toggleScenarioSelection(scenario.label, button, event)
        );
        scenarioList.appendChild(button);
      });
    }

    function renderRequirements(requirements, noticeText) {
      results.innerHTML = '';

      if (noticeText) {
        const notice = document.createElement('p');
        notice.innerHTML = `<strong style="color: #c00;">${noticeText}</strong>`;
        notice.style.marginBottom = '0.5rem';
        results.appendChild(notice);
      }

      if (!requirements.length) {
        const empty = document.createElement('p');
        empty.textContent = '必要な書類はありません。';
        results.appendChild(empty);
        return;
      }

      const list = document.createElement('ul');
      requirements.forEach((item) => {
        const li = document.createElement('li');
        li.textContent = item;
        list.appendChild(li);
      });
      results.appendChild(list);
    }

    function getSelectedOptionalSelections() {
      const checkboxes = optionsContainer.querySelectorAll(
        'input[type="checkbox"]:checked'
      );
      return Array.from(checkboxes).map((checkbox) => {
        const selection = { label: checkbox.dataset.label || '', requirements: [] };
        try {
          selection.requirements = JSON.parse(checkbox.dataset.requirements || '[]');
        } catch (err) {
          selection.requirements = [];
        }
        return selection;
      });
    }

    function showRequirements() {
      const status = statusSelect.value;
      const scholarship = scholarshipSelect.value;
      const scholarshipStatus = nonGovScholarships.includes(scholarship)
        ? scholarshipStatusSelect.value
        : '';
      if (!status || selectedScenarios.size === 0) {
        renderRequirements([]);
        return;
      }

      const scenarios = statusData[status] || [];
      const scenarioRequirements = Array.from(selectedScenarios).flatMap(
        (label) => {
          const scenario = scenarios.find((item) => item.label === label);
          return scenario ? scenario.requirements : [];
        }
      );
      const optionalSelections = getSelectedOptionalSelections();
      const optionalRequirements = optionalSelections.flatMap(
        (selection) => selection.requirements
      );
      const shouldShowAdvancementNotice =
        status === '正規生' &&
        optionalSelections.some((selection) => selection.label === 'これから進学予定');
      const noticeText = shouldShowAdvancementNotice ? ADVANCEMENT_NOTICE : '';
      const requirements = [
        ...commonRequirements,
        ...scenarioRequirements,
        ...optionalRequirements,
        ...(scholarship ? (scholarshipData[scholarship] || []) : []),
        ...(scholarshipStatus
          ? scholarshipStatusData[scholarshipStatus] || []
          : []),
      ];
      renderRequirements(requirements, noticeText);
    }

    statusSelect.addEventListener('change', () => {
      renderScenarios();
      showRequirements();
    });

    scholarshipSelect.addEventListener('change', showRequirements);
    scholarshipSelect.addEventListener('change', () => {
      const isNonGov = nonGovScholarships.includes(scholarshipSelect.value);
      if (!scholarshipSelect.value) {
        scholarshipStatusGroup.classList.add('hidden');
        scholarshipStatusSelect.value = '';
        scholarshipStatusSelect.disabled = true;
        scholarshipStatusSelect.options[0].textContent = '奨学金区分を先に選んでください';
      } else if (isNonGov) {
        scholarshipStatusGroup.classList.remove('hidden');
        scholarshipStatusSelect.disabled = false;
        scholarshipStatusSelect.options[0].textContent = '奨学金の状況を選択してください';
      } else {
        scholarshipStatusGroup.classList.add('hidden');
        scholarshipStatusSelect.value = '';
        scholarshipStatusSelect.disabled = true;
        scholarshipStatusSelect.options[0].textContent = '奨学金区分を先に選んでください';
      }
    });
    scholarshipStatusSelect.addEventListener('change', showRequirements);
    showButton.addEventListener('click', showRequirements);

    populateStatuses();
    populateScholarships();
    populateScholarshipStatuses();
    renderScenarios();
  </script>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="在留期間更新の必要書類をWebで案内します。")
    parser.add_argument("--host", default="0.0.0.0", help="サーバーのバインド先ホスト")
    parser.add_argument("--port", type=int, default=5000, help="サーバーのポート番号")
    args = parser.parse_args()

    app.run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
