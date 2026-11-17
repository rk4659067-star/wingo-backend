import time
import hashlib
import json
import random
import requests
from flask import Flask, render_template_string, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# Global Bot State
bot_state = {
    "is_running": False,
    "token": "",
    "game_type_id": 30,
    "base_amount": 10,
    "custom_bet_counts": [1, 10, 100, 1000, 10000, 100000],
    "win_count": 0,
    "loss_count": 0,
    "win_streak": 0,
    "max_win_streak": 0,
    "loss_streak": 0,
    "max_loss_streak": 0,
    "current_level": 1,
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
    idx = min(bot_state["current_level"] - 1, len(levels) - 1)
    return levels[idx]

def get_current_total_bet_amount():
    return bot_state["base_amount"] * get_current_bet_count()

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

# BACKGROUND WORKER FOR 24/7 AUTO BETTING
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
            "Accept": "application/json, text/plain, */*",
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
                epoch_sec = int(time.time())
                remaining_sec = 30 - (epoch_sec % 30)

                if issue_num and issue_num not in bot_state["processed_periods"]:
                    bot_state["processed_periods"].add(issue_num)
                    if bot_state["last_prediction"]:
                        actual = get_bs(num)
                        is_win = (bot_state["last_prediction"] == "SMALL" and actual == "S") or (bot_state["last_prediction"] == "BIG" and actual == "B")
                        was_real_bet = issue_num in bot_state["real_bet_issues"]

                        if is_win:
                            bot_state["win_count"] += 1
                            bot_state["win_streak"] += 1
                            bot_state["loss_streak"] = 0
                            if bot_state["win_streak"] > bot_state["max_win_streak"]:
                                bot_state["max_win_streak"] = bot_state["win_streak"]
                        else:
                            bot_state["loss_count"] += 1
                            bot_state["loss_streak"] += 1
                            bot_state["win_streak"] = 0
                            if bot_state["loss_streak"] > bot_state["max_loss_streak"]:
                                bot_state["max_loss_streak"] = bot_state["loss_streak"]

                        current_total_bet = get_current_total_bet_amount()
                        levels = bot_state["custom_bet_counts"]

                        if was_real_bet:
                            if is_win:
                                bot_state["net_pl"] += current_total_bet
                                log_message(f"Round Win [Real]! Num: {num} [{actual}] | +{current_total_bet} Won.", "win")
                                bot_state["current_level"] = 1
                                bot_state["can_place_bet"] = True
                            else:
                                bot_state["net_pl"] -= current_total_bet
                                log_message(f"Round Loss [Real]! Num: {num} [{actual}] | -{current_total_bet} Lost. Skipping next.", "loss")
                                bot_state["current_level"] += 1
                                if bot_state["current_level"] > len(levels):
                                    bot_state["current_level"] = 1
                                bot_state["can_place_bet"] = False
                        else:
                            if is_win:
                                log_message(f"Skipped Round WIN ✅ ({num} [{actual}]). Resuming real bets.", "win")
                                bot_state["can_place_bet"] = True
                            else:
                                log_message(f"Skipped Round LOSS ❌ ({num} [{actual}]). Continuing skip.", "loss")
                                bot_state["can_place_bet"] = False

                    bot_state["numbers"].append(num)
                    if len(bot_state["numbers"]) > 20:
                        bot_state["numbers"].pop(0)

                next_pred = analyze_pattern()
                bot_state["last_prediction"] = next_pred
                current_active_issue = str(int(issue_num) + 1) if issue_num.isdigit() else ""

                if next_pred and current_active_issue and current_active_issue != bot_state["last_betted_issue"]:
                    if 6 <= remaining_sec <= 29:
                        bot_state["last_betted_issue"] = current_active_issue
                        if bot_state["can_place_bet"]:
                            bot_state["real_bet_issues"].add(current_active_issue)
                            b_count = get_current_bet_count()
                            select_type_val = 13 if next_pred == "BIG" else 14
                            t_val = int(time.time())
                            r_val = generate_random_hex()
                            
                            bet_payload = {
                                "typeId": bot_state["game_type_id"],
                                "issuenumber": current_active_issue,
                                "amount": bot_state["base_amount"],
                                "betCount": b_count,
                                "gameType": 2,
                                "selectType": select_type_val,
                                "language": 7,
                                "random": r_val,
                                "timestamp": t_val
                            }
                            bet_payload["signature"] = calculate_dynamic_signature(bet_payload)
                            requests.post("https://ckygjf6r.com/api/webapi/GameBetting", json=bet_payload, headers=headers, timeout=10)
                            log_message(f"✅ Auto Bet Placed [{current_active_issue}]: {next_pred}", "win")
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
    <title>🔥 WinGo Fully Automatic Bot (Clean Trend Predictor)</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: Arial, sans-serif; }
        body { background: #020617; color: #fff; text-align: center; padding: 15px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .container { width: 100%; max-width: 400px; }
        .card { background: #1e1e1e; padding: 15px; margin: 10px auto; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.5); text-align: left; }
        .dash-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
        .top-badge { background-color: #271515; border: 1px solid #573333; color: #2ecc71; padding: 5px 10px; border-radius: 15px; font-size: 11px; font-weight: bold; }
        .period { color: #f39c12; font-weight: bold; }
        .number { font-size: 22px; color: #2ecc71; font-weight: bold; }
        .timer-display { font-size: 16px; color: #e74c3c; font-weight: bold; background: #2a1215; padding: 4px 8px; border-radius: 6px; border: 1px solid #723232; display: inline-block; }
        #result { margin-top: 10px; font-size: 18px; font-weight: bold; color: #38bdf8; text-align: center; }
        #historyBox { max-height: 140px; overflow-y: auto; background: #111; padding: 10px; margin-top: 15px; border-radius: 10px; text-align: left; font-size: 12px; }
        .win { color: #00ff88; margin-bottom: 4px; }
        .loss { color: #ff3b3b; margin-bottom: 4px; }
        .box { margin-top: 15px; background: #1e1e1e; padding: 12px; border-radius: 8px; text-align: left; }
        .primary-btn { width: 100%; padding: 14px; background: linear-gradient(to right, #f3cf8c, #c99b46); border: none; border-radius: 8px; color: #1a0f0f; font-weight: bold; font-size: 15px; cursor: pointer; margin-top: 10px; box-shadow: 0 4px 10px rgba(212, 163, 83, 0.3); }
        .stop-btn { background: linear-gradient(to right, #e74c3c, #c0392b); color: #fff; }
        .input-group { margin-bottom: 10px; }
        .input-group label { display: block; font-size: 12px; color: #c9a973; margin-bottom: 4px; }
        .input-group input, .input-group select { width: 100%; padding: 10px; background-color: #0f0707; border: 1px solid #573333; border-radius: 6px; color: #fff; font-size: 13px; outline: none; }
    </style>
</head>
<body>
    <!-- 1. LOGIN SCREEN -->
    <div id="login-screen" class="container" style="display: {% if logged_in %}none{% else %}block{% endif %};">
        <div style="text-align: center; margin-bottom: 20px;">
            <div style="font-size: 30px;">🟡</div>
            <h2>Ck Lottery</h2>
            <p style="font-size: 11px; color: #bfa16f;">Cloud 24/7 Server Login</p>
        </div>
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
            <button id="login-btn" class="primary-btn" style="text-align: center;">🔓 Login & Connect</button>
            <div id="login-error" style="color: #ff3b3b; font-size: 12px; margin-top: 8px; text-align: center;">{{ login_error }}</div>
        </div>
    </div>

    <!-- 2. DASHBOARD -->
    <div id="dashboard-screen" class="container" style="display: {% if logged_in %}block{% else %}none{% endif %};">
        <div class="dash-header">
            <h3 style="font-size: 14px; color: #f3cf8c;">🤖 CLOUD SMART GUARD BOT</h3>
            <button class="top-badge" id="user-balance">Bal: Active</button>
        </div>
        <div class="card">
            <button id="bot-toggle-btn" class="primary-btn {% if is_running %}stop-btn{% else %}{% endif %}" onclick="toggleBot()">
                {% if is_running %}⏹ Stop Cloud Bot{% else %}🚀 Start Cloud Bot{% endif %}
            </button>
            <button onclick="logoutSession()" style="width:100%; margin-top:8px; background:none; border:none; color:#c9a973; font-size:11px; text-decoration:underline; cursor:pointer;">🚪 Logout / Change Account</button>
        </div>
        <div class="box">
            <p style="font-size: 12px;">📊 Win: <span id="win">{{ win_count }}</span> | Loss: <span id="loss">{{ loss_count }}</span></p>
            <p style="font-size: 12px; margin-top: 4px;">📈 Net P/L: <span id="net-pl">{{ net_pl }}</span></p>
        </div>
        <h3 style="font-size: 13px; color: #c9a973; margin-top: 15px; text-align: left;">📜 Cloud Live Logs</h3>
        <div id="historyBox">
            {% for log in logs %}
                <div class="{{ log.type }}">[{{ log.time }}] {{ log.msg }}</div>
            {% endfor %}
        </div>
    </div>

    <script>
        const loginBtn = document.getElementById('login-btn');
        const loginError = document.getElementById('login-error');

        function generateRandomHex() {
            return [...Array(32)].map(() => Math.floor(Math.random() * 16).toString(16)).join('');
        }

        loginBtn.addEventListener('click', async () => {
            const phone = document.getElementById('phone-input').value.trim();
            const password = document.getElementById('password-input').value.trim();

            if (!phone || !password) {
                loginError.innerText = "Please enter phone number and password!";
                return;
            }
            loginBtn.innerText = "Logging in...";

            let response = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ phone, password })
            });
            let data = await response.json();
            if (data.success) {
                location.reload();
            } else {
                loginError.innerText = data.msg || "Login failed!";
                loginBtn.innerText = "🔓 Login & Connect";
            }
        });

        async function toggleBot() {
            let res = await fetch('/api/toggle', { method: 'POST' });
            let data = await res.json();
            location.reload();
        }

        async function logoutSession() {
            await fetch('/api/logout', { method: 'POST' });
            location.reload();
        }
    </script>
</body>
</html>
    """, logged_in=bool(bot_state["token"]), is_running=bot_state["is_running"],
       win_count=bot_state["win_count"], loss_count=bot_state["loss_count"],
       net_pl=bot_state["net_pl"], logs=bot_state["logs"], login_error="")

@app.route('/api/login', methods=['POST'])
def api_login():
    req = request.json
    phone = req.get('phone')
    password = req.get('password')
    
    timestamp_val = int(time.time())
    random_val = generate_random_hex()
    login_payload = {
        "username": phone, "pwd": password, "phonetype": 1, "logintype": "mobile",
        "packId": "", "deviceId": "451af594f1be19145249ec1687a6bef2",
        "pixelId": "", "fbcId": "", "fbc": "", "fbp": "", "adId": "",
        "language": 7, "random": random_val, "timestamp": timestamp_val
    }
    login_payload["signature"] = calculate_dynamic_signature(login_payload)

    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "x-app-type": "PWA", 
        "ar-origin": "https://cklottery.cc",
        "origin": "https://cklottery.cc", 
        "referer": "https://cklottery.cc/"
    }

    try:
        res = requests.post("https://ckygjf6r.com/api/webapi/Login", json=login_payload, headers=headers, timeout=15)
        data = res.json()
        if data and data.get("code") == 0:
            token = data.get("token") or (data.get("data") if isinstance(data.get("data"), str) else data.get("data", {}).get("token"))
            if token:
                bot_state["token"] = token
                bot_state["is_running"] = True
                log_message("Cloud bot logged in successfully!", "win")
                return jsonify({"success": True})
        return jsonify({"success": False, "msg": data.get("msg", "Invalid credentials")})
    except Exception as e:
        return jsonify({"success": False, "msg": "Network error: " + str(e)})

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
