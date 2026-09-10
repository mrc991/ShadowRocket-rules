# -*- coding: utf-8 -*-
"""Invariant checks: US App Store via US node + UnionPay DIRECT."""
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
ruleset=🍎 App Store,[]DOMAIN-SUFFIX,apps.apple.com
ruleset=🍎 App Store,[]DOMAIN-SUFFIX,itunes.apple.com
ruleset=🍎 苹果中国,[]GEOSITE,apple-cn
ruleset=🎯 全球直连,[]DOMAIN-SUFFIX,unionpay.com
ruleset=🎯 全球直连,[]DOMAIN-SUFFIX,95516.com
ruleset=🐟 漏网之鱼,[]FINAL
custom_proxy_group=🎯 全球直连`select`[]DIRECT
custom_proxy_group=🎥 AppleTV+`select`[]🇭🇰 香港节点`[]🎯 全球直连
custom_proxy_group=🍎 App Store`select`[]🇺🇸 美国节点`[]🎯 全球直连
custom_proxy_group=🍎 苹果中国`select`[]🎯 全球直连`[]🚀 手动选择
custom_proxy_group=🇭🇰 香港节点`url-test`(港)`https://cp.cloudflare.com/generate_204`300,,50
custom_proxy_group=🇺🇸 美国节点`url-test`(美)`https://cp.cloudflare.com/generate_204`300,,50
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


def test_priority_us_appstore_and_unionpay() -> None:
    rules = base.priority_direct_rules()
    text = "\n".join(rules)
    if "95516.com" not in text or "unionpay.com" not in text:
        _fail("priority rules missing UnionPay domains")
    if "PROCESS-NAME,AppStore,🍎 App Store" not in text:
        _fail("AppStore process must go to 🍎 App Store, not DIRECT")
    if any("AppStore,🎯 全球直连" in x for x in rules):
        _fail("AppStore must not be forced DIRECT for US Apple ID")
    if any(x.startswith("DOMAIN-SUFFIX,apple.com,") for x in rules):
        _fail("apple.com must not be prepended")
    if any(x.startswith("DOMAIN-SUFFIX,itunes.apple.com,") for x in rules):
        _fail("itunes.apple.com must not be prepended before AppleTV+")


def test_overlay_order_appletv_then_appstore() -> None:
    rules = base.parse_ini_rules(FIXTURE_INI)
    tv = next(i for i, r in enumerate(rules) if "AppleTV" in r)
    store = next(i for i, r in enumerate(rules) if r.startswith("DOMAIN-SUFFIX,itunes.apple.com,"))
    apps = next(i for i, r in enumerate(rules) if r.startswith("DOMAIN-SUFFIX,apps.apple.com,"))
    union = next(i for i, r in enumerate(rules) if r.startswith("DOMAIN-SUFFIX,unionpay.com,"))
    if not (tv < store):
        _fail(f"AppleTV must precede itunes.apple.com: tv={tv} store={store}")
    if "🍎 App Store" not in rules[store] or "🍎 App Store" not in rules[apps]:
        _fail("itunes/apps.apple.com must map to 🍎 App Store")
    if "🎯 全球直连" not in rules[union]:
        _fail("unionpay.com must be DIRECT group")
    if any(r.startswith("DOMAIN-SUFFIX,apple.com,") for r in rules):
        _fail("apple.com suffix should not be forced")
    apple_list = [r for r in rules if "Apple/Apple.list" in r]
    if apple_list:
        _fail(f"Apple.list 17.0.0.0/8 must not be used: {apple_list}")


def test_appstore_group_defaults_to_us() -> None:
    groups = base.parse_ini_groups(FIXTURE_INI)
    line = next((g for g in groups if g.startswith("🍎 App Store =")), "")
    if not line.startswith("🍎 App Store = select,🇺🇸 美国节点"):
        _fail(f"App Store group must default to US: {line}")


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
        if "PROCESS-NAME,AppStore,🍎 App Store" not in text:
            _fail(f"{path.name} AppStore process must use 🍎 App Store")
        if "PROCESS-NAME,AppStore,🎯 全球直连" in text:
            _fail(f"{path.name} AppStore must not be DIRECT")
        if "🍎 App Store = select,🇺🇸 美国节点" not in text:
            _fail(f"{path.name} missing App Store group defaulting to US")
        if "DOMAIN-SUFFIX,itunes.apple.com,🍎 App Store" not in text:
            _fail(f"{path.name} missing itunes.apple.com -> App Store")
        if "DOMAIN-SUFFIX,apple.com,🍎 苹果中国" in text:
            _fail(f"{path.name} apple.com must not be forced to 苹果中国")
        if "Apple/Apple.list,🍎 苹果中国" in text:
            _fail(f"{path.name} Apple.list must not map to 苹果中国")
        tv_at = text.find("AppleTV/AppleTV.list")
        itunes_at = text.find("DOMAIN-SUFFIX,itunes.apple.com,🍎 App Store")
        if tv_at < 0 or itunes_at < 0 or not (tv_at < itunes_at):
            _fail(f"{path.name} AppleTV list must appear before itunes.apple.com suffix")
        net_rule = "DOMAIN-SUFFIX,jsdelivr.net,🚀 手动选择"
        com_rule = "DOMAIN-SUFFIX,jsdelivr.com,🚀 手动选择"
        if net_rule not in text or com_rule not in text:
            _fail(f"{path.name} jsdelivr.net/com must go to 🚀 手动选择")
        if "DOMAIN-SUFFIX,jsdelivr.net,🎯 全球直连" in text or "DOMAIN-SUFFIX,jsdelivr.com,🎯 全球直连" in text:
            _fail(f"{path.name} jsdelivr must not be forced DIRECT")
        net_at = text.find(net_rule)
        direct_at = text.find("Custom_Direct.list")
        if net_at < 0 or direct_at < 0 or not (net_at < direct_at):
            _fail(f"{path.name} jsdelivr proxy rule must appear before Custom_Direct.list")
        if not text.strip().endswith("FINAL,🐟 漏网之鱼") and "\nFINAL,🐟 漏网之鱼\n" not in text:
            _fail(f"{path.name} missing FINAL 漏网之鱼")


def main() -> None:
    test_dns_helpers()
    test_priority_us_appstore_and_unionpay()
    test_overlay_order_appletv_then_appstore()
    test_appstore_group_defaults_to_us()
    test_rewrite_general_keeps_china_doh()
    test_generated_confs()
    print("test_invariants: ok")


if __name__ == "__main__":
    main()
