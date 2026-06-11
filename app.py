from flask import Flask, request, Response
import requests

app = Flask(__name__)

# 🔐 BURAYA SONRADAN EKLEME YAPACAKSIN
ALLOWED_TARGETS = [
    "207.180.239.205:8627",
    "sub1.domain.com:8000",
    "sub2.domain.com:8000",
    "sub3.domain.com:8000",
    "sub4.domain.com:8000",
]

@app.route("/sub")
def sub():

    url = request.args.get("url")
    if not url:
        return "missing url", 400

    # 🔐 whitelist kontrol
    if not any(x in url for x in ALLOWED_TARGETS):
        return "blocked", 403

    try:
        r = requests.get(url, timeout=10)

        excluded = ["content-encoding", "content-length", "transfer-encoding", "connection"]

        headers = {k: v for k, v in r.headers.items() if k.lower() not in excluded}

        return Response(r.content, status=r.status_code, headers=headers)

    except Exception as e:
        return str(e), 500


@app.route("/")
def home():
    return "OK"
