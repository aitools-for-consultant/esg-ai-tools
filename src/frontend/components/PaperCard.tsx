import React from 'react';
import { Paper } from '../types/types';

interface PaperCardProps {
  paper: Paper;
  onClick?: (paper: Paper) => void;
  showSummary?: boolean;
}

/**
 * Component to display a research paper card
 */
const PaperCard: React.FC<PaperCardProps> = ({ paper, onClick, showSummary = false }) => {
  // Format the publication date
  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString();
    } catch (error) {
      return dateString;
    }
  };

  // Handle click on the card
  const handleClick = () => {
    if (onClick) {
      onClick(paper);
    }
  };

  // Format authors list
  const formatAuthors = (authors: string[] | string) => {
    if (Array.isArray(authors)) {
      return authors.join(', ');
    }
    return authors;
  };

  return (
    <div 
      className="paper-card"
      onClick={handleClick}
      style={{
        border: '1px solid #ddd',
        borderRadius: '8px',
        padding: '16px',
        marginBottom: '16px',
        cursor: onClick ? 'pointer' : 'default',
        transition: 'box-shadow 0.3s ease',
        boxShadow: '0 2px 5px rgba(0,0,0,0.05)',
        backgroundColor: '#fff',
      }}
    >
      <h3 style={{ margin: '0 0 8px' }}>{paper.title}</h3>
      
      <div style={{ fontSize: '0.9em', color: '#555', marginBottom: '12px' }}>
        <span>
          <strong>Authors:</strong> {formatAuthors(paper.authors)}
        </span>
        <span style={{ marginLeft: '12px' }}>
          <strong>Published:</strong> {formatDate(paper.published_date)}
        </span>
        {paper.similarity !== undefined && (
          <span style={{ marginLeft: '12px', color: '#007bff' }}>
            <strong>Relevance:</strong> {Math.round(paper.similarity * 100)}%
          </span>
        )}
      </div>

      {paper.categories && (
        <div style={{ marginBottom: '12px' }}>
          {Array.isArray(paper.categories) ? paper.categories.map((category, index) => (
            <span
              key={index}
              style={{
                display: 'inline-block',
                backgroundColor: '#f0f0f0',
                padding: '4px 8px',
                borderRadius: '4px',
                fontSize: '0.8em',
                marginRight: '6px',
                marginBottom: '6px'
              }}
            >
              {category}
            </span>
          )) : paper.categories}
        </div>
      )}
      
      <p style={{ margin: '12px 0', lineHeight: '1.5' }}>{paper.abstract}</p>
      
      {showSummary && paper.summary && (
        <div style={{ marginTop: '16px', borderTop: '1px solid #eee', paddingTop: '16px' }}>
          <h4 style={{ margin: '0 0 8px' }}>Summary</h4>
          <p>{paper.summary.summary}</p>
          
          <div style={{ display: 'flex', marginTop: '12px', gap: '16px' }}>
            <div style={{ flex: 1 }}>
              <div style={{ 
                height: '6px', 
                backgroundColor: '#e9ecef', 
                borderRadius: '3px',
                overflow: 'hidden'
              }}>
                <div style={{ 
                  width: `${paper.summary.esg_relevance_score}%`, 
                  height: '100%', 
                  backgroundColor: '#28a745',
                  borderRadius: '3px'
                }}></div>
              </div>
              <div style={{ fontSize: '0.8em', marginTop: '4px' }}>
                ESG Relevance: {paper.summary.esg_relevance_score}%
              </div>
            </div>
            
            <div style={{ flex: 1 }}>
              <div style={{ 
                height: '6px', 
                backgroundColor: '#e9ecef', 
                borderRadius: '3px',
                overflow: 'hidden'
              }}>
                <div style={{ 
                  width: `${paper.summary.finance_relevance_score}%`, 
                  height: '100%', 
                  backgroundColor: '#007bff',
                  borderRadius: '3px'
                }}></div>
              </div>
              <div style={{ fontSize: '0.8em', marginTop: '4px' }}>
                Finance Relevance: {paper.summary.finance_relevance_score}%
              </div>
            </div>
          </div>
          
          {paper.summary.key_findings && (
            <div style={{ marginTop: '12px' }}>
              <h4 style={{ margin: '0 0 8px' }}>Key Findings</h4>
              <ul style={{ paddingLeft: '20px', margin: '0' }}>
                {Array.isArray(paper.summary.key_findings) 
                  ? paper.summary.key_findings.map((finding, index) => (
                      <li key={index}>{finding}</li>
                    ))
                  : <li>{paper.summary.key_findings}</li>
                }
              </ul>
            </div>
          )}
          
          {paper.summary.keywords && (
            <div style={{ marginTop: '12px' }}>
              <h4 style={{ margin: '0 0 8px' }}>Keywords</h4>
              <div>
                {Array.isArray(paper.summary.keywords) 
                  ? paper.summary.keywords.map((keyword, index) => (
                      <span
                        key={index}
                        style={{
                          display: 'inline-block',
                          backgroundColor: '#e9ecef',
                          padding: '4px 8px',
                          borderRadius: '4px',
                          fontSize: '0.8em',
                          marginRight: '6px',
                          marginBottom: '6px'
                        }}
                      >
                        {keyword}
                      </span>
                    ))
                  : paper.summary.keywords
                }
              </div>
            </div>
          )}
        </div>
      )}
      
      <div style={{ marginTop: '16px' }}>
        <a 
          href={paper.url} 
          target="_blank" 
          rel="noopener noreferrer"
          style={{
            color: '#007bff',
            textDecoration: 'none',
            marginRight: '16px'
          }}
          onClick={(e) => e.stopPropagation()}
        >
          View Source
        </a>
        {paper.pdf_url && (
          <a 
            href={paper.pdf_url} 
            target="_blank" 
            rel="noopener noreferrer"
            style={{
              color: '#dc3545',
              textDecoration: 'none'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            Download PDF
          </a>
        )}
      </div>
    </div>
  );
};

export default PaperCard;