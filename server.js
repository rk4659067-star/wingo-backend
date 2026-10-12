const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

let historyData = [];
let processedPeriods = new Set();

const apiUrl = "https://ckygjf6r.com/api/webapi/GetNoaverageEmerdList";
const payload = {
    pageSize: 10,
    pageNo: 1,
    typeId: 30, // Sirf 30s ke liye
    language: 7,
    random: "1f6d74756f024a74891dd1d4a9db6720",
    signature: "030503A5B0C2FF81B0D3E536EA272C93",
    timestamp: 1791640138
};

const apiHeaders = {
    "Content-Type": "application/json",
    "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOiIxNzkxNjM5ODI0IiwibmJmIjoiMTc5MTYzOTgyNCIsImV4cCI6IjE3OTE2NDE2MjQiLCJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL2V4cGlyYXRpb24iOiIxMC8xMC8yMDI2IDg6NDM6NDQgUE0iLCJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL3JvbGUiOiJBY2Nlc3NfVG9rZW4iLCJVc2VySWQiOiIzODc3NjUiLCJVc2VyTmFtZSI6Ijk1OTc4NTkyNTMyMyIsIlVzZXJQaG90byI6IjEiLCJOaWNrTmFtZSI6Ik1lbWJlck5OR1FDREFSIiwiQW1vdW50IjoiMzk0Ni4zNCIsIkludGVncmFsIjoiMCIsIkxvZ2luTWFyayI6Ikg1IiwiTG9naW5UaW1lIjoiMTAvMTAvMjAyNiA4OjEzOjQ0IFBNIiwiTG9naW5JUEFkZHJlc3MiOiIyNy4xMzAuMTY5LjE2IiwiRGJOdW1iZXIiOiIwIiwiSXN2YWxpZGF0b3IiOiIwIiwiS2V5Q29kZSI6IjI1NSIsIlRva2VuVHlwZSI6IkFjY2Vzc19Ub2tlbiIsIlBob25lVHlwZSI6IjEiLCJVc2VyVHlwZSI6IjAiLCJVc2VyTmFtZTIiOiIiLCJpc3MiOiJqd3RJc3N1ZXIiOiJhdWQiOiJsb3R0ZXJ5VGlja2V0In0.IUMgb7VsDkGelJ08vzwmjftvYtOuA7uSQafKHdldyFQ",
    "ar-origin": "https://cklottery.cc",
    "origin": "https://cklottery.cc",
    "referer": "https://cklottery.cc/",
    "user-agent": "Mozilla/5.0 (Linux; Android 10)"
};

async function fetchAndStore() {
    try {
        let response = await fetch(apiUrl, {
            method: "POST",
            headers: apiHeaders,
            body: JSON.stringify(payload)
        });
        
        let text = await response.text();
        let data;
        try {
            data = JSON.parse(text);
        } catch (e) {
            console.error("Non-JSON Response received:", text.substring(0, 100));
            return;
        }

        if (data && data.code === 0 && data.data && data.data.list) {
            let list = data.data.list.slice().reverse();
            list.forEach(item => {
                if (!processedPeriods.has(item.issueNumber)) {
                    processedPeriods.add(item.issueNumber);
                    historyData.unshift(item);
                    if (historyData.length > 200) historyData.pop();
                }
            });
            console.log(`[${new Date().toLocaleTimeString()}] 30s Polled successfully. Total stored: ${historyData.length}`);
        }
    } catch (error) {
        console.error("API Fetch Error:", error.message);
    }
}

// Har 5 second mein 30s ka data fetch karega
setInterval(fetchAndStore, 5000);

app.get('/api/get-data', (req, res) => {
    res.json({
        success: true,
        history: historyData
    });
});

app.get('/', (req, res) => {
    res.send("🔥 WinGo 30s Background Bot is Active!");
});

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
