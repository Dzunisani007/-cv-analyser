# CV Analyser Backend - Production Deployment Guide

## Overview
The CV Analyser has been successfully refactored to a pure AI-driven text processing engine. It no longer handles file uploads or storage - it accepts raw CV text via JSON API.

## Environment Variables

### Required Environment Variables
```bash
# Database
DATABASE_URL=postgresql://username:password@host:port/database?sslmode=require

# Authentication
AUTH_SECRET=your-secret-key-here

# Hugging Face API (for AI models)
HF_API_TOKEN=hf_your-huggingface-token-here
```

### Optional Environment Variables
```bash
# AI Model Configuration
NER_MODEL=dslim/bert-base-NER
GLINER_MODEL=urchade/gliner_base-v2.1
STRUCTURED_EXTRACTION_MODEL=microsoft/DialoGPT-medium
ENABLE_STRUCTURED_EXTRACTION=true

# Service Configuration
WORKER_COUNT=2
INLINE_JOBS=false
PROMETHEUS_ENABLED=true
DEBUG=false
```

## Database Migration

Once you have your production database URL configured:

1. Update alembic.ini with your production DATABASE_URL
2. Run the migration:
   ```bash
   alembic upgrade head
   ```

## Deployment Platforms

### Render Deployment
1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set environment variables in Render dashboard
4. Use the following start command:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

### Docker Deployment
Create a Dockerfile:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.runtime.txt .
RUN pip install -r requirements.runtime.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Heroku Deployment
1. Create a Procfile:
   ```
   web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
2. Set environment variables
3. Deploy using Heroku CLI

## API Endpoints

### New Analyze Endpoint
```http
POST /api/v1/analyze
Content-Type: application/json
Authorization: Bearer YOUR_AUTH_SECRET

{
  "cv_text": "Raw CV text here...",
  "job_description": "Optional job description",
  "industry": "Optional industry context"
}
```

Response:
```json
{
  "analysis_id": "uuid-here",
  "status": "pending"
}
```

### Check Status
```http
GET /api/v1/analyze/{analysis_id}/status
```

### Get Results
```http
GET /api/v1/analyze/{analysis_id}/result
```

## Integration with Recruitment App

Update your Recruitment App to send requests to the new endpoint:

```javascript
const response = await fetch('https://your-analyser-url.com/api/v1/analyze', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${process.env.ANALYSIS_SERVICE_SECRET}`
  },
  body: JSON.stringify({
    cv_text: extractedCvText,
    job_description: jobDescription,
    industry: 'technology'
  })
});

const { analysis_id } = await response.json();
```

## Health Check
The service includes a health check endpoint:
```http
GET /health
```

## Monitoring
- Prometheus metrics are available at `/metrics` when `PROMETHEUS_ENABLED=true`
- Logs include analysis status and errors

## Troubleshooting

### Common Issues
1. **Database connection errors**: Verify DATABASE_URL is correct and accessible
2. **AI model errors**: Check HF_API_TOKEN is valid and has sufficient quota
3. **Migration failures**: Ensure database user has CREATE TABLE permissions

### Debug Mode
Set `DEBUG=true` to enable detailed logging

## Security Notes
- Always use HTTPS in production
- Keep AUTH_SECRET secure and private
- Database should use SSL connections
- Consider rate limiting for the API endpoint
