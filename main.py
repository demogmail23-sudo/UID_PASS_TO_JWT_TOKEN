from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import binascii
import my_pb2
import output_pb2
import json
import base64
import warnings
from urllib3.exceptions import InsecureRequestWarning

warnings.filterwarnings("ignore", category=InsecureRequestWarning)

app = Flask(__name__)
CORS(app)

# ========== CONFIG ==========
AES_KEY = b'Yg&tc%DEuh6%Zc^8'
AES_IV = b'6oyZDr22E3ychjM%'

OAUTH_URL = "https://100067.connect.garena.com/oauth/guest/token/grant"
MAJOR_LOGIN_URL = "https://loginbp.ggpolarbear.com/MajorLogin"

# ========== ENCRYPTION ==========
def encrypt_message(key, iv, plaintext):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_message = pad(plaintext, AES.block_size)
    return cipher.encrypt(padded_message)

# ========== 1. GET ACCESS TOKEN ==========
def get_access_token(uid, password):
    payload = {
        'uid': uid,
        'password': password,
        'response_type': "token",
        'client_type': "2",
        'client_secret': "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        'client_id': "100067"
    }
    headers = {'User-Agent': "GarenaMSDK/4.0.19P9(SM-M526B ;Android 13;pt;BR;)"}
    
    resp = requests.post(OAUTH_URL, data=payload, headers=headers, timeout=10, verify=False)
    data = resp.json()
    
    if 'access_token' in data:
        return data['access_token'], data.get('open_id')
    return None, None

# ========== 2. GET JWT TOKEN + FULL RESPONSE ==========
def get_jwt_with_info(access_token, open_id, uid):
    game_data = my_pb2.GameData()
    game_data.timestamp = "2025-05-29 13:11:47"
    game_data.game_name = "free fire"
    game_data.game_version = 1
    game_data.version_code = "1.118.1"
    game_data.os_info = "Android OS 11 / API-30"
    game_data.device_type = "Handheld"
    game_data.network_provider = "JIO"
    game_data.connection_type = "MOBILE"
    game_data.screen_width = 720
    game_data.screen_height = 1600
    game_data.dpi = "280"
    game_data.cpu_info = "ARM Cortex-A73 | 2200 | 4"
    game_data.total_ram = 4096
    game_data.gpu_name = "Adreno (TM) 610"
    game_data.gpu_version = "OpenGL ES 3.2"
    game_data.user_id = uid
    game_data.ip_address = "182.75.115.22"
    game_data.language = "en"
    game_data.open_id = open_id
    game_data.access_token = access_token
    game_data.platform_type = 4
    game_data.device_form_factor = "Handheld"
    game_data.device_model = "realme RMX1825"
    game_data.field_60 = 30000
    game_data.field_61 = 27500
    game_data.field_62 = 1940
    game_data.field_63 = 720
    game_data.field_64 = 28000
    game_data.field_65 = 30000
    game_data.field_66 = 28000
    game_data.field_67 = 30000
    game_data.field_70 = 4
    game_data.field_73 = 2
    game_data.library_path = "/data/app/com.dts.freefireth-XaT5M7jRwEL-nPaKOQvqdg==/lib/arm"
    game_data.field_76 = 1
    game_data.apk_info = "2f4a7f349f3a3ea581fc4d803bc5a977|/data/app/com.dts.freefireth-XaT5M7jRwEL-nPaKOQvqdg==/base.apk"
    game_data.field_78 = 6
    game_data.field_79 = 1
    game_data.os_architecture = "64"
    game_data.build_number = "2022041388"
    game_data.field_85 = 1
    game_data.graphics_backend = "OpenGLES3"
    game_data.max_texture_units = 16383
    game_data.rendering_api = 4
    game_data.encoded_field_89 = "\x10U\x15\x03\x02\t\rPYN\tEX\x03AZO9X\x07\rU\niZPVj\x05\rm\t\x04c"
    game_data.field_92 = 8999
    game_data.marketplace = "3rd_party"
    game_data.encryption_key = "Jp2DT7F3Is55K/92LSJ4PWkJxZnMzSNn+HEBK2AFBDBdrLpWTA3bZjtbU3JbXigkIFFJ5ZJKi0fpnlJCPDD2A7h2aPQ="
    game_data.total_storage = 64000
    game_data.field_97 = 1
    game_data.field_98 = 1
    game_data.field_99 = "4"
    game_data.field_100 = b"4"

    serialized = game_data.SerializeToString()
    encrypted = encrypt_message(AES_KEY, AES_IV, serialized)
    hex_encrypted = binascii.hexlify(encrypted).decode('utf-8')

    headers = {
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; ASUS_Z01QD Build/PI)",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/octet-stream",
        'X-Unity-Version': "2018.4.11f1",
        'X-GA': "v1 1",
        'ReleaseVersion': "OB53"
    }
    
    edata = bytes.fromhex(hex_encrypted)
    resp = requests.post(MAJOR_LOGIN_URL, data=edata, headers=headers, timeout=10, verify=False)
    
    if resp.status_code == 200:
        msg = output_pb2.Lokesh()
        msg.ParseFromString(resp.content)
        
        # Extract all info from protobuf response
        result = {
            "token": getattr(msg, "token", None),
            "account_id": getattr(msg, "account_id", None),
            "region": getattr(msg, "region", None),
            "status": getattr(msg, "status", None),
            "name": getattr(msg, "name", None),
            "place": getattr(msg, "place", None),
            "location": getattr(msg, "location", None),
            "city": getattr(msg, "city", None),
            "area": getattr(msg, "area", None),
            "main_area": getattr(msg, "main_area", None)
        }
        return result
    return None

# ========== API ENDPOINTS ==========

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "name": "FF Token Generator API",
        "version": "3.0",
        "endpoints": {
            "/api/token?uid=XXX&pass=XXX": "Get tokens + player info from UID/Password",
            "/api/token?access_token=XXX": "Get JWT from existing access_token"
        },
        "credit": "@ZAINUBHAIFF | @ZAINUBHAIFF"
    })

@app.route('/api/token', methods=['GET', 'POST'])
def get_tokens():
    # GET or POST se parameters lo
    if request.method == 'GET':
        uid = request.args.get('uid')
        password = request.args.get('pass') or request.args.get('password')
        access_token = request.args.get('access_token')
    else:
        data = request.get_json() or request.form
        uid = data.get('uid')
        password = data.get('pass') or data.get('password')
        access_token = data.get('access_token')
    
    # Case 1: Access token se JWT generate
    if access_token:
        inspect_url = f"https://100067.connect.garena.com/oauth/token/inspect?token={access_token}"
        insp_resp = requests.get(inspect_url, verify=False)
        if insp_resp.status_code == 200:
            insp_data = insp_resp.json()
            open_id = insp_data.get('open_id')
            uid_from_token = str(insp_data.get('uid'))
            
            result = get_jwt_with_info(access_token, open_id, uid_from_token)
            if result and result.get('token'):
                return jsonify({
                    "success": True,
                    "credit": "@ZAINUBHAIFF",
                    "tokens": {
                        "access_token": access_token,
                        "jwt_token": result.get('token')
                    },
                    "player_info": {
                        "account_id": str(result.get('account_id')),
                        "name": result.get('name'),
                        "region": result.get('region'),
                        "status": result.get('status'),
                        "place": result.get('place'),
                        "location": result.get('location'),
                        "city": result.get('city'),
                        "area": result.get('area')
                    }
                })
        return jsonify({"success": False, "error": "Invalid or expired access_token"}), 401
    
    # Case 2: UID/Password se tokens
    elif uid and password:
        access_token, open_id = get_access_token(uid, password)
        
        if not access_token:
            return jsonify({"success": False, "error": "Invalid UID or Password"}), 401
        
        result = get_jwt_with_info(access_token, open_id, uid)
        
        if result and result.get('token'):
            return jsonify({
                "success": True,
                "credit": "@ZAINUBHAIFF",
                "tokens": {
                    "access_token": access_token,
                    "jwt_token": result.get('token'),
                    "open_id": open_id
                },
                "player_info": {
                    "account_id": str(result.get('account_id')),
                    "name": result.get('name'),
                    "region": result.get('region'),
                    "status": result.get('status'),
                    "place": result.get('place'),
                    "location": result.get('location'),
                    "city": result.get('city'),
                    "area": result.get('area'),
                    "main_area": result.get('main_area')
                }
            })
        else:
            return jsonify({"success": False, "error": "Failed to generate JWT"}), 500
    
    else:
        return jsonify({
            "success": False,
            "error": "Provide either (uid + pass) OR access_token",
            "example": {
                "get": "/api/token?uid=123456&pass=password",
                "post": '{"uid": "123456", "pass": "password"}'
            }
        }), 400

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "credit": "@ZAINUBHAIFF"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5030, debug=True)