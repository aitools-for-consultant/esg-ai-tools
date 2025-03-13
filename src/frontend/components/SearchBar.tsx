import React, { useState } from 'react';

interface SearchBarProps {
  onSearch: (query: string) => void;
  onGenerateBrief: (query: string) => void;
  isLoading?: boolean;
}

/**
 * Component for searching papers and generating research briefs
 */
const SearchBar: React.FC<SearchBarProps> = ({ onSearch, onGenerateBrief, isLoading = false }) => {
  const [query, setQuery] = useState('');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  const handleGenerateBrief = () => {
    if (query.trim()) {
      onGenerateBrief(query.trim());
    }
  };

  return (
    <div style={{
      backgroundColor: '#f8f9fa',
      padding: '24px',
      borderRadius: '8px',
      marginBottom: '32px',
      boxShadow: '0 2px 5px rgba(0,0,0,0.05)',
    }}>
      <h2 style={{ marginTop: 0, marginBottom: '16px', color: '#343a40' }}>
        ESG & Finance Research Search
      </h2>
      
      <form onSubmit={handleSearch} style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search for ESG and finance research papers..."
          style={{
            flex: '1 0 250px',
            padding: '10px 16px',
            borderRadius: '4px',
            border: '1px solid #ced4da',
            fontSize: '16px',
            minWidth: '200px',
          }}
        />
        
        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            type="submit"
            disabled={isLoading || !query.trim()}
            style={{
              padding: '10px 16px',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: isLoading || !query.trim() ? 'not-allowed' : 'pointer',
              opacity: isLoading || !query.trim() ? 0.7 : 1,
              fontSize: '16px',
              fontWeight: 'bold',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              minWidth: '110px',
              justifyContent: 'center',
            }}
          >
            {isLoading && (
              <div style={{ 
                width: '16px', 
                height: '16px', 
                border: '3px solid rgba(255,255,255,0.3)',
                borderTop: '3px solid white',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite',
              }} />
            )}
            Search
          </button>
          
          <button
            type="button"
            onClick={handleGenerateBrief}
            disabled={isLoading || !query.trim()}
            style={{
              padding: '10px 16px',
              backgroundColor: '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: isLoading || !query.trim() ? 'not-allowed' : 'pointer',
              opacity: isLoading || !query.trim() ? 0.7 : 1,
              fontSize: '16px',
              fontWeight: 'bold',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              minWidth: '160px',
              justifyContent: 'center',
            }}
          >
            {isLoading && (
              <div style={{ 
                width: '16px', 
                height: '16px', 
                border: '3px solid rgba(255,255,255,0.3)',
                borderTop: '3px solid white',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite',
              }} />
            )}
            Generate Brief
          </button>
        </div>
      </form>
      
      <div style={{ marginTop: '12px', fontSize: '14px', color: '#6c757d' }}>
        <p style={{ margin: '4px 0' }}>
          Search for ESG and finance related research by topic, keyword or theme.
        </p>
        <p style={{ margin: '4px 0' }}>
          <strong>Example queries:</strong> "climate finance impact", "ESG reporting standards", "sustainable investing performance"
        </p>
      </div>
      
      <style jsx global>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default SearchBar;