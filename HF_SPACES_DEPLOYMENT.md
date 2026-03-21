# Hugging Face Spaces Deployment Guide

## Quick Deployment Steps

### 1. Create Hugging Face Space
1. Go to [huggingface.co/spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Choose:
   - **Space name**: `cv-analyser` (or your choice)
   - **License**: MIT or Apache 2.0
   - **SDK**: Docker
   - **Hardware**: CPU Basic (free)
   - **Visibility**: Public or Private

### 2. Push Code to Space
```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial HF Spaces deployment"

# Add your space as remote (replace with your username)
git remote add hf https://huggingface.co/spaces/your-username/cv-analyser

# Push to HF Spaces
git push hf main
```

### 3. Configure Secrets
In your HF Space settings, add these secrets:
- `DATABASE_URL`: `postgresql://recruiter:zhubXkTYjieGoYevXB7jtHj5EdhNYmV7@dpg-d6v72fchg0os73ddre00-a.oregon-postgres.render.com/analyser_w2n9?sslmode=require`
- `HF_API_TOKEN`: (optional, if you want to use HF API)

### 4. Test Deployment
1. Wait for the build to complete (check Build tab)
2. Test health endpoint: `https://your-space.hf.space/health`
3. Warmup models: `POST https://your-space.hf.space/warmup`
4. Test analyze: `POST https://your-space.hf.space/api/v1/analyze`

## Architecture After Migration

```
Frontend (Render/Web) 
    ↓
Recruitment API (Render)
    ↓
CV Analyser API (Hugging Face Spaces)
    ↓
PostgreSQL (Render DB - analyser_w2n9)
```

## Environment Variables (HF Spaces)

The service will use these defaults on HF Spaces:
- `SERVICE_PORT=7860` (HF Spaces default)
- `LAZY_MODEL_LOAD=true` (load on first request)
- `INLINE_JOBS=true` (synchronous processing)
- `SKIP_MODEL_LOAD=false` (load models when needed)

## Performance Benefits

### Before (Render Free Tier)
- 512MB RAM
- Model loading timeouts
- Cold start issues
- Unstable performance

### After (Hugging Face Spaces)
- ~16GB RAM
- Native ML environment
- Stable performance
- Better resource allocation

## Monitoring

- Check the "Logs" tab in your HF Space
- Monitor model loading times
- Track request durations
- Check error rates

## Scaling

If you need more resources:
- Upgrade to CPU Basic (2x) or CPU Upgrade
- Consider GPU for faster model loading
- Use multiple spaces for load balancing

## Troubleshooting

### Common Issues
1. **Build fails**: Check requirements.txt for conflicts
2. **Database connection**: Verify DATABASE_URL secret
3. **Model loading errors**: Check logs for memory issues
4. **Slow responses**: Call POST /warmup after deployment

### Health Check Endpoints
- `/health` - Basic health check
- `/warmup` - Pre-load models
- `/api/v1/analyze` - Main analysis endpoint

## Next Steps

1. Update recruitment app to point to HF Spaces URL
2. Set up monitoring and alerts
3. Consider CDN for static assets
4. Implement request queuing for high traffic
