# Render Deployment Guide

## Quick Deployment Steps

### 1. Push to GitHub
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. Create Render Service
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select the `cv-analyser-backend/service` directory
5. Render will automatically detect the `render.yaml` configuration

### 3. Verify Environment Variables
Ensure the following are set in Render dashboard:
- `DATABASE_URL`: postgresql://recruitement_deploy_user:tHkpCaJ8nxQpN1tCItF7BEXNvzLrkgiQ@dpg-d62tb67pm1nc738h8jv0-a.oregon-postgres.render.com/recruitement_deploy?sslmode=require
- `STORAGE_BACKEND`: local
- `SKIP_MODEL_LOAD`: true
- `AUTH_SECRET`: 3c9f1e7a8b6d4c2f5a9e0d1b7c3f8a6e
- `PUBLIC_UPLOADS`: false
- `HF_API_TOKEN`: (empty)

### 4. Deploy and Monitor
- Click "Create Web Service"
- Monitor the build logs
- Wait for deployment to complete

### 5. Test Deployment
```bash
# Test health endpoint
curl -X GET https://your-service.onrender.com/health \
  -H "Authorization: Bearer 3c9f1e7a8b6d4c2f5a9e0d1b7c3f8a6e"

# Test upload endpoint
curl -X POST https://your-service.onrender.com/upload \
  -H "Authorization: Bearer 3c9f1e7a8b6d4c2f5a9e0d1b7c3f8a6e" \
  -F "file=@test.pdf" \
  -F "job_description=Software Engineer with Python"
```

## Expected Service URL
Once deployed, your service will be available at:
`https://cv-analysis-service.onrender.com`

## Integration URLs
- Health: `https://cv-analysis-service.onrender.com/health`
- Upload: `https://cv-analysis-service.onrender.com/upload`
- Status: `https://cv-analysis-service.onrender.com/analyses/{analysis_id}/status`
- Result: `https://cv-analysis-service.onrender.com/analyses/{analysis_id}/result`

## Troubleshooting

### Common Issues
1. **Build Failures**: Check that all requirements are in `requirements.runtime.txt`
2. **Database Connection**: Verify DATABASE_URL is correct and accessible
3. **Permission Errors**: Ensure AUTH_SECRET matches between services
4. **Memory Issues**: Monitor resource usage, may need to upgrade Render plan

### Logs
- Check Render service logs for any errors
- Monitor build logs for dependency installation issues
- Use health endpoint to verify service status

### Performance
- Monitor response times
- Check database query performance
- Consider upgrading to paid plan for better performance

## Next Steps
After successful deployment:
1. Update main app environment variables
2. Implement AnalysisServiceClient
3. Test end-to-end integration
4. Monitor production performance
