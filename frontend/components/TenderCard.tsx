'use client';

import { ThumbsUp, ThumbsDown, ExternalLink, Calendar, Building2 } from 'lucide-react';
import { RankedTender } from '@/lib/types';
import { useState } from 'react';

interface TenderCardProps {
  tender: RankedTender;
  onFeedback: (tenderId: string, feedback: 'positive' | 'negative') => void;
}

export default function TenderCard({ tender, onFeedback }: TenderCardProps) {
  const [localFeedback, setLocalFeedback] = useState<'positive' | 'negative' | null>(null);

  const handleFeedback = (feedback: 'positive' | 'negative') => {
    setLocalFeedback(feedback);
    onFeedback(tender.id, feedback);
  };

  const relevanceColor =
    tender.relevance_score >= 0.7 ? 'bg-green-100 text-green-800' :
    tender.relevance_score >= 0.5 ? 'bg-yellow-100 text-yellow-800' :
    'bg-gray-100 text-gray-800';

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow border border-gray-200">
      {/* Header with ranking and relevance */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <span className="text-2xl font-bold text-gray-400">#{tender.ranking_position}</span>
          <span className={`px-3 py-1 rounded-full text-sm font-semibold ${relevanceColor}`}>
            {(tender.relevance_score * 100).toFixed(1)}% Match
          </span>
        </div>

        {/* Feedback buttons */}
        <div className="flex gap-2">
          <button
            onClick={() => handleFeedback('positive')}
            className={`p-2 rounded-lg transition-colors ${
              localFeedback === 'positive'
                ? 'bg-green-500 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-green-100 hover:text-green-600'
            }`}
            title="Thumbs up"
          >
            <ThumbsUp className="h-5 w-5" />
          </button>
          <button
            onClick={() => handleFeedback('negative')}
            className={`p-2 rounded-lg transition-colors ${
              localFeedback === 'negative'
                ? 'bg-red-500 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-red-100 hover:text-red-600'
            }`}
            title="Thumbs down"
          >
            <ThumbsDown className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Tender name */}
      <h3 className="text-lg font-semibold text-gray-900 mb-3 line-clamp-2">
        {tender.name}
      </h3>

      {/* Organization */}
      <div className="flex items-center gap-2 text-gray-600 mb-2">
        <Building2 className="h-4 w-4" />
        <span className="text-sm">{tender.organization}</span>
      </div>

      {/* Deadline */}
      <div className="flex items-center gap-2 text-gray-600 mb-4">
        <Calendar className="h-4 w-4" />
        <span className="text-sm">
          Deadline: <span className="font-medium">{tender.submission_deadline}</span>
        </span>
      </div>

      {/* Footer with link */}
      <div className="pt-4 border-t border-gray-200">
        <a
          href={tender.tender_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 text-primary-600 hover:text-primary-700 font-medium text-sm"
        >
          View Full Tender
          <ExternalLink className="h-4 w-4" />
        </a>
        <span className="text-gray-400 text-xs ml-4">
          {tender.files_count} {tender.files_count === 1 ? 'file' : 'files'}
        </span>
      </div>
    </div>
  );
}
