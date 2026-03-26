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

new-gen-box/ ├── server.js ├── .env ├── public/ ├── routes/ ├── controllers/ ├── sockets/ ├── assets/

---

## ✨ Features

### 🔐 Authentication
- Email & Password login  
- Strong password validation  
- Password visibility toggle  
- OTP verification  

---

### 🔢 OTP System
- 6-digit OTP  
- Auto-trigger after login  
- Fallback → OTP shown in terminal  

---

### 💬 Real-Time Chat (Socket.IO)
- Instant messaging  
- Text, images, videos, files  
- Reply, Copy, React, Delete  

---

### 👥 Contacts
- Add users via NGB UID (e.g. `ngb00000001`)  
- Auto-fetch user data  

---

### 📎 Extras
- Profile system  
- Block users  
- Clear chat  

---

## 🧠 Requirements

- Python 3.x  
- Node.js  
- Internet connection  

---

## 👨‍💻 Author

**Hussain**

---

## ⭐ Support

- Star ⭐ the repo  
- Fork 🍴  
- Contribute 🛠  

---

# ⚙️ Setup & Run (Commands)

## 📥 1. Clone Repository

### 🔗 HTTPS
```bash
git clone https://github.com/hs2463296-debug/Hope-web-.git

🔐 SSH

git clone git@github.com:hs2463296-debug/Hope-web-.git

💻 GitHub CLI

gh repo clone hs2463296-debug/Hope-web-


---

📂 2. Move Into Project

cd Hope-web-


---

▶️ 3. Run Setup Script

python3 setup_newgenbox.py


---

📂 4. Enter Generated Folder

cd new-gen-box


---

⚙️ 5. Configure Environment

nano .env

Add:

EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password
JWT_SECRET=your_secure_random_string


---

🚀 6. Start Server

node server.js


---

🌐 7. Open Application

http://localhost:3000

