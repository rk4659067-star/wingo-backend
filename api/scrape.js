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

export default async function handler(req, res) {
    try {
        const client = axios.create({
            headers: {
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Referer": "https://cklottery.cc/",
                "Origin": "https://cklottery.cc"
            }
        });

        // Main site se session handshake
        const homeResponse = await client.get('https://cklottery.cc/', { maxRedirects: 5 });
        const cookies = homeResponse.headers['set-cookie'];
        const cookieHeader = cookies ? cookies.join('; ') : '';

        // API request to fetch data
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
            return res.status(200).json({ success: true, message: "Data updated to Firebase successfully!" });
        } else {
            return res.status(400).json({ success: false, error: data });
        }
    } catch (error) {
        return res.status(500).json({ success: false, error: error.message });
    }
}
