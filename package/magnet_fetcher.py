#!/usr/bin/env python3
"""
magnet_fetcher.py
指定URLからマグネットリンクを抽出し、Transmissionに投入するスクリプト
"""
import requests
import re
import sys
import subprocess
from urllib.parse import urljoin

def fetch_magnets(url):
    res = requests.get(url)
    res.raise_for_status()
    magnets = re.findall(r"magnet:\?xt=urn:[^'\"\s<]+", res.text)
    return list(set(magnets))

def add_to_transmission(magnets, host='localhost', port=9091, user=None, password=None):
    for magnet in magnets:
        cmd = ["transmission-remote", f"{host}:{port}", "--add", magnet]
        if user:
            cmd += ["--auth", f"{user}:{password}"]
        subprocess.run(cmd, check=True)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 magnet_fetcher.py <url>")
        sys.exit(1)
    url = sys.argv[1]
    magnets = fetch_magnets(url)
    print(f"Found {len(magnets)} magnet links.")
    if not magnets:
        print("No magnets found.")
        return
    add_to_transmission(magnets)
    print("All magnets added to Transmission queue.")

if __name__ == "__main__":
    main()
