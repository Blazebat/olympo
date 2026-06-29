import requests
from flask import Flask, Response

app = Flask(__name__)

@app.route('/')
@app.route('/master.m3u8')
def generate_m3u8():
    # The Olympics token generator endpoint
    token_url = "https://www.olympics.com/tokenGenerator?url=https://ott-dai-oc.akamaized.net/OC1/master.m3u8&domain=https://ott-dai-oc.akamaized.net"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://olympics.com/"
    }
    
    try:
        # Fetch the token payload
        response = requests.get(token_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # The API typically returns a JSON containing the full authenticated URL or just the token parameters.
        # Assuming it returns a JSON with a key like 'url' or raw string, we adapt:
        data = response.json()
        final_url = data.get("url") or data.get("rawUrl")
        
        if not final_url:
            # Fallback if the structure is different (e.g., if it returns just the token query string)
            token_string = data.get("token") or response.text
            if "hdnts=" in token_string:
                final_url = f"https://ott-dai-oc.akamaized.net/OC1/master.m3u8?{token_string.lstrip('?')}"
            else:
                return "Failed to parse token from provider", 502

        # Create the master.m3u8 content redirecting or proxying the stream playlist
        m3u8_content = f"#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-STREAM-INF:BANDWIDTH=5000000\n{final_url}\n"
        
        return Response(
            m3u8_content,
            m3type="application/x-mpegURL",
            headers={"Content-Disposition": "inline; filename=master.m3u8"}
        )

    except Exception as e:
        return f"Error generating master.m3u8: {str(e)}", 500

# For local testing
if __name__ == '__main__':
    app.run(debug=True)
