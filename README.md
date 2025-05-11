# image_processor

個人で使う画像処理用スクリプトなど


## 忘備録

仮想環境の構築
uvを使っておこなう

```bash
# install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
# sh, bash, zsh
source $HOME/.cargo/env
# bash
echo 'eval "$(uv generate-shell-completion bash)"' >> ~/.bashrc
# self update
uv self update
```

uvの使い方

```bash
uv python install 3.13
uv python list

# プロジェクトの作成
uv init uv-sample-project
# 今回はこのプロジェクト直下で uv init

# pythonバージョンの変更
uv python pin 3.10

# パッケージを入れる
uv add (パッケージ名)
# devパッケージとしていれる
uv add --dev (パッケージ名)

# パッケージの更新・削除
uv tool upgrade (パッケージ名)
uv tool uninstall (パッケージ名)

# uv runで実行
uv run (ファイル名)
```

## uvだとrembgのインストールができなかったのでvenvでやる

```bash
# 仮想環境の作成
python3 -m venv master
# 仮想環境の有効化
source master/bin/activate
# 仮想環境の無効化
deactivate
```
