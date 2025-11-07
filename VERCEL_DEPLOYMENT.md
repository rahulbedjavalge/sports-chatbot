# Vercel Deployment Guide for Sports Chatbot

## 🚀 Quick Deployment Steps

### 1. Prerequisites
- GitHub account
- Vercel account (free tier available)
- OpenRouter API key (free tier available)

### 2. Repository Setup
```bash
# 1. Initialize git repository
git init
git add .
git commit -m "Initial commit - Enhanced Sports Chatbot"

# 2. Create GitHub repository and push
git remote add origin https://github.com/yourusername/sports-chatbot.git
git branch -M main
git push -u origin main
```

### 3. Vercel Deployment
1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "New Project"
3. Import your GitHub repository
4. Configure build settings:
   - Framework Preset: `Other`
   - Build Command: (leave empty)
   - Output Directory: `frontend`
   - Install Command: `pip install -r requirements.txt`

### 4. Environment Variables
In Vercel dashboard, add these environment variables:
- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `OPENROUTER_MODEL`: `tngtech/deepseek-r1t2-chimera:free`

### 5. Domain Setup
- Vercel will provide a free domain: `your-app-name.vercel.app`
- Custom domain can be added in project settings

## 📁 Project Structure for Vercel

```
sports-chatbot/
├── api/                    # Vercel serverless functions
│   └── app.py             # Main API endpoint
├── frontend/               # Static frontend files
│   ├── index.html
│   ├── app.js
│   └── style.css
├── backend/               # Local development backend
│   ├── app.py
│   └── db.sqlite3
├── nlp/                   # ML models and training
│   ├── artifacts/
│   └── data/
├── vercel.json           # Vercel configuration
├── requirements.txt      # Python dependencies
├── package.json         # Project metadata
└── README.md            # Documentation
```

## 🔧 Technology Stack (Production)

### Backend (Serverless)
- **Runtime**: Python 3.9+ on Vercel
- **Framework**: Flask with CORS
- **API**: OpenRouter (free DeepSeek model)
- **Data**: In-memory mock data (Vercel-optimized)

### Frontend
- **Hosting**: Vercel CDN
- **Tech**: Vanilla HTML/CSS/JavaScript
- **Features**: Real-time chat, responsive design

### Features Supported in Production:
✅ Match score queries
✅ Stadium information
✅ Match dates and tournaments
✅ Team rankings
✅ Scorer information
✅ LLM fallback for general questions
✅ Responsive web interface

## 🌐 Live Demo URLs
- **Production**: `https://your-app-name.vercel.app`
- **API Health**: `https://your-app-name.vercel.app/api/health`
- **API Endpoint**: `https://your-app-name.vercel.app/api/chat`

## 🔒 Security Features
- Environment variable protection
- CORS configuration
- API rate limiting (via Vercel)
- Secure API key management

## 📊 Performance
- **Cold Start**: ~2-3 seconds (Vercel serverless)
- **Response Time**: 100-500ms for structured queries
- **LLM Fallback**: 1-3 seconds
- **Global CDN**: Vercel Edge Network

## 🧪 Testing Production Deployment

### Health Check:
```bash
curl https://your-app-name.vercel.app/api/health
```

### Chat API Test:
```bash
curl -X POST https://your-app-name.vercel.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What was the score of Alpha FC vs Beta United?"}'
```

## 🔄 Continuous Deployment
- Automatic deployment on git push to main branch
- Preview deployments for pull requests
- Rollback capabilities in Vercel dashboard

## 💡 Production Optimizations Applied
1. **Serverless Architecture** - Scales automatically
2. **CDN Distribution** - Fast global loading
3. **Environment Security** - API keys protected
4. **Simplified Data Layer** - Optimized for serverless
5. **Smart API Routing** - Dynamic endpoint detection
6. **Error Handling** - Graceful fallbacks

## 🆘 Troubleshooting

### Common Issues:
1. **500 Error**: Check environment variables are set
2. **CORS Issues**: Verify frontend domain in CORS settings
3. **Cold Starts**: First request may be slow (normal for serverless)
4. **API Timeout**: LLM requests have 30s timeout

### Debug Commands:
```bash
# Check deployment logs
vercel logs your-app-name

# Test locally before deployment  
vercel dev
```

## 🎯 Next Steps
1. Custom domain setup
2. Analytics integration
3. Advanced caching strategies
4. Database upgrade (if needed)
5. Mobile app development