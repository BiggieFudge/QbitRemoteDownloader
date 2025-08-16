# QbitRemoteDownloader

A private Telegram bot that allows authorized users to search for movies and TV shows on TorrentLeech and automatically download them to qBittorrent with organized file structure.

## Features

- 🔐 **Private Access**: Only authorized users can access the bot
- 🎬 **Movie & TV Show Search**: Search for content using Prowlarr
- 🆓 **Freeleech Only**: Automatically filters for freeleech torrents
- 📁 **Organized Downloads**: Movies go to `E:\Movies\{Title (Year)}`, TV shows to `E:\TVShows\{Title}`
- ⚡ **qBittorrent Integration**: Direct magnet link downloads with improved search
- 📱 **Telegram Notifications**: Get notified when downloads complete
- 🔮 **Future Downloads**: Set up auto-download rules for upcoming content
- 📺 **Smart TV Rules**: Configure season-specific download rules
- 🎬 **Movie Rules**: Auto-download movies when they become available
- 🔄 **Pagination**: Browse through search results easily

## Prerequisites

- Python 3.8 or higher
- qBittorrent with Web UI enabled
- Prowlarr instance with TorrentLeech indexer configured
- TMDB API key for movie/TV show information
- Telegram Bot Token

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd QbitRemoteDownloader
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   # or
   source .venv/bin/activate  # On Linux/Mac
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment file**:
   Create a `.env` file in the project root with the following content:
   ```env
   # Telegram Bot Configuration
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   
   # Prowlarr Configuration
   PROWLARR_API_KEY=your_prowlarr_api_key_here
   PROWLARR_BASE_URL=http://localhost:9696
   
   # TMDB Configuration
   TMDB_API_KEY=your_tmdb_api_key_here
   
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

## Setup Instructions

### 1. Create a Telegram Bot

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token and add it to your `.env` file

### 2. Get Your Telegram User ID

1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. It will reply with your user ID
3. Add your user ID to the `AUTHORIZED_USERS` in your `.env` file

### 3. Configure qBittorrent

1. Open qBittorrent
2. Go to **Tools** → **Options** → **Web UI**
3. Enable Web UI
4. Set port to `8080` (or update in `.env`)
5. Set username and password (or update in `.env`)
6. Apply and restart qBittorrent

### 4. Create Download Directories

Create the following directories:
- `E:\Movies` (or your preferred movies path)
- `E:\TVShows` (or your preferred TV shows path)

## Usage

### Starting the Bot

```bash
python main.py
```

### Bot Commands

- `/start` - Start the bot and show main menu
- `/search` - Search for movies or TV shows
- `/downloads` - View your download history
- `/help` - Show help information

### Using the Bot

1. **Start the bot** with `/start`
2. **Choose content type** (Movies or TV Shows)
3. **Enter search query** (e.g., "Avengers Endgame")
4. **Browse results** and select a torrent
5. **Confirm download** - the bot will add it to qBittorrent
6. **Get notified** when download completes

## Project Structure

```
QbitRemoteDownloader/
├── config/
│   ├── __init__.py
│   └── settings.py          # Configuration management
├── models/
│   ├── __init__.py
│   └── database.py          # Database operations
├── services/
│   ├── __init__.py
│   ├── telegram_bot.py      # Main bot logic
│   ├── prowlarr_client.py   # Prowlarr API client
│   ├── tmdb_client.py       # TMDB API client
│   └── qbittorrent_client.py # qBittorrent API client
├── tests/                   # Test files
│   ├── __init__.py
│   ├── README.md
│   └── test_basic.py        # Basic functionality tests
├── utils/
│   ├── __init__.py
│   └── helpers.py           # Utility functions
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token | Yes |
| `PROWLARR_API_KEY` | Your Prowlarr API key | Yes |
| `PROWLARR_BASE_URL` | Prowlarr instance URL | No (default: http://localhost:9696) |
| `TMDB_API_KEY` | Your TMDB API key | Yes |
| `QBITTORRENT_HOST` | qBittorrent Web UI host | No (default: localhost) |
| `QBITTORRENT_PORT` | qBittorrent Web UI port | No (default: 8080) |
| `QBITTORRENT_USERNAME` | qBittorrent Web UI username | No (default: admin) |
| `QBITTORRENT_PASSWORD` | qBittorrent Web UI password | No (default: admin) |
| `MOVIES_DOWNLOAD_PATH` | Path for movie downloads | No (default: E:\Movies) |
| `TVSHOWS_DOWNLOAD_PATH` | Path for TV show downloads | No (default: E:\TVShows) |
| `AUTHORIZED_USERS` | Comma-separated list of Telegram user IDs | Yes |

### Adding More Users

To add more authorized users:

1. Get their Telegram user ID (ask them to message @userinfobot)
2. Add their user ID to the `AUTHORIZED_USERS` in your `.env` file:
   ```env
   AUTHORIZED_USERS=123456789,987654321,555666777
   ```

## Recent Improvements

### Version 2.0 Updates

- **Improved Search Logic**: Better torrent name matching with space-to-dot conversion
- **Enhanced Path Organization**: 
  - Movies: `E:\Movies\Movie Name (2024)\`
  - TV Shows: `E:\TVShows\Show Name\`
- **Future Downloads**: Set up auto-download rules for upcoming content
- **TV Show Rules**: Configure season-specific download rules with user input
- **Rule Duplication Check**: Prevents creating duplicate auto-download rules
- **Removed Download Status**: Simplified interface by removing non-functional status feature
- **Test Organization**: Moved all tests to dedicated `tests/` directory

### Search Improvements

The bot now uses improved search logic that:
- Replaces spaces with dots (common in torrent names)
- Handles multiple search patterns for better matching
- Focuses on show/movie names and season/episode information
- Provides more accurate torrent identification

## Troubleshooting

### Common Issues

1. **"You are not authorized to use this bot"**
   - Check that your Telegram user ID is in the `AUTHORIZED_USERS` list
   - Verify the user ID format (should be numbers only)

2. **"Failed to connect to qBittorrent"**
   - Ensure qBittorrent is running
   - Check Web UI is enabled and accessible
   - Verify username/password in `.env` file

3. **"No results found"**
   - Check your Prowlarr API key
   - Verify your Prowlarr instance is running
   - Ensure TorrentLeech indexer is configured in Prowlarr
   - Try different search terms

4. **"Failed to add torrent to qBittorrent"**
   - Check qBittorrent is running
   - Verify download paths exist
   - Check qBittorrent Web UI credentials

### Logs

The bot creates a `bot.log` file with detailed logs. Check this file for debugging information.

## Security Notes

- Keep your `.env` file secure and never commit it to version control
- The bot only works with authorized users listed in the configuration
- All downloads are freeleech only to avoid ratio issues
- The bot runs locally on your machine

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for personal use only. Please respect the terms of service of TorrentLeech and other services used.

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the logs in `bot.log`
3. Ensure all prerequisites are met
4. Verify your configuration in `.env`

---

**Note**: This bot is designed for personal use with authorized users only. Please ensure you comply with all applicable laws and terms of service. 
