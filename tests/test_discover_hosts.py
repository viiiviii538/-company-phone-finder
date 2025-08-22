import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src import discover_hosts


def test_discover_hosts_includes_hostname_and_vendor(monkeypatch):
    sample_hosts = [{
        "ip": "192.168.0.2",
        "mac": "AA:BB:CC:DD:EE:FF",
        "hostname": "test-host"
    }]

    monkeypatch.setattr(discover_hosts.network_utils, "_run_nmap_scan", lambda net: sample_hosts)

    class DummyResp:
        status_code = 200
        text = "DummyVendor"

    monkeypatch.setattr(discover_hosts.requests, "get", lambda url, timeout=5: DummyResp())
    monkeypatch.setattr(discover_hosts, "OUI_FILE", pathlib.Path("/nonexistent/oui.txt"))

    result = discover_hosts.discover_hosts("192.168.0.0/24")
    assert result == [{
        "ip": "192.168.0.2",
        "mac": "AA:BB:CC:DD:EE:FF",
        "hostname": "test-host",
        "vendor": "DummyVendor",
    }]
