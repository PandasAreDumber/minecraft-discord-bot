# Minecraft Discord Bot

A Discord bot that monitors a Minecraft server and lets you control it from Discord.

## Features

- Checks every 60 seconds if the server is online or offline and posts to a channel when the status changes
- Detects public IP address changes and pings `@everyone` with the new address
- `!start` — start the Minecraft server (admin only)
- `!stop` — stop the Minecraft server (admin only)
- `!status` — check if the server is online and see the current IP

## Requirements

- Python 3.10+
- Java (must be on your PATH so `java` works in a terminal)
- A Discord bot token

## Setup

### 1. Create a Discord bot

1. Go to https://discord.com/developers/applications and click **New Application**
2. Go to the **Bot** tab, click **Add Bot**
3. Under **Privileged Gateway Intents**, enable **Message Content Intent**
4. Copy the token — you'll need it in a moment
5. Go to **OAuth2 → URL Generator**, select `bot` scope, then tick these permissions:
   - Send Messages
   - Mention Everyone
6. Open the generated URL in your browser and invite the bot to your server

### 2. Get your channel ID

1. In Discord, go to **Settings → Advanced** and enable **Developer Mode**
2. Right-click the channel where you want status updates and click **Copy Channel ID**

### 3. Configure the bot

```
# On the server PC, in the project folder:
copy .env.example .env
notepad .env
```

Fill in all the values in `.env`. Do **not** commit `.env` to GitHub — it contains your bot token.

### 4. Install dependencies

```
pip install -r requirements.txt
```

### 5. Run the bot

```
python bot.py
```

To keep it running after you close the terminal, use a tool like [NSSM](https://nssm.cc/) to run it as a Windows service, or simply start it in a persistent terminal session.

## Pulling updates from GitHub (on the server PC)

```
git pull
pip install -r requirements.txt   # only needed if requirements changed
python bot.py
```

## Commands

| Command   | Who can use it | Description                        |
|-----------|----------------|------------------------------------|
| `!status` | Everyone       | Shows online/offline status and IP |
| `!start`  | Admins only    | Starts the Minecraft server        |
| `!stop`   | Admins only    | Stops the Minecraft server         |

## Notes

- `!start` and `!stop` only work when the bot is running on the **same machine** as the server
- If the server was started before the bot, `!stop` will not work — stop it manually or restart it via `!stop` after using `!start` through the bot
- The `@everyone` ping on IP change requires the bot to have **Mention Everyone** permission in that channel
