# Student-Plaza-3F-VISA-Extension
学生プラザ３F 在留期間更新に関する書類

## 使い方
`visa_requirements.py` で、身分や奨学金区分に応じた必要書類を表示できます。

### 例: 引数指定
```
python visa_requirements.py --status 正規生 --scenario 現学年・前学期在籍 --scholarship 国費留学生
```

### 例: 対話式
```
python visa_requirements.py
```
身分 → 状況 → 奨学金の順に選ぶと、提出書類が一覧で表示されます。
