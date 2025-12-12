<div align="center">

#        个人使用  
**酷 • 干净 • 现代 **

---

### 混合型的项目仓库  
配置 · 脚本 · 工具 · 资源

</div>

---

## 📁收藏夹

| 分类 | 描述 | 链接 | 分类 | 描述 | 链接 |
|-----|------|-----|-----|------|-----|
| 名字 | 描述 | 链接 | 名字 | 描述 | 链接 |
| 名字 | 描述 | 链接 | 名字 | 描述 | 链接 |
| 名字 | 描述 | 链接 | 名字 | 描述 | 链接 |
| 名字 | 描述 | 链接 | 名字 | 描述 | 链接 |

---


<details>
<summary>个人定制修改</summary>
<summary>DNS防泄漏配置文件</summary>

```yaml
# =================== 自动测速（真实可用检测） ==
BaseUT: &BaseUT
  type: url-test
  url: https://cp.cloudflare.com/generate_204
  interval: 120
  timeout: 3500
  tolerance: 100
  max-failed-times: 3
  lazy: true
  hidden: true
  skip-cert-verify: true

  use-real-ip: true

# =================负载均衡-哈希策略（真实检测）==
BaseCH: &BaseCH
  type: load-balance
  url: https://cp.cloudflare.com/generate_204
  interval: 120
  timeout: 3500
  tolerance: 100
  max-failed-times: 3
  lazy: true
  hidden: true
  strategy: consistent-hashing
  skip-cert-verify: true

  use-real-ip: true

# =================负载均衡-轮询策略（真实检测）==
BaseCR: &BaseCR
  type: load-balance
  url: https://cp.cloudflare.com/generate_204
  interval: 120
  timeout: 3500
  tolerance: 100
  max-failed-times: 3
  lazy: true
  hidden: true
  strategy: round-robin
  skip-cert-verify: true

  use-real-ip: true

# =================服务商 provider（真实检测）==
BaseProvider: &BaseProvider
  type: http
  interval: 86400    # 一天更新一次订阅
  skip-cert-verify: true
  max-failed-times: 5

  health-check:
    enable: true
    interval: 600
    web-page-proxy: true
    url: https://www.gstatic.com/generate_204

    use-real-ip: true
  
# =================全球选择单独================
SelectAx: &SelectAx
  type: select
  proxies: [节点选择, 直接连接, 节点自选, 中国香港, 中国台湾, 日本国家, 韩国国家, 美国国家, 中国国家, 法国国家, 德国国家, 英国国家,]

# =================软件统一通用================
SelectAh: &SelectAh
  type: select
  proxies: [全球选择, 节点选择, 直接连接, 中国香港, 中国台湾, 日本国家, 韩国国家, 美国国家, 中国国家, 法国国家, 德国国家, 英国国家,]

# ================故障转移单独=================
SelectAg: &SelectAg
  type: select
  proxies: [全球选择, 拒绝流量, 直接连接, 中国香港, 中国台湾, 日本国家, 韩国国家, 美国国家, 中国国家, 法国国家, 德国国家, 英国国家,]

# =================国外流量单独================
SelectAo: &SelectAo
  type: select
  proxies: [全球选择, REJECT, REJECT]

# =================国内流量单独================
SelectAn: &SelectAn
  type: select
  proxies: [直接连接, 全球选择, 直接连接]

# =================拒绝流量单独================
SelectAu: &SelectAu
  type: select
  proxies: [REJECT, DIRECT, REJECT]

# =================服务商-提供 ================
proxy-providers: 
  服务商优:
    <<: *BaseProvider
    url: "https://gist.github.com/go4sharing/256ba0fc8a12ca81e1d556061f8b6fbd/raw/e6a323e04d1d5c66590f2ad7cbf8732382656f8b/gistfile1.txt"
    override:
    additional-prefix: "[优]"
  服务商备:
    <<: *BaseProvider
    url: "https://raw.githubusercontent.com/go4sharing/sub/main/sub.yaml"
    override:
    additional-prefix: "[备]"

#=================== DNS配置 =================
# ==================== DNS =====================
dns:
  listen: 0.0.0.0:5353
  ipv6: false
  enhanced-mode: fake-ip
  fake-ip-range: 198.18.0.1/16

  fake-ip-filter:
    - "*.lan"
    - "*.localdomain"
    - "*.example"
    - "*.test"
    - "*.localhost"
    - "*.home.arpa"
    - "*.local"
    - "*.mshome.net"
    - "*.corp"

  nameserver:
    - 233.6.6.6

  proxy-server-nameserver:
    - https://cloudflare-dns.com/dns-query

  fallback:
    - tls://dns.google:853

  fake-ip-ttl: 1

  fallback-filter:
    geoip: true
    ipcidr:
      - 0.0.0.0/8
      - 10.0.0.0/8
      - 192.0.0.0/24
      - 192.0.2.0/24
      - 192.168.0.0/16
      - 198.18.0.0/15
      - 198.51.100.0/24

  use-hosts: false
  proxy-dns-server: true
  parallel-request: true
  use-system-dns: false


# ==================== TUN =====================
tun:
  enable: true
  stack: system
  mtu: 1500
  dns-hijack:
    - any:53
    - udp://any:53
    - tcp://any:53
  auto-route: true
  auto-detect-interface: true
  strict-route: true
  endpoint-independent-nat: true
  udp-timeout: 60
# ===================国家大全-策略 ============
FilterHK: &FilterHK '^(?=.*(?i)(港|🇭🇰|HK|Hong|HKG)).*$'
FilterJP: &FilterJP '^(?=.*(?i)(日|🇯🇵|JP|Japan|NRT|HND|KIX|CTS|FUK)).*$'
FilterKR: &FilterKR '^(?=.*(?i)(韩|🇰🇷|韓|首尔|南朝鲜|KR|KOR|Korea|South)).*$'
FilterUS: &FilterUS '^(?=.*(?i)(美|美国|🇺🇸|US|USA|SJC|JFK|LAX|ORD|ATL|DFW|SFO|MIA|SEA|IAD)).*$'
FilterTW: &FilterTW '^(?=.*(?i)(台|🇼🇸|🇹🇼|TW|tai|TPE|TSA|KHH)).*$'
FilterCN: &FilterCN '^(?=.*(?i)(中|🇨🇳|CN|China|PEK|SHA|CAN|SHE|XMN)).*$'
FilterFR: &FilterFR '^(?=.*(?i)(法|🇫🇷|FR|France|CDG|LYS|MRS|NCE)).*$'
FilterDE: &FilterDE '^(?=.*(?i)(德|🇩🇪|DE|Germany|FRA|MUC|BER|DUS)).*$'
FilterGB: &FilterGB '^(?=.*(?i)(英|🇬🇧|GB|UK|England|LHR|LGW|MAN|STN)).*$'

FilterOT: &FilterOT '^(?!.*(DIRECT|直接连接|美|港|坡|台|新|日|韩|奥|比|保|克罗地亚|塞|捷|丹|爱沙|芬|法|德|希|匈|爱尔|意|拉|立|卢|马其它|荷|波|葡|罗|斯洛伐|斯洛文|西|瑞|英|🇭🇰|🇼🇸|🇹🇼|🇸🇬|🇯🇵|🇰🇷|🇺🇸|🇬🇧|🇦🇹|🇧🇪|🇨🇿|🇩🇰|🇫🇮|🇫🇷|🇩🇪|🇮🇪|🇮🇹|🇱🇹|🇱🇺|🇳🇱|🇵🇱|🇸🇪|HK|TW|SG|JP|KR|US|GB|CDG|FRA|AMS|MAD|BCN|FCO|MUC|BRU|HKG|TPE|TSA|KHH|SIN|XSP|NRT|HND|KIX|CTS|FUK|JFK|LAX|ORD|ATL|DFW|SFO|MIA|SEA|IAD|LHR|LGW))'

FilterAL: &FilterAL '^(?!.*(DIRECT|直接连接|群|邀请|返利|循环|官网|客服|网站|网址|获取|订阅|流量|到期|机场|下次|版本|官址|备用|过期|已用|联系|邮箱|工单|贩卖|通知|倒卖|防止|国内|地址|频道|无法|说明|使用|提示|特别|访问|支持|教程|关注|更新|作者|加入|USE|USED|TOTAL|EXPIRE|EMAIL|Panel|Channel|Author))'

proxy-groups:
  - {name: 全球选择, <<: *SelectAx}
  - {name: 节点选择, type: url-test, include-all: true}
  
  - {name: 中国香港, type: select, proxies: [香港自动, 香港散列, 香港轮询], include-all: true, filter: *FilterHK}
  - {name: 中国台湾, type: select, proxies: [台湾自动, 台湾散列, 台湾轮询], include-all: true, filter: *FilterTW}
  - {name: 日本国家, type: select, proxies: [日本自动, 日本散列, 日本轮询], include-all: true, filter: *FilterJP}
  - {name: 韩国国家, type: select, proxies: [韩国自动, 韩国散列, 韩国轮询], include-all: true, filter: *FilterKR}
  - {name: 美国国家, type: select, proxies: [美国自动, 美国散列, 美国轮询], include-all: true, filter: *FilterUS}
  - {name: 中国国家, type: select, proxies: [中国自动, 中国散列, 中国轮询], include-all: true, filter: *FilterCN}
  - {name: 法国国家, type: select, proxies: [法国自动, 法国散列, 法国轮询], include-all: true, filter: *FilterFR}
  - {name: 德国国家, type: select, proxies: [德国自动, 德国散列, 德国轮询], include-all: true, filter: *FilterDE}
  - {name: 英国国家, type: select, proxies: [英国自动, 英国散列, 英国轮询], include-all: true, filter: *FilterGB}
  - {name: 龙王之鱼, <<: *SelectAo}
  - {name: 国外流量, <<: *SelectAo}
  - {name: 国内流量, <<: *SelectAn}
  - {name: 链式代理,   type: select, proxies: [中转代理, 落地代理]}
  - {name: 中转代理,       type: select, proxies: [节点自选, 节点选择, 直接连接, 中国香港, 中国台湾, 日本国家, 韩国国家, 美国国家, 中国国家, 法国国家, 德国国家, 英国国家]}
  - {name: 落地代理,       type: select, include-all: true, filter: *FilterAL}
  - {name: 节点自选, type: select, include-all: true}
  - {name: 故障转移, type: select, <<: *SelectAg}
  - {name: 直接连接, type: select, proxies: [DIRECT], hidden: true}
  - {name: 拒绝流量, type: select, <<: *SelectAu}

# ===================自动测速-策略 ============
  - {name: 香港自动, <<: *BaseUT, include-all: true, filter: *FilterHK}
  - {name: 台湾自动, <<: *BaseUT, include-all: true, filter: *FilterTW}
  - {name: 日本自动, <<: *BaseUT, include-all: true, filter: *FilterJP}
  - {name: 韩国自动, <<: *BaseUT, include-all: true, filter: *FilterKR}
  - {name: 美国自动, <<: *BaseUT, include-all: true, filter: *FilterUS}
  - {name: 中国自动, <<: *BaseUT, include-all: true, filter: *FilterCN}
  - {name: 法国自动, <<: *BaseUT, include-all: true, filter: *FilterFR}
  - {name: 德国自动, <<: *BaseUT, include-all: true, filter: *FilterDE}
  - {name: 英国自动, <<: *BaseUT, include-all: true, filter: *FilterGB}

# =================负载均衡-,散列 =============
  - {name: 香港散列, <<: *BaseCH, include-all: true, filter: *FilterHK}
  - {name: 台湾散列, <<: *BaseCH, include-all: true, filter: *FilterTW}
  - {name: 日本散列, <<: *BaseCH, include-all: true, filter: *FilterJP}
  - {name: 韩国散列, <<: *BaseCH, include-all: true, filter: *FilterKR}
  - {name: 美国散列, <<: *BaseCH, include-all: true, filter: *FilterUS}
  - {name: 中国散列, <<: *BaseCH, include-all: true, filter: *FilterCN}
  - {name: 法国散列, <<: *BaseCH, include-all: true, filter: *FilterFR}
  - {name: 德国散列, <<: *BaseCH, include-all: true, filter: *FilterDE}
  - {name: 英国散列, <<: *BaseCH, include-all: true, filter: *FilterGB}

# =================负载均衡-轮询 ==============
  - {name: 香港轮询, <<: *BaseCR, include-all: true, filter: *FilterHK}
  - {name: 台湾轮询, <<: *BaseCR, include-all: true, filter: *FilterTW}
  - {name: 日本轮询, <<: *BaseCR, include-all: true, filter: *FilterJP}
  - {name: 韩国轮询, <<: *BaseCR, include-all: true, filter: *FilterKR}
  - {name: 美国轮询, <<: *BaseCR, include-all: true, filter: *FilterUS}
  - {name: 中国轮询, <<: *BaseCR, include-all: true, filter: *FilterCN}
  - {name: 法国轮询, <<: *BaseCR, include-all: true, filter: *FilterFR}
  - {name: 德国轮询, <<: *BaseCR, include-all: true, filter: *FilterDE}
  - {name: 英国轮询, <<: *BaseCR, include-all: true, filter: *FilterGB}
# =================规则 ======================
rules:
  - RULE-SET,国内流量,国内流量

  - RULE-SET,国内流量IP,国内流量,no-resolve
  
  - MATCH,国外流量

# ===============规则集行为模板=================
BehaviorDN: &BehaviorDN {type: http, behavior: domain, format: mrs, interval: 86400}
BehaviorIP: &BehaviorIP {type: http, behavior: ipcidr, format: mrs, interval: 86400}

# ================规则提供者===================
rule-providers:

  国内流量:
    <<: *BehaviorDN
    url: https://raw.githubusercontent.com/666OS/rules/release/mihomo/domain/China.mrs

  国内流量IP:
    <<: *BehaviorIP
    url: https://raw.githubusercontent.com/666OS/rules/release/mihomo/ip/China.mrs
```

</details>

<details>
<summary>DNS防泄漏脚本</summary>

```js
const config = {
  dns: {
    listen: "0.0.0.0:5353",
    ipv6: false,
    enhancedMode: "fake-ip",
    fakeIpRange: "198.18.0.1/16",
    fakeIpFilter: [
      "*.lan",
      "*.localdomain",
      "*.example",
      "*.test",
      "*.localhost",
      "*.home.arpa",
      "*.local",
      "*.mshome.net",
      "*.corp"
    ],
    nameserver: [
      "233.6.6.6"
    ],
    proxyServerNameserver: [
      "https://cloudflare-dns.com/dns-query"
    ],
    fallback: [
      "tls://dns.google:853"
    ],
    fakeIpTtl: 1,
    fallbackFilter: {
      geoip: true,
      ipcidr: [
        "0.0.0.0/8",
        "10.0.0.0/8",
        "192.0.0.0/24",
        "192.0.2.0/24",
        "192.168.0.0/16",
        "198.18.0.0/15",
        "198.51.100.0/24"
      ]
    },
    useHosts: false,
    proxyDnsServer: true,
    parallelRequest: true,
    useSystemDns: false
  },

  tun: {
    enable: true,
    stack: "system",
    mtu: 1500,
    dnsHijack: [
      "any:53",
      "udp://any:53",
      "tcp://any:53"
    ],
    autoRoute: true,
    autoDetectInterface: true,
    strictRoute: true,
    endpointIndependentNat: true,
    udpTimeout: 60
  }
};

function main() {
  return config;
}

main();
```

</details>