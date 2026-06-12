import os
import requests
from flask import Flask, request, Response

app = Flask(__name__)

# ==========================================
# ⚙️ GENEL AYARLAR (Buradan kolayca düzenleyebilirsiniz)
# ==========================================

# 1. İzin Verilen Marzban Panel Adresleri (Çoklu Liste)
ALLOWED_PANELS = [
    "207.180.239.205:8627",
    "sub.togreben.xyz",
    "sub.yadow.xyz",
    "lite.yadow.xyz",
    "panel.fkjwox.xyz:8000"
]

# 2. Happ / Hiddify Uygulama Ayarları
HAPP_SETTINGS = {
    "profile-title": "Name VPN",                        
    "profile-web-page-url": "https://google.com",       
    "profile-update-interval": "24",                    
    "support-url": ""                                   
}

# 3. Müşterilere Gösterilecek Duyuru Mesajı
ANNOUNCE_MESSAGE = "#announce: base64:SGFwcCB0aGUgYmVzdCE="

# ==========================================
# 🚀 KODUN İŞLEYİŞ KISMI (Buradan sonrasına dokunmanıza gerek yok)
# ==========================================

@app.route('/sub', methods=['GET'])
def dynamic_proxy():
    target_url = request.args.get('url')
    
    if not target_url:
        return "Hata: Lütfen bir URL belirtin (Örn: ?url=http...)", 400

    # Güvenlik Kontrolü: Gelen URL, listedeki domainlerden birini içeriyor mu?
    is_allowed = any(panel in target_url for panel in ALLOWED_PANELS)
    if not is_allowed:
        return "Erişim Reddedildi: Sadece yetkili sunuculara izin var.", 403

    try:
        # Gelen orijinal User-Agent'ı (Hiddify/v2rayNG) alıp doğrudan Marzban'a iletiyoruz
        client_headers = {"User-Agent": request.headers.get("User-Agent", "HiddifyNext/1.0")}
        resp = requests.get(target_url, headers=client_headers, timeout=15)
        
        forwarded_headers = {}
        for key, value in resp.headers.items():
            if key.lower() not in ['content-encoding', 'content-length', 'transfer-encoding', 'connection']:
                forwarded_headers[key] = value
                
        for key, value in HAPP_SETTINGS.items():
            if value:  
                forwarded_headers[key] = value

        content = resp.text
        
        if ANNOUNCE_MESSAGE:
            content = ANNOUNCE_MESSAGE + "\n" + content

        return Response(
            content, 
            status=resp.status_code, 
            headers=forwarded_headers,
            content_type=resp.headers.get('Content-Type')
        )
    except Exception as e:
        return f"Proxy Hatası: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
