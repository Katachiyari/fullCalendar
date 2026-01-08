from __future__ import annotations

import asyncio
import shutil
import socket
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class MonitorTarget:
    host: str
    ssh_port: int = 22
    disk_path: str = "/"


def _tcp_reachable(host: str, port: int, timeout_s: float = 2.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout_s):
            return True
    except Exception:
        return False


async def _run_ssh_command(user: str, host: str, port: int, key_path: str, command: str, timeout_s: float = 6.0) -> str:
    ssh_bin = shutil.which("ssh")
    if not ssh_bin:
        raise RuntimeError("ssh client not available")

    proc = await asyncio.create_subprocess_exec(
        ssh_bin,
        "-i",
        key_path,
        "-p",
        str(port),
        "-o",
        "BatchMode=yes",
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        "UserKnownHostsFile=/dev/null",
        "-o",
        f"ConnectTimeout={int(max(1, timeout_s // 2))}",
        f"{user}@{host}",
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        out_b, err_b = await asyncio.wait_for(proc.communicate(), timeout=timeout_s)
    except asyncio.TimeoutError as e:
        proc.kill()
        raise RuntimeError("ssh timeout") from e

    if proc.returncode != 0:
        raise RuntimeError((err_b or out_b).decode("utf-8", errors="replace").strip() or "ssh error")

    return out_b.decode("utf-8", errors="replace")


def _parse_meminfo(meminfo: str) -> tuple[int | None, int | None, int | None]:
    # meminfo in kB
    values: dict[str, int] = {}
    for line in meminfo.splitlines():
        if ":" not in line:
            continue
        key, rest = line.split(":", 1)
        parts = rest.strip().split()
        if not parts:
            continue
        try:
            values[key] = int(parts[0]) * 1024
        except Exception:
            continue

    total = values.get("MemTotal")
    available = values.get("MemAvailable")
    if total is None or available is None:
        return None, None, None
    used = total - available
    return total, used, available


def _parse_loadavg(loadavg: str) -> tuple[float, float, float]:
    parts = loadavg.strip().split()
    if len(parts) < 3:
        return 0.0, 0.0, 0.0
    try:
        return float(parts[0]), float(parts[1]), float(parts[2])
    except Exception:
        return 0.0, 0.0, 0.0


def _parse_df_bytes(df_out: str) -> tuple[int | None, int | None, int | None]:
    # Expect: Filesystem 1B-blocks Used Available Use% Mounted on
    lines = [l for l in df_out.splitlines() if l.strip()]
    if len(lines) < 2:
        return None, None, None
    parts = lines[-1].split()
    if len(parts) < 5:
        return None, None, None
    try:
        total = int(parts[1])
        used = int(parts[2])
        avail = int(parts[3])
        free = avail
        return total, used, free
    except Exception:
        return None, None, None


async def collect_remote_metrics(
    target: MonitorTarget,
    ssh_user: str | None = None,
    ssh_key_path: str | None = None,
) -> dict[str, Any]:
    """Collect remote metrics.

    Strategy:
    - Always returns reachability information.
    - If SSH is configured and reachable, runs a few basic Linux commands.

    Note: This is best-effort; environments without ssh client or without access return null metrics.
    """

    reachable = _tcp_reachable(target.host, target.ssh_port)

    base = {
        "target": {"host": target.host, "ssh_port": target.ssh_port, "disk_path": target.disk_path},
        "reachable": reachable,
        "collected_at": datetime.utcnow().isoformat(),
        "method": None,
        "error": None,
        "cpu": {"cores": 0, "load": {"avg_1": 0.0, "avg_5": 0.0, "avg_15": 0.0}},
        "memory": {"total_bytes": None, "used_bytes": None, "available_bytes": None},
        "storage": {"path": target.disk_path, "total_bytes": None, "used_bytes": None, "free_bytes": None},
    }

    if not reachable or not ssh_user or not ssh_key_path:
        return base

    try:
        base["method"] = "ssh"
        cores_raw = await _run_ssh_command(ssh_user, target.host, target.ssh_port, ssh_key_path, "nproc")
        load_raw = await _run_ssh_command(ssh_user, target.host, target.ssh_port, ssh_key_path, "cat /proc/loadavg")
        mem_raw = await _run_ssh_command(ssh_user, target.host, target.ssh_port, ssh_key_path, "cat /proc/meminfo")
        df_raw = await _run_ssh_command(
            ssh_user,
            target.host,
            target.ssh_port,
            ssh_key_path,
            f"df -B1 {target.disk_path} || df -B1 /",
        )

        try:
            base["cpu"]["cores"] = int(cores_raw.strip())
        except Exception:
            base["cpu"]["cores"] = 0

        a1, a5, a15 = _parse_loadavg(load_raw)
        base["cpu"]["load"] = {"avg_1": a1, "avg_5": a5, "avg_15": a15}

        mt, mu, ma = _parse_meminfo(mem_raw)
        base["memory"] = {"total_bytes": mt, "used_bytes": mu, "available_bytes": ma}

        dt, du, dfree = _parse_df_bytes(df_raw)
        base["storage"].update({"total_bytes": dt, "used_bytes": du, "free_bytes": dfree})

        return base
    except Exception as e:
        base["error"] = str(e)
        return base
