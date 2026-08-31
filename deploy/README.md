# Home-directory deployment

The Debian deployment keeps application code and runtimes under the user home:

- Application: `~/apps/SXUWhatEat`
- Node.js: `~/.local/node`
- Python/uv: `~/.local/bin` and the project `.venv`
- Database: `~/apps/SXUWhatEat/data/sxuwhateat.db`
- Logs: `~/apps/SXUWhatEat/logs`
- Services: `~/.config/systemd/user/sxuwhateat-*.service`

Useful commands:

```bash
systemctl --user status sxuwhateat-backend sxuwhateat-frontend
systemctl --user restart sxuwhateat-backend sxuwhateat-frontend
tail -f ~/apps/SXUWhatEat/logs/backend.log ~/apps/SXUWhatEat/logs/frontend.log
```

The backend binds to `127.0.0.1:8000`; only the Next.js frontend is exposed on
port `8080`. The frontend proxies `/api` and `/uploads` to the backend. On the
VPN, open `http://10.100.0.2:8080`.
