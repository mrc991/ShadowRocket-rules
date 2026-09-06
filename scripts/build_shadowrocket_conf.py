# -*- coding: utf-8 -*-
"""Build a nodes-free Shadowrocket conf from Custom_Clash.ini (scheme A)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Custom_Shadowrocket.conf"

BM = "https://testingcf.jsdelivr.net/gh/blackmatrix7/ios_rule_script@master/rule/Shadowrocket"
COR = "https://testingcf.jsdelivr.net/gh/mrc991/Custom_OpenClash_Rules@main/rule"

INFO = r"^((?!(流量|到期|套餐|剩余|官网|Expire|Traffic)).)*$"

# Shadowrocket 正则不吃 \b / lookbehind。日志里节点名是「US LA BWG」「🇯🇵 日本 02 …」。
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

TEST_URL = "https://cp.cloudflare.com/generate_204"


def bm(name: str) -> str:
    return f"{BM}/{name}/{name}.list"


def cor(name: str) -> str:
    return f"{COR}/{name}"


def rs(url: str, policy: str) -> str:
    return f"RULE-SET,{url},{policy}"


REGIONS = [
    "🇺🇸 美国节点",
    "🇭🇰 香港节点",
    "🇯🇵 日本节点",
    "🇸🇬 新加坡节点",
    "🇼🇸 台湾节点",
    "🇰🇷 韩国节点",
    "🌐 其他地区",
    "♻️ 自动选择",
]

CORE = ["🚀 手动选择", "🀄️ 优选地址", "📁 文件传输"]


def select(name: str, members: list[str]) -> str:
    return f"{name} = select," + ",".join(members)


def url_test(name: str, regex: str) -> str:
    return (
        f"{name} = url-test,url={TEST_URL},interval=300,timeout=5,tolerance=50,"
        f"policy-regex-filter={regex}"
    )


def proxy_group_lines() -> list[str]:
    a: list[str] = []
    p = a.append
    p(f"🚀 手动选择 = select,policy-regex-filter={INFO}")
    p(f"🀄️ 优选地址 = select,policy-regex-filter={INFO}")
    p(f"📁 文件传输 = select,policy-regex-filter={INFO}")
    p(
        f"♻️ 自动选择 = url-test,url={TEST_URL},interval=300,timeout=5,tolerance=50,"
        f"policy-regex-filter={INFO}"
    )
    p(url_test("🇭🇰 香港节点", HK))
    p(url_test("🇺🇸 美国节点", US))
    p(url_test("🇯🇵 日本节点", JP))
    p(url_test("🇸🇬 新加坡节点", SG))
    p(url_test("🇼🇸 台湾节点", TW))
    p(url_test("🇰🇷 韩国节点", KR))
    p(url_test("🌐 其他地区", OTHER))
    p("🎯 全球直连 = select,DIRECT")
    p(select("💬 即时通讯", CORE + REGIONS + ["🎯 全球直连"]))
    p(select("🌐 社交媒体", CORE + REGIONS + ["🎯 全球直连"]))
    p(select("🚀 GitHub", ["🚀 手动选择", "📁 文件传输", "🀄️ 优选地址"] + REGIONS + ["🎯 全球直连"]))
    p(select("🤖 ChatGPT", ["🀄️ 优选地址", "📁 文件传输", "🚀 手动选择"] + REGIONS + ["🎯 全球直连"]))
    p(select("🤖 AI服务", ["🀄️ 优选地址", "📁 文件传输", "🚀 手动选择"] + REGIONS + ["🎯 全球直连"]))
    p(select("📈 Crypto", ["🇭🇰 香港节点", "🚀 手动选择", "🀄️ 优选地址", "📁 文件传输", "🇺🇸 美国节点", "🇯🇵 日本节点", "🇸🇬 新加坡节点", "🇼🇸 台湾节点", "🇰🇷 韩国节点", "🌐 其他地区", "♻️ 自动选择", "🎯 全球直连"]))
    p(select("🎶 TikTok", CORE + REGIONS + ["🎯 全球直连"]))
    p(select("📹 YouTube", CORE + REGIONS + ["🎯 全球直连"]))
    p(select("🎥 TV Box", ["🎯 全球直连"] + CORE + ["🇺🇸 美国节点", "🇭🇰 香港节点", "🇯🇵 日本节点", "🇸🇬 新加坡节点", "🇼🇸 台湾节点", "🇰🇷 韩国节点", "🌐 其他地区", "♻️ 自动选择"]))
    p(select("🎥 Netflix", ["🇭🇰 香港节点"] + CORE + ["🇺🇸 美国节点", "🇯🇵 日本节点", "🇸🇬 新加坡节点", "🇼🇸 台湾节点", "🇰🇷 韩国节点", "🌐 其他地区", "♻️ 自动选择", "🎯 全球直连"]))
    p(select("🎥 DisneyPlus", ["🇭🇰 香港节点"] + CORE + ["🇺🇸 美国节点", "🇯🇵 日本节点", "🇸🇬 新加坡节点", "🇼🇸 台湾节点", "🇰🇷 韩国节点", "🌐 其他地区", "♻️ 自动选择", "🎯 全球直连"]))
    p(select("🎥 HBO", ["🇭🇰 香港节点"] + CORE + ["🇺🇸 美国节点", "🇯🇵 日本节点", "🇸🇬 新加坡节点", "🇼🇸 台湾节点", "🇰🇷 韩国节点", "🌐 其他地区", "♻️ 自动选择", "🎯 全球直连"]))
    p(select("🎥 PrimeVideo", ["🇭🇰 香港节点"] + CORE + ["🇺🇸 美国节点", "🇯🇵 日本节点", "🇸🇬 新加坡节点", "🇼🇸 台湾节点", "🇰🇷 韩国节点", "🌐 其他地区", "♻️ 自动选择", "🎯 全球直连"]))
    p(select("🎥 AppleTV+", ["🇭🇰 香港节点"] + CORE + ["🇺🇸 美国节点", "🇯🇵 日本节点", "🇸🇬 新加坡节点", "🇼🇸 台湾节点", "🇰🇷 韩国节点", "🌐 其他地区", "♻️ 自动选择", "🎯 全球直连"]))
    p(select("🎥 Emby", ["🇭🇰 香港节点"] + CORE + ["🇺🇸 美国节点", "🇯🇵 日本节点", "🇸🇬 新加坡节点", "🇼🇸 台湾节点", "🇰🇷 韩国节点", "🌐 其他地区", "♻️ 自动选择", "🎯 全球直连"]))
    p(select("🎻 Spotify", ["🇭🇰 香港节点"] + CORE + ["🇺🇸 美国节点", "🇯🇵 日本节点", "🇸🇬 新加坡节点", "🇼🇸 台湾节点", "🇰🇷 韩国节点", "🌐 其他地区", "♻️ 自动选择", "🎯 全球直连"]))
    p(select("📺 Bahamut", ["🇼🇸 台湾节点", "🚀 手动选择", "🎯 全球直连"]))
    p(select("🌎 国外媒体", ["🇺🇸 美国节点"] + CORE + ["🇭🇰 香港节点", "🇯🇵 日本节点", "🇸🇬 新加坡节点", "🇼🇸 台湾节点", "🇰🇷 韩国节点", "🌐 其他地区", "♻️ 自动选择", "🎯 全球直连"]))
    p(select("🛒 国外电商", ["🇺🇸 美国节点"] + CORE + ["🇭🇰 香港节点", "🇯🇵 日本节点", "🇸🇬 新加坡节点", "🇼🇸 台湾节点", "🇰🇷 韩国节点", "🌐 其他地区", "♻️ 自动选择", "🎯 全球直连"]))
    p(select("📢 谷歌FCM", ["🀄️ 优选地址", "📁 文件传输", "🚀 手动选择"] + REGIONS + ["🎯 全球直连"]))
    p(select("🇬 谷歌服务", ["🀄️ 优选地址", "📁 文件传输", "🚀 手动选择"] + REGIONS + ["🎯 全球直连"]))
    p(select("🍎 苹果中国", ["🎯 全球直连"] + CORE + ["🇭🇰 香港节点", "🇺🇸 美国节点", "🇯🇵 日本节点", "🇸🇬 新加坡节点", "🇼🇸 台湾节点", "🇰🇷 韩国节点", "🌐 其他地区", "♻️ 自动选择"]))
    p(select("Ⓜ️ 微软中国", ["🎯 全球直连"] + CORE + ["🇭🇰 香港节点", "🇺🇸 美国节点", "🇯🇵 日本节点", "🇸🇬 新加坡节点", "🇼🇸 台湾节点", "🇰🇷 韩国节点", "🌐 其他地区", "♻️ 自动选择"]))
    p(select("🎮 游戏平台", ["🎯 全球直连"] + CORE + ["🇭🇰 香港节点", "🇺🇸 美国节点", "🇯🇵 日本节点", "🇸🇬 新加坡节点", "🇼🇸 台湾节点", "🇰🇷 韩国节点", "🌐 其他地区", "♻️ 自动选择"]))
    p(select("🎮 Steam", ["🎯 全球直连"] + CORE + ["🇭🇰 香港节点", "🇺🇸 美国节点", "🇯🇵 日本节点", "🇸🇬 新加坡节点", "🇼🇸 台湾节点", "🇰🇷 韩国节点", "🌐 其他地区", "♻️ 自动选择"]))
    p(select("🚀 测速工具", ["🎯 全球直连"] + CORE + ["🇭🇰 香港节点", "🇺🇸 美国节点", "🇯🇵 日本节点", "🇸🇬 新加坡节点", "🇼🇸 台湾节点", "🇰🇷 韩国节点", "🌐 其他地区", "♻️ 自动选择"]))
    p(select("🐟 漏网之鱼", CORE + REGIONS + ["🎯 全球直连"]))
    p(select("🔀 非标端口", ["🐟 漏网之鱼", "📁 文件传输", "🎯 全球直连"]))
    return a


def overlay_rule_lines(
    *,
    include_broad_cn: bool = True,
    include_final: bool = True,
    include_nonstandard_ports: bool = True,
) -> list[str]:
    a: list[str] = []
    p = a.append
    p("# 局域网 / 私网")
    p(rs(cor("Lan.list"), "🎯 全球直连"))
    p("IP-CIDR,192.168.0.0/16,🎯 全球直连,no-resolve")
    p("IP-CIDR,10.0.0.0/8,🎯 全球直连,no-resolve")
    p("IP-CIDR,172.16.0.0/12,🎯 全球直连,no-resolve")
    p("IP-CIDR,127.0.0.0/8,🎯 全球直连,no-resolve")
    p("IP-CIDR,100.64.0.0/10,🎯 全球直连,no-resolve")
    p("IP-CIDR,169.254.0.0/16,🎯 全球直连,no-resolve")
    p("IP-CIDR6,fc00::/7,🎯 全球直连,no-resolve")
    p("IP-CIDR6,fe80::/10,🎯 全球直连,no-resolve")
    p("IP-CIDR6,::1/128,🎯 全球直连,no-resolve")

    p("# Tailscale 控制面 → 优选（须在 Custom_Direct 之前）")
    p("DOMAIN-SUFFIX,tailscale.com,🀄️ 优选地址")
    p("DOMAIN-SUFFIX,tailscale.io,🀄️ 优选地址")

    p("# TV Box（客厅 Shield 电影天堂，默认直连，可切代理）")
    p("DOMAIN-SUFFIX,jimxtc.com,🎥 TV Box")
    p("DOMAIN-SUFFIX,cqkpx.com,🎥 TV Box")
    p("DOMAIN-SUFFIX,dytt-tvs.com,🎥 TV Box")
    p("DOMAIN-SUFFIX,dytt-tupian.com,🎥 TV Box")
    p("DOMAIN-SUFFIX,dyttzyapi.com,🎥 TV Box")

    p("# 自建 DERP")
    p("IP-CIDR,45.62.118.67/32,🎯 全球直连,no-resolve")
    p("IP-CIDR,192.210.136.225/32,🎯 全球直连,no-resolve")

    p("# 项目收录直连 / 代理")
    p(rs(cor("Custom_Direct.list"), "🎯 全球直连"))
    p(rs(cor("Custom_Proxy.list"), "🚀 手动选择"))

    p("# 国内游戏 / 下载 / Tracker")
    p(rs(bm("SteamCN"), "🎯 全球直连"))
    p(rs(cor("Steam_CDN.list"), "🎯 全球直连"))
    p(rs(bm("PrivateTracker"), "🎯 全球直连"))

    p("# 即时通讯 / 社交媒体")
    p(rs(bm("Telegram"), "💬 即时通讯"))
    p(rs(bm("Whatsapp"), "💬 即时通讯"))
    p(rs(bm("Line"), "💬 即时通讯"))
    p(rs(bm("Discord"), "💬 即时通讯"))
    p(rs(bm("KakaoTalk"), "💬 即时通讯"))
    p(rs(bm("Twitter"), "🌐 社交媒体"))
    p(rs(bm("Facebook"), "🌐 社交媒体"))
    p(rs(bm("Instagram"), "🌐 社交媒体"))
    p(rs(bm("Reddit"), "🌐 社交媒体"))
    p(rs(bm("Threads"), "🌐 社交媒体"))
    p(rs(bm("LinkedIn"), "🌐 社交媒体"))

    p("# AI / GitHub / 测速 / Steam / 媒体")
    p(rs(bm("OpenAI"), "🤖 ChatGPT"))
    p(rs(bm("Claude"), "🤖 AI服务"))
    p(rs(bm("Anthropic"), "🤖 AI服务"))
    p(rs(bm("Gemini"), "🤖 AI服务"))
    p(rs(bm("Copilot"), "🤖 AI服务"))
    p(rs(bm("BardAI"), "🤖 AI服务"))
    p(rs(bm("Civitai"), "🤖 AI服务"))
    p("DOMAIN-SUFFIX,x.ai,🤖 AI服务")
    p("DOMAIN-SUFFIX,grok.com,🤖 AI服务")
    p(rs(bm("GitHub"), "🚀 GitHub"))
    p(rs(bm("Speedtest"), "🚀 测速工具"))
    p(rs(bm("Steam"), "🎮 Steam"))
    p(rs(bm("YouTube"), "📹 YouTube"))
    p(rs(bm("AppleTV"), "🎥 AppleTV+"))
    p(rs(bm("Apple"), "🍎 苹果中国"))
    p("DOMAIN-SUFFIX,cdn-apple.com,🍎 苹果中国")
    p("DOMAIN-SUFFIX,icloud.com,🍎 苹果中国")
    p("DOMAIN-SUFFIX,icloud-content.com,🍎 苹果中国")
    p(rs(bm("Microsoft"), "Ⓜ️ 微软中国"))

    p("# 文件传输")
    p("DOMAIN-KEYWORD,filen,📁 文件传输")
    p("DOMAIN-SUFFIX,drive.google.com,📁 文件传输")
    p("DOMAIN-SUFFIX,googledrive.com,📁 文件传输")
    p("DOMAIN-SUFFIX,docs.google.com,📁 文件传输")
    p("DOMAIN-KEYWORD,googledrive,📁 文件传输")
    p(rs(bm("GoogleDrive"), "📁 文件传输"))

    p("# 自定义")
    p("DOMAIN-SUFFIX,bigrich.cc,🚀 手动选择")
    p("DOMAIN-SUFFIX,heiyu.space,🎯 全球直连")
    p("DOMAIN-SUFFIX,lazycat.cloud,🎯 全球直连")
    p("DOMAIN-KEYWORD,blueair,🎯 全球直连")
    p("DOMAIN-KEYWORD,qzymetc,🇭🇰 香港节点")
    p(rs(bm("Cryptocurrency"), "📈 Crypto"))
    p(rs(bm("Crypto"), "📈 Crypto"))
    p(rs(bm("Binance"), "📈 Crypto"))
    p("IP-CIDR,47.246.0.0/16,🎯 全球直连,no-resolve")
    p("IP-CIDR,47.251.0.0/16,🎯 全球直连,no-resolve")
    p("IP-CIDR,47.88.0.0/17,🎯 全球直连,no-resolve")
    p("DOMAIN-SUFFIX,taobao.com,🎯 全球直连")
    p("DOMAIN-SUFFIX,tmall.com,🎯 全球直连")
    p("DOMAIN-SUFFIX,alicdn.com,🎯 全球直连")
    p("DOMAIN-SUFFIX,alibabadns.com,🎯 全球直连")
    p("DOMAIN-SUFFIX,tbcache.com,🎯 全球直连")
    p("DOMAIN-SUFFIX,umeng.com,🎯 全球直连")

    p("# 谷歌 / 流媒体")
    p(rs(bm("GoogleFCM"), "📢 谷歌FCM"))
    p(rs(bm("Google"), "🇬 谷歌服务"))
    p(rs(bm("TikTok"), "🎶 TikTok"))
    p(rs(bm("Netflix"), "🎥 Netflix"))
    p(rs(bm("Disney"), "🎥 DisneyPlus"))
    p(rs(bm("HBO"), "🎥 HBO"))
    p(rs(bm("AmazonPrimeVideo"), "🎥 PrimeVideo"))
    p(rs(bm("PrimeVideo"), "🎥 PrimeVideo"))
    p(rs(bm("Emby"), "🎥 Emby"))
    p(rs(bm("Spotify"), "🎻 Spotify"))
    p(rs(bm("Bahamut"), "📺 Bahamut"))
    p(rs(bm("Game"), "🎮 游戏平台"))
    p(rs(bm("GlobalMedia"), "🌎 国外媒体"))
    p(rs(bm("Amazon"), "🛒 国外电商"))
    p(rs(bm("eBay"), "🛒 国外电商"))
    p(rs(bm("Shopify"), "🛒 国外电商"))
    p(rs(bm("Shopee"), "🛒 国外电商"))

    if include_broad_cn:
        p("# GFW / 国内兜底")
        p(rs(bm("Proxy"), "🚀 手动选择"))
        p(rs(bm("China"), "🎯 全球直连"))
        p("GEOIP,CN,🎯 全球直连,no-resolve")

    if include_nonstandard_ports:
        p("# 80/443 以外端口")
        p("DST-PORT,1-79,🔀 非标端口")
        p("DST-PORT,81-442,🔀 非标端口")
        p("DST-PORT,444-65535,🔀 非标端口")

    if include_final:
        p("FINAL,🐟 漏网之鱼")
    return a


def nonstandard_port_lines() -> list[str]:
    return [
        "# 80/443 以外端口",
        "DST-PORT,1-79,🔀 非标端口",
        "DST-PORT,81-442,🔀 非标端口",
        "DST-PORT,444-65535,🔀 非标端口",
    ]


def main() -> None:
    lines: list[str] = [
        "# Shadowrocket 分流试玩版（方案 A）",
        "# 源: mrc991/Custom_OpenClash_Rules cfg/Custom_Clash.ini @ eb44922e (2026-08-28)",
        "# 不含节点。不要从「首页 → 订阅」导入；从「配置 → 从 URL 下载 / 本地文件」导入。",
        "# 导入后点该文件 → 使用配置；首页全局路由选「配置」。现有订阅不要动。",
        "",
        "[General]",
        "bypass-system = true",
        "skip-proxy = 127.0.0.1, 192.168.0.0/16, 10.0.0.0/8, 172.16.0.0/12, 169.254.0.0/16, localhost, *.local, captive.apple.com",
        "tun-excluded-routes = 10.0.0.0/8, 100.64.0.0/10, 127.0.0.0/8, 169.254.0.0/16, 172.16.0.0/12, 192.168.0.0/16, 224.0.0.0/4, 255.255.255.255/32",
        "dns-server = system, 223.5.5.5, 119.29.29.29",
        "fallback-dns-server = 8.8.8.8, 1.1.1.1",
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
