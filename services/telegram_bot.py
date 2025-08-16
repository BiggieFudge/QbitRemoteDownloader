import logging
import asyncio
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from typing import Dict, List, Optional
import json

from config.settings import Settings
from services.prowlarr_client import ProwlarrClient
from services.qbittorrent_client import QBittorrentClient
from services.tmdb_client import TMDBClient
from models.database import Database

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.settings = Settings()
        self.prowlarr_client = ProwlarrClient()
        self.qbittorrent_client = QBittorrentClient()
        self.tmdb_client = TMDBClient()
        self.database = Database()
        
        # Log authorized users on startup
        logger.info(f"Bot initialized with {len(self.settings.AUTHORIZED_USERS)} authorized users: {self.settings.AUTHORIZED_USERS}")
        
        # Initialize bot application
        self.application = Application.builder().token(self.settings.TELEGRAM_BOT_TOKEN).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup all command and message handlers."""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("search", self.search_command))
        self.application.add_handler(CommandHandler("downloads", self.downloads_command))

        self.application.add_handler(CommandHandler("debug", self.debug_command))
        self.application.add_handler(CommandHandler("cleanup", self.cleanup_command))
        
        # Message handlers
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Callback query handlers
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        first_name = update.effective_user.first_name or "Unknown"
        
        logger.info(f"[START] User {user_id} (@{username}, {first_name}) requested /start command")
        
        if not self._is_authorized_user(user_id):
            logger.warning(f"[AUTH] User {user_id} (@{username}) is NOT authorized. Authorized users: {self.settings.AUTHORIZED_USERS}")
            await update.message.reply_text("❌ You are not authorized to use this bot.")
            return
        
        logger.info(f"[AUTH] User {user_id} (@{username}) is authorized")
        
        # Create or update user session
        self.database.create_user_session(user_id, 'idle')
        
        keyboard = [
            [InlineKeyboardButton("🎬 Search Movies", callback_data="search_movies")],
            [InlineKeyboardButton("📺 Search TV Show Episodes", callback_data="search_tv_episodes")],
            [InlineKeyboardButton("📦 Search TV Show Boxsets", callback_data="search_tv_boxsets")],
            [InlineKeyboardButton("🔮 Future Downloads", callback_data="future_downloads")],
            [InlineKeyboardButton("📥 My Downloads", callback_data="my_downloads")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎬 Welcome to Torrent Downloader Bot!\n\n"
            "What would you like to do?",
            reply_markup=reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        
        logger.info(f"[HELP] User {user_id} (@{username}) requested /help command")
        
        if not self._is_authorized_user(user_id):
            logger.warning(f"[AUTH] User {user_id} (@{username}) is NOT authorized for /help")
            return
        
        help_text = """
🤖 **Torrent Downloader Bot Help**

**Commands:**
• `/start` - Start the bot
• `/search` - Search for content
• `/downloads` - View your downloads
• `/help` - Show this help

**Features:**
• Search for movies and TV shows
• Freeleech torrents only
• Automatic download to qBittorrent
• Download completion notifications
• Organized file structure

**Usage:**
1. Choose to search movies or TV shows
2. Enter your search query
3. Browse results and select a torrent
4. Confirm download
5. Get notified when complete!
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /search command."""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        
        logger.info(f"[SEARCH] User {user_id} (@{username}) requested /search command")
        
        if not self._is_authorized_user(user_id):
            logger.warning(f"[AUTH] User {user_id} (@{username}) is NOT authorized for /search")
            return
        
        keyboard = [
            [InlineKeyboardButton("🎬 Search Movies", callback_data="search_movies")],
            [InlineKeyboardButton("📺 Search TV Show Episodes", callback_data="search_tv_episodes")],
            [InlineKeyboardButton("📦 Search TV Show Boxsets", callback_data="search_tv_boxsets")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "What type of content would you like to search for?",
            reply_markup=reply_markup
        )
    
    async def downloads_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /downloads command."""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        
        logger.info(f"[DOWNLOADS] User {user_id} (@{username}) requested /downloads command")
        
        if not self._is_authorized_user(user_id):
            logger.warning(f"[AUTH] User {user_id} (@{username}) is NOT authorized for /downloads")
            return
        
        await self._show_downloads(update, context)
    

    
    async def debug_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /debug command for troubleshooting."""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        first_name = update.effective_user.first_name or "Unknown"
        last_name = update.effective_user.last_name or ""
        
        logger.info(f"[DEBUG] User {user_id} (@{username}) requested /debug command")
        
        # Always allow debug command for troubleshooting
        debug_info = f"""
🔍 **Debug Information**

👤 **User Details:**
• User ID: `{user_id}`
• Username: @{username}
• Name: {first_name} {last_name}

🔐 **Authorization:**
• Is Authorized: {'✅ Yes' if self._is_authorized_user(user_id) else '❌ No'}
• Authorized Users: `{self.settings.AUTHORIZED_USERS}`
• Total Authorized: {len(self.settings.AUTHORIZED_USERS)}

⚙️ **Bot Configuration:**
• Bot Token: {'✅ Set' if self.settings.TELEGRAM_BOT_TOKEN else '❌ Missing'}
• Prowlarr API: {'✅ Set' if self.settings.PROWLARR_API_KEY else '❌ Missing'}
• TMDB API: {'✅ Set' if self.settings.TMDB_API_KEY else '❌ Missing'}

📊 **Session Data:**
• User Session: {'✅ Active' if self.database.get_user_session(user_id) else '❌ None'}
• Context Data Keys: {list(context.user_data.keys()) if context.user_data else 'None'}
        """
        
        await update.message.reply_text(debug_info, parse_mode='Markdown')
    
    async def cleanup_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /cleanup command for database maintenance."""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        
        logger.info(f"[CLEANUP] User {user_id} (@{username}) requested /cleanup command")
        
        if not self._is_authorized_user(user_id):
            logger.warning(f"[AUTH] User {user_id} (@{username}) is NOT authorized for /cleanup")
            return
        
        # Get count of old downloads before cleanup
        old_downloads = self.database.get_all_downloads_older_than(24)
        old_count = len(old_downloads)
        
        # Perform cleanup
        deleted_count = self.database.cleanup_old_downloads(hours=24)
        
        cleanup_info = f"""
🧹 **Database Cleanup Completed!**

📊 **Cleanup Results:**
• Old downloads found: {old_count}
• Downloads deleted: {deleted_count}
• Time period: Last 24 hours

💾 **Database Status:**
• Only recent downloads (last 24h) are kept
• Old completed downloads are automatically removed
• This helps keep the database clean and fast

🔄 **Next cleanup:** Automatic cleanup runs daily
        """
        
        await update.message.reply_text(cleanup_info, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages."""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        message_text = update.message.text
        
        logger.info(f"[MESSAGE] User {user_id} (@{username}) sent message: '{message_text[:50]}{'...' if len(message_text) > 50 else ''}'")
        
        if not self._is_authorized_user(user_id):
            logger.warning(f"[AUTH] User {user_id} (@{username}) is NOT authorized for message handling")
            return
        
        # Check if user is in future search mode
        future_search_type = context.user_data.get('future_search_type')
        if future_search_type:
            logger.info(f"[FUTURE_SEARCH] User {user_id} (@{username}) in future search mode: {future_search_type}")
            await self._handle_future_search_query(update, context)
            return
        
        # Check if user is waiting for season input
        if context.user_data.get('waiting_for_season'):
            logger.info(f"[SEASON_INPUT] User {user_id} (@{username}) entering season number")
            await self._handle_season_input(update, context)
            return
        
        user_session = self.database.get_user_session(user_id)
        if not user_session:
            logger.info(f"[SESSION] User {user_id} (@{username}) has no active session, redirecting to /start")
            await update.message.reply_text("Please use /start to begin.")
            return
        
        current_state = user_session['current_state']
        logger.info(f"[SESSION] User {user_id} (@{username}) current state: {current_state}")
        
        if current_state == 'waiting_for_search_query':
            await self._handle_search_query(update, context)
        else:
            await update.message.reply_text("Please use /start to begin.")
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards."""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        username = query.from_user.username or "Unknown"
        callback_data = query.data
        
        logger.info(f"[CALLBACK] User {user_id} (@{username}) clicked callback: {callback_data}")
        
        if not self._is_authorized_user(user_id):
            logger.warning(f"[AUTH] User {user_id} (@{username}) is NOT authorized for callback: {callback_data}")
            await query.edit_message_text("❌ You are not authorized to use this bot.")
            return
        
        data = query.data
        
        if data.startswith("search_"):
            await self._handle_search_type(query, data, context)
        elif data.startswith("search_results_"):
            await self._handle_search_results(query, data, context=context)
        elif data.startswith("download_"):
            await self._handle_download_selection(query, data, context=context)
        elif data.startswith("confirm_download_"):
            await self._handle_confirm_download(query, data, context=context)
        elif data == "cancel_download":
            await query.edit_message_text("❌ Download cancelled.")
        elif data.startswith("page_"):
            await self._handle_search_results(query, data, context=context)
        elif data == "my_downloads":
            await self._show_downloads(query, context)

        elif data == "back_to_main":
            await self._show_main_menu(query)
        elif data == "future_downloads":
            await self._handle_future_downloads(query, data, context)
        elif data.startswith("future_"):
            await self._handle_future_downloads(query, data, context)
        elif data.startswith("create_rule_"):
            await self._handle_create_rule(query, data, context)
        elif data.startswith("replace_rule_"):
            await self._handle_replace_rule(query, data, context)

        else:
            await query.edit_message_text("❌ Unknown action.")
    
    async def _handle_search_type(self, query, data, context):
        """Handle search type selection."""
        user_id = query.from_user.id
        username = query.from_user.username or "Unknown"
        search_type = data.split("_", 1)[1]  # movies, tv_episodes, or tv_boxsets
        
        logger.info(f"[SEARCH_TYPE] User {user_id} (@{username}) selected search type: {search_type}")
        
        context.user_data['search_type'] = search_type
        
        # Update user session to waiting for search query
        self.database.update_user_session(user_id, 'waiting_for_search_query')
        
        prompt = {
            'movies': 'movie',
            'tv_episodes': 'TV show episode',
            'tv_boxsets': 'TV show boxset'
        }.get(search_type, 'content')
        
        await query.edit_message_text(
            f"🔍 Enter the title of the {prompt} you want to search for:"
        )
    
    async def _handle_search_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        user_session = self.database.get_user_session(user_id)
        search_type = context.user_data.get('search_type', 'movies')
        query_text = update.message.text
        
        logger.info(f"[SEARCH_QUERY] User {user_id} (@{username}) searching for '{query_text}' with type '{search_type}'")
        
        await update.message.reply_text(f"🔍 Searching for '{query_text}'...")
        try:
            # Perform search
            if search_type == 'movies':
                results = self.prowlarr_client.search_movies(query_text, page=0)
            elif search_type == 'tv_episodes':
                results = self.prowlarr_client.search_tv_episodes(query_text, page=0)
            elif search_type == 'tv_boxsets':
                results = self.prowlarr_client.search_tv_boxsets(query_text, page=0)
            else:
                results = self.prowlarr_client.search_movies(query_text, page=0)
            
            if not results or not results.get('torrents'):
                logger.info(f"[SEARCH_RESULTS] User {user_id} (@{username}) - No results found for '{query_text}'")
                await update.message.reply_text(
                    f"❌ No results found for '{query_text}'.\nTry a different search term."
                )
                return
            
            logger.info(f"[SEARCH_RESULTS] User {user_id} (@{username}) - Found {len(results.get('torrents', []))} results for '{query_text}'")
            
            context.user_data['search_results'] = results
            context.user_data['search_query'] = query_text
            context.user_data['search_type'] = search_type
            await self._display_search_results(update.message, results, 0, context)
        except Exception as e:
            logger.error(f"[SEARCH_ERROR] User {user_id} (@{username}) - Error during search: {e}")
            await update.message.reply_text(f"❌ Error during search: {str(e)}")
    
    async def _handle_future_search_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle future search queries for movies and TV shows."""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        query_text = update.message.text
        future_search_type = context.user_data.get('future_search_type')
        
        logger.info(f"[FUTURE_SEARCH_QUERY] User {user_id} (@{username}) searching for '{query_text}' with type '{future_search_type}'")
        
        await update.message.reply_text(f"🔍 Searching for '{query_text}'...")
        
        try:
            if future_search_type == 'movie':
                results = self.tmdb_client.search_movie(query_text)
                if not results:
                    logger.info(f"[FUTURE_SEARCH_RESULTS] User {user_id} (@{username}) - No movies found for '{query_text}'")
                    await update.message.reply_text(
                        f"❌ No movies found for '{query_text}'.\nTry a different search term."
                    )
                    return
                
                logger.info(f"[FUTURE_SEARCH_RESULTS] User {user_id} (@{username}) - Found {len(results)} movies for '{query_text}'")
                
                # Show movie results with quality selection
                text = f"🎬 **Movies Found for '{query_text}'**\n\n"
                keyboard = []
                
                # Filter movies to only show those released within the last 2 months
                filtered_movies = [movie for movie in results if self.tmdb_client.is_recently_released_movie(movie, days_threshold=60)]
                
                if not filtered_movies:
                    text += "❌ **No recently released movies found**\n"
                    text += "Only movies released within the last 2 months are shown.\n"
                    text += "Try searching for a different movie or check back later."
                else:
                    for i, movie in enumerate(filtered_movies[:5]):  # Show first 5 filtered results
                        title = movie.get('title', 'Unknown')
                        release_date = movie.get('release_date', 'Unknown')
                        movie_id = movie.get('id')
                        is_upcoming = self.tmdb_client.is_upcoming_movie(movie)
                        
                        text += f"🎬 **{title}**\n"
                        text += f"📅 Release: {release_date}\n"
                        text += f"🔮 Status: {'🟡 Upcoming' if is_upcoming else '🟢 Released'}\n\n"
                        
                        # Add quality selection buttons for filtered movies
                        keyboard.append([
                            InlineKeyboardButton(f"1080p", callback_data=f"create_rule_movie_{movie_id}_1080p"),
                            InlineKeyboardButton(f"2160p", callback_data=f"create_rule_movie_{movie_id}_2160p")
                        ])
                
                keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="future_movies")])
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
                
            elif future_search_type == 'tv':
                results = self.tmdb_client.search_tv_show(query_text)
                if not results:
                    logger.info(f"[FUTURE_SEARCH_RESULTS] User {user_id} (@{username}) - No TV shows found for '{query_text}'")
                    await update.message.reply_text(
                        f"❌ No TV shows found for '{query_text}'.\nTry a different search term."
                    )
                    return
                
                logger.info(f"[FUTURE_SEARCH_RESULTS] User {user_id} (@{username}) - Found {len(results)} TV shows for '{query_text}'")
                
                # Get detailed info for each result and filter for shows in production
                text = f"📺 **TV Shows in Production for '{query_text}'**\n\n"
                keyboard = []
                shows_in_production = []
                
                for i, tv_show in enumerate(results[:10]):  # Check more results to find production shows
                    name = tv_show.get('name', 'Unknown')
                    first_air_date = tv_show.get('first_air_date', 'Unknown')
                    tv_id = tv_show.get('id')
                    
                    # Get detailed info to check if in production
                    if tv_id:
                        detailed = self.tmdb_client.get_tv_show_details(tv_id)
                        if detailed:
                            is_in_production = self.tmdb_client.is_show_in_production(detailed)
                            last_season_info = self.tmdb_client.get_last_season_info(detailed)
                            
                            # Only show shows that are in production and have season info
                            if is_in_production and last_season_info:
                                season_number = last_season_info['season_number']
                                episode_count = last_season_info['episode_count']
                                status = self.tmdb_client.get_tv_show_status(detailed)
                                
                                # Determine the target season for auto-download
                                if episode_count == 0:
                                    target_season = season_number  # This is the next season to be released
                                    season_display = f"Next Season: {season_number}"
                                else:
                                    target_season = season_number  # Use current season
                                    season_display = f"Current Season: {season_number}"
                                
                                text += f"📺 **{name}**\n"
                                text += f"📅 First Air: {first_air_date}\n"
                                text += f"🔮 Status: {status}\n"
                                text += f"🟢 **In Production** - {season_display}\n"
                                text += f"📊 Season {season_number}: {episode_count} episodes\n\n"
                                
                                # Add quality selection buttons for shows in production
                                keyboard.append([
                                    InlineKeyboardButton(f"1080p", callback_data=f"create_rule_tv_{tv_id}_1080p"),
                                    InlineKeyboardButton(f"2160p", callback_data=f"create_rule_tv_{tv_id}_2160p")
                                ])
                                
                                # Store detailed data for rule creation
                                shows_in_production.append({
                                    'id': tv_id,
                                    'data': detailed
                                })
                                
                                # Limit to 5 shows in production
                                if len(shows_in_production) >= 5:
                                    break
                
                if not shows_in_production:
                    text += "❌ **No shows in production found**\n"
                    text += "Only shows currently in production can have auto-download rules created.\n"
                    text += "Try searching for a different show or check back later."
                
                keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="future_tv_shows")])
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
                
                # Store the shows in production data for rule creation
                context.user_data['shows_in_production'] = shows_in_production
            
            # Clear the future search type
            context.user_data.pop('future_search_type', None)
            
        except Exception as e:
            logger.error(f"[FUTURE_SEARCH_ERROR] User {user_id} (@{username}) - Error during future search: {e}")
            await update.message.reply_text(f"❌ Error during search: {str(e)}")
    
    async def _display_search_results(self, message, results, page, context=None):
        """Display search results with pagination."""
        torrents = results['torrents']
        total_pages = results['total_pages']
        current_page = results['current_page']
        
        if not torrents:
            # Handle both CallbackQuery and regular message objects
            if hasattr(message, 'edit_message_text'):
                await message.edit_message_text("No results found.")
            else:
                await message.reply_text("No results found.")
            return
            
        # Create result text
        result_text = f"🔍 Search Results (Page {current_page + 1}/{total_pages})\n\n"
        for i, torrent in enumerate(torrents):
            result_text += f"**{i + 1}. {torrent['name']}**\n"
            result_text += f"📁 Size: {torrent['size']}\n"
            result_text += f"⬆️ Seeders: {torrent['seeders']} | ⬇️ Leechers: {torrent['leechers']}\n"
            if torrent.get('year'):
                result_text += f"📅 Year: {torrent['year']}\n"
            if torrent.get('quality'):
                result_text += f"🎬 Quality: {torrent['quality']}\n"
            if torrent.get('resolution'):
                result_text += f"📺 Resolution: {torrent['resolution']}\n"
            result_text += f"🆓 Freeleech: {'Yes' if torrent['freeleech'] else 'No'}\n\n"
        # Create keyboard
        keyboard = []
        for i, torrent in enumerate(torrents):
            short_id = f"{current_page}_{i}"
            if context is not None:
                context.user_data[f"result_{short_id}"] = torrent
            keyboard.append([
                InlineKeyboardButton(
                    f"📥 Download {i + 1}", 
                    callback_data=f"download_{short_id}"
                )
            ])
        nav_buttons = []
        if current_page > 0:
            nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"page_{current_page - 1}"))
        if current_page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"page_{current_page + 1}"))
        if nav_buttons:
            keyboard.append(nav_buttons)
        keyboard.append([InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Use edit_message_text if it's a callback query, otherwise reply_text
        if hasattr(message, 'edit_message_text'):
            await message.edit_message_text(result_text, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await message.reply_text(result_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def _handle_search_results(self, query, data, context=None):
        """Handle search result pagination."""
        # Handle both page_ and search_results_ formats
        if data.startswith("page_"):
            page = int(data.split("_")[1])
        elif data.startswith("search_results_"):
            page = int(data.split("_")[2])
        else:
            page = 0
            
        user_id = query.from_user.id
        
        # Get stored search data
        user_data = context.user_data if context is not None else query.get_bot().application.context_types.context.user_data
        
        search_query = user_data.get('search_query')
        search_type = user_data.get('search_type')
        
        if not search_query or not search_type:
            await query.edit_message_text("Search session expired. Please search again.")
            return
        
        # Perform search for the requested page
        if search_type == 'movies':
            results = self.prowlarr_client.search_movies(search_query, page=page)
        elif search_type == 'tv_episodes':
            results = self.prowlarr_client.search_tv_episodes(search_query, page=page)
        elif search_type == 'tv_boxsets':
            results = self.prowlarr_client.search_tv_boxsets(search_query, page=page)
        else:
            results = self.prowlarr_client.search_movies(search_query, page=page)
        
        user_data['search_results'] = results
        
        await self._display_search_results(query, results, page, context)
    
    async def _handle_download_selection(self, query, data, context=None):
        """Handle torrent download selection with confirmation."""
        short_id = data.split("_", 1)[1]
        if context is not None:
            torrent = context.user_data.get(f"result_{short_id}")
        else:
            torrent = None
        if not torrent:
            await query.edit_message_text("❌ Could not find the selected torrent.")
            return
        
        # Show confirmation prompt
        summary = (
            f"**Title:** {torrent['name']}\n"
            f"**Size:** {torrent['size']}\n"
            f"**Seeders:** {torrent['seeders']}\n"
            f"**Leechers:** {torrent['leechers']}\n"
            f"**Freeleech:** {'Yes' if torrent['freeleech'] else 'No'}\n\n"
            f"Do you want to download this torrent?"
        )
        keyboard = [
            [
                InlineKeyboardButton("✅ Yes", callback_data=f"confirm_download_{short_id}"),
                InlineKeyboardButton("❌ No", callback_data="cancel_download")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(summary, reply_markup=reply_markup, parse_mode='Markdown')

    async def _handle_confirm_download(self, query, data, context=None):
        """Handle confirmation and add the torrent if not duplicate."""
        short_id = data.split("_", 2)[2]
        if context is not None:
            torrent = context.user_data.get(f"result_{short_id}")
        else:
            torrent = None
        if not torrent:
            await query.edit_message_text("❌ Could not find the selected torrent.")
            return
        magnet_link = torrent.get('magnet_link') or torrent.get('download_url')
        if not magnet_link:
            await query.edit_message_text("❌ Failed to get magnet link for this torrent.")
            return
        search_type = context.user_data.get('search_type', 'movies') if context is not None else 'movies'
        
        # Determine content type and extract year for movies
        content_type = 'movie' if search_type == 'movies' else 'tv'
        year = None
        if content_type == 'movie' and torrent.get('year'):
            year = torrent['year']
        
        download_path = self.qbittorrent_client.get_download_path(
            content_type,
            torrent['name'],
            year=year
        )
        # Add to qBittorrent
        torrent_hash = self.qbittorrent_client.add_magnet_link(
            magnet_link, 
            download_path,
            category=search_type
        )
        if not torrent_hash:
            await query.edit_message_text("❌ Failed to add torrent to qBittorrent.")
            return
        download_id = self.database.add_download(
            query.from_user.id,
            torrent['name'],
            torrent['id'],
            magnet_link,
            download_path
        )
        if context is not None:
            context.user_data[f'torrent_{download_id}'] = torrent_hash
        await query.edit_message_text(
            f"✅ **Download Started!**\n\n"
            f"📁 **Title:** {torrent['name']}\n"
            f"📂 **Path:** {download_path}\n"
            f"🆔 **Download ID:** {download_id}\n\n"
            f"You'll be notified when the download completes!",
            parse_mode='Markdown'
        )
    
    async def _show_downloads(self, update, context):
        """Show user's downloads."""
        user_id = update.effective_user.id if hasattr(update, 'effective_user') else update.from_user.id
        
        # Get downloads from last 24 hours and statistics
        downloads = self.database.get_user_downloads(user_id, hours=24)
        stats = self.database.get_download_statistics(user_id, hours=24)
        
        if not downloads:
            text = "📥 **Your Downloads (Last 24 Hours)**\n\n"
            text += "❌ No downloads in the last 24 hours.\n\n"
            text += f"📊 **Statistics:**\n"
            text += f"• Total Downloads: {stats['total_downloads']}\n"
            text += f"• Completed: {stats['completed_downloads']}\n"
            text += f"• In Progress: {stats['downloading_count']}\n"
        else:
            text = "📥 **Your Downloads (Last 24 Hours)**\n\n"
            text += f"📊 **Statistics:**\n"
            text += f"• Total Downloads: {stats['total_downloads']}\n"
            text += f"• Completed: {stats['completed_downloads']}\n"
            text += f"• In Progress: {stats['downloading_count']}\n\n"
            text += "📋 **Recent Downloads:**\n\n"
            
            for download in downloads[:10]:  # Show last 10 downloads
                status_emoji = "✅" if download[3] == 'completed' else "⏳"
                text += f"{status_emoji} **{download[1]}**\n"
                text += f"📊 Status: {download[3]}\n"
                text += f"📅 Added: {download[4]}\n\n"
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if hasattr(update, 'edit_message_text'):
            await update.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await update.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    

    
    async def _show_main_menu(self, query):
        """Show main menu."""
        keyboard = [
            [InlineKeyboardButton("🎬 Search Movies", callback_data="search_movies")],
            [InlineKeyboardButton("📺 Search TV Show Episodes", callback_data="search_tv_episodes")],
            [InlineKeyboardButton("📦 Search TV Show Boxsets", callback_data="search_tv_boxsets")],
            [InlineKeyboardButton("🔮 Future Downloads", callback_data="future_downloads")],
            [InlineKeyboardButton("📥 My Downloads", callback_data="my_downloads")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🎬 Welcome to Torrent Downloader Bot!\n\n"
            "What would you like to do?",
            reply_markup=reply_markup
        )
    
    def _is_authorized_user(self, user_id: int) -> bool:
        """Check if user is authorized."""
        is_authorized = user_id in self.settings.AUTHORIZED_USERS
        logger.debug(f"[AUTH_CHECK] User {user_id} authorization: {is_authorized} (Authorized users: {self.settings.AUTHORIZED_USERS})")
        return is_authorized
    
    def _format_speed(self, speed_bytes: int) -> str:
        """Format speed in bytes to human readable format."""
        if speed_bytes == 0:
            return "0 B/s"
        
        size_names = ["B/s", "KB/s", "MB/s", "GB/s"]
        i = 0
        while speed_bytes >= 1024 and i < len(size_names) - 1:
            speed_bytes /= 1024.0
            i += 1
        
        return f"{speed_bytes:.1f} {size_names[i]}"
    
    async def check_completed_downloads(self):
        """Check for completed downloads and notify users."""
        import time
        while True:
            try:
                logger.info("[Checker] Checking for completed downloads...")
                # Get all downloads from database (last 24 hours only)
                all_downloads = []
                for user_id in self.settings.AUTHORIZED_USERS:
                    downloads = self.database.get_user_downloads(user_id, hours=24)
                    all_downloads.extend([(user_id, download) for download in downloads])
                # Check each download
                for user_id, download in all_downloads:
                    download_id = download[0]
                    title = download[1]
                    torrent_id = download[2]
                    status = download[3]
                    # Get the torrent hash from user_data if available
                    torrent_hash = None
                    for k, v in self.application.bot_data.items():
                        if k.startswith('torrent_') and str(download_id) in k:
                            torrent_hash = v
                            break
                    if not torrent_hash:
                        # Try to get hash from qBittorrent using improved search method
                        # Get the magnet link from the database if available
                        magnet_link = None
                        try:
                            # Try to get magnet link from database
                            download_details = self.database.get_download_by_id(download_id)
                            if download_details and len(download_details) > 4:
                                magnet_link = download_details[4]  # magnet_link field
                        except Exception as e:
                            logger.debug(f"Could not get magnet link from database: {e}")
                        
                        torrent_info = self.qbittorrent_client.find_torrent_by_name(title, magnet_link=magnet_link)
                        if torrent_info:
                            torrent_hash = torrent_info['hash']
                    if not torrent_hash:
                        logger.info(f"[Checker] No hash found for download {download_id} ({title})")
                        continue
                    if status == 'downloading':
                        # Check if torrent is completed
                        is_completed = self.qbittorrent_client.is_torrent_completed(torrent_hash)
                        logger.info(f"[Checker] Download {download_id} ({title}) hash={torrent_hash} completed={is_completed}")
                        if is_completed:
                            # Update database
                            self.database.update_download_status(download_id, 'completed')
                            # Send notification
                            await self._send_completion_notification(user_id, title)
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error checking completed downloads: {e}")
                time.sleep(60)
    
    async def _send_completion_notification(self, user_id: int, title: str):
        """Send download completion notification."""
        try:
            await self.application.bot.send_message(
                chat_id=user_id,
                text=f"✅ **Download Completed!**\n\n"
                     f"📁 **Title:** {title}\n"
                     f"🎉 Your download has finished successfully!",
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error sending completion notification: {e}")
    
    async def _handle_future_downloads(self, query, data=None, context=None):
        """Handle future downloads feature."""
        if data == "future_downloads" or data is None:
            # Show future downloads menu
            keyboard = [
                [InlineKeyboardButton("🎬 Future Movies", callback_data="future_movies")],
                [InlineKeyboardButton("📺 Future TV Shows", callback_data="future_tv_shows")],
                [InlineKeyboardButton("📋 My Auto-Download Rules", callback_data="future_rules")],
                [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "🔮 **Future Downloads**\n\n"
                "Set up automatic downloads for upcoming movies and TV shows!\n\n"
                "Choose an option:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        elif data == "future_movies":
            await self._handle_future_movies(query, context)
        elif data == "future_tv_shows":
            await self._handle_future_tv_shows(query, context)
        elif data == "future_rules":
            await self._show_auto_download_rules(query, context)
        elif data == "future_search_movie":
            await self._handle_future_search_movie(query, context)
        elif data == "future_search_tv":
            await self._handle_future_search_tv(query, context)
        elif data == "future_upcoming_movies":
            await self._handle_future_upcoming_movies(query, context)
        elif data.startswith("create_rule_"):
            await self._handle_create_rule(query, data, context)
    
    async def _handle_future_movies(self, query, context):
        """Handle future movies search."""
        keyboard = [
            [InlineKeyboardButton("🔍 Search Movie", callback_data="future_search_movie")],
            [InlineKeyboardButton("📅 Upcoming Movies", callback_data="future_upcoming_movies")],
            [InlineKeyboardButton("🔙 Back", callback_data="future_downloads")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🎬 **Future Movies**\n\n"
            "Search for movies and set up auto-download rules for when they become available.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def _handle_future_tv_shows(self, query, context):
        """Handle future TV shows search."""
        keyboard = [
            [InlineKeyboardButton("🔍 Search TV Show", callback_data="future_search_tv")],
            [InlineKeyboardButton("🔙 Back", callback_data="future_downloads")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "📺 **Future TV Shows**\n\n"
            "Search for TV shows and set up auto-download rules for new episodes.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def _show_auto_download_rules(self, query, context):
        """Show current auto-download rules."""
        try:
            rules = self.qbittorrent_client.get_auto_download_rules()
            
            if not rules:
                text = "📋 **Auto-Download Rules**\n\nNo rules configured yet."
            else:
                text = "📋 **Auto-Download Rules**\n\n"
                
                # Convert rules to list if it's not already, and handle slicing safely
                if isinstance(rules, (list, tuple)):
                    rules_to_show = rules[:10]  # Show first 10 rules
                else:
                    # If rules is not a list/tuple, try to convert it
                    try:
                        rules_list = list(rules) if hasattr(rules, '__iter__') else [rules]
                        rules_to_show = rules_list[:10]
                    except Exception as convert_error:
                        logger.warning(f"Could not convert rules to list: {convert_error}")
                        rules_to_show = [rules] if rules else []
                
                # Process each rule safely
                for i, rule in enumerate(rules_to_show):
                    try:
                        if isinstance(rule, dict):
                            rule_name = rule.get('ruleName', rule.get('name', f'Rule {i+1}'))
                            enabled = "✅" if rule.get('enabled', False) else "❌"
                        elif hasattr(rule, 'ruleName'):
                            rule_name = rule.ruleName
                            enabled = "✅" if getattr(rule, 'enabled', False) else "❌"
                        elif hasattr(rule, 'name'):
                            rule_name = rule.name
                            enabled = "✅" if getattr(rule, 'enabled', False) else "❌"
                        else:
                            rule_name = str(rule)
                            enabled = "❓"
                        
                        # Clean up the rule name for better display
                        clean_rule_name = rule_name.replace('Auto', '').replace('_', ' ').strip()
                        
                        # Extract quality, season, and other metadata
                        quality = None
                        season = None
                        is_upcoming = False
                        
                        # Check for quality
                        if '1080p' in clean_rule_name:
                            quality = '1080p'
                            clean_rule_name = clean_rule_name.replace('1080p', '').strip()
                        elif '2160p' in clean_rule_name:
                            quality = '2160p'
                            clean_rule_name = clean_rule_name.replace('2160p', '').strip()
                        
                        # Check for season
                        season_match = re.search(r'S(\d+)', clean_rule_name)
                        if season_match:
                            season = season_match.group(1)
                            clean_rule_name = clean_rule_name.replace(f'S{season}', '').strip()
                        
                        # Check if it's an upcoming movie
                        if 'Upcoming' in clean_rule_name:
                            is_upcoming = True
                            clean_rule_name = clean_rule_name.replace('Upcoming', '').strip()
                        
                        # Clean up any remaining artifacts
                        clean_rule_name = clean_rule_name.replace('  ', ' ').strip()
                        
                        # Determine content type and add appropriate emoji
                        content_emoji = "🎬"  # Default to movie
                        content_info = ""
                        
                        # Check if it's a TV show (has season info or common TV show indicators)
                        if season or any(tv_indicator in clean_rule_name.lower() for tv_indicator in ['guy', 'park', 'sunny', 'farm', 'morty']):
                            content_emoji = "📺"
                            if season:
                                content_info = f" (Season {season})"
                        elif is_upcoming:
                            content_info = " (Upcoming)"
                        
                        # Build the display text
                        display_text = f"{content_emoji} **{clean_rule_name}**"
                        if quality:
                            display_text += f" - {quality}"
                        if content_info:
                            display_text += content_info
                        
                        # Add proper spacing and formatting
                        text += f"{enabled} {display_text}\n\n"
                    except Exception as rule_error:
                        logger.warning(f"Error processing rule {i}: {rule_error}")
                        text += f"❓ **Rule {i+1}** (Error processing)\n\n"
            
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="future_downloads")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error showing auto-download rules: {e}")
            await query.edit_message_text("❌ Error loading auto-download rules.")
    
    async def _handle_create_rule(self, query, data, context):
        """Handle creating auto-download rules."""
        try:
            # Parse rule data from callback
            parts = data.split("_")
            content_type = parts[2]  # movie or tv
            content_id = parts[3]
            quality = parts[4] if len(parts) > 4 else "1080p"
            
            if content_type == "movie":
                movie_data = self.tmdb_client.get_movie_details(int(content_id))
                if movie_data:
                    title = movie_data.get('title', 'Unknown')
                    year = movie_data.get('release_date', '')[:4] if movie_data.get('release_date') else None
                    
                    # Check if ANY rule already exists for this movie title (regardless of quality)
                    logger.info(f"[MOVIE_RULE_CHECK] Checking if ANY rule exists for movie: '{title}'")
                    
                    if self.qbittorrent_client.rule_exists_by_title(title):
                        logger.info(f"[MOVIE_RULE_CHECK] ✅ Rule already exists for movie: '{title}'")
                        
                        # Get existing rule details
                        existing_rule = self.qbittorrent_client.get_rule_by_title(title)
                        existing_rule_name = "Unknown"
                        if existing_rule:
                            if hasattr(existing_rule, 'name'):
                                existing_rule_name = existing_rule.name
                            elif hasattr(existing_rule, 'ruleName'):
                                existing_rule_name = existing_rule.ruleName
                            elif isinstance(existing_rule, dict):
                                existing_rule_name = existing_rule.get('name') or existing_rule.get('ruleName')
                        
                        # Offer to replace the existing rule
                        keyboard = [
                            [InlineKeyboardButton("🔄 Replace Existing Rule", callback_data=f"replace_rule_movie_{content_id}_{quality}")],
                            [InlineKeyboardButton("❌ Cancel", callback_data="future_movies")]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        
                        await query.edit_message_text(
                            f"⚠️ **Rule Already Exists!**\n\n"
                            f"🎬 **Movie:** {title}\n"
                            f"📋 **Existing Rule:** {existing_rule_name}\n"
                            f"ℹ️ An auto-download rule for this movie already exists.\n\n"
                            f"Would you like to replace the existing rule?",
                            reply_markup=reply_markup,
                            parse_mode='Markdown'
                        )
                        return
                    else:
                        logger.info(f"[MOVIE_RULE_CHECK] ❌ No rule exists for movie: '{title}'")
                    
                    # Use upcoming movie rule for movies that are not yet released
                    if self.tmdb_client.is_upcoming_movie(movie_data):
                        success = self.qbittorrent_client.create_upcoming_movie_rule(title, quality, movie_data=movie_data)
                    else:
                        success = self.qbittorrent_client.create_movie_rule(title, quality, movie_data=movie_data)
                    
                    if success:
                        # Show different message for upcoming movies
                        if self.tmdb_client.is_upcoming_movie(movie_data):
                            status_text = "Will auto-download when released (ignores duplicates for 365 days)"
                        else:
                            status_text = "Will auto-download when available"
                        
                        await query.edit_message_text(
                            f"✅ **Auto-Download Rule Created!**\n\n"
                            f"🎬 **Movie:** {title}\n"
                            f"📺 **Quality:** {quality}\n"
                            f"🔮 **Status:** {status_text}",
                            parse_mode='Markdown'
                        )
                    else:
                        await query.edit_message_text("❌ Failed to create auto-download rule.")
                else:
                    await query.edit_message_text("❌ Could not find movie details.")
            
            elif content_type == "tv":
                # Use the shows_in_production data stored in context.user_data
                shows_in_production = context.user_data.get('shows_in_production')
                if not shows_in_production:
                    await query.edit_message_text("❌ No TV show details found for this search. Please try again.")
                    return
                
                found_show = None
                for show_info in shows_in_production:
                    if show_info['id'] == int(content_id):
                        found_show = show_info['data']
                        break
                
                if found_show:
                    title = found_show.get('name', 'Unknown')
                    status = self.tmdb_client.get_tv_show_status(found_show)
                    
                    # Check if ANY rule already exists for this TV show title (regardless of quality or season)
                    logger.info(f"[TV_RULE_CHECK] Checking if ANY rule exists for TV show: '{title}'")
                    
                    if self.qbittorrent_client.rule_exists_by_title(title):
                        logger.info(f"[TV_RULE_CHECK] ✅ Rule already exists for TV show: '{title}'")
                        
                        # Get existing rule details
                        existing_rule = self.qbittorrent_client.get_rule_by_title(title)
                        existing_rule_name = "Unknown"
                        if existing_rule:
                            if hasattr(existing_rule, 'name'):
                                existing_rule_name = existing_rule.name
                            elif hasattr(existing_rule, 'ruleName'):
                                existing_rule_name = existing_rule.ruleName
                            elif isinstance(existing_rule, dict):
                                existing_rule_name = existing_rule.get('name') or existing_rule.get('ruleName')
                        
                        # Offer to replace the existing rule
                        keyboard = [
                            [InlineKeyboardButton("🔄 Replace Existing Rule", callback_data=f"replace_rule_tv_{content_id}_{quality}")],
                            [InlineKeyboardButton("❌ Cancel", callback_data="future_tv_shows")]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        
                        await query.edit_message_text(
                            f"⚠️ **Rule Already Exists!**\n\n"
                            f"📺 **TV Show:** {title}\n"
                            f"📋 **Existing Rule:** {existing_rule_name}\n"
                            f"ℹ️ An auto-download rule for this TV show already exists.\n\n"
                            f"Would you like to replace the existing rule?",
                            reply_markup=reply_markup,
                            parse_mode='Markdown'
                        )
                        return
                    else:
                        logger.info(f"[TV_RULE_CHECK] ❌ No rule exists for TV show: '{title}'")
                    
                    # Ask user for season number directly
                    context.user_data['pending_tv_rule'] = {
                        'title': title,
                        'quality': quality,
                        'tv_data': found_show,
                        'content_id': content_id
                    }
                    
                    await query.edit_message_text(
                        f"📺 **Create Auto-Download Rule for {title}**\n\n"
                        f"🔮 **Status:** {status}\n"
                        f"📺 **Quality:** {quality}\n\n"
                        f"Enter the season number you want to auto-download:",
                        parse_mode='Markdown'
                    )
                    
                    # Set up message handler for season input
                    context.user_data['waiting_for_season'] = True
                else:
                    await query.edit_message_text("❌ Could not find TV show details.")
            
        except Exception as e:
            logger.error(f"Error creating rule: {e}")
            await query.edit_message_text("❌ Error creating auto-download rule.")
    

    
    async def _handle_season_input(self, update, context):
        """Handle season number input for TV rule creation."""
        try:
            season_text = update.message.text.strip()
            
            # Validate season input
            if not season_text.isdigit():
                await update.message.reply_text(
                    "❌ Please enter a valid season number (e.g., 1, 2, 3):"
                )
                return
            
            season = int(season_text)
            if season < 1:
                await update.message.reply_text(
                    "❌ Season number must be 1 or higher. Please try again:"
                )
                return
            
            pending_rule = context.user_data.get('pending_tv_rule')
            if not pending_rule:
                await update.message.reply_text("❌ No pending TV rule found. Please try again.")
                return
            
            title = pending_rule['title']
            quality = pending_rule['quality']
            tv_data = pending_rule['tv_data']
            
            # Create the rule with specific season
            success = self.qbittorrent_client.create_tv_show_rule(
                title, quality, tv_data=tv_data, season=str(season)
            )
            
            if success:
                await update.message.reply_text(
                    f"✅ **Auto-Download Rule Created!**\n\n"
                    f"📺 **TV Show:** {title}\n"
                    f"📺 **Season:** {season}\n"
                    f"📺 **Quality:** {quality}\n"
                    f"🔮 **Action:** Will auto-download Season {season} episodes",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text("❌ Failed to create auto-download rule.")
            
            # Clean up pending rule and season input flag
            context.user_data.pop('pending_tv_rule', None)
            context.user_data.pop('waiting_for_season', None)
            
        except Exception as e:
            logger.error(f"Error handling season input: {e}")
            await update.message.reply_text("❌ Error creating TV rule. Please try again.")
            # Clean up on error
            context.user_data.pop('pending_tv_rule', None)
            context.user_data.pop('waiting_for_season', None)
    
    async def _handle_future_search_movie(self, query, context):
        """Handle future movie search."""
        await query.edit_message_text(
            "🔍 **Search for a Movie**\n\n"
            "Enter the name of the movie you want to set up auto-download for:",
            parse_mode='Markdown'
        )
        # Store the search type for the next message
        context.user_data['future_search_type'] = 'movie'
    
    async def _handle_future_search_tv(self, query, context):
        """Handle future TV show search."""
        await query.edit_message_text(
            "🔍 **Search for a TV Show**\n\n"
            "Enter the name of the TV show you want to set up auto-download for:",
            parse_mode='Markdown'
        )
        # Store the search type for the next message
        context.user_data['future_search_type'] = 'tv'
    
    async def _handle_future_upcoming_movies(self, query, context):
        """Handle upcoming movies display."""
        try:
            upcoming_movies = self.tmdb_client.get_upcoming_movies(30)  # Next 30 days
            
            if not upcoming_movies:
                await query.edit_message_text(
                    "📅 **Upcoming Movies**\n\n"
                    "No upcoming movies found in the next 30 days.",
                    parse_mode='Markdown'
                )
                return
            
            text = "📅 **Upcoming Movies (Next 30 Days)**\n\n"
            keyboard = []
            
            # Filter movies to only show those released within the last 2 months
            filtered_upcoming = [movie for movie in upcoming_movies if self.tmdb_client.is_recently_released_movie(movie, days_threshold=60)]
            
            if not filtered_upcoming:
                text += "❌ **No recently released movies found**\n"
                text += "Only movies released within the last 2 months are shown.\n"
                text += "Try searching for a different movie or check back later."
            else:
                for i, movie in enumerate(filtered_upcoming[:10]):  # Show first 10 filtered results
                    title = movie.get('title', 'Unknown')
                    release_date = movie.get('release_date', 'Unknown')
                    movie_id = movie.get('id')
                    is_upcoming = self.tmdb_client.is_upcoming_movie(movie)
                    
                    text += f"🎬 **{title}**\n"
                    text += f"📅 Release: {release_date}\n"
                    text += f"🔮 Status: {'🟡 Upcoming' if is_upcoming else '🟢 Released'}\n\n"
                    
                    # Add quality selection buttons for filtered upcoming movies
                    keyboard.append([
                        InlineKeyboardButton(f"1080p", callback_data=f"create_rule_movie_{movie_id}_1080p"),
                        InlineKeyboardButton(f"2160p", callback_data=f"create_rule_movie_{movie_id}_2160p")
                    ])
            
            keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="future_movies")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error getting upcoming movies: {e}")
            await query.edit_message_text("❌ Error loading upcoming movies.")
     
    async def _handle_replace_rule(self, query, data, context):
        """Handle replacing existing auto-download rules."""
        try:
            # Parse rule data from callback
            parts = data.split("_")
            content_type = parts[2]  # movie or tv
            content_id = parts[3]
            quality = parts[4] if len(parts) > 4 else "1080p"
            
            if content_type == "movie":
                movie_data = self.tmdb_client.get_movie_details(int(content_id))
                if movie_data:
                    title = movie_data.get('title', 'Unknown')
                    
                    # Delete existing rule
                    if self.qbittorrent_client.delete_rule_by_title(title):
                        logger.info(f"[REPLACE_RULE] Deleted existing rule for movie: '{title}'")
                        
                        # Create new rule
                        # Use upcoming movie rule for movies that are not yet released
                        if self.tmdb_client.is_upcoming_movie(movie_data):
                            success = self.qbittorrent_client.create_upcoming_movie_rule(title, quality, movie_data=movie_data)
                        else:
                            success = self.qbittorrent_client.create_movie_rule(title, quality, movie_data=movie_data)
                        
                        if success:
                            # Show different message for upcoming movies
                            if self.tmdb_client.is_upcoming_movie(movie_data):
                                status_text = "Replaced existing rule (ignores duplicates for 365 days)"
                            else:
                                status_text = "Replaced existing rule with new one"
                            
                            await query.edit_message_text(
                                f"✅ **Auto-Download Rule Replaced!**\n\n"
                                f"🎬 **Movie:** {title}\n"
                                f"📺 **Quality:** {quality}\n"
                                f"🔄 **Action:** {status_text}",
                                parse_mode='Markdown'
                            )
                        else:
                            await query.edit_message_text("❌ Failed to create new auto-download rule.")
                    else:
                        await query.edit_message_text("❌ Failed to delete existing rule.")
                else:
                    await query.edit_message_text("❌ Could not find movie details.")
            
            elif content_type == "tv":
                # Use the shows_in_production data stored in context.user_data
                shows_in_production = context.user_data.get('shows_in_production')
                if not shows_in_production:
                    await query.edit_message_text("❌ No TV show details found for this search. Please try again.")
                    return
                
                found_show = None
                for show_info in shows_in_production:
                    if show_info['id'] == int(content_id):
                        found_show = show_info['data']
                        break
                
                if found_show:
                    title = found_show.get('name', 'Unknown')
                    
                    # Delete existing rule
                    if self.qbittorrent_client.delete_rule_by_title(title):
                        logger.info(f"[REPLACE_RULE] Deleted existing rule for TV show: '{title}'")
                        
                        # Ask user for season number directly
                        context.user_data['pending_tv_rule'] = {
                            'title': title,
                            'quality': quality,
                            'tv_data': found_show,
                            'content_id': content_id
                        }
                        
                        await query.edit_message_text(
                            f"📺 **Replace Auto-Download Rule for {title}**\n\n"
                            f"📺 **Quality:** {quality}\n"
                            f"🔄 **Action:** Replaced existing rule\n\n"
                            f"Enter the season number you want to auto-download:",
                            parse_mode='Markdown'
                        )
                        
                        # Set up message handler for season input
                        context.user_data['waiting_for_season'] = True
                    else:
                        await query.edit_message_text("❌ Failed to delete existing rule.")
                else:
                    await query.edit_message_text("❌ Could not find TV show details.")
            
        except Exception as e:
            logger.error(f"Error replacing rule: {e}")
            await query.edit_message_text("❌ Error replacing auto-download rule.")
    
    async def _automatic_cleanup_task(self):
        """Automatic database cleanup task that runs every 24 hours."""
        import time
        while True:
            try:
                logger.info("[AUTO_CLEANUP] Starting automatic database cleanup...")
                
                # Clean up downloads older than 24 hours
                deleted_count = self.database.cleanup_old_downloads(hours=24)
                
                if deleted_count > 0:
                    logger.info(f"[AUTO_CLEANUP] Cleaned up {deleted_count} old downloads")
                else:
                    logger.info("[AUTO_CLEANUP] No old downloads to clean up")
                
                # Wait 24 hours before next cleanup
                await asyncio.sleep(24 * 60 * 60)  # 24 hours in seconds
                
            except Exception as e:
                logger.error(f"[AUTO_CLEANUP] Error during automatic cleanup: {e}")
                # Wait 1 hour before retrying on error
                await asyncio.sleep(60 * 60)  # 1 hour in seconds
    
    def run(self):
        """Start the bot."""
        logger.info("Starting Telegram bot...")
        import threading
        import time
        
        # Start the completion checker in a background thread
        threading.Thread(target=lambda: asyncio.run(self.check_completed_downloads()), daemon=True).start()
        
        # Start the automatic cleanup task in a background thread
        threading.Thread(target=lambda: asyncio.run(self._automatic_cleanup_task()), daemon=True).start()
        
        # Start the bot with error handling and retry logic
        max_retries = 5
        retry_delay = 30  # seconds
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Starting bot (attempt {attempt + 1}/{max_retries})")
                self.application.run_polling(
                    allowed_updates=Update.ALL_TYPES,
                    drop_pending_updates=True,
                    close_loop=False
                )
                break  # If we get here, the bot ran successfully
                
            except Exception as e:
                logger.error(f"Bot crashed on attempt {attempt + 1}: {e}")
                
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error("Max retries reached. Bot failed to start.")
                    raise 