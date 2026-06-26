import os
import re

file_path = r"c:\Users\mrcte\Desktop\Planner\index.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. CSS for Login Overlay
login_css = """
    /* FIREBASE LOGIN OVERLAY */
    #loginOverlay {
      position: fixed;
      top: 0; left: 0; width: 100%; height: 100%;
      background: var(--bg-primary);
      z-index: 9999;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: opacity 0.3s;
    }
    .login-box {
      background: var(--bg-card);
      border: 1px solid var(--border-primary);
      border-radius: var(--radius-lg);
      padding: 40px;
      width: 100%;
      max-width: 400px;
      text-align: center;
      box-shadow: var(--shadow-lg);
    }
    .login-box h2 {
      margin-bottom: 24px;
      color: var(--text-primary);
    }
    .login-box input {
      width: 100%;
      padding: 12px;
      margin-bottom: 16px;
      background: var(--bg-secondary);
      border: 1px solid var(--border-secondary);
      border-radius: var(--radius-sm);
      color: var(--text-primary);
    }
    .login-box button {
      width: 100%;
      padding: 12px;
      background: var(--accent-purple);
      color: white;
      border: none;
      border-radius: var(--radius-sm);
      font-weight: bold;
      cursor: pointer;
      margin-bottom: 12px;
    }
    .login-box button:hover {
      background: #6d28d9;
    }
    .auth-error {
      color: var(--accent-rose);
      font-size: 13px;
      margin-bottom: 16px;
      display: none;
    }
"""
if "FIREBASE LOGIN OVERLAY" not in content:
    content = content.replace("</style>", login_css + "\n  </style>")


# 2. HTML for Login Overlay
login_html = """
  <div id="loginOverlay">
    <div class="login-box">
      <h2>Planner Residência</h2>
      <p style="color: var(--text-secondary); margin-bottom: 24px; font-size: 14px;">Faça login para acessar e sincronizar seus estudos.</p>
      <div id="authError" class="auth-error"></div>
      <input type="email" id="emailInput" placeholder="E-mail" />
      <input type="password" id="passwordInput" placeholder="Senha" />
      <button onclick="handleLogin()">Entrar</button>
      <button onclick="handleSignup()" style="background: transparent; border: 1px solid var(--border-secondary); color: var(--text-secondary);">Criar Conta</button>
    </div>
  </div>
"""
if 'id="loginOverlay"' not in content:
    content = re.sub(r'(<body[^>]*>)', r'\1' + "\n" + login_html, content)


# 3. Add Firebase CDNs before the main script logic
firebase_scripts = """
  <!-- Firebase Compat Libraries -->
  <script src="https://www.gstatic.com/firebasejs/10.8.1/firebase-app-compat.js"></script>
  <script src="https://www.gstatic.com/firebasejs/10.8.1/firebase-auth-compat.js"></script>
  <script src="https://www.gstatic.com/firebasejs/10.8.1/firebase-firestore-compat.js"></script>
"""
if "firebase-app-compat" not in content:
    # Just insert it before <script>
    content = content.replace("<script>", firebase_scripts + "\n  <script>", 1)


# 4. Replace localStorage persistence with Firebase logic
old_persistence = """    // ═══════════════════════════════════════════
    // PERSISTENCE — localStorage
    // ═══════════════════════════════════════════
    const STORAGE_KEY = 'planner_residencia_lucas_2026';

    function loadData() {
      try {
        const raw = localStorage.getItem(STORAGE_KEY);
        return raw ? JSON.parse(raw) : {};
      } catch (e) { return {}; }
    }

    function saveData(data) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    }

    function getItemData(idx) {
      const data = loadData();
      return data[idx] || { status: 'pending', notes: '', doubts: '' };
    }

    function setItemData(idx, updates) {
      const data = loadData();
      data[idx] = { ...(data[idx] || { status: 'pending', notes: '', doubts: '' }), ...updates };
      saveData(data);
    }"""

new_persistence = """    // ═══════════════════════════════════════════
    // PERSISTENCE — FIREBASE
    // ═══════════════════════════════════════════
    const STORAGE_KEY = 'planner_residencia_lucas_2026';
    let globalData = {}; // in-memory cache updated by firestore listener
    let currentUserUid = null;

    function loadData() {
      // Local check if offline/unloaded, but usually globalData has the state
      return globalData;
    }

    function saveData(data) {
      globalData = data;
      // Also save to localStorage as a fallback
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
      
      // Async save to firestore
      if (currentUserUid && window.db) {
        db.collection('users').doc(currentUserUid).set({
          plannerData: JSON.stringify(data),
          lastUpdated: firebase.firestore.FieldValue.serverTimestamp()
        }, { merge: true }).catch(err => console.error("Error saving to Firebase", err));
      }
    }

    function getItemData(idx) {
      return globalData[idx] || { status: 'pending', notes: '', doubts: '' };
    }

    function setItemData(idx, updates) {
      globalData[idx] = { ...(globalData[idx] || { status: 'pending', notes: '', doubts: '' }), ...updates };
      saveData(globalData);
    }"""

if "PERSISTENCE — localStorage" in content:
    content = content.replace(old_persistence, new_persistence)

# 5. Append Firebase Init and Auth at the end of the script block
firebase_init = """
    // ═══════════════════════════════════════════
    // FIREBASE INIT & AUTH
    // ═══════════════════════════════════════════
    const firebaseConfig = {
      apiKey: "AIzaSyB2RY-fLj_gpHzCGUgSEWLtdc2fOcxr2XM",
      authDomain: "planner-b3325.firebaseapp.com",
      projectId: "planner-b3325",
      storageBucket: "planner-b3325.firebasestorage.app",
      messagingSenderId: "436258954359",
      appId: "1:436258954359:web:7986b9d102c3e0f157ba72",
      measurementId: "G-G1N4X64DN3"
    };

    if (!firebase.apps.length) {
      firebase.initializeApp(firebaseConfig);
    }
    window.db = firebase.firestore();
    window.auth = firebase.auth();

    // Fallback load from local storage immediately so it's not empty
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) globalData = JSON.parse(raw);
    } catch(e) {}

    auth.onAuthStateChanged((user) => {
      const overlay = document.getElementById('loginOverlay');
      if (user) {
        currentUserUid = user.uid;
        overlay.style.display = 'none';
        
        // Setup Realtime Listener
        db.collection('users').doc(user.uid).onSnapshot((doc) => {
          if (doc.exists) {
            const serverData = doc.data().plannerData;
            if (serverData) {
              globalData = JSON.parse(serverData);
              localStorage.setItem(STORAGE_KEY, serverData); // Update local cache
              renderAll(); // Re-render the UI with new data!
            }
          }
        });
      } else {
        currentUserUid = null;
        overlay.style.display = 'flex';
      }
    });

    function handleLogin() {
      const e = document.getElementById('emailInput').value;
      const p = document.getElementById('passwordInput').value;
      const errBox = document.getElementById('authError');
      if(!e || !p) return;
      
      auth.signInWithEmailAndPassword(e, p).catch(err => {
        errBox.style.display = 'block';
        errBox.innerText = "Erro ao entrar: " + err.message;
      });
    }

    function handleSignup() {
      const e = document.getElementById('emailInput').value;
      const p = document.getElementById('passwordInput').value;
      const errBox = document.getElementById('authError');
      if(!e || !p) return;
      
      auth.createUserWithEmailAndPassword(e, p).then((cred) => {
        // Upload any existing local data upon signup!
        if(Object.keys(globalData).length > 0) {
          db.collection('users').doc(cred.user.uid).set({
            plannerData: JSON.stringify(globalData),
            lastUpdated: firebase.firestore.FieldValue.serverTimestamp()
          });
        }
      }).catch(err => {
        errBox.style.display = 'block';
        errBox.innerText = "Erro ao criar conta: " + err.message;
      });
    }
    
    function handleLogout() {
      auth.signOut();
    }
    
    // Add logout button to header if not exists
    const headerRight = document.querySelector('.header-right');
    if(headerRight && !document.getElementById('logoutBtn')) {
        const btn = document.createElement('button');
        btn.id = 'logoutBtn';
        btn.className = 'header-btn';
        btn.innerHTML = 'Sair do Sistema';
        btn.onclick = handleLogout;
        headerRight.appendChild(btn);
    }
"""

if "FIREBASE INIT & AUTH" not in content:
    # Append before the last </script>
    content = content.replace("</script>\n</body>", firebase_init + "\n  </script>\n</body>")
    content = content.replace("</script></body>", firebase_init + "\n  </script></body>") # backup


with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Firebase integration completed in index.html!")
