import requests
import json
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# ========== PROTO FILES IMPORT (Tere paas already hain) ==========
import my_pb2
import output_pb2

app = Flask(__name__)
CORS(app)

# ========== CONFIG ==========
KEY = b'Yg&tc%DEuh6%Zc^8'
IV = b'6oyZDr22E3ychjM%'

OAUTH_URL = "https://100067.connect.garena.com/oauth/guest/token/grant"
MAJOR_LOGIN_URL = "https://loginbp.ggblueshark.com/MajorLogin"

# ========== ENCRYPTION ==========
def encrypt_aes(data_bytes):
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    padded = pad(data_bytes, AES.block_size)
    return cipher.encrypt(padded)

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

# ========== 2. GET JWT TOKEN (Major Login) ==========
def get_jwt_token(access_token, open_id):
    headers = {
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "Content-Type": "application/octet-stream",
        "X-Unity-Version": "2018.4.11f1",
        "X-GA": "v1 1",
        "ReleaseVersion": "OB53"
    }
    
    platforms = [8, 3, 4, 6]
    
    for platform_type in platforms:
        try:
            game_data = my_pb2.GameData()
            game_data.timestamp = "2024-12-05 18:15:32"
            game_data.game_name = "free fire"
            game_data.game_version = 1
            game_data.version_code = "1.108.3"
            game_data.os_info = "Android OS 9 / API-28"
            game_data.device_type = "Handheld"
            game_data.network_provider = "Verizon Wireless"
            game_data.connection_type = "WIFI"
            game_data.screen_width = 1280
            game_data.screen_height = 960
            game_data.dpi = "240"
            game_data.cpu_info = "ARMv7 VFPv3 NEON VMH | 2400 | 4"
            game_data.total_ram = 5951
            game_data.gpu_name = "Adreno (TM) 640"
            game_data.gpu_version = "OpenGL ES 3.0"
            game_data.user_id = "Google|74b585a9-0268-4ad3-8f36-ef41d2e53610"
            game_data.ip_address = "172.190.111.97"
            game_data.language = "en"
            game_data.open_id = open_id
            game_data.access_token = access_token
            game_data.platform_type = platform_type
            game_data.field_99 = str(platform_type)
            game_data.field_100 = str(platform_type)
            
            encrypted = encrypt_aes(game_data.SerializeToString())
            resp = requests.post(MAJOR_LOGIN_URL, data=encrypted, headers=headers, timeout=10, verify=False)
            
            if resp.status_code == 200:
                msg = output_pb2.Garena_420()
                msg.ParseFromString(resp.content)
                token = getattr(msg, "token", None)
                if token:
                    return token
        except Exception as e:
            continue
    
    return None

# ========== 3. DECODE JWT (Get User Info) ==========
def decode_jwt(token):
    try:
        payload = token.split('.')[1]
        payload += '=' * (-len(payload) % 4)
        data = json.loads(base64.urlsafe_b64decode(payload))
        return data.get('account_id'), data.get('nickname'), data.get('lock_region')
    except:
        return None, None, None

# ========== 4. API ENDPOINTS ==========

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "active",
        "name": "Free Fire Token Generator API",
        "version": "2.0.0",
        "endpoints": {
            "GET": {
                "url": "/api/token?uid=UID&pass=PASSWORD",
                "description": "Get access_token and jwt_token"
            },
            "POST": {
                "url": "/api/token",
                "body": '{"uid": "123456", "pass": "password"}',
                "description": "Get tokens using JSON"
            }
        },
        "credit": "@spideyabd | @zainu"
    })

@app.route('/api/token', methods=['GET', 'POST', 'OPTIONS'])
def get_tokens():
    # Handle CORS
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    # Get credentials
    if request.method == 'GET':
        uid = request.args.get('uid')
        password = request.args.get('pass')
        password = password or request.args.get('password')
    else:
        if request.is_json:
            data = request.get_json()
            uid = data.get('uid')
            password = data.get('pass') or data.get('password')
        else:
            uid = request.form.get('uid')
            password = request.form.get('pass')
    
    # Validate
    if not uid or not password:
        return jsonify({
            "success": False,
            "error": "UID and Password required",
            "example": {
                "GET": "/api/token?uid=123456&pass=yourpassword",
                "POST": '{"uid": "123456", "pass": "yourpassword"}'
            }
        }), 400
    
    # Step 1: Get Access Token
    access_token, open_id = get_access_token(uid, password)
    
    if not access_token:
        return jsonify({
            "success": False,
            "error": "Invalid UID or Password. Please check your credentials."
        }), 401
    
    # Step 2: Get JWT Token
    jwt_token = get_jwt_token(access_token, open_id)
    
    # Step 3: Decode info if JWT available
    uid_from_jwt = None
    name = None
    region = None
    
    if jwt_token:
        uid_from_jwt, name, region = decode_jwt(jwt_token)
    
    response_data = {
        "success": True,
        "credit": "@spideyabd",
        "developer": "@zainu",
        "tokens": {
            "access_token": access_token,
            "jwt_token": jwt_token,
            "open_id": open_id
        },
        "player_info": {
            "uid": uid_from_jwt or uid,
            "name": name,
            "region": region
        }
    }
    
    return jsonify(response_data), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": "2026-05-11"
    }), 200

# ========== RUN ==========
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
