# 🚀 NewGenBox — Fully Automated Project Generator

NewGenBox is a powerful **Python automation script** that creates a complete chat application from scratch.

> ⚡ Just run one script — everything is automatically installed, configured, and generated.

---

## 🤖 What This Script Does

This script is a **full project generator**, not just a setup tool.

### ✅ It Automatically:

- 📦 Installs all required packages  
- 🌐 Sets up Node.js backend  
- 🔌 Configures Socket.IO (real-time chat)  
- 📁 Generates complete folder & file structure  
- 🔐 Creates authentication system (Login + OTP)  
- 💬 Builds real-time chat system  
- ⚙️ Creates `.env` configuration  

---

## 📁 Generated Project Structure
```
new-gen-box/
├── server.js
├── package.json
├── package-lock.json
├── .env
├── README.md
│
├── config/
│   └── config.js
│
├── controllers/
│   ├── authController.js
│   ├── userController.js
│   ├── messageController.js
│   └── contactController.js
│
├── middleware/
│   ├── auth.js
│   ├── rateLimit.js
│   └── upload.js
│
├── models/
│   ├── db.js
│   ├── Counter.js
│   ├── User.js
│   ├── Message.js
│   └── OTP.js
│
├── routes/
│   ├── auth.js
│   ├── user.js
│   ├── message.js
│   └── contact.js
│
├── socket/
│   └── socketHandlers.js
│
├── utils/
│   ├── logger.js
│   ├── encryption.js
│   ├── emailService.js
│   └── validators.js
│
├── database/
│   └── db.json
│
├── public/
│   ├── index.html
│   ├── manifest.json
│   ├── service-worker.js
│   │
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       ├── main.js
│       ├── auth.js
│       ├── socket.js
│       ├── chat.js
│       ├── chatList.js
│       ├── contacts.js
│       ├── profile.js
│       ├── mediaViewer.js
│       ├── storage.js
│       └── utils.js
│
└── logs/
```
---

⚙️ Setup & Run (Step-by-Step)

📥 1. Clone Repository

🔗 HTTPS
```bash
git clone https://github.com/hs2463296-debug/Hope-web-.git
```


🔐 SSH
```bash
git clone git@github.com:hs2463296-debug/Hope-web-.git
```


💻 GitHub CLI
```bash
gh repo clone hs2463296-debug/Hope-web-
```

---

📂 2. Move Into Project
```bash
cd Hope-web-
```

---

▶️ 3. Run Setup Script
```bash
python3 setup_newgenbox.py
```

---

📂 4. Enter Generated Folder
```bash
cd new-gen-box
```

---

⚙️ 5. Configure Environment
```bash
nano .env
```
Add:

EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password
JWT_SECRET=your_secure_random_string


---

🚀 6. Start Server
```bash
node server.js
```

---

🌐 7. Open Application
```bash
http://localhost:3000
```

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

Text, images, videos, files

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
