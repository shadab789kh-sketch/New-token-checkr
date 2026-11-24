
import os
import requests
from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Facebook Token Checker</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{
 min-height:100vh;padding:100px 16px 35px;
 font-family:Segoe UI,Arial,sans-serif;color:white;
 background:radial-gradient(circle at 15% 15%,#38216b,transparent 40%),
 radial-gradient(circle at 85% 80%,#123b5a,transparent 40%),
 linear-gradient(135deg,#080b18,#17152b);
}
header{
 position:fixed;top:0;left:0;right:0;height:70px;
 display:flex;align-items:center;justify-content:space-between;
 padding:0 5%;background:#101426e8;
 border-bottom:1px solid #ffffff25;backdrop-filter:blur(14px);
}
.brand{font-weight:bold;font-size:20px}
.brand i{color:#a78bfa}
.owner{font-size:13px;color:#d8ccff}
.container{max-width:760px;margin:auto}
.card{
 background:#ffffff12;border:1px solid #ffffff30;
 border-radius:22px;padding:30px;
 box-shadow:0 22px 70px #0008;backdrop-filter:blur(18px);
}
h1{text-align:center;font-size:28px;margin-bottom:12px}
.subtitle{text-align:center;color:#b9bdd0;margin-bottom:28px}
label{display:block;font-weight:bold;margin-bottom:10px}
textarea{
 width:100%;min-height:125px;padding:15px;
 border-radius:12px;border:1px solid #ffffff40;
 background:#090d1b;color:white;
 font-family:monospace;font-size:13px;
}
textarea:focus{outline:none;border-color:#a78bfa}
button{
 width:100%;margin-top:16px;padding:15px;
 border:0;border-radius:12px;
 background:linear-gradient(110deg,#7c3aed,#4f46e5);
 color:white;font-size:16px;font-weight:bold;cursor:pointer;
}
button:hover{filter:brightness(1.2)}
.result{margin-top:20px;padding:18px;border-radius:12px;line-height:1.8}
.good{background:#16a34a25;border:1px solid #22c55e}
.bad{background:#ef444425;border:1px solid #ef4444}
.notice{
 margin-top:20px;padding:14px;border-radius:10px;
 background:#f59e0b20;border:1px solid #f59e0b70;
 color:#fbd38d;font-size:13px;line-height:1.6;
}
.footer{text-align:center;color:#999;margin-top:20px;font-size:12px}
@media(max-width:500px){
 .card{padding:22px 16px}
 h1{font-size:23px}
}
</style>
</head>
<body>

<header>
 <div class="brand"><i class="fas fa-shield-halved"></i> TOKEN CHECKER</div>
 <div class="owner">SECURE PANEL</div>
</header>

<div class="container">
 <div class="card">
  <h1><i class="fab fa-facebook"></i> Facebook Token Checker</h1>
  <p class="subtitle">Verify your own Facebook access token</p>

  <form method="POST">
   <label><i class="fas fa-key"></i> Enter Access Token</label>
   <textarea name="token" placeholder="Paste your token here..." required></textarea>
   <button type="submit">
    <i class="fas fa-check-circle"></i> CHECK TOKEN
   </button>
  </form>

  {% if result %}
  <div class="result {{ 'good' if result.ok else 'bad' }}">
   {% if result.ok %}
    <b><i class="fas fa-check-circle"></i> VALID TOKEN</b><br>
    Name: {{ result.name or 'Not provided' }}<br>
    User ID: {{ result.user_id }}
   {% else %}
    <b><i class="fas fa-times-circle"></i> INVALID / UNVERIFIED</b><br>
    {{ result.message }}
   {% endif %}
  </div>
  {% endif %}

  <div class="notice">
   <b>Security Notice:</b> Only use tokens you own or are
   authorized to test. Tokens are not stored by this application.
   Verification requests are sent to Meta Graph API.
  </div>

  <div class="footer">
   FACEBOOK TOKEN CHECKER | SECURE VERSION
  </div>
 </div>
</div>
</body>
</html>
"""

def check_token(token):
    try:
        response = requests.get(
            "https://graph.facebook.com/v23.0/me",
            params={
                "fields": "id,name",
                "access_token": token
            },
            timeout=12
        )

        data = response.json()

        if response.ok and data.get("id"):
            return {
                "ok": True,
                "name": data.get("name"),
                "user_id": data.get("id")
            }

        error = data.get("error", {})
        return {
            "ok": False,
            "message": error.get("message", "Meta rejected this token.")[:220]
        }

    except requests.RequestException:
        return {
            "ok": False,
            "message": "Connection error. Try again."
        }
    except ValueError:
        return {
            "ok": False,
            "message": "Unexpected API response."
        }


@app.route("/", methods=["GET", "POST"])
def home():
    result = None

    if request.method == "POST":
        token = request.form.get("token", "").strip()

        if not token or len(token) > 10000:
            result = {
                "ok": False,
                "message": "Invalid token input."
            }
        else:
            result = check_token(token)

    return render_template_string(HTML, result=result)


@app.route("/api")
def api():
    return jsonify({
        "status": "online",
        "service": "Facebook Token Checker",
        "endpoint": "/api/check",
        "method": "POST"
    })


@app.route("/api/check", methods=["POST"])
def api_check():
    data = request.get_json(silent=True) or {}
    token = str(data.get("token", "")).strip()

    if not token or len(token) > 10000:
        return jsonify({
            "ok": False,
            "message": "Valid token required."
        }), 400

    return jsonify(check_token(token))


@app.errorhandler(413)
def too_large(error):
    return jsonify({"error": "Request too large"}), 413


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
