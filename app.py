import os
from flask import Flask, render_template_string

app = Flask(__name__)

# Aapka 100% Exact Original HTML/JS Code jo Render par as it is run hoga
ORIGINAL_HTML_CODE = """
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
        .row-flex { display: flex; gap: 10px; }
        .row-flex .input-group { flex: 1; }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/crypto-js/4.1.1/crypto-js.min.js"></script>
</head>
<body>

    <!-- 1. LOGIN SCREEN -->
    <div id="login-screen" class="container">
        <div style="text-align: center; margin-bottom: 20px;">
            <div style="font-size: 30px;">🟡</div>
            <h2>Ck Lottery</h2>
            <p style="font-size: 11px; color: #bfa16f;">Direct Mobile Login</p>
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
            <div id="login-error" style="color: #ff3b3b; font-size: 12px; margin-top: 8px; text-align: center;"></div>
        </div>
    </div>

    <!-- 2. DASHBOARD -->
    <div id="dashboard-screen" class="container" style="display: none;">
        <div class="dash-header">
            <h3 style="font-size: 14px; color: #f3cf8c;">🤖 SMART GUARD BOT</h3>
            <button class="top-badge" id="user-balance">Bal: Checking...</button>
        </div>

        <div class="card">
            <div class="input-group">
                <label>Select Game Timer (Mode)</label>
                <select id="game-type-id">
                    <option value="30">WinGo 30s</option>
                    <option value="1">WinGo 1Min</option>
                    <option value="2">WinGo 3Min</option>
                    <option value="3">WinGo 5Min</option>
                </select>
            </div>

            <div class="input-group">
                <label>Base Amount</label>
                <input type="number" id="base-amount" value="10">
            </div>

            <div class="input-group">
                <label>Custom Bet Count Levels (Comma Separated)</label>
                <input type="text" id="custom-bet-counts" value="1, 10, 100, 1000, 10000, 100000" placeholder="e.g. 1, 10, 100, 1000">
            </div>
            
            <div style="display: flex; justify-content: space-between; align-items: center; margin: 8px 0;">
                <div style="font-size: 12px;">Latest Period: <span id="latest-period" class="period">-</span></div>
                <div class="timer-display">⏳ <span id="game-timer">00:30</span></div>
            </div>
            <div style="font-size: 12px; margin-bottom: 8px;">Winning Number: <span id="latest-number" class="number">-</span></div>
            <div id="result">Bot Idle (Click Start)</div>

            <button id="bot-toggle-btn" class="primary-btn" onclick="toggleBot()">🚀 Start Smart-Auto Bot</button>
            <button onclick="logoutSession()" style="width:100%; margin-top:8px; background:none; border:none; color:#c9a973; font-size:11px; text-decoration:underline; cursor:pointer;">🚪 Logout / Change Account</button>
        </div>

        <div class="box">
            <p style="font-size: 12px;">📊 Win: <span id="win">0</span> | Loss: <span id="loss">0</span></p>
            <p style="font-size: 12px; margin-top: 4px;">🔥 Win Streak: <span id="win-streak">0</span> (Max: <span id="max-win-streak">0</span>)</p>
            <p style="font-size: 12px; margin-top: 4px;">❄️ Loss Streak: <span id="loss-streak">0</span> (Max: <span id="max-loss-streak">0</span>)</p>
            <p style="font-size: 12px; margin-top: 4px;">🎯 Confidence: <span id="conf">0%</span></p>
            <p style="font-size: 12px; margin-top: 4px;">🔥 Current Level: Level <span id="current-level">1</span> (Bet Count: <span id="current-bet-count">1</span>)</p>
            <p style="font-size: 12px; margin-top: 4px;">💰 Next Bet Total Amount: <span id="bet-amount">10</span></p>
            <p style="font-size: 12px; margin-top: 4px; font-weight: bold; color: #f3cf8c;">📈 Net P/L: <span id="net-pl">0</span></p>
        </div>

        <h3 style="font-size: 13px; color: #c9a973; margin-top: 15px; text-align: left;">📜 Live Action & Logs</h3>
        <div id="historyBox"></div>
    </div>

    <script>
        const loginScreen = document.getElementById('login-screen');
        const dashboardScreen = document.getElementById('dashboard-screen');
        const loginBtn = document.getElementById('login-btn');
        const userBalance = document.getElementById('user-balance');
        const loginError = document.getElementById('login-error');

        let activeToken = "";
        let numbers = [];
        let lastPrediction = "";
        let historyList = [];
        let processedPeriods = new Set();
        let lastBettedIssue = "";
        let realBetIssues = new Set();

        let winCount = 0, lossCount = 0;
        let currentWinStreak = 0, maxWinStreak = 0;
        let currentLossStreak = 0, maxLossStreak = 0;
        let currentLevel = 1;
        let netProfitLoss = 0;
        let isBotRunning = false;
        let canPlaceBet = true;

        function getActiveBetCountsArray() {
            let inputVal = document.getElementById("custom-bet-counts").value;
            let arr = inputVal.split(',').map(item => parseInt(item.trim())).filter(num => !isNaN(num) && num > 0);
            if (arr.length === 0) arr = [1];
            return arr;
        }

        function getCurrentBetCount() {
            let levels = getActiveBetCountsArray();
            let idx = Math.min(currentLevel - 1, levels.length - 1);
            return levels[idx];
        }

        function getCurrentTotalBetAmount() {
            let baseAmt = parseInt(document.getElementById("base-amount").value) || 10;
            return baseAmt * getCurrentBetCount();
        }

        function calculateDynamicSignature(payloadObj) {
            let t = { ...payloadObj };
            delete t.signature;
            delete t.timestamp;
            delete t.track;
            delete t.xosoBettingData;

            const sortedObj = {};
            Object.keys(t).sort().forEach(r => {
                const o = t[r];
                if (o !== null && o !== "" && o !== undefined) {
                    sortedObj[r] = (o === 0) ? 0 : o;
                }
            });

            let jsonStr = JSON.stringify(sortedObj);
            let md5Hash = CryptoJS.MD5(jsonStr).toString().toUpperCase();
            return md5Hash.slice(0, 32);
        }

        function generateRandomHex() {
            return [...Array(32)].map(() => Math.floor(Math.random() * 16).toString(16)).join('');
        }

        window.addEventListener('DOMContentLoaded', () => {
            const savedToken = localStorage.getItem("wingo_phone_token");
            if (savedToken) {
                activeToken = savedToken;
                loginScreen.style.display = 'none';
                dashboardScreen.style.display = 'block';
                fetchUserBalance();
                fetchLiveData();
                setInterval(fetchLiveData, 1000);
            }
        });

        loginBtn.addEventListener('click', async () => {
            const phone = document.getElementById('phone-input').value.trim();
            const password = document.getElementById('password-input').value.trim();

            if (!phone || !password) {
                loginError.innerText = "Please enter phone number and password!";
                return;
            }

            loginBtn.innerText = "Logging in...";
            loginError.innerText = "";

            let timestampVal = Math.floor(Date.now() / 1000);
            let randomVal = generateRandomHex();

            let loginPayload = {
                username: phone, pwd: password, phonetype: 1, logintype: "mobile",
                packId: "", deviceId: "451af594f1be19145249ec1687a6bef2",
                pixelId: "", fbcId: "", fbc: "", fbp: "", adId: "",
                language: 7, random: randomVal, timestamp: timestampVal
            };
            loginPayload.signature = calculateDynamicSignature(loginPayload);

            try {
                let response = await fetch("https://ckygjf6r.com/api/webapi/Login", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json;charset=UTF-8",
                        "Accept": "application/json, text/plain, */*",
                        "x-app-type": "PWA", "ar-origin": "https://cklottery.cc",
                        "origin": "https://cklottery.cc", "referer": "https://cklottery.cc/"
                    },
                    body: JSON.stringify(loginPayload)
                });

                let data = await response.json();
                
                if (data && data.code === 0) {
                    if (data.token) activeToken = data.token;
                    else if (data.data) {
                        if (typeof data.data === 'string') activeToken = data.data;
                        else if (data.data.token) activeToken = data.data.token;
                    }

                    if (!activeToken && data.data) {
                        activeToken = JSON.stringify(data.data);
                    }

                    localStorage.setItem("wingo_phone_token", activeToken);

                    loginScreen.style.display = 'none';
                    dashboardScreen.style.display = 'block';
                    fetchUserBalance();
                    fetchLiveData();
                    setInterval(fetchLiveData, 1000);
                } else {
                    loginError.innerText = data.msg || "Login failed! Check credentials.";
                    loginBtn.innerText = "🔓 Login & Connect";
                }
            } catch (err) {
                loginError.innerText = "Network error during login.";
                loginBtn.innerText = "🔓 Login & Connect";
            }
        });

        function logoutSession() {
            localStorage.removeItem("wingo_phone_token");
            dashboardScreen.style.display = 'none';
            loginScreen.style.display = 'block';
            loginBtn.innerText = "🔓 Login & Connect";
        }

        async function fetchUserBalance() {
            try {
                let timestampVal = Math.floor(Date.now() / 1000);
                let randomVal = generateRandomHex();
                let balPayload = { language: 7, random: randomVal, timestamp: timestampVal };
                balPayload.signature = calculateDynamicSignature(balPayload);

                let response = await fetch("https://ckygjf6r.com/api/webapi/GetBalance", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json;charset=UTF-8",
                        "authorization": "Bearer " + activeToken,
                        "x-app-type": "PWA", "ar-origin": "https://cklottery.cc",
                        "origin": "https://cklottery.cc", "referer": "https://cklottery.cc/"
                    },
                    body: JSON.stringify(balPayload)
                });
                let data = await response.json();
                
                let balValue = "0";
                if (data && data.code === 0 && data.data !== undefined) {
                    if (typeof data.data === 'object' && data.data !== null) {
                        balValue = data.data.amount ?? data.data.money ?? data.data.balance ?? Object.values(data.data)[0] ?? "0";
                    } else {
                        balValue = data.data;
                    }
                }
                userBalance.innerText = "Bal: " + balValue;
            } catch (err) {
                userBalance.innerText = "Bal: Err";
            }
        }

        function toggleBot() {
            isBotRunning = !isBotRunning;
            const btn = document.getElementById("bot-toggle-btn");
            if (isBotRunning) {
                btn.innerText = "⏹ Stop Smart-Auto Bot";
                btn.className = "primary-btn stop-btn";
                currentLevel = 1;
                netProfitLoss = 0;
                winCount = 0; lossCount = 0;
                currentWinStreak = 0; maxWinStreak = 0;
                currentLossStreak = 0; maxLossStreak = 0;
                canPlaceBet = true;
                realBetIssues.clear();
                lastBettedIssue = "";
                logMessage("Smart-Auto bot started successfully!", "win");
            } else {
                btn.innerText = "🚀 Start Smart-Auto Bot";
                btn.className = "primary-btn";
                logMessage("Bot stopped by user.", "loss");
            }
        }

        function logMessage(msg, type = "") {
            let cls = type === "win" ? "win" : (type === "loss" ? "loss" : "");
            historyList.unshift(`<div class="${cls}">[${new Date().toLocaleTimeString()}] ${msg}</div>`);
            document.getElementById("historyBox").innerHTML = historyList.join("");
        }

        async function fetchLiveData() {
            if (dashboardScreen.style.display === 'none') return;

            const selectedTypeId = parseInt(document.getElementById("game-type-id").value) || 30;
            const url = "https://ckygjf6r.com/api/webapi/GetNoaverageEmerdList";
            
            let timestampVal = Math.floor(Date.now() / 1000);
            let randomVal = generateRandomHex();

            const payload = {
                pageSize: 10, pageNo: 1, typeId: selectedTypeId, language: 7,
                random: randomVal, timestamp: timestampVal
            };
            payload.signature = calculateDynamicSignature(payload);

            try {
                let response = await fetch(url, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json;charset=UTF-8",
                        "authorization": "Bearer " + activeToken,
                        "x-app-type": "PWA", "ar-origin": "https://cklottery.cc",
                        "origin": "https://cklottery.cc", "referer": "https://cklottery.cc/"
                    },
                    body: JSON.stringify(payload)
                });

                let data = await response.json();
                
                if (data && data.code === 0 && data.data) {
                    let list = data.data.list || data.data.data || data.data;
                    if (Array.isArray(list) && list.length > 0) {
                        let latestItem = list[0];
                        let issueNum = latestItem.issueNumber || latestItem.issuenumber;
                        let num = parseInt(latestItem.number);

                        let epochSeconds = Math.floor(Date.now() / 1000);
                        let remainingSeconds = 30 - (epochSeconds % 30);
                        let timerFormatted = "00:" + (remainingSeconds < 10 ? "0" : "") + remainingSeconds;
                        document.getElementById("game-timer").innerText = timerFormatted;

                        if (issueNum && !processedPeriods.has(issueNum)) {
                            processedPeriods.add(issueNum);
                            document.getElementById("latest-period").innerText = issueNum;
                            document.getElementById("latest-number").innerText = num;

                            checkResultAndProgression(issueNum, num);
                            numbers.push(num);
                        }

                        let nextPred = analyzePattern();
                        let currentActiveIssue = (BigInt(issueNum) + 1n).toString();

                        if (isBotRunning && nextPred && currentActiveIssue !== lastBettedIssue) {
                            if (remainingSeconds >= 6 && remainingSeconds <= 29) {
                                lastBettedIssue = currentActiveIssue;
                                if (canPlaceBet) {
                                    realBetIssues.add(currentActiveIssue);
                                    placeRealBet(nextPred, selectedTypeId, currentActiveIssue);
                                } else {
                                    logMessage(`⏭️ [SKIP] Previous bet lost. Skipping round ${currentActiveIssue} (Tracking virtually).`, "");
                                }
                            }
                        }
                    }
                }
            } catch (error) {
                console.error("Error fetching live data:", error);
            }
        }

        function getBS(n) { return n <= 4 ? "S" : "B"; }

        function analyzePattern() {
            if (numbers.length < 3) {
                document.getElementById("result").innerText = "Collecting history (" + numbers.length + "/3)...";
                document.getElementById("conf").innerText = "0%";
                return "";
            }

            let recentBS = numbers.map(getBS);
            let fullStr = recentBS.join(""); 
            let prediction = "";
            let patternName = "Standard Trend";
            let confidence = 85;

            if (fullStr.endsWith("SBS")) {
                prediction = "BIG";
                patternName = "Zig-Zag Trend (SBS)";
                confidence = 90;
            } else if (fullStr.endsWith("BSB")) {
                prediction = "SMALL";
                patternName = "Zig-Zag Trend (BSB)";
                confidence = 90;
            } else {
                let lastBS = recentBS[recentBS.length - 1];
                prediction = (lastBS === "S") ? "SMALL" : "BIG";
                patternName = "Same Trend Follow";
                confidence = 75;
            }

            document.getElementById("conf").innerText = confidence + "%";
            document.getElementById("result").innerText = `🤖 [${patternName}] ➔ ${prediction}`;
            lastPrediction = prediction;
            return prediction;
        }

        function checkResultAndProgression(issueNum, n) {
            if (!lastPrediction) return;

            let actual = getBS(n);
            let isWin = (lastPrediction === "SMALL" && actual === "S") || (lastPrediction === "BIG" && actual === "B");
            let wasRealBet = realBetIssues.has(issueNum);

            if (isWin) {
                winCount++;
                currentWinStreak++;
                currentLossStreak = 0;
                if (currentWinStreak > maxWinStreak) maxWinStreak = currentWinStreak;
            } else {
                lossCount++;
                currentLossStreak++;
                currentWinStreak = 0;
                if (currentLossStreak > maxLossStreak) maxLossStreak = currentLossStreak;
            }

            if (wasRealBet) {
                let currentTotalBet = getCurrentTotalBetAmount();
                let levels = getActiveBetCountsArray();

                if (isWin) {
                    let wonAmount = currentTotalBet; 
                    netProfitLoss += wonAmount;
                    logMessage(`Round Win [Real Bet]! Actual: ${n} [${actual}] | +${wonAmount} Won. Continuing real bets.`, "win");
                    currentLevel = 1;
                    canPlaceBet = true;
                } else {
                    let lostAmount = currentTotalBet;
                    netProfitLoss -= lostAmount;
                    logMessage(`Round Loss [Real Bet]! Actual: ${n} [${actual}] | -${lostAmount} Lost. Skipping next bet until a win occurs.`, "loss");
                    currentLevel++;
                    if (currentLevel > levels.length) {
                        currentLevel = 1;
                    }
                    canPlaceBet = false;
                }
            } else {
                if (isWin) {
                    logMessage(`Skipped Round Result: WIN ✅ (${n} [${actual}]). Target win achieved! Resuming real bets on next round.`, "win");
                    canPlaceBet = true;
                } else {
                    logMessage(`Skipped Round Result: LOSS ❌ (${n} [${actual}]). Still waiting for a win to resume real betting.`, "loss");
                    canPlaceBet = false;
                }
            }

            let nextTotalBet = getCurrentTotalBetAmount();
            let nextBetCount = getCurrentBetCount();
            document.getElementById("win").innerText = winCount;
            document.getElementById("loss").innerText = lossCount;
            document.getElementById("win-streak").innerText = currentWinStreak;
            document.getElementById("max-win-streak").innerText = maxWinStreak;
            document.getElementById("loss-streak").innerText = currentLossStreak;
            document.getElementById("max-loss-streak").innerText = maxLossStreak;
            document.getElementById("current-level").innerText = currentLevel;
            document.getElementById("current-bet-count").innerText = nextBetCount;
            document.getElementById("bet-amount").innerText = nextTotalBet;
            document.getElementById("net-pl").innerText = (netProfitLoss >= 0 ? "+" : "") + netProfitLoss;
            document.getElementById("net-plstyle").color = netProfitLoss >= 0 ? "#00ff88" : "#ff3b3b";
            
            fetchUserBalance();
        }

        async function placeRealBet(prediction, typeIdVal, targetIssue) {
            if (!prediction || !targetIssue) return;

            let baseAmt = parseInt(document.getElementById("base-amount").value) || 10;
            let finalBetCount = getCurrentBetCount(); 
            let selectTypeVal = (prediction === "BIG") ? 13 : 14;

            let timestampVal = Math.floor(Date.now() / 1000);
            let randomVal = generateRandomHex();

            const betPayload = {
                typeId: typeIdVal, 
                issuenumber: targetIssue, 
                amount: baseAmt,
                betCount: finalBetCount,
                gameType: 2, 
                selectType: selectTypeVal,
                language: 7, 
                random: randomVal, 
                timestamp: timestampVal
            };
            betPayload.signature = calculateDynamicSignature(betPayload);

            try {
                let response = await fetch("https://ckygjf6r.com/api/webapi/GameBetting", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json;charset=UTF-8",
                        "authorization": "Bearer " + activeToken,
                        "x-app-type": "PWA", "ar-origin": "https://cklottery.cc",
                        "origin": "https://cklottery.cc", "referer": "https://cklottery.cc/"
                    },
                    body: JSON.stringify(betPayload)
                });

                let resData = await response.json();
                
                if (resData && (resData.code === 0 || resData.msg === "Succeed" || resData.msg === "Bet success")) {
                    logMessage(`✅ Bet Placed [${targetIssue}]: ${prediction} (Total: ${getCurrentTotalBetAmount()})`, "win");
                    fetchUserBalance();
                } else {
                    let serverMsg = resData.msg || "Unknown Error";
                    let serverCode = resData.code ?? "No Code";
                    logMessage(`❌ Bet Fail [${targetIssue}] (Code: ${serverCode}): ${serverMsg}`, "loss");
                }
            } catch (err) {
                logMessage(`❌ Network error during betting.`, "loss");
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(ORIGINAL_HTML_CODE)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
