# dsm-magnet-dl DSMパッケージ構成例

package/
├── INFO/
│   └── package.info
├── magnet_fetcher.py
├── mullvad_connect.sh
├── start.sh
├── stop.sh
├── README.md

# パッケージ化手順（ローカル）
1. リポジトリ直下でビルドスクリプトを実行
2. `dist/` に `.spk` が出力される
3. DSMのパッケージセンターから手動インストール

例：
```
./scripts/build_spk.sh
```

出力例:
```
dist/dsm-magnet-dl-1.0.0.spk
```

# GitHub Actions（自動ビルド）
- ワークフロー: `.github/workflows/build-dsm-package.yml`
- トリガー:
  - `main` への push
  - `v*` タグ push
  - `workflow_dispatch`（手動実行）
- 生成物:
  - Actions Artifact に `.spk` をアップロード
  - タグ実行時は GitHub Release Asset にも `.spk` を添付

# 注意
- 必要な依存パッケージ（python3, transmission, wg-quick等）は事前にDSMにインストールしてください。
- WireGuard設定ファイル（mullvad-wg.conf）は /usr/local/etc/ に配置してください。
- DSMのセキュリティ設定や権限に注意してください。
