#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║           NEW GEN BOX v2.0 — COMPLETE SETUP SCRIPT                 ║
║                                                                      ║
║  USAGE:   python3 setup_newgenbox.py                                ║
║                                                                      ║
║  Creates: new-gen-box/ folder with ALL files + npm install          ║
║                                                                      ║
║  FEATURES:                                                           ║
║  ✅ OTP Login/Register (shows in terminal if email not configured)  ║
║  ✅ OTP screen appears correctly in browser                         ║
║  ✅ Real-time chat (Socket.IO)                                      ║
║  ✅ File sharing (photo/video/doc)                                  ║
║  ✅ Media viewer (fullscreen, zoomable)                             ║
║  ✅ Contact management by NGB UID (ngbXXXXXXXX)                    ║
║  ✅ Typing indicators + online/offline                              ║
║  ✅ Message ticks ✓ ✓✓ (blue = read)                               ║
║  ✅ Profile edit (name, bio, emoji, availability)                   ║
║  ✅ Dark mode                                                        ║
║  ✅ PWA (installable on phone)                                      ║
║  ✅ Security (Helmet, bcrypt, JWT, rate limiting, OTP)              ║
╚══════════════════════════════════════════════════════════════════════╝
"""
import os, sys, json, subprocess

PROJECT = "new-gen-box"

def w(path, content):
    full = os.path.join(PROJECT, path)
    os.makedirs(os.path.dirname(full) or '.', exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✓  {path}")



FILES = {}

FILES[".env"] = """\
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_gmail_app_password
JWT_SECRET=change_this_to_64_char_random_string_abcdef1234567890abcdef1234567890
PORT=3000
NODE_ENV=development
OTP_EXPIRY_MS=300000
OTP_RESEND_COOLDOWN_MS=30000
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_MS=300000
"""

FILES["package.json"] = """\
{
  "name": "new-gen-box",
  "version": "2.0.0",
  "description": "New Gen Box - Secure Real-Time Chat App",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js"
  },
  "dependencies": {
    "bcryptjs": "^2.4.3",
    "compression": "^1.7.4",
    "cors": "^2.8.5",
    "dotenv": "^16.0.3",
    "express": "^4.18.2",
    "express-rate-limit": "^6.7.0",
    "helmet": "^7.0.0",
    "jsonwebtoken": "^9.0.0",
    "lowdb": "^1.0.0",
    "multer": "^1.4.5-lts.1",
    "nodemailer": "^6.9.3",
    "socket.io": "^4.6.1",
    "validator": "^13.9.0",
    "winston": "^3.9.0",
    "uuid": "^9.0.0",
    "morgan": "^1.10.0"
  },
  "devDependencies": { "nodemon": "^3.0.1" }
}
"""

FILES["server.js"] = """\
'use strict';
require('dotenv').config();
const express     = require('express');
const http        = require('http');
const { Server }  = require('socket.io');
const helmet      = require('helmet');
const cors        = require('cors');
const compression = require('compression');
const morgan      = require('morgan');
const path        = require('path');
const fs          = require('fs');

const authRoutes    = require('./routes/auth');
const userRoutes    = require('./routes/user');
const messageRoutes = require('./routes/message');
const contactRoutes = require('./routes/contact');
const { initSocket }    = require('./socket/socketHandlers');
const { globalLimiter } = require('./middleware/rateLimit');

const app    = express();
const server = http.createServer(app);
const io     = new Server(server, {
  cors: { origin: '*', methods: ['GET','POST','PUT','DELETE'] },
  pingTimeout: 60000, pingInterval: 25000,
  maxHttpBufferSize: 50e6,
  transports: ['websocket','polling'],
});

['public/uploads','logs','database'].forEach(d => {
  if (!fs.existsSync(d)) fs.mkdirSync(d, { recursive: true });
});

app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc:  ["'self'","'unsafe-inline'","https://cdn.socket.io"],
      styleSrc:   ["'self'","'unsafe-inline'"],
      imgSrc:     ["'self'","data:","blob:"],
      connectSrc: ["'self'","ws:","wss:"],
      mediaSrc:   ["'self'","blob:"],
    }
  },
  crossOriginEmbedderPolicy: false,
}));

app.use(compression());
app.use(cors({ origin: '*' }));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));
app.use(globalLimiter);
if (process.env.NODE_ENV !== 'production') app.use(morgan('dev'));

app.use(express.static(path.join(__dirname, 'public'), { maxAge: '1d' }));

app.use('/api/auth',     authRoutes);
app.use('/api/users',    userRoutes);
app.use('/api/messages', messageRoutes);
app.use('/api/contacts', contactRoutes);

app.get('/api/health', (req, res) => res.json({
  status: 'ok', version: '2.0.0',
  uptime: Math.floor(process.uptime()),
  timestamp: new Date().toISOString()
}));

app.use((req, res) => res.status(404).json({ error: 'Not found' }));
app.use((err, req, res, next) => {
  console.error('[ERR]', err.message);
  res.status(err.status || 500).json({ error: err.message || 'Server error' });
});

initSocket(io);

const PORT = process.env.PORT || 3000;
server.listen(PORT, '0.0.0.0', () => {
  try {
    const os = require('os');
    let ip = 'localhost';
    Object.values(os.networkInterfaces()).flat().forEach(i => {
      if (i && i.family === 'IPv4' && !i.internal) ip = i.address;
    });
    console.log('\\n╔══════════════════════════════════════╗');
    console.log('║   NEW GEN BOX v2.0 — RUNNING!        ║');
    console.log('╚══════════════════════════════════════╝');
    console.log('  Local:   http://localhost:' + PORT);
    console.log('  Network: http://' + ip + ':' + PORT + '\\n');
  } catch(e) { console.log('Running on port ' + PORT); }
});
module.exports = { app, server, io };
"""

FILES["config/config.js"] = """\
'use strict';
module.exports = {
  JWT_SECRET:          process.env.JWT_SECRET || 'dev_secret_CHANGE_THIS',
  JWT_EXPIRES:         '7d',
  REFRESH_EXPIRES:     '30d',
  OTP_EXPIRY_MS:       parseInt(process.env.OTP_EXPIRY_MS)          || 300000,
  OTP_RESEND_COOLDOWN: parseInt(process.env.OTP_RESEND_COOLDOWN_MS) || 30000,
  MAX_LOGIN_ATTEMPTS:  parseInt(process.env.MAX_LOGIN_ATTEMPTS)      || 5,
  LOCKOUT_MS:          parseInt(process.env.LOCKOUT_MS)              || 300000,
  UPLOAD_DIR:          'public/uploads',
  MAX_FILE_SIZE:       50 * 1024 * 1024,
  MSG_PAGE_SIZE:       50,
};
"""

FILES["models/db.js"] = """\
'use strict';
const low      = require('lowdb');
const FileSync = require('lowdb/adapters/FileSync');
const path     = require('path');

const db = low(new FileSync(path.join(__dirname, '../database/db.json')));
db.defaults({
  users: [], messages: [], otps: [],
  counter: { lastUid: 0 },
}).write();
module.exports = { db };
"""

FILES["models/Counter.js"] = """\
'use strict';
const { db } = require('./db');
class Counter {
  static nextUid() {
    const n = (db.get('counter.lastUid').value() || 0) + 1;
    db.set('counter.lastUid', n).write();
    return 'ngb' + String(n).padStart(8, '0');
  }
}
module.exports = Counter;
"""

FILES["models/User.js"] = """\
'use strict';
const { db } = require('./db');
class User {
  static findByEmail(email)   { return db.get('users').find({ email }).value(); }
  static findByUid(uid)       { return db.get('users').find({ uid }).value(); }
  static create(data)         { db.get('users').push(data).write(); return data; }
  static update(uid, updates) { db.get('users').find({ uid }).assign(updates).write(); return User.findByUid(uid); }
  static delete(uid)          { db.get('users').remove({ uid }).write(); }
  static count()              { return db.get('users').size().value(); }
  static search(q, limit=20) {
    const lq = q.toLowerCase();
    return db.get('users')
      .filter(u => u.name.toLowerCase().includes(lq) || u.uid.includes(lq))
      .take(limit).value()
      .map(({ passwordHash, ...safe }) => safe);
  }
  static safe(uid) {
    const u = User.findByUid(uid);
    if (!u) return null;
    const { passwordHash, ...safe } = u;
    return safe;
  }
}
module.exports = User;
"""

FILES["models/Message.js"] = """\
'use strict';
const { db } = require('./db');
class Message {
  static create(data) { db.get('messages').push(data).write(); return data; }
  static findById(id) { return db.get('messages').find({ id }).value(); }
  static update(id, updates) { db.get('messages').find({ id }).assign(updates).write(); }
  static getConversation(uid1, uid2, before=null, limit=50) {
    let q = db.get('messages').filter(m =>
      (m.from===uid1&&m.to===uid2)||(m.from===uid2&&m.to===uid1)
    );
    if (before) q = q.filter(m => m.timestamp < before);
    return q.sortBy('timestamp').takeRight(limit).value();
  }
  static markRead(fromUid, toUid) {
    db.get('messages')
      .filter(m => m.from===fromUid && m.to===toUid && m.status!=='read')
      .each(m => { m.status = 'read'; }).write();
  }
  static unreadCount(fromUid, toUid) {
    return db.get('messages')
      .filter(m => m.from===fromUid && m.to===toUid && m.status!=='read' && !m.deleted)
      .size().value();
  }
  static lastMsg(uid1, uid2) {
    return db.get('messages')
      .filter(m => (m.from===uid1&&m.to===uid2)||(m.from===uid2&&m.to===uid1))
      .sortBy('timestamp').last().value();
  }
  static deleteConvo(uid1, uid2) {
    db.get('messages').remove(m =>
      (m.from===uid1&&m.to===uid2)||(m.from===uid2&&m.to===uid1)
    ).write();
  }
  static deleteForMe(id, uid) {
    const m = Message.findById(id);
    if (!m) return;
    const df = [...(m.deletedFor||[])];
    if (!df.includes(uid)) { df.push(uid); Message.update(id, { deletedFor: df }); }
  }
  static deleteForAll(id) {
    Message.update(id, { deleted:true, text:'', fileUrl:null });
  }
  static react(id, uid, emoji) {
    const m = Message.findById(id);
    if (!m) return {};
    const r = { ...(m.reactions||{}) };
    if (!r[emoji]) r[emoji] = [];
    const i = r[emoji].indexOf(uid);
    if (i===-1) r[emoji].push(uid); else r[emoji].splice(i,1);
    if (!r[emoji].length) delete r[emoji];
    Message.update(id, { reactions: r });
    return r;
  }
}
module.exports = Message;
"""

FILES["models/OTP.js"] = """\
'use strict';
const { db } = require('./db');
class OTP {
  static set(email, otp, data, expiresAt) {
    db.get('otps').remove({ email }).write();
    db.get('otps').push({ email, otp, data:data||{}, expiresAt, sentAt:Date.now(), attempts:0 }).write();
    console.log('[OTP] Saved → ' + email + ' : ' + otp);
  }
  static get(email)  { return db.get('otps').find({ email }).value(); }
  static inc(email)  {
    const o = OTP.get(email);
    if (o) db.get('otps').find({ email }).assign({ attempts:(o.attempts||0)+1 }).write();
  }
  static del(email)  { db.get('otps').remove({ email }).write(); }
  static cleanup()   { db.get('otps').remove(o => Date.now() > o.expiresAt).write(); }
}
module.exports = OTP;
"""

FILES["utils/logger.js"] = """\
'use strict';
const winston = require('winston');
const fs      = require('fs');
if (!fs.existsSync('logs')) fs.mkdirSync('logs', { recursive: true });
const logger = winston.createLogger({
  level: process.env.NODE_ENV==='production' ? 'warn' : 'debug',
  format: winston.format.combine(
    winston.format.timestamp({ format:'YYYY-MM-DD HH:mm:ss' }),
    winston.format.colorize(),
    winston.format.printf(({ timestamp,level,message }) => `[${timestamp}] ${level}: ${message}`)
  ),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename:'logs/error.log', level:'error', maxsize:5242880, maxFiles:3 }),
    new winston.transports.File({ filename:'logs/app.log', maxsize:10485760, maxFiles:5 }),
  ]
});
module.exports = logger;
"""

FILES["utils/encryption.js"] = """\
'use strict';
const bcrypt = require('bcryptjs');
const jwt    = require('jsonwebtoken');
const crypto = require('crypto');
const { JWT_SECRET, JWT_EXPIRES } = require('../config/config');

const hashPw    = pw   => bcrypt.hash(pw, 12);
const comparePw = (pw,h) => bcrypt.compare(pw, h);
const genToken  = payload => jwt.sign(payload, JWT_SECRET, { expiresIn: JWT_EXPIRES, issuer:'ngb' });
const verToken  = token   => jwt.verify(token, JWT_SECRET, { issuer:'ngb' });
const genOTP    = ()  => crypto.randomInt(100000,999999).toString();
const genId     = (p='id') => p+'_'+Date.now()+'_'+crypto.randomBytes(4).toString('hex');

module.exports = { hashPw, comparePw, genToken, verToken, genOTP, genId };
"""

FILES["utils/emailService.js"] = """\
'use strict';
const nodemailer = require('nodemailer');

let _t = null;
function trans() {
  if (!_t) _t = nodemailer.createTransport({
    service: 'gmail',
    auth: { user: process.env.EMAIL_USER, pass: process.env.EMAIL_PASS },
    tls: { rejectUnauthorized: false },
  });
  return _t;
}

async function sendOTP(email, otp, type='login') {
  // ★ ALWAYS show in console ★
  console.log('\\n' + '★'.repeat(45));
  console.log('  OTP FOR  : ' + email);
  console.log('  OTP CODE : ' + otp);
  console.log('  TYPE     : ' + type);
  console.log('★'.repeat(45) + '\\n');

  if (!process.env.EMAIL_USER || process.env.EMAIL_USER === 'your_email@gmail.com') {
    console.log('[EMAIL] Not configured — use OTP from console\\n');
    return;
  }
  try {
    await trans().sendMail({
      from: '"New Gen Box 💬" <' + process.env.EMAIL_USER + '>',
      to: email,
      subject: otp + ' — New Gen Box OTP',
      html: '<div style="font-family:Arial;background:#000;color:#fff;padding:32px;border-radius:16px;max-width:400px;margin:40px auto;text-align:center"><h2 style="margin:0 0 16px">💬 New Gen Box</h2><p style="color:#aaa;margin:0 0 12px">Your OTP:</p><div style="font-size:44px;font-weight:900;letter-spacing:12px;font-family:monospace">'+otp+'</div><p style="color:#666;margin:16px 0 0;font-size:13px">Valid 5 min · Do not share</p></div>',
      text: 'New Gen Box OTP: ' + otp + '\\nValid 5 minutes.',
    });
    console.log('[EMAIL] ✅ Sent to ' + email);
  } catch(e) {
    console.error('[EMAIL] ❌ Failed:', e.message);
    console.log('[EMAIL] 👆 Use OTP from console above!\\n');
  }
}

async function sendWelcome(email, name, uid) {
  if (!process.env.EMAIL_USER || process.env.EMAIL_USER === 'your_email@gmail.com') return;
  try {
    await trans().sendMail({
      from: '"New Gen Box 💬" <' + process.env.EMAIL_USER + '>',
      to: email,
      subject: 'Welcome to New Gen Box! 🎉',
      text: 'Hi ' + name + '!\\nYour NGB ID: ' + uid + '\\nShare it with friends to chat!',
    });
  } catch {}
}

module.exports = { sendOTP, sendWelcome };
"""

FILES["utils/validators.js"] = """\
'use strict';
const validator = require('validator');
const isEmail    = e => typeof e==='string' && validator.isEmail(e.trim());
const isStrongPw = p => p && p.length>=8 && /[A-Z]/.test(p) && /[a-z]/.test(p) && /[0-9]/.test(p);
const sanitize   = (s,max=2000) => typeof s==='string' ? validator.escape(s.trim()).substring(0,max) : '';
const sanitizeRaw= (s,max=5000) => typeof s==='string' ? s.trim().substring(0,max) : '';
module.exports = { isEmail, isStrongPw, sanitize, sanitizeRaw };
"""

FILES["middleware/auth.js"] = """\
'use strict';
const { verToken } = require('../utils/encryption');
function auth(req, res, next) {
  const h = req.headers.authorization;
  if (!h || !h.startsWith('Bearer '))
    return res.status(401).json({ error: 'Login required' });
  try { req.user = verToken(h.slice(7)); next(); }
  catch { res.status(401).json({ error: 'Session expired. Login again.' }); }
}
module.exports = { auth };
"""

FILES["middleware/rateLimit.js"] = """\
'use strict';
const rateLimit = require('express-rate-limit');
const mk = (max, windowMs, msg) => rateLimit({
  windowMs, max,
  message: { error: msg },
  standardHeaders: true, legacyHeaders: false,
  skip: req => req.ip==='127.0.0.1'||req.ip==='::1',
});
module.exports = {
  globalLimiter:  mk(500,  15*60000, 'Too many requests'),
  authLimiter:    mk(20,   15*60000, 'Too many auth attempts'),
  msgLimiter:     mk(100,  60000,    'Message rate limit exceeded'),
  uploadLimiter:  mk(20,   60000,    'Upload rate limit exceeded'),
};
"""

FILES["middleware/upload.js"] = """\
'use strict';
const multer = require('multer');
const path   = require('path');
const fs     = require('fs');
const UPLOAD_DIR = 'public/uploads';
if (!fs.existsSync(UPLOAD_DIR)) fs.mkdirSync(UPLOAD_DIR, { recursive: true });

const storage = multer.diskStorage({
  destination: (req,file,cb) => cb(null, UPLOAD_DIR),
  filename:    (req,file,cb) => {
    const ext  = path.extname(file.originalname).toLowerCase().replace(/[^.a-z0-9]/g,'');
    const name = path.basename(file.originalname,ext).replace(/[^a-zA-Z0-9._-]/g,'_').substring(0,40);
    cb(null, Date.now()+'_'+Math.random().toString(36).slice(2,7)+'_'+name+ext);
  }
});

module.exports = multer({
  storage,
  limits: { fileSize: 50*1024*1024, files: 5 },
  fileFilter: (req,file,cb) => {
    const allowed = new Set(['image/jpeg','image/png','image/gif','image/webp',
      'video/mp4','video/webm','video/quicktime',
      'audio/mpeg','audio/ogg','audio/wav','audio/webm',
      'application/pdf','application/zip','text/plain',
      'application/vnd.android.package-archive','application/octet-stream']);
    cb(null, allowed.has(file.mimetype)||file.mimetype.startsWith('image/')||file.mimetype.startsWith('video/')||file.mimetype.startsWith('audio/'));
  }
});
"""

for path_, content in FILES.items():
    w(path_, content)

w("controllers/authController.js", """\
'use strict';
const User    = require('../models/User');
const OTP     = require('../models/OTP');
const Counter = require('../models/Counter');
const { hashPw,comparePw,genToken,genOTP } = require('../utils/encryption');
const { sendOTP, sendWelcome }             = require('../utils/emailService');
const { OTP_EXPIRY_MS,OTP_RESEND_COOLDOWN,MAX_LOGIN_ATTEMPTS,LOCKOUT_MS } = require('../config/config');

const locks = {};
const chkLock = e => {
  const l = locks[e];
  if (!l) return null;
  if (Date.now()<l.until) return 'Locked '+Math.ceil((l.until-Date.now())/1000)+'s';
  delete locks[e]; return null;
};
const recFail = e => {
  if (!locks[e]) locks[e] = { count:0, until:0 };
  locks[e].count++;
  if (locks[e].count>=MAX_LOGIN_ATTEMPTS) { locks[e].until=Date.now()+LOCKOUT_MS; locks[e].count=0; }
};

exports.register = async (req,res) => {
  try {
    const { email,password,name } = req.body;
    if (!email||!password) return res.status(400).json({ error:'Email and password required' });
    const e = email.trim().toLowerCase();
    if (User.findByEmail(e)) return res.status(409).json({ error:'Email already registered. Login instead.' });
    const rec = OTP.get(e);
    if (rec && Date.now()-rec.sentAt < OTP_RESEND_COOLDOWN) {
      const w = Math.ceil((OTP_RESEND_COOLDOWN-(Date.now()-rec.sentAt))/1000);
      return res.status(429).json({ error:'Wait '+w+'s for next OTP' });
    }
    const pwHash = await hashPw(password);
    const otp    = genOTP();
    OTP.set(e, otp, { pwHash, name:(name||'').trim() }, Date.now()+OTP_EXPIRY_MS);
    await sendOTP(e, otp, 'register');
    res.json({ message:'OTP sent! Check email or server console', step:'verify', email:e });
  } catch(err) {
    console.error('[CTRL] register:', err.message);
    res.status(500).json({ error:err.message });
  }
};

exports.verifyRegister = async (req,res) => {
  try {
    const { email,otp } = req.body;
    if (!email||!otp) return res.status(400).json({ error:'Email and OTP required' });
    const e   = email.trim().toLowerCase();
    const rec = OTP.get(e);
    if (!rec)                   return res.status(400).json({ error:'No OTP. Register again.' });
    if (Date.now()>rec.expiresAt) { OTP.del(e); return res.status(400).json({ error:'OTP expired. Register again.' }); }
    OTP.inc(e);
    if ((rec.attempts||0)>=5)   { OTP.del(e); return res.status(400).json({ error:'Too many attempts.' }); }
    if (rec.otp!==String(otp).trim()) return res.status(400).json({ error:'Wrong OTP. Check server console.' });
    const uid  = Counter.nextUid();
    const name = rec.data.name || e.split('@')[0].replace(/[^a-zA-Z0-9_]/g,'_').substring(0,30);
    const user = {
      uid, email:e, passwordHash:rec.data.pwHash, name, emoji:'👤', bio:'',
      status:'available', customStatus:'', contacts:[], blockedUsers:[],
      online:false, lastSeen:new Date().toISOString(),
      createdAt:new Date().toISOString(), role:'user',
      settings:{ notifications:true, sounds:true, readReceipts:true, theme:'light', enterToSend:false },
      loginHistory:[{ ip:req.ip||'?', at:new Date().toISOString() }],
    };
    User.create(user);
    OTP.del(e);
    sendWelcome(e, name, uid).catch(()=>{});
    console.log('[AUTH] ✅ Registered:', uid, e);
    const token = genToken({ uid, email:e });
    const { passwordHash:_, ...safe } = user;
    res.json({ token, uid, name, emoji:'👤', user:safe });
  } catch(err) {
    console.error('[CTRL] verifyRegister:', err.message);
    res.status(500).json({ error:'Server error' });
  }
};

exports.login = async (req,res) => {
  try {
    const { email,password } = req.body;
    if (!email||!password) return res.status(400).json({ error:'Email and password required' });
    const e = email.trim().toLowerCase();
    const lk = chkLock(e);
    if (lk) return res.status(429).json({ error:lk });
    const user = User.findByEmail(e);
    if (!user) { recFail(e); return res.status(401).json({ error:'Invalid email or password' }); }
    const ok = await comparePw(password, user.passwordHash);
    if (!ok) { recFail(e); return res.status(401).json({ error:'Invalid email or password' }); }
    delete locks[e];
    const rec = OTP.get(e);
    if (rec && Date.now()-rec.sentAt<OTP_RESEND_COOLDOWN) {
      const w = Math.ceil((OTP_RESEND_COOLDOWN-(Date.now()-rec.sentAt))/1000);
      return res.status(429).json({ error:'Wait '+w+'s for next OTP' });
    }
    const otp = genOTP();
    OTP.set(e, otp, {}, Date.now()+OTP_EXPIRY_MS);
    await sendOTP(e, otp, 'login');
    res.json({ message:'OTP sent! Check email or server console', step:'verify', email:e });
  } catch(err) {
    console.error('[CTRL] login:', err.message);
    res.status(500).json({ error:'Server error' });
  }
};

exports.verifyLogin = async (req,res) => {
  try {
    const { email,otp } = req.body;
    if (!email||!otp) return res.status(400).json({ error:'Email and OTP required' });
    const e   = email.trim().toLowerCase();
    const rec = OTP.get(e);
    if (!rec)                   return res.status(400).json({ error:'No OTP. Login again.' });
    if (Date.now()>rec.expiresAt) { OTP.del(e); return res.status(400).json({ error:'OTP expired. Login again.' }); }
    OTP.inc(e);
    if ((rec.attempts||0)>=5)   { OTP.del(e); return res.status(400).json({ error:'Too many attempts.' }); }
    if (rec.otp!==String(otp).trim()) return res.status(400).json({ error:'Wrong OTP. Check server console.' });
    OTP.del(e);
    const user = User.findByEmail(e);
    if (!user) return res.status(404).json({ error:'User not found' });
    User.update(user.uid, {
      lastLogin:new Date().toISOString(),
      loginHistory:[...(user.loginHistory||[]).slice(-19),{ ip:req.ip||'?',at:new Date().toISOString() }]
    });
    console.log('[AUTH] ✅ Login:', user.uid, e);
    const token = genToken({ uid:user.uid, email:e });
    const { passwordHash:_, ...safe } = User.findByUid(user.uid);
    res.json({ token, uid:user.uid, name:user.name, emoji:user.emoji, user:safe });
  } catch(err) {
    console.error('[CTRL] verifyLogin:', err.message);
    res.status(500).json({ error:'Server error' });
  }
};

exports.resendOtp = async (req,res) => {
  try {
    const e = (req.body.email||'').trim().toLowerCase();
    if (!e) return res.status(400).json({ error:'Email required' });
    const rec = OTP.get(e);
    if (rec && Date.now()-rec.sentAt<OTP_RESEND_COOLDOWN) {
      const w = Math.ceil((OTP_RESEND_COOLDOWN-(Date.now()-rec.sentAt))/1000);
      return res.status(429).json({ error:'Wait '+w+'s' });
    }
    const otp = genOTP();
    OTP.set(e, otp, rec?.data||{}, Date.now()+OTP_EXPIRY_MS);
    await sendOTP(e, otp);
    res.json({ message:'OTP resent!' });
  } catch(err) { res.status(500).json({ error:err.message }); }
};

exports.logout = (req,res) => res.json({ message:'Logged out' });
""")

w("controllers/userController.js", """\
'use strict';
const User = require('../models/User');
const { comparePw, hashPw } = require('../utils/encryption');
const { sanitize, isStrongPw } = require('../utils/validators');

exports.getMe      = (req,res) => { const u=User.safe(req.user.uid); u?res.json(u):res.status(404).json({error:'Not found'}); };
exports.getProfile = (req,res) => { const u=User.safe(req.params.uid); u?res.json(u):res.status(404).json({error:'Not found'}); };
exports.searchUsers= (req,res) => { const {q}=req.query; if(!q||q.length<2) return res.json([]); res.json(User.search(q,20)); };

exports.updateProfile = (req,res) => {
  const { name,emoji,bio,customStatus,status } = req.body;
  const up = {};
  if (name         !==undefined) up.name         = sanitize(name,50);
  if (emoji        !==undefined) up.emoji        = (emoji||'👤').trim().substring(0,8);
  if (bio          !==undefined) up.bio          = sanitize(bio,300);
  if (customStatus !==undefined) up.customStatus = sanitize(customStatus,60);
  if (status && ['available','away','busy','invisible'].includes(status)) up.status = status;
  User.update(req.user.uid, up);
  res.json({ message:'Profile updated', ...up });
};

exports.changePw = async (req,res) => {
  const { currentPassword,newPassword } = req.body;
  if (!currentPassword||!newPassword) return res.status(400).json({ error:'Both passwords required' });
  const user = User.findByUid(req.user.uid);
  const ok   = await comparePw(currentPassword, user.passwordHash);
  if (!ok) return res.status(401).json({ error:'Current password wrong' });
  if (!isStrongPw(newPassword)) return res.status(400).json({ error:'New password too weak (8+ chars, uppercase, lowercase, number)' });
  User.update(req.user.uid, { passwordHash: await hashPw(newPassword) });
  res.json({ message:'Password changed!' });
};

exports.blockUser = (req,res) => {
  const { uid } = req.body;
  if (!uid||uid===req.user.uid) return res.status(400).json({ error:'Invalid UID' });
  const user    = User.findByUid(req.user.uid);
  const blocked = [...(user.blockedUsers||[])];
  const idx     = blocked.indexOf(uid);
  const action  = idx===-1 ? 'blocked':'unblocked';
  if (idx===-1) blocked.push(uid); else blocked.splice(idx,1);
  User.update(req.user.uid, { blockedUsers:blocked });
  res.json({ message:'User '+action, action });
};

exports.updateSettings = (req,res) => {
  const { settings } = req.body;
  if (!settings||typeof settings!=='object') return res.status(400).json({ error:'Invalid settings' });
  const user = User.findByUid(req.user.uid);
  User.update(req.user.uid, { settings:{ ...(user.settings||{}), ...settings } });
  res.json({ message:'Settings saved' });
};

exports.deleteAccount = async (req,res) => {
  const { password } = req.body;
  if (!password) return res.status(400).json({ error:'Password required' });
  const user = User.findByUid(req.user.uid);
  const ok   = await comparePw(password, user.passwordHash);
  if (!ok) return res.status(401).json({ error:'Wrong password' });
  User.delete(req.user.uid);
  res.json({ message:'Account deleted.' });
};
""")

w("controllers/messageController.js", """\
'use strict';
const Message = require('../models/Message');
const User    = require('../models/User');
const { sanitize } = require('../utils/validators');
const { genId }    = require('../utils/encryption');

exports.getMessages = (req,res) => {
  const { contactUid } = req.params;
  const before = req.query.before||null;
  const limit  = Math.min(parseInt(req.query.limit)||50, 100);
  const msgs   = Message.getConversation(req.user.uid, contactUid, before, limit);
  const myUid  = req.user.uid;
  res.json(msgs.filter(m => !(m.deletedFor||[]).includes(myUid)));
};

exports.sendMessage = (req,res) => {
  const { to,text,replyTo } = req.body;
  const target = User.findByUid(to);
  if (!target) return res.status(404).json({ error:'User not found' });
  if ((target.blockedUsers||[]).includes(req.user.uid)) return res.status(403).json({ error:'Blocked' });
  const clean = sanitize(text||'', 4096);
  if (!clean) return res.status(400).json({ error:'Empty message' });
  const msg = {
    id:genId('msg'), from:req.user.uid, to,
    text:clean, status:'sent',
    timestamp:new Date().toISOString(),
    type:'text', replyTo:replyTo||null,
    edited:false, deleted:false, deletedFor:[], reactions:{},
  };
  Message.create(msg);
  res.json(msg);
};

exports.sendFile = (req,res) => {
  if (!req.file) return res.status(400).json({ error:'No file' });
  const { to } = req.body;
  if (!to) return res.status(400).json({ error:'Recipient required' });
  const target = User.findByUid(to);
  if (!target) return res.status(404).json({ error:'User not found' });
  const msg = {
    id:genId('fil'), from:req.user.uid, to,
    text:req.body.caption ? sanitize(req.body.caption,200) : '',
    fileUrl:'/uploads/'+req.file.filename,
    fileName:req.file.originalname,
    fileType:req.file.mimetype,
    fileSize:req.file.size,
    status:'sent', timestamp:new Date().toISOString(),
    type:'file', deleted:false, deletedFor:[], reactions:{},
  };
  Message.create(msg);
  res.json(msg);
};

exports.markRead = (req,res) => {
  const { messageId } = req.body;
  Message.update(messageId, { status:'read' });
  res.json({ ok:true });
};

exports.markConvoRead = (req,res) => {
  Message.markRead(req.body.contactUid, req.user.uid);
  res.json({ ok:true });
};

exports.clearChat = (req,res) => {
  Message.deleteConvo(req.user.uid, req.params.contactUid);
  res.json({ message:'Chat cleared' });
};

exports.deleteMessage = (req,res) => {
  const { id } = req.params;
  const { forEveryone } = req.body;
  const msg = Message.findById(id);
  if (!msg) return res.status(404).json({ error:'Not found' });
  if (forEveryone && msg.from!==req.user.uid) return res.status(403).json({ error:'Not your message' });
  if (forEveryone) Message.deleteForAll(id);
  else             Message.deleteForMe(id, req.user.uid);
  res.json({ message:'Deleted', id });
};

exports.reactToMsg = (req,res) => {
  const { id }    = req.params;
  const { emoji } = req.body;
  if (!emoji) return res.status(400).json({ error:'Emoji required' });
  const reactions = Message.react(id, req.user.uid, emoji);
  res.json({ reactions, messageId:id });
};

exports.exportChat = (req,res) => {
  const { contactUid } = req.params;
  const msgs = Message.getConversation(req.user.uid, contactUid, null, 9999);
  const me   = User.safe(req.user.uid);
  const them = User.safe(contactUid);
  let txt = 'Chat Export — New Gen Box\\n';
  txt += 'Me: '+me?.name+' ('+me?.uid+')\\n';
  txt += 'With: '+them?.name+' ('+them?.uid+')\\n';
  txt += 'Exported: '+new Date().toLocaleString()+'\\n';
  txt += '-'.repeat(50)+'\\n\\n';
  msgs.forEach(m => {
    if (m.deleted) return;
    const who  = m.from===req.user.uid ? 'Me' : them?.name;
    const time = new Date(m.timestamp).toLocaleString();
    const cont = m.type==='file' ? '[File: '+m.fileName+']' : m.text;
    txt += '['+time+'] '+who+': '+cont+'\\n';
  });
  res.setHeader('Content-Type','text/plain; charset=utf-8');
  res.setHeader('Content-Disposition','attachment; filename="chat_'+contactUid+'.txt"');
  res.send(txt);
};
""")

w("controllers/contactController.js", """\
'use strict';
const User    = require('../models/User');
const Message = require('../models/Message');

exports.getContacts = (req,res) => {
  const user = User.findByUid(req.user.uid);
  const list = (user.contacts||[]).map(uid => {
    const c = User.findByUid(uid);
    if (!c) return null;
    const lastMsg = Message.lastMsg(req.user.uid, uid);
    const unread  = Message.unreadCount(uid, req.user.uid);
    return {
      uid:c.uid, name:c.name, emoji:c.emoji,
      online:c.online, lastSeen:c.lastSeen,
      status:c.status, customStatus:c.customStatus,
      bio:c.bio||'',
      lastMessage:lastMsg||null,
      unreadCount:unread,
    };
  }).filter(Boolean);
  list.sort((a,b) => {
    const ta=a.lastMessage?.timestamp||'';
    const tb=b.lastMessage?.timestamp||'';
    return tb.localeCompare(ta);
  });
  res.json(list);
};

exports.addContact = (req,res) => {
  const { uid } = req.body;
  if (!uid||uid===req.user.uid) return res.status(400).json({ error:'Invalid UID' });
  const target = User.findByUid(uid);
  if (!target) return res.status(404).json({ error:'User '+uid+' not found. Check the UID.' });
  const user = User.findByUid(req.user.uid);
  const contacts = [...(user.contacts||[])];
  if (contacts.includes(uid)) return res.status(409).json({ error:'Already in contacts' });
  contacts.push(uid);
  User.update(req.user.uid, { contacts });
  const { passwordHash:_, ...safe } = target;
  res.json({ message:target.name+' added!', contact:safe });
};

exports.removeContact = (req,res) => {
  const user = User.findByUid(req.user.uid);
  User.update(req.user.uid, { contacts:(user.contacts||[]).filter(c=>c!==req.params.uid) });
  res.json({ message:'Removed' });
};
""")


w("routes/auth.js", """\
'use strict';
const r    = require('express').Router();
const c    = require('../controllers/authController');
const { authLimiter } = require('../middleware/rateLimit');
const { auth }        = require('../middleware/auth');

r.post('/register',         authLimiter, c.register);
r.post('/verify-register',  authLimiter, c.verifyRegister);
r.post('/login',            authLimiter, c.login);
r.post('/verify-login',     authLimiter, c.verifyLogin);
r.post('/resend-otp',       authLimiter, c.resendOtp);
r.post('/logout',           auth,        c.logout);
module.exports = r;
""")

w("routes/user.js", """\
'use strict';
const r    = require('express').Router();
const c    = require('../controllers/userController');
const { auth }   = require('../middleware/auth');
const upload     = require('../middleware/upload');

r.get('/me',              auth, c.getMe);
r.get('/search',          auth, c.searchUsers);
r.get('/:uid',            auth, c.getProfile);
r.put('/profile',         auth, c.updateProfile);
r.put('/change-password', auth, c.changePw);
r.put('/settings',        auth, c.updateSettings);
r.post('/block',          auth, c.blockUser);
r.delete('/account',      auth, c.deleteAccount);
module.exports = r;
""")

w("routes/message.js", """\
'use strict';
const r    = require('express').Router();
const c    = require('../controllers/messageController');
const { auth }   = require('../middleware/auth');
const upload     = require('../middleware/upload');
const { msgLimiter, uploadLimiter } = require('../middleware/rateLimit');

r.get('/export/:contactUid',    auth, c.exportChat);
r.get('/:contactUid',           auth, c.getMessages);
r.post('/',                     auth, msgLimiter, c.sendMessage);
r.post('/file',                 auth, uploadLimiter, upload.single('file'), c.sendFile);
r.post('/read-conversation',    auth, c.markConvoRead);
r.put('/read',                  auth, c.markRead);
r.post('/:id/react',            auth, c.reactToMsg);
r.delete('/clear/:contactUid',  auth, c.clearChat);
r.delete('/:id',                auth, c.deleteMessage);
module.exports = r;
""")

w("routes/contact.js", """\
'use strict';
const r = require('express').Router();
const c = require('../controllers/contactController');
const { auth } = require('../middleware/auth');

r.get('/',         auth, c.getContacts);
r.post('/add',     auth, c.addContact);
r.delete('/:uid',  auth, c.removeContact);
module.exports = r;
""")

w("socket/socketHandlers.js", """\
'use strict';
const { verToken, genId }  = require('../utils/encryption');
const User    = require('../models/User');
const Message = require('../models/Message');
const logger  = require('../utils/logger');

const online = {};   // uid => Set<socketId>
const queue  = {};   // uid => [msg]

function sockets(io, uid) {
  return [...(online[uid]||new Set())].map(id=>io.sockets.sockets.get(id)).filter(Boolean);
}
function emit(io, uid, ev, data) {
  sockets(io,uid).forEach(s=>s.emit(ev,data));
}
function isOnline(uid) { return !!(online[uid]&&online[uid].size>0); }

function broadcastStatus(io, uid, isOnlineNow) {
  const user = User.findByUid(uid);
  if (!user) return;
  const ev = { uid, online:isOnlineNow, lastSeen:user.lastSeen, status:user.status };
  (user.contacts||[]).forEach(c => emit(io, c, 'user-status', ev));
}

function flushQueue(io, uid, socket) {
  if (!queue[uid]||!queue[uid].length) return;
  queue[uid].forEach(m => {
    socket.emit('private-message', m);
    Message.update(m.id, { status:'delivered' });
  });
  delete queue[uid];
}

function initSocket(io) {
  // Cleanup expired OTPs every 5 minutes
  setInterval(() => { try { require('../models/OTP').cleanup(); } catch {} }, 300000);

  io.use((socket, next) => {
    try {
      socket.user = verToken(socket.handshake.auth?.token||'');
      const user  = User.findByUid(socket.user.uid);
      if (!user||user.banned) return next(new Error('Access denied'));
      next();
    } catch { next(new Error('Invalid token')); }
  });

  io.on('connection', socket => {
    const uid = socket.user.uid;
    if (!online[uid]) online[uid] = new Set();
    online[uid].add(socket.id);
    User.update(uid, { online:true, lastSeen:new Date().toISOString() });
    broadcastStatus(io, uid, true);
    flushQueue(io, uid, socket);
    logger.debug('+ ' + uid);

    // ── PRIVATE MESSAGE ──────────────────────────────
    socket.on('private-message', (data, ack) => {
      try {
        const { to,text,replyTo,tempId,type='text' } = data;
        if (!to||!text?.trim()) return;
        const target = User.findByUid(to);
        if (!target||(target.blockedUsers||[]).includes(uid)) return;
        const id  = genId('msg');
        const msg = {
          id, from:uid, to,
          text:text.trim().substring(0,4096),
          status:'sent', timestamp:new Date().toISOString(),
          type, replyTo:replyTo||null, tempId,
          edited:false, deleted:false, deletedFor:[], reactions:{},
        };
        Message.create(msg);
        const recvSockets = sockets(io,to);
        if (recvSockets.length) {
          recvSockets.forEach(s=>s.emit('private-message', msg));
          Message.update(id, { status:'delivered' });
          msg.status = 'delivered';
          emit(io, uid, 'message-status', { id, status:'delivered', tempId });
        } else {
          if (!queue[to]) queue[to]=[];
          queue[to].push({ ...msg });
        }
        if (ack) ack({ id, status:msg.status });
      } catch(e) { logger.warn('msg error: '+e.message); }
    });

    // ── TYPING ───────────────────────────────────────
    socket.on('typing', ({ to, isTyping }) => {
      emit(io, to, 'typing', { from:uid, isTyping });
    });

    // ── READ RECEIPT ─────────────────────────────────
    socket.on('message-read', ({ messageId, from }) => {
      Message.update(messageId, { status:'read' });
      emit(io, from, 'message-read', { messageId });
    });

    socket.on('conversation-read', ({ contactUid }) => {
      Message.markRead(contactUid, uid);
      emit(io, contactUid, 'conversation-read', { by:uid });
    });

    // ── REACTION ─────────────────────────────────────
    socket.on('react', ({ messageId, emoji }) => {
      try {
        const reactions = Message.react(messageId, uid, emoji);
        const msg       = Message.findById(messageId);
        if (!msg) return;
        [uid, msg.from, msg.to].filter(Boolean)
          .forEach(u => emit(io, u, 'reaction-update', { messageId, reactions }));
      } catch {}
    });

    // ── DELETE ───────────────────────────────────────
    socket.on('delete-message', ({ messageId, forEveryone }) => {
      try {
        const msg = Message.findById(messageId);
        if (!msg) return;
        if (forEveryone && msg.from===uid) {
          Message.deleteForAll(messageId);
          [msg.from,msg.to].filter(Boolean)
            .forEach(u=>emit(io,u,'message-deleted',{messageId,forEveryone:true}));
        } else {
          Message.deleteForMe(messageId, uid);
          socket.emit('message-deleted', { messageId, forEveryone:false });
        }
      } catch {}
    });

    // ── STATUS UPDATE ────────────────────────────────
    socket.on('update-status', ({ status, customStatus }) => {
      const up = {};
      if (['available','away','busy','invisible'].includes(status)) up.status = status;
      if (customStatus!==undefined) up.customStatus = String(customStatus).substring(0,60);
      if (Object.keys(up).length) { User.update(uid,up); broadcastStatus(io,uid,true); }
    });

    // ── CHECK ONLINE ─────────────────────────────────
    socket.on('check-online', ({ uid:targetUid }) => {
      socket.emit('online-status', { uid:targetUid, online:isOnline(targetUid) });
    });

    // ── DISCONNECT ───────────────────────────────────
    socket.on('disconnect', reason => {
      online[uid]?.delete(socket.id);
      if (!online[uid]?.size) {
        delete online[uid];
        User.update(uid, { online:false, lastSeen:new Date().toISOString() });
        broadcastStatus(io, uid, false);
      }
      logger.debug('- ' + uid + ' (' + reason + ')');
    });
  });
}

module.exports = { initSocket };
""")


w("public/index.html", """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">
<meta name="theme-color" content="#000000">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black">
<title>New Gen Box</title>
<link rel="manifest" href="/manifest.json">
<link rel="stylesheet" href="/css/style.css">
</head>
<body>

<!-- SPLASH -->
<div id="splash">
  <div class="splash-icon">💬</div>
  <div class="splash-title">New Gen Box</div>
  <div class="splash-sub">Secure Chat</div>
  <div class="splash-loader"><div class="splash-bar"></div></div>
</div>

<!-- TOAST -->
<div id="toast"></div>

<!-- NET BANNER -->
<div id="net-banner" class="hidden">📡 No internet connection</div>

<!-- ═══════════════════════════════════════════
     AUTH SCREEN
═══════════════════════════════════════════ -->
<div id="screen-auth" class="screen hidden">
  <div class="auth-wrap">

    <!-- Top logo -->
    <div class="auth-top">
      <span class="auth-icon">💬</span>
      <div class="auth-brand">New Gen Box</div>
      <div class="auth-tag">Secure Chat</div>
    </div>

    <!-- Tab row -->
    <div class="tab-row">
      <button id="tab-login"    class="tab-btn active" onclick="authUI.switchTab('login')">Login</button>
      <button id="tab-register" class="tab-btn"        onclick="authUI.switchTab('register')">Register</button>
    </div>

    <!-- LOGIN FORM -->
    <div id="form-login">
      <div class="field-group">
        <label class="field-label">📧 Email</label>
        <input id="login-email" class="field-input" type="email" placeholder="you@example.com" autocomplete="email" inputmode="email">
      </div>
      <div class="field-group">
        <label class="field-label">🔒 Password</label>
        <div class="pw-row">
          <input id="login-pw" class="field-input" type="password" placeholder="Your password" autocomplete="current-password">
          <button class="eye-btn" onclick="authUI.toggleEye('login-pw',this)">👁️</button>
        </div>
      </div>
      <div id="login-err" class="err-msg"></div>
      <button id="login-btn" class="btn-primary" onclick="authUI.login()">Continue →</button>
    </div>

    <!-- REGISTER FORM -->
    <div id="form-register" class="hidden">
      <div class="field-group">
        <label class="field-label">👤 Name</label>
        <input id="reg-name" class="field-input" type="text" placeholder="Your name" maxlength="50" autocomplete="name">
      </div>
      <div class="field-group">
        <label class="field-label">📧 Email</label>
        <input id="reg-email" class="field-input" type="email" placeholder="you@example.com" autocomplete="email" inputmode="email">
      </div>
      <div class="field-group">
        <label class="field-label">🔒 Password</label>
        <div class="pw-row">
          <input id="reg-pw" class="field-input" type="password" placeholder="Strong password" autocomplete="new-password" oninput="authUI.checkStrength(this.value)">
          <button class="eye-btn" onclick="authUI.toggleEye('reg-pw',this)">👁️</button>
        </div>
        <!-- Strength indicator -->
        <div class="strength-wrap">
          <div class="strength-bar-bg"><div id="strength-fill"></div></div>
          <div id="strength-label" class="strength-label">Enter a password</div>
        </div>
        <!-- Rules -->
        <div class="pw-rules">
          <span id="sr-len">✗ 8+ chars</span>
          <span id="sr-upper">✗ A-Z</span>
          <span id="sr-lower">✗ a-z</span>
          <span id="sr-num">✗ Number</span>
        </div>
      </div>
      <div id="reg-err" class="err-msg"></div>
      <button id="reg-btn" class="btn-primary" onclick="authUI.register()">Create Account →</button>
    </div>

    <p class="auth-footer">🔒 Secured with OTP verification</p>
  </div>
</div>

<!-- ═══════════════════════════════════════════
     OTP SCREEN  — inline in same page
═══════════════════════════════════════════ -->
<div id="screen-otp" class="screen hidden">
  <div class="auth-wrap">
    <div class="otp-top">
      <div class="otp-icon">📧</div>
      <div class="otp-title">Enter OTP</div>
      <div class="otp-sub">6-digit code sent to<br><strong id="otp-email-lbl"></strong></div>
    </div>

    <!-- 6 boxes -->
    <div class="otp-boxes">
      <input class="otp-box" type="tel" maxlength="1" inputmode="numeric" oninput="authUI.otpInput(this,0)" onkeydown="authUI.otpKey(event,0)">
      <input class="otp-box" type="tel" maxlength="1" inputmode="numeric" oninput="authUI.otpInput(this,1)" onkeydown="authUI.otpKey(event,1)">
      <input class="otp-box" type="tel" maxlength="1" inputmode="numeric" oninput="authUI.otpInput(this,2)" onkeydown="authUI.otpKey(event,2)">
      <input class="otp-box" type="tel" maxlength="1" inputmode="numeric" oninput="authUI.otpInput(this,3)" onkeydown="authUI.otpKey(event,3)">
      <input class="otp-box" type="tel" maxlength="1" inputmode="numeric" oninput="authUI.otpInput(this,4)" onkeydown="authUI.otpKey(event,4)">
      <input class="otp-box" type="tel" maxlength="1" inputmode="numeric" oninput="authUI.otpInput(this,5)" onkeydown="authUI.otpKey(event,5)">
    </div>

    <div id="otp-err" class="err-msg" style="text-align:center"></div>
    <button id="otp-btn" class="btn-primary" onclick="authUI.verifyOtp()">Verify →</button>

    <div class="otp-footer">
      <span id="resend-timer" class="resend-timer"></span>
      <button id="resend-btn" class="btn-link hidden" onclick="authUI.resendOtp()">Resend OTP</button>
      <button class="btn-link" onclick="authUI.backToAuth()">← Back</button>
    </div>

    <div class="otp-hint">
      <strong>📱 Can't see email?</strong><br>
      Check your server terminal — OTP is printed there!
    </div>
  </div>
</div>

<!-- ═══════════════════════════════════════════
     CHAT LIST SCREEN
═══════════════════════════════════════════ -->
<div id="screen-chatlist" class="screen hidden">
  <!-- Header -->
  <div class="app-header">
    <div class="header-left" onclick="nav.go('my-profile')">
      <div class="my-avatar" id="my-avatar">👤</div>
      <div>
        <div class="header-title">Messages</div>
        <div class="my-uid" id="my-uid-tag"></div>
      </div>
    </div>
    <div class="header-right">
      <button class="icon-btn" onclick="nav.go('add-contact')" title="Add Contact">➕</button>
      <div class="menu-wrap">
        <button class="icon-btn" id="cl-menu-btn" onclick="toggleMenu('cl-menu')">⋮</button>
        <div id="cl-menu" class="dropdown hidden">
          <div class="dd-item" onclick="nav.go('my-profile')">👤 Edit Profile</div>
          <div class="dd-sep"></div>
          <div class="dd-item danger" onclick="doLogout()">🚪 Logout</div>
        </div>
      </div>
    </div>
  </div>
  <!-- Search -->
  <div class="search-bar">
    <span class="search-ico">🔍</span>
    <input id="cl-search" class="search-inp" type="search" placeholder="Search chats..." oninput="chatList.search(this.value)">
  </div>
  <!-- List -->
  <div id="cl-list" class="scroll-area"></div>
  <!-- FAB add contact -->
  <button class="fab" onclick="nav.go('add-contact')" title="New Chat">➕</button>
</div>

<!-- ═══════════════════════════════════════════
     CHAT SCREEN
═══════════════════════════════════════════ -->
<div id="screen-chat" class="screen hidden">
  <!-- Header -->
  <div class="app-header">
    <button class="back-btn" onclick="nav.back()">‹</button>
    <div class="ch-info" id="ch-info" onclick="chatUI.openProfile()">
      <div class="ch-avatar" id="ch-avatar">👤</div>
      <div>
        <div class="ch-name" id="ch-name">Contact</div>
        <div class="ch-status" id="ch-status">offline</div>
      </div>
    </div>
    <div class="menu-wrap">
      <button class="icon-btn" onclick="toggleMenu('ch-menu')">⋮</button>
      <div id="ch-menu" class="dropdown hidden">
        <div class="dd-item" onclick="chatUI.openProfile()">👤 View Profile</div>
        <div class="dd-item" onclick="chatUI.exportChat()">📄 Export Chat</div>
        <div class="dd-sep"></div>
        <div class="dd-item danger" onclick="chatUI.clearChat()">🗑 Clear Chat</div>
      </div>
    </div>
  </div>
  <!-- Messages area -->
  <div id="msgs" class="msgs" onscroll="chatUI.onScroll()"></div>
  <!-- Typing indicator -->
  <div id="typing-bar" class="typing-bar hidden">
    <div class="typing-dots"><span></span><span></span><span></span></div>
    <span id="typing-name"></span> is typing...
  </div>
  <!-- Reply preview -->
  <div id="reply-preview" class="reply-preview hidden">
    <div class="rp-bar"></div>
    <div class="rp-body">
      <div class="rp-name" id="rp-name"></div>
      <div class="rp-text" id="rp-text"></div>
    </div>
    <button class="rp-close" onclick="chatUI.cancelReply()">✕</button>
  </div>
  <!-- Input bar -->
  <div class="input-bar">
    <button class="input-btn" onclick="chatUI.toggleAttach()" id="attach-btn">📎</button>
    <div class="input-wrap">
      <textarea id="msg-input" placeholder="Type a message..."
        oninput="chatUI.onInput(this)"
        onkeydown="chatUI.onKeyDown(event)"
        rows="1"></textarea>
    </div>
    <button class="send-btn" id="send-btn" onclick="chatUI.send()">🎤</button>
  </div>
  <!-- Attach menu -->
  <div id="attach-menu" class="attach-menu hidden">
    <button onclick="chatUI.pickFile('image/*')">📸 Photo</button>
    <button onclick="chatUI.pickFile('video/*')">🎥 Video</button>
    <button onclick="chatUI.pickFile('*/*')">📁 File</button>
  </div>
  <input type="file" id="file-picker" style="display:none" onchange="chatUI.onFilePicked(event)">
</div>

<!-- ═══════════════════════════════════════════
     ADD CONTACT SCREEN
═══════════════════════════════════════════ -->
<div id="screen-add-contact" class="screen slide-screen hidden">
  <div class="app-header">
    <button class="back-btn" onclick="nav.back()">‹</button>
    <div class="screen-title">Add Contact</div>
  </div>
  <div class="form-page">
    <div class="uid-info-box">
      <div style="font-size:48px;text-align:center;margin-bottom:12px">🔍</div>
      <p>Enter the <strong>NGB User ID</strong> of the person you want to chat with.</p>
      <p style="margin-top:6px;font-size:13px;color:var(--fg4)">IDs look like: <code>ngb00000001</code></p>
    </div>
    <div class="field-group">
      <label class="field-label">NGB User ID</label>
      <input id="add-uid" class="field-input uid-field" type="text" placeholder="ngb00000001"
        oninput="addContact.lookup(this.value)" maxlength="12">
    </div>
    <div id="uid-preview" class="uid-preview hidden"></div>
    <div id="add-err" class="err-msg"></div>
    <button id="add-btn" class="btn-primary hidden" onclick="addContact.add()">Add Contact ✓</button>
    <div class="divider">— My ID —</div>
    <div class="my-id-box" onclick="addContact.copyMyId()">
      <div class="my-id-label">Tap to copy your NGB ID</div>
      <div class="my-id-val" id="my-id-val"></div>
    </div>
  </div>
</div>

<!-- ═══════════════════════════════════════════
     CONTACT PROFILE SCREEN
═══════════════════════════════════════════ -->
<div id="screen-contact-profile" class="screen slide-screen hidden">
  <div class="app-header">
    <button class="back-btn" onclick="nav.back()">‹</button>
    <div class="screen-title">Profile</div>
  </div>
  <div id="contact-profile-body" class="form-page"></div>
</div>

<!-- ═══════════════════════════════════════════
     MY PROFILE SCREEN
═══════════════════════════════════════════ -->
<div id="screen-my-profile" class="screen slide-screen hidden">
  <div class="app-header">
    <button class="back-btn" onclick="nav.back()">‹</button>
    <div class="screen-title">Edit Profile</div>
    <button class="icon-btn" onclick="myProfile.save()">💾</button>
  </div>
  <div class="form-page">
    <div class="profile-av-wrap">
      <div class="profile-av" id="my-profile-av" onclick="myProfile.changeEmoji()">👤</div>
      <button class="av-change-btn" onclick="myProfile.changeEmoji()">✏️ Change</button>
    </div>
    <div class="my-profile-uid-box" onclick="myProfile.copyUid()">
      <span>🆔 </span><span id="profile-uid-val"></span>
      <span class="copy-hint">tap to copy</span>
    </div>
    <div class="field-group">
      <label class="field-label">🏷 Username</label>
      <input id="pf-name" class="field-input" placeholder="Your name" maxlength="50">
    </div>
    <div class="field-group">
      <label class="field-label">📝 Bio</label>
      <textarea id="pf-bio" class="field-input" placeholder="Write something about you..." maxlength="300" rows="3"></textarea>
    </div>
    <div class="field-group">
      <label class="field-label">💬 Status</label>
      <input id="pf-status-txt" class="field-input" placeholder="What's on your mind?" maxlength="60">
    </div>
    <div class="section-label">Availability</div>
    <div class="status-btns">
      <button class="status-chip active" data-status="available" onclick="myProfile.setStatus('available',this)">🟢 Available</button>
      <button class="status-chip" data-status="away"      onclick="myProfile.setStatus('away',this)">🟡 Away</button>
      <button class="status-chip" data-status="busy"      onclick="myProfile.setStatus('busy',this)">🔴 Busy</button>
      <button class="status-chip" data-status="invisible" onclick="myProfile.setStatus('invisible',this)">⚫ Invisible</button>
    </div>
    <div class="divider">— Account —</div>
    <div class="action-list">
      <div class="action-item" onclick="nav.go('change-password')">🔑 Change Password</div>
    </div>
    <div class="divider">— Danger Zone —</div>
    <div class="action-list">
      <div class="action-item danger" onclick="myProfile.deleteAccount()">⚠️ Delete Account</div>
    </div>
  </div>
</div>

<!-- ═══════════════════════════════════════════
     CHANGE PASSWORD SCREEN
═══════════════════════════════════════════ -->
<div id="screen-change-password" class="screen slide-screen hidden">
  <div class="app-header">
    <button class="back-btn" onclick="nav.back()">‹</button>
    <div class="screen-title">Change Password</div>
  </div>
  <div class="form-page">
    <div class="field-group">
      <label class="field-label">🔒 Current Password</label>
      <div class="pw-row">
        <input id="cp-cur" class="field-input" type="password" placeholder="Current password">
        <button class="eye-btn" onclick="authUI.toggleEye('cp-cur',this)">👁️</button>
      </div>
    </div>
    <div class="field-group">
      <label class="field-label">🔑 New Password</label>
      <div class="pw-row">
        <input id="cp-new" class="field-input" type="password" placeholder="New password (8+ chars)">
        <button class="eye-btn" onclick="authUI.toggleEye('cp-new',this)">👁️</button>
      </div>
    </div>
    <div class="field-group">
      <label class="field-label">✅ Confirm Password</label>
      <div class="pw-row">
        <input id="cp-confirm" class="field-input" type="password" placeholder="Repeat new password">
        <button class="eye-btn" onclick="authUI.toggleEye('cp-confirm',this)">👁️</button>
      </div>
    </div>
    <div id="cp-err" class="err-msg"></div>
    <button class="btn-primary" onclick="myProfile.changePw()">Update Password 🔑</button>
  </div>
</div>

<!-- ═══════════════════════════════════════════
     MEDIA VIEWER OVERLAY
═══════════════════════════════════════════ -->
<div id="media-viewer" class="media-viewer hidden">
  <div class="mv-top">
    <button class="mv-close" onclick="mediaViewer.close()">✕</button>
    <span class="mv-title" id="mv-title">Media</span>
    <button class="mv-dl" onclick="mediaViewer.download()">⬇</button>
  </div>
  <div class="mv-body" id="mv-body">
    <div class="mv-inner" id="mv-inner"></div>
  </div>
</div>

<!-- CONTEXT MENU -->
<div id="ctx-menu" class="ctx-menu hidden"></div>
<div id="backdrop" onclick="closeAll()" style="display:none;position:fixed;inset:0;z-index:499"></div>

<!-- SCRIPTS -->
<script src="https://cdn.socket.io/4.6.0/socket.io.min.js"></script>
<script src="/js/utils.js"></script>
<script src="/js/storage.js"></script>
<script src="/js/auth.js"></script>
<script src="/js/socket.js"></script>
<script src="/js/chatList.js"></script>
<script src="/js/chat.js"></script>
<script src="/js/contacts.js"></script>
<script src="/js/profile.js"></script>
<script src="/js/mediaViewer.js"></script>
<script src="/js/main.js"></script>
</body>
</html>
""")


w("public/css/style.css", """\
/* ═══════════════════════════════════════════════
   NEW GEN BOX — Complete CSS
   Pure black/white minimal design
═══════════════════════════════════════════════ */

/* Variables */
:root {
  --bg:      #ffffff;
  --bg2:     #f7f7f7;
  --bg3:     #efefef;
  --fg:      #000000;
  --fg2:     #222222;
  --fg3:     #555555;
  --fg4:     #999999;
  --border:  #e0e0e0;
  --border2: #cccccc;
  --accent:  #000000;
  --danger:  #cc0000;
  --success: #007700;
  --blue:    #1a73e8;
  --green:   #22c55e;
  --bubble-me:     #000000;
  --bubble-me-fg:  #ffffff;
  --bubble-them:   #f0f0f0;
  --bubble-them-fg:#000000;
  --safe-bottom: env(safe-area-inset-bottom, 0px);
  --safe-top:    env(safe-area-inset-top,    0px);
  --header-h: 56px;
  --input-h:  60px;
  --radius:   14px;
  --font: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
  --mono: 'SF Mono', 'Fira Code', 'Consolas', monospace;
}

[data-theme="dark"] {
  --bg:  #0c0c0c; --bg2: #161616; --bg3: #202020;
  --fg:  #f0f0f0; --fg2: #d0d0d0; --fg3: #a0a0a0; --fg4: #606060;
  --border: #2c2c2c; --border2: #383838;
  --bubble-me:     #e8e8e8; --bubble-me-fg: #000000;
  --bubble-them:   #202020; --bubble-them-fg:#f0f0f0;
}

/* Reset */
*,*::before,*::after { box-sizing:border-box; margin:0; padding:0; }
html,body { height:100%; overflow:hidden; font-family:var(--font); font-size:15px; background:var(--bg); color:var(--fg); -webkit-font-smoothing:antialiased; overscroll-behavior:none; }
button { cursor:pointer; -webkit-tap-highlight-color:transparent; }
input,textarea,select { font-family:var(--font); }
img { max-width:100%; display:block; }

/* Screens */
.screen { position:fixed; inset:0; display:flex; flex-direction:column; background:var(--bg); transition:transform .28s ease,opacity .28s ease; will-change:transform; }
.screen.hidden { display:none !important; }
.slide-screen { transform:translateX(100%); transition:transform .28s cubic-bezier(.4,0,.2,1); }
.slide-screen.visible { transform:translateX(0); }

/* Scrollbar */
::-webkit-scrollbar { width:3px; height:3px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:var(--border2); border-radius:2px; }

/* Toast */
#toast {
  position:fixed; bottom:80px; left:50%; transform:translateX(-50%);
  background:var(--fg); color:var(--bg); padding:10px 20px;
  border-radius:100px; font-size:13px; font-weight:600; z-index:9999;
  opacity:0; transition:opacity .25s; pointer-events:none;
  white-space:nowrap; max-width:90vw; text-align:center;
}
#toast.show { opacity:1; }
#toast.err  { background:var(--danger); }
#toast.ok   { background:var(--success); }

/* Net banner */
#net-banner {
  position:fixed; top:0; left:0; right:0; background:#c00; color:#fff;
  text-align:center; padding:8px; font-size:13px; font-weight:600;
  z-index:1000;
}

/* Splash */
#splash {
  position:fixed; inset:0; background:#000; color:#fff;
  display:flex; flex-direction:column; align-items:center; justify-content:center;
  z-index:9999; transition:opacity .5s;
}
.splash-icon  { font-size:72px; animation:bounce .6s ease; }
.splash-title { font-size:24px; font-weight:800; letter-spacing:1px; margin-top:12px; }
.splash-sub   { font-size:12px; color:rgba(255,255,255,.5); margin-top:4px; letter-spacing:2px; }
.splash-loader{ width:180px; height:2px; background:rgba(255,255,255,.15); border-radius:1px; margin-top:48px; overflow:hidden; }
.splash-bar   { height:100%; background:#fff; border-radius:1px; animation:load 2s ease forwards; }

/* App header */
.app-header {
  display:flex; align-items:center; gap:10px;
  padding:0 14px;
  height:calc(var(--header-h) + var(--safe-top));
  padding-top:var(--safe-top);
  background:var(--bg); border-bottom:1px solid var(--border);
  flex-shrink:0; z-index:100;
}
.header-left  { display:flex; align-items:center; gap:10px; flex:1; cursor:pointer; min-width:0; }
.header-right { display:flex; align-items:center; gap:2px; }
.header-title { font-size:18px; font-weight:800; }
.screen-title { font-size:17px; font-weight:700; flex:1; }
.back-btn     { background:none; border:none; font-size:26px; color:var(--fg); padding:4px 8px 4px 0; line-height:1; }

/* My avatar */
.my-avatar { font-size:28px; flex-shrink:0; cursor:pointer; }
.my-uid    { font-size:11px; color:var(--fg4); font-family:var(--mono); }

/* Icon buttons */
.icon-btn { background:none; border:none; font-size:22px; color:var(--fg); padding:8px; border-radius:50%; transition:background .15s; }
.icon-btn:active { background:var(--bg3); }

/* Dropdown */
.menu-wrap   { position:relative; }
.dropdown    { position:absolute; right:0; top:46px; background:var(--bg); border:1px solid var(--border); border-radius:14px; min-width:180px; z-index:600; box-shadow:0 8px 32px rgba(0,0,0,.15); overflow:hidden; animation:pop .12s ease; }
.dd-item     { padding:14px 18px; font-size:14px; cursor:pointer; transition:background .12s; display:flex; align-items:center; gap:10px; }
.dd-item:hover { background:var(--bg2); }
.dd-item.danger { color:var(--danger); }
.dd-sep      { height:1px; background:var(--border); }
.hidden      { display:none !important; }

/* Auth screen */
#screen-auth { align-items:center; justify-content:center; padding:20px; overflow-y:auto; }
.auth-wrap   { width:100%; max-width:400px; }
.auth-top    { text-align:center; margin-bottom:28px; }
.auth-icon   { font-size:56px; display:block; animation:bounce .5s ease; }
.auth-brand  { font-size:24px; font-weight:900; margin-top:10px; }
.auth-tag    { font-size:12px; color:var(--fg4); margin-top:4px; letter-spacing:1px; }
.auth-footer { font-size:12px; color:var(--fg4); text-align:center; margin-top:16px; }

/* Tab row */
.tab-row  { display:flex; border:1.5px solid var(--border); border-radius:10px; overflow:hidden; margin-bottom:20px; }
.tab-btn  { flex:1; padding:11px; border:none; background:transparent; font-size:14px; font-weight:700; cursor:pointer; color:var(--fg4); transition:all .15s; }
.tab-btn.active { background:var(--fg); color:var(--bg); }

/* Field */
.field-group  { margin-top:14px; }
.field-label  { display:block; font-size:12px; font-weight:700; color:var(--fg4); margin-bottom:6px; letter-spacing:.4px; text-transform:uppercase; }
.field-input  { width:100%; padding:13px 14px; background:var(--bg2); border:1.5px solid var(--border); border-radius:10px; font-size:15px; color:var(--fg); outline:none; resize:none; transition:border-color .15s; -webkit-appearance:none; }
.field-input:focus { border-color:var(--fg); }
.uid-field    { font-family:var(--mono); font-size:18px; letter-spacing:2px; text-transform:lowercase; }

/* Password row */
.pw-row      { position:relative; }
.pw-row .field-input { padding-right:46px; }
.eye-btn     { position:absolute; right:13px; top:50%; transform:translateY(-50%); background:none; border:none; font-size:18px; color:var(--fg4); cursor:pointer; }

/* Strength bar */
.strength-wrap  { margin-top:10px; }
.strength-bar-bg{ height:4px; background:var(--bg3); border-radius:2px; overflow:hidden; margin-bottom:5px; }
#strength-fill  { height:100%; width:0; border-radius:2px; transition:width .3s,background .3s; }
.strength-label { font-size:12px; color:var(--fg4); font-weight:600; }
.pw-rules       { display:flex; flex-wrap:wrap; gap:6px 12px; margin-top:10px; }
.pw-rules span  { font-size:12px; color:var(--fg4); }
.pw-rules span.ok { color:var(--success); }

/* Buttons */
.btn-primary { width:100%; margin-top:16px; padding:14px; background:var(--fg); color:var(--bg); border:none; border-radius:12px; font-size:15px; font-weight:700; cursor:pointer; transition:all .15s; }
.btn-primary:active { transform:scale(.97); }
.btn-link    { background:none; border:none; color:var(--fg4); font-size:13px; text-decoration:underline; cursor:pointer; padding:4px 8px; }

/* Error / success messages */
.err-msg { color:var(--danger); font-size:13px; min-height:18px; margin-top:8px; }

/* OTP screen */
#screen-otp { align-items:center; justify-content:center; padding:20px; }
.otp-top    { text-align:center; margin-bottom:24px; }
.otp-icon   { font-size:48px; }
.otp-title  { font-size:22px; font-weight:800; margin-top:10px; }
.otp-sub    { font-size:14px; color:var(--fg4); margin-top:8px; line-height:1.5; }
.otp-sub strong { color:var(--fg); }

.otp-boxes  { display:flex; gap:10px; justify-content:center; margin:20px 0; }
.otp-box    {
  width:48px; height:58px; text-align:center;
  font-size:26px; font-weight:900; font-family:var(--mono);
  border:2px solid var(--border); border-radius:12px;
  background:var(--bg2); color:var(--fg); outline:none;
  transition:border-color .15s, transform .15s, box-shadow .15s;
  -webkit-appearance:none;
}
.otp-box:focus { border-color:var(--fg); transform:scale(1.07); box-shadow:0 0 0 3px rgba(0,0,0,.08); }
.otp-box.filled { border-color:var(--fg); background:var(--bg3); }

.otp-footer     { display:flex; align-items:center; gap:10px; justify-content:center; margin:12px 0; flex-wrap:wrap; }
.resend-timer   { font-size:12px; color:var(--fg4); }
.otp-hint       { background:var(--bg2); border:1px solid var(--border); border-radius:12px; padding:14px 16px; text-align:center; font-size:13px; color:var(--fg3); margin-top:16px; line-height:1.6; }
.otp-hint strong { color:var(--fg); }

/* Search bar */
.search-bar  { display:flex; align-items:center; gap:8px; padding:10px 14px; border-bottom:1px solid var(--border); background:var(--bg); flex-shrink:0; }
.search-ico  { font-size:15px; color:var(--fg4); }
.search-inp  { flex:1; border:none; background:transparent; outline:none; font-size:14px; color:var(--fg); }
.search-inp::placeholder { color:var(--fg4); }

/* Chat list */
.scroll-area { flex:1; overflow-y:auto; }
.cl-item     { display:flex; align-items:center; gap:12px; padding:13px 16px; border-bottom:1px solid var(--border); cursor:pointer; transition:background .12s; }
.cl-item:active { background:var(--bg2); }
.cl-avatar   { font-size:32px; flex-shrink:0; width:48px; height:48px; display:flex; align-items:center; justify-content:center; background:var(--bg2); border-radius:50%; border:1px solid var(--border); overflow:hidden; position:relative; }
.online-dot  { position:absolute; bottom:1px; right:1px; width:12px; height:12px; border-radius:50%; border:2px solid var(--bg); }
.online-dot.on  { background:var(--green); }
.online-dot.off { background:var(--fg4); }
.cl-body     { flex:1; min-width:0; }
.cl-name     { font-weight:700; font-size:15px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.cl-preview  { font-size:13px; color:var(--fg4); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; margin-top:2px; }
.cl-meta     { text-align:right; flex-shrink:0; display:flex; flex-direction:column; align-items:flex-end; gap:5px; }
.cl-time     { font-size:11px; color:var(--fg4); white-space:nowrap; }
.cl-badge    { background:var(--fg); color:var(--bg); border-radius:100px; font-size:11px; font-weight:800; padding:1px 7px; min-width:20px; text-align:center; }

/* Chat screen */
.ch-info   { display:flex; align-items:center; gap:10px; flex:1; cursor:pointer; min-width:0; }
.ch-avatar { font-size:30px; flex-shrink:0; }
.ch-name   { font-size:16px; font-weight:800; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.ch-status { font-size:12px; color:var(--fg4); }
.ch-status.online { color:var(--green); }

/* Messages */
.msgs { flex:1; overflow-y:auto; padding:10px 12px; display:flex; flex-direction:column; gap:2px; scroll-behavior:smooth; overscroll-behavior:contain; }

.date-sep  { text-align:center; padding:14px 0 4px; }
.date-sep span { background:var(--bg2); border:1px solid var(--border); padding:3px 12px; border-radius:100px; font-size:11px; color:var(--fg4); font-weight:700; }

.msg-row   { display:flex; flex-direction:column; margin-bottom:2px; animation:msgIn .15s ease; }
.msg-row.me    { align-items:flex-end; }
.msg-row.them  { align-items:flex-start; }

.bubble    { max-width:min(72vw,300px); padding:9px 13px; border-radius:18px; font-size:14px; line-height:1.55; word-break:break-word; cursor:pointer; position:relative; user-select:text; }
.bubble:active { opacity:.85; }
.me   .bubble  { background:var(--bubble-me); color:var(--bubble-me-fg); border-bottom-right-radius:4px; }
.them .bubble  { background:var(--bubble-them); color:var(--bubble-them-fg); border-bottom-left-radius:4px; }
.bubble.deleted { opacity:.5; font-style:italic; font-size:13px; }

.msg-meta { display:flex; align-items:center; gap:4px; font-size:10px; color:var(--fg4); margin-top:2px; padding:0 4px; }
.me .msg-meta { flex-direction:row-reverse; color:rgba(255,255,255,.45); }
[data-theme="dark"] .me .msg-meta { color:rgba(0,0,0,.45); }

.tick       { font-size:12px; }
.tick.sent  { color:var(--fg4); }
.tick.read  { color:var(--blue); }

/* Reply preview */
.reply-preview { display:flex; align-items:center; gap:10px; padding:10px 14px; border-top:1px solid var(--border); background:var(--bg2); flex-shrink:0; animation:slideUp .15s ease; }
.rp-bar  { width:3px; height:36px; background:var(--fg); border-radius:2px; flex-shrink:0; }
.rp-body { flex:1; min-width:0; }
.rp-name { font-size:12px; font-weight:800; margin-bottom:2px; }
.rp-text { font-size:13px; color:var(--fg4); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.rp-close{ background:none; border:none; font-size:20px; color:var(--fg4); cursor:pointer; flex-shrink:0; }

/* Reply block in message */
.reply-block { border-left:3px solid currentColor; padding:5px 10px; margin-bottom:7px; border-radius:4px; background:rgba(0,0,0,.07); cursor:pointer; }
[data-theme="dark"] .reply-block { background:rgba(255,255,255,.07); }
.rb-name { font-size:11px; font-weight:800; opacity:.85; margin-bottom:2px; }
.rb-txt  { font-size:12px; opacity:.65; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:220px; }

/* Typing bar */
.typing-bar { display:flex; align-items:center; gap:8px; padding:8px 16px; font-size:13px; color:var(--fg4); font-style:italic; flex-shrink:0; }
.typing-dots { display:flex; gap:4px; align-items:center; }
.typing-dots span { width:6px; height:6px; background:var(--fg4); border-radius:50%; animation:typeDot 1.4s ease infinite; }
.typing-dots span:nth-child(2) { animation-delay:.2s; }
.typing-dots span:nth-child(3) { animation-delay:.4s; }

/* Input bar */
.input-bar { display:flex; align-items:flex-end; gap:6px; padding:10px 12px; padding-bottom:calc(10px + var(--safe-bottom)); border-top:1px solid var(--border); background:var(--bg); flex-shrink:0; min-height:var(--input-h); }
.input-btn { background:none; border:none; font-size:22px; color:var(--fg); padding:8px; border-radius:50%; transition:background .12s; flex-shrink:0; }
.input-btn:active { background:var(--bg3); }
.input-wrap { flex:1; }
#msg-input {
  width:100%; background:var(--bg2); border:1.5px solid var(--border);
  border-radius:20px; padding:10px 15px; font-size:15px; color:var(--fg);
  outline:none; resize:none; line-height:1.45; max-height:120px; overflow-y:auto;
  transition:border-color .15s;
}
#msg-input:focus { border-color:var(--fg); }
#msg-input::placeholder { color:var(--fg4); }
.send-btn { width:44px; height:44px; border-radius:50%; background:var(--fg); color:var(--bg); border:none; font-size:20px; display:flex; align-items:center; justify-content:center; transition:all .15s; flex-shrink:0; }
.send-btn:active { transform:scale(.88); }

/* Attach menu */
.attach-menu { position:absolute; bottom:calc(var(--input-h) + 4px); left:12px; background:var(--bg); border:1px solid var(--border); border-radius:14px; overflow:hidden; box-shadow:0 8px 32px rgba(0,0,0,.15); animation:pop .12s ease; z-index:50; }
.attach-menu button { display:block; width:100%; text-align:left; padding:14px 18px; border:none; background:none; font-size:14px; color:var(--fg); cursor:pointer; transition:background .12s; }
.attach-menu button:hover { background:var(--bg2); }

/* File bubble */
.file-bubble { display:flex; align-items:center; gap:10px; padding:2px 0; }
.file-icon   { font-size:30px; flex-shrink:0; }
.file-info   { flex:1; min-width:0; }
.file-name   { font-size:13px; font-weight:700; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:160px; }
.file-size   { font-size:11px; opacity:.6; margin-top:2px; }
.file-dl     { color:inherit; text-decoration:none; font-size:12px; opacity:.7; }

/* Reactions */
.reactions   { display:flex; flex-wrap:wrap; gap:3px; margin-top:4px; padding:0 4px; }
.react-chip  { display:inline-flex; align-items:center; gap:3px; background:var(--bg); border:1px solid var(--border); border-radius:100px; padding:3px 8px; font-size:14px; cursor:pointer; transition:background .12s; }
.react-chip:active { background:var(--bg3); }
.react-count { font-size:11px; color:var(--fg4); font-weight:700; }

/* Context menu */
.ctx-menu    { position:fixed; background:var(--bg); border:1px solid var(--border); border-radius:14px; min-width:190px; z-index:700; box-shadow:0 8px 32px rgba(0,0,0,.18); overflow:hidden; animation:pop .12s ease; }
.ctx-item    { display:flex; align-items:center; gap:10px; padding:13px 18px; font-size:14px; font-weight:500; cursor:pointer; transition:background .12s; }
.ctx-item:hover { background:var(--bg2); }
.ctx-item.danger { color:var(--danger); }
.ctx-sep     { height:1px; background:var(--border); }

/* FAB */
.fab { position:absolute; bottom:calc(var(--input-h) + 16px); right:16px; width:48px; height:48px; border-radius:50%; background:var(--fg); color:var(--bg); border:none; font-size:22px; cursor:pointer; box-shadow:0 4px 16px rgba(0,0,0,.2); display:flex; align-items:center; justify-content:center; transition:all .15s; z-index:30; }
.fab:active { transform:scale(.88); }
#screen-chatlist { position:relative; }
#screen-chatlist .fab { bottom:20px; }

/* Add contact */
.form-page      { flex:1; overflow-y:auto; padding:20px; padding-bottom:calc(24px + var(--safe-bottom)); }
.uid-info-box   { background:var(--bg2); border-radius:14px; padding:20px; text-align:center; margin-bottom:12px; font-size:14px; color:var(--fg3); line-height:1.6; }
.uid-preview    { background:var(--bg2); border:1.5px solid var(--border); border-radius:12px; padding:14px 18px; display:flex; align-items:center; gap:14px; margin:10px 0; animation:slideUp .2s ease; }
.uid-prev-av    { font-size:36px; flex-shrink:0; }
.uid-prev-name  { font-size:16px; font-weight:700; }
.uid-prev-uid   { font-size:12px; color:var(--fg4); font-family:var(--mono); margin-top:2px; }
.divider        { text-align:center; font-size:12px; color:var(--fg4); margin:20px 0 16px; font-weight:600; }
.my-id-box      { background:var(--bg2); border:1px solid var(--border); border-radius:12px; padding:16px; text-align:center; cursor:pointer; transition:background .12s; }
.my-id-box:active { background:var(--bg3); }
.my-id-label    { font-size:12px; color:var(--fg4); margin-bottom:6px; }
.my-id-val      { font-size:20px; font-weight:900; font-family:var(--mono); letter-spacing:2px; }
.copy-hint      { font-size:11px; color:var(--fg4); margin-left:8px; }

/* Profile */
.profile-av-wrap { display:flex; flex-direction:column; align-items:center; padding:24px 0 8px; }
.profile-av      { font-size:88px; cursor:pointer; transition:transform .15s; }
.profile-av:active { transform:scale(.9); }
.av-change-btn   { background:none; border:1px solid var(--border); border-radius:100px; padding:6px 14px; font-size:13px; color:var(--fg); cursor:pointer; margin-top:8px; }
.my-profile-uid-box { display:flex; align-items:center; justify-content:center; gap:6px; margin:10px 0 6px; cursor:pointer; padding:10px; border-radius:10px; background:var(--bg2); }
.section-label  { font-size:11px; font-weight:700; color:var(--fg4); letter-spacing:.6px; text-transform:uppercase; margin:20px 0 10px; }
.status-btns    { display:flex; flex-wrap:wrap; gap:8px; }
.status-chip    { border:1.5px solid var(--border); border-radius:100px; padding:7px 14px; font-size:13px; font-weight:600; cursor:pointer; background:transparent; color:var(--fg4); transition:all .15s; }
.status-chip.active { background:var(--fg); color:var(--bg); border-color:var(--fg); }
.action-list    { border:1px solid var(--border); border-radius:12px; overflow:hidden; }
.action-item    { padding:15px 18px; font-size:14px; font-weight:500; cursor:pointer; border-bottom:1px solid var(--border); transition:background .12s; }
.action-item:last-child { border-bottom:none; }
.action-item:active { background:var(--bg3); }
.action-item.danger { color:var(--danger); }

/* Contact profile */
.cpf-top        { display:flex; flex-direction:column; align-items:center; padding:32px 20px 20px; text-align:center; }
.cpf-avatar     { font-size:88px; margin-bottom:14px; }
.cpf-name       { font-size:24px; font-weight:900; }
.cpf-uid        { font-size:13px; color:var(--fg4); font-family:var(--mono); margin-top:6px; cursor:pointer; background:var(--bg2); padding:5px 14px; border-radius:100px; }
.cpf-bio        { font-size:14px; color:var(--fg3); margin-top:8px; line-height:1.6; max-width:280px; }
.cpf-actions    { display:grid; grid-template-columns:repeat(2,1fr); gap:10px; width:100%; max-width:340px; margin-top:20px; }
.cpf-action     { display:flex; flex-direction:column; align-items:center; gap:5px; padding:14px 8px; background:var(--bg2); border:1.5px solid var(--border); border-radius:14px; cursor:pointer; transition:all .15s; font-size:12px; font-weight:700; color:var(--fg4); }
.cpf-action:active { transform:scale(.95); }
.cpf-action span:first-child { font-size:24px; }
.cpf-action.danger { border-color:var(--danger); color:var(--danger); }

/* Media viewer */
.media-viewer { position:fixed; inset:0; background:#000; z-index:2000; display:flex; flex-direction:column; animation:fadeIn .2s ease; }
.mv-top { display:flex; align-items:center; justify-content:space-between; padding:16px 20px; }
.mv-close { background:rgba(255,255,255,.12); border:none; color:#fff; border-radius:50%; width:38px; height:38px; font-size:18px; cursor:pointer; display:flex; align-items:center; justify-content:center; }
.mv-title { color:rgba(255,255,255,.7); font-size:14px; flex:1; text-align:center; }
.mv-dl    { background:rgba(255,255,255,.12); border:none; color:#fff; border-radius:50%; width:38px; height:38px; font-size:18px; cursor:pointer; display:flex; align-items:center; justify-content:center; }
.mv-body  { flex:1; display:flex; align-items:center; justify-content:center; overflow:hidden; }
.mv-inner { transition:transform .2s ease; transform-origin:center; cursor:grab; }
.mv-inner:active { cursor:grabbing; }
.mv-inner img,.mv-inner video { max-width:95vw; max-height:85vh; object-fit:contain; border-radius:8px; display:block; }

/* Empty states */
.empty { text-align:center; padding:60px 24px; color:var(--fg4); }
.empty-icon  { font-size:52px; margin-bottom:14px; opacity:.5; }
.empty-title { font-size:18px; font-weight:700; color:var(--fg2); margin-bottom:6px; }
.empty-sub   { font-size:14px; line-height:1.6; }

/* Animations */
@keyframes bounce   { 0%{transform:scale(0);opacity:0}60%{transform:scale(1.1)}100%{transform:scale(1);opacity:1} }
@keyframes pop      { from{opacity:0;transform:scale(.9) translateY(-4px)}to{opacity:1;transform:scale(1) translateY(0)} }
@keyframes slideUp  { from{transform:translateY(10px);opacity:0}to{transform:translateY(0);opacity:1} }
@keyframes msgIn    { from{opacity:0;transform:translateY(8px) scale(.97)}to{opacity:1;transform:translateY(0) scale(1)} }
@keyframes fadeIn   { from{opacity:0}to{opacity:1} }
@keyframes load     { 0%{width:0}50%{width:65%}100%{width:100%} }
@keyframes shake    { 0%,100%{transform:translateX(0)}20%,60%{transform:translateX(-5px)}40%,80%{transform:translateX(5px)} }
@keyframes typeDot  { 0%,80%,100%{transform:scale(.5);opacity:.3}40%{transform:scale(1);opacity:1} }
.shake { animation:shake .4s ease; }
""")


w("public/js/utils.js", """\
'use strict';
const fmtTime = ts => {
  if (!ts) return '';
  const d=new Date(ts), n=new Date();
  if (d.toDateString()===n.toDateString()) return d.toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'});
  const y=new Date(n); y.setDate(n.getDate()-1);
  if (d.toDateString()===y.toDateString()) return 'Yesterday';
  if (n-d<7*86400000) return d.toLocaleDateString([],{weekday:'short'});
  return d.toLocaleDateString([],{month:'short',day:'numeric'});
};
const fmtDate = ts => {
  if (!ts) return '';
  const d=new Date(ts), n=new Date();
  if (d.toDateString()===n.toDateString()) return 'Today';
  const y=new Date(n); y.setDate(n.getDate()-1);
  if (d.toDateString()===y.toDateString()) return 'Yesterday';
  return d.toLocaleDateString([],{weekday:'long',month:'long',day:'numeric'});
};
const fmtSize = bytes => {
  if (!bytes) return '0B';
  if (bytes<1024) return bytes+'B';
  if (bytes<1048576) return (bytes/1024).toFixed(1)+'KB';
  return (bytes/1048576).toFixed(1)+'MB';
};
const fmtDur = s => { const m=Math.floor(s/60); return m+':'+(s%60<10?'0':'')+s%60; };
const esc    = s => { const d=document.createElement('div'); d.textContent=s; return d.innerHTML; };
const nl2br  = s => (s||'').replace(/\\n/g,'<br>');
const trunc  = (s,n=60) => s&&s.length>n ? s.substring(0,n)+'…' : s||'';
const copyTxt= t => { if(navigator.clipboard) navigator.clipboard.writeText(t).catch(()=>{}); else{ const el=document.createElement('textarea'); el.value=t; document.body.appendChild(el); el.select(); document.execCommand('copy'); document.body.removeChild(el); } };
const debounce=(fn,d=300)=>{ let t; return(...a)=>{ clearTimeout(t); t=setTimeout(()=>fn(...a),d); }; };
const fileIcon = (name='',mime='') => {
  if (mime.startsWith('image/')) return '🖼️';
  if (mime.startsWith('video/')) return '🎬';
  if (mime.startsWith('audio/')) return '🎵';
  const ext=(name.split('.').pop()||'').toLowerCase();
  return {pdf:'📄',doc:'📝',docx:'📝',xls:'📊',xlsx:'📊',zip:'📦',rar:'📦',apk:'📱',txt:'📃'}[ext]||'📎';
};
const isImg  = m => m&&m.startsWith('image/');
const isVid  = m => m&&m.startsWith('video/');
const isAud  = m => m&&m.startsWith('audio/');
const linkify= t => t.replace(/https?:\\/\\/[^\\s<>"]+/gi, u=>'<a href="'+u+'" target="_blank" rel="noopener" style="color:inherit;text-decoration:underline">'+u+'</a>');
const uuid   = ()=>'id_'+Date.now()+'_'+Math.random().toString(36).slice(2,8);
const sleep  = ms => new Promise(r=>setTimeout(r,ms));
window.fmtTime=fmtTime; window.fmtDate=fmtDate; window.fmtSize=fmtSize;
window.fmtDur=fmtDur; window.esc=esc; window.nl2br=nl2br; window.trunc=trunc;
window.copyTxt=copyTxt; window.debounce=debounce; window.fileIcon=fileIcon;
window.isImg=isImg; window.isVid=isVid; window.isAud=isAud;
window.linkify=linkify; window.uuid=uuid; window.sleep=sleep;

function toast(msg, type='', dur=2800) {
  const el=document.getElementById('toast');
  if (!el) return;
  el.textContent=msg; el.className='show'+(type?' '+type:'');
  clearTimeout(el._t); el._t=setTimeout(()=>el.className='',dur);
}
window.toast=toast;

async function api(path, opts={}) {
  const token=localStorage.getItem('ngb_token');
  const headers={'Content-Type':'application/json',...(token?{Authorization:'Bearer '+token}:{}),...(opts.headers||{})};
  if (opts.body instanceof FormData) delete headers['Content-Type'];
  else if (opts.body&&typeof opts.body==='object') opts.body=JSON.stringify(opts.body);
  let res;
  try { res=await fetch('/api'+path,{...opts,headers}); }
  catch(e) { throw new Error('Network error'); }
  if (res.status===401) { authLogout && authLogout(); throw new Error('Session expired'); }
  const ct=res.headers.get('content-type')||'';
  if (ct.includes('application/json')) {
    const d=await res.json();
    if (!res.ok) throw new Error(d.error||'Request failed');
    return d;
  }
  if (!res.ok) throw new Error('Request failed: '+res.status);
  return res;
}
window.api=api;

function toggleMenu(id) {
  const el=document.getElementById(id);
  if (!el) return;
  const hidden=el.classList.contains('hidden');
  document.querySelectorAll('.dropdown').forEach(d=>d.classList.add('hidden'));
  const bd=document.getElementById('backdrop');
  if (hidden) { el.classList.remove('hidden'); if(bd) bd.style.display='block'; }
  else        { if(bd) bd.style.display='none'; }
}
window.toggleMenu=toggleMenu;

function closeAll() {
  document.querySelectorAll('.dropdown,.ctx-menu,.attach-menu').forEach(d=>d.classList.add('hidden'));
  const bd=document.getElementById('backdrop');
  if (bd) bd.style.display='none';
}
window.closeAll=closeAll;
""")

w("public/js/storage.js", """\
'use strict';
const store = {
  get:  (k,d=null) => { try{const v=localStorage.getItem(k); return v===null?d:JSON.parse(v);}catch{return d;} },
  set:  (k,v)      => { try{localStorage.setItem(k,JSON.stringify(v));}catch{} },
  del:  k          => { try{localStorage.removeItem(k);}catch{} },
  token:()         => store.get('ngb_token'),
  user: ()         => store.get('ngb_user',{}),
  setUser: u       => store.set('ngb_user',u),
  settings:()      => store.get('ngb_settings',{notifications:true,sounds:true,readReceipts:true,theme:'light',enterToSend:false}),
  draft:(uid)      => store.get('draft_'+uid,''),
  setDraft:(uid,t) => t ? store.set('draft_'+uid,t) : store.del('draft_'+uid),
};
window.store=store;
""")

w("public/js/auth.js", """\
'use strict';
let _otpType='login', _otpEmail='', _resendInt=null;

const authUI = {
  switchTab(tab) {
    const fL=document.getElementById('form-login'), fR=document.getElementById('form-register');
    const tL=document.getElementById('tab-login'),  tR=document.getElementById('tab-register');
    if (tab==='login') {
      fL&&fL.classList.remove('hidden'); fR&&fR.classList.add('hidden');
      tL&&tL.classList.add('active');    tR&&tR.classList.remove('active');
    } else {
      fR&&fR.classList.remove('hidden'); fL&&fL.classList.add('hidden');
      tR&&tR.classList.add('active');    tL&&tL.classList.remove('active');
    }
  },
  toggleEye(id,btn) {
    const el=document.getElementById(id); if(!el) return;
    el.type=el.type==='password'?'text':'password';
    if(btn) btn.textContent=el.type==='password'?'👁️':'🙈';
  },
  checkStrength(pw) {
    const fill=document.getElementById('strength-fill');
    const lbl=document.getElementById('strength-label');
    if(!fill||!lbl) return;
    const c={len:pw.length>=8,upper:/[A-Z]/.test(pw),lower:/[a-z]/.test(pw),num:/[0-9]/.test(pw)};
    const score=Object.values(c).filter(Boolean).length;
    const colors=['','#cc0000','#ff6600','#ffaa00','#00aa44'];
    const labels=['','Very Weak','Weak','Fair','Strong'];
    fill.style.width=(score*25)+'%'; fill.style.background=colors[score]||'#ccc';
    lbl.textContent=pw?labels[score]:'Enter a password'; lbl.style.color=colors[score]||'#888';
    const rm={len:'sr-len',upper:'sr-upper',lower:'sr-lower',num:'sr-num'};
    const rt={len:'8+ chars',upper:'A-Z',lower:'a-z',num:'Number'};
    Object.entries(c).forEach(([k,v])=>{const el=document.getElementById(rm[k]); if(el){el.textContent=(v?'✓ ':'✗ ')+rt[k]; el.className=v?'ok':'';}});
  },
  otpInput(inp,idx) {
    const boxes=document.querySelectorAll('.otp-box');
    const v=inp.value.replace(/\\D/g,'').slice(-1);
    inp.value=v;
    if(v) { inp.classList.add('filled'); if(idx<5) boxes[idx+1]&&boxes[idx+1].focus(); else setTimeout(()=>authUI.verifyOtp(),350); }
    else  { inp.classList.remove('filled'); }
  },
  otpKey(e,idx) {
    const boxes=document.querySelectorAll('.otp-box');
    if(e.key==='Backspace'&&!boxes[idx].value&&idx>0) boxes[idx-1]?.focus();
    if(e.key==='ArrowLeft'&&idx>0) boxes[idx-1]?.focus();
    if(e.key==='ArrowRight'&&idx<5) boxes[idx+1]?.focus();
  },
  _getOtp() { return [...document.querySelectorAll('.otp-box')].map(b=>b.value).join(''); },
  _clearOtp() {
    document.querySelectorAll('.otp-box').forEach(b=>{b.value='';b.classList.remove('filled');});
    setTimeout(()=>document.querySelectorAll('.otp-box')[0]?.focus(),80);
  },

  async register() {
    const name=document.getElementById('reg-name')?.value.trim()||'';
    const email=document.getElementById('reg-email')?.value.trim().toLowerCase()||'';
    const pw=document.getElementById('reg-pw')?.value||'';
    const err=document.getElementById('reg-err');
    if(err) err.textContent='';
    if(!name)  {if(err)err.textContent='⚠ Name required';return;}
    if(!email) {if(err)err.textContent='⚠ Email required';return;}
    if(!pw)    {if(err)err.textContent='⚠ Password required';return;}
    const btn=document.getElementById('reg-btn');
    if(btn){btn.disabled=true;btn.textContent='⏳ Sending OTP...';}
    try {
      const res=await fetch('/api/auth/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email,password:pw,name})});
      const data=await res.json();
      if(!res.ok) throw new Error(data.error||'Registration failed');
      _otpType='register'; _otpEmail=email;
      this._gotoOtp(email);
    } catch(e) {
      if(err)err.textContent='⚠ '+e.message;
    } finally {
      if(btn){btn.disabled=false;btn.textContent='Create Account →';}
    }
  },

  async login() {
    const email=document.getElementById('login-email')?.value.trim().toLowerCase()||'';
    const pw=document.getElementById('login-pw')?.value||'';
    const err=document.getElementById('login-err');
    if(err)err.textContent='';
    if(!email||!pw){if(err)err.textContent='⚠ Email and password required';return;}
    const btn=document.getElementById('login-btn');
    if(btn){btn.disabled=true;btn.textContent='⏳ Sending OTP...';}
    try {
      const res=await fetch('/api/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email,password:pw})});
      const data=await res.json();
      if(!res.ok) throw new Error(data.error||'Login failed');
      _otpType='login'; _otpEmail=email;
      this._gotoOtp(email);
    } catch(e) {
      if(err)err.textContent='⚠ '+e.message;
    } finally {
      if(btn){btn.disabled=false;btn.textContent='Continue →';}
    }
  },

  _gotoOtp(email) {
    console.log('[AUTH] Going to OTP screen for:', email);
    // Hide all screens
    document.querySelectorAll('.screen').forEach(s=>{s.classList.add('hidden');s.style.cssText='';});
    // Show OTP screen forcefully
    const otp=document.getElementById('screen-otp');
    if(!otp){ alert('OTP screen not found in HTML!'); return; }
    otp.classList.remove('hidden');
    otp.style.display='flex';
    otp.style.flexDirection='column';
    otp.style.alignItems='center';
    otp.style.justifyContent='center';
    otp.style.position='fixed';
    otp.style.inset='0';
    otp.style.background='var(--bg,#fff)';
    otp.style.zIndex='9998';
    otp.style.padding='20px';
    // Set email
    const lbl=document.getElementById('otp-email-lbl');
    if(lbl) lbl.textContent=email;
    // Clear boxes
    this._clearOtp();
    // Clear error
    const otpErr=document.getElementById('otp-err');
    if(otpErr) otpErr.textContent='';
    // Start timer
    this._startTimer(30);
    console.log('[AUTH] ✅ OTP screen visible');
  },

  _startTimer(secs) {
    clearInterval(_resendInt);
    let rem=secs;
    const tEl=document.getElementById('resend-timer');
    const rBtn=document.getElementById('resend-btn');
    if(tEl){tEl.classList.remove('hidden');tEl.textContent='Resend in '+rem+'s';}
    if(rBtn) rBtn.classList.add('hidden');
    _resendInt=setInterval(()=>{
      rem--;
      if(rem<=0){
        clearInterval(_resendInt);
        if(tEl) tEl.classList.add('hidden');
        if(rBtn) rBtn.classList.remove('hidden');
      } else {
        if(tEl) tEl.textContent='Resend in '+rem+'s';
      }
    },1000);
  },

  async verifyOtp() {
    const otp=this._getOtp();
    const err=document.getElementById('otp-err');
    if(err) err.textContent='';
    if(otp.length!==6){if(err)err.textContent='⚠ Enter all 6 digits';return;}
    const btn=document.getElementById('otp-btn');
    if(btn){btn.disabled=true;btn.textContent='⏳ Verifying...';}
    try {
      const endpoint=_otpType==='register'?'/api/auth/verify-register':'/api/auth/verify-login';
      const res=await fetch(endpoint,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:_otpEmail,otp})});
      const data=await res.json();
      if(!res.ok) throw new Error(data.error||'Verification failed');
      localStorage.setItem('ngb_token',data.token);
      localStorage.setItem('ngb_user',JSON.stringify(data.user||{uid:data.uid,name:data.name,emoji:data.emoji||'👤'}));
      clearInterval(_resendInt);
      if(window.app&&window.app.init) await window.app.init(true);
      else window.location.reload();
    } catch(e) {
      if(err)err.textContent='⚠ '+e.message;
      this._clearOtp();
      document.querySelectorAll('.otp-box').forEach(b=>{b.classList.add('shake');setTimeout(()=>b.classList.remove('shake'),500);});
    } finally {
      if(btn){btn.disabled=false;btn.textContent='Verify →';}
    }
  },

  async resendOtp() {
    try {
      const res=await fetch('/api/auth/resend-otp',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:_otpEmail})});
      const data=await res.json();
      if(!res.ok) throw new Error(data.error);
      this._clearOtp();
      this._startTimer(30);
      toast('OTP resent! Check email + server console 📧');
    } catch(e) { toast('Error: '+e.message,'err'); }
  },

  backToAuth() {
    clearInterval(_resendInt);
    document.querySelectorAll('.screen').forEach(s=>{s.classList.add('hidden');s.style.cssText='';});
    const auth=document.getElementById('screen-auth');
    if(auth){auth.classList.remove('hidden');auth.style.display='flex';}
  },
};
window.authUI=authUI;

async function authLogout() {
  if(!confirm('Logout?')) return;
  try{ const t=localStorage.getItem('ngb_token'); if(t) await fetch('/api/auth/logout',{method:'POST',headers:{Authorization:'Bearer '+t}}); }catch{}
  localStorage.removeItem('ngb_token');
  localStorage.removeItem('ngb_user');
  if(window.socketEngine) socketEngine.disconnect();
  document.querySelectorAll('.screen').forEach(s=>{s.classList.add('hidden');s.style.cssText='';});
  const auth=document.getElementById('screen-auth');
  if(auth){auth.classList.remove('hidden');}
  toast('Logged out 👋');
}
window.authLogout=authLogout;

async function doLogout() {
  closeAll();
  await authLogout();
}
window.doLogout=doLogout;
""")


w("public/js/socket.js", """\
'use strict';
const socketEngine = {
  socket:null, handlers:{}, _conn:false,
  connect(token) {
    if(this.socket) {this.socket.disconnect();this.socket=null;}
    this.socket=io({auth:{token},transports:['websocket','polling'],reconnection:true,reconnectionAttempts:10,reconnectionDelay:1000,reconnectionDelayMax:30000,timeout:20000});
    this.socket.on('connect',()=>{this._conn=true;console.log('[Socket] Connected');});
    this.socket.on('disconnect',r=>{this._conn=false;console.log('[Socket] Disconnected:',r);});
    this.socket.on('reconnect',()=>{this._conn=true;toast('Reconnected ✓','ok');});
    this.socket.on('reconnect_failed',()=>toast('Connection failed. Refresh page.','err',5000));
    const evs=['private-message','typing','message-read','conversation-read','message-status','reaction-update','message-deleted','user-status','online-status'];
    evs.forEach(ev=>this.socket.on(ev,d=>(this.handlers[ev]||[]).forEach(fn=>fn(d))));
  },
  on(ev,fn)  { if(!this.handlers[ev]) this.handlers[ev]=[]; this.handlers[ev].push(fn); },
  off(ev,fn) { if(!this.handlers[ev]) return; this.handlers[ev]=fn?this.handlers[ev].filter(h=>h!==fn):[]; },
  emit(ev,d,ack) { if(!this.socket||!this._conn){console.warn('[Socket] Not connected for',ev);return;} ack?this.socket.emit(ev,d,ack):this.socket.emit(ev,d); },
  disconnect() { if(this.socket){this.socket.disconnect();this.socket=null;} },
  isConnected(){ return this._conn; },
};
window.socketEngine=socketEngine;
""")

w("public/js/chatList.js", """\
'use strict';
const chatList = {
  contacts:[], q:'',
  async init() {
    await this.load();
    this._bind();
    setInterval(()=>this.load(),30000);
  },
  async load() {
    try {
      const data=await api('/contacts');
      this.contacts=data;
      this.render();
    } catch(e) { console.warn('chatList.load:',e.message); }
  },
  render() {
    const el=document.getElementById('cl-list');
    if(!el) return;
    const myUid=store.user().uid;
    let list=this.contacts;
    if(this.q) list=list.filter(c=>c.name.toLowerCase().includes(this.q)||c.uid.includes(this.q));
    if(!list.length) {
      el.innerHTML='<div class="empty"><div class="empty-icon">💬</div><div class="empty-title">No chats yet</div><div class="empty-sub">Tap ➕ to add a contact</div></div>';
      return;
    }
    el.innerHTML=list.map(c => {
      const lm=c.lastMessage;
      const tick=lm&&lm.from===myUid ? (lm.status==='read'?'<span class="tick read">✓✓</span>':lm.status==='delivered'?'<span class="tick">✓✓</span>':'<span class="tick">✓</span>') : '';
      const preview=lm?(tick+(lm.type==='file'?'📎 File':esc(trunc(lm.text||'',45)))):(esc(c.customStatus||c.bio||''));
      const badge=c.unreadCount>0?'<span class="cl-badge">'+(c.unreadCount>99?'99+':c.unreadCount)+'</span>':'';
      const dot=c.online?'on':'off';
      return `<div class="cl-item" onclick="app.openChat('${c.uid}')">
        <div class="cl-avatar">${esc(c.emoji||'👤')}<div class="online-dot ${dot}"></div></div>
        <div class="cl-body">
          <div class="cl-name">${esc(c.name)}</div>
          <div class="cl-preview">${preview}</div>
        </div>
        <div class="cl-meta">
          <span class="cl-time">${lm?fmtTime(lm.timestamp):''}</span>
          ${badge}
        </div>
      </div>`;
    }).join('');
  },
  search(q) { this.q=q.toLowerCase().trim(); this.render(); },
  _bind() {
    socketEngine.on('private-message', msg => {
      const myUid=store.user().uid;
      const other=msg.from===myUid?msg.to:msg.from;
      const idx=this.contacts.findIndex(c=>c.uid===other);
      if(idx!==-1) {
        this.contacts[idx].lastMessage=msg;
        if(msg.from!==myUid) this.contacts[idx].unreadCount=(this.contacts[idx].unreadCount||0)+1;
        this.contacts.sort((a,b)=>(b.lastMessage?.timestamp||'').localeCompare(a.lastMessage?.timestamp||''));
        this.render();
        if(msg.from!==myUid&&(!chatUI.contactUid||chatUI.contactUid!==msg.from)) {
          const c=this.contacts[idx];
          if(window.Notification&&Notification.permission==='granted') {
            new Notification(c.name||msg.from,{body:trunc(msg.text||'📎 File',60)});
          }
        }
      }
    });
    socketEngine.on('user-status', data => {
      const idx=this.contacts.findIndex(c=>c.uid===data.uid);
      if(idx!==-1) { this.contacts[idx].online=data.online; this.contacts[idx].lastSeen=data.lastSeen; this.render(); }
    });
  },
  clearUnread(uid) {
    const idx=this.contacts.findIndex(c=>c.uid===uid);
    if(idx!==-1) { this.contacts[idx].unreadCount=0; this.render(); }
  },
};
window.chatList=chatList;
""")

w("public/js/chat.js", """\
'use strict';
const chatUI = {
  contactUid:null, contactData:null, msgs:[],
  replyTo:null, _typingTimer:null, _isTyping:false,

  async open(uid) {
    this.contactUid=uid; this.replyTo=null; this.msgs=[]; this._isTyping=false;
    const sc=document.getElementById('screen-chat');
    if(!sc) return;
    document.querySelectorAll('.screen').forEach(s=>s.classList.add('hidden'));
    sc.classList.remove('hidden');
    document.getElementById('msgs').innerHTML='';
    document.getElementById('reply-preview')?.classList.add('hidden');
    document.getElementById('typing-bar')?.classList.add('hidden');
    document.getElementById('attach-menu')?.classList.add('hidden');
    await this._loadContact(uid);
    await this._loadMsgs();
    const draft=store.draft(uid);
    const inp=document.getElementById('msg-input'); if(inp) inp.value=draft;
    socketEngine.emit('conversation-read',{contactUid:uid});
    api('/messages/read-conversation',{method:'POST',body:{contactUid:uid}}).catch(()=>{});
    socketEngine.emit('check-online',{uid});
  },

  async _loadContact(uid) {
    try {
      this.contactData=await api('/users/'+uid);
      const cd=this.contactData;
      document.getElementById('ch-avatar').textContent=cd.emoji||'👤';
      document.getElementById('ch-name').textContent=cd.name;
      this._updateStatus(cd);
    } catch { document.getElementById('ch-name').textContent=uid; }
  },

  _updateStatus(cd) {
    const el=document.getElementById('ch-status'); if(!el) return;
    if(cd.online){el.textContent='● online';el.className='ch-status online';}
    else{el.textContent=cd.lastSeen?'last seen '+fmtTime(cd.lastSeen):'offline';el.className='ch-status';}
  },

  async _loadMsgs(before=null) {
    try {
      const params=new URLSearchParams({limit:50}); if(before) params.set('before',before);
      const msgs=await api('/messages/'+this.contactUid+'?'+params);
      if(!before) { this.msgs=msgs; this._renderAll(); this._scrollBottom(false); }
      else {
        const c=document.getElementById('msgs'); const prev=c.scrollHeight;
        this.msgs=[...msgs,...this.msgs]; this._prependMsgs(msgs);
        c.scrollTop=c.scrollHeight-prev;
      }
    } catch(e) { toast(e.message,'err'); }
  },

  _renderAll() {
    const c=document.getElementById('msgs'); if(!c) return;
    c.innerHTML='';
    const myUid=store.user().uid;
    let lastDate=null;
    this.msgs.forEach(m => {
      const d=new Date(m.timestamp).toDateString();
      if(d!==lastDate){ lastDate=d; const s=document.createElement('div'); s.className='date-sep'; s.innerHTML='<span>'+fmtDate(m.timestamp)+'</span>'; c.appendChild(s); }
      c.appendChild(this._buildRow(m,myUid));
    });
  },

  _prependMsgs(msgs) {
    const c=document.getElementById('msgs'); const myUid=store.user().uid;
    const frag=document.createDocumentFragment();
    msgs.forEach(m=>frag.appendChild(this._buildRow(m,myUid)));
    c.insertBefore(frag,c.firstChild);
  },

  _buildRow(msg, myUid) {
    const isMine=msg.from===myUid;
    const row=document.createElement('div');
    row.className='msg-row '+(isMine?'me':'them');
    row.dataset.id=msg.id;
    if((msg.deletedFor||[]).includes(myUid)){row.style.display='none';return row;}
    const bubble=document.createElement('div');
    bubble.className='bubble'+(msg.deleted?' deleted':'');
    let html='';
    if(msg.deleted) { html='🚫 Message deleted'; }
    else {
      if(msg.replyTo) {
        const orig=this.msgs.find(m=>m.id===msg.replyTo);
        if(orig) {
          const rn=orig.from===myUid?'You':(this.contactData?.name||orig.from);
          html+='<div class="reply-block" onclick="chatUI._scrollTo(\''+orig.id+'\')"><div class="rb-name">'+esc(rn)+'</div><div class="rb-txt">'+esc(trunc(orig.text||'📎',55))+'</div></div>';
        }
      }
      if(msg.type==='file'&&msg.fileUrl) { html+=this._buildFile(msg); }
      else { html+='<span>'+nl2br(linkify(esc(msg.text||'')))+'</span>'; }
      if(msg.edited) html+='<span style="font-size:10px;opacity:.5;font-style:italic"> edited</span>';
    }
    const tick=isMine?(msg.status==='read'?'<span class="tick read">✓✓</span>':msg.status==='delivered'?'<span class="tick">✓✓</span>':'<span class="tick">✓</span>'):'';
    html+='<div class="msg-meta"><span>'+fmtTime(msg.timestamp)+'</span>'+tick+'</div>';
    if(msg.reactions&&Object.keys(msg.reactions).length) html+=this._buildReactions(msg.reactions,myUid,msg.id);
    bubble.innerHTML=html;
    bubble.addEventListener('contextmenu',e=>{e.preventDefault();this._ctxMenu(e,msg,isMine);});
    bubble.addEventListener('touchstart',e=>{ let t=setTimeout(()=>this._ctxMenu(e,msg,isMine),500); bubble.addEventListener('touchend',()=>clearTimeout(t),{once:true}); bubble.addEventListener('touchmove',()=>clearTimeout(t),{once:true}); },{passive:true});
    row.appendChild(bubble);
    return row;
  },

  _buildFile(msg) {
    const s=fmtSize(msg.fileSize||0); const n=esc(msg.fileName||'File');
    if(isImg(msg.fileType)) return '<img src="'+msg.fileUrl+'" style="max-width:220px;border-radius:12px;cursor:pointer" onclick="mediaViewer.open(\''+msg.fileUrl+'\',\'image\',\''+n+'\')" loading="lazy"><div style="font-size:11px;opacity:.6;margin-top:3px">'+s+'</div>';
    if(isVid(msg.fileType)) return '<video src="'+msg.fileUrl+'" style="max-width:220px;border-radius:12px" controls></video><div style="font-size:11px;opacity:.6;margin-top:3px">'+s+'</div>';
    if(isAud(msg.fileType)) return '<audio src="'+msg.fileUrl+'" controls style="max-width:220px"></audio>';
    const ico=fileIcon(msg.fileName||'',msg.fileType||'');
    return '<div class="file-bubble"><div class="file-icon">'+ico+'</div><div class="file-info"><div class="file-name">'+n+'</div><div class="file-size">'+s+'</div><a class="file-dl" href="'+msg.fileUrl+'" download="'+n+'">⬇ Download</a></div></div>';
  },

  _buildReactions(reactions,myUid,msgId) {
    let html='<div class="reactions">';
    Object.entries(reactions).forEach(([emoji,uids])=>{
      if(!uids||!uids.length) return;
      const mine=uids.includes(myUid);
      html+='<span class="react-chip'+(mine?' me-react':'')+'" onclick="chatUI.react(\''+msgId+'\',\''+emoji+'\')">'+emoji+'<span class="react-count">'+uids.length+'</span></span>';
    });
    return html+'</div>';
  },

  _ctxMenu(e,msg,isMine) {
    closeAll();
    const menu=document.getElementById('ctx-menu'); if(!menu) return;
    const myUid=store.user().uid;
    let items='';
    if(!msg.deleted) {
      items+='<div class="ctx-item" onclick="closeAll();chatUI.reply(\''+msg.id+'\')">↩️ Reply</div>';
      if(msg.text) items+='<div class="ctx-item" onclick="closeAll();copyTxt('+JSON.stringify(msg.text||'')+');toast(\'Copied!\')">📋 Copy</div>';
      items+='<div class="ctx-sep"></div>';
      if(msg.text) {
        items+='<div class="ctx-item" onclick="closeAll();chatUI._quickReact(\''+msg.id+'\')">😊 React</div>';
      }
    }
    if(isMine&&!msg.deleted) items+='<div class="ctx-item danger" onclick="closeAll();chatUI.delForAll(\''+msg.id+'\')">🗑 Delete for Everyone</div>';
    items+='<div class="ctx-item" onclick="closeAll();chatUI.delForMe(\''+msg.id+'\')">🗑 Delete for Me</div>';
    menu.innerHTML=items;
    const bd=document.getElementById('backdrop'); if(bd) bd.style.display='block';
    let x=e.clientX||(e.touches&&e.touches[0]?e.touches[0].clientX:100);
    let y=e.clientY||(e.touches&&e.touches[0]?e.touches[0].clientY:200);
    if(x+200>window.innerWidth) x=window.innerWidth-210;
    if(y+200>window.innerHeight) y=window.innerHeight-210;
    menu.style.left=x+'px'; menu.style.top=y+'px';
    menu.classList.remove('hidden');
  },

  _quickReact(msgId) {
    const emojis=['👍','❤️','😂','😮','😢','😡','🔥','🎉'];
    const menu=document.getElementById('ctx-menu'); if(!menu) return;
    menu.innerHTML='<div style="display:flex;gap:2px;padding:8px 6px">'+ emojis.map(e=>'<span onclick="closeAll();chatUI.react(\''+msgId+'\',\''+e+'\')" style="font-size:26px;cursor:pointer;padding:6px;border-radius:8px;transition:background .12s" onmouseover="this.style.background=\'var(--bg3)\'" onmouseout="this.style.background=\'\'">'+e+'</span>').join('') +'</div>';
    menu.classList.remove('hidden');
  },

  addIncoming(msg) {
    const myUid=store.user().uid;
    if(msg.from!==this.contactUid&&msg.to!==this.contactUid) return;
    this.msgs.push(msg);
    const c=document.getElementById('msgs'); if(!c) return;
    const row=this._buildRow(msg,myUid);
    const lastSep=c.lastElementChild;
    const d=new Date(msg.timestamp).toDateString();
    const prevMsg=this.msgs[this.msgs.length-2];
    if(!prevMsg||new Date(prevMsg.timestamp).toDateString()!==d){
      const sep=document.createElement('div'); sep.className='date-sep'; sep.innerHTML='<span>'+fmtDate(msg.timestamp)+'</span>'; c.appendChild(sep);
    }
    c.appendChild(row);
    const nearBottom=c.scrollHeight-c.scrollTop-c.clientHeight<120;
    if(nearBottom) { this._scrollBottom(true); if(msg.from===this.contactUid) socketEngine.emit('message-read',{messageId:msg.id,from:msg.from}); }
  },

  updateMsgStatus(tempId,newId,status) {
    const row=document.querySelector('.msg-row[data-id="'+tempId+'"]');
    if(row) { row.dataset.id=newId; const tick=row.querySelector('.tick'); if(tick){tick.className='tick '+(status==='read'?'read':'');tick.textContent=status==='read'?'✓✓':status==='delivered'?'✓✓':'✓';} }
  },

  _scrollBottom(smooth=true) {
    const c=document.getElementById('msgs'); if(c) c.scrollTo({top:c.scrollHeight,behavior:smooth?'smooth':'auto'});
  },
  _scrollTo(id) {
    const el=document.querySelector('.msg-row[data-id="'+id+'"]');
    if(el){el.scrollIntoView({behavior:'smooth',block:'center'});el.querySelector('.bubble')?.classList.add('shake');setTimeout(()=>el.querySelector('.bubble')?.classList.remove('shake'),500);}
  },
  onScroll() {
    const c=document.getElementById('msgs'); if(!c) return;
    if(c.scrollTop<60&&this.msgs.length>=50) { const oldest=this.msgs[0]; if(oldest) this._loadMsgs(oldest.timestamp); }
  },

  async send() {
    const inp=document.getElementById('msg-input');
    const text=(inp?.value||'').trim();
    if(!text) return;
    inp.value=''; inp.style.height='';
    store.setDraft(this.contactUid,'');
    this._stopTyping();
    const tempId=uuid(); const myUid=store.user().uid; const myUser=store.user();
    const tempMsg={id:tempId,from:myUid,to:this.contactUid,text,status:'sending',timestamp:new Date().toISOString(),type:'text',replyTo:this.replyTo?.id||null,deleted:false,deletedFor:[],reactions:{},tempId};
    this.msgs.push(tempMsg);
    document.getElementById('msgs')?.appendChild(this._buildRow(tempMsg,myUid));
    this._scrollBottom(true);
    this.cancelReply();
    socketEngine.emit('private-message',{to:this.contactUid,text,replyTo:this.replyTo?.id||null,tempId,type:'text'},(ack)=>{
      if(ack?.id){const idx=this.msgs.findIndex(m=>m.tempId===tempId); if(idx!==-1){this.msgs[idx]={...this.msgs[idx],id:ack.id,status:ack.status}; this.updateMsgStatus(tempId,ack.id,ack.status);}}
    });
  },

  onInput(el) {
    el.style.height='auto'; el.style.height=Math.min(el.scrollHeight,120)+'px';
    store.setDraft(this.contactUid,el.value);
    this._sendTyping(!!el.value.trim());
    const btn=document.getElementById('send-btn');
    if(btn) btn.textContent=el.value.trim()?'➤':'🎤';
  },
  onKeyDown(e) {
    if(e.key==='Enter'&&!e.shiftKey&&store.settings().enterToSend&&window.innerWidth>600){e.preventDefault();this.send();}
  },

  _sendTyping(on) {
    if(on===this._isTyping) return;
    this._isTyping=on;
    socketEngine.emit('typing',{to:this.contactUid,isTyping:on});
    if(on){clearTimeout(this._typingTimer);this._typingTimer=setTimeout(()=>this._stopTyping(),2500);}
  },
  _stopTyping() { if(this._isTyping){this._isTyping=false;socketEngine.emit('typing',{to:this.contactUid,isTyping:false});} clearTimeout(this._typingTimer); },

  reply(msgId) {
    const msg=this.msgs.find(m=>m.id===msgId); if(!msg) return;
    this.replyTo=msg;
    const myUid=store.user().uid;
    document.getElementById('rp-name').textContent=msg.from===myUid?'You':(this.contactData?.name||msg.from);
    document.getElementById('rp-text').textContent=trunc(msg.text||'📎',60);
    document.getElementById('reply-preview')?.classList.remove('hidden');
    document.getElementById('msg-input')?.focus();
  },
  cancelReply() { this.replyTo=null; document.getElementById('reply-preview')?.classList.add('hidden'); },

  react(msgId,emoji) {
    socketEngine.emit('react',{messageId:msgId,emoji});
    api('/messages/'+msgId+'/react',{method:'POST',body:{emoji}}).then(d=>{
      const idx=this.msgs.findIndex(m=>m.id===msgId);
      if(idx!==-1){this.msgs[idx].reactions=d.reactions; const row=document.querySelector('.msg-row[data-id="'+msgId+'"]'); if(row){const ex=row.querySelector('.reactions'); const myUid=store.user().uid; const html=this._buildReactions(d.reactions,myUid,msgId); if(ex)ex.outerHTML=html; else row.querySelector('.bubble')?.insertAdjacentHTML('beforeend',html);}}
    }).catch(()=>{});
  },

  delForMe(id)   { api('/messages/'+id,{method:'DELETE',body:{forEveryone:false}}).then(()=>{this.msgs=this.msgs.filter(m=>m.id!==id);this._renderAll();}).catch(e=>toast(e.message,'err')); },
  delForAll(id)  { api('/messages/'+id,{method:'DELETE',body:{forEveryone:true}}).then(()=>{const idx=this.msgs.findIndex(m=>m.id===id); if(idx!==-1){this.msgs[idx].deleted=true;this.msgs[idx].text='';this._renderAll();}}).catch(e=>toast(e.message,'err')); },

  async clearChat() { closeAll(); if(!confirm('Clear all messages?')) return; await api('/messages/clear/'+this.contactUid,{method:'DELETE'}); this.msgs=[]; this._renderAll(); toast('Chat cleared'); },
  async exportChat() { closeAll(); try{const res=await api('/messages/export/'+this.contactUid); const b=await res.blob(); const a=document.createElement('a'); a.href=URL.createObjectURL(b); a.download='chat_'+this.contactUid+'.txt'; a.click(); toast('Exported!');}catch(e){toast(e.message,'err');} },

  openProfile()  { if(this.contactUid) contactProfile.open(this.contactUid); },

  toggleAttach() {
    const m=document.getElementById('attach-menu');
    if(!m) return;
    if(m.classList.contains('hidden')) m.classList.remove('hidden');
    else m.classList.add('hidden');
  },
  pickFile(accept) {
    document.getElementById('attach-menu')?.classList.add('hidden');
    const fp=document.getElementById('file-picker');
    if(fp){fp.accept=accept;fp.click();}
  },
  async onFilePicked(e) {
    const files=e.target.files; if(!files.length) return;
    for(const file of files) await this._uploadFile(file);
    e.target.value='';
  },
  async _uploadFile(file) {
    if(file.size>50*1024*1024){toast('File too large (max 50MB)','err');return;}
    const fd=new FormData(); fd.append('file',file); fd.append('to',this.contactUid);
    const tempId=uuid(); const myUid=store.user().uid;
    const tempMsg={id:tempId,from:myUid,to:this.contactUid,text:'',status:'sending',timestamp:new Date().toISOString(),type:'file',fileName:file.name,fileType:file.type,fileSize:file.size,deleted:false,deletedFor:[],reactions:{},tempId};
    this.msgs.push(tempMsg);
    document.getElementById('msgs')?.appendChild(this._buildRow(tempMsg,myUid));
    this._scrollBottom(true);
    const token=localStorage.getItem('ngb_token');
    try {
      const res=await fetch('/api/messages/file',{method:'POST',headers:{Authorization:'Bearer '+token},body:fd});
      const msg=await res.json();
      if(!res.ok) throw new Error(msg.error||'Upload failed');
      const idx=this.msgs.findIndex(m=>m.tempId===tempId);
      if(idx!==-1){this.msgs[idx]={...msg};this._renderAll();}
      socketEngine.emit('private-message',{to:this.contactUid,text:'📎 '+file.name,type:'file',fileUrl:msg.fileUrl,tempId:uuid()});
    } catch(e) { toast(e.message,'err'); this.msgs=this.msgs.filter(m=>m.tempId!==tempId); this._renderAll(); }
  },
};
window.chatUI=chatUI;
""")


w("public/js/contacts.js", """\
'use strict';
const addContact = {
  found:null,
  init() { const el=document.getElementById('my-id-val'); if(el) el.textContent=store.user().uid||''; },
  lookup:debounce(async function(val){
    const uid=val.trim().toLowerCase();
    const prev=document.getElementById('uid-preview'); const btn=document.getElementById('add-btn'); const err=document.getElementById('add-err');
    if(prev) prev.classList.add('hidden'); if(btn) btn.classList.add('hidden'); if(err) err.textContent=''; addContact.found=null;
    if(uid.length<3||!uid.startsWith('ngb')) return;
    try {
      const user=await api('/users/'+uid);
      addContact.found=user;
      if(prev){prev.innerHTML='<div class="uid-prev-av">'+esc(user.emoji||'👤')+'</div><div><div class="uid-prev-name">'+esc(user.name)+'</div><div class="uid-prev-uid">'+esc(user.uid)+'</div></div>'; prev.classList.remove('hidden');}
      if(btn) btn.classList.remove('hidden');
    } catch(e) { if(uid.length===10&&err) err.textContent='User not found. Check the ID.'; }
  },400),
  async add() {
    if(!addContact.found) return;
    const btn=document.getElementById('add-btn');
    if(btn){btn.disabled=true;btn.textContent='Adding...';}
    try {
      await api('/contacts/add',{method:'POST',body:{uid:addContact.found.uid}});
      toast(addContact.found.name+' added! 🎉','ok');
      chatList.load();
      const inp=document.getElementById('add-uid'); if(inp) inp.value='';
      const prev=document.getElementById('uid-preview'); if(prev) prev.classList.add('hidden');
      if(btn) btn.classList.add('hidden');
      addContact.found=null;
      setTimeout(()=>nav.back(),600);
    } catch(e) { toast(e.message,'err'); }
    finally { if(btn){btn.disabled=false;btn.textContent='Add Contact ✓';} }
  },
  copyMyId() { copyTxt(store.user().uid||''); toast('Your NGB ID copied! 🔗','ok'); },
};
window.addContact=addContact;
""")

w("public/js/profile.js", """\
'use strict';
const myProfile = {
  _status:'available',
  async init() {
    const user=store.user();
    const el=document.getElementById('my-profile-av'); if(el) el.textContent=user.emoji||'👤';
    const uel=document.getElementById('profile-uid-val'); if(uel) uel.textContent=user.uid||'';
    try {
      const fresh=await api('/users/me');
      store.setUser(fresh);
      const e=v=>document.getElementById(v);
      e('pf-name')&&(e('pf-name').value=fresh.name||'');
      e('pf-bio')&&(e('pf-bio').value=fresh.bio||'');
      e('pf-status-txt')&&(e('pf-status-txt').value=fresh.customStatus||'');
      if(el) el.textContent=fresh.emoji||'👤';
      if(uel) uel.textContent=fresh.uid||'';
      this._status=fresh.status||'available';
      document.querySelectorAll('.status-chip').forEach(b=>{
        b.classList.toggle('active',b.dataset.status===this._status);
      });
    } catch{}
  },
  setStatus(s,btn) {
    this._status=s;
    document.querySelectorAll('.status-chip').forEach(b=>b.classList.remove('active'));
    if(btn) btn.classList.add('active');
  },
  async save() {
    const g=id=>document.getElementById(id)?.value||'';
    const body={name:g('pf-name').trim(),bio:g('pf-bio').trim(),customStatus:g('pf-status-txt').trim(),status:this._status};
    if(!body.name){toast('Name required','err');return;}
    try {
      const updated=await api('/users/profile',{method:'PUT',body});
      const user=store.user(); store.setUser({...user,...updated});
      const av=document.getElementById('my-avatar'); if(av) av.textContent=store.user().emoji||'👤';
      toast('Profile saved ✓','ok');
    } catch(e){toast(e.message,'err');}
  },
  copyUid() { copyTxt(store.user().uid||''); toast('NGB ID copied!','ok'); },
  changeEmoji() {
    const emojis=['👤','😊','😎','🦁','🐯','🦊','🐻','🦄','🐸','🐙','🌟','🔥','💎','🎭','🚀','🌈','🎨','🎪','💫','⚡'];
    const d=document.createElement('div');
    d.style.cssText='position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:800;display:flex;align-items:center;justify-content:center;';
    d.innerHTML='<div style="background:var(--bg);border-radius:20px;padding:24px;max-width:320px;width:90%"><div style="font-weight:800;font-size:16px;margin-bottom:16px;text-align:center">Choose Avatar</div><div style="display:flex;flex-wrap:wrap;gap:6px;justify-content:center">'+emojis.map(e=>'<span onclick="myProfile._pickEmoji(\''+e+'\',this.closest(\'[style]\'))" style="font-size:34px;cursor:pointer;padding:7px;border-radius:10px;transition:background .1s" onmouseover="this.style.background=\'var(--bg3)\'" onmouseout="this.style.background=\'\'">'+e+'</span>').join('')+'</div></div>';
    d.onclick=ev=>{if(ev.target===d)d.remove();};
    document.body.appendChild(d);
  },
  _pickEmoji(emoji,sheet) {
    if(sheet) sheet.remove();
    const av=document.getElementById('my-profile-av'); if(av) av.textContent=emoji;
    const mav=document.getElementById('my-avatar'); if(mav) mav.textContent=emoji;
    api('/users/profile',{method:'PUT',body:{emoji}}).then(()=>{const u=store.user(); store.setUser({...u,emoji}); toast('Avatar updated!','ok');}).catch(()=>{});
  },
  async changePw() {
    const cur=document.getElementById('cp-cur')?.value||'';
    const nw=document.getElementById('cp-new')?.value||'';
    const cf=document.getElementById('cp-confirm')?.value||'';
    const err=document.getElementById('cp-err');
    if(err) err.textContent='';
    if(!cur||!nw||!cf){if(err)err.textContent='All fields required';return;}
    if(nw!==cf){if(err)err.textContent='Passwords do not match';return;}
    if(nw.length<8){if(err)err.textContent='Min 8 characters';return;}
    try {
      await api('/users/change-password',{method:'PUT',body:{currentPassword:cur,newPassword:nw}});
      toast('Password changed! 🔑','ok');
      ['cp-cur','cp-new','cp-confirm'].forEach(id=>{const el=document.getElementById(id);if(el)el.value='';});
      nav.back();
    } catch(e){if(err)err.textContent=e.message;}
  },
  async deleteAccount() {
    if(!confirm('Delete your account? This cannot be undone!')) return;
    const pw=prompt('Enter your password:'); if(!pw) return;
    try { await api('/users/account',{method:'DELETE',body:{password:pw}}); localStorage.clear(); window.location.reload(); }
    catch(e){toast(e.message,'err');}
  },
};
window.myProfile=myProfile;

const contactProfile = {
  uid:null, user:null,
  async open(uid) {
    this.uid=uid;
    const sc=document.getElementById('screen-contact-profile');
    const body=document.getElementById('contact-profile-body');
    if(!sc||!body) return;
    document.querySelectorAll('.screen').forEach(s=>s.classList.add('hidden'));
    sc.classList.remove('hidden'); sc.classList.add('slide-screen');
    setTimeout(()=>sc.classList.add('visible'),10);
    body.innerHTML='<div class="empty"><div style="font-size:40px">⏳</div></div>';
    try {
      const user=await api('/users/'+uid);
      this.user=user;
      const isContact=(store.user().contacts||[]).includes(uid);
      const statusDot={available:'🟢',away:'🟡',busy:'🔴',invisible:'⚫'}[user.status]||'⚫';
      body.innerHTML=`<div class="cpf-top">
        <div class="cpf-avatar">${esc(user.emoji||'👤')}</div>
        <div class="cpf-name">${esc(user.name)}</div>
        <div class="cpf-uid" onclick="copyTxt('${esc(user.uid)}');toast('UID copied!')">${esc(user.uid)} 📋</div>
        ${user.bio?'<div class="cpf-bio">'+esc(user.bio)+'</div>':''}
        ${user.customStatus?'<div style="font-size:13px;color:var(--fg4);font-style:italic;margin-top:6px">"'+esc(user.customStatus)+'"</div>':''}
        <div style="display:flex;align-items:center;gap:6px;margin-top:10px;font-size:13px;color:var(--fg4)">${statusDot} ${esc(user.status||'available')} ${user.online?'· 🟢 Online':'· Last seen '+fmtTime(user.lastSeen)}</div>
        <div class="cpf-actions">
          <div class="cpf-action" onclick="app.openChat('${uid}');"><span>💬</span><span>Message</span></div>
          ${!isContact?'<div class="cpf-action" onclick="contactProfile.addToContacts()"><span>➕</span><span>Add Contact</span></div>':''}
          <div class="cpf-action" onclick="contactProfile.blockUser()"><span>🚫</span><span>Block</span></div>
          <div class="cpf-action danger" onclick="contactProfile.clearChat()"><span>🗑</span><span>Clear Chat</span></div>
        </div>
      </div>`;
    } catch(e){ body.innerHTML='<div class="empty"><div class="empty-icon">❌</div><div class="empty-title">'+esc(e.message)+'</div></div>'; }
  },
  async addToContacts() {
    try { await api('/contacts/add',{method:'POST',body:{uid:this.uid}}); toast('Contact added!','ok'); chatList.load(); }
    catch(e){toast(e.message,'err');}
  },
  async blockUser() {
    try { const r=await api('/users/block',{method:'POST',body:{uid:this.uid}}); toast('User '+r.action,'ok'); }
    catch(e){toast(e.message,'err');}
  },
  async clearChat() {
    if(!confirm('Clear all messages with this contact?')) return;
    try { await api('/messages/clear/'+this.uid,{method:'DELETE'}); toast('Chat cleared','ok'); chatList.load(); nav.back(); }
    catch(e){toast(e.message,'err');}
  },
};
window.contactProfile=contactProfile;
""")

w("public/js/mediaViewer.js", """\
'use strict';
const mediaViewer = {
  _zoom:1, _tx:0, _ty:0, _url:'', _type:'', _name:'',
  open(url,type='image',name='') {
    this._url=url; this._type=type; this._name=name; this._zoom=1; this._tx=0; this._ty=0;
    const mv=document.getElementById('media-viewer'); if(!mv) return;
    const inner=document.getElementById('mv-inner'); if(!inner) return;
    if(type==='image') inner.innerHTML='<img src="'+url+'" alt="'+esc(name)+'">';
    else if(type==='video') inner.innerHTML='<video src="'+url+'" controls autoplay></video>';
    else inner.innerHTML='<div style="color:#fff;text-align:center;padding:40px"><div style="font-size:60px">📎</div><div style="margin-top:12px">'+esc(name)+'</div><a href="'+url+'" download="'+esc(name)+'" style="color:#aaa;display:block;margin-top:8px">⬇ Download</a></div>';
    document.getElementById('mv-title').textContent=name||'Media';
    mv.classList.remove('hidden');
    document.addEventListener('keydown',this._keyDown);
    // Pinch zoom for touch
    const stage=document.getElementById('mv-body');
    let initDist=0, initZoom=1;
    stage.addEventListener('touchstart',e=>{ if(e.touches.length===2){ initDist=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY); initZoom=this._zoom; } },{passive:true});
    stage.addEventListener('touchmove',e=>{ if(e.touches.length===2){ e.preventDefault(); const d=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY); this._zoom=Math.max(.5,Math.min(5,initZoom*(d/initDist))); this._apply(); } },{passive:false});
  },
  close() {
    const mv=document.getElementById('media-viewer'); if(mv) mv.classList.add('hidden');
    const inner=document.getElementById('mv-inner'); if(inner){const v=inner.querySelector('video'); if(v){v.pause();v.src='';} inner.innerHTML='';}
    document.removeEventListener('keydown',this._keyDown);
  },
  _apply() { const inner=document.getElementById('mv-inner'); if(inner) inner.style.transform='translate('+this._tx+'px,'+this._ty+'px) scale('+this._zoom+')'; },
  zoomIn()    { this._zoom=Math.min(this._zoom*1.3,5); this._apply(); },
  zoomOut()   { this._zoom=Math.max(this._zoom/1.3,.3); this._apply(); },
  zoomReset() { this._zoom=1; this._tx=0; this._ty=0; this._apply(); },
  download()  { const a=document.createElement('a'); a.href=this._url; a.download=this._name||'file'; a.click(); },
  _keyDown: null,
};
mediaViewer._keyDown = e => {
  if(!document.getElementById('media-viewer')?.classList.contains('hidden')) {
    if(e.key==='Escape') mediaViewer.close();
    if(e.key==='+'||e.key==='=') mediaViewer.zoomIn();
    if(e.key==='-') mediaViewer.zoomOut();
    if(e.key==='0') mediaViewer.zoomReset();
  }
};
window.mediaViewer=mediaViewer;
""")

w("public/js/main.js", """\
'use strict';

// ── Navigation ───────────────────────────────────────────────
const nav = {
  _stack:[],
  go(screen) {
    this._stack.push(screen);
    document.querySelectorAll('.screen').forEach(s=>{s.classList.add('hidden');s.style.cssText='';});
    const sc=document.getElementById('screen-'+screen);
    if(!sc) return;
    sc.classList.remove('hidden');
    if(sc.classList.contains('slide-screen')){
      sc.style.transform='translateX(100%)'; sc.style.transition='';
      requestAnimationFrame(()=>{ sc.style.transition='transform .28s cubic-bezier(.4,0,.2,1)'; sc.style.transform='translateX(0)'; });
    }
    this._onNav(screen);
  },
  back() {
    this._stack.pop();
    const prev=this._stack[this._stack.length-1]||'chatlist';
    document.querySelectorAll('.screen').forEach(s=>{s.classList.add('hidden');s.style.cssText='';});
    const sc=document.getElementById('screen-'+prev);
    if(sc) sc.classList.remove('hidden');
    this._onNav(prev);
  },
  _onNav(screen) {
    switch(screen) {
      case 'add-contact':     addContact.init(); break;
      case 'my-profile':      myProfile.init(); break;
      case 'chatlist':        chatList.load(); break;
    }
  },
};
window.nav=nav;

// ── App Init ─────────────────────────────────────────────────
const app = {
  async init(fresh=false) {
    const token=localStorage.getItem('ngb_token');
    if(!token||this._tokenExpired(token)) {
      this._hideSplash(); this._showAuth(); return;
    }
    try {
      const user=await api('/users/me');
      store.setUser(user);
      // Update header
      const av=document.getElementById('my-avatar'); if(av) av.textContent=user.emoji||'👤';
      const uid=document.getElementById('my-uid-tag'); if(uid) uid.textContent=user.uid||'';
      // Connect socket
      socketEngine.connect(token);
      // Bind events
      this._bindSocket();
      // Load chat list
      await chatList.init();
      // Init push notifications
      if('Notification' in window && Notification.permission==='default') Notification.requestPermission().catch(()=>{});
      // Theme
      const theme=user.settings?.theme||'light';
      document.documentElement.setAttribute('data-theme',theme);
      this._hideSplash();
      this._showChatList();
    } catch(e) {
      console.error('[APP] Init error:',e.message);
      this._hideSplash(); this._showAuth();
    }
  },

  _bindSocket() {
    socketEngine.on('private-message', msg => {
      const myUid=store.user().uid;
      if(chatUI.contactUid&&(msg.from===chatUI.contactUid||msg.to===chatUI.contactUid)) {
        chatUI.addIncoming(msg);
        if(msg.from===chatUI.contactUid) {
          socketEngine.emit('message-read',{messageId:msg.id,from:msg.from});
          chatList.clearUnread(msg.from);
        }
      }
    });

    socketEngine.on('user-status', data => {
      if(chatUI.contactUid&&data.uid===chatUI.contactUid) chatUI._updateStatus(data);
    });

    socketEngine.on('online-status', data => {
      if(chatUI.contactUid&&data.uid===chatUI.contactUid) chatUI._updateStatus(data);
    });

    socketEngine.on('typing', data => {
      if(!chatUI.contactUid||data.from!==chatUI.contactUid) return;
      const bar=document.getElementById('typing-bar');
      const name=document.getElementById('typing-name');
      if(!bar) return;
      if(data.isTyping){
        if(name) name.textContent=chatUI.contactData?.name||data.from;
        bar.classList.remove('hidden');
        clearTimeout(bar._t); bar._t=setTimeout(()=>bar.classList.add('hidden'),3500);
      } else { bar.classList.add('hidden'); }
    });

    socketEngine.on('message-read', data => {
      const idx=chatUI.msgs?.findIndex(m=>m.id===data.messageId);
      if(idx!==-1&&chatUI.msgs) { chatUI.msgs[idx].status='read'; chatUI.updateMsgStatus(data.messageId,data.messageId,'read'); }
    });

    socketEngine.on('conversation-read', data => {
      const myUid=store.user().uid;
      chatUI.msgs?.forEach(m=>{if(m.from===myUid&&m.status!=='read'){m.status='read';}});
      chatUI.updateMsgStatus&&chatUI._renderAll&&chatUI._renderAll();
    });

    socketEngine.on('reaction-update', data => {
      if(chatUI.msgs) {
        const idx=chatUI.msgs.findIndex(m=>m.id===data.messageId);
        if(idx!==-1) { chatUI.msgs[idx].reactions=data.reactions; chatUI._renderAll&&chatUI._renderAll(); }
      }
    });

    socketEngine.on('message-deleted', data => {
      if(chatUI.msgs) {
        const idx=chatUI.msgs.findIndex(m=>m.id===data.messageId);
        if(idx!==-1) { if(data.forEveryone){chatUI.msgs[idx].deleted=true;chatUI.msgs[idx].text='';}else{chatUI.msgs.splice(idx,1);} chatUI._renderAll&&chatUI._renderAll(); }
      }
    });
  },

  openChat(uid) { chatList.clearUnread(uid); chatUI.open(uid); },

  _tokenExpired(token) {
    try { const p=JSON.parse(atob(token.split('.')[1])); return p.exp*1000<Date.now()+30000; }
    catch { return true; }
  },
  _hideSplash() {
    const sp=document.getElementById('splash'); if(!sp) return;
    sp.style.opacity='0'; setTimeout(()=>sp.style.display='none',500);
  },
  _showAuth() {
    document.querySelectorAll('.screen').forEach(s=>{s.classList.add('hidden');s.style.cssText='';});
    const auth=document.getElementById('screen-auth'); if(auth) auth.classList.remove('hidden');
  },
  _showChatList() {
    document.querySelectorAll('.screen').forEach(s=>{s.classList.add('hidden');s.style.cssText='';});
    const cl=document.getElementById('screen-chatlist'); if(cl) cl.classList.remove('hidden');
  },
};
window.app=app;

// ── Start ────────────────────────────────────────────────────
window.addEventListener('online',  ()=>{ const b=document.getElementById('net-banner'); if(b){b.style.background='#007700';b.textContent='✅ Back online';b.classList.remove('hidden');setTimeout(()=>b.classList.add('hidden'),2500);} socketEngine.reconnect&&socketEngine.reconnect(); });
window.addEventListener('offline', ()=>{ const b=document.getElementById('net-banner'); if(b){b.style.background='#cc0000';b.textContent='📡 No internet connection';b.classList.remove('hidden');} });
document.addEventListener('click',  e=>{ if(!e.target.closest('.dropdown')&&!e.target.closest('[onclick*="toggleMenu"]')) closeAll(); });
document.addEventListener('DOMContentLoaded', ()=>app.init());
""")

w("public/manifest.json", """\
{
  "name": "New Gen Box",
  "short_name": "NGB",
  "description": "Secure Real-Time Chat App",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#000000",
  "theme_color": "#000000",
  "orientation": "portrait",
  "icons": [
    {
      "src": "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='20' fill='%23000'/><text x='50' y='65' font-size='50' text-anchor='middle'>💬</text></svg>",
      "sizes": "192x192",
      "type": "image/svg+xml",
      "purpose": "any maskable"
    }
  ]
}
""")

w("public/service-worker.js", """\
'use strict';
const CACHE = 'ngb-v2';
const STATIC = ['/','/css/style.css','/js/utils.js','/js/storage.js','/js/auth.js','/js/socket.js','/js/chatList.js','/js/chat.js','/js/contacts.js','/js/profile.js','/js/mediaViewer.js','/js/main.js'];
self.addEventListener('install',  e => e.waitUntil(caches.open(CACHE).then(c=>c.addAll(STATIC)).then(()=>self.skipWaiting())));
self.addEventListener('activate', e => e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch', e => {
  const url=new URL(e.request.url);
  if(url.pathname.startsWith('/api/')||url.pathname.startsWith('/uploads/')||url.pathname.startsWith('/socket.io')) return;
  e.respondWith(caches.match(e.request).then(cached=>cached||fetch(e.request).then(r=>{if(!r||r.status!==200||r.type!=='basic') return r; const clone=r.clone(); caches.open(CACHE).then(c=>c.put(e.request,clone)); return r;}).catch(()=>{if(e.request.mode==='navigate') return caches.match('/');}) ));
});
""")



# ═══════════════════════════════════════════════════════════════
# MAIN SETUP FUNCTION
# ═══════════════════════════════════════════════════════════════

def build():
    print("""
╔══════════════════════════════════════════════════════╗
║      NEW GEN BOX v2.0 — SETUP STARTING              ║
╚══════════════════════════════════════════════════════╝
""")
    print(f"  Creating project: {PROJECT}/\n")

    # Create dirs
    for d in ['','config','models','utils','middleware','controllers','routes','socket',
              'public/css','public/js','public/uploads','database','logs']:
        os.makedirs(os.path.join(PROJECT, d), exist_ok=True)

    # Write FILES dict entries
    for path, content in FILES.items():
        w(path, content)

    # Create empty db
    db_path = os.path.join(PROJECT, 'database', 'db.json')
    if not os.path.exists(db_path):
        with open(db_path, 'w') as f:
            json.dump({}, f)
        print("  ✓  database/db.json")

    # .gitignore
    with open(os.path.join(PROJECT, '.gitignore'), 'w') as f:
        f.write("node_modules/\n.env\ndatabase/db.json\nlogs/\npublic/uploads/\n*.log\n.DS_Store\n")

    # README
    with open(os.path.join(PROJECT, 'README.md'), 'w') as f:
        f.write("""# New Gen Box v2.0

## Quick Start
1. Edit `.env` with Gmail credentials
2. `npm install`
3. `node server.js`
4. Open http://localhost:3000

## OTP Note
If email not configured, OTP shows in SERVER TERMINAL!

## Gmail App Password
Google Account → Security → 2-Step Verification → App Passwords
""")

    print("\n  Running npm install...\n")
    try:
        subprocess.run(['npm', 'install'], cwd=PROJECT, timeout=300)
        print("\n  ✅ npm install complete!")
    except FileNotFoundError:
        print("\n  ⚠️  npm not found. Run: cd " + PROJECT + " && npm install")
    except Exception as e:
        print(f"\n  ⚠️  {e}")

    print(f"""
╔══════════════════════════════════════════════════════╗
║              ✅ SETUP COMPLETE!                      ║
╠══════════════════════════════════════════════════════╣
║  1. Edit {PROJECT}/.env                       ║
║     EMAIL_USER=your@gmail.com                        ║
║     EMAIL_PASS=your_gmail_app_password               ║
║     JWT_SECRET=any_long_random_string                ║
║                                                      ║
║  2. cd {PROJECT} && node server.js             ║
║                                                      ║
║  3. Open http://localhost:3000                       ║
║                                                      ║
║  ⚠️  OTP shows in terminal if email not set up     ║
╚══════════════════════════════════════════════════════╝
""")

if __name__ == '__main__':
    build()
