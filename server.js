const axios = require('axios');
const { initializeApp } = require('firebase/app');
const { getFirestore, doc, setDoc } = require('firebase/firestore');

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

// Axios client with mobile headers simulation
const client = axios.create({
    headers: {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://cklottery.cc/",
        "Origin": "https://cklottery.cc"
    }
});

async function fetchAndSaveData() {
    try {
        // Step 1: Main site se session / cookies handshake karte hain
        const homeResponse = await client.get('https://cklottery.cc/', { maxRedirects: 5 });
        const cookies = homeResponse.headers['set-cookie'];
        const cookieHeader = cookies ? cookies.join('; ') : '';

        // Step 2: Live data API ko valid session cookies ke sath request bhejte hain
        const url = "https://ckygjf6r.com/api/webapi/GetNoaverageEmerdList";
        
        const payload = {
            pageSize: 10,
            pageNo: 1,
            typeId: 30,
            language: 7
        };

        const response = await client.post(url, payload, {
            headers: {
                "Content-Type": "application/json",
                "Cookie": cookieHeader,
                "ar-origin": "https://cklottery.cc"
            }
        });

        let data = response.data;
        if (data && data.code === 0 && data.data && data.data.list) {
            await setDoc(doc(db, "wingo_data", "latest_results"), {
                list: data.data.list,
                updatedAt: new Date().toISOString()
            });
            console.log("Data successfully fetched via HTTP session & updated to Firebase!");
        } else {
            console.log("Server response error:", data);
        }
    } catch (error) {
        console.error("HTTP Fetch Error:", error.message);
        if (error.response) {
            console.error("Status code:", error.response.status);
        }
    }
}

// Pehli baar run hoga
fetchAndSaveData();

// Har 10 second mein repeat hoga
setInterval(fetchAndSaveData, 10000);
console.log("WinGo HTTP Proxy Worker Started...");
