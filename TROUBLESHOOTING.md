# Troubleshooting User Access Issues

## Problem
Only one user can search for movies and TV shows, while other users cannot access the bot features.

## Solution Steps

### 1. Check Authorization Setup
Run the authorization test script:
```bash
python test_authorization.py
```

This will show:
- ✅ Environment variables are set correctly
- ✅ Authorized users are parsed correctly
- ✅ Settings are loaded properly

### 2. Enhanced Logging
The bot now has comprehensive logging to track user requests:

**New Log Features:**
- User ID and username logging for all requests
- Authorization check logging
- Session state tracking
- Search query logging
- Error tracking with user context

**Log Files:**
- `bot.log` - Detailed bot logs
- Console output - Real-time logs

### 3. Debug Command
Users can now use `/debug` command in the bot to get:
- Their user ID
- Authorization status
- Bot configuration status
- Session data

### 4. Common Issues and Fixes

#### Issue: User not in AUTHORIZED_USERS
**Symptoms:**
- User gets "You are not authorized" message
- Log shows: `[AUTH] User X is NOT authorized`

**Fix:**
1. Get user's Telegram ID from @userinfobot
2. Add to `.env` file: `AUTHORIZED_USERS=123456789,987654321`
3. Restart the bot

#### Issue: Session Problems
**Symptoms:**
- User can't search after selecting search type
- Log shows: `[SESSION] User has no active session`

**Fix:**
- The bot now automatically creates sessions when users start
- Use `/start` command to reset session

#### Issue: Environment Variable Problems
**Symptoms:**
- No authorized users found
- Bot only works for owner

**Fix:**
1. Check `.env` file exists in project root
2. Ensure `AUTHORIZED_USERS` is set correctly
3. Format: `AUTHORIZED_USERS=123456789,987654321`
4. No spaces around commas

### 5. Testing Steps

1. **Run Authorization Test:**
   ```bash
   python test_authorization.py
   ```

2. **Start Bot with Logging:**
   ```bash
   python test_bot_logging.py
   ```

3. **Test User Access:**
   - Have each user send `/start` to the bot
   - Check logs for authorization messages
   - Use `/debug` command to verify user ID

4. **Monitor Logs:**
   - Watch `bot.log` for detailed activity
   - Look for `[AUTH]` messages
   - Check for `[SESSION]` messages

### 6. Log Examples

**Successful Authorization:**
```
[START] User 5142004715 (@username) requested /start command
[AUTH] User 5142004715 (@username) is authorized
[DB] Created session for user 5142004715 with state: idle
```

**Failed Authorization:**
```
[START] User 123456789 (@username) requested /start command
[AUTH] User 123456789 (@username) is NOT authorized. Authorized users: [5142004715, 7810026064]
```

**Search Request:**
```
[SEARCH_TYPE] User 5142004715 (@username) selected search type: movies
[DB] Updated session for user 5142004715: state=waiting_for_search_query, query=None, page=0
[SEARCH_QUERY] User 5142004715 (@username) searching for 'Avengers' with type 'movies'
[SEARCH_RESULTS] User 5142004715 (@username) - Found 8 results for 'Avengers'
```

### 7. Quick Fix Checklist

- [ ] `.env` file exists in project root
- [ ] `AUTHORIZED_USERS` is set in `.env`
- [ ] User IDs are correct (get from @userinfobot)
- [ ] No spaces in `AUTHORIZED_USERS` value
- [ ] Bot restarted after changing `.env`
- [ ] Users use `/start` command first
- [ ] Check logs for authorization messages

### 8. Support Commands

**For Users:**
- `/start` - Initialize bot session
- `/debug` - Get user info and bot status
- `/help` - Show help information

**For Administrators:**
- Check `bot.log` for detailed activity
- Run `python test_authorization.py` to verify setup
- Monitor authorization logs for failed attempts

## Current Configuration
Based on the test results:
- ✅ 2 authorized users configured: `[5142004715, 7810026064]`
- ✅ All environment variables set correctly
- ✅ Enhanced logging implemented
- ✅ Debug command available

If users are still having issues, the enhanced logging will help identify the exact problem. 