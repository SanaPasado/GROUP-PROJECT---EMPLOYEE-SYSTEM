# Employee System Deployment Guide

## Prerequisites
- GitHub repository with your code
- Supabase account
- Render.com account

## Step 1: Prepare Your Repository

1. Ensure all files are committed to your GitHub repository
2. The following files should be present:
   - `build.sh` (executable)
   - `start.sh` (executable)
   - `requirements.txt`
   - `render.yaml`
   - `env.example`

## Step 2: Set Up Supabase

Follow the instructions in `SUPABASE_SETUP.md` to:
1. Create a Supabase project
2. Set up the database
3. Configure storage for media files
4. Get all required credentials

## Step 3: Deploy to Render.com

### Option A: Using render.yaml (Recommended)
1. Connect your GitHub repository to Render.com
2. Render will automatically detect the `render.yaml` file
3. Review the configuration and deploy

### Option B: Manual Setup
1. Go to Render.com dashboard
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: employee-system
   - **Environment**: Python 3
   - **Build Command**: `./build.sh`
   - **Start Command**: `./start.sh`
   - **Plan**: Free (or paid if needed)

## Step 4: Environment Variables

Set these environment variables in Render.com:

```bash
SECRET_KEY=your-django-secret-key
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com
DATABASE_URL=postgresql://postgres:[password]@[host]:5432/postgres
SUPABASE_ACCESS_KEY_ID=your-supabase-access-key
SUPABASE_SECRET_ACCESS_KEY=your-supabase-secret-key
SUPABASE_BUCKET_NAME=employee-photos
SUPABASE_ENDPOINT_URL=https://[project-ref].supabase.co/storage/v1/s3
SUPABASE_REGION=us-east-1
```

## Step 5: Database Setup

1. After deployment, the migrations will run automatically
2. Create a superuser by running in Render.com shell:
   ```bash
   python manage.py createsuperuser
   ```

## Step 6: Test Deployment

1. Visit your deployed application URL
2. Test the following features:
   - User registration/login
   - Employee photo uploads
   - Attendance tracking
   - OTP authentication

## Post-Deployment

### Security Checklist
- [ ] DEBUG is set to False
- [ ] SECRET_KEY is properly generated
- [ ] Database credentials are secure
- [ ] Storage credentials are secure
- [ ] HTTPS is enabled (automatic on Render.com)

### Monitoring
- Check Render.com logs for any errors
- Monitor Supabase dashboard for database usage
- Test file uploads to ensure storage is working

## Troubleshooting

### Common Issues:

1. **Build Fails**
   - Check `requirements.txt` for correct dependencies
   - Ensure `build.sh` is executable

2. **Database Connection Issues**
   - Verify DATABASE_URL format
   - Check Supabase database is running

3. **Static Files Not Loading**
   - Check STATIC_ROOT configuration
   - Verify WhiteNoise middleware is enabled

4. **File Upload Issues**
   - Verify Supabase storage credentials
   - Check bucket permissions

5. **OTP Not Working**
   - Ensure TOTP devices are properly configured
   - Check QR code generation

## Support

If you encounter issues:
1. Check Render.com logs
2. Review Supabase dashboard
3. Test locally with production settings
4. Check Django documentation for specific errors
