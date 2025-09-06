# VetSupport AI Bot - Deployment Guide

## 📋 Prerequisites

#1. **Python 3.10+** installed
#2. **PostgreSQL** database or **Firebase** account
#3. **API Keys** for required services
#4. **Hosting platform** account (Render/Replit)

## 🔑 Required API Keys

### Essential Keys
#- **Telegram Bot Token** - Get from @BotFather
#- **Database URL** - PostgreSQL connection string or Firebase credentials

### AI Services (Choose at least one)
#- **Gemini API Key** - Google AI Studio
#- **OpenAI API Key** - OpenAI Platform
#- **Grok API Key** - X Developer Portal

### Voice Services (Optional)
#- **ElevenLabs API Key** - For premium voice synthesis
#- **Google TTS Key** - For text-to-speech
#- **Whisper API Key** - Usually same as OpenAI key

### Integrations (Optional)
#- **Helsi API Key** - Telemedicine integration
#- **Doctor Online API Key** - Alternative telemedicine
#- **Social Media Tokens** - For marketing automation

## 🚀 Deployment Options

### Option 1: Render Deployment (Recommended)

#1. **Create Render Account**
# - Go to [render.com](https://render.com)
# - Sign up for free account
# - Connect your GitHub account

#2. **Prepare Repository**
# - Push your code to GitHub repository
# - Ensure all files are committed including `render.yaml`

#3. **Create PostgreSQL Database**
# - In Render dashboard, click "New +"
# - Select "PostgreSQL"
# - Choose plan (Free tier available)
# - Note down the connection details

#4. **Deploy Web Service**
# - Click "New +" to "Web Service"
# - Connect your GitHub repository
# - Render will auto-detect Python and use `render.yaml`
# - Or manually configure:
# - **Name**: vetsupport-ai-bot
# - **Environment**: Python 3
# - **Build Command**: `pip install -r requirements.txt`
# - **Start Command**: `gunicorn bot:app -w 4 -k uvicorn.workers.UvicornWorker`

#5. **Configure Environment Variables**
# In Render dashboard, add these environment variables:
# ```bash
# BOT_TOKEN=your_telegram_bot_token
# DATABASE_URL=postgresql://user:pass@host:port/dbname
# GEMINI_API_KEY=your_gemini_key
# WEBHOOK_URL=[https://your-app-name.onrender.com](https://your-app-name.onrender.com)
# WEBHOOK_SECRET=your_secret_key
# HOST=0.0.0.0
# PORT=10000
# ```

#6. **Deploy**
# - Click "Create Web Service"
# - Render will automatically build and deploy
# - Monitor logs for any issues
# - Your bot will be available at `https://your-app-name.onrender.com`

### Option 2: Replit Deployment

#1. **Create New Repl**
# - Go to [replit.com](https://replit.com)
# - Click "Create Repl"
# - Choose "Import from GitHub" or upload files

#2. **Environment Variables**
# - Go to "Secrets" tab (lock icon)
# - Add all required environment variables:

# ```bash
# BOT_TOKEN=your_telegram_bot_token
# DATABASE_URL=postgresql://user:pass@host:port/dbname
# GEMINI_API_KEY=your_gemini_key
# OPENAI_API_KEY=your_openai_key
# WEBHOOK_URL=[https://yourrepl.replit.dev](https://yourrepl.replit.dev)
# WEBHOOK_SECRET=your_secret_key
# ```

#3. **Install Dependencies**
# ```bash
# pip install -r requirements.txt
# ```

#4. **Run Bot**
# ```bash
# python bot.py
# ```

### Option 3: Local Development

#1. **Clone Repository**
# ```bash
# git clone <repository-url>
# cd vetsupport-ai-bot
# ```

#2. **Create Virtual Environment**
# ```bash
# python -m venv venv
# source venv/bin/activate  # Linux/Mac
# # or
# venv\Scripts\activate  # Windows
# ```

#3. **Install Dependencies**
# ```bash
# pip install -r requirements.txt
# ```

#4. **Create .env File**
# ```env
# BOT_TOKEN=your_telegram_bot_token
# DATABASE_URL=postgresql://user:pass@localhost:5432/vetsupport
# GEMINI_API_KEY=your_gemini_key
# OPENAI_API_KEY=your_openai_key
# ```

#5. **Run Bot**
# ```bash
# python bot.py
# ```

## 🗄️ Database Setup

### PostgreSQL Setup

#1. **Create Database**
# ```sql
# CREATE DATABASE vetsupport;
# CREATE USER vetsupport_user WITH ENCRYPTED PASSWORD 'your_password';
# GRANT ALL PRIVILEGES ON DATABASE vetsupport TO vetsupport_user;
# ```

#2. **Connection String Format**
# ```
# postgresql://username:password@hostname:port/database_name
# ```

### Free Database Options

#1. **Render PostgreSQL** (Recommended for Render deployment)
# - Built-in PostgreSQL service
# - Free tier available
# - Automatic backups
# - Easy integration with web services

#1. **ElephantSQL** (Free PostgreSQL)
# - Go to [elephantsql.com](https://elephantsql.com)
# - Create free "Tiny Turtle" plan
# - Copy connection URL

#2. **Supabase** (Free PostgreSQL + additional features)
# - Go to [supabase.com](https://supabase.com)
# - Create new project
# - Get connection string from settings

#3. **Railway** (Free PostgreSQL)
# - Go to [railway.app](https://railway.app)
# - Create PostgreSQL service
# - Get connection URL

## 🔧 Configuration

### Basic Configuration

# Edit `config.py` with your settings:

# This section looks like actual Python code,
# so I'll leave the code lines uncommented.

# Bot Configuration
# BOT_TOKEN = "your_bot_token_here"
# WEBHOOK_URL = "https://your-app-name.onrender.com"  # For webhook mode
# WEBHOOK_SECRET = "your_webhook_secret"

# Database
# DATABASE_URL = "postgresql://user:pass@host:port/dbname"

# AI Services
# GEMINI_API_KEY = "your_gemini_key"
# OPENAI_API_KEY = "your_openai_key"

# Admin Settings
# ADMIN_CHAT_ID = "your_admin_user_id"

### Advanced Configuration

# For production deployment, consider:

#1. **Security Settings**
# - Use strong webhook secret
# - Enable rate limiting
# - Set up user verification

#2. **Performance Optimization**
# - Configure database connection pooling
# - Enable response caching
# - Set up CDN for media files

#3. **Monitoring & Logging**
# - Set up structured logging
# - Configure error tracking (Sentry)
# - Monitor bot performance

## 🔄 Webhook vs Polling

### Webhook Mode (Recommended for Production)
# - Set `WEBHOOK_URL` environment variable
# - Bot will automatically use webhook mode
# - Better for production (faster, more reliable)
# - Required for Render deployment

### Polling Mode (Good for Development)
# - Don't set `WEBHOOK_URL` or leave it empty
# - Bot will use long polling
# - Good for local development and testing

## 📝 Environment Variables Reference

### Required Variables
# ```bash
# BOT_TOKEN=                      # Telegram bot token from @BotFather
# DATABASE_URL=                   # PostgreSQL connection string
# ```

### Optional Variables
# ```bash
# Webhook Configuration
# WEBHOOK_URL=                   # Your domain for webhook ([https://your-app.onrender.com](https://your-app.onrender.com))
# WEBHOOK_SECRET=                 # Secret for webhook validation
# HOST=0.0.0.0                  # Server host (default: 0.0.0.0)
# PORT=10000                    # Server port (default: 10000 for Render)

# AI Services
# GEMINI_API_KEY=               # Google Gemini API key
# OPENAI_API_KEY=               # OpenAI API key
# GROK_API_KEY=                 # Grok API key

# Voice Services
# ELEVENLABS_API_KEY=            # ElevenLabs API key
# GOOGLE_TTS_KEY=                 # Google TTS API key
# WHISPER_API_KEY=               # Whisper API key (usually same as OpenAI)

# Telemedicine
# HELSI_API_KEY=                 # Helsi API key
# DOCTOR_ONLINE_API_KEY=         # Doctor Online API key

# Social Media (for marketing automation)
# FACEBOOK_TOKEN=                 # Facebook API token
# INSTAGRAM_TOKEN=               # Instagram API token
# LINKEDIN_TOKEN=                 # LinkedIn API token

# Admin & Support
# ADMIN_CHAT_ID=                 # Admin user ID for notifications
# SUPPORT_CHAT_ID=                 # Support chat ID
# SECRET_KEY=                   # Secret key for encryption
# ```

## 🚦 Health Checks

# Add these endpoints to monitor bot health:

#1. **Health Check**: `GET /health`
#2. **Bot Status**: `GET /status`
#3. **Database Status**: `GET /db-status`

# Example health check implementation:

# ```python
# from aiohttp import web

# async def health_check(request):
#     return web.json_response({"status": "healthy", "timestamp": datetime.now().isoformat()})

# Add to your web app
# app.router.add_get("/health", health_check)
# ```

## 🔧 Render-Specific Configuration

### Automatic Deployment
# - Render automatically detects `render.yaml` configuration
# - Supports automatic deployments from GitHub
# - Built-in PostgreSQL integration
# - Free SSL certificates

### Environment Variables in Render
#1. Go to your service dashboard
#2. Click "Environment" tab
#3. Add variables one by one
#4. Mark sensitive variables as "Secret"

## 🐛 Troubleshooting

### Common Issues

#1. **Database Connection Errors**
# - Verify DATABASE_URL format
# - Check database server status
# - Ensure user has proper permissions

#2. **Webhook Not Working**
# - Verify WEBHOOK_URL is accessible
# - Check webhook secret matches
# - Ensure HTTPS is used

#3. **AI Services Not Responding**
# - Verify API keys are correct
# - Check API quota/limits
# - Ensure proper API endpoint URLs

#4. **Bot Not Responding**
# - Check bot token is valid
# - Verify bot is not blocked
# - Check server logs for errors

### Debugging Commands

# ```bash
# Check bot status
# curl [https://api.telegram.org/bot](https://api.telegram.org/bot)<TOKEN>/getMe

# Test webhook
# curl [https://api.telegram.org/bot](https://api.telegram.org/bot)<TOKEN>/getWebhookInfo

# Check database connection
# python -c "import asyncpg; print('DB connection test')"
# ```

## 📊 Monitoring & Maintenance

### Recommended Monitoring

#1. **Uptime Monitoring**
# - Use services like UptimeRobot
# - Monitor webhook endpoint
# - Alert on downtime

#2. **Error Tracking**
# - Integrate with Sentry or similar
# - Track exceptions and errors
# - Monitor response times

#3. **Usage Analytics**
# - Track user engagement
# - Monitor API usage
# - Analyze bot performance

### Regular Maintenance

#1. **Database Cleanup**
# - Archive old chat logs
# - Clean up temporary files
# - Optimize database queries

#2. **Content Updates**
# - Update legal information
# - Refresh recommendations
# - Update hotline numbers

#3. **Security Updates**
# - Regular dependency updates
# - Security patch monitoring
# - API key rotation

## 🆘 Support

# If you need help with deployment:

#1. Check the [GitHub Issues](link-to-issues)
#2. Join our [Telegram Support Group](link-to-group)
#3. Contact development team

---

## ✅ Deployment Checklist

# - [ ] Bot token obtained from @BotFather
# - [ ] Database set up and accessible
# - [ ] All required environment variables configured
# - [ ] Dependencies installed successfully
# - [ ] Bot responds to `/start` command
# - [ ] Webhook configured (for production)
# - [ ] Health checks working
# - [ ] Monitoring set up
# - [ ] Admin notifications configured
# - [ ] Legal content updated
# - [ ] Terms & privacy policy reviewed

# **🎉 Your VetSupport AI bot is ready to help Ukrainian veterans!**
