#!/usr/bin/env python3
"""Fetch magnet links from URL and add them to Transmission."""
import argparse
import re
import subprocess
import sys

import requests


def fetch_magnets(url, proxy_url=None, timeout=30):
    proxies = None
    if proxy_url:
        proxies = {"http": proxy_url, "https": proxy_url}
    res = requests.get(url, proxies=proxies, timeout=timeout)
    res.raise_for_status()
    magnets = re.findall(r"magnet:\?xt=urn:[^'\"\s<]+", res.text)
    return list(dict.fromkeys(magnets))


def add_to_transmission(magnets, host="localhost", port=9091, user=None, password=None):
    for magnet in magnets:
        cmd = ["transmission-remote", f"{host}:{port}", "--add", magnet]
        if user:
            cmd += ["--auth", f"{user}:{password or ''}"]
        subprocess.run(cmd, check=True)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("url")
    p.add_argument("--host", default="localhost")
    p.add_argument("--port", type=int, default=9091)
    p.add_argument("--user")
    p.add_argument("--password")
    p.add_argument("--proxy-url")
    return p.parse_args()


def main():
    args = parse_args()
    magnets = fetch_magnets(args.url, proxy_url=args.proxy_url)
    print(f"Found {len(magnets)} magnet links.")
    if not magnets:
        print("No magnets found.")
        return
    add_to_transmission(
        magnets,
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
    )
    print("All magnets added to Transmission queue.")

if __name__ == "__main__":
    main()
