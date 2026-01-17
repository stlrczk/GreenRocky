# AI Tender Matching System

An MVP system that matches Polish tenders to companies using OpenAI embeddings and user feedback.

**Tech Stack:** FastAPI (backend), Next.js 14 (frontend), OpenAI text-embedding-3-small

---

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

---

## How Recommendations Work

### 1. **Semantic Matching with Embeddings**

The system converts both tenders and company descriptions into high-dimensional vectors (embeddings) using OpenAI's `text-embedding-3-small` model. These embeddings capture semantic meaning, not just keywords.

**Process:**
1. **One-time setup:** Generate embeddings for all 1,412 tenders from metadata (title + organization)
2. **Per query:** Generate embedding for user's company description
3. **Similarity calculation:** Compute cosine similarity between company embedding and each tender embedding
4. **Initial ranking:** Sort tenders by similarity score (0-1 range), return top 100

**Example:**
- Company: *"We provide landscaping, tree cutting, and green area maintenance"*
- High-scoring tender: *"Tree cutting services for Warsaw parks"* (similarity: 0.85)
- Low-scoring tender: *"Hospital medical equipment procurement"* (similarity: 0.23)

### 2. **Company-Aware Feedback Adjustment**

After initial ranking, the system applies feedback weights from **similar companies only**:

**Feedback Formula:**
```
final_score = similarity_score × (1 + feedback_weight)

where:
feedback_weight = (positive - negative) / (positive + negative + 10)
```

**Key Innovation:** Feedback is filtered by company similarity:
- Company A (landscaping) rates tender as 👍
- Tender gets boosted **only** for similar companies (tree services, gardening, etc.)
- Dissimilar companies (medical, IT) are unaffected

**Similarity Threshold:** 0.7 (configurable in [backend/app/config.py](backend/app/config.py))

---

## User Feedback System

### How Feedback Influences Ranking

**Step-by-Step Flow:**

1. **User rates a tender:** Clicks 👍 or 👎 on a tender card
2. **Backend stores:**
   - Feedback entry: `{"tender_id": "123", "company_hash": "abc...", "feedback": "positive"}`
   - Company embedding: Saved for future similarity comparisons
3. **Future rankings:**
   - System calculates similarity between new company and all past companies
   - Only feedback from similar companies (≥0.7 similarity) affects scores
   - Positive feedback boosts scores, negative feedback reduces them

**Example Scenario:**

```
Company A (GreenWorks - Landscaping):
  → Rates Tender #1243607 "Tree cutting" as 👍 positive

Company B (TreeCare - Similar to GreenWorks, 0.81 similarity):
  → Searches for tenders
  → Tender #1243607 IS boosted (+9% score increase)

Company C (MedSupply - Medical, 0.15 similarity to GreenWorks):
  → Searches for tenders
  → Tender #1243607 NOT affected (similarity below 0.7 threshold)
```

### Benefits of Company-Aware Feedback

- **Personalization:** Each company type learns from relevant feedback only
- **No pollution:** Landscaping feedback doesn't affect medical companies
- **Cold start friendly:** New companies benefit from existing similar companies' feedback
- **Zero cost:** Reuses embeddings already generated during ranking

---

## Key Assumptions & Limitations

### Assumptions

1. **Metadata is sufficient:** Tender titles and organization names contain enough information for matching
   - *Reality:* Most Polish tenders have descriptive titles (e.g., "Tree cutting for Warsaw parks")
   - *Limitation:* Some tenders have vague titles ("Various services")

2. **Text-based matching works:** Semantic similarity in embeddings correlates with business relevance
   - *Reality:* Works well for clear service descriptions
   - *Limitation:* Doesn't capture non-textual factors (pricing, location, certifications)

3. **Company similarity predicts feedback relevance:** Companies with similar descriptions have similar tender preferences
   - *Reality:* True for most cases (landscaping companies prefer similar tenders)
   - *Limitation:* Doesn't account for company size, experience level, or regional focus

4. **User feedback is honest:** Thumbs up/down accurately reflects tender relevance
   - *Limitation:* No spam protection, single user can skew results

### Current Limitations

**Data:**
- Only tender metadata used (title + organization), not full tender documents
- 1,412 tenders from single snapshot (no updates)
- No tender filtering (all tenders shown, regardless of deadline status)

**Functionality:**
- No user accounts or session persistence
- No tender search/filtering by category, location, or deadline
- No notification system for new matching tenders
- Feedback buttons reset on page refresh (local state only)

**Performance:**
- First ranking query takes ~500ms (acceptable for MVP)
- Company embeddings file grows linearly (~15KB per company)
- No optimization for 10,000+ companies (would need vector database)

**Cost:**
- Initial setup: $0.0014 (one-time)
- Per query: $0.000006 (~$0.02/month for 3,000 queries)
- Cost increases 71× if using full tender documents (~$0.10/month)

---

## Next Iteration Improvements

### High Priority (Core Functionality)

1. **Full Document Embeddings**
   - Use tender detail files instead of just metadata
   - Cost: ~$0.10 one-time for all 1,412 tenders
   - Expected improvement: 15-20% better precision
   - **Implementation:** [COST_ANALYSIS.md](COST_ANALYSIS.md) has full analysis

2. **User Accounts & Saved Preferences**
   - Persistent feedback history per user
   - Saved company descriptions
   - Email notifications for new matching tenders
   - **Stack:** Add PostgreSQL + authentication (JWT or OAuth)

3. **Advanced Filtering**
   - Filter by deadline, location, tender value range
   - Category-based filtering (construction, services, goods)
   - Hide expired tenders automatically
   - **Implementation:** Add filters to ranking endpoint + frontend UI

4. **Tender Updates**
   - Automatic scraping of new tenders (daily/weekly)
   - Notification system for new matches above threshold
   - Archive old tenders past deadline

### Medium Priority (UX & Performance)

5. **Improved Feedback Visualization**
   - Show why tender was recommended (matching keywords)
   - Display feedback confidence (e.g., "5 similar companies ranked it as relevant")
   - Feedback explanation tooltips

6. **Performance Optimization**
   - Cache ranking results per company description (avoid re-ranking)
   - Use vector database (Pinecone, Weaviate) for >10K companies
   - Background job for embedding generation (non-blocking)

7. **Multi-language Support**
   - Translate tender titles to English (Google Translate API)
   - Support English company descriptions
   - **Note:** OpenAI embeddings already handle Polish well

### Low Priority (Nice to Have)

8. **Analytics Dashboard**
   - Show trending tenders (most viewed/liked)
   - Company matching statistics
   - Feedback effectiveness metrics (precision improvements)

9. **Collaborative Filtering**
   - "Companies like yours also viewed..." recommendations
   - Learn from viewing patterns, not just explicit feedback

10. **A/B Testing Framework**
    - Test different similarity thresholds (0.6 vs 0.7 vs 0.8)
    - Compare metadata-only vs full-document embeddings
    - Measure precision improvements
