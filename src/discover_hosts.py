from pathlib import Path
from typing import List, Dict
import re
import requests

from . import network_utils

OUI_FILE = Path(__file__).with_name("oui.txt")


def _lookup_vendor(mac: str) -> str | None:
    if not mac:
        return None
    prefix = re.sub(r"[^0-9A-Fa-f]", "", mac)[:6].upper()
    if OUI_FILE.exists():
        try:
            for line in OUI_FILE.read_text().splitlines():
                if line[:6].upper() == prefix:
                    parts = line.split(None, 1)
                    if len(parts) == 2:
                        return parts[1].strip()
        except Exception:
            pass
    try:
        resp = requests.get(f"https://api.macvendors.com/{mac}", timeout=5)
        if resp.status_code == 200:
            text = resp.text.strip()
            if text:
                return text
    except Exception:
        pass
    return None


def discover_hosts(network: str) -> List[Dict[str, str]]:
    hosts = network_utils._run_nmap_scan(network)
    for host in hosts:
        mac = host.get("mac")
        if mac and not host.get("vendor"):
            vendor = _lookup_vendor(mac)
            if vendor:
                host["vendor"] = vendor
        if "hostname" not in host:
            host["hostname"] = ""
    return hosts
