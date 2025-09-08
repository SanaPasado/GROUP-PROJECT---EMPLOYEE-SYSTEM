# Supabase Setup Guide for Employee System

## 1. Database Setup

### Create Supabase Project
1. Go to [Supabase](https://supabase.com) and create a new project
2. Note down your project URL and API keys

### Database Configuration
1. In your Supabase dashboard, go to Settings > Database
2. Copy the connection string (it looks like: `postgresql://postgres:[password]@[host]:5432/postgres`)
3. Set this as your `DATABASE_URL` environment variable

## 2. Storage Setup (for Media Files)

### Create Storage Bucket
1. In Supabase dashboard, go to Storage
2. Create a new bucket named `employee-photos` (or your preferred name)
3. Set the bucket to public if you want public access to employee photos

### Get Storage Credentials
1. Go to Settings > API
2. Copy the following values:
   - `SUPABASE_ACCESS_KEY_ID` (from Storage API keys)
   - `SUPABASE_SECRET_ACCESS_KEY` (from Storage API keys)
   - `SUPABASE_BUCKET_NAME` (the bucket name you created)
   - `SUPABASE_ENDPOINT_URL` (format: `https://[project-ref].supabase.co/storage/v1/s3`)
   - `SUPABASE_REGION` (usually `us-east-1`)

## 3. Environment Variables

Set these environment variables in your Render.com deployment:

```bash
SECRET_KEY=your-django-secret-key
DEBUG=False
ALLOWED_HOSTS=your-app.onrender.com
DATABASE_URL=postgresql://postgres:[password]@[host]:5432/postgres
SUPABASE_ACCESS_KEY_ID=your-access-key
SUPABASE_SECRET_ACCESS_KEY=your-secret-key
SUPABASE_BUCKET_NAME=employee-photos
SUPABASE_ENDPOINT_URL=https://[project-ref].supabase.co/storage/v1/s3
SUPABASE_REGION=us-east-1
```

## 4. Database Migrations

After setting up the database, run migrations:

```bash
python manage.py migrate
```

## 5. Create Superuser

Create an admin user:

```bash
python manage.py createsuperuser
```

## 6. Test the Setup

1. Deploy to Render.com
2. Check that the application loads correctly
3. Test file uploads (employee photos)
4. Verify database connectivity

## Troubleshooting

### Common Issues:
1. **Database Connection**: Ensure DATABASE_URL is correctly formatted
2. **Storage Access**: Check that storage bucket exists and is accessible
3. **CORS Issues**: Configure CORS in Supabase if needed
4. **File Uploads**: Verify storage credentials and bucket permissions
