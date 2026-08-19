import httpx

r = httpx.options("http://localhost:8000/auth/token", headers={
    "Origin": "http://localhost:3000",
    "Access-Control-Request-Method": "POST"
})
print("OPTIONS:", r.status_code, r.headers)
