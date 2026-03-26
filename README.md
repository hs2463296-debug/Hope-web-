# 🚀 NewGenBox — Fully Automated Project Generator

NewGenBox is a powerful **Python-based automation script** that generates a complete chat application from scratch.

> ⚡ Just run one script — everything (packages, backend, frontend, Socket.IO, structure) is created automatically.

---

## 📥 Clone Repository

Choose any method:

### 🔗 HTTPS
```bash
git clone https://github.com/hs2463296-debug/Hope-web-.git

🔐 SSH

git clone git@github.com:hs2463296-debug/Hope-web-.git

💻 GitHub CLI

gh repo clone hs2463296-debug/Hope-web-


---

📂 Move Into Project

cd Hope-web-


---

⚙️ Run Setup Script

python3 setup_newgenbox.py


---

🤖 What Happens Automatically

After running the script:

📦 All required packages are installed

🌐 Node.js project is initialized

🔌 Socket.IO is fully configured

📁 Complete folder & file structure is generated

🔐 Authentication system (Login + OTP) is created

💬 Chat system (real-time messaging) is ready



---

📁 Generated Project

new-gen-box/
├── server.js
├── .env
├── public/
├── routes/
├── controllers/
├── sockets/
├── assets/


---

🛠 Final Setup (Manual Step)

📂 Enter Generated Folder

cd new-gen-box


---

⚙️ Configure Environment

nano .env

Add your credentials:

EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password
JWT_SECRET=your_secure_random_string


---

▶️ Start Server

node server.js


---

🌐 Open Application

http://localhost:3000


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

Fallback → OTP shown in terminal if email fails



---

💬 Real-Time Chat (Socket.IO)

Instant messaging

Send text, images, videos, files

Message actions: Reply, Copy, React, Delete



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

⚡ Why This Project?

✅ No manual setup

✅ No dependency issues

✅ Fully automated

✅ Beginner-friendly

✅ Ready-to-use chat system



---

👨‍💻 Author

Hussain


---

⭐ Support

Star ⭐ the repo

Fork 🍴

Contribute 🛠



---

🚀 Future Plans

Mobile app

Cloud deployment

End-to-end encryption

UI improvements

