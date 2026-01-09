# Render.com Deployment Guide - ScooterShare Pro

## Prerequisites
- GitHub account connected to Render.com
- Repository: https://github.com/eazybusiness/scooter-share-pro

## Automatic Deployment (Recommended)

Render.com will automatically detect the `render.yaml` file and set up:
- PostgreSQL database (free tier)
- Web service with Python environment
- Environment variables

### Steps:

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com/

2. **Create New Blueprint**
   - Click "New +" → "Blueprint"
   - Connect GitHub repository: `eazybusiness/scooter-share-pro`
   - Branch: `main`
   - Render will detect `render.yaml` automatically

3. **Review Configuration**
   - Service Name: `scooter-share-pro`
   - Database: `scooter-share-pro-db` (PostgreSQL)
   - Environment: Production
   - Auto-deploy: Enabled

4. **Deploy**
   - Click "Apply"
   - Wait for deployment (5-10 minutes)
   - Database will be created automatically
   - Tables will be created on first run

## Manual Deployment (Alternative)

### Step 1: Create PostgreSQL Database

1. Go to Render Dashboard
2. Click "New +" → "PostgreSQL"
3. Configure:
   - Name: `scooter-share-pro-db`
   - Database: `scooter_share_pro`
   - User: `scooter_user`
   - Region: Choose closest to you
   - Plan: Free
4. Click "Create Database"
5. Copy the "Internal Database URL"

### Step 2: Create Web Service

1. Click "New +" → "Web Service"
2. Connect GitHub repository: `eazybusiness/scooter-share-pro`
3. Configure:
   - Name: `scooter-share-pro`
   - Region: Same as database
   - Branch: `main`
   - Root Directory: (leave empty)
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn -w 4 -b 0.0.0.0:$PORT run:app`
   - Plan: Free

### Step 3: Environment Variables

Add these environment variables in Render dashboard:

```
FLASK_APP=run.py
FLASK_ENV=production
FLASK_CONFIG=production
SECRET_KEY=<generate-random-string>
JWT_SECRET_KEY=<generate-random-string>
DATABASE_URL=<paste-internal-database-url>
BASE_PRICE_PER_MINUTE=0.25
START_FEE=1.00
```

### Step 4: Deploy

1. Click "Create Web Service"
2. Wait for initial deployment
3. Check logs for any errors

## Post-Deployment

### Initialize Database

The database tables will be created automatically on first run using `db.create_all()`.

### Create Admin User

Connect to your service shell:

```bash
# In Render dashboard, go to Shell tab
flask create-admin
```

Or use Python directly:

```python
from app import create_app, db
from app.models import User

app = create_app('production')
with app.app_context():
    admin = User(
        email='admin@scootershare.com',
        first_name='Admin',
        last_name='User',
        role='admin'
    )
    admin.set_password('SecurePassword123!')
    db.session.add(admin)
    db.session.commit()
```

## Access Your Application

Your app will be available at:
```
https://scooter-share-pro.onrender.com
```

API Documentation (Swagger):
```
https://scooter-share-pro.onrender.com/api/docs/
```

## Monitoring

- **Logs**: Available in Render dashboard
- **Metrics**: CPU, Memory usage in dashboard
- **Health Check**: Automatic by Render

## Troubleshooting

### Database Connection Issues
- Verify DATABASE_URL is set correctly
- Check database is in same region as web service
- Ensure internal database URL is used (not external)

### Application Won't Start
- Check logs in Render dashboard
- Verify all environment variables are set
- Check requirements.txt is complete

### Migrations
If you need to run migrations:
```bash
flask db upgrade
```

## Free Tier Limitations

- **Database**: 1GB storage, expires after 90 days
- **Web Service**: 750 hours/month, sleeps after 15 min inactivity
- **Cold Start**: ~30 seconds when waking from sleep

## Updating

Push to GitHub `main` branch:
```bash
git push origin main
```

Render will automatically redeploy.

## Support

- Render Docs: https://render.com/docs
- Community: https://community.render.com
