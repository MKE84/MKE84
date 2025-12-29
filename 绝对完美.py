import logging
import concurrent.futures
import socket
import base64
import requests
import yaml
import time
import datetime  
import logging
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    Defaults,
    filters
)
import re
from urllib.parse import unquote
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib3.exceptions import InsecureRequestWarning
import warnings



# ---------------- 导入所有依赖模块 --------------------
import warnings
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import re
import base64
from urllib.parse import unquote
import yaml
import logging

BOT_TOKEN = ""  # 去@BotFather获取
AUTHORIZED_USER_IDS = {}  # 去@userinfobot获取自己的ID
NODES_PER_PAGE = 100  # 每页显示节点数量
# ---------------- 初始化日志 --------------------

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# ---------------- 用户相关全局状态 --------------------
nodes_cache = dict()
nodes_fold_status = dict()
user_filter_params = dict()

# ---------------- 定义国旗映射表 --------------------
COUNTRY_FLAGS = {

    "CN": "🇨🇳",   # 中国
    "TW": "🇹🇼",   # 台湾
    "HK": "🇭🇰",   # 香港
    "MO": "🇲🇴",   # 澳门
    "BD": "🇧🇩",   # 孟加拉国
    "LK": "🇱🇰",   # 斯里兰卡
    "MM": "🇲🇲",   # 缅甸
    "KH": "🇰🇭",   # 柬埔寨
    "LA": "🇱🇦",   # 老挝
    "MN": "🇲🇳",   # 蒙古
    "BH": "🇧🇭",   # 巴林
    "OM": "🇴🇲",   # 阿曼
    "SY": "🇸🇾",   # 叙利亚
    "JO": "🇯🇴",   # 约旦
    "LB": "🇱🇧",   # 黎巴嫩
    "KZ": "🇰🇿",   # 哈萨克斯坦
    "UZ": "🇺🇿",   # 乌兹别克斯坦
    "GR": "🇬🇷",   # 希腊
    "RO": "🇷🇴",   # 罗马尼亚
    "BG": "🇧🇬",   # 保加利亚
    "RS": "🇷🇸",   # 塞尔维亚
    "BY": "🇧🇾",   # 白俄罗斯
    "EE": "🇪🇪",   # 爱沙尼亚
    "LV": "🇱🇻",   # 拉脱维亚
    "LT": "🇱🇹",   # 立陶宛
    "SI": "🇸🇮",   # 斯洛文尼亚
    "SK": "🇸🇰",   # 斯洛伐克
    "HR": "🇭🇷",   # 克罗地亚
    "IS": "🇮🇸",   # 冰岛
    "MT": "🇲🇹",   # 马耳他
    "CY": "🇨🇾",   # 塞浦路斯

    # 美洲（新增）
    "CO": "🇨🇴",   # 哥伦比亚
    "VE": "🇻🇪",   # 委内瑞拉
    "PE": "🇵🇪",   # 秘鲁
    "EC": "🇪🇨",   # 厄瓜多尔
    "UY": "🇺🇾",   # 乌拉圭
    "PY": "🇵🇾",   # 巴拉圭
    "CU": "🇨🇺",   # 古巴
    "DO": "🇩🇴",   # 多米尼加
    "JM": "🇯🇲",   # 牙买加
    "PG": "🇵🇬",   # 巴布亚新几内亚
    "FJ": "🇫🇯",   # 斐济
    "SB": "🇸🇧",   # 所罗门群岛
    "KE": "🇰🇪",   # 肯尼亚
    "TZ": "🇹🇿",   # 坦桑尼亚
    "GH": "🇬🇭",   # 加纳
    "NA": "🇳🇦",   # 纳米比亚
    "ZW": "🇿🇼",   # 津巴布韦
    "BW": "🇧🇼",   # 博茨瓦纳
    "ZM": "🇿🇲",   # 赞比亚
    "MG": "🇲🇬",   # 马达加斯加
    "DZ": "🇩🇿",   # 阿尔及利亚
    "MA": "🇲🇦",   # 摩洛哥
    "TN": "🇹🇳",   # 突尼斯
    "SG": "🇸🇬",   # 新加坡
    "JP": "🇯🇵",   # 日本
    "KR": "🇰🇷",   # 韩国
    "MY": "🇲🇾",   # 马来西亚
    "TH": "🇹🇭",   # 泰国
    "US": "🇺🇸",   # 美国
    "GB": "🇬🇧",   # 英国
    "DE": "🇩🇪",   # 德国
    "FR": "🇫🇷",   # 法国
    "NL": "🇳🇱",   # 荷兰
    "CA": "🇨🇦",   # 加拿大
    "AU": "🇦🇺",   # 澳大利亚
    "NZ": "🇳🇿",   # 新西兰
    "ZA": "🇿🇦",   # 南非

    # 兜底
    "UNKNOWN": "❓"  # 全球通用图标
}

# ---------------- 定义缺失的extract_country_from_name函数 --------------------
def extract_country_from_name(name: str) -> str:
    """基础版国家码提取函数，作为兜底逻辑"""
    name_lower = name.lower()
    country_maps = {
            "台湾": "TW", "taiwan": "TW", "tw": "TW",
            "香港": "HK", "hongkong": "HK", "hk": "HK",
            "澳门": "MO", "macau": "MO", "macao": "MO", "mo": "MO",
            "新加坡": "SG", "singapore": "SG", "sg": "SG",
            "日本": "JP", "japan": "JP", "jp": "JP",
            "韩国": "KR", "korea": "KR", "south korea": "KR", "kr": "KR",
            "马来西亚": "MY", "malaysia": "MY", "my": "MY",
            "泰国": "TH", "thailand": "TH", "th": "TH",
            "越南": "VN", "vietnam": "VN", "vn": "VN",
            "印度": "IN", "india": "IN", "in": "IN",
            "俄罗斯": "RU", "russia": "RU", "ru": "RU",
            "菲律宾": "PH", "philippines": "PH", "ph": "PH",
            "印尼": "ID", "indonesia": "ID", "id": "ID",
            "印度尼西亚": "ID",
            "阿联酋": "AE", "uae": "AE", "united arab emirates": "AE", "ae": "AE",
            "沙特阿拉伯": "SA", "saudi arabia": "SA", "sa": "SA",
            "土耳其": "TR", "turkey": "TR", "tr": "TR",
            "伊朗": "IR", "iran": "IR", "ir": "IR",
            "以色列": "IL", "israel": "IL", "il": "IL",
            "哈萨克斯坦": "KZ", "kazakhstan": "KZ", "kz": "KZ",
            "巴基斯坦": "PK", "pakistan": "PK", "pk": "PK",
            "孟加拉国": "BD", "bangladesh": "BD", "bd": "BD",
            "斯里兰卡": "LK", "sri lanka": "LK", "lk": "LK",
            "缅甸": "MM", "myanmar": "MM", "mm": "MM",
            "柬埔寨": "KH", "cambodia": "KH", "kh": "KH",
            "老挝": "LA", "laos": "LA", "la": "LA",
            "蒙古": "MN", "mongolia": "MN", "mn": "MN",
            "卡塔尔": "QA", "qatar": "QA", "qa": "QA",
            "科威特": "KW", "kuwait": "KW", "kw": "KW",
            "阿曼": "OM", "oman": "OM", "om": "OM",
            "巴林": "BH", "bahrain": "BH", "bh": "BH",
            "叙利亚": "SY", "syria": "SY", "sy": "SY",
            "约旦": "JO", "jordan": "JO", "jo": "JO",
            "黎巴嫩": "LB", "lebanon": "LB", "lb": "LB",
            # 欧洲
            "英国": "GB", "uk": "GB", "united kingdom": "GB", "gb": "GB",
            "德国": "DE", "germany": "DE", "de": "DE",
            "法国": "FR", "france": "FR", "fr": "FR",
            "荷兰": "NL", "netherlands": "NL", "nl": "NL",
            "意大利": "IT", "italy": "IT", "it": "IT",
            "西班牙": "ES", "spain": "ES", "es": "ES",
            "瑞士": "CH", "switzerland": "CH", "ch": "CH",
            "瑞典": "SE", "sweden": "SE", "se": "SE",
            "挪威": "NO", "norway": "NO", "no": "NO",
            "丹麦": "DK", "denmark": "DK", "dk": "DK",
            "芬兰": "FI", "finland": "FI", "fi": "FI",
            "比利时": "BE", "belgium": "BE", "be": "BE",
            "奥地利": "AT", "austria": "AT", "at": "AT",
            "葡萄牙": "PT", "portugal": "PT", "pt": "PT",
            "希腊": "GR", "greece": "GR", "gr": "GR",
            "波兰": "PL", "poland": "PL", "pl": "PL",
            "捷克": "CZ", "czech republic": "CZ", "cz": "CZ",
            "匈牙利": "HU", "hungary": "HU", "hu": "HU",
            "罗马尼亚": "RO", "romania": "RO", "ro": "RO",
            "保加利亚": "BG", "bulgaria": "BG", "bg": "BG",
            "塞尔维亚": "RS", "serbia": "RS", "rs": "RS",
            "乌克兰": "UA", "ukraine": "UA", "ua": "UA",
            "白俄罗斯": "BY", "belarus": "BY", "by": "BY",
            "爱沙尼亚": "EE", "estonia": "EE", "ee": "EE",
            "拉脱维亚": "LV", "latvia": "LV", "lv": "LV",
            "立陶宛": "LT", "lithuania": "LT", "lt": "LT",
            "斯洛文尼亚": "SI", "slovenia": "SI", "si": "SI",
            "斯洛伐克": "SK", "slovakia": "SK", "sk": "SK",
            "克罗地亚": "HR", "croatia": "HR", "hr": "HR",
            "冰岛": "IS", "iceland": "IS", "is": "IS",
            "马耳他": "MT", "malta": "MT", "mt": "MT",
            "塞浦路斯": "CY", "cyprus": "CY", "cy": "CY",
            # 美洲
            "美国": "US", "usa": "US", "united states": "US", "us": "US",
            "加拿大": "CA", "canada": "CA", "ca": "CA",
            "墨西哥": "MX", "mexico": "MX", "mx": "MX",
            "巴西": "BR", "brazil": "BR", "br": "BR",
            "阿根廷": "AR", "argentina": "AR", "ar": "AR",
            "智利": "CL", "chile": "CL", "cl": "CL",
            "哥伦比亚": "CO", "colombia": "CO", "co": "CO",
            "委内瑞拉": "VE", "venezuela": "VE", "ve": "VE",
            "秘鲁": "PE", "peru": "PE", "pe": "PE",
            "厄瓜多尔": "EC", "ecuador": "EC", "ec": "EC",
            "玻利维亚": "BO", "bolivia": "BO", "bo": "BO",
            "巴拉圭": "PY", "paraguay": "PY", "py": "PY",
            "乌拉圭": "UY", "uruguay": "UY", "uy": "UY",
            "古巴": "CU", "cuba": "CU", "cu": "CU",
            "多米尼加": "DO", "dominican republic": "DO", "do": "DO",
            "牙买加": "JM", "jamaica": "JM", "jm": "JM",
            "特立尼达和多巴哥": "TT", "trinidad and tobago": "TT", "tt": "TT",
            "海地": "HT", "haiti": "HT", "ht": "HT",
            # 大洋洲
            "澳大利亚": "AU", "australia": "AU", "au": "AU",
            "新西兰": "NZ", "new zealand": "NZ", "nz": "NZ",
            "巴布亚新几内亚": "PG", "papua new guinea": "PG", "pg": "PG",
            "斐济": "FJ", "fiji": "FJ", "fj": "FJ",
            "所罗门群岛": "SB", "solomon islands": "SB", "sb": "SB",
            # 非洲
            "南非": "ZA", "south africa": "ZA", "za": "ZA",
            "埃及": "EG", "egypt": "EG", "eg": "EG",
            "尼日利亚": "NG", "nigeria": "NG", "ng": "NG",
            "肯尼亚": "KE", "kenya": "KE", "ke": "KE",
            "坦桑尼亚": "TZ", "tanzania": "TZ", "tz": "TZ",
            "加纳": "GH", "ghana": "GH", "gh": "GH",
            "纳米比亚": "NA", "namibia": "NA", "na": "NA",
            "津巴布韦": "ZW", "zimbabwe": "ZW", "zw": "ZW",
            "博茨瓦纳": "BW", "botswana": "BW", "bw": "BW",
            "赞比亚": "ZM", "zambia": "ZM", "zm": "ZM",
            "马达加斯加": "MG", "madagascar": "MG", "mg": "MG",
            "阿尔及利亚": "DZ", "algeria": "DZ", "dz": "DZ",
            "摩洛哥": "MA", "morocco": "MA", "ma": "MA",
            "突尼斯": "TN", "tunisia": "TN", "tn": "TN",
            "塞内加尔": "SN", "senegal": "SN", "sn": "SN",
            "乌干达": "UG", "uganda": "UG", "ug": "UG",
            "卢旺达": "RW", "rwanda": "RW", "rw": "RW"
    }
    for map_name, map_code in country_maps.items():
        if map_name in name_lower:
            return map_code
    return "UNKNOWN"

# ---------------- 定义辅助函数 --------------------
def bytes_to_human(size: float) -> str:
    """字节转人类可读格式（比如1024→1KB）"""
    units = ["B", "KB", "MB", "GB", "TB"]
    for unit in units:
        if size < 1024:
            return f"{round(size, 2)} {unit}"
        size /= 1024
    return f"{round(size, 2)} PB"

def auto_detect_traffic_display(used: str, total: str) -> tuple:
    """流量显示自动处理（根据你的需求简单实现）"""
    return used if used != "隐藏" else "0", total if total != "隐藏" else "0"

def auto_detect_time_display(expired: str) -> str:
    """过期时间自动处理（转成人类可读格式）"""
    if expired == "隐藏" or not expired.isdigit():
        return "未知"
    try:
        from datetime import datetime
        return datetime.fromtimestamp(int(expired)).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return "未知"

# ---------------- 订阅解析主函数（完全沿用之前的最终版逻辑） --------------------
def parse_clash_subscription(sub_url: str) -> dict:
    """解析Clash订阅（支持base64编码、节点链接、更多协议，返回标准格式数据）"""
    try:
        warnings.filterwarnings("ignore", category=InsecureRequestWarning)
        session = requests.Session()
        session.mount("http://", HTTPAdapter(max_retries=Retry(3, backoff_factor=1, status_forcelist=[429,500,502,503,504])))
        session.mount("https://", HTTPAdapter(max_retries=Retry(3, backoff_factor=1, status_forcelist=[429,500,502,503,504])))
        
        # ========== 节点链接解析 ==========
        SUPPORTED_PROTOCOLS = {"ss", "vmess", "trojan", "vless", "ssr", "trojan-go", "wireguard", "shadowsocksr"}
        single_node_match = re.match(rf'^({"|".join(SUPPORTED_PROTOCOLS)})://[A-Za-z0-9+/=]+$', sub_url.strip(), re.IGNORECASE)
        if single_node_match:
            logger.info("检测到节点链接，开始解析...")
            proto = single_node_match.group(1).lower()
            encoded_part = sub_url.split("://")[1]
            padded = encoded_part + '=' * ((4 - len(encoded_part) % 4) % 4)
            
            try:
                decoded = base64.urlsafe_b64decode(padded).decode('utf-8', errors='replace')
                name_match = re.search(r'name=([^&,]+)', decoded) or re.search(r'"ps":"([^"]+)"', decoded) or re.search(r'ps=([^&,]+)', decoded)
                name = name_match.group(1) if name_match else f"{proto}节点"
                country_code = extract_country_from_name(name)
                flag = COUNTRY_FLAGS.get(country_code, "🌐")
                
                return {
                    "subscription_url": "节点解析",
                    "traffic_used": "隐藏",
                    "traffic_total": "隐藏",
                    "expired": "隐藏",
                    "protocol": proto,
                    "total_nodes": 1,
                    "nodes": [
                        {
                            "name": name,
                            "protocol": proto,
                            "country": country_code,
                            "country_name": next((k for k, v in COUNTRY_FLAGS.items() if v == flag), "未知地区"),
                            "flag": flag,
                            "server": "未知（节点提取）",
                            "port": "未知（节点提取）"
                        }
                    ],
                    "all_countries": [next((k for k, v in COUNTRY_FLAGS.items() if v == flag), "未知地区")]
                }
            except Exception as e:
                logger.warning(f"节点解析失败，fallback到原订阅逻辑：{str(e)}")

        # ========== 原有订阅请求逻辑 ==========
        response = session.get(
            sub_url,
            timeout=25,
            headers={"User-Agent": "Clash/1.17.0 (+https://clash.dev)"},
            allow_redirects=True,
            verify=False
        )
        response.raise_for_status()
        raw_content = response.text.strip()
        if not raw_content:
            return {"error": "❌ 订阅返回空内容"}
        
        # ========== 解码逻辑 ==========
        decoded_text = raw_content
        if raw_content.startswith("clash://subscribe?url="):
            raw_content = re.sub(r'^clash://subscribe\?url=|&.*$', '', raw_content)
            raw_content = unquote(raw_content)
        for _ in range(3):
            try:
                padded = raw_content + '=' * ((4 - len(raw_content) % 4) % 4)
                decoded = base64.urlsafe_b64decode(padded).decode('utf-8', errors='replace')
                if re.match(r'^[A-Za-z0-9+/=]+$', decoded.strip()):
                    raw_content = decoded
                else:
                    decoded_text = decoded
                    break
            except:
                break
        
        # ========== 流量&过期时间提取 ==========
        traffic_used = None
        traffic_total = None
        expired = None
        
        info_headers = [
            response.headers.get("subscription-userinfo"),
            response.headers.get("X-Subscription-Userinfo"),
            response.headers.get("UserInfo")
        ]
        for header in info_headers:
            if header:
                upload = re.search(r'upload=(\d+)', header)
                download = re.search(r'download=(\d+)', header)
                total = re.search(r'total=(\d+)', header)
                expire_ts = re.search(r'expire=(\d+)', header)
                if upload and download and total:
                    total_used_bytes = float(upload.group(1)) + float(download.group(1))
                    traffic_used = bytes_to_human(total_used_bytes)
                    traffic_total = bytes_to_human(float(total.group(1)))
                if expire_ts:
                    expired = str(expire_ts.group(1))
                if traffic_used and expired:
                    break
        
        if not traffic_used:
            traffic_used_match = re.search(r'traffic_used:\s*([^\n]+)', decoded_text)
            traffic_total_match = re.search(r'traffic_total:\s*([^\n]+)', decoded_text)
            if traffic_used_match and traffic_total_match:
                traffic_used = traffic_used_match.group(1).strip()
                traffic_total = traffic_total_match.group(1).strip()
        
        if not expired:
            expired_match = re.search(r'expired:\s*([^\n]+)', decoded_text)
            if expired_match:
                expired = expired_match.group(1).strip()
        
        # ========== YAML解析节点 ==========
        try:
            config = yaml.safe_load(decoded_text)
            if not isinstance(config, dict):
                config = {"proxies": []}
        except yaml.YAMLError as e:
            logger.warning(f"YAML解析失败：{str(e)}，使用空节点列表")
            config = {"proxies": []}

        # ========== 节点处理（国旗优先识别） ==========
        proxies = config.get("proxies", [])
        valid_nodes = []
        
        FLAG_TO_COUNTRY = {
        
        }

        country_maps = {
        
        }

        
        for item in proxies:
            if not isinstance(item, dict):
                continue
            
            name = item.get("name", f"节点{len(valid_nodes)+1}")
            proto = item.get("type", "未知")
            if proto in SUPPORTED_PROTOCOLS:
                proto = proto.lower()
            else:
                proto = "未知"
            
            # 国旗优先识别逻辑
            flag = "❓"
            country_code = "UNKNOWN"
            country_name = "未知地区"
            
            for emoji, info in FLAG_TO_COUNTRY.items():
                if emoji in name:
                    flag = emoji
                    country_code = info["code"]
                    country_name = info["name"]
                    break
            
            if country_code == "UNKNOWN":
                country_code = item.get("country", extract_country_from_name(name))
                flag = COUNTRY_FLAGS.get(country_code, "❓")
                country_name = next((k for k, v in COUNTRY_FLAGS.items() if v == flag), "未知地区")
            
            if country_code == "UNKNOWN":
                name_lower = name.lower()
                for map_name, map_code in country_maps.items():
                    if map_name in name_lower:
                        country_code = map_code
                        flag = COUNTRY_FLAGS.get(country_code, "❓")
                        country_name = next((k for k, v in COUNTRY_FLAGS.items() if v == flag), "未知地区")
                        break
            
            server = item.get("server", "未知")
            port = item.get("port", "未知")

            valid_nodes.append({
                "name": name,
                "protocol": proto,
                "country": country_code,
                "country_name": country_name,
                "flag": flag,
                "server": server,
                "port": port
            })

        # 最终参数处理
        final_traffic_used = traffic_used or config.get("traffic_used", "隐藏")
        final_traffic_total = traffic_total or config.get("traffic_total", "隐藏")
        final_expired = expired or config.get("expired", "隐藏")

        auto_used, auto_total = auto_detect_traffic_display(final_traffic_used, final_traffic_total)
        auto_expired = auto_detect_time_display(final_expired)

        # 返回结果
        return {
            "subscription_url": sub_url,
            "traffic_used": auto_used,
            "traffic_total": auto_total,
            "expired": auto_expired,
            "protocol": ",".join(list(set(n["protocol"] for n in valid_nodes))) if valid_nodes else "未知",
            "total_nodes": len(valid_nodes),
            "nodes": valid_nodes,
            "all_countries": list(set(n["country_name"] for n in valid_nodes)) if valid_nodes else ["未知地区"]
        }
    except requests.exceptions.Timeout:
        return {"error": "❌ 订阅请求超时"}
    except requests.exceptions.RequestException as e:
        return {"error": f"❌ 订阅请求失败: {str(e)}"}
    except Exception as e:
        logger.error(f"订阅解析失败：{str(e)}")
        return {"error": f"❌ 订阅解析失败：{str(e)}"}






async def refresh_subscription(user_id: int) -> dict:
    """刷新订阅（无延迟测试逻辑）"""
    if user_id not in nodes_cache:
        return {"error": "无订阅数据可刷新"}
    
    sub_url = nodes_cache[user_id]["subscription_url"]
    logger.info(f"用户{user_id}开始刷新订阅：{sub_url}")

    parse_result = parse_clash_subscription(sub_url)
    if parse_result.get("error"):
        return parse_result

    nodes_cache[user_id] = parse_result
    return parse_result





# ---------------- 接收订阅链接的处理函数 --------------------
async def handle_subscription_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理用户发送的订阅链接（清除延迟测试残留）"""
    user_id = update.effective_user.id
    sub_url = update.message.text.strip()

    await update.message.reply_text("🔍 正在解析订阅链接...请稍等～")

    try:
        parse_result = parse_clash_subscription(sub_url)
        if parse_result.get("error"):
            await update.message.reply_text(f"解析失败：{parse_result['error']}")
            return

        nodes_cache[user_id] = parse_result
        user_filter_params.setdefault(user_id, {"country": None})
        nodes_fold_status.setdefault(user_id, True)

        await send_nodes_page(update, context, user_id, page=0)
    except Exception as e:
        logger.error(f"处理订阅失败：{str(e)}")
        await update.message.reply_text(f"处理失败：{str(e)}")


async def send_nodes_page(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, page: int, show_nodes=None, message_to_edit=None):
    try:
        data = nodes_cache[user_id]
        
        filter_country = user_filter_params.get(user_id, {}).get("country")
        filtered_nodes = data["nodes"]
        if filter_country and filter_country != "未知地区": 
            filtered_nodes = [n for n in filtered_nodes if n["country_name"] == filter_country]
        print(f"filtered_nodes长度: {len(filtered_nodes)}，内容预览: {[n.get('name') for n in filtered_nodes[:3]]}")
        
        nodes_per_page = NODES_PER_PAGE
        total_nodes = len(filtered_nodes)
        total_pages = (total_nodes - 1) // nodes_per_page + 1 if total_nodes > 0 else 1
        page = max(0, min(page, total_pages - 1))

        node_flags = []
        for n in filtered_nodes:
            flag = n.get("flag")
            if flag and flag not in node_flags:
                node_flags.append(flag)
        node_range = ",".join(node_flags) if node_flags else "🌐"

        header_text = (
            f"╭─━━━━━💠━订阅 信息━💠━━━━━╮\n"
            f"┃ 订阅链接: <code>{data['subscription_url'][:100]}</code>\n"
            f"┃ 流量详情: {data.get('traffic_used','隐藏')[:20]} / {data.get('traffic_total','隐藏')[:15]}\n"
            f"┃ 剩余时间: {data.get('expired','隐藏')[:30]}\n"
            f"┃ 协议类型: {data.get('protocol','未知')[:18]}\n"
            f"┃ 节点数量: {total_nodes}\n"
            f"┃ 国家范围: {node_range[:100]}\n"
            f"╰━━━━━━━━━━━━━━━━━━━━╯\n"
        )

        nodes_text = ""
        if show_nodes is None:
            show_nodes = nodes_fold_status.get(user_id, True)
        nodes_fold_status[user_id] = show_nodes

        if show_nodes and total_nodes > 0:
            start = page * nodes_per_page
            end = start + nodes_per_page
            chunk_nodes = filtered_nodes[start:end]
            node_lines = []
            for idx, node in enumerate(chunk_nodes, start=start+1):
                name = node.get("name","未知")[:15]
                flag = node.get("flag","") 
                node_lines.append(f"{name:<20} | {flag:2}")
            nodes_text = f" ╭──━━━🌐节点列表页 {page + 1}/{total_pages}🌐━━━──╮\n <pre>{'\n '.join(node_lines)}</pre>\n ╰━━━━━━━━━━━━━━━━━━━╯"

        elif show_nodes and total_nodes == 0:
            nodes_text = f" ╭─━━─━🌐节点列表🌐━─━━─╮\n <pre>⚠️ 该地区暂无节点哦～</pre>\n ╰━━━━━━━━━━━━━━━━╯"






        # ---------------- 按钮组try块内部！----------------
        keyboard = []
        page_buttons = []
        if page > 0:
            page_buttons.append(InlineKeyboardButton(" 上一页", callback_data=f"nodepage_{page-1}"))
        if page < total_pages - 1:
            page_buttons.append(InlineKeyboardButton("下一页 »", callback_data=f"nodepage_{page+1}"))
        page_buttons.append(InlineKeyboardButton(
            "展开节点" if not show_nodes else "收起节点",
            callback_data=f"toggle_nodes_{page}"
        ))
        keyboard.append(page_buttons)

        func_buttons = [
            InlineKeyboardButton("🌐 选择地区", callback_data=f"filter_country"),
            InlineKeyboardButton("🔄 刷新订阅", callback_data=f"refresh_sub")
        ]
        keyboard.append(func_buttons)

        # ---------------- try块内部try-except结构 ----------------
        full_message = header_text + (nodes_text if show_nodes else "")
        print(f"header_text: {header_text}")
        print(f"nodes_text: {nodes_text}")
        try:
            if message_to_edit:
                await message_to_edit.edit_text(full_message, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
            elif update.callback_query:
                await update.callback_query.edit_message_text(full_message, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
            else:
                await update.message.reply_text(full_message, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception as msg_err:
            prompt = "网络有点卡，稍后试试～" if "timed out" in str(msg_err).lower() else "稍后再试试吧～"
            logging.warning(f"发送消息出错：{str(msg_err)}")
            if update.callback_query:
                await update.callback_query.edit_message_text(prompt)
            else:
                await update.message.reply_text(prompt)




    # ---------------- 外层except和try配对 ----------------
    except Exception as e:
        logging.warning(f"加载页面出错: {str(e)}")
        prompt = f"⚠️ 页面加载失败：{str(e)}"
        if update.callback_query:
            await update.callback_query.edit_message_text(prompt)
        else:
            await update.message.reply_text(prompt)





# ---------------- 回调处理 --------------------
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in nodes_cache:
        await query.edit_message_text("⚠️ 请先发送订阅链接哦～")
        return

    callback_data = query.data

    if callback_data.startswith("nodepage_"):
        parts = callback_data.split("_")
        page = int(parts[1]) if len(parts) == 2 and parts[1].isdigit() else 0
        await send_nodes_page(update, context, user_id, page=page, message_to_edit=query.message)

    elif callback_data.startswith("toggle_nodes_"): 
        parts = callback_data.split("_")
        page = int(parts[2]) if len(parts) == 3 and parts[2].isdigit() else 0
        current_show = nodes_fold_status.get(user_id, False)
        new_show_status = not current_show
        nodes_fold_status[user_id] = new_show_status
        await send_nodes_page(update, context, user_id, page=page, show_nodes=new_show_status, message_to_edit=query.message)


# 地区筛选处理
    elif callback_data == "filter_country":
        keyboard = generate_country_filter_keyboard(user_id)
        await query.edit_message_text("🌐 请选择要筛选的地区：", reply_markup=keyboard)

    elif callback_data.startswith("select_country_"):
        try:
            selected_country = callback_data.split("_", 2)[2]
            user_filter_params[user_id]["country"] = selected_country
            await send_nodes_page(update, context, user_id, page=0, message_to_edit=query.message)
        except IndexError:
            await query.edit_message_text("⚠️ 地区选择失败，请重新尝试～")

    elif callback_data == "cancel_filter":
        user_filter_params[user_id]["country"] = None
        await send_nodes_page(update, context, user_id, page=0, message_to_edit=query.message)

    # 刷新订阅处理
    elif callback_data == "refresh_sub":
        await query.edit_message_text("🔄 正在刷新订阅...请稍等～")
        refresh_result = await refresh_subscription(user_id)
        if refresh_result.get("error"):
            await query.edit_message_text(f"❌ 刷新失败：{refresh_result['error']}")
        else:
            show_nodes = nodes_fold_status.get(user_id, True)
            await send_nodes_page(update, context, user_id, page=0, show_nodes=show_nodes, message_to_edit=query.message)

    else:
        await query.edit_message_text("⚠️ 未知操作，请重新尝试～")





# ---------------- 地区筛选功能（修复后可正常使用） --------------------
def generate_country_filter_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """生成地区筛选按钮"""
    if user_id not in nodes_cache:
        return InlineKeyboardMarkup([[InlineKeyboardButton("❌ 无订阅数据", callback_data="cancel_filter")]])
    
    all_countries = nodes_cache[user_id]["all_countries"]
    all_countries.sort()
    buttons = []
    for i in range(0, len(all_countries), 3):
        row = [
            InlineKeyboardButton(country, callback_data=f"select_country_{country}")
            for country in all_countries[i:i+3]
        ]
        buttons.append(row)
    buttons.append([InlineKeyboardButton("❌ 取消筛选", callback_data="cancel_filter")])
    return InlineKeyboardMarkup(buttons)





# ---------------- 命令 & 消息处理 --------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start 命令处理"""
    await update.message.reply_text(
        "👋 欢迎使用【Clash订阅工具】！\n"
        "直接发送Clash订阅链接即可查看节点信息～\n"
    )






# ========== handle_subscription函数==========
async def handle_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理订阅/节点/混发（分栏显示解析中+实时进度数字）"""
    sub_content = update.message.text.strip()
    SUBSCRIPTION_PROTOS = {"http", "https"} 
    NODE_PROTOS = {
        "ss", "vmess", "trojan", "vless", "ssr",
        "trojan-go", "wireguard", "shadowsocksr", "tuic", "hysteria"
    }  
    ALL_PROTOS = SUBSCRIPTION_PROTOS.union(NODE_PROTOS)

    # ========== 1. 提取完整==========
    node_link_pattern = re.compile(
        rf'(?:{"|".join(ALL_PROTOS)})://[A-Za-z0-9+/=_\-./?&%#]+',
        re.IGNORECASE | re.MULTILINE
    )
    all_links = node_link_pattern.findall(sub_content)
    unique_links = list(dict.fromkeys(all_links))  # 严格去重+保序

    if not unique_links:
        await update.message.reply_text(
            "❌ 没检测到任何有效内容哦～\n请发送订阅链接"
        )
        return

    # 分组：订阅组 + 节点组
    sub_links = [link for link in unique_links if link.split("://")[0].lower() in SUBSCRIPTION_PROTOS]
    node_links = [link for link in unique_links if link.split("://")[0].lower() in NODE_PROTOS]
    sub_count = len(sub_links)
    node_count = len(node_links)

    # ========== 2. 初始化分栏进度提示 ==========
    # 构造分栏显示文本，比如“订阅解析中 0/2 | 节点解析中 0/3”
    def get_progress_text(sub_done, node_done):
        sub_part = f"📥 订阅解析中 {sub_done}/{sub_count}" if sub_count > 0 else ""
        node_part = f"🔗 节点解析中 {node_done}/{node_count}" if node_count > 0 else ""
        return " | ".join(filter(None, [sub_part, node_part]))

    loading_msg = await update.message.reply_text(get_progress_text(0, 0))

    # ========== 3. 分栏解析+实时更新进度数字 ==========
    valid_nodes = []
    fail_details = []
    sub_done = 0
    node_done = 0

    # 解析订阅组
    if sub_count > 0:
        for link in sub_links:
            try:
                parse_result = parse_clash_subscription(link)
                if parse_result.get("error"):
                    fail_details.append(f"- 订阅[{link[:30]}...]：{parse_result['error']}")
                else:
                    valid_nodes.extend(parse_result["nodes"])
                sub_done += 1
                # 实时更新订阅进度数字
                await loading_msg.edit_text(get_progress_text(sub_done, node_done))
            except Exception as e:
                fail_details.append(f"- 订阅[{link[:30]}...]：未知异常：{str(e)}")
                sub_done += 1
                await loading_msg.edit_text(get_progress_text(sub_done, node_done))

    # 解析节点组
    if node_count > 0:
        for link in node_links:
            try:
                parse_result = parse_clash_subscription(link)
                if parse_result.get("error"):
                    fail_details.append(f"- 节点[{link[:30]}...]：{parse_result['error']}")
                else:
                    valid_nodes.extend(parse_result["nodes"])
                node_done += 1
                # 实时更新节点进度数字
                await loading_msg.edit_text(get_progress_text(sub_done, node_done))
            except Exception as e:
                fail_details.append(f"- 节点[{link[:30]}...]：未知异常：{str(e)}")
                node_done += 1
                await loading_msg.edit_text(get_progress_text(sub_done, node_done))

    # ========== 4. 结果处理 ==========
    if not valid_nodes:
        error_msg = "失败原因如下：\n" + "\n".join(fail_details)
        await loading_msg.edit_text(error_msg)
        return

    seen_node_keys = set()
    final_nodes = []
    for node in valid_nodes:
        node_key = f"{node['name']}_{node['protocol']}_{node['server']}_{node['port']}"
        if node_key not in seen_node_keys:
            seen_node_keys.add(node_key)
            final_nodes.append(node)


    user_id = update.effective_user.id
    sub_url = sub_links[-1] if sub_count > 0 and (sub_done - sum(1 for d in fail_details if '订阅' in d)) > 0 else "内容"
    merged_result = {
        "subscription_url": sub_url,
        "traffic_used": parse_clash_subscription(sub_url)["traffic_used"] if sub_count > 0 else "隐藏",
        "traffic_total": parse_clash_subscription(sub_url)["traffic_total"] if sub_count > 0 else "隐藏",
        "expired": parse_clash_subscription(sub_url)["expired"] if sub_count > 0 else "隐藏",
        "protocol": ",".join(list(set(n["protocol"] for n in final_nodes))),
        "total_nodes": len(final_nodes),
        "nodes": final_nodes,
        "all_countries": list(set(n["country_name"] for n in final_nodes)) if final_nodes else ["未知地区"]
    }

    nodes_cache[user_id] = merged_result
    nodes_fold_status[user_id] = False
    user_filter_params[user_id] = {"country": None}
    await send_nodes_page(update, context, user_id, page=0, message_to_edit=loading_msg)

# 分栏提示结果
    sub_success = sub_count - sum(1 for d in fail_details if '订阅' in d)
    node_success = node_count - sum(1 for d in fail_details if '节点' in d)


    # ---------------- 放进字符串里显示 ----------------
    tip_msg = f"📥 订阅：{sub_success}/{sub_count} 成功\n"
    tip_msg += f"🔗 节点：{node_success}/{node_count} 成功\n"

    if fail_details:
        tip_msg += "\n💡 失败原因：\n" + "\n".join(fail_details)

    await update.message.reply_text(tip_msg)







# ---------------- 主函数 --------------------
def main() -> None:
    defaults = Defaults(parse_mode="HTML")
    application = ApplicationBuilder().token(BOT_TOKEN).defaults(defaults).build()

    # 注册处理器
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_subscription))
    application.add_handler(CallbackQueryHandler(handle_callback))

    print("🚀 机器人启动成功了～")
    application.run_polling()


if __name__ == "__main__":
    main()