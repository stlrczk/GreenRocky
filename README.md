# AI Tender Matching System

MVP system matching Polish tenders to companies using OpenAI embeddings and company-aware feedback.

**Tech Stack:** FastAPI, Next.js 14, OpenAI text-embedding-3-small

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- OpenAI API key

### Setup

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Add your OPENAI_API_KEY to .env
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.local.example .env.local
```

### Run

**Option 1 - Using start scripts (recommended):**
```bash
# Terminal 1 - Backend
cd backend
./start.sh

# Terminal 2 - Frontend
cd frontend
./start.sh
```

**Option 2 - Manual commands:**
```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## How It Works

### 1. Semantic Matching

Uses OpenAI `text-embedding-3-small` to convert tenders and company descriptions into vectors. Ranking based on cosine similarity between company and tender embeddings.

**Process:**
1. One-time: Generate embeddings for hardcoded 1,412 tenders (metadata: title + organization) - already cached in repository
2. Per query: Generate embedding for company description
3. Calculate cosine similarity, return top 100 by similarity score (0-1 range)

### 2. Company-Aware Feedback

Feedback adjusts ranking **only for similar companies**, filtered by embedding similarity (threshold: 0.7).

**Formula:**
```
final_score = similarity_score × (1 + feedback_weight)
feedback_weight = (positive - negative) / (positive + negative + 10)
```

**Key points:**
- Feedback from Company A affects only companies with ≥0.7 similarity to Company A
- Companies with <0.7 similarity are unaffected
- Feedback applies **only to tenders in current dataset** - when new tender list is loaded, feedback must be reset

### 3. Storage

- **Tender embeddings:** `backend/data/embeddings_cache.json`
- **Feedback:** `backend/data/feedback.jsonl`
- **Company embeddings:** `backend/data/company_embeddings.jsonl`

## Key Assumptions & Limitations

**Assumptions:**
1. Tender metadata (title + organization) sufficient for matching
2. Embedding similarity correlates with business relevance
3. Company similarity predicts feedback relevance
4. User feedback is honest

**Limitations:**

- Metadata-only embeddings (no full tender documents)
- Static snapshot of 1,412 tenders (no auto-updates)
- No filtering by deadline, location, or category
- **Feedback tied to specific tender dataset** - new tenders require feedback reset

## Next Iteration

### High Priority [crucial for better MVP/PoC]
1. **Full document embeddings** - Use tender detail files instead of metadata only
2. **Brainstorm ideas** for feedback algorithm to improve over time with brand new, daily tenders lists
  - Option 1: Tender Similarity Transfer
    - When new tenders arrive, transfer feedback by finding similar old tenders (via embedding similarity) and applying their feedback weights to new tenders for companies with similar profiles.
- Option 2: Company Preference Vectors
    - Learn persistent "preference vectors" per company by aggregating embeddings of positively-rated tenders, then score new tenders by similarity to each company's preference vector instead of using per-tender feedback.
3. **User accounts and database** - PostgreSQL + JWT/OAuth for persistent feedback and saved preferences and embeddings

### Medium Priority [mandatory for production release]
4. **Performance optimization** - Caching, vector database

### Low Priority [nice to have after releasing to prod]
5. **Analytics dashboard** - Trending tenders, feedback effectiveness metrics
6. **A/B testing** - Compare thresholds (0.6/0.7/0.8), metadata vs full documents
