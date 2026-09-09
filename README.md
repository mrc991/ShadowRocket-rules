# ShadowRocket-rules

Shadowrocket (小火箭) 完整分流规则配置，每日自动与上游广告规则同步更新。

## 特色

1. **上游广告拦截与白名单**：每日同步 [Johnshall/Shadowrocket-ADBlock-Rules-Forever](https://github.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever) 的 `sr_top500_whitelist_ad.conf`（拦截广告 + 国内 top500 白名单直连）。
2. **精细化策略组**：无缝叠加 `Custom_Clash.ini` 策略分组（GitHub / AI 服务 / 即时通讯 / 社交媒体 / 流媒体 Netflix/Disney/YouTube / 游戏 Steam / TV Box 等）。
3. **DNS / DoH**：主 DNS 用阿里 `dns.alidns.com` + DNSPod `doh.pub`（国内视图，保证 App Store 搜索与云闪付走国区）；Cloudflare / Google DoH 仅作 `fallback-dns-server` 且加 `#proxy`，避免海外域名被污染。国区 App Store / 银联云闪付进程与域名强制直连，且排在广告规则之前。
4. **无节点纯规则**：配置内不包含节点服务器，不破坏您在小火箭中已添加的机场节点与订阅。
5. **GitHub Actions 每日自动构建**：每天定时拉取上游合并，用户只需在小火箭中更新一次配置链接即可长久保持最新。

---

## 小火箭导入说明

> **重要提醒**：不要在小火箭首页「+」添加为节点订阅！必须在「配置」页面中导入。

### 1. 推荐配置链接（广告拦截 + 自定义分组）

* **GitHub Raw 链接**:
  ```text
  https://raw.githubusercontent.com/mrc991/ShadowRocket-rules/main/Custom_Shadowrocket_whitelist_ad.conf
  ```
* **jsDelivr CDN 加速链接**:
  ```text
  https://testingcf.jsdelivr.net/gh/mrc991/ShadowRocket-rules@main/Custom_Shadowrocket_whitelist_ad.conf
  ```

### 2. 纯分组配置链接（方案 A 基础版）

* **GitHub Raw 链接**:
  ```text
  https://raw.githubusercontent.com/mrc991/ShadowRocket-rules/main/Custom_Shadowrocket.conf
  ```
* **jsDelivr CDN 加速链接**:
  ```text
  https://testingcf.jsdelivr.net/gh/mrc991/ShadowRocket-rules@main/Custom_Shadowrocket.conf
  ```

---

## 导入步骤

1. 打开 Shadowrocket (小火箭) 底栏 **配置** 页面。
2. 点击右上角 **+** 号。
3. 粘贴上述配置 URL，点击 **下载**。
4. 在配置列表中找到下载的配置文件，点击并选择 **使用配置**（首次使用会编译规则集，稍等片刻）。
5. 返回小火箭首页，将「全局路由」设置为 **配置** 即可。首页现有节点与订阅完全不受影响。
