import axios from 'axios';
import {
  TendersResponse,
  RankingResponse,
  RankingRequest,
  FeedbackRequest,
  FeedbackResponse,
} from './types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const tendersApi = {
  /**
   * Get all tenders
   */
  getAllTenders: async (): Promise<TendersResponse> => {
    const response = await api.get<TendersResponse>('/api/tenders');
    return response.data;
  },

  /**
   * Rank tenders based on company description
   */
  rankTenders: async (request: RankingRequest): Promise<RankingResponse> => {
    const response = await api.post<RankingResponse>('/api/rank', request);
    return response.data;
  },

  /**
   * Submit user feedback for a tender
   */
  submitFeedback: async (request: FeedbackRequest): Promise<FeedbackResponse> => {
    const response = await api.post<FeedbackResponse>('/api/feedback', request);
    return response.data;
  },
};

/**
 * Generate MD5 hash of a string (for company_description_hash)
 */
export const generateHash = async (text: string): Promise<string> => {
  const encoder = new TextEncoder();
  const data = encoder.encode(text);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  return hashHex;
};
