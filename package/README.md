# DSM Magnet Downloader Package

## 概要
- Transmissionを使い、Mullvad VPN経由でmagnetリンクからファイルをダウンロードします。
- 指定URLからmagnetリンクを自動取得し、Transmissionに投入します。

## 使い方
1. TransmissionとMullvad VPNをDSMにインストール・設定してください。
2. `magnet_fetcher.py` を実行して、magnetリンクをTransmissionに投入します。

```
python3 magnet_fetcher.py "https://sukebei.nyaa.si/?f=0&c=0_0&q=AliceHolic13"
```

## SEED最小化設定例（transmission-daemon）
- `settings.json` の以下を調整：
  - "seedRatioLimit": 0.01
  - "seedRatioLimited": true
  - "upload-slots-per-torrent": 1
  - "speed-limit-up": 1
  - "speed-limit-up-enabled": true

## 必要パッケージ
- transmission-daemon
- transmission-remote
- python3
- requests

---

## 今後のTODO
- Mullvad VPN自動接続スクリプト追加
- DSMパッケージ化（spk化）
