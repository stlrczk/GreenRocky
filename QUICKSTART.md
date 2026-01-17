# Quick Start Guide

## Prerequisites

You'll need:
1. OpenAI API key - Get one from https://platform.openai.com/api-keys
2. Python 3.11+ installed
3. Node.js 18+ installed

## Setup (One-Time)

### 1. Configure OpenAI API Key

Edit the backend `.env` file:
```bash
cd backend
nano .env  # or use any text editor
```

Replace `sk-your-key-here` with your actual OpenAI API key.

### 2. Verify Dependencies

Both backend and frontend dependencies have been installed. If you need to reinstall:

```bash
# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

## Running the Application

You'll need **two terminal windows**.

### Terminal 1: Start Backend

```bash
cd backend
./start.sh
```

Or manually:
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Wait for the message: "Loaded X tenders into memory"

### Terminal 2: Start Frontend

```bash
cd frontend
./start.sh
```

Or manually:
```bash
cd frontend
npm run dev
```

### Access the Application

Open your browser to: **http://localhost:3000**

## First Run

On the first ranking request:
- Backend will generate embeddings for all 1,412 tenders (~30 seconds)
- Embeddings are cached in `backend/data/embeddings_cache.json`
- Subsequent requests use cached embeddings (~200ms)

## Test the System

1. Click "Load Example" to load the GreenWorks company profile
2. Click "Find Matching Tenders"
3. Wait for results (first run: ~30s, subsequent: <1s)
4. Review top 100 tenders ranked by relevance
5. Use 👍 👎 buttons to rate tender relevance

Expected top results for GreenWorks:
- Green area maintenance tenders
- Tree cutting services
- Landscaping projects
- Municipal park maintenance

## Troubleshooting

### Backend won't start
- ✅ Check OpenAI API key in `backend/.env`
- ✅ Verify virtual environment is activated
- ✅ Ensure port 8000 is not in use

### Frontend can't connect to backend
- ✅ Verify backend is running on port 8000
- ✅ Check `frontend/.env.local` has correct API URL
- ✅ Look for CORS errors in browser console

### Embeddings generation fails
- ✅ Verify OpenAI API key is valid
- ✅ Check you have API credits available
- ✅ Review backend terminal for error messages

### "Module not found" errors
- ✅ Reinstall dependencies (see Setup section)
- ✅ Verify you're in the correct directory
- ✅ For backend: ensure venv is activated

## API Endpoints

Once running, you can test the API directly:

- Health check: http://localhost:8000
- API docs: http://localhost:8000/docs
- Get all tenders: GET http://localhost:8000/api/tenders
- Rank tenders: POST http://localhost:8000/api/rank
- Submit feedback: POST http://localhost:8000/api/feedback

## Feedback System

The feedback system stores user ratings in `backend/data/feedback.jsonl`:
- Each thumbs up/down is appended as a new line
- Feedback influences future rankings
- File grows over time (1 line per feedback)
- Can be cleared by deleting the file (will auto-recreate)

## Cost Monitoring

Check your OpenAI usage:
1. Go to https://platform.openai.com/usage
2. Look for embedding API calls
3. Expected costs:
   - Initial: ~$0.0014 (one-time)
   - Per query: ~$0.000006
   - Monthly (3K queries): ~$0.02

## Next Steps

- Review [README.md](README.md) for full documentation
- Customize company profiles
- Test with different industries
- Monitor feedback trends
- Consider deploying to production

## Support

If you encounter issues:
1. Check backend terminal for errors
2. Check frontend browser console for errors
3. Review the logs in both terminals
4. Ensure all prerequisites are met
5. Try restarting both services
