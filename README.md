# Tender Matching System - MVP

An AI-powered tender matching system that ranks Polish tenders against company profiles using OpenAI embeddings.

## Tech Stack

### Backend
- FastAPI
- Python 3.11+
- OpenAI API (text-embedding-3-small)
- NumPy

### Frontend
- Next.js 14 (App Router)
- React 18
- TypeScript
- Tailwind CSS
- React Query

## Project Structure

```
GreenRocky/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── api/      # API routes
│   │   ├── models/   # Pydantic models
│   │   └── services/ # Business logic
│   └── data/         # Data files
├── frontend/         # Next.js frontend
│   ├── app/          # App router pages
│   ├── components/   # React components
│   └── lib/          # Utilities & API client
└── company_profile.md
```

## Setup Instructions

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local
# Edit .env.local if needed (default: http://localhost:8000)
```

### 3. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Visit http://localhost:3000 in your browser.

## How It Works

### AI Ranking Process

1. **One-Time Setup**: Generate embeddings for all 1,412 tenders (cached)
2. **User Query**: Generate embedding for company description
3. **Similarity Calculation**: Compute cosine similarity between company and each tender
4. **Ranking**: Sort by similarity score, return top 100
5. **Feedback Integration**: Adjust scores based on historical thumbs up/down feedback

### Cost Efficiency
- Initial setup: ~$0.0014 (one-time)
- Per query: ~$0.000006
- Monthly (3K queries): ~$0.02

### Feedback Loop
- Users rate tenders with thumbs up/down
- Feedback stored in JSONL file
- Future rankings weighted by feedback history
- Formula: `final_score = similarity × (1 + feedback_weight)`

## API Endpoints

### GET /api/tenders
Get all tenders

### POST /api/rank
Rank tenders based on company description

**Request:**
```json
{
  "company_description": "Your company description...",
  "top_n": 100,
  "use_feedback": true
}
```

### POST /api/feedback
Submit user feedback

**Request:**
```json
{
  "tender_id": "1243607",
  "company_description_hash": "abc123...",
  "feedback": "positive",
  "timestamp": "2026-01-17T10:30:00Z"
}
```

## Testing

### Test with Example Company Profile

The system includes an example company profile (GreenWorks Infrastructure Ltd.). Click "Load Example" in the UI to test.

Expected results: Top tenders should include:
- Green area maintenance
- Landscaping projects
- Tree cutting services
- Municipal infrastructure work

### Manual Testing Checklist

- [ ] Backend starts without errors
- [ ] Frontend loads at http://localhost:3000
- [ ] Company description input works
- [ ] "Find Matching Tenders" button triggers ranking
- [ ] Top 100 tenders display with relevance scores
- [ ] Thumbs up/down buttons work
- [ ] Feedback persists (check backend/data/feedback.jsonl)
- [ ] Re-ranking includes feedback weights

## Troubleshooting

### Backend won't start
- Check OpenAI API key in .env
- Ensure Tenders_List.json is in backend/data/
- Verify Python 3.11+ is installed

### Frontend won't connect to backend
- Check NEXT_PUBLIC_API_URL in .env.local
- Ensure backend is running on port 8000
- Check CORS_ORIGINS in backend .env

### Embeddings generation is slow
- First run generates embeddings for all tenders (~30s)
- Subsequent runs use cached embeddings (<1s)
- Cache file: backend/data/embeddings_cache.json

## Development

### Adding New Features

1. **Backend**: Add routes in `backend/app/api/routes/`
2. **Frontend**: Add components in `frontend/components/`
3. **Types**: Update `frontend/lib/types.ts` to match backend models

### Code Style

- Backend: PEP 8 (Python)
- Frontend: ESLint + Prettier (TypeScript/React)
- Use descriptive variable names
- Add comments for complex logic

## Production Deployment

### Backend
- Deploy to Railway.app, Render.com, or similar
- Set environment variables (OPENAI_API_KEY, CORS_ORIGINS)
- Ensure persistent volume for data files

### Frontend
- Deploy to Vercel or Netlify
- Set NEXT_PUBLIC_API_URL to production backend URL
- Enable automatic deployments from Git

## License

MIT

## Contact

For questions or issues, please create an issue in the repository.
