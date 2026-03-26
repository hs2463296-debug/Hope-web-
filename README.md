# 🚀 NewGenBox — Fully Automated Project Generator

NewGenBox is a powerful **Python-based automation script** that generates a complete chat application from scratch.

With just one command, it will:
- Install all required dependencies
- Configure backend & frontend
- Setup Socket.IO for real-time communication
- Generate full project structure (files + folders)
- Deliver a ready-to-run application

> ⚡ No manual setup required — just run the script and your project is ready.

---

## 🔥 What This Script Does

This is not just a setup script — it is a **full project generator**.

### ✅ Automatic Setup Includes:
- 📦 Auto-installation of all required packages
- 🌐 Node.js project initialization
- 🔌 Socket.IO setup (real-time chat)
- 📁 Complete folder & file structure generation
- 🔐 Authentication system (Login + OTP)
- 💬 Chat system with media support
- ⚙️ Environment configuration (.env)

---

## ✨ Features

### 🔐 Authentication
- Email + Password login
- Strong password validation
- Password visibility toggle
- OTP verification system

---

### 🔢 OTP System
- 6-digit secure OTP
- Auto-trigger after login
- Fallback:
  - If email fails → OTP shown in terminal

---

### 💬 Real-Time Chat (Socket.IO)
- Instant messaging
- Send:
  - Text
  - Images
  - Videos
  - Files
- Message actions:
  - Reply
  - Copy
  - React
  - Delete

---

### 👥 Contacts System
- Add users via NGB UID (e.g. `ngb00000001`)
- Auto-fetch user data
- Fast contact management

---

### 📎 Extra Features
- Profile system
- Block users
- Clear chat history

---

## ⚙️ How It Works

### 1️⃣ Run the Script

```bash
python3 setup_newgenbox.py
2️⃣ Script Automatically:
Installs dependencies (Node.js packages, etc.)
Creates project folder:

new-gen-box/
Generates all required files:
server.js
routes
controllers
frontend files
Configures Socket.IO
Sets up authentication system
3️⃣ Final Step (Manual Config)
Bash
cd new-gen-box
nano .env
Add:

EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password
JWT_SECRET=your_secure_key
4️⃣ Start Server
Bash
node server.js
5️⃣ Open App

http://localhost:3000
📁 Generated Project Structure

new-gen-box/
├── server.js
├── .env
├── public/
├── routes/
├── controllers/
├── sockets/
├── assets/
🧠 Requirements
Python 3.x
Node.js (recommended)
Internet connection (for auto package installation)
⚡ Why Use NewGenBox?
❌ No manual coding required
❌ No dependency issues
❌ No complex setup
✅ Fully automated system
✅ Beginner-friendly
✅ Ready-to-use project
👨‍💻 Author
Hussain
⭐ Support
If you like this project:
Star ⭐ the repository
Share with others
Contribute improvements
