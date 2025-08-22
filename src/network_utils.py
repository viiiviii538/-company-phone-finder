import subprocess
import re
from typing import List, Dict


def _parse_nmap_output(output: str) -> List[Dict[str, str]]:
    hosts = []
    current = None
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("Nmap scan report for"):
            match = re.match(r"Nmap scan report for (?:(?P<hostname>[^\s]+) )?\((?P<ip>[^)]+)\)", line)
            if match:
                current = {
                    "ip": match.group("ip"),
                }
                hostname = match.group("hostname")
                if hostname and hostname != match.group("ip"):
                    current["hostname"] = hostname
                hosts.append(current)
            else:
                parts = line.split()
                ip = parts[-1]
                current = {"ip": ip}
                if len(parts) >= 5:
                    current["hostname"] = parts[4]
                hosts.append(current)
        elif line.startswith("MAC Address:") and current is not None:
            parts = line.split("MAC Address:", 1)[1].strip().split(" ")
            if parts:
                current["mac"] = parts[0]
                if len(parts) > 1:
                    current["vendor"] = " ".join(parts[1:]).strip()
    return hosts


def _nbtscan(ips: List[str]) -> Dict[str, str]:
    if not ips:
        return {}
    try:
        result = subprocess.run(["nbtscan", "-f"] + ips, capture_output=True, text=True, check=False)
        mapping = {}
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line or line.startswith("doing"):
                continue
            parts = re.split(r"\s+", line)
            if len(parts) >= 2:
                mapping[parts[0]] = parts[1]
        return mapping
    except FileNotFoundError:
        return {}


def _avahi_resolve(ips: List[str]) -> Dict[str, str]:
    mapping = {}
    for ip in ips:
        try:
            result = subprocess.run(["avahi-resolve", "-a", ip], capture_output=True, text=True, check=False)
            for line in result.stdout.splitlines():
                line = line.strip()
                parts = line.split()
                if len(parts) >= 2:
                    mapping[ip] = parts[1]
        except FileNotFoundError:
            break
    return mapping


def _run_nmap_scan(network: str) -> List[Dict[str, str]]:
    try:
        result = subprocess.run(["nmap", "-sn", network], capture_output=True, text=True, check=False)
        hosts = _parse_nmap_output(result.stdout)
    except FileNotFoundError:
        hosts = []
    ips = [h["ip"] for h in hosts]
    nbts = _nbtscan(ips)
    avahi = _avahi_resolve(ips)
    for host in hosts:
        ip = host["ip"]
        if ip in nbts:
            host["hostname"] = nbts[ip]
        elif ip in avahi and not host.get("hostname"):
            host["hostname"] = avahi[ip]
    return hosts
