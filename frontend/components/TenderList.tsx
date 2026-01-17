'use client';

import { RankedTender } from '@/lib/types';
import TenderCard from './TenderCard';
import { AlertCircle } from 'lucide-react';

interface TenderListProps {
  tenders: RankedTender[];
  onFeedback: (tenderId: string, feedback: 'positive' | 'negative') => void;
  processingTime?: number;
}

export default function TenderList({ tenders, onFeedback, processingTime }: TenderListProps) {
  if (!tenders || tenders.length === 0) {
    return (
      <div className="w-full max-w-4xl mx-auto p-6">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 flex items-start gap-4">
          <AlertCircle className="h-6 w-6 text-blue-600 flex-shrink-0 mt-1" />
          <div>
            <h3 className="text-lg font-semibold text-blue-900 mb-2">
              No Results Yet
            </h3>
            <p className="text-blue-800">
              Enter your company description above and click "Find Matching Tenders" to see AI-ranked results.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-4xl mx-auto p-6">
      {/* Results header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Top {tenders.length} Matching Tenders
        </h2>
        {processingTime && (
          <p className="text-sm text-gray-600">
            Ranked in {processingTime.toFixed(0)}ms using AI embeddings
          </p>
        )}
      </div>

      {/* Tender cards */}
      <div className="space-y-4">
        {tenders.map((tender) => (
          <TenderCard
            key={tender.id}
            tender={tender}
            onFeedback={onFeedback}
          />
        ))}
      </div>

      {/* Footer message */}
      <div className="mt-8 p-4 bg-gray-50 rounded-lg text-center">
        <p className="text-sm text-gray-600">
          Rate the relevance of results using 👍 or 👎 to improve future recommendations
        </p>
      </div>
    </div>
  );
}
