import asyncio
from app.scanner import safe_port_scan


def test_safe_port_scan_returns_dict():
    result = asyncio.run(safe_port_scan("127.0.0.1", ports=[1]))
    assert "status" in result
    assert "details" in result
