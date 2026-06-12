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

        # 2. Gelen veriyi çöz
        raw_b64 = resp.text.strip()
        try:
            decoded_text = base64.b64decode(raw_b64).decode('utf-8')
        except Exception:
            decoded_text = raw_b64

        # 3. CRITICAL FIX: Sadece gerçek VPN protokol bağlantılarını ayıkla (Çakışmayı önler)
        lines = decoded_text.splitlines()
        valid_configs = []
        protocols = ("vless://", "vmess://", "trojan://", "ss://", "ssr://", "tuic://", "hy2://", "hysteria2://")
        
        for line in lines:
            line_stripped = line.strip()
            if line_stripped.startswith(protocols):
                valid_configs.append(line_stripped)

        # 4. Yeni temiz içeriği oluştur
        output_lines = HAPP_SETTINGS.copy()
        
        if userinfo:
            output_lines.append(f"#subscription-userinfo: {userinfo}")
            
        output_lines.extend(valid_configs)
        
        # Tüm satırları birleştir ve Base64 olarak şifrele
        final_content = "\n".join(output_lines)
        encoded_output = base64.b64encode(final_content.encode('utf-8')).decode('utf-8')

        # 5. Güncelleme butonunun sorunsuz çalışması için Header'ları ayarla
        response_headers = {
            "Content-Type": "text/plain; charset=utf-8"
        }
        if userinfo:
            response_headers["subscription-userinfo"] = userinfo
            response_headers["Subscription-Userinfo"] = userinfo

        return Response(
            encoded_output, 
            status=200, 
            headers=response_headers
        )
    except Exception as e:
        return f"Proxy Hatası: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
