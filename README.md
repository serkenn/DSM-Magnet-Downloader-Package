# DSM Magnet Downloader Package

Synology DSM向けに、`Mullvad VPN + Transmission` を前提として magnet リンク取得と投入を補助するパッケージです。  
このリポジトリは `.spk` パッケージを GitHub Actions で自動ビルドし、タグ時に Release へ添付します。

## Repository Structure

- `package/`: DSMパッケージ本体
- `package/INFO/package.info`: パッケージ名・バージョン定義
- `scripts/build_spk.sh`: `.spk` ビルドスクリプト
- `.github/workflows/build-dsm-package.yml`: CI/CD（ビルドとRelease添付）

## Local Build

```bash
./scripts/build_spk.sh
```

出力先:

```text
dist/dsm-magnet-dl-<version>.spk
```

`<version>` は `package/INFO/package.info` の `version` を使用します。

## GitHub Actions

ワークフロー: `Build DSM Package`

トリガー:
- `main` への push: `.spk` を Artifact として保存
- `v*` タグ push: Artifact に加え GitHub Releases に `.spk` を添付
- `workflow_dispatch`: 手動実行

## Release Procedure

1. `package/INFO/package.info` の `version` を更新
2. `main` に push
3. バージョンタグを作成して push

```bash
git tag -a v1.0.1 -m "Release v1.0.1"
git push origin v1.0.1
```

## Runtime Requirements (DSM side)

- Python 3
- Transmission (`transmission-daemon`, `transmission-remote`)
- WireGuard (`wg-quick`)
- Mullvad WireGuard config (`/usr/local/etc/mullvad-wg.conf`)

## Notes

- 本リポジトリの `.spk` は簡易構成です。実運用前にDSMの権限・依存関係・起動スクリプトを環境に合わせて確認してください。
