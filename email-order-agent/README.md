# Email Order Monitoring Agent

Automated system that monitors IMAP email inbox, detects purchase orders in PDF attachments using Claude AI, and sends real-time WhatsApp notifications via Twilio.

## Features

- **Automated Email Monitoring**: Checks IMAP inbox every 10 minutes
- **Smart PDF Detection**: Identifies PDF attachments from specific clients
- **AI-Powered Analysis**: Uses Claude Haiku to extract order details
- **WhatsApp Notifications**: Instant alerts via Twilio WhatsApp API
- **Duplicate Prevention**: Tracks processed emails to avoid duplicates
- **Comprehensive Logging**: Detailed logs for troubleshooting
- **Cost-Effective**: Uses Claude Haiku (~$0.005/PDF) + Twilio Sandbox (free)

## System Requirements

- Python 3.10 or higher
- Active internet connection
- IMAP email account
- Anthropic API key (Claude)
- Twilio account with WhatsApp Sandbox

## Project Structure

```
email-order-agent/
├── main.py                 # Main application entry point
├── config.py               # Configuration management
├── imap_client.py          # IMAP email monitoring
├── pdf_processor.py        # PDF text extraction
├── claude_analyzer.py      # AI analysis with Claude
├── whatsapp_notifier.py    # Twilio WhatsApp integration
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create from .env.example)
├── .env.example            # Template for environment variables
├── .gitignore              # Git ignore rules
├── README.md               # This file
└── logs/                   # Application logs
    ├── email_monitor.log   # Main log file
    └── processed_emails.txt # Tracking processed emails
```

## Installation

### 1. Clone/Download the Project

```bash
cd /Users/amauryperezverdejo/Desktop/agentes/mensajeriaPO/email-order-agent
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
nano .env  # or use any text editor
```

Edit `.env` with your credentials:

```env
# IMAP Configuration
IMAP_SERVER=mail.quimicaguba.com
IMAP_PORT=993
IMAP_USER=ventas@quimicaguba.com
IMAP_PASSWORD=your_actual_password

# Claude API
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx

# Twilio WhatsApp
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_actual_auth_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
TWILIO_WHATSAPP_TO=whatsapp:+52XXXXXXXXXX

# Monitoring
CHECK_INTERVAL_MINUTES=10

# Monitored Clients
MONITORED_CLIENTS=bpomex@vallen.com,svalois@aiig.com,rocio.santana@chemicollc.com,chihuahua@rshughes.com
```

## Configuration Guide

### IMAP Email Setup

Pre-configured for Química Guba:
- **Server**: mail.quimicaguba.com
- **Port**: 993 (IMAP SSL)
- **User**: ventas@quimicaguba.com
- **Password**: Add to `.env`

### Claude API (Anthropic)

1. Create account at https://console.anthropic.com
2. Navigate to Settings → API Keys
3. Create new API key
4. Copy to `.env` as `ANTHROPIC_API_KEY`

**Cost**: ~$0.25 per 1M input tokens (Haiku)
- Typical PDF: ~2,000 tokens
- Cost per PDF: ~$0.005
- 100 PDFs/month: ~$0.50

### Twilio WhatsApp Setup

#### Configure Your Credentials:
- **Account SID**: Get from Twilio Console (starts with AC...)
- **From Number**: whatsapp:+14155238886 (Twilio Sandbox)
- **To Number**: Your WhatsApp number (format: whatsapp:+52XXXXXXXXXX)

#### Activate Twilio WhatsApp Sandbox:

1. **Login to Twilio Console**: https://console.twilio.com
2. **Navigate to**: Messaging → Try it out → Send a WhatsApp message
3. **Join Sandbox**:
   - Send WhatsApp message to: **+1 415 523 8886**
   - Message content: `join <your-sandbox-code>`
   - Example: `join yellow-tiger`
4. **Get Auth Token**:
   - Go to Account → API Keys & Tokens
   - Copy Auth Token to `.env`

**Note**: Sandbox is FREE but requires periodic re-joining (every few days).

### Monitored Clients

Pre-configured to monitor 4 clients:
1. bpomex@vallen.com
2. svalois@aiig.com
3. rocio.santana@chemicollc.com
4. chihuahua@rshughes.com

To add/remove clients, edit `MONITORED_CLIENTS` in `.env`.

## Usage

### Start the Agent

```bash
python3 main.py
```

The agent will:
1. Validate configuration
2. Send startup WhatsApp notification
3. Perform immediate email check
4. Schedule checks every 10 minutes
5. Run continuously until stopped

### Stop the Agent

Press `Ctrl+C` in the terminal

### View Logs

```bash
# Real-time log monitoring
tail -f logs/email_monitor.log

# View last 50 lines
tail -n 50 logs/email_monitor.log

# Search for errors
grep ERROR logs/email_monitor.log

# Search for successful notifications
grep "WhatsApp message sent" logs/email_monitor.log
```

## Running in Background

### Option 1: Using nohup (Simple)

```bash
nohup python3 main.py > output.log 2>&1 &
```

To stop:
```bash
ps aux | grep main.py
kill [PID]
```

### Option 2: Using screen (Recommended)

```bash
# Install screen (if needed)
brew install screen  # macOS
# or
sudo apt-get install screen  # Linux

# Start screen session
screen -S email-agent

# Run the agent
python3 main.py

# Detach: Press Ctrl+A, then D
# Process continues running in background

# Re-attach later
screen -r email-agent

# List all sessions
screen -ls
```

### Option 3: macOS LaunchAgent (Persistent)

Create file: `~/Library/LaunchAgents/com.quimicaguba.emailagent.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.quimicaguba.emailagent</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/amauryperezverdejo/Desktop/agentes/mensajeriaPO/email-order-agent/venv/bin/python3</string>
        <string>/Users/amauryperezverdejo/Desktop/agentes/mensajeriaPO/email-order-agent/main.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/amauryperezverdejo/Desktop/agentes/mensajeriaPO/email-order-agent/logs/stdout.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/amauryperezverdejo/Desktop/agentes/mensajeriaPO/email-order-agent/logs/stderr.log</string>
</dict>
</plist>
```

Load the service:
```bash
launchctl load ~/Library/LaunchAgents/com.quimicaguba.emailagent.plist
launchctl start com.quimicaguba.emailagent

# Check status
launchctl list | grep emailagent

# Stop
launchctl stop com.quimicaguba.emailagent

# Unload
launchctl unload ~/Library/LaunchAgents/com.quimicaguba.emailagent.plist
```

## WhatsApp Message Format

When a purchase order is detected:

```
🔔 NUEVA ORDEN DE COMPRA

👤 Cliente: ACME Corporation
📧 De: bpomex@vallen.com
📅 2025-10-09

📄 Orden: PO-2025-1234

📦 Productos:
- Widget A - 100 pcs @ $5.00
- Widget B - 50 pcs @ $10.00

💰 Total: $1,000.00

📝 Entrega urgente - antes del viernes

📎 Archivo: purchase_order_oct.pdf
📧 Asunto: Nueva orden de compra...

✅ Confianza: alta
```

## Troubleshooting

### Configuration Errors

**Error**: "Missing required environment variables"

**Solution**:
```bash
# Verify .env file exists
ls -la .env

# Check content
cat .env

# Ensure all required variables are set
grep -E "PASSWORD|API_KEY|AUTH_TOKEN" .env
```

### IMAP Connection Issues

**Error**: "IMAP authentication failed"

**Solutions**:
1. Verify IMAP credentials in `.env`
2. Test connection:
   ```bash
   telnet mail.quimicaguba.com 993
   ```
3. Check if IMAP is enabled on email account
4. Verify firewall isn't blocking port 993

### Twilio WhatsApp Issues

**Error**: "Twilio API error: 63007"

**Solution**: Sandbox expired or not joined
1. Re-join Twilio Sandbox:
   - Send WhatsApp to +1 415 523 8886
   - Message: `join <your-code>`

**Error**: "Invalid Auth Token"

**Solution**:
1. Go to Twilio Console
2. Copy fresh Auth Token
3. Update `.env`

### Claude API Issues

**Error**: "Authentication error"

**Solution**:
1. Verify API key in `.env`
2. Check account has credits: https://console.anthropic.com
3. Ensure API key hasn't expired

### PDF Processing Fails

**Error**: "Could not extract text from PDF"

**Possible causes**:
- Scanned PDF (image-based, no text layer)
- Encrypted/protected PDF
- Corrupted PDF file

**Solution**: Check PDF manually, may need OCR for scanned docs

## Cost Breakdown

### Monthly Operating Costs

| Service | Usage | Cost |
|---------|-------|------|
| Claude Haiku | 100 PDFs analyzed | $0.50 |
| Claude Haiku | 500 PDFs analyzed | $2.50 |
| Twilio WhatsApp Sandbox | Unlimited* | FREE |
| **Total (100 PDFs)** | | **$0.50** |
| **Total (500 PDFs)** | | **$2.50** |

*Sandbox requires re-joining every few days

### Production WhatsApp (Optional)

For production WhatsApp (no sandbox):
- Twilio: ~$0.005 per message
- 100 messages: $0.50
- Combined with Claude: $1.00-$3.00/month

## Maintenance

### Clear Processed Emails Log

```bash
# Backup first
cp logs/processed_emails.txt logs/processed_emails_backup.txt

# Clear (all emails will be re-processed on next run)
> logs/processed_emails.txt
```

### Rotate Logs

```bash
# Archive current log
mv logs/email_monitor.log logs/email_monitor_$(date +%Y%m%d).log

# Compress old logs
gzip logs/email_monitor_*.log

# Delete logs older than 30 days
find logs -name "*.log.gz" -mtime +30 -delete
```

### Update Dependencies

```bash
pip install --upgrade -r requirements.txt
```

## Security Best Practices

- **Never commit `.env`** to version control
- **Rotate API keys** every 90 days
- **Use strong IMAP password**
- **Limit WhatsApp recipient** to trusted numbers
- **Monitor logs** for suspicious activity
- **Backup processed emails list** regularly

## Monitoring & Alerts

### Check System Health

```bash
# Check if process is running
ps aux | grep main.py

# Check recent activity
tail -20 logs/email_monitor.log

# Count processed emails today
grep "$(date +%Y-%m-%d)" logs/email_monitor.log | grep "Successfully processed" | wc -l
```

### Set Up Alerts (Optional)

Add to `config.py` to send WhatsApp alert if agent crashes:

```python
def send_crash_notification():
    # Implementation for error notifications
    pass
```

## Future Enhancements

- [ ] Web dashboard for statistics
- [ ] Support for Excel/Word attachments
- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] Multi-language support
- [ ] OCR for scanned PDFs
- [ ] Email auto-reply confirmation
- [ ] Slack/Telegram integration
- [ ] Advanced analytics & reporting

## Support

For issues or questions:

1. Check logs: `logs/email_monitor.log`
2. Verify configuration: Review `.env`
3. Test components individually:
   ```python
   from whatsapp_notifier import WhatsAppNotifier
   notifier = WhatsAppNotifier()
   notifier.send_test_message()
   ```

## License

Internal use - Química Guba

---

**Version**: 1.0.0
**Last Updated**: October 2025
**Developed for**: Química Guba
**Contact**: ventas@quimicaguba.com
