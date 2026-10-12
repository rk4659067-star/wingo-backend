const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

// In-memory storage for 24/7 background data
let historyData = [];
let processedPeriods = new Set();

const apiUrl = "https://ckygjf6r.com/api/webapi/GetNoaverageEmerdList";
const payload = {
    pageSize: 10,
    pageNo: 1,
    typeId: 30,
    language: 7,
    random: "1f6d74756f024a74891dd1d4a9db6720",
    signature: "030503A5B0C2FF81B0D3E536EA272C93",
    timestamp: 1791640138
};

const apiHeaders = {
    "Content-Type": "application/json",
    "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOiIxNzkxNjM5ODI0IiwibmJmIjoiMTc5MTYzOTgyNCIsImV4cCI6IjE3OTE2NDE2MjQiLCJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL2V4cGlyYXRpb24iOiIxMC8xMC8yMDI2IDg6NDM6NDQgUE0iLCJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL3JvbGUiOiJBY2Nlc3NfVG9rZW4iLCJVc2RuSWQiOiIzODc3NjUiLCJVc2VyTmFtZSI6Ijk1OTc4NTkyNTMyMyIsIlVzZXJQaG90byI6IjEiLCJOaWNrTmFtZSI6Ik1lbWJlck5OR1FDREFSIiwiQW1vdW50IjoiMzk0Ni4zNCIsIkludGVncmFsIjoiMCIsIkxvZ2luTWFyayI6Ikg1IiwiTG9naW5UaW1lIjoiMTAvMTAvMjAyNiA4OjEzOjQ0IFBNIiwiTG9naW5JUEFkZHJlc3MiOiIyNy4xMzAuMTY5LjE2IiwiRGJOdW1iZXIiOiIwIiwiSXN2YWxpZGF0borIiwiS2V5Q29kZSI6IjI1NSIsIlRva2VuVHlwZSI6IkFjY2Vzc19Ub2tlbiIsIlBob25lVHlwZSI6IjEiLCJVc2VyVHlwZSI6IjAiLCJVc2VyTmFtZTIiOiIiLCJpc3MiOiJqd3RJc3N1ZXIiOiJhdWQiOiJsb3R0ZXJ5VGlja2V0In0.IUMgb7VsDkGelJ08vzwmjftvYtOuA7uSQafKHdldyFQ",
    "ar-origin": "https://cklottery.cc",
    "origin": "https://cklottery.cc",
    "referer": "https://cklottery.cc/",
    "user-agent": "Mozilla/5.0 (Linux; Android 10)"
};

// Background polling function running 24/7 on Render
async function fetchAndStore() {
    try {
        let response = await fetch(apiUrl, {
            method: "POST",
            headers: apiHeaders,
            body: JSON.stringify(payload)
        });
        let data = await response.json();

        if (data && data.code === 0 && data.data && data.data.list) {
            let list = data.data.list.slice().reverse();
            list.forEach(item => {
                if (!processedPeriods.has(item.issueNumber)) {
                    processedPeriods.add(item.issueNumber);
                    historyData.unshift(item);
                    // Keep max last 200 items in memory
                    if (historyData.length > 200) historyData.pop();
                }
            });
            console.log(`[${new Date().toLocaleTimeString()}] Polled successfully. Total stored: ${historyData.length}`);
        }
    } catch (error) {
        console.error("API Fetch Error:", error);
    }
}

// Poll every 5 seconds
setInterval(fetchAndStore, 5000);

// Endpoint for your HTML app to fetch data anytime
app.get('/api/get-data', (req, res) => {
    res.json({
        success: true,
        history: historyData
    });
});

app.get('/', (req, res) => {
    res.send("🔥 WinGo 24/7 Background Bot is Active!");
});

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
