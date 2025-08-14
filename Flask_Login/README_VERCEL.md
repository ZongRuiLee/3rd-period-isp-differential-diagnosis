# Deploying Flask App to Vercel

This guide will help you deploy your Flask differential diagnosis application to Vercel.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Vercel CLI**: Install with `npm i -g vercel`
3. **Git Repository**: Your code should be in a Git repository

## Important Considerations

### ⚠️ Limitations on Vercel

1. **File Size Limits**: Your ML model files (`xgboostModel.joblib` - 6.7MB) exceed Vercel's 50MB function size limit
2. **Database**: SQLite won't work on Vercel - you'll need PostgreSQL
3. **File System**: Vercel has read-only file system, so file uploads won't work

## Deployment Options

### Option 1: Use Vercel with External Services (Recommended)

1. **Set up PostgreSQL Database**:
   - Use [Supabase](https://supabase.com) (free tier available)
   - Or [Neon](https://neon.tech) (free tier available)
   - Get your `DATABASE_URL`

2. **Host ML Models Externally**:
   - Upload models to [Hugging Face](https://huggingface.co)
   - Or use [Google Cloud Storage](https://cloud.google.com/storage)
   - Update the code to download models at runtime

3. **Deploy to Vercel**:
   ```bash
   cd Flask_Login
   vercel
   ```

### Option 2: Alternative Hosting Platforms

Consider these platforms that better support Flask apps:

- **Railway**: `railway.app` - Supports Flask natively
- **Render**: `render.com` - Good Flask support
- **Heroku**: `heroku.com` - Classic Flask hosting
- **DigitalOcean App Platform**: `digitalocean.com/products/app-platform`

## Required Changes for Vercel

### 1. Database Configuration

Update `api/index.py` to use environment variables:

```python
# Set these in Vercel dashboard
DATABASE_URL=postgresql://username:password@host:port/database
SECRET_KEY=your-secret-key
```

### 2. ML Model Loading

Replace local file loading with external URLs:

```python
import requests

def load_model_from_url(url):
    response = requests.get(url)
    return joblib.load(BytesIO(response.content))

# Load models from external URLs
xgb = load_model_from_url('https://your-storage.com/xgboostModel.joblib')
encoder = load_model_from_url('https://your-storage.com/label_encoder.joblib')
```

### 3. Environment Variables

Set these in Vercel dashboard:

```
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
RECAPTCHA_SITE_KEY=your-recaptcha-key
```

## Deployment Steps

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   cd Flask_Login
   vercel
   ```

4. **Follow prompts**:
   - Link to existing project or create new
   - Set root directory to `Flask_Login`
   - Deploy

## Post-Deployment

1. **Set Environment Variables** in Vercel dashboard
2. **Set up Database** and update `DATABASE_URL`
3. **Upload ML Models** to external storage
4. **Test the Application**

## Troubleshooting

### Common Issues:

1. **Function Size Too Large**: ML models exceed limits
2. **Database Connection**: SQLite not supported
3. **File Paths**: Relative paths may not work
4. **Dependencies**: Some packages may not be compatible

### Solutions:

1. **Use External ML Model Hosting**
2. **Switch to PostgreSQL**
3. **Use Absolute Paths**
4. **Check Package Compatibility**

## Alternative: Simplified Vercel Version

If you want to deploy a simplified version without ML features:

1. Remove ML model loading
2. Use mock predictions
3. Focus on the web interface
4. Deploy core Flask functionality

## Support

- [Vercel Documentation](https://vercel.com/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Vercel Community](https://github.com/vercel/vercel/discussions) 