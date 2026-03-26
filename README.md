

# 🚀 NewGenBox — Fully Automated Project Generator

NewGenBox is a powerful **Python automation script** that generates a complete, production-ready chat application.

> ⚡ One command → full backend + frontend + real-time chat system ready.

---

## 🤖 What This Script Does

This is not just a setup script — it is a **complete project generator**.

### ✅ Automatically:

- 📦 Installs all required npm packages  
- 🌐 Sets up Node.js backend  
- 🔌 Configures Socket.IO (real-time chat)  
- 📁 Generates full project structure  
- 🔐 Builds authentication system (Login + OTP)  
- 💬 Creates real-time chat system  
- ⚙️ Generates `.env` configuration  

---

## 🧪 Real Setup Output (Proof)

When you run the script:

```bash
python3 setup_newgenbox.py

You will see:

✓ server.js
✓ models/User.js
✓ controllers/authController.js
✓ routes/message.js
✓ socket/socketHandlers.js
✓ public/index.html
...

Then:

✅ npm install complete!
✅ SETUP COMPLETE!


---

📁 Generated Project Structure

new-gen-box/
├── server.js
├── package.json
├── .env
├── config/
├── controllers/
├── middleware/
├── models/
├── routes/
├── socket/
├── database/
├── utils/
├── public/
├── logs/


---

✨ Features

🔐 Authentication

Email & Password login

Strong password validation

Password visibility toggle

OTP verification



---

🔢 OTP System

6-digit OTP

Auto-trigger after login

Fallback → OTP shown in terminal



---

💬 Real-Time Chat (Socket.IO)

Instant messaging

Send text, images, videos, files

Reply, Copy, React, Delete



---

👥 Contacts

Add users via NGB UID (e.g. ngb00000001)

Auto-fetch user data



---

📎 Extras

Profile system

Block users

Clear chat



---

🧠 Requirements

Python 3.x

Node.js

Internet connection



---

👨‍💻 Author

Hussain


---

⭐ Support

Star ⭐ the repo

Fork 🍴

Contribute 🛠



---

⚙️ Setup & Run (Commands)

📥 1. Clone Repository

🔗 HTTPS
```bash
git clone https://github.com/hs2463296-debug/Hope-web-.git

🔐 SSH
```bash
git clone git@github.com:hs2463296-debug/Hope-web-.git

💻 GitHub CLI
```bash
gh repo clone hs2463296-debug/Hope-web-


---

📂 2. Enter Project
```bash
cd Hope-web-


---

▶️ 3. Run Setup Script
```bash
python3 setup_newgenbox.py


---

📂 4. Open Generated Project
```bash
cd new-gen-box


---

⚙️ 5. Configure Environment
```bash
nano .env

Add:

EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password
JWT_SECRET=your_secure_random_string


---

🚀 6. Start Server
```bash
node server.js


---

🌐 7. Open in Browser
```bash
http://localhost:3000


---

⚠️ Notes

OTP will always work

If email fails → shown in terminal


First run may take time (npm install)

Internet required for package installation



---

🚀 Future Plans

Mobile app version

Cloud deployment

End-to-end encryption

Advanced UI

