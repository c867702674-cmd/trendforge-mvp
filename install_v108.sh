#!/bin/bash

echo "Installing TrendForge V108..."

mkdir -p server/sql
mkdir -p server/api
mkdir -p server/docs
mkdir -p web

########################
# SQL
########################
cat > server/sql/migrate_v108.sql << 'EOF'
CREATE TABLE IF NOT EXISTS users_v108 (
id INTEGER PRIMARY KEY AUTOINCREMENT,
email TEXT UNIQUE,
password TEXT,
plan TEXT,
created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
EOF

########################
# API LOGIN
########################
cat > server/api/login_v108_api.py << 'EOF'
import sqlite3, json, hashlib, sys

DB='/root/trendforge-mvp/server/trendforge.db'

def hash_pw(p):
    return hashlib.sha256(p.encode()).hexdigest()

def login(email, pw):
    conn=sqlite3.connect(DB)
    cur=conn.cursor()

    pw_hash=hash_pw(pw)

    r=cur.execute(
        "SELECT id,email,plan FROM users_v108 WHERE email=? AND password=?",
        (email,pw_hash)
    ).fetchone()

    conn.close()

    if r:
        print(json.dumps({"status":"ok","user":r[1],"plan":r[2]}))
    else:
        print(json.dumps({"status":"fail"}))

if __name__=="__main__":
    login(sys.argv[1],sys.argv[2])
EOF

########################
# WEB LOGIN
########################
cat > web/login-v108.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>TrendForge Login</title>
</head>

<body style="background:#081224;color:white;font-family:Arial;padding:40px;">

<h1>TrendForge Login</h1>

<input id="email" placeholder="email" style="padding:10px;margin:6px;width:260px;"><br>
<input id="pw" placeholder="password" type="password" style="padding:10px;margin:6px;width:260px;"><br>

<button onclick="login()" style="padding:10px 18px;margin-top:10px;">Login</button>

<script>

function login(){

let e=document.getElementById("email").value
let p=document.getElementById("pw").value

fetch("/api/login_v108?email="+e+"&pw="+p)
.then(r=>r.json())
.then(d=>{

if(d.status=="ok"){
alert("Login success")
window.location="/dashboard-v108.html"
}else{
alert("Login fail")
}

})

}

</script>

</body>
</html>
EOF

########################
# WEB REGISTER
########################
cat > web/register-v108.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>TrendForge Register</title>
</head>

<body style="background:#081224;color:white;font-family:Arial;padding:40px;">

<h1>TrendForge Register</h1>

<input id="email" placeholder="email" style="padding:10px;margin:6px;width:260px;"><br>
<input id="pw" placeholder="password" type="password" style="padding:10px;margin:6px;width:260px;"><br>

<button onclick="reg()" style="padding:10px 18px;margin-top:10px;">Register</button>

<script>

function reg(){

alert("Demo register page — backend API next version")

}

</script>

</body>
</html>
EOF

########################
# WEB DASHBOARD
########################
cat > web/dashboard-v108.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>TrendForge Dashboard</title>
</head>

<body style="background:#081224;color:white;font-family:Arial;padding:40px;">

<h1>User Dashboard</h1>

<p>Welcome to TrendForge SaaS.</p>

<ul>
<li><a href="/home-portal-v106.html">Command Center</a></li>
<li><a href="/commercial-dashboard-v105.html">System Overview</a></li>
<li><a href="/index-v107.html">Homepage</a></li>
</ul>

</body>
</html>
EOF

echo "TrendForge V108 files installed successfully."
