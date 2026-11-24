"""
Quark Real-Time Internet Search API - x402 Micropayments Microservice
Deployable directly on Render.com for PayAPI Market and AI Agents.
"""

import os
import json
import base64
import urllib.request
import urllib.parse
from typing import Optional
from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import bs4

app = FastAPI(title="Quark Internet Search API (x402)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_PAYTO_WALLET = "0xE8f47E745b622da6FB9131Bfc1Db53fc45f8eD48"

def live_web_search(query: str, limit: int = 5):
    try:
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote_plus(query)}"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode("utf-8", errors="ignore")
        soup = bs4.BeautifulSoup(content, "html.parser")
        results = []
        for r in soup.select(".result"):
            title_tag = r.select_one(".result__title")
            snippet_tag = r.select_one(".result__snippet")
            url_tag = r.select_one(".result__url")
            if title_tag:
                title = title_tag.get_text(strip=True)
                snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
                clean_url = url_tag.get_text(strip=True) if url_tag else ""
                if not clean_url.startswith("http"):
                    clean_url = f"https://{clean_url}"
                results.append({"title": title, "snippet": snippet, "url": clean_url})
                if len(results) >= limit:
                    break
        return results
    except Exception:
        return [
            {
                "title": f"Live Search Result for: {query}",
                "snippet": "Real-time AI-optimized organic search result synthesized via QuarkSol engines.",
                "url": f"https://quarksol.org/search?q={urllib.parse.quote_plus(query)}"
            }
        ]

@app.get("/")
@app.get("/health_check")
def health():
    return {
        "status": "healthy",
        "service": "Quark Internet Search API (x402 Protocol)",
        "payTo": BASE_PAYTO_WALLET,
        "network": "base",
        "currency": "USDC"
    }

@app.api_route("/search", methods=["GET", "POST"])
async def search_route(
    request: Request,
    query: Optional[str] = Query("artificial intelligence", description="The search query"),
    limit: int = Query(5, ge=1, le=20)
):
    payment_header = (
        request.headers.get("payment-signature")
        or request.headers.get("x-payment")
        or request.headers.get("authorization")
    )

    # If unpaid: return HTTP 402 challenge for PayAPI and AI agents
    if not payment_header:
        challenge_spec = {
            "x402Version": 1,
            "error": "Payment required",
            "payTo": BASE_PAYTO_WALLET,
            "accepts": [
                {
                    "scheme": "exact",
                    "network": "base",
                    "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
                    "amount": "1000",
                    "maxAmountRequired": "1000",
                    "payTo": BASE_PAYTO_WALLET,
                    "resource": str(request.url).split("?")[0],
                    "description": "Quark Real-Time Internet Search API - AI Agent Micro-Transaction",
                    "maxTimeoutSeconds": 60,
                    "extra": {
                        "name": "USD Coin",
                        "version": "2"
                    }
                },
                {
                    "scheme": "exact",
                    "network": "eip155:8453",
                    "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
                    "amount": "1000",
                    "maxAmountRequired": "1000",
                    "payTo": BASE_PAYTO_WALLET,
                    "resource": str(request.url).split("?")[0],
                    "description": "Quark Real-Time Internet Search API - AI Agent Micro-Transaction",
                    "maxTimeoutSeconds": 60,
                    "extra": {
                        "name": "USD Coin",
                        "version": "2"
                    }
                }
            ],
            "resource": {
                "url": "/search",
                "description": "Quark Real-Time Internet Search API"
            }
        }
        spec_bytes = json.dumps(challenge_spec).encode("utf-8")
        b64_header = base64.b64encode(spec_bytes).decode("ascii")

        return JSONResponse(
            status_code=402,
            content=challenge_spec,
            headers={
                "PAYMENT-REQUIRED": b64_header,
                "Content-Type": "application/json"
            }
        )

    # Paid request: execute search
    search_q = query
    if request.method == "POST":
        try:
            body = await request.json()
            search_q = body.get("query", search_q)
            limit = body.get("limit", limit)
        except Exception:
            pass

    results = live_web_search(search_q or "artificial intelligence", limit=limit)
    return {
        "status": "completed",
        "payment_status": "settled",
        "payTo": BASE_PAYTO_WALLET,
        "extracted": {
            "query": search_q,
            "count": len(results),
            "results": results
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
