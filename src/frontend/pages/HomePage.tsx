import React, { useState, useEffect, useCallback } from 'react';
import SearchBar from '../components/SearchBar';
import PaperCard from '../components/PaperCard';
import ResearchBrief from '../components/ResearchBrief';
import SystemStatus from '../components/SystemStatus';
import { useApiGet, useApiMutation } from '../hooks/useApi';
import { getSystemStatus, getPapers, searchPapers, generateBrief } from '../services/api';
import { Paper, ResearchBrief as ResearchBriefType, PaperFilterParams } from '../types/types';

/**
 * Main home page of the ESG & Finance AI Research Assistant
 */
const HomePage: React.FC = () => {
  // State for search query and paper filtering
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [filterParams, setFilterParams] = useState<PaperFilterParams>({
    limit: 10,
    offset: 0,
  });
  
  // State for paper detail view
  const [selectedPaper, setSelectedPaper] = useState<Paper | null>(null);
  
  // State for research brief
  const [researchBrief, setResearchBrief] = useState<ResearchBriefType | null>(null);
  
  // Fetch system status
  const [statusState, refreshStatus] = useApiGet(getSystemStatus, undefined, []);
  
  // Fetch papers
  const [papersState, fetchPapers] = useApiGet(
    () => getPapers(filterParams),
    [],
    [JSON.stringify(filterParams)]
  );
  
  // Search papers mutation
  const [searchState, searchPapersMutation] = useApiMutation(
    (query: string) => searchPapers({ query, limit: 10 })
  );
  
  // Generate brief mutation
  const [briefState, generateBriefMutation] = useApiMutation(generateBrief);
  
  // Handle search submission
  const handleSearch = useCallback(async (query: string) => {
    setSearchQuery(query);
    const results = await searchPapersMutation(query);
    if (results) {
      // Reset any existing research brief
      setResearchBrief(null);
    }
  }, [searchPapersMutation]);
  
  // Handle research brief generation
  const handleGenerateBrief = useCallback(async (query: string) => {
    setSearchQuery(query);
    const brief = await generateBriefMutation(query);
    if (brief) {
      setResearchBrief(brief);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }, [generateBriefMutation]);
  
  // Handle paper selection
  const handlePaperClick = useCallback((paper: Paper) => {
    setSelectedPaper(paper);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);
  
  // Handle closing paper detail view
  const handleCloseDetail = useCallback(() => {
    setSelectedPaper(null);
  }, []);
  
  // Handle closing research brief
  const handleCloseBrief = useCallback(() => {
    setResearchBrief(null);
  }, []);
  
  // Get current papers to display
  const currentPapers = searchState.data || papersState.data || [];
  
  // Check if there's any loading state
  const isLoading = papersState.loading || searchState.loading || briefState.loading;
  
  // Display any errors
  const error = papersState.error || searchState.error || briefState.error;

  return (
    <div style={{ 
      maxWidth: '1200px', 
      margin: '0 auto', 
      padding: '32px 16px',
      fontFamily: 'Arial, sans-serif',
    }}>
      <header style={{ marginBottom: '32px', textAlign: 'center' }}>
        <h1 style={{ 
          color: '#2c3e50', 
          marginBottom: '8px',
          fontSize: '32px'
        }}>
          ESG & Finance AI Research Assistant
        </h1>
        <p style={{ color: '#7f8c8d', fontSize: '18px' }}>
          Automated research paper collection, analysis, and insight generation
        </p>
      </header>

      {statusState.data && (
        <SystemStatus 
          status={statusState.data} 
          onRefresh={refreshStatus}
        />
      )}
      
      <SearchBar 
        onSearch={handleSearch}
        onGenerateBrief={handleGenerateBrief}
        isLoading={isLoading}
      />
      
      {error && (
        <div style={{
          padding: '12px',
          backgroundColor: '#f8d7da',
          color: '#721c24',
          borderRadius: '4px',
          marginBottom: '24px',
        }}>
          <strong>Error: </strong>{error}
        </div>
      )}
      
      {researchBrief && (
        <ResearchBrief 
          brief={researchBrief}
          onClose={handleCloseBrief}
        />
      )}
      
      {selectedPaper ? (
        <div>
          <div style={{ marginBottom: '16px' }}>
            <button
              onClick={handleCloseDetail}
              style={{
                background: 'none',
                border: 'none',
                color: '#007bff',
                cursor: 'pointer',
                padding: '8px 0',
                display: 'flex',
                alignItems: 'center',
                fontSize: '16px',
              }}
            >
              ← Back to results
            </button>
          </div>
          
          <PaperCard 
            paper={selectedPaper}
            showSummary={true}
          />
        </div>
      ) : (
        <div>
          {searchQuery && (
            <h2 style={{ marginBottom: '24px', color: '#2c3e50', fontSize: '24px' }}>
              {searchState.data ? 'Search Results' : 'Recent Papers'}
              {searchState.data && ` for "${searchQuery}"`}
            </h2>
          )}
          
          {isLoading && !currentPapers.length ? (
            <div style={{ 
              display: 'flex', 
              justifyContent: 'center', 
              padding: '40px 0' 
            }}>
              <div style={{ 
                width: '50px', 
                height: '50px', 
                border: '5px solid rgba(0,0,0,0.1)',
                borderTop: '5px solid #007bff',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite',
              }} />
            </div>
          ) : currentPapers.length === 0 ? (
            <div style={{ 
              textAlign: 'center', 
              padding: '40px 0',
              color: '#6c757d' 
            }}>
              <h3>No papers found</h3>
              <p>Try a different search query or collect new papers</p>
            </div>
          ) : (
            <div>
              {currentPapers.map((paper) => (
                <PaperCard
                  key={paper.id}
                  paper={paper}
                  onClick={handlePaperClick}
                />
              ))}
              
              {/* Pagination controls would go here */}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default HomePage;