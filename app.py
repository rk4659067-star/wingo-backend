import time
import hashlib
import json
import random
import requests
from flask import Flask, render_template_string, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# Global Bot State (100% replicating your frontend logic in Python backend)
bot_state = {
    "is_running": False,
    "phone": "",
    "password": "",
    "token": "",
    "game_type_id": 30,
    "base_amount": 10,
    "custom_bet_counts": [1, 10, 100, 1000, 10000, 100000],
    
    # Statistics & Progress (Same as your JS variables)
    "win_count": 0,
    "loss_count": 0,
    "win_streak": 0,
    "max_win_streak": 0,
    "loss_streak": 0,
    "max_loss_streak": 0,
    "current_level": 1,
    "net_pl": 0,
    
    # Internal Tracking
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
        if o is not None and o != "" and o is not None:
            sorted_obj[r] = 0 if o == 0 else o

    json_str = json.dumps(sorted_obj, separators=(',', ':'))
    md5_hash = hashlib.md5(json_str.encode('utf-8')).hexdigest().upper()
    return md5_hash[:32]

def generate_random_hex():
    return ''.join(random.choice('0123456789abcdef') for _ in range(32))

def get_active_bet_counts_array():
    return bot_state["custom_bet_counts"]

def getCurrentBetCount():
    levels = get_active_bet_counts_array()
    idx = min(bot_state["current_level"] - 1, len(levels) - 1)
    return levels[idx]

def getCurrentTotalBetAmount():
    return bot_state["base_amount"] * getCurrentBetCount()

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

# ----------------- PURE PYTHON 24/7 BACKGROUND WORKER -----------------
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

                epoch_sec = int(time.time())
                remaining_sec = 30 - (epoch_sec % 30)

                # Process Period Result
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

                        current_total_bet = getCurrentTotalBetAmount()
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

                # Prediction & Auto-Betting Logic
                next_pred = analyze_pattern()
                bot_state["last_prediction"] = next_pred
                current_active_issue = str(int(issue_num) + 1) if issue_num.isdigit() else ""

                if next_pred and current_active_issue and current_active_issue != bot_state["last_betted_issue"]:
                    if 6 <= remaining_sec <= 29:
                        bot_state["last_betted_issue"] = current_active_issue
                        if bot_state["can_place_bet"]:
                            bot_state["real_bet_issues"].add(current_active_issue)
                            
                            b_count = getCurrentBetCount()
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

                            bet_res = requests.post("https://ckygjf6r.com/api/webapi/GameBetting", json=bet_payload, headers=headers, timeout=10)
                            b_data = bet_res.json()
                            
                            if b_data and (b_data.get("code") == 0 or b_data.get("msg") in ["Succeed", "Bet success"]):
                                log_message(f"✅ Server Auto Bet Placed [{current_active_issue}]: {next_pred} (Amt: {getCurrentTotalBetAmount()})", "win")
                            else:
                                log_message(f"❌ Bet Failed [{current_active_issue}]: {b_data.get('msg', 'Unknown')}", "loss")
                        else:
                            log_message(f"⏭️ [SKIP] Skipping round {current_active_issue} on server.", "")

    except Exception as e:
        print("Server worker error:", str(e))

# Run independent background worker every 3 seconds on the cloud server
scheduler = BackgroundScheduler()
scheduler.add_job(func=background_bot_loop, trigger="interval", seconds=3)
scheduler.start()

# ----------------- DASHBOARD UI ROUTE -----------------
@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔥 WinGo Fully Automatic Bot (Server 24/7)</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: Arial, sans-serif; }
        body { background: #020617; color: #fff; text-align: center; padding: 15px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .container { width: 100%; max-width: 400px; }
        .card { background: #1e1e1e; padding: 15px; margin: 10px auto; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.5); text-align: left; }
        .dash-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
        .top-badge { background-color: #271515; border: 1px solid #573333; color: #2ecc71; padding: 5px 10px; border-radius: 15px; font-size: 11px; font-weight: bold; }
        #historyBox { max-height: 150px; overflow-y: auto; background: #111; padding: 10px; margin-top: 15px; border-radius: 10px; text-align: left; font-size: 11px; }
        .win { color: #00ff88; margin-bottom: 4px; }
        .loss { color: #ff3b3b; margin-bottom: 4px; }
        .primary-btn { width: 100%; padding: 14px; background: linear-gradient(to right, #f3cf8c, #c99b46); border: none; border-radius: 8px; color: #1a0f0f; font-weight: bold; font-size: 15px; cursor: pointer; margin-top: 10px; box-shadow: 0 4px 10px rgba(212, 163, 83, 0.3); }
        .stop-btn { background: linear-gradient(to right, #e74c3c, #c0392b); color: #fff; }
        .input-group { margin-bottom: 10px; }
        .input-group label { display: block; font-size: 12px; color: #c9a973; margin-bottom: 4px; }
        .input-group input, .input-group select { width: 100%; padding: 10px; background-color: #0f0707; border: 1px solid #573333; border-radius: 6px; color: #fff; font-size: 13px; outline: none; }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/crypto-js/4.1.1/crypto-js.min.js"></script>
</head>
<body>

    <!-- 1. LOGIN SCREEN -->
    <div id="login-screen" class="container" style="display: {% if logged_in %}none{% else %}block{% endif %};">
        <div style="text-align: center; margin-bottom: 20px;">
            <div style="font-size: 30px;">🟡</div>
            <h2>Ck Lottery</h2>
            <p style="font-size: 11px; color: #bfa16f;">Server 24/7 Autonomous Bot Login</p>
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
            <button id="login-btn" class="primary-btn" style="text-align: center;">🔓 Login & Start Server Bot</button>
            <div id="login-error" style="color: #ff3b3b; font-size: 12px; margin-top: 8px; text-align: center;"></div>
        </div>
    </div>

    <!-- 2. DASHBOARD -->
    <div id="dashboard-screen" class="container" style="display: {% if logged_in %}block{% else %}none{% endif %};">
        <div class="dash-header">
            <h3 style="font-size: 13px; color: #f3cf8c;">🤖 24/7 CLOUD SERVER BOT</h3>
            <button class="top-badge" id="user-balance">Bal: Active</button>
        </div>

        <div class="card">
            <div class="input-group">
                <label>Select Game Timer (Mode)</label>
                <select id="game-type-id" onchange="updateSettings()">
                    <option value="30" {% if game_type_id == 30 %}selected{% endif %}>WinGo 30s</option>
                    <option value="1" {% if game_type_id == 1 %}selected{% endif %}>WinGo 1Min</option>
                    <option value="2" {% if game_type_id == 2 %}selected{% endif %}>WinGo 3Min</option>
                    <option value="3" {% if game_type_id == 3 %}selected{% endif %}>WinGo 5Min</option>
                </select>
            </div>

            <div class="input-group">
                <label>Base Amount</label>
                <input type="number" id="base-amount" value="{{ base_amount }}" onchange="updateSettings()">
            </div>

            <div class="input-group">
                <label>Custom Bet Count Levels</label>
                <input type="text" id="custom-bet-counts" value="1, 10, 100, 1000, 10000, 100000" onchange="updateSettings()">
            </div>
            
            <div style="font-size: 12px; margin: 8px 0;">Server Bot Status: <span style="color: #00ff88; font-weight: bold;">{% if is_running %}Running 24/7 on Cloud 🚀{% else %}Paused ⏸️{% endif %}</span></div>

            <button id="bot-toggle-btn" class="primary-btn {% if is_running %}stop-btn{% else %}{% endif %}" onclick="toggleBot()">
                {% if is_running %}⏹ Stop Server Bot{% else %}🚀 Start Server Bot{% endif %}
            </button>
            <button onclick="logoutSession()" style="width:100%; margin-top:8px; background:none; border:none; color:#c9a973; font-size:11px; text-decoration:underline; cursor:pointer;">🚪 Logout / Change Account</button>
        </div>

        <div class="card" style="font-size: 12px;">
            <p>📊 Win: <span style="color: #00ff88">{{ win_count }}</span> | Loss: <span style="color: #ff3b3b">{{ loss_count }}</span></p>
            <p style="margin-top: 4px;">🔥 Win Streak: {{ win_streak }} (Max: {{ max_win_streak }})</p>
            <p style="margin-top: 4px;">❄️ Loss Streak: {{ loss_streak }} (Max: {{ max_loss_streak }})</p>
            <p style="margin-top: 4px;">🔥 Current Level: Level {{ current_level }}</p>
            <p style="margin-top: 4px; font-weight: bold; color: #f3cf8c;">📈 Net P/L: <span style="color: {% if net_pl >= 0 %}#00ff88{% else %}#ff3b3b{% endif %};">{{ net_pl }}</span></p>
        </div>

        <h3 style="font-size: 13px; color: #c9a973; margin-top: 15px; text-align: left;">📜 Server 24/7 Live Logs</h3>
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
            if(!phone || !password) { errDiv.innerText = "Enter phone and password!"; return; }

            document.getElementById('login-btn').innerText = "Logging in...";

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
                    await fetch('/api/login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ phone, password, token })
                    });
                    location.reload();
                } else {
                    errDiv.innerText = data.msg || "Login failed";
                    document.getElementById('login-btn').innerText = "🔓 Login & Start Server Bot";
                }
            } catch(e) { 
                errDiv.innerText = "Login network error"; 
                document.getElementById('login-btn').innerText = "🔓 Login & Start Server Bot";
            }
        });

        async function toggleBot() {
            await fetch('/api/toggle', { method: 'POST' });
            location.reload();
        }

        async function updateSettings() {
            let gameTypeId = document.getElementById('game-type-id').value;
            let baseAmount = document.getElementById('base-amount').value;
            let levels = document.getElementById('custom-bet-counts').value;
            await fetch('/api/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ game_type_id: gameTypeId, base_amount: baseAmount, custom_bet_counts: levels })
            });
        }

        async function logoutSession() {
            await fetch('/api/logout', { method: 'POST' });
            location.reload();
        }

        // Auto refresh dashboard every 4 seconds to show live server background logs and profit/loss
        setTimeout(function(){ location.reload(); }, 4000);
    </script>
</body>
</html>
    """, logged_in=bool(bot_state["token"]), is_running=bot_state["is_running"],
       win_count=bot_state["win_count"], loss_count=bot_state["loss_count"],
       win_streak=bot_state["win_streak"], max_win_streak=bot_state["max_win_streak"],
       loss_streak=bot_state["loss_streak"], max_loss_streak=bot_state["max_loss_streak"],
       current_level=bot_state["current_level"], net_pl=bot_state["net_pl"],
       game_type_id=bot_state["game_type_id"], base_amount=bot_state["base_amount"],
       logs=bot_state["logs"])

@app.route('/api/login', methods=['POST'])
def api_login():
    req = request.json
    bot_state["phone"] = req.get('phone')
    bot_state["password"] = req.get('password')
    token = req.get('token')
    if token:
        if isinstance(token, dict): token = token.get('token', '')
        bot_state["token"] = str(token)
        bot_state["is_running"] = True
        log_message("Server Bot connected and started successfully!", "win")
    return jsonify({"success": True})

@app.route('/api/toggle', methods=['POST'])
def api_toggle():
    bot_state["is_running"] = not bot_state["is_running"]
    status_msg = "Resumed" if bot_state["is_running"] else "Paused"
    log_message(f"Server Bot {status_msg} by user.", "win" if bot_state["is_running"] else "loss")
    return jsonify({"is_running": bot_state["is_running"]})

@app.route('/api/settings', methods=['POST'])
def api_settings():
    req = request.json
    bot_state["game_type_id"] = int(req.get('game_type_id', 30))
    bot_state["base_amount"] = int(req.get('base_amount', 10))
    levels_str = req.get('custom_bet_counts', '1,10,100,1000,10000,100000')
    try:
        bot_state["custom_bet_counts"] = [int(x.strip()) for x in levels_str.split(',') if x.strip().isdigit()]
    except:
        pass
    return jsonify({"success": True})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    bot_state["token"] = ""
    bot_state["is_running"] = False
    bot_state["logs"] = []
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
