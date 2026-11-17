import time
import hashlib
import json
import random
import requests
from flask import Flask, render_template_string, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

bot_state = {
    "is_running": False,
    "token": "",
    "game_type_id": 30,
    "base_amount": 10,
    "custom_bet_counts": [1, 10, 100, 1000, 10000, 100000],
    "win_count": 0,
    "loss_count": 0,
    "net_pl": 0,
    "numbers": [],
    "last_prediction": "",
    "processed_periods": set(),
    "last_betted_issue": "",
    "real_bet_issues": set(),
    "can_place_bet": True,
    "logs": []
}

def log_message(msg, type_cls=""):
    timestamp = time.strftime("%H:%M:%S")
    entry = {"time": timestamp, "msg": msg, "type": type_cls}
    bot_state["logs"].insert(0, entry)
    if len(bot_state["logs"]) > 100:
        bot_state["logs"].pop()

def calculate_dynamic_signature(payload_obj):
    t = payload_obj.copy()
    t.pop('signature', None)
    t.pop('timestamp', None)
    t.pop('track', None)
    t.pop('xosoBettingData', None)
    sorted_obj = {}
    for r in sorted(t.keys()):
        o = t[r]
        if o is not None and o != "":
            sorted_obj[r] = 0 if o == 0 else o
    json_str = json.dumps(sorted_obj, separators=(',', ':'))
    md5_hash = hashlib.md5(json_str.encode('utf-8')).hexdigest().upper()
    return md5_hash[:32]

def generate_random_hex():
    return ''.join(random.choice('0123456789abcdef') for _ in range(32))

def get_current_bet_count():
    levels = bot_state["custom_bet_counts"]
    idx = min(bot_state["win_count"] + bot_state["loss_count"], len(levels) - 1)
    return levels[idx]

def get_bs(n):
    return "S" if n <= 4 else "B"

def analyze_pattern():
    numbers = bot_state["numbers"]
    if len(numbers) < 3:
        return ""
    recent_bs = [get_bs(n) for n in numbers]
    full_str = "".join(recent_bs)
    if full_str.endswith("SBS"):
        return "BIG"
    elif full_str.endswith("BSB"):
        return "SMALL"
    else:
        last_bs = recent_bs[-1]
        return "SMALL" if last_bs == "S" else "BIG"

def background_bot_loop():
    if not bot_state["is_running"] or not bot_state["token"]:
        return
    try:
        timestamp_val = int(time.time())
        random_val = generate_random_hex()
        live_payload = {
            "pageSize": 10, "pageNo": 1, "typeId": bot_state["game_type_id"],
            "language": 7, "random": random_val, "timestamp": timestamp_val
        }
        live_payload["signature"] = calculate_dynamic_signature(live_payload)
        headers = {
            "Content-Type": "application/json;charset=UTF-8",
            "authorization": "Bearer " + bot_state["token"],
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "x-app-type": "PWA", "ar-origin": "https://cklottery.cc",
            "origin": "https://cklottery.cc", "referer": "https://cklottery.cc/"
        }
        res = requests.post("https://ckygjf6r.com/api/webapi/GetNoaverageEmerdList", json=live_payload, headers=headers, timeout=10)
        data = res.json()
        if data and data.get("code") == 0 and data.get("data"):
            lst = data["data"].get("list") or data["data"].get("data") or data["data"]
            if isinstance(lst, list) and len(lst) > 0:
                latest = lst[0]
                issue_num = str(latest.get("issueNumber") or latest.get("issuenumber"))
                num = int(latest.get("number"))
                if issue_num and issue_num not in bot_state["processed_periods"]:
                    bot_state["processed_periods"].add(issue_num)
                    bot_state["numbers"].append(num)
                    if len(bot_state["numbers"]) > 20:
                        bot_state["numbers"].pop(0)
                next_pred = analyze_pattern()
                bot_state["last_prediction"] = next_pred
    except Exception as e:
        print("Worker error:", str(e))

scheduler = BackgroundScheduler()
scheduler.add_job(func=background_bot_loop, trigger="interval", seconds=5)
scheduler.start()

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔥 WinGo Fully Automatic Bot</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: Arial, sans-serif; }
        body { background: #020617; color: #fff; text-align: center; padding: 15px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .container { width: 100%; max-width: 400px; }
        .card { background: #1e1e1e; padding: 15px; margin: 10px auto; border-radius: 8px; text-align: left; box-shadow: 0 2px 4px rgba(0,0,0,0.5); }
        .primary-btn { width: 100%; padding: 14px; background: linear-gradient(to right, #f3cf8c, #c99b46); border: none; border-radius: 8px; color: #1a0f0f; font-weight: bold; font-size: 15px; cursor: pointer; margin-top: 10px; }
        .stop-btn { background: linear-gradient(to right, #e74c3c, #c0392b); color: #fff; }
        .input-group { margin-bottom: 10px; }
        .input-group label { display: block; font-size: 12px; color: #c9a973; margin-bottom: 4px; }
        .input-group input { width: 100%; padding: 10px; background-color: #0f0707; border: 1px solid #573333; border-radius: 6px; color: #fff; font-size: 13px; outline: none; }
        #historyBox { max-height: 140px; overflow-y: auto; background: #111; padding: 10px; margin-top: 15px; border-radius: 10px; text-align: left; font-size: 12px; }
        .win { color: #00ff88; margin-bottom: 4px; }
        .loss { color: #ff3b3b; margin-bottom: 4px; }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/crypto-js/4.1.1/crypto-js.min.js"></script>
</head>
<body>
    <div id="login-screen" class="container" style="display: {% if logged_in %}none{% else %}block{% endif %};">
        <div class="card">
            <h3>📱 Enter Account Credentials</h3>
            <div class="input-group">
                <label>Phone Number</label>
                <input type="text" id="phone-input" placeholder="e.g. 959780000003">
            </div>
            <div class="input-group">
                <label>Password</label>
                <input type="password" id="password-input" placeholder="Enter your password">
            </div>
            <button id="login-btn" class="primary-btn">🔓 Login & Connect</button>
            <div id="login-error" style="color: #ff3b3b; font-size: 12px; margin-top: 8px; text-align: center;"></div>
        </div>
    </div>

    <div id="dashboard-screen" class="container" style="display: {% if logged_in %}block{% else %}none{% endif %};">
        <div class="card">
            <h3>🤖 CLOUD SMART BOT</h3>
            <button id="bot-toggle-btn" class="primary-btn {% if is_running %}stop-btn{% else %}{% endif %}" onclick="toggleBot()">
                {% if is_running %}⏹ Stop Cloud Bot{% else %}🚀 Start Cloud Bot{% endif %}
            </button>
            <button onclick="logoutSession()" style="width:100%; margin-top:8px; background:none; border:none; color:#c9a973; font-size:11px; text-decoration:underline; cursor:pointer;">🚪 Logout</button>
        </div>
        <h3 style="font-size: 13px; color: #c9a973; margin-top: 15px; text-align: left;">📜 Cloud Live Logs</h3>
        <div id="historyBox">
            {% for log in logs %}
                <div class="{{ log.type }}">[{{ log.time }}] {{ log.msg }}</div>
            {% endfor %}
        </div>
    </div>

    <script>
        function calculateDynamicSignature(payloadObj) {
            let t = { ...payloadObj };
            delete t.signature; delete t.timestamp; delete t.track; delete t.xosoBettingData;
            const sortedObj = {};
            Object.keys(t).sort().forEach(r => {
                const o = t[r];
                if (o !== null && o !== "" && o !== undefined) sortedObj[r] = (o === 0) ? 0 : o;
            });
            return CryptoJS.MD5(JSON.stringify(sortedObj)).toString().toUpperCase().slice(0, 32);
        }
        function generateRandomHex() {
            return [...Array(32)].map(() => Math.floor(Math.random() * 16).toString(16)).join('');
        }

        document.getElementById('login-btn').addEventListener('click', async () => {
            const phone = document.getElementById('phone-input').value.trim();
            const password = document.getElementById('password-input').value.trim();
            const errDiv = document.getElementById('login-error');
            if(!phone || !password) { errDiv.innerText = "Enter credentials!"; return; }
            
            let timestampVal = Math.floor(Date.now() / 1000);
            let randomVal = generateRandomHex();
            let payload = { username: phone, pwd: password, phonetype: 1, logintype: "mobile", packId: "", deviceId: "451af594f1be19145249ec1687a6bef2", pixelId: "", fbcId: "", fbc: "", fbp: "", adId: "", language: 7, random: randomVal, timestamp: timestampVal };
            payload.signature = calculateDynamicSignature(payload);

            try {
                let res = await fetch("https://ckygjf6r.com/api/webapi/Login", {
                    method: "POST",
                    headers: { "Content-Type": "application/json;charset=UTF-8" },
                    body: JSON.stringify(payload)
                });
                let data = await res.json();
                if(data && data.code === 0) {
                    let token = data.token || (data.data?.token || data.data);
                    await fetch('/api/set_token', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ token })
                    });
                    location.reload();
                } else {
                    errDiv.innerText = data.msg || "Login failed";
                }
            } catch(e) { errDiv.innerText = "Login network error"; }
        });

        async function toggleBot() {
            await fetch('/api/toggle', { method: 'POST' });
            location.reload();
        }
        async function logoutSession() {
            await fetch('/api/logout', { method: 'POST' });
            location.reload();
        }
    </script>
</body>
</html>
    """, logged_in=bool(bot_state["token"]), is_running=bot_state["is_running"], logs=bot_state["logs"])

@app.route('/api/set_token', methods=['POST'])
def set_token():
    req = request.json
    token = req.get('token')
    if token:
        if isinstance(token, dict): token = token.get('token', '')
        bot_state["token"] = str(token)
        bot_state["is_running"] = True
        log_message("Cloud bot connected successfully via browser token!", "win")
    return jsonify({"success": True})

@app.route('/api/toggle', methods=['POST'])
def api_toggle():
    bot_state["is_running"] = not bot_state["is_running"]
    return jsonify({"is_running": bot_state["is_running"]})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    bot_state["token"] = ""
    bot_state["is_running"] = False
    bot_state["logs"] = []
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
