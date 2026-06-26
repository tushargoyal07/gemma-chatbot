# Deployment Checklist

Use this checklist when deploying for internal testing.

## Local Ollama

- [ ] Ollama installed and running
- [ ] `ollama pull gemma4:e2b` completed
- [ ] `OLLAMA_HOST=0.0.0.0:11434` set and Ollama restarted
- [ ] Router port forward: TCP 11434 → local machine
- [ ] Firewall allows inbound TCP 11434
- [ ] Sleep/hibernate disabled on host machine
- [ ] `curl http://localhost:11434/api/tags` works
- [ ] `curl http://<PUBLIC_IP>:11434/api/tags` works from external network

## Railway (Backend)

- [ ] GitHub repo connected
- [ ] Root directory set to `backend`
- [ ] `ENVIRONMENT=production`
- [ ] `OLLAMA_BASE_URL=http://<PUBLIC_IP>:11434`
- [ ] `GEMMA_MODEL=gemma4:e2b`
- [ ] `CORS_ORIGINS` set (update after Vercel deploy)
- [ ] `STARTUP_VALIDATE_OLLAMA=true`
- [ ] Deploy succeeded (green status)
- [ ] `GET /health` returns `{"status":"healthy"}`
- [ ] `GET /health/model` returns healthy + `model_loaded: true`

## Vercel (Frontend)

- [ ] GitHub repo connected
- [ ] Root directory set to `frontend`
- [ ] `VITE_API_URL` set to Railway public URL
- [ ] Build succeeded
- [ ] Site loads at Vercel URL

## Cross-service wiring

- [ ] Railway `CORS_ORIGINS` includes Vercel URL
- [ ] Backend redeployed after CORS update (if needed)
- [ ] `python scripts/verify_deployment.py` passes
- [ ] Manual chat test in browser works
- [ ] Streaming responses work (`/chat/stream`)

## Ongoing operations

- [ ] Know how to check Railway logs for errors
- [ ] Know how to update `OLLAMA_BASE_URL` if public IP changes
- [ ] Plan to shut down port forwarding when testing ends

## Quick verification commands

```bash
# Backend health
curl https://<railway-url>/health

# Ollama via backend
curl https://<railway-url>/health/model

# Full deployment script
BACKEND_URL=https://<railway-url> FRONTEND_URL=https://<vercel-url> python scripts/verify_deployment.py
```
