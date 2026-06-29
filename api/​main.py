from http.server import BaseHTTPRequestHandler
import requests

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        token_url = "https://www.olympics.com/tokenGenerator?url=https://ott-dai-oc.akamaized.net/OC1/master.m3u8&domain=https://ott-dai-oc.akamaized.net"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://olympics.com/"
        }
        
        try:
            # Fetch token payload from the provider
            response = requests.get(token_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse the provider response safely
            try:
                data = response.json()
                final_url = data.get("url") or data.get("rawUrl")
                if not final_url:
                    token_string = data.get("token") or response.text
                    if "hdnts=" in token_string:
                        final_url = f"https://ott-dai-oc.akamaized.net/OC1/master.m3u8?{token_string.lstrip('?')}"
            except Exception:
                token_string = response.text
                if "hdnts=" in token_string:
                    final_url = f"https://ott-dai-oc.akamaized.net/OC1/master.m3u8?{token_string.strip().lstrip('?')}"
                else:
                    final_url = token_string.strip()

            if not final_url or "hdnts=" not in final_url:
                raise ValueError("Valid auth token string missing from provider response.")

            # Construct the dynamic M3U8 payload
            m3u8_content = f"#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-STREAM-INF:BANDWIDTH=5000000\n{final_url}\n"
            
            # Send HTTP Headers
            self.send_response(200)
            self.send_header('Content-Type', 'application/x-mpegURL')
            self.send_header('Content-Disposition', 'inline; filename="master.m3u8"')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Access-Control-Allow-Origin', '*')  # Allows IPTV players to bypass CORS
            self.end_headers()
            
            # Output payload
            self.wfile.write(m3u8_content.encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            error_message = f"Error generating playlist payload: {str(e)}"
            self.wfile.write(error_message.encode('utf-8'))
