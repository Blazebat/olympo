import requests
from flask import Flask, Response

app = Flask(__name__)

# Catch-all route to prevent any 404 routing mismatches on Vercel
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    token_url = "https://www.olympics.com/tokenGenerator?url=https://ott-dai-oc.akamaized.net/OC1/master.m3u8&domain=https://ott-dai-oc.akamaized.net"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://olympics.com/"
    }
    
    try:
        response = requests.get(token_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Try to parse as JSON first
        try:
            data = response.json()
            final_url = data.get("url") or data.get("rawUrl")
            if not final_url:
                token_string = data.get("token") or response.text
                if "hdnts=" in token_string:
                    final_url = f"https://ott-dai-oc.akamaized.net/OC1/master.m3u8?{token_string.lstrip('?')}"
        except Exception:
            # Fallback if raw text/query string is returned
            token_string = response.text
            if "hdnts=" in token_string:
                final_url = f"https://ott-dai-oc.akamaized.net/OC1/master.m3u8?{token_string.strip().lstrip('?')}"
            else:
                final_url = token_string.strip()

        if not final_url or "hdnts=" not in final_url:
            return "Failed to parse tokenized URL from source.", 502

        # Format the master.m3u8 file content
        m3u8_content = f"#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-STREAM-INF:BANDWIDTH=5000000\n{final_url}\n"
        
        return Response(
            m3u8_content,
            mimetype="application/x-mpegURL",
            headers={"Content-Disposition": "inline; filename=master.m3u8"}
        )

    except Exception as e:
        return f"Error generating master.m3u8: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
