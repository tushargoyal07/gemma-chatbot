# Cloudflare Tunnel for Ollama (replaces ngrok)

Use this to expose local Ollama to Railway with a **stable URL** that does not change on restart.

## Why switch from ngrok?

| | ngrok (free) | Cloudflare Tunnel (free) |
|--|--|--|
| URL on restart | Changes every time | **Stable** with a named tunnel + your domain |
| Ollama host header | `--host-header=localhost:11434` required | Set in tunnel config |
| Browser warning page | Yes (needs skip header) | No |
| PC must stay on | Yes | Yes |

> **Requirement for a stable URL:** A domain added to your [Cloudflare](https://dash.cloudflare.com) account (free plan is fine). Without a domain, use a quick tunnel — but the URL still changes each run (similar to ngrok).

---

## Option A: Stable subdomain (recommended)

Example result: `https://ollama.yourdomain.com` → always the same.

### 1. Install cloudflared (Windows)

```powershell
winget install Cloudflare.cloudflared
```

Or download from [developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads).

Close and reopen PowerShell, then verify:

```powershell
cloudflared --version
```

### 2. Log in to Cloudflare

```powershell
cloudflared tunnel login
```

This opens a browser — pick the domain you want to use.

### 3. Create a named `scripts/cloudflared-config.yml`

Copy from `scripts/cloudflared-config.example.yml` and set:

- `tunnel`: your tunnel name (e.g. `ollama`)
- `credentials-file`: path to the JSON file created in step 4
- `hostname`: subdomain you want (e.g. `ollama.yourdomain.com`)

### 4. Create the tunnel

```powershell
cd "c:\Users\tusha\OneDrive\Desktop\gemma-chatbot"

cloudflared tunnel create ollama
```

Note the credentials file path (usually `%USERPROFILE%\.cloudflared\<UUID>.json`).

### 5. Route DNS to the tunnel

```powershell
cloudflared tunnel route dns ollama ollama.yourdomain.com
```

Replace `ollama.yourdomain.com` with your chosen hostname.

### 6. Start the tunnel

```powershell
cloudflared tunnel --config scripts/cloudflared-config.yml run ollama
```

Keep this terminal open while testing.

### 7. Verify locally

```powershell
curl.exe https://ollama.yourdomain.com/api/tags
```

Expected: JSON listing `gemma4:e2b`.

### 8. Update Railway

| Variable | Value |
|----------|-------|
| `OLLAMA_BASE_URL` | `https://ollama.yourdomain.com` |

No trailing slash. Railway redeploys automatically.

Test:

```powershell
curl.exe https://gemma-chatbot-production.up.railway.app/health/model
```

---

## Option B: Quick tunnel (no domain)

Random URL each run — use only as a temporary ngrok replacement.

```powershell
cloudflared tunnel --url http://localhost:11434
```

Copy the `https://....trycloudflare.com` URL into Railway `OLLAMA_BASE_URL`.

If Ollama returns 403, Ollama may need `OLLAMA_ORIGINS=*` (Windows env vars, restart Ollama) or use Option A with `httpHostHeader: localhost:11434` in config.

---

## Run tunnel on Windows startup (optional)

```powershell
cloudflared service install --config "c:\Users\tusha\OneDrive\Desktop\gemma-chatbot\scripts\cloudflared-config.yml"
```

To remove later: `cloudflared service uninstall`

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| 403 from Ollama via tunnel | Ensure `httpHostHeader: localhost:11434` in config (see example) |
| Railway `/health/model` unreachable | Tunnel terminal closed, or wrong `OLLAMA_BASE_URL` |
| DNS not resolving | Wait a few minutes after `tunnel route dns`; check Cloudflare dashboard |
| Chat slow first message | Normal — model cold start can take 60–90s through tunnel |

---

## ngrok → Cloudflare checklist

- [ ] Ollama running locally (`curl http://localhost:11434/api/tags`)
- [ ] cloudflared installed and logged in
- [ ] Named tunnel created + DNS route configured
- [ ] Tunnel running with `httpHostHeader: localhost:11434`
- [ ] Railway `OLLAMA_BASE_URL` updated (no trailing slash)
- [ ] `/health/model` returns `model_loaded: true`
- [ ] Stop ngrok (only one tunnel needed)
