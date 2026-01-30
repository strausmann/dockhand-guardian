# Webhook Documentation

This document describes the webhook notification system in Dockhand Guardian, powered by [Apprise](https://github.com/caronc/apprise).

## Overview

Dockhand Guardian uses Apprise to send notifications to 80+ services when recovery actions are triggered. Notifications are sent after both successful and failed recovery attempts.

## Why Apprise?

[Apprise](https://github.com/caronc/apprise) is a mature, well-maintained Python library that provides:
- 🎯 **80+ services** supported out of the box
- 🔧 **Unified API** for all notification services
- 📝 **URL-based configuration** (simple and portable)
- 🛡️ **Well tested** and actively maintained
- 🚀 **Zero custom code** required for new services

## Configuration

Configure webhooks via the `WEBHOOK_URLS` environment variable using Apprise URL format:

```yaml
environment:
  # Single service
  WEBHOOK_URLS: discord://webhook_id/webhook_token
  
  # Multiple services (comma-separated)
  WEBHOOK_URLS: discord://ID/TOKEN,msteams://A/B/C/,slack://X/Y/Z/
```

## Supported Services

### Discord

**Setup:**
1. Open your Discord server
2. Go to Server Settings → Integrations
3. Click "Webhooks" → "New Webhook"
4. Name it (e.g., "Dockhand Guardian")
5. Select the channel
6. Copy the Webhook URL: `https://discord.com/api/webhooks/ID/TOKEN`

**Configuration:**
```yaml
WEBHOOK_URLS: discord://webhook_id/webhook_token
```

**Example:**
```yaml
WEBHOOK_URLS: discord://123456789012345678/AbCdEfGhIjKlMnOpQrStUvWxYz1234567890
```

### Microsoft Teams

**Setup:**
1. Open your Teams channel
2. Click the three dots (•••) → "Connectors"
3. Search for "Incoming Webhook"
4. Click "Configure"
5. Name it and copy the webhook URL
6. Extract tokens from URL

**Configuration:**
```yaml
WEBHOOK_URLS: msteams://TokenA/TokenB/TokenC/
```

**URL Format:** The Teams webhook URL looks like:
```
https://outlook.office.com/webhook/GUID@GUID/IncomingWebhook/HASH/GUID
```
Convert it to Apprise format by extracting the tokens.

### Slack

**Setup:**
1. Create a Slack App: https://api.slack.com/apps
2. Enable "Incoming Webhooks"
3. Add webhook to workspace
4. Copy the webhook URL tokens

**Configuration:**
```yaml
WEBHOOK_URLS: slack://TokenA/TokenB/TokenC/
```

### Email (SMTP)

**Gmail Example:**
```yaml
WEBHOOK_URLS: mailto://user:password@gmail.com?to=alerts@example.com
```

**Generic SMTP:**
```yaml
WEBHOOK_URLS: mailto://user:pass@mail.example.com?smtp=mail.example.com&from=guardian@example.com&to=admin@example.com
```

### Telegram

**Setup:**
1. Create a bot via [@BotFather](https://t.me/botfather)
2. Get your chat ID
3. Use bot token and chat ID

**Configuration:**
```yaml
WEBHOOK_URLS: tgram://bot_token/chat_id
```

### Pushover

**Configuration:**
```yaml
WEBHOOK_URLS: pover://user_key@token
```

### Matrix

**Configuration:**
```yaml
WEBHOOK_URLS: matrix://user:password@hostname/#room
```

### JSON (Generic Webhook)

For custom JSON endpoints:

**Configuration:**
```yaml
WEBHOOK_URLS: json://example.com/endpoint
# or with headers:
WEBHOOK_URLS: json://example.com/endpoint?+HeaderKey=value
```

### IFTTT

**Configuration:**
```yaml
WEBHOOK_URLS: ifttt://webhook_id/event_name
```

### More Services

Apprise supports many more services. See the [complete list](https://github.com/caronc/apprise/wiki#notification-services):
- Gotify
- Mattermost
- Rocket.Chat
- Prowl
- PushBullet
- Pushjet
- Discord
- Gitter
- AWS SNS
- AWS SES
- Microsoft Teams
- Office 365
- And 60+ more!

## Multiple Notifications

Send to multiple services simultaneously by separating URLs with commas:

```yaml
WEBHOOK_URLS: discord://ID/TOKEN,mailto://user:pass@gmail.com,slack://A/B/C/
```

All services will receive notifications when recovery is triggered.

## Notification Format

Notifications include:

**Title:**
```
✅ Dockhand Guardian Alert  (success)
❌ Dockhand Guardian Alert  (failure)
```

**Body:**
```
**Recovery Successful**

🐳 **Affected Containers:**
  • dockhand-app
  • dockhand-database

⏰ **Timestamp:** 2026-01-30 12:34:56
```

## Testing Webhooks

### Test with a stopped container

```bash
# Stop a monitored container
docker stop dockhand-app

# Watch guardian logs
docker compose logs -f guardian

# Wait for grace period to expire
# Guardian will trigger recovery and send notification
```

### Test Apprise URLs manually

```bash
# Install apprise CLI
pip install apprise

# Test a Discord webhook
apprise -t "Test" -b "This is a test" discord://webhook_id/token

# Test multiple services
apprise -t "Test" -b "Message" discord://ID/TOKEN slack://A/B/C/
```

### Webhook Testing Services

- [webhook.site](https://webhook.site) - View incoming webhooks
- [RequestBin](https://requestbin.com) - Inspect webhook payloads
- Use Apprise JSON endpoint for debugging

## Troubleshooting

### No notifications received

1. **Check configuration:**
   ```bash
   docker compose exec guardian env | grep WEBHOOK
   ```

2. **Verify URL format:**
   - Discord: `discord://webhook_id/webhook_token`
   - Teams: `msteams://TokenA/TokenB/TokenC/`
   - Slack: `slack://TokenA/TokenB/TokenC/`

3. **Check guardian logs:**
   ```bash
   docker compose logs guardian | grep -i webhook
   ```

4. **Test URL manually:**
   ```bash
   docker compose exec guardian python3 -c "
   import apprise
   apobj = apprise.Apprise()
   apobj.add('YOUR_WEBHOOK_URL')
   apobj.notify(title='Test', body='Testing...')
   "
   ```

### Wrong format or service not supported

1. Check [Apprise documentation](https://github.com/caronc/apprise/wiki) for correct URL format
2. Ensure service is in [supported list](https://github.com/caronc/apprise/wiki#notification-services)
3. Try using JSON endpoint as fallback for unsupported services

### Notifications delayed

- Notifications are sent synchronously during recovery
- Network issues can cause delays
- Multiple services are notified in sequence

## Advanced Configuration

### Custom Apprise Config File

For complex setups, you can use an Apprise configuration file:

```yaml
volumes:
  - ./apprise.yml:/etc/apprise.yml:ro

environment:
  WEBHOOK_URLS: file:///etc/apprise.yml
```

**apprise.yml:**
```yaml
urls:
  - discord://webhook_id/token:
      - tag: critical
  - mailto://user:pass@gmail.com:
      - tag: all
```

### Environment Variable Substitution

```yaml
WEBHOOK_URLS: discord://${DISCORD_WEBHOOK_ID}/${DISCORD_WEBHOOK_TOKEN}
```

## Security Considerations

- **Keep webhook URLs secret** - they grant posting access
- **Use HTTPS** - Apprise supports HTTPS by default
- **Rotate webhooks** periodically
- **Use environment variables** for sensitive tokens
- **Monitor for abuse** - check logs for unauthorized usage
- **Limit permissions** - webhook should only post to specific channels

## Performance

- Notifications are **synchronous** - recovery waits for webhook delivery
- Each service is notified **sequentially**
- Timeout is handled by Apprise (typically 4-10 seconds per service)
- Failed notifications are logged but don't block recovery

## Examples

### Production Setup (Discord + Email)

```yaml
environment:
  WEBHOOK_URLS: discord://ID/TOKEN,mailto://guardian:pass@smtp.gmail.com?to=ops@company.com
```

### Development Setup (Slack)

```yaml
environment:
  WEBHOOK_URLS: slack://xoxb-token/channel
```

### High Availability (Multiple Channels)

```yaml
environment:
  WEBHOOK_URLS: discord://ops-ID/TOKEN,discord://backup-ID/TOKEN,mailto://admin@company.com
```

## Future Enhancements

Potential improvements:
1. **Async delivery** - Non-blocking webhook sends
2. **Retry logic** - Automatic retries on failure (via Apprise)
3. **Custom templates** - User-defined message formats
4. **Webhook queue** - Buffer for high-volume scenarios
5. **Config file support** - Native apprise.yml mounting

## References

- [Apprise GitHub](https://github.com/caronc/apprise)
- [Apprise Documentation](https://github.com/caronc/apprise/wiki)
- [Supported Services](https://github.com/caronc/apprise/wiki#notification-services)
- [URL Format Guide](https://github.com/caronc/apprise/wiki#notification-services)

