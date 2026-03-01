#!/usr/bin/env python3
"""Use Chrome DevTools Protocol to intercept network requests on CrossFit Games leaderboard."""

import asyncio
import json
import websockets

WS_URL = "ws://localhost:9222/devtools/page/09D5B2FD7F5BB36E64AB61FFCF213CF5"

async def main():
    async with websockets.connect(WS_URL, max_size=10*1024*1024) as ws:
        msg_id = 1

        async def send(method, params=None):
            nonlocal msg_id
            msg = {"id": msg_id, "method": method}
            if params:
                msg["params"] = params
            await ws.send(json.dumps(msg))
            mid = msg_id
            msg_id += 1
            return mid

        # Enable network monitoring
        await send("Network.enable")

        # Navigate to women's division
        nav_id = await send("Page.navigate", {
            "url": "https://games.crossfit.com/leaderboard/open/2025?view=0&division=2&region=0&scaled=0&sort=0"
        })

        # Collect network requests for 15 seconds
        api_requests = []
        try:
            deadline = asyncio.get_event_loop().time() + 15
            while asyncio.get_event_loop().time() < deadline:
                try:
                    raw = await asyncio.wait_for(ws.recv(), timeout=1.0)
                    data = json.loads(raw)
                    method = data.get("method", "")

                    if method == "Network.requestWillBeSent":
                        url = data["params"]["request"]["url"]
                        req_method = data["params"]["request"]["method"]
                        headers = data["params"]["request"].get("headers", {})
                        # Filter for API-like requests (not static assets)
                        if any(kw in url.lower() for kw in ["api", "leaderboard", "competition", "graphql", "json", "ajax"]):
                            api_requests.append({
                                "url": url,
                                "method": req_method,
                                "headers": headers,
                                "type": data["params"].get("type", ""),
                                "requestId": data["params"]["requestId"]
                            })
                            print(f"[API] {req_method} {url}")
                        elif not any(ext in url for ext in [".js", ".css", ".png", ".jpg", ".svg", ".woff", ".gif", ".ico"]):
                            print(f"[OTHER] {req_method} {url[:120]}")
                except asyncio.TimeoutError:
                    continue
        except Exception as e:
            print(f"Error: {e}")

        print(f"\n=== Found {len(api_requests)} API requests ===")
        for req in api_requests:
            print(f"\nURL: {req['url']}")
            print(f"Method: {req['method']}")
            print(f"Headers: {json.dumps(req['headers'], indent=2)}")

        # Also check performance entries via JS evaluation
        print("\n=== Checking performance entries ===")
        eval_id = await send("Runtime.evaluate", {
            "expression": "JSON.stringify(performance.getEntriesByType('resource').filter(e => e.name.includes('api') || e.name.includes('leaderboard') || e.name.includes('competition')).map(e => ({name: e.name, type: e.initiatorType})))",
            "returnByValue": True
        })

        deadline2 = asyncio.get_event_loop().time() + 5
        while asyncio.get_event_loop().time() < deadline2:
            raw = await asyncio.wait_for(ws.recv(), timeout=2.0)
            data = json.loads(raw)
            if data.get("id") == eval_id:
                result = data.get("result", {}).get("result", {}).get("value", "[]")
                entries = json.loads(result) if isinstance(result, str) else result
                print(f"Performance entries: {json.dumps(entries, indent=2)}")
                break

asyncio.run(main())
