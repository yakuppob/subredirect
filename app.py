import os
import requests
from flask import Flask, request, Response

app = Flask(__name__)

@app.route('/sub', methods=['GET'])
def dynamic_proxy():
    target_url = request.args.get('url')
    
    if not target_url:
        return "Hata: Lütfen bir URL belirtin (Örn: /sub?url=http...)", 400

    # GÜVENLİK KONTROLÜ: Sadece senin IP ve Port'una izin veriyoruz
    if "207.180.239.205:8627" not in target_url:
         return "Erişim Reddedildi: Sadece yetkili sunucuya izin var.", 403

    try:
        resp = requests.get(target_url, timeout=10)
        return Response(resp.content, status=resp.status_code, content_type=resp.headers.get('Content-Type'))
    except Exception as e:
        return f"Proxy Hatası: {str(e)}", 500

if __name__ == '__main__':
    # Cloud Run, uygulamana otomatik olarak bir PORT atar, onu dinlemeliyiz
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
