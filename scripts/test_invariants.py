# -*- coding: utf-8 -*-
"""Invariant checks for App Store search + UnionPay DIRECT routing."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).parent))
import build_shadowrocket_conf as base  # noqa: E402
import merge_johnshall as merge  # noqa: E402

FIXTURE_INI = """
[custom]
ruleset=🎥 AppleTV+,[]GEOSITE,apple-tvplus
ruleset=🍎 苹果中国,[]GEOSITE,apple-cn
ruleset=🍎 苹果中国,[]DOMAIN-SUFFIX,apple.com
ruleset=🎯 全球直连,[]DOMAIN-SUFFIX,unionpay.com
ruleset=🎯 全球直连,[]DOMAIN-SUFFIX,95516.com
ruleset=🐟 漏网之鱼,[]FINAL
custom_proxy_group=🎯 全球直连`select`[]DIRECT
custom_proxy_group=🎥 AppleTV+`select`[]🇭🇰 香港节点`[]🎯 全球直连
custom_proxy_group=🍎 苹果中国`select`[]🎯 全球直连`[]🚀 手动选择
custom_proxy_group=🇭🇰 香港节点`url-test`(港)`https://cp.cloudflare.com/generate_204`300,,50
custom_proxy_group=🐟 漏网之鱼`select`[]🚀 手动选择`[]🎯 全球直连
"""


def _fail(msg: str) -> None:
    raise AssertionError(msg)


def test_dns_helpers() -> None:
    assert "dns.alidns.com" in base.PRIMARY_DNS
    assert "doh.pub" in base.PRIMARY_DNS
    assert "1.1.1.1" not in base.PRIMARY_DNS
    assert "#proxy" in base.FALLBACK_DNS
    assert "1.1.1.1" in base.FALLBACK_DNS


def test_priority_unionpay_before_apple_suffix() -> None:
    rules = base.priority_direct_rules()
    text = "\n".join(rules)
    if "95516.com" not in text or "unionpay.com" not in text:
        _fail("priority rules missing UnionPay domains")
    if "PROCESS-NAME,AppStore" not in text:
        _fail("priority rules missing AppStore process")
    if any(x.startswith("DOMAIN-SUFFIX,apple.com,") for x in rules):
        _fail("apple.com must not be prepended before AppleTV+")
    if any(x.startswith("DOMAIN-SUFFIX,itunes.apple.com,") for x in rules):
        _fail("itunes.apple.com must not be prepended before AppleTV+")


def test_overlay_order_appletv_before_apple() -> None:
    rules = base.parse_ini_rules(FIXTURE_INI)
    tv = next(i for i, r in enumerate(rules) if "AppleTV" in r)
    apple = next(i for i, r in enumerate(rules) if r.startswith("DOMAIN-SUFFIX,apple.com,"))
    union = next(i for i, r in enumerate(rules) if r.startswith("DOMAIN-SUFFIX,unionpay.com,"))
    if not (tv < apple):
        _fail(f"AppleTV must precede apple.com suffix: tv={tv} apple={apple}")
    if "🍎 苹果中国" not in rules[apple]:
        _fail("apple.com suffix must map to 苹果中国")
    if "🎯 全球直连" not in rules[union]:
        _fail("unionpay.com must be DIRECT group")


def test_rewrite_general_keeps_china_doh() -> None:
    general = [
        "ipv6 = false",
        "skip-proxy = localhost, captive.apple.com",
        "dns-server = https://1.1.1.1/dns-query #proxy",
    ]
    out = merge.rewrite_general(general)
    joined = "\n".join(out)
    if "dns.alidns.com" not in joined:
        _fail("rewrite_general did not restore AliDNS")
    if re.search(r"^dns-server = .*1\.1\.1\.1", joined, re.M):
        _fail("primary dns-server still uses Cloudflare")
    if "fallback-dns-server" not in joined or "#proxy" not in joined:
        _fail("missing proxied fallback DoH")
    if "95516.com" not in joined:
        _fail("skip-proxy missing UnionPay")


def test_generated_confs() -> None:
    files = [
        ROOT / "Custom_Shadowrocket.conf",
        ROOT / "Custom_Shadowrocket_whitelist_ad.conf",
    ]
    for path in files:
        if not path.is_file():
            _fail(f"missing generated conf: {path}")
        text = path.read_text(encoding="utf-8")
        dns_line = next((ln for ln in text.splitlines() if re.match(r"^\s*dns-server\s*=", ln, re.I)), "")
        if "dns.alidns.com" not in dns_line:
            _fail(f"{path.name} primary DNS is not AliDNS: {dns_line}")
        if "1.1.1.1" in dns_line:
            _fail(f"{path.name} primary DNS still includes Cloudflare: {dns_line}")
        if "ipv6 = false" not in text:
            _fail(f"{path.name} ipv6 not disabled")
        if "DOMAIN-SUFFIX,95516.com,🎯 全球直连" not in text:
            _fail(f"{path.name} missing 95516 DIRECT")
        if "PROCESS-NAME,AppStore,🎯 全球直连" not in text:
            _fail(f"{path.name} missing AppStore process DIRECT")
        if "DOMAIN-SUFFIX,apple.com,🍎 苹果中国" not in text:
            _fail(f"{path.name} missing apple.com -> 苹果中国")
        if "AppleTV/AppleTV.list,🎥 AppleTV+" not in text:
            _fail(f"{path.name} missing AppleTV+ list")
        tv_at = text.find("AppleTV/AppleTV.list")
        apple_at = text.find("DOMAIN-SUFFIX,apple.com,🍎 苹果中国")
        if tv_at < 0 or apple_at < 0 or not (tv_at < apple_at):
            _fail(f"{path.name} AppleTV list must appear before apple.com suffix")
        if not text.strip().endswith("FINAL,🐟 漏网之鱼") and "\nFINAL,🐟 漏网之鱼\n" not in text:
            _fail(f"{path.name} missing FINAL 漏网之鱼")


def main() -> None:
    test_dns_helpers()
    test_priority_unionpay_before_apple_suffix()
    test_overlay_order_appletv_before_apple()
    test_rewrite_general_keeps_china_doh()
    test_generated_confs()
    print("test_invariants: ok")


if __name__ == "__main__":
    main()
