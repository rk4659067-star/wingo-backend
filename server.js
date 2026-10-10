const puppeteer = require('puppeteer');
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

async function scrapeAndSaveData() {
    console.log("Launching browser...");
    let browser;
    try {
        // Render ke Linux environment ke liye necessary args
        browser = await puppeteer.launch({
            headless: true,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu'
            ]
        });

        const page = await browser.newPage();
        
        // Mobile user-agent set karte hain taaki site mobile version load kare
        await page.setUserAgent("Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36");

        console.log("Opening game website...");
        // Game ki main URL jahan se session/signature banta hai
        await page.goto('https://cklottery.cc/#/home/CosmicWingo', { waitUntil: 'networkidle2', timeout: 60000 });

        // Thoda wait karte hain taaki page fully load ho jaye aur API request trigger ho
        await new Promise(resolve => setTimeout(resolve, 5000));

        // Browser ke andar se hi API call intercept karke data nikal lenge ya direct fetch execute karenge
        const result = await page.evaluate(async () => {
            try {
                // Browser ke context mein fetch request chalayenge jiske paas saare valid cookies aur signatures honge
                const response = await fetch("https://ckygjf6r.com/api/webapi/GetNoaverageEmerdList", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        pageSize: 10,
                        pageNo: 1,
                        typeId: 30,
                        language: 7
                    })
                });
                return await response.json();
            } catch (err) {
                return { error: err.message };
            }
        });

        if (result && result.code === 0 && result.data && result.data.list) {
            await setDoc(doc(db, "wingo_data", "latest_results"), {
                list: result.data.list,
                updatedAt: new Date().toISOString()
            });
            console.log("Data successfully scraped and updated to Firebase!");
        } else {
            console.log("Scraping response error:", result);
        }

        await browser.close();
    } catch (error) {
        console.error("Puppeteer Error:", error.message);
        if (browser) {
            await browser.close();
        }
    }
}

// Pehli baar run hoga
scrapeAndSaveData();

// Har 10 second mein repeat hoga
setInterval(scrapeAndSaveData, 10000);
console.log("WinGo Puppeteer 24/7 Worker Started...");
