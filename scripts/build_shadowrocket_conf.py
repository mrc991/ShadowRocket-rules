# -*- coding: utf-8 -*-
"""Dynamic Shadowrocket conf builder: fetches and parses Custom_Clash.ini."""
from __future__ import annotations

import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Custom_Shadowrocket.conf"
CACHE_DIR = ROOT / ".cache"
INI_CACHE = CACHE_DIR / "Custom_Clash.ini"

INI_URL = "https://raw.githubusercontent.com/mrc991/Custom_OpenClash_Rules/main/cfg/Custom_Clash.ini"

BM = "https://testingcf.jsdelivr.net/gh/blackmatrix7/ios_rule_script@master/rule/Shadowrocket"
COR = "https://testingcf.jsdelivr.net/gh/mrc991/Custom_OpenClash_Rules@main/rule"

INFO = r"^((?!(流量|到期|套餐|剩余|官网|Expire|Traffic)).)*$"

# Shadowrocket-safe region regexes
HK = r"🇭🇰|香港|Hong Kong|HongKong|HONGKONG|深港|HKG|九龙|Kowloon|(HK )|(HK-)|(HK_)|港"
US = r"🇺🇸|美国|美國|USA|America|AMERICA|洛杉矶|硅谷|圣何塞|西雅图|芝加哥|纽约|达拉斯|波特兰|(US )|(US-)|(US_)|(US$)"
JP = r"🇯🇵|日本|东京|大阪|Japan|JAPAN|JPN|(JP )|(JP-)|(JP_)"
SG = r"🇸🇬|新加坡|狮城|Singapore|SINGAPORE|(SG )|(SG-)|(SG_)"
TW = r"🇹🇼|🇼🇸|台湾|台灣|Taiwan|TAIWAN|台北|新北|彰化|(TW )|(TW-)|(TW_)"
KR = r"🇰🇷|韩国|韓國|Korea|KOREA|KOR|首尔|首爾|韩|韓|(KR )|(KR-)|(KR_)"
OTHER = (
    r"^((?!(香港|🇭🇰|Hong|HK |HK-|美国|美國|🇺🇸|USA|US |US-|日本|🇯🇵|Japan|JP |"
    r"新加坡|🇸🇬|Singapore|SG |台湾|台灣|🇹🇼|Taiwan|TW |韩国|韓國|🇰🇷|Korea|KR |"
    r"流量|到期|套餐|剩余|官网)).)*$"
)

REGION_REGEX_MAP = {
    "🇭🇰 香港节点": HK,
    "🇺🇸 美国节点": US,
    "🇯🇵 日本节点": JP,
    "🇸🇬 新加坡节点": SG,
    "🇼🇸 台湾节点": TW,
    "🇰🇷 韩国节点": KR,
    "🌐 其他地区": OTHER,
}

TEST_URL = "https://cp.cloudflare.com/generate_204"

GEOSITE_MAP = {
    "private": [
        "# 局域网 / 私网",
        f"RULE-SET,{COR}/Lan.list,🎯 全球直连",
        "IP-CIDR,192.168.0.0/16,🎯 全球直连,no-resolve",
        "IP-CIDR,10.0.0.0/8,🎯 全球直连,no-resolve",
        "IP-CIDR,172.16.0.0/12,🎯 全球直连,no-resolve",
        "IP-CIDR,127.0.0.0/8,🎯 全球直连,no-resolve",
        "IP-CIDR,100.64.0.0/10,🎯 全球直连,no-resolve",
        "IP-CIDR,169.254.0.0/16,🎯 全球直连,no-resolve",
        "IP-CIDR6,fc00::/7,🎯 全球直连,no-resolve",
        "IP-CIDR6,fe80::/10,🎯 全球直连,no-resolve",
        "IP-CIDR6,::1/128,🎯 全球直连,no-resolve",
    ],
    "google-cn": [f"RULE-SET,{BM}/Google/Google.list,🇬 谷歌服务"],
    "category-games@cn": [f"RULE-SET,{BM}/SteamCN/SteamCN.list,🎯 全球直连"],
    "category-game-platforms-download": [f"RULE-SET,{BM}/Game/Game.list,🎯 全球直连"],
    "category-public-tracker": [f"RULE-SET,{BM}/PrivateTracker/PrivateTracker.list,🎯 全球直连"],
    "category-communication": [
        f"RULE-SET,{BM}/Telegram/Telegram.list,💬 即时通讯",
        f"RULE-SET,{BM}/Whatsapp/Whatsapp.list,💬 即时通讯",
        f"RULE-SET,{BM}/Line/Line.list,💬 即时通讯",
        f"RULE-SET,{BM}/Discord/Discord.list,💬 即时通讯",
        f"RULE-SET,{BM}/KakaoTalk/KakaoTalk.list,💬 即时通讯",
    ],
    "category-social-media-!cn": [
        f"RULE-SET,{BM}/Twitter/Twitter.list,🌐 社交媒体",
        f"RULE-SET,{BM}/Facebook/Facebook.list,🌐 社交媒体",
        f"RULE-SET,{BM}/Instagram/Instagram.list,🌐 社交媒体",
        f"RULE-SET,{BM}/Reddit/Reddit.list,🌐 社交媒体",
        f"RULE-SET,{BM}/Threads/Threads.list,🌐 社交媒体",
        f"RULE-SET,{BM}/LinkedIn/LinkedIn.list,🌐 社交媒体",
    ],
    "openai": [f"RULE-SET,{BM}/OpenAI/OpenAI.list,🤖 ChatGPT"],
    "category-ai-!cn": [
        f"RULE-SET,{BM}/Claude/Claude.list,🤖 AI服务",
        f"RULE-SET,{BM}/Anthropic/Anthropic.list,🤖 AI服务",
        f"RULE-SET,{BM}/Gemini/Gemini.list,🤖 AI服务",
        f"RULE-SET,{BM}/Copilot/Copilot.list,🤖 AI服务",
        f"RULE-SET,{BM}/BardAI/BardAI.list,🤖 AI服务",
        f"RULE-SET,{BM}/Civitai/Civitai.list,🤖 AI服务",
        "DOMAIN-SUFFIX,x.ai,🤖 AI服务",
        "DOMAIN-SUFFIX,grok.com,🤖 AI服务",
    ],
    "github": [f"RULE-SET,{BM}/GitHub/GitHub.list,🚀 GitHub"],
    "category-speedtest": [f"RULE-SET,{BM}/Speedtest/Speedtest.list,🚀 测速工具"],
    "steam": [f"RULE-SET,{BM}/Steam/Steam.list,🎮 Steam"],
    "youtube": [f"RULE-SET,{BM}/YouTube/YouTube.list,📹 YouTube"],
    "apple-tvplus": [f"RULE-SET,{BM}/AppleTV/AppleTV.list,🎥 AppleTV+"],
    "apple-cn": [
        f"RULE-SET,{BM}/Apple/Apple.list,🍎 苹果中国",
        "DOMAIN-SUFFIX,cdn-apple.com,🍎 苹果中国",
        "DOMAIN-SUFFIX,icloud.com,🍎 苹果中国",
        "DOMAIN-SUFFIX,icloud-content.com,🍎 苹果中国",
    ],
    "microsoft@cn": [f"RULE-SET,{BM}/Microsoft/Microsoft.list,Ⓜ️ 微软中国"],
    "category-cryptocurrency": [
        f"RULE-SET,{BM}/Cryptocurrency/Cryptocurrency.list,📈 Crypto",
        f"RULE-SET,{BM}/Crypto/Crypto.list,📈 Crypto",
        f"RULE-SET,{BM}/Binance/Binance.list,📈 Crypto",
    ],
    "googlefcm": [f"RULE-SET,{BM}/GoogleFCM/GoogleFCM.list,📢 谷歌FCM"],
    "google": [f"RULE-SET,{BM}/Google/Google.list,🇬 谷歌服务"],
    "tiktok": [f"RULE-SET,{BM}/TikTok/TikTok.list,🎶 TikTok"],
    "netflix": [f"RULE-SET,{BM}/Netflix/Netflix.list,🎥 Netflix"],
    "disney": [f"RULE-SET,{BM}/Disney/Disney.list,🎥 DisneyPlus"],
    "hbo": [f"RULE-SET,{BM}/HBO/HBO.list,🎥 HBO"],
    "primevideo": [
        f"RULE-SET,{BM}/AmazonPrimeVideo/AmazonPrimeVideo.list,🎥 PrimeVideo",
        f"RULE-SET,{BM}/PrimeVideo/PrimeVideo.list,🎥 PrimeVideo",
    ],
    "category-emby": [f"RULE-SET,{BM}/Emby/Emby.list,🎥 Emby"],
    "spotify": [f"RULE-SET,{BM}/Spotify/Spotify.list,🎻 Spotify"],
    "bahamut": [f"RULE-SET,{BM}/Bahamut/Bahamut.list,📺 Bahamut"],
    "category-games": [f"RULE-SET,{BM}/Game/Game.list,🎮 游戏平台"],
    "category-entertainment": [f"RULE-SET,{BM}/GlobalMedia/GlobalMedia.list,🌎 国外媒体"],
    "category-ecommerce": [
        f"RULE-SET,{BM}/Amazon/Amazon.list,🛒 国外电商",
        f"RULE-SET,{BM}/eBay/eBay.list,🛒 国外电商",
        f"RULE-SET,{BM}/Shopify/Shopify.list,🛒 国外电商",
        f"RULE-SET,{BM}/Shopee/Shopee.list,🛒 国外电商",
    ],
    "gfw": [f"RULE-SET,{BM}/Proxy/Proxy.list,🚀 手动选择"],
    "cn": [f"RULE-SET,{BM}/China/China.list,🎯 全球直连", "GEOIP,CN,🎯 全球直连,no-resolve"],
}

GEOIP_MAP = {
    "private": [],
    "telegram": [f"RULE-SET,{BM}/Telegram/Telegram.list,💬 即时通讯"],
    "twitter": [f"RULE-SET,{BM}/Twitter/Twitter.list,🌐 社交媒体"],
    "facebook": [f"RULE-SET,{BM}/Facebook/Facebook.list,🌐 社交媒体"],
    "google": [f"RULE-SET,{BM}/Google/Google.list,🇬 谷歌服务"],
    "netflix": [f"RULE-SET,{BM}/Netflix/Netflix.list,🎥 Netflix"],
    "cn": ["GEOIP,CN,🎯 全球直连,no-resolve"],
}


def fetch_ini_text() -> str:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(INI_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            if data:
                INI_CACHE.write_bytes(data)
                return data.decode("utf-8")
    except Exception as e:
        print(f"[build] Note: network fetch Custom_Clash.ini failed ({e}), using cache if available")

    if INI_CACHE.exists():
        return INI_CACHE.read_text(encoding="utf-8")
    raise SystemExit("No Custom_Clash.ini available (network failed and cache missing)")


def parse_ini_rules(
    ini_text: str,
    *,
    include_broad_cn: bool = True,
    include_final: bool = True,
    include_nonstandard_ports: bool = True,
) -> list[str]:
    rules: list[str] = []
    seen: set[str] = set()

    for raw_line in ini_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith(";"):
            continue
        if not line.startswith("ruleset="):
            continue

        content = line[len("ruleset="):].strip()
        parts = [p.strip() for p in content.split(",")]
        if not parts:
            continue
        group = parts[0]

        if len(parts) >= 2 and parts[1].startswith("[]"):
            rule_type = parts[1][2:].upper()
            val = parts[2] if len(parts) > 2 else ""
            no_resolve = any("no-resolve" in p.lower() for p in parts[3:]) or (len(parts) > 3 and "no-resolve" in parts[2].lower())

            if rule_type == "GEOSITE":
                val_lower = val.lower()
                if val_lower in ("cn", "gfw") and not include_broad_cn:
                    continue
                mapped = GEOSITE_MAP.get(val_lower)
                if mapped:
                    for m in mapped:
                        if m not in seen:
                            seen.add(m)
                            rules.append(m)
                else:
                    r = f"RULE-SET,{BM}/{val}/{val}.list,{group}"
                    if r not in seen:
                        seen.add(r)
                        rules.append(r)
            elif rule_type == "GEOIP":
                val_lower = val.lower()
                if val_lower == "cn" and not include_broad_cn:
                    continue
                mapped = GEOIP_MAP.get(val_lower)
                if mapped:
                    for m in mapped:
                        if m not in seen:
                            seen.add(m)
                            rules.append(m)
                else:
                    r = f"GEOIP,{val.upper()},{group}" + (",no-resolve" if no_resolve else "")
                    if r not in seen:
                        seen.add(r)
                        rules.append(r)
            elif rule_type in ("DOMAIN-SUFFIX", "DOMAIN-KEYWORD", "DOMAIN", "IP-CIDR", "IP-CIDR6"):
                nr = ",no-resolve" if (no_resolve or "no-resolve" in content.lower()) else ""
                r = f"{rule_type},{val},{group}{nr}"
                if r not in seen:
                    seen.add(r)
                    rules.append(r)
            elif rule_type == "FINAL":
                if include_final:
                    rules.append(f"FINAL,{group}")

        elif len(parts) >= 2 and (parts[1].startswith("clash-domain:") or parts[1].startswith("clash-classic:")):
            url_part = parts[1].split(":", 1)[1].strip()
            filename = url_part.split("/")[-1]
            list_name = filename.replace("_Domain.yaml", ".list").replace("_Classical.yaml", ".list").replace(".yaml", ".list")
            if "Custom_Port_Direct" in filename:
                if include_nonstandard_ports:
                    rules.append("# 80/443 以外端口")
                    rules.append(f"DST-PORT,1-79,{group}")
                    rules.append(f"DST-PORT,81-442,{group}")
                    rules.append(f"DST-PORT,444-65535,{group}")
            else:
                sr_url = f"{COR}/{list_name}"
                r = f"RULE-SET,{sr_url},{group}"
                if r not in seen:
                    seen.add(r)
                    rules.append(r)

    return rules


def parse_ini_groups(ini_text: str) -> list[str]:
    groups: list[str] = []
    for raw_line in ini_text.splitlines():
        line = raw_line.strip()
        if not line.startswith("custom_proxy_group="):
            continue
        content = line[len("custom_proxy_group="):].strip()
        parts = content.split("`")
        if len(parts) < 2:
            continue
        name = parts[0].strip()
        gtype = parts[1].strip().lower()

        if gtype == "url-test":
            if name in REGION_REGEX_MAP:
                regex = REGION_REGEX_MAP[name]
            elif name == "♻️ 自动选择":
                regex = INFO
            else:
                regex = parts[2].strip() if len(parts) > 2 else ".*"
            groups.append(
                f"{name} = url-test,url={TEST_URL},interval=300,timeout=5,tolerance=50,policy-regex-filter={regex}"
            )
        elif gtype == "select":
            if name in ("🚀 手动选择", "🀄️ 优选地址", "📁 文件传输"):
                groups.append(f"{name} = select,policy-regex-filter={INFO}")
            elif name == "🎯 全球直连":
                groups.append("🎯 全球直连 = select,DIRECT")
            else:
                members = []
                for p in parts[2:]:
                    p = p.strip()
                    if not p or p.startswith(".*"):
                        continue
                    if p.startswith("[]"):
                        members.append(p[2:].strip())
                    elif p in ("DIRECT", "REJECT"):
                        members.append(p)
                # Ensure GitHub defaults to 手动选择 first for reliability
                if name == "🚀 GitHub" and "🚀 手动选择" in members:
                    members = ["🚀 手动选择"] + [m for m in members if m != "🚀 手动选择"]
                groups.append(f"{name} = select," + ",".join(members))

    return groups


def proxy_group_lines() -> list[str]:
    ini_text = fetch_ini_text()
    return parse_ini_groups(ini_text)


def overlay_rule_lines(
    *,
    include_broad_cn: bool = True,
    include_final: bool = True,
    include_nonstandard_ports: bool = True,
) -> list[str]:
    ini_text = fetch_ini_text()
    return parse_ini_rules(
        ini_text,
        include_broad_cn=include_broad_cn,
        include_final=include_final,
        include_nonstandard_ports=include_nonstandard_ports,
    )


def nonstandard_port_lines() -> list[str]:
    return [
        "# 80/443 以外端口",
        "DST-PORT,1-79,🔀 非标端口",
        "DST-PORT,81-442,🔀 非标端口",
        "DST-PORT,444-65535,🔀 非标端口",
    ]


def main() -> None:
    lines: list[str] = [
        "# Shadowrocket 分流版（方案 A）",
        "# 源: mrc991/Custom_OpenClash_Rules cfg/Custom_Clash.ini (动态拉取解析)",
        "# 不含节点。不要从「首页 → 订阅」导入；从「配置 → 从 URL 下载 / 本地文件」导入。",
        "# 导入后点该文件 → 使用配置；首页全局路由选「配置」。现有订阅不要动。",
        "",
        "[General]",
        "bypass-system = true",
        "skip-proxy = 127.0.0.1, 192.168.0.0/16, 10.0.0.0/8, 172.16.0.0/12, 169.254.0.0/16, localhost, *.local, captive.apple.com",
        "tun-excluded-routes = 10.0.0.0/8, 100.64.0.0/10, 127.0.0.0/8, 169.254.0.0/16, 172.16.0.0/12, 192.168.0.0/16, 224.0.0.0/4, 255.255.255.255/32",
        "dns-server = https://1.1.1.1/dns-query #proxy, https://dns.google/dns-query #proxy",
        "fallback-dns-server = 1.1.1.1, 8.8.8.8",
        "ipv6 = true",
        "udp-policy-not-supported-behaviour = REJECT",
        "",
        "[Proxy Group]",
    ]
    lines.extend(proxy_group_lines())
    lines.append("")
    lines.append("[Rule]")
    lines.extend(
        overlay_rule_lines(include_broad_cn=True, include_final=True, include_nonstandard_ports=True)
    )
    lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes, {len(lines)} lines)")


if __name__ == "__main__":
    main()
