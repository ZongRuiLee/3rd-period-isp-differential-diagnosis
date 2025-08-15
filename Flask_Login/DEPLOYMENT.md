# Railway Deployment Guide

## Environment Variables

Set these environment variables in your Railway project:

### Required Variables:
- `SECRET_KEY`: A secure random string for Flask sessions
- `RECAPTCHA_SITE_KEY`: Your reCAPTCHA site key (if using reCAPTCHA)

### Database (Auto-configured by Railway):
- `DATABASE_URL`: Railway automatically provides this for PostgreSQL

## Deployment Steps

1. **Connect to Railway:**
   - Install Railway CLI: `npm install -g @railway/cli`
   - Login: `railway login`
   - Link project: `railway link`

2. **Set Environment Variables:**
   ```bash
   railway variables set SECRET_KEY="your-secure-secret-key-here"
   railway variables set RECAPTCHA_SITE_KEY="your-recaptcha-key-here"
   ```

3. **Deploy:**
   ```bash
   railway up
   ```

4. **Check Status:**
   ```bash
   railway status
   ```

## Health Check

The application includes a health check endpoint at `/health` that Railway will use to monitor the service.

## Troubleshooting

- Check logs: `railway logs`
- Restart service: `railway service restart`
- View variables: `railway variables`

## Security Notes

- Never commit `.env` files to version control
- Use strong, random secret keys
- Railway automatically handles HTTPS and SSL termination
