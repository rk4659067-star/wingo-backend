const axios = require('axios');
const { initializeApp } = require('firebase/app');
const { getFirestore, doc, setDoc } = require('firebase/firestore');

// Firebase Configuration (Apni details yahan dalo agar change karni hon)
const firebaseConfig = {
  apiKey: "YOUR_FIREBASE_API_KEY",
  authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT_ID.appspot.com",
  messagingSenderId: "YOUR_SENDER_ID",
  appId: "YOUR_APP_ID"
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

async function fetchAndSaveData() {
    const url = "https://ckygjf6r.com/api/webapi/GetNoaverageEmerdList";
    
    // Fresh payload
    const payload = {
        pageSize: 10,
        pageNo: 1,
        typeId: 30,
        language: 7,
        random: "23792de78b5b4b86aa76681229f03b2",
        signature: "BBDA0366DD3EF072D7ACFAC97983DE0D",
        timestamp: 1791645408
    };

    try {
        let response = await axios.post(url, payload, {
            headers: {
                "Content-Type": "application/json",
                "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOiIxNzkxNjM5ODI0IiwibmJmIjoiMTc5MTYzOTgyNCIsImV4cCI6IjE3OTE2NDE2MjQiLCJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL2V4cGlyYXRpb24iOiIxMC8xMC8yMDI2IDg6NDM6NDQgUE0iLCJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL3JvbGUiOiJBY2Nlc3NfVG9rZW4iLCJVc2VySWQiOiIzODc3NjUiLCJVc2VyTmFtZSI6Ijk1OTc4NTkyNTMyMyIsIlVzZXJQaG90byI6IjEiLCJOaWNrTmFtZSI6Ik1lbWJlck5OR1FDREFSIiwiQW1vdW50IjoiMzk0Ni4zNCIsIkludGVncmFsIjoiMCIsIkxvZ2luTWFyayI6Ikg1IiwiTG9naW5UaW1lIjoiMTAvMTAvMjAyNiA4OjEzOjQ0IFBNIiwiTG9naW5JUEFkZHJlc3MiOiIyNy4xMzAuMTY5LjE2IiwiRGJOdW1iZXIiOiIwIiwiSXN2YWxpZGF0b3IiOiIwIiwiS2V5Q29kZSI6IjI1NSIsIlRva2VuVHlwZSI6IkFjY2Vzc19Ub2tlbiIsIlBob25lVHlwZSI6IjEiLCJVc2VyVHlwZSI6IjAiLCJVc2VyTmFtZTIiOiIiLCJpc3MiOiJqd3RJc3N1ZXIiOiJhdWQiOiJsb3R0ZXJ5VGlja2V0In0.IUMgb7VsDkGelJ08vzwmjftvYtOuA7uSQafKHdldyFQ",
                "ar-origin": "https://cklottery.cc",
                "origin": "https://cklottery.cc",
                "referer": "https://cklottery.cc/",
                "user-agent": "Mozilla/5.0 (Linux; Android 10)"
            }
        });

        let data = response.data;
        if (data && data.code === 0 && data.data && data.data.list) {
            await setDoc(doc(db, "wingo_data", "latest_results"), {
                list: data.data.list,
                updatedAt: new Date().toISOString()
            });
            console.log("Data successfully updated to Firebase!");
        } else {
            console.log("Server response error:", data);
        }
    } catch (error) {
        console.error("Error fetching data:", error.message);
    }
}

// Pehli baar run hoga
fetchAndSaveData();

// Har 5 second mein repeat hoga
setInterval(fetchAndSaveData, 5000);
console.log("WinGo Background Worker Started...");
