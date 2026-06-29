export default async function handler(request, response) {
  const tokenUrl = "https://www.olympics.com/tokenGenerator?url=https://ott-dai-oc.akamaized.net/OC1/master.m3u8&domain=https://ott-dai-oc.akamaized.net";

  const fetchOptions = {
    headers: {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      "Referer": "https://olympics.com/"
    }
  };

  try {
    const apiResponse = await fetch(tokenUrl, fetchOptions);
    if (!apiResponse.ok) {
      return response.status(502).send(`Provider error: ${apiResponse.statusText}`);
    }

    let finalUrl = "";
    const contentType = apiResponse.headers.get("content-type") || "";

    // Parse response dynamically based on type
    if (contentType.includes("application/json")) {
      const data = await apiResponse.json();
      finalUrl = data.url || data.rawUrl;
      
      if (!finalUrl) {
        const tokenString = data.token || "";
        if (tokenString.includes("hdnts=")) {
          finalUrl = `https://ott-dai-oc.akamaized.net/OC1/master.m3u8?${tokenString.replace(/^\?/, '')}`;
        }
      }
    } else {
      const textData = await apiResponse.text();
      if (textData.includes("hdnts=")) {
        finalUrl = `https://ott-dai-oc.akamaized.net/OC1/master.m3u8?${textData.trim().replace(/^\?/, '')}`;
      } else {
        finalUrl = textData.trim();
      }
    }

    if (!finalUrl || !finalUrl.includes("hdnts=")) {
      return response.status(502).send("Valid authorization token missing from provider response.");
    }

    // Build the master playlist body
    const m3u8Content = `#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-STREAM-INF:BANDWIDTH=5000000\n${finalUrl}\n`;

    // Deliver response with accurate stream headers and CORS enabled
    response.setHeader('Content-Type', 'application/x-mpegURL');
    response.setHeader('Content-Disposition', 'inline; filename="master.m3u8"');
    response.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
    response.setHeader('Access-Control-Allow-Origin', '*');

    return response.status(200).send(m3u8Content);

  } catch (error) {
    return response.status(500).send(`Server Error: ${error.message}`);
  }
}
