'use client';

import { useState } from 'react';
import CompanyProfileInput from '@/components/CompanyProfileInput';
import TenderList from '@/components/TenderList';
import { tendersApi, generateHash } from '@/lib/api';
import { RankedTender } from '@/lib/types';

export default function Home() {
  const [rankedTenders, setRankedTenders] = useState<RankedTender[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [processingTime, setProcessingTime] = useState<number | undefined>();
  const [companyDescription, setCompanyDescription] = useState<string>('');

  const handleSubmit = async (description: string) => {
    setIsLoading(true);
    setError(null);
    setCompanyDescription(description);

    try {
      const response = await tendersApi.rankTenders({
        company_description: description,
        top_n: 100,
        use_feedback: true,
      });

      setRankedTenders(response.ranked_tenders);
      setProcessingTime(response.processing_time_ms);
    } catch (err: any) {
      console.error('Error ranking tenders:', err);
      setError(err.response?.data?.detail || 'Failed to rank tenders. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFeedback = async (tenderId: string, feedback: 'positive' | 'negative') => {
    try {
      const companyHash = await generateHash(companyDescription);

      await tendersApi.submitFeedback({
        tender_id: tenderId,
        company_description_hash: companyHash,
        feedback: feedback,
        timestamp: new Date().toISOString(),
      });

      console.log(`Feedback submitted: ${feedback} for tender ${tenderId}`);
    } catch (err) {
      console.error('Error submitting feedback:', err);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 py-12 px-4">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Company Profile Input */}
        <CompanyProfileInput onSubmit={handleSubmit} isLoading={isLoading} />

        {/* Error Message */}
        {error && (
          <div className="w-full max-w-4xl mx-auto p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Tender List */}
        <TenderList
          tenders={rankedTenders}
          onFeedback={handleFeedback}
          processingTime={processingTime}
        />
      </div>
    </main>
  );
}
