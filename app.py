import os
import requests
import base64
from flask import Flask, request, Response

app = Flask(__name__)

# ==========================================
# ⚙️ GENEL AYARLAR
# ==========================================

ALLOWED_PANELS = [
    "207.180.239.205:8627",
    "sub.togreben.xyz",
    "sub.yadow.xyz",
    "lite.yadow.xyz",
    "panel.fkjwox.xyz:8000"
]

HAPP_SETTINGS = [
    "#profile-title: Name VPN",
    "#profile-web-page-url: https://google.com",
    "#profile-update-interval: 24",
    "#announce: base64:SGFwcCB0aGUgYmVzdCE="
]

# ==========================================
# 🚀 KODUN İŞLEYİŞ KISMI
# ==========================================

@app.route('/sub', methods=['GET'])
def dynamic_proxy():
    target_url = request.args.get('url')
    
    if not target_url:
        return "Hata: Lütfen bir URL belirtin", 400

    is_allowed = any(panel in target_url for panel in ALLOWED_PANELS)
    if not is_allowed:
        return "Erişim Reddedildi.", 403

    try:
        client_headers = {"User-Agent": request.headers.get("User-Agent", "HiddifyNext/1.0")}
        resp = requests.get(target_url, headers=client_headers, timeout=15)
        
        # 1. Marzban'dan kullanıcı kotasını (Header'dan) çek
        userinfo = resp.headers.get('subscription-userinfo') or resp.headers.get('Subscription-Userinfo')

        # 2. Gelen veriyi (Base64) düz metne çevir
        raw_b64 = resp.text.strip()
        try:
            decoded_text = base64.b64decode(raw_b64).decode('utf-8')
        except Exception:
            # Eğer zaten çözülmüş düz metinse aynen kullan
            decoded_text = raw_b64

        # 3. Yeni içeriği oluştur (Ayarlar + Kota + Vless/Vmess Kodları)
        output_lines = HAPP_SETTINGS.copy()
        
        if userinfo:
            output_lines.append(f"#subscription-userinfo: {userinfo}")
            
        output_lines.append(decoded_text)
        
        # Tüm satırları birleştir
        final_content = "\n".join(output_lines)

        # 4. Her şeyi yeniden Base64 olarak şifrele (Happ'ın beklediği format)
        encoded_output = base64.b64encode(final_content.encode('utf-8')).decode('utf-8')

        return Response(
            encoded_output, 
            status=200, 
            content_type="text/plain; charset=utf-8"
        )
    except Exception as e:
        return f"Proxy Hatası: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
