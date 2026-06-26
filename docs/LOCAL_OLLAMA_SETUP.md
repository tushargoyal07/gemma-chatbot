# Local Ollama Setup

Configure Ollama on your machine so Railway can reach it at `http://<PUBLIC_IP>:11434`.

> **Security warning:** This exposes the Ollama API without authentication. Use only for temporary internal testing.

## 1. Install Ollama

Download and install from [ollama.com](https://ollama.com/download).

**Windows:** Run the installer and launch the Ollama app from the system tray.

**macOS / Linux:**

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

## 2. Pull Gemma 4

```bash
ollama pull gemma4:e2b
```

Verify:

```bash
ollama list
```

You should see `gemma4:e2b` in the list.

## 3. Bind Ollama to all network interfaces

By default Ollama listens on `127.0.0.1` only. External connections need `0.0.0.0`.

### Windows

1. Open **Settings → System → About → Advanced system settings → Environment Variables**.
2. Under **User** or **System** variables, add:
   - Name: `OLLAMA_HOST`
   - Value: `0.0.0.0:11434`
3. Restart the Ollama application (quit from system tray, reopen).
4. Confirm Ollama is listening:

```powershell
netstat -an | findstr 11434
```

Look for `0.0.0.0:11434` in the LISTENING state.

### macOS / Linux

```bash
export OLLAMA_HOST=0.0.0.0:11434
ollama serve
```

To persist, add `OLLAMA_HOST=0.0.0.0:11434` to `~/.bashrc` or `~/.zshrc`.

## 4. Configure router port forwarding

Forward **TCP port 11434** from your router to your local machine's LAN IP.

Example (varies by router):

| Setting | Value |
|---------|-------|
| External port | `11434` |
| Internal IP | Your PC's LAN IP (e.g. `192.168.1.100`) |
| Internal port | `11434` |
| Protocol | TCP |

Find your LAN IP:

**Windows:**

```powershell
ipconfig
```

**macOS / Linux:**

```bash
ip addr
```

## 5. Configure firewall

### Windows Firewall

1. Open **Windows Defender Firewall → Advanced settings**.
2. **Inbound Rules → New Rule**.
3. Port → TCP → `11434` → Allow → apply to Private (and Domain if needed).
4. Name it `Ollama API`.

### macOS

```bash
# If using the built-in firewall, allow incoming on 11434 via System Settings
```

### Linux (ufw)

```bash
sudo ufw allow 11434/tcp
```

## 6. Find your public IP

Visit [https://ifconfig.me](https://ifconfig.me) or run:

```bash
curl ifconfig.me
```

Use this IP in Railway's `OLLAMA_BASE_URL`:

```
OLLAMA_BASE_URL=http://<PUBLIC_IP>:11434
```

> **Note:** Most home ISPs assign dynamic public IPs. If connectivity breaks after a router reboot, check your IP and update Railway.

## 7. Verify external access

From a **different network** (phone on cellular, friend's Wi-Fi, or an online curl tool):

```bash
curl http://<PUBLIC_IP>:11434/api/tags
```

Expected: JSON listing available models including `gemma4:e2b`.

If this fails, check port forwarding, firewall, and that Ollama is bound to `0.0.0.0`.

## 8. Disable sleep mode

The machine running Ollama must stay awake while testing.

**Windows:**

1. **Settings → System → Power & battery**.
2. Set **Screen and sleep** to **Never** (while plugged in).

**macOS:**

```bash
caffeinate -d
```

Or disable sleep in **System Settings → Energy**.

## 9. Optional: restrict access

For slightly better security during testing:

- Allow inbound port 11434 only from Railway's egress IPs (if known), or
- Use a VPN/tunnel (e.g. ngrok, Cloudflare Tunnel) instead of raw port forwarding — then set `OLLAMA_BASE_URL` to the tunnel URL.

## Quick local test (before deploying)

```bash
curl http://localhost:11434/api/tags
curl http://<PUBLIC_IP>:11434/api/tags
```

Both should return model tags when setup is correct.
