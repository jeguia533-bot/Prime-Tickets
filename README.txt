Prime Stock Bot - Railway Ready

Files:
- bot.py
- requirements.txt
- Procfile
- .env.example

Railway setup:
1. Upload/deploy this folder through GitHub.
2. In Railway, go to Variables.
3. Add:
   DISCORD_TOKEN=your_bot_token_here
4. Deploy.
5. In Discord, run:
   /ping
   /ticketpanel

Developer Portal:
- Enable Server Members Intent
- Enable Message Content Intent
- Invite with bot + applications.commands scopes
- Give Manage Channels, Manage Messages, Send Messages, Read Message History, Embed Links, Attach Files



Crash fix:
- Railway may default to Python 3.13.
- Python 3.13 removed audioop, which discord.py imports.
- This project includes runtime.txt forcing Python 3.12.7.
- It also includes audioop-lts as a backup package.
