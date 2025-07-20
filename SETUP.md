# Setup Guide

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Create `.env` file** in the project root with the following content:
   ```env
   # Telegram Bot Configuration
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   
   # TorrentLeech Configuration
   TORRENTLEECH_API_TOKEN=your_torrentleech_api_token_here
   
   # qBittorrent Configuration
   QBITTORRENT_HOST=localhost
   QBITTORRENT_PORT=8080
   QBITTORRENT_USERNAME=admin
   QBITTORRENT_PASSWORD=admin
   
   # Download Paths
   MOVIES_DOWNLOAD_PATH=E:\Movies
   TVSHOWS_DOWNLOAD_PATH=E:\TVShows
   
   # Authorized Users (comma-separated Telegram user IDs)
   AUTHORIZED_USERS=your_telegram_user_id_here
   ```

3. **Run the bot**:
   ```bash
   python main.py
   ```

## Detailed Setup Instructions

### Step 1: Create Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Choose a name for your bot (e.g., "My Torrent Downloader")
4. Choose a username (must end with 'bot', e.g., "mytorrentdownloader_bot")
5. Copy the bot token (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
6. Add it to your `.env` file as `TELEGRAM_BOT_TOKEN`

### Step 2: Get Your Telegram User ID

1. Open Telegram and search for `@userinfobot`
2. Send any message to it
3. It will reply with your user ID (a number like `123456789`)
4. Add your user ID to the `AUTHORIZED_USERS` in your `.env` file

### Step 3: Configure qBittorrent

1. Open qBittorrent
2. Go to **Tools** → **Options** → **Web UI**
3. Check "Web User Interface (Remote control)"
4. Set port to `8080`
5. Set username to `admin` (or your preferred username)
6. Set password to `admin` (or your preferred password)
7. Click **Apply** and restart qBittorrent
8. Test by opening `http://localhost:8080` in your browser

### Step 4: Get TorrentLeech API Token

1. Log in to your TorrentLeech account
2. Go to your profile settings
3. Look for API or Developer settings
4. Generate an API token
5. Add the token to your `.env` file as `TORRENTLEECH_API_TOKEN`

### Step 5: Create Download Directories

Create these folders on your system:
- `E:\Movies` (for movie downloads)
- `E:\TVShows` (for TV show downloads)

Or update the paths in your `.env` file to match your preferred locations.

### Step 6: Test the Bot

1. Start the bot: `python main.py`
2. Open Telegram and find your bot
3. Send `/start` command
4. You should see the main menu with options

## Adding More Users

To allow other people to use your bot:

1. Ask them to message `@userinfobot` to get their user ID
2. Add their user ID to the `AUTHORIZED_USERS` in your `.env` file:
   ```env
   AUTHORIZED_USERS=123456789,987654321,555666777
   ```
3. Restart the bot

## Troubleshooting

### Bot doesn't respond
- Check that your user ID is in the `AUTHORIZED_USERS` list
- Verify the bot token is correct
- Make sure the bot is running (`python main.py`)

### Can't connect to qBittorrent
- Ensure qBittorrent is running
- Check Web UI is enabled on port 8080
- Verify username/password in `.env` file
- Try accessing `http://localhost:8080` in browser

### No search results
- Check your TorrentLeech API token
- Verify your TorrentLeech account is active
- Try different search terms

### Downloads not starting
- Check qBittorrent is running
- Verify download paths exist
- Check qBittorrent Web UI credentials

## Configuration Options

### Download Paths
You can customize where files are downloaded:

```env
MOVIES_DOWNLOAD_PATH=D:\MyMovies
TVSHOWS_DOWNLOAD_PATH=D:\MyTVShows
```

### qBittorrent Settings
If you changed the default qBittorrent Web UI settings:

```env
QBITTORRENT_HOST=localhost
QBITTORRENT_PORT=8080
QBITTORRENT_USERNAME=your_username
QBITTORRENT_PASSWORD=your_password
```

### Multiple Users
Add multiple user IDs separated by commas:

```env
AUTHORIZED_USERS=123456789,987654321,555666777
```

## Security Notes

- Keep your `.env` file secure and never share it
- The bot only works with authorized users
- All downloads are freeleech only
- The bot runs locally on your machine

## Getting Help

If you encounter issues:

1. Check the logs in `bot.log`
2. Verify all prerequisites are installed
3. Ensure all configuration is correct
4. Test each component individually

The bot will show helpful error messages if something is misconfigured. 