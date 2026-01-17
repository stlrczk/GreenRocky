export interface Tender {
  id: string;
  tender_url: string;
  name: string;
  organization: string;
  submission_deadline: string;
  initiation_date: string;
  procedure_type: string | null;
  source_type: string;
  files_count: number;
}

export interface RankedTender extends Tender {
  relevance_score: number;
  ranking_position: number;
}

export interface TendersResponse {
  count: number;
  target_date: string;
  tenders: Tender[];
}

export interface RankingResponse {
  ranked_tenders: RankedTender[];
  total_tenders: number;
  processing_time_ms?: number;
}

export interface RankingRequest {
  company_description: string;
  top_n?: number;
  use_feedback?: boolean;
}

export interface FeedbackRequest {
  tender_id: string;
  company_description_hash: string;
  feedback: "positive" | "negative";
  timestamp: string;
}

export interface FeedbackResponse {
  status: string;
  message: string;
}
