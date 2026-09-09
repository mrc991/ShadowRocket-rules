# -*- coding: utf-8 -*-
"""Merge LC groups into johnshall sr_top500_whitelist_ad.conf; keep China DoH, proxy DoH as fallback."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).parent))
import build_shadowrocket_conf as base  # noqa: E402

UPSTREAM_REPO = "Johnshall/Shadowrocket-ADBlock-Rules-Forever"
UPSTREAM_PATH = "sr_top500_whitelist_ad.conf"
UPSTREAM_REF = "release"
CACHE = ROOT / ".cache" / UPSTREAM_PATH
OUT = ROOT / "Custom_Shadowrocket_whitelist_ad.conf"

# 国区 App Store / 云闪付需要国内 DNS 视图；海外域名解析失败再走代理 DoH。
DOH_LINE = base.PRIMARY_DNS
FALLBACK_DOH_LINE = base.FALLBACK_DNS
SKIP_APPEND = ", " + base.SKIP_PROXY_EXTRA


def fetch_upstream() -> str:
    import urllib.request

    urls = [
        f"https://raw.githubusercontent.com/{UPSTREAM_REPO}/{UPSTREAM_REF}/{UPSTREAM_PATH}",
        "https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/sr_top500_whitelist_ad.conf",
    ]
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                if data:
                    CACHE.parent.mkdir(parents=True, exist_ok=True)
                    CACHE.write_bytes(data)
                    return data.decode("utf-8")
        except Exception:
            continue

    r = subprocess.run(
        [
            "gh",
            "api",
            "-H",
            "Accept: application/vnd.github.raw",
            f"repos/{UPSTREAM_REPO}/contents/{UPSTREAM_PATH}?ref={UPSTREAM_REF}",
        ],
        capture_output=True,
    )
    if r.returncode == 0 and r.stdout:
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_bytes(r.stdout)
        return r.stdout.decode("utf-8")

    raise SystemExit("fetch johnshall failed from all sources")


def split_sections(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {"HEADER": []}
    current = "HEADER"
    for line in text.splitlines():
        s = line.strip()
        if len(s) >= 3 and s.startswith("[") and s.endswith("]") and s[1].isalpha():
            current = s
            sections[current] = []
            continue
        sections.setdefault(current, []).append(line)
    return sections


def rewrite_general(lines: list[str]) -> list[str]:
    out: list[str] = []
    replaced_dns = False
    replaced_fallback = False
    for line in lines:
        if re.match(r"^\s*dns-server\s*=", line, re.I):
            out.append(DOH_LINE)
            replaced_dns = True
        elif re.match(r"^\s*fallback-dns-server\s*=", line, re.I):
            out.append(FALLBACK_DOH_LINE)
            replaced_fallback = True
        elif re.match(r"^\s*skip-proxy\s*=", line, re.I):
            if "95516.com" not in line:
                line = line.rstrip() + SKIP_APPEND
            out.append(line)
        else:
            out.append(line)
    if not replaced_dns:
        out.append(DOH_LINE)
    if not replaced_fallback:
        out.append(FALLBACK_DOH_LINE)
    return out


def split_johnshall_rules(rule_lines: list[str]) -> tuple[list[str], list[str]]:
    """Ads (Reject) stay first; Direct/CN/FINAL stay after LC overlay."""
    ads: list[str] = []
    rest: list[str] = []
    seen_direct_block = False
    for line in rule_lines:
        stripped = line.strip()
        if not seen_direct_block and (
            stripped.endswith(",Direct")
            or stripped.endswith(",DIRECT")
            or stripped.startswith("FINAL,")
            or "AppleNews" in stripped
        ):
            seen_direct_block = True
        if seen_direct_block:
            rest.append(line)
        else:
            ads.append(line)
    return ads, rest


def remap_upstream_policy(line: str) -> str:
    s = line.strip()
    if not s or s.startswith("#"):
        return line
    if "AppleNews" in s and s.endswith(",PROXY"):
        return s[:-6] + ",🇺🇸 美国节点"
    if s == "FINAL,PROXY":
        return "FINAL,🐟 漏网之鱼"
    if s.endswith(",PROXY"):
        return s[:-6] + ",🐟 漏网之鱼"
    return line


def main() -> None:
    text = fetch_upstream()
    sections = split_sections(text)
    general = rewrite_general(sections.get("[General]", []))
    ads, rest = split_johnshall_rules(sections.get("[Rule]", []))
    rest = [remap_upstream_policy(x) for x in rest]
    rest_body = [x for x in rest if not x.strip().startswith("FINAL,")]

    header = [
        "# LC merge of johnshall sr_top500_whitelist_ad + Custom_Clash groups",
        f"# upstream: https://github.com/{UPSTREAM_REPO}/blob/{UPSTREAM_REF}/{UPSTREAM_PATH}",
        "# DNS: AliDNS/DNSPod 直连解析；Cloudflare/Google DoH 仅 fallback 且走代理",
        "# 不含节点。配置页导入，不要改首页订阅。",
        "",
    ]

    out: list[str] = []
    out.extend(header)
    out.append("[General]")
    out.extend(general)
    if general and general[-1].strip():
        out.append("")
    out.append("[Proxy Group]")
    out.extend(base.proxy_group_lines())
    out.append("")
    out.append("[Rule]")
    out.extend(base.priority_direct_rules())
    out.append("")
    out.extend(ads)
    if ads and ads[-1].strip():
        out.append("")
    out.append("# ===== LC groups (Custom_Clash.ini) =====")
    out.extend(
        base.overlay_rule_lines(
            include_broad_cn=False,
            include_final=False,
            include_nonstandard_ports=False,
        )
    )
    out.append("")
    out.append("# ===== johnshall Direct / CN =====")
    out.extend(rest_body)
    out.append("")
    out.extend(base.nonstandard_port_lines())
    out.append("FINAL,🐟 漏网之鱼")
    out.append("")

    for extra in ("[URL Rewrite]", "[MITM]", "[Host]", "[Script]"):
        if extra in sections:
            out.append(extra)
            out.extend(sections[extra])
            if sections[extra] and sections[extra][-1].strip():
                out.append("")

    OUT.write_text("\n".join(out), encoding="utf-8", newline="\n")
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes, {len(out)} lines)")


if __name__ == "__main__":
    main()
