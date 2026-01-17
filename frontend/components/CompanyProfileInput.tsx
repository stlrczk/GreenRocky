'use client';

import { useState } from 'react';
import { Loader2 } from 'lucide-react';

interface CompanyProfileInputProps {
  onSubmit: (description: string) => void;
  isLoading?: boolean;
}

const EXAMPLE_PROFILE = `GreenWorks Infrastructure Ltd. is a mid-sized environmental services company specializing in the development, maintenance, and revitalization of green areas. The company delivers end-to-end services related to urban greenery, public parks, roadside vegetation, and municipal green infrastructure.

GreenWorks works primarily with public sector clients, including municipalities, road authorities, public institutions, and state-owned entities.

Core Services:
- Maintenance of public green areas (parks, squares, recreational zones)
- Tree cutting and controlled tree removal (sometimes a part of roadworks and construction tenders)
- New plantings (trees, shrubs, lawns)
- Green area revitalization and landscaping projects
- Seasonal vegetation management (mowing, trimming, cleaning)
- Works related to greenery along roads, railways, and public infrastructure

Geographic Focus: Poland`;

export default function CompanyProfileInput({ onSubmit, isLoading }: CompanyProfileInputProps) {
  const [description, setDescription] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (description.trim()) {
      onSubmit(description);
    }
  };

  const loadExample = () => {
    setDescription(EXAMPLE_PROFILE);
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h1 className="text-3xl font-bold mb-2 text-gray-900">Tender Matching System</h1>
      <p className="text-gray-600 mb-6">
        Enter your company description to find the most relevant tenders using AI.
      </p>

      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label htmlFor="company-description" className="block text-sm font-medium text-gray-700 mb-2">
            Company Description
          </label>
          <textarea
            id="company-description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe your company's services, industry, target clients, and geographic focus..."
            className="w-full h-64 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent text-gray-900 placeholder-gray-400"
            disabled={isLoading}
          />
        </div>

        <div className="flex gap-4">
          <button
            type="submit"
            disabled={!description.trim() || isLoading}
            className="flex-1 px-6 py-3 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
          >
            {isLoading ? (
              <>
                <Loader2 className="animate-spin mr-2 h-5 w-5" />
                Finding Matches...
              </>
            ) : (
              'Find Matching Tenders'
            )}
          </button>

          <button
            type="button"
            onClick={loadExample}
            disabled={isLoading}
            className="px-6 py-3 bg-gray-200 text-gray-700 font-semibold rounded-lg hover:bg-gray-300 disabled:bg-gray-100 disabled:cursor-not-allowed transition-colors"
          >
            Load Example
          </button>
        </div>
      </form>
    </div>
  );
}
