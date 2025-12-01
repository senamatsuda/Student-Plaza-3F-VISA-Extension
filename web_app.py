"""簡易Web UI: 身分と状況を選択して必要書類を確認できます。"""

from __future__ import annotations

import argparse
import json
from typing import Dict, List

from flask import Flask, Response, render_template_string

from visa_requirements import COMMON_REQUIREMENTS, SCHOLARSHIP_RULES, STATUS_RULES

app = Flask(__name__)


def build_status_payload() -> Dict[str, List[Dict[str, List[str]]]]:
    """シリアライズしやすい形で身分・状況データを返す。"""

    return {
        status: [{"label": sc.label, "requirements": sc.requirements} for sc in scenarios]
        for status, scenarios in STATUS_RULES.items()
    }


@app.route("/")
def index() -> Response:
    status_payload = build_status_payload()
    status_json = json.dumps(status_payload, ensure_ascii=False)
    scholarship_json = json.dumps(SCHOLARSHIP_RULES, ensure_ascii=False)
    common_json = json.dumps(COMMON_REQUIREMENTS, ensure_ascii=False)

    return render_template_string(
        INDEX_HTML,
        status_json=status_json,
        scholarship_json=scholarship_json,
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
    ul { padding-left: 1.2rem; }
    .muted { color: #555; }
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
    <select id=\"scenario\" disabled>
      <option value=\"\">身分を先に選んでください</option>
    </select>

    <label for=\"scholarship\">奨学金区分（任意）</label>
    <select id=\"scholarship\">
      <option value=\"\">選択なし</option>
    </select>

    <button id=\"show\" disabled>必要書類を表示</button>

    <div id=\"results\" style=\"margin-top: 1.4rem;\"></div>
  </div>

  <script>
    const statusData = {{ status_json | safe }};
    const scholarshipData = {{ scholarship_json | safe }};
    const commonRequirements = {{ common_json | safe }};

    const statusSelect = document.getElementById('status');
    const scenarioSelect = document.getElementById('scenario');
    const scholarshipSelect = document.getElementById('scholarship');
    const showButton = document.getElementById('show');
    const results = document.getElementById('results');

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

    function refreshScenarios() {
      const status = statusSelect.value;
      scenarioSelect.innerHTML = '';
      if (!status) {
        const option = document.createElement('option');
        option.value = '';
        option.textContent = '身分を先に選んでください';
        scenarioSelect.appendChild(option);
        scenarioSelect.disabled = true;
        showButton.disabled = true;
        return;
      }

      statusData[status].forEach((scenario) => {
        const option = document.createElement('option');
        option.value = scenario.label;
        option.textContent = scenario.label;
        scenarioSelect.appendChild(option);
      });
      scenarioSelect.disabled = false;
      showButton.disabled = !scenarioSelect.value;
    }

    function renderRequirements(requirements) {
      results.innerHTML = '';
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

    function showRequirements() {
      const status = statusSelect.value;
      const scenarioLabel = scenarioSelect.value;
      const scholarship = scholarshipSelect.value;
      if (!status || !scenarioLabel) {
        renderRequirements([]);
        return;
      }

      const scenario = statusData[status].find((item) => item.label === scenarioLabel);
      const requirements = [
        ...commonRequirements,
        ...(scenario ? scenario.requirements : []),
        ...(scholarship ? (scholarshipData[scholarship] || []) : []),
      ];
      renderRequirements(requirements);
    }

    statusSelect.addEventListener('change', () => {
      refreshScenarios();
      showRequirements();
    });

    scenarioSelect.addEventListener('change', () => {
      showButton.disabled = !scenarioSelect.value;
    });

    scholarshipSelect.addEventListener('change', showRequirements);
    showButton.addEventListener('click', showRequirements);

    populateStatuses();
    populateScholarships();
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
