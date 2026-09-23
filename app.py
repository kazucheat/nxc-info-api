import asyncio
import time
import httpx
import json
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64
from datetime import datetime, timedelta
from google.protobuf import json_format

# ============= =============
try:
    import FreeFire_pb2, main_pb2, AccountPersonalShow_pb2
    import GetOutfit_pb2
    print("✅ Proto files imported successfully")
except ImportError as e:
    print(f"❌ Proto import error: {e}")
    sys.exit(1)

# =============================================
# CONFIG
# =============================================

RELEASEVERSION = "OB55"
USERAGENT = "Dalvik/2.1.0 (Linux; U; Android 14; CPH2095 Build/RKQ1.211119.001)"

MAIN_KEY = b'Yg&tc%DEuh6%Zc^8'
MAIN_IV = b'6oyZDr22E3ychjM%'

# =============================================
# JWT TOKEN API
# =============================================

JWT_API_BASE = "https://jwt-wxun.vercel.app/token"   #JWT API BY NXC OFFICAL

# =============================================
# ACCOUNTS FOR JWT
# =============================================

BD_CREDS =   {
    "uid": "7910439685",
    "password": "25A89721242592D62E1E539E38D4EF95D7B3BD75B8A71BD4AEF49706BB358DE7"
  },
  {
    "uid": "7910439977",
    "password": "2E5F8C83158DD4B29E988408A2F6B5311C2416643532A1315C92D59F9EC80550"
  },
  {
    "uid": "7910440015",
    "password": "5AE2454475364A204EB462A0BBF7117F81F5BE9F165CCE1245C48C0C1D3AE46A"
  },
  {
    "uid": "7910208605",
    "password": "E160072CB0372887DC121438ADFE57CD5F5AF4A69541FC06C1EA853430C5BA49"
  },
  {
    "uid": "7910439548",
    "password": "C82924678BDE69890718C0AE32806228BB89A52C4973728D450A2E78940FECA2"
  },
  {
    "uid": "7910439591",
    "password": "D83E15EBE6E5D381579FECBFA15A35E422FCFBFD385EC56837086C4BE4AD9FFD"
  },
  {
    "uid": "7910439111",
    "password": "98BBE946F5FB2553E8D06630C20F7686511B7FD055D004CDA46A5683EB038491"
  },
  {
    "uid": "7910439774",
    "password": "8F2DA46FD6B3F05D1D5E6473CF9D62A7C7B32DC489DB9A3A5B9656897DA2958C"
  }

IND_CREDS = {
    "uid": "7910473048",
    "password": "407BA7D7F3497AE792E4D3FF58C71E653866750F984E801DCF4B032E44BC7980"
  },
  {
    "uid": "7910473012",
    "password": "AA86A98175703AADDAC97A2E466D35455A64A1FAF3B16C42FC8A6D30D75242AF"
  },
  {
    "uid": "7910473015",
    "password": "074E01D6AEE24380E2F881444291B3681426E9F739CB9F289D34898DBE2DDCFA"
  },
  {
    "uid": "7910473038",
    "password": "CBCAD69C94A6D6706E98E71B9FD31E1FCCDD357836F3F88E938B51217E0A487D"
  },
  {
    "uid": "7910473042",
    "password": "B5A4484CC06C167410250C3BB774CB413A2147C9BD283C1F1D4EA8611F0924DB"
  },
  {
    "uid": "7910473043",
    "password": "2407B093A43D870A456888E208567694E09BD95189C645999A43580D0ABEA678"
  },
  {
    "uid": "7910473033",
    "password": "24A4148A2E931FDB6EA5473CB66AA860887FD47528CF2C062BAE298B11B82295"
  },
  {
    "uid": "7910473018",
    "password": "D6B11DD67403D8B361045657DC0C9ACABE961F01720BDED7D56A6640281014CF"
  }

BR_CREDS = {
    "uid": "7910484024",
    "password": "6B7509FB9DAB367BEA388941CF68F31B343CAA46F6D6DF6CDA1C4C3814C0BC95"
  },
  {
    "uid": "7910483927",
    "password": "A845D5FACC002264DB9F30611B96C0CB3F13AADAAEEBBA9427A87BB4C0D8F62A"
  },
  {
    "uid": "7910484012",
    "password": "5D8E97C54693BEFBDC62673A1F56832A11EBD1ADFF01A47ABE8039E01D9968C1"
  },
  {
    "uid": "7910484026",
    "password": "5E3D898D42FB9E1751F913BA47A70F9DF5D9BA78B3F77EE21CAA7EA6A940B8FE"
  },
  {
    "uid": "7910473915",
    "password": "5FBA66CD55FC9B7F1371955B90E0AA0949123D503C320A0519A28A3323ADED76"
  },
  {
    "uid": "7910484000",
    "password": "165E895B36B3D7D6630DCF5395ED2E87142DFF05A5DD047DA602512ED67A34B3"
  },
  {
    "uid": "7910484020",
    "password": "59B0F15A2D03ADC7E1FC77D8A12E95F5DF6DA44799A0086C4BDF63B93CC6CC8D"
  },
  {
    "uid": "7910484025",
    "password": "BCE0301F46296F0CC9A4F0F36582EA9FF4C70FC1DB4E9ED99D1F139F49AA7422"
  },
  {
    "uid": "7910474012",
    "password": "537F36BAE9FAA6B327C19E726A081D8AA76C9B68493A69EE76DAF59BF0746632"
  },
  {
    "uid": "7910483936",
    "password": "74A83908E189B1B04DFF536D6E713B2B8490A2475AE4B761DF0DAD5CB28D6A4B"
  },
  {
    "uid": "7910484082",
    "password": "CBC6C3224E3D3803F9823A5F15CDD4D4E9B9A88295A690766ACFCD09C6091678"
  },
  {
    "uid": "7910484352",
    "password": "E5475B05BC90DB687FBEECB5B7957F8DEF389DCD85DE4FE9BCA8F559F44DB7A3"
  }

ACCOUNT_CREDENTIALS = {
    "BD": BD_CREDS,
    "IND": IND_CREDS,
    "BR": BR_CREDS
}

# =============================================
# 🌍
# =============================================

REGION_CONFIG = {
    "BD": {"server_url": "https://clientbp.ppmainecoonghj.com", "release_version": "OB55"},
    "IND": {"server_url": "https://client.ind.freefiremobile.com", "release_version": "OB55"},
    "BR": {"server_url": "https://client.us.freefiremobile.com", "release_version": "OB55"}
}

LOGIN_URLS = {
    "BD": "https://loginbp.ppmainecoonghj.com",
    "IND": "https://loginbp.ppmainecoonghj.com",
    "BR": "https://loginbp.ppmainecoonghj.com"
}


REGION_PRIORITY = ["BD", "IND", "BR"]

# === Flask App ===
app = Flask(__name__)
CORS(app)

# =============================================
# In-Memory Token Cache (per container)
# =============================================

_token_cache = {}

# =============================================
# JWT Token Function
# =============================================

async def get_jwt_token_from_api(region: str):
    cred = ACCOUNT_CREDENTIALS.get(region)
    if not cred:
        return None

    url = f"{JWT_API_BASE}?uid={cred['uid']}&password={cred['password']}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code != 200:
                print(f"⚠️ [{region}] JWT API returned {response.status_code}: {response.text[:120]}")
                return None

            data = response.json()
            token = data.get("token")
            if not token:
                print(f"⚠️ [{region}] JWT API returned no token: {data}")
                return None

            api_region = data.get("region", region)
            server_url = REGION_CONFIG.get(api_region, REGION_CONFIG["BD"])["server_url"]

            return {
                "token": f"Bearer {token}",
                "region": api_region,
                "server_url": server_url,
                "expires_at": time.time() + 25200
            }
    except Exception as e:
        print(f"❌ JWT API exception for {region}: {e}")
        return None

# =============================================
# Token Getter (with cache)
# =============================================

async def get_token(region: str):
    cached = _token_cache.get(region)
    if cached and cached.get('expires_at', 0) > time.time():
        return cached

    token_info = await get_jwt_token_from_api(region)

    if not token_info:
        token_info = await generate_token_backup(region)

    if token_info:
        _token_cache[region] = token_info
        return token_info

    print(f"❌ [{region}] Unable to acquire bot token. Account may be banned or API unreachable.")
    return None

async def generate_token_backup(region: str):
    try:
        cred = ACCOUNT_CREDENTIALS.get(region, ACCOUNT_CREDENTIALS["BD"])
        account = f"uid={cred['uid']}&password={cred['password']}"

        token_val, open_id = await get_access_token(account)
        if not token_val or not open_id:
            return None

        body = json.dumps({
            "open_id": open_id,
            "open_id_type": "4",
            "login_token": token_val,
            "orign_platform_type": "4"
        })
        proto_bytes = await json_to_proto(body, FreeFire_pb2.LoginReq())
        payload = aes_cbc_encrypt(MAIN_KEY, MAIN_IV, proto_bytes)

        config = REGION_CONFIG.get(region, REGION_CONFIG["BD"])
        login_url = LOGIN_URLS.get(region, LOGIN_URLS["BD"])
        url = f"{login_url}/MajorLogin"

        headers = {
            'User-Agent': USERAGENT,
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/octet-stream",
            'X-Unity-Version': "2018.4.11f1",
            'X-GA': "v1 1",
            'ReleaseVersion': config['release_version']
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, data=payload, headers=headers)
            if resp.status_code != 200:
                print(f"❌ Backup MajorLogin failed for {region}: {resp.status_code}")
                return None

            if b"Exploiting loopholes" in resp.content:
                print(f"🚨 [{region}] Bot account (UID: {cred['uid']}) is BANNED by Garena (Reason: Exploiting loopholes)!")
                return None
            if b"Modifiers" in resp.content:
                print(f"🚨 [{region}] Bot account (UID: {cred['uid']}) is BANNED by Garena (Reason: Modifiers)!")
                return None

            try:
                login_res = FreeFire_pb2.LoginRes()
                login_res.ParseFromString(resp.content)
                msg_json = json_format.MessageToJson(login_res)
                msg = json.loads(msg_json)
                if not msg.get("token"):
                    print(f"⚠️ [{region}] MajorLogin returned no token for UID {cred['uid']}")
                    return None
            except Exception as parse_err:
                print(f"⚠️ [{region}] MajorLogin parse error: {parse_err}")
                return None

            return {
                'token': f"Bearer {msg.get('token','0')}",
                'region': msg.get('lockRegion','0'),
                'server_url': msg.get('serverUrl','0'),
                'expires_at': time.time() + 25200
            }
    except Exception as e:
        print(f"❌ Backup token error for {region}: {e}")
        return None

# === Helper Functions ===
def pad(text: bytes) -> bytes:
    padding_length = AES.block_size - (len(text) % AES.block_size)
    return text + bytes([padding_length] * padding_length)

def aes_cbc_encrypt(key: bytes, iv: bytes, plaintext: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(plaintext))

async def json_to_proto(json_data: str, proto_message) -> bytes:
    json_format.ParseDict(json.loads(json_data), proto_message)
    return proto_message.SerializeToString()

async def get_access_token(account: str):
    url = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant"
    payload = account + "&response_type=token&client_type=2&client_secret=2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3&client_id=100067"
    headers = {'User-Agent': USERAGENT, 'Content-Type': "application/x-www-form-urlencoded"}

    for attempt in range(2):
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.post(url, data=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("access_token"), data.get("open_id")
                await asyncio.sleep(1)
        except:
            await asyncio.sleep(1)
    return None, None

async def GetAccountInformation(uid, region):
    try:
        token_info = await get_token(region)
        if not token_info:
            return {"success": False, "error_type": "NO_TOKEN", "region": region}

        actual_region = token_info.get('region', region)
        token = token_info['token']
        server_url = token_info['server_url']
        config = REGION_CONFIG.get(actual_region, REGION_CONFIG["BD"])

        payload = await json_to_proto(json.dumps({'a': uid, 'b': 7}), main_pb2.GetPlayerPersonalShow())
        data_enc = aes_cbc_encrypt(MAIN_KEY, MAIN_IV, payload)

        headers = {
            'User-Agent': USERAGENT,
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/octet-stream",
            'Authorization': token,
            'X-Unity-Version': "2018.4.11f1",
            'X-GA': "v1 1",
            'ReleaseVersion': config['release_version']
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(server_url + '/GetPlayerPersonalShow', data=data_enc, headers=headers)

            if resp.status_code != 200:
                print(f"⚠️ [{actual_region}] GetPlayerPersonalShow returned {resp.status_code} for UID {uid}")
                if resp.status_code in (401, 429):
                    _token_cache.pop(region, None)
                err_type = "RATE_LIMITED" if resp.status_code == 429 else "NOT_FOUND"
                return {"success": False, "error_type": err_type, "region": actual_region, "status_code": resp.status_code}

            account_info = AccountPersonalShow_pb2.AccountPersonalShowInfo()
            account_info.ParseFromString(resp.content)
            result = json.loads(json_format.MessageToJson(account_info))

            is_banned = result.get("isBanned", False)
            if isinstance(is_banned, bool):
                result["ban_status"] = "🔴 BANNED" if is_banned else "🟢 UNBANNED"
            else:
                result["ban_status"] = "❓ UNKNOWN"

            result["region"] = actual_region
            return {"success": True, "data": result}

    except Exception as e:
        print(f"❌ Error in GetAccountInformation for {region}: {e}")
        return {"success": False, "error_type": "EXCEPTION", "region": region, "error": str(e)}

# =============================================
# HELPER
# =============================================

def get_item_name(item_id):
    if not item_id or item_id == "0" or item_id == 0:
        return "N/A"
    try:
        import requests
        response = requests.get(f"https://api.danger.workers.dev/item/{item_id}", timeout=3)
        if response.status_code == 200:
            data = response.json()
            return data.get("name", str(item_id))
        return str(item_id)
    except:
        return str(item_id)

def get_rank_name(rp):
    try:
        rp = int(rp)
    except:
        return "N/A"
    if rp == 0: return "Bronze I"
    if rp < 100: return "Bronze II"
    if rp < 200: return "Bronze III"
    if rp < 300: return "Silver I"
    if rp < 400: return "Silver II"
    if rp < 500: return "Silver III"
    if rp < 600: return "Gold I"
    if rp < 700: return "Gold II"
    if rp < 800: return "Gold III"
    if rp < 900: return "Platinum I"
    if rp < 1000: return "Platinum II"
    if rp < 1100: return "Platinum III"
    if rp < 1200: return "Diamond I"
    if rp < 1300: return "Diamond II"
    if rp < 1400: return "Diamond III"
    if rp < 1500: return "Heroic"
    if rp < 2000: return "Master"
    return "Grandmaster"

def ts_to_bst(ts):
    try:
        dt = datetime.fromtimestamp(int(ts)) + timedelta(hours=6)
        return dt.strftime("%d %b %Y at %I:%M:%S %p") + " (BST)"
    except:
        return "N/A"

# =============================================
# MAIN API
# =============================================

@app.route('/info')
def get_full_info():
    uid = request.args.get('uid')
    requested_region = (request.args.get('region') or request.args.get('server') or '').strip().upper()

    if not uid:
        return jsonify({"error": "UID required"}), 400

    try:
        uid_int = int(uid)
    except:
        return jsonify({"error": "Invalid UID"}), 400

    regions_to_try = list(REGION_PRIORITY)
    if requested_region in regions_to_try:
        regions_to_try.remove(requested_region)
        regions_to_try.insert(0, requested_region)

    async def try_all_regions_parallel():
        """BD, IND, BR — Parallel with priority fallback."""
        tasks = []
        for region in regions_to_try:
            tasks.append(asyncio.create_task(GetAccountInformation(uid_int, region)))
        
        errors = []
        try:
            for coro in asyncio.as_completed(tasks, timeout=20):
                try:
                    res = await coro
                    if res and res.get("success"):
                        for t in tasks:
                            if not t.done():
                                t.cancel()
                        return res.get("data"), None
                    elif res:
                        errors.append(res)
                except Exception as ex:
                    errors.append({"error_type": "EXCEPTION", "error": str(ex)})
        except asyncio.TimeoutError:
            pass
        
        for t in tasks:
            if not t.done():
                t.cancel()
        return None, errors

    try:
        account_data, errors = asyncio.run(try_all_regions_parallel())
    except Exception as e:
        print(f"❌ Global error: {e}")
        account_data, errors = None, [{"error_type": "GLOBAL", "error": str(e)}]

    if not account_data:
        if errors and all(e.get("error_type") == "NO_TOKEN" for e in errors):
            return jsonify({
                "status": "error",
                "error": "Bot accounts unavailable or banned",
                "message": "All bot accounts failed to authenticate with Garena. Please check server console or update guest credentials in app.py."
            }), 503
        if errors and all(e.get("error_type") == "RATE_LIMITED" for e in errors):
            return jsonify({
                "status": "error",
                "error": "Rate limited by Garena",
                "message": "All bot accounts are currently rate limited by Garena (429). Please wait for cooldown or add more accounts."
            }), 429
        return jsonify({"error": "Player not found"}), 404

    used_region = account_data.get("region", "Unknown")

    basic = account_data.get("basicInfo", {})
    clan = account_data.get("clanBasicInfo", {})
    social = account_data.get("socialInfo", {})
    pet = account_data.get("petInfo", {})
    captain = account_data.get("captainBasicInfo", {})
    credit = account_data.get("creditScoreInfo", {})

    prime_level = "N/A"
    try:
        prime_data = basic.get("primeLevel")
        if isinstance(prime_data, dict):
            prime_level = prime_data.get("level", "N/A")
        elif prime_data is not None:
            prime_level = str(prime_data)
    except:
        prime_level = "N/A"

    response = {
        "owner": "@kuchupuchu04",
        "credit": "@kuchupuchu04",
        "status": "success",
        "server_used": used_region,
        "BanStatus": account_data.get("ban_status", "❓ UNKNOWN"),
        "BasicInformation": {
            "PrimeLevel": prime_level,
            "Name": basic.get("nickname", "N/A"),
            "UID": uid,
            "Level": basic.get("level", "N/A"),
            "Exp": basic.get("exp", "N/A"),
            "Region": basic.get("region", "N/A"),
            "Likes": basic.get("liked", "N/A"),
            "HonorScore": credit.get("creditScore", "N/A"),
            "CelebrityStatus": "Yes" if basic.get("showBrRank") else "No",
            "Title": get_item_name(basic.get("title", "0")),
            "Signature": social.get("signature", "N/A")
        },
        "ActivityInformation": {
            "MostRecentOB": basic.get("releaseVersion", "N/A"),
            "BooyahPass": "Yes" if basic.get("hasElitePass") else "No",
            "CurrentBpBadges": basic.get("badgeCnt", "N/A"),
            "BRRank": get_rank_name(basic.get("rankingPoints", 0)),
            "BRPoints": basic.get("rankingPoints", 0),
            "ShowBRRank": "True" if basic.get("showBrRank") else "False",
            "ShowCSRank": "True" if basic.get("showCsRank") else "False",
            "CreatedAt": ts_to_bst(basic.get("createAt", 0)),
            "LastLogin": ts_to_bst(basic.get("lastLoginAt", 0))
        },
        "GuildInformation": {
            "GuildName": clan.get("clanName", "No Guild"),
            "GuildID": clan.get("clanId", "N/A"),
            "GuildLevel": clan.get("clanLevel", "N/A"),
            "LiveMembers": clan.get("memberNum", "N/A"),
            "MaxMembers": clan.get("capacity", "N/A")
        },
        "PetDetails": {
            "Equipped": "Yes" if pet.get("isSelected") else "No",
            "PetNick": pet.get("name", "N/A"),
            "PetType": get_item_name(pet.get("id", "0")),
            "PetSkill": get_item_name(pet.get("selectedSkillId", "0")),
            "PetSkin": get_item_name(pet.get("skinId", "0")),
            "PetExp": pet.get("exp", "N/A"),
            "PetLevel": pet.get("level", "N/A")
        },
        "LeaderInformation": {
            "Name": captain.get("nickname", "N/A"),
            "UID": captain.get("accountId", "N/A"),
            "Level": captain.get("level", "N/A"),
            "Region": captain.get("region", "N/A"),
            "BooyahPass": "Yes" if captain.get("hasElitePass") else "No",
            "CreatedAt": ts_to_bst(captain.get("createAt", 0)),
            "LastLogin": ts_to_bst(captain.get("lastLoginAt", 0)),
            "MostRecentOB": captain.get("releaseVersion", "N/A"),
            "Title": get_item_name(captain.get("title", "0")),
            "BpBadges": captain.get("badgeCnt", "N/A"),
            "BRRank": get_rank_name(captain.get("rankingPoints", 0)),
            "BRPoints": captain.get("rankingPoints", 0)
        }
    }

    return jsonify(response)

@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "version": "OB55",
        "endpoint": "/info?uid=UID",
        "example": "/info?uid=13921432690",
        "priority": "BD → IND → BR",
        "credit": "TG-- @kuchupuchu04 || DC-- @nxc_official"
    })

@app.route('/status')
def token_status():
    status = {}
    for region, info in _token_cache.items():
        expires_in = info['expires_at'] - time.time()
        status[region] = {"has_token": True, "expires_in": f"{expires_in/3600:.1f} hours"}
    return jsonify({"total_tokens": len(_token_cache), "tokens": status})

# =============================================
# Local dev entry point
# =============================================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=False)
