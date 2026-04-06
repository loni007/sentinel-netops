import asyncio
from typing import Iterable

COMMON_PORTS = {
    22: "SSH",
    53: "DNS",
    80: "HTTP",
    123: "NTP",
    443: "HTTPS",
    3306: "MySQL",
    5432: "PostgreSQL",
    6379: "Redis",
    8080: "HTTP-Alt",
}


async def check_tcp(host: str, port: int, timeout: float = 1.0) -> bool:
    try:
        conn = asyncio.open_connection(host, port)
        reader, writer = await asyncio.wait_for(conn, timeout=timeout)
        writer.close()
        await writer.wait_closed()
        return True
    except Exception:
        return False


async def health_check(host: str) -> dict:
    for port in (443, 80, 22):
        if await check_tcp(host, port):
            return {"status": "reachable", "details": f"TCP connectivity succeeded on port {port}"}
    return {"status": "unreachable", "details": "No response on common service ports 443/80/22"}


async def safe_port_scan(host: str, ports: Iterable[int] | None = None) -> dict:
    ports = list(ports or COMMON_PORTS.keys())
    tasks = [check_tcp(host, port) for port in ports]
    results = await asyncio.gather(*tasks)
    open_ports = [f"{port}/{COMMON_PORTS.get(port, 'unknown')}" for port, is_open in zip(ports, results) if is_open]
    status = "ports_detected" if open_ports else "no_common_ports_detected"
    details = ", ".join(open_ports) if open_ports else "No configured common ports responded"
    return {"status": status, "details": details}
