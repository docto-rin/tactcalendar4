#!/usr/bin/env bash

# エラーが起きた時にスクリプトの実行を停止
set -o errexit
# 設定されていない変数をエラーとして扱う
set -o nounset
# パイプの一部が失敗したらパイプ全体の失敗とみなす
set -o pipefail

# プロジェクトのルートディレクトリを取得
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 仮想環境のパスを環境変数から取得するか、デフォルト値を使用
VENV_PATH="${VIRTUAL_ENV:-$PROJECT_ROOT/env}"

# Pythonインタープリタを見つける
PYTHON_INTERPRETER="$VENV_PATH/bin/python"
if [ ! -f "$PYTHON_INTERPRETER" ]; then
    PYTHON_INTERPRETER=$(which python)
fi

# メインスクリプトのパス
MAIN_SCRIPT="$PROJECT_ROOT/TACTcalendar4.py"

# デバッグ情報の出力
echo "Project Root: $PROJECT_ROOT"
echo "Virtual Env Path: $VENV_PATH"
echo "Python Interpreter: $PYTHON_INTERPRETER"
echo "Main Script: $MAIN_SCRIPT"

# スクリプトを実行
"$PYTHON_INTERPRETER" "$MAIN_SCRIPT"