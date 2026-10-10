const axios = require('axios');
const { initializeApp } = require('firebase/app');
const { getFirestore, doc, setDoc } = require('firebase/firestore');

// Apna Firebase configuration yahan dalein
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
    
    // 30s ya 1m ka payload
    const payload = {
        pageSize: 10,
        pageNo: 1,
        typeId: 30,  // 30s ke liye
        language: 7,
        random: "1f6d74756f024a74891dd1d4a9db6720",
        signature: "030503A5B0C2FF81B0D3E536EA272C93",
        timestamp: Date.now()
    };

    try {
        let response = await axios.post(url, payload, {
            headers: {
                "Content-Type": "application/json",
                "authorization": "Bearer APNA_JWT_TOKEN_YAHAN_DAALEIN",
                "origin": "https://cklottery.cc",
                "referer": "https://cklottery.cc/",
                "user-agent": "Mozilla/5.0 (Linux; Android 10)"
            }
        });

        let data = response.data;
        if (data && data.code === 0 && data.data && data.data.list) {
            // Firestore database mein latest data save kar rahe hain
            await setDoc(doc(db, "wingo_data", "latest_results"), {
                list: data.data.list,
                updatedAt: new Date().toISOString()
            });
            console.log("Data successfully updated to Firebase!");
        }
    } catch (error) {
        console.error("Error fetching data:", error.message);
    }
}

// Har 5 second mein background mein run hoga
setInterval(fetchAndSaveData, 5000);
console.log("WinGo Background Worker Started...");
