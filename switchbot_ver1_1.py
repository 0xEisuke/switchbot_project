import requests
import json
import time
import uuid
import hmac
import hashlib
import base64
from config import SWITCHBOT_API_TOKEN, SWITCHBOT_SECRET_TOKEN

# SwitchBotのAPIトークンとAPIホストの設定
API_TOKEN = SWITCHBOT_API_TOKEN
SECRET_TOKEN = SWITCHBOT_SECRET_TOKEN
API_HOST = 'https://api.switch-bot.com/v1.1'

# デバイスリスト取得用のURL
DEBICELIST_URL = f"{API_HOST}/devices"

# HMAC署名の生成
def generate_signature(api_token, secret_token):
    t = int(time.time() * 1000)
    nonce = str(uuid.uuid4())
    string_to_sign = f"{api_token}{t}{nonce}".encode('utf-8')
    secret_key = secret_token.encode('utf-8')
    signature = hmac.new(secret_key, string_to_sign, hashlib.sha256).digest()
    sign = base64.b64encode(signature).decode('utf-8').upper()
    return t, nonce, sign

# HTTP GETリクエストの関数
def _get_request(url):
    t, nonce, sign = generate_signature(API_TOKEN, SECRET_TOKEN)
    headers = {
        "Authorization": API_TOKEN,
        "Content-Type": "application/json; charset=utf8",
        "t": str(t),
        "nonce": nonce,
        "sign": sign
    }
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        data = res.json()
        if data['message'] == 'success':
            return data
        else:
            print(f"Error in response message: {data['message']}")
            print(data)
            return {}
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return {}

# HTTP POSTリクエストの関数
def _post_request(url, params):
    t, nonce, sign = generate_signature(API_TOKEN, SECRET_TOKEN)
    headers = {
        "Authorization": API_TOKEN,
        "Content-Type": "application/json; charset=utf8",
        "t": str(t),
        "nonce": nonce,
        "sign": sign
    }
    try:
        res = requests.post(url, data=json.dumps(params), headers=headers)
        res.raise_for_status()
        data = res.json()
        if data['message'] == 'success':
            return data
        else:
            print(f"Error in response message: {data['message']}")
            print(data)
            return {}
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return {}

# デバイスリストを取得する関数
def get_device_list():
    try:
        response = _get_request(DEBICELIST_URL)
        if "body" in response:
            return response["body"]
        else:
            print("Error: No 'body' in response")
            print(response)
            return None
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None

# バーチャルデバイスリストを取得する関数
def get_virtual_device_list():
    devices = get_device_list()
    if devices is None:
        print("Error: No devices found")
        return None
    return devices.get('infraredRemoteList', [])

# エアコンを操作する関数
def send_air_condition(deviceId, temperature, mode, fanspeed, power_state):
    url = f"{API_HOST}/devices/{deviceId}/commands"
    params = {
        "commandType": "command",
        "command": "setAll",
        "parameter": f"{temperature},{mode},{fanspeed},{power_state}"
    }
    res = _post_request(url, params)
    print_response(res, deviceId, "Air Conditioner")
    return res

def send_Light(deviceId, command):
    url = f"{API_HOST}/devices/{deviceId}/commands"
    params = {
        "commandType": "command",
        "command": f"{command}",
        "parameter": "default"
    }
    res = _post_request(url, params)
    print_response(res, deviceId, "Light")
    return res

def print_response(response, device_id, device_type):
    if response.get('statusCode') == 100:
        for item in response['body']['items']:
            status = item['status']
            status_message = ', '.join(f"{key}: {value}" for key, value in status.items())
            print(f"Device ID: {device_id}, Device Type: {device_type}, Status: {status_message}, Message: {item['message']}")
    else:
        print(f"Failed to execute command for Device ID: {device_id}, Device Type: {device_type}")

def air_condition_dry_on():
    data = get_virtual_device_list()
    if data is None:
        return json.dumps({
            "command": "air_condition_dry_on",
            "execution result": "Error: No virtual devices found"
        })
    
    for device in data:
        if device['remoteType'] == 'Air Conditioner':
            send_air_condition(device['deviceId'], 23, 3, 1, 'on')
            break
    command_info = {
        "command": "air_condition_dry_on",
        "execution result": "エアコンを除湿モードにしました",
    }
    return json.dumps(command_info)

def air_condition_cool_on():
    data = get_virtual_device_list()
    if data is None:
        return json.dumps({
            "command": "air_condition_cool_on",
            "execution result": "Error: No virtual devices found"
        })
    
    for device in data:
        if device['remoteType'] == 'Air Conditioner':
            send_air_condition(device['deviceId'], 23, 2, 5, 'on')
            break
    command_info = {
        "command": "air_condition_cool_on",
        "execution result": "エアコンを冷房モードにしました",
    }
    return json.dumps(command_info)

def air_condition_off():
    data = get_virtual_device_list()
    if data is None:
        return json.dumps({
            "command": "air_condition_off",
            "execution result": "Error: No virtual devices found"
        })
    
    for device in data:
        if device['remoteType'] == 'Air Conditioner':
            send_air_condition(device['deviceId'], 23, 3, 1, 'off')
            break
    command_info = {
        "command": "air_condition_off",
        "execution result": "エアコンの電源を切りました",
    }
    return json.dumps(command_info)

def Ceiling_Light_on():
    data = get_virtual_device_list()
    if data is None:
        return json.dumps({
            "command": "Ceiling_Light_on",
            "execution result": "Error: No virtual devices found"
        })
    
    for device in data:
        if device['remoteType'] == 'Light':
            send_Light(device['deviceId'], 'turnOn')
            break
    command_info = {
        "command": "Ceiling_Light_on",
        "execution result": "天井のライトの電源を点けました",
    }
    return json.dumps(command_info)

def Ceiling_Light_off():
    data = get_virtual_device_list()
    if data is None:
        return json.dumps({
            "command": "Ceiling_Light_off",
            "execution result": "Error: No virtual devices found"
        })
    
    for device in data:
        if device['remoteType'] == 'Light':
            send_Light(device['deviceId'], 'turnOff')
            break
    command_info = {
        "command": "Ceiling_Light_off",
        "execution result": "天井のライトの電源を切りました",
    }
    return json.dumps(command_info)

if __name__ == '__main__':
    Ceiling_Light_off()
    Ceiling_Light_on()
    # air_condition_off()
    # air_condition_dry_on()
    # air_condition_cool_on()
