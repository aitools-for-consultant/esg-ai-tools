import React from 'react';
import { ResearchBrief as ResearchBriefType } from '../types/types';
import PaperCard from './PaperCard';

interface ResearchBriefProps {
  brief: ResearchBriefType;
  onClose: () => void;
}

/**
 * Component to display a generated research brief
 */
const ResearchBrief: React.FC<ResearchBriefProps> = ({ brief, onClose }) => {
  // Format the brief content with proper section styling
  const formatBriefContent = (content: string) => {
    // Add styling for sections
    let formattedContent = content;
    
    const sections = [
      'Executive Summary', 
      'Key Themes and Findings', 
      'Research Gaps', 
      'Practical Implications', 
      'Recommended Next Steps'
    ];
    
    sections.forEach(section => {
      const regex = new RegExp(`(${section}:?)`, 'gi');
      formattedContent = formattedContent.replace(regex, '<h3>$1</h3>');
    });
    
    // Split by paragraphs and wrap in <p> tags
    formattedContent = formattedContent
      .split('\n\n')
      .map(para => {
        if (para.includes('<h3>')) return para;
        return `<p>${para}</p>`;
      })
      .join('');
    
    return formattedContent;
  };

  // Format date for display
  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    } catch (error) {
      return dateString;
    }
  };

  return (
    <div style={{
      backgroundColor: '#fff',
      borderRadius: '8px',
      padding: '24px',
      boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
      margin: '32px 0',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h2 style={{ margin: 0 }}>Research Brief</h2>
        <button
          onClick={onClose}
          style={{
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            fontSize: '24px',
            color: '#6c757d',
            padding: '4px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          &times;
        </button>
      </div>
      
      <div style={{ 
        backgroundColor: '#f8f9fa',
        padding: '16px',
        borderRadius: '4px',
        marginBottom: '24px'
      }}>
        <div style={{ marginBottom: '8px' }}>
          <strong>Query:</strong> {brief.query}
        </div>
        <div>
          <strong>Generated:</strong> {formatDate(brief.timestamp)}
        </div>
      </div>

      <div 
        style={{ lineHeight: '1.6', fontSize: '16px', marginBottom: '32px' }}
        dangerouslySetInnerHTML={{ __html: formatBriefContent(brief.brief) }}
      ></div>
      
      {brief.papers && brief.papers.length > 0 && (
        <div>
          <h3 style={{ marginBottom: '16px', borderBottom: '1px solid #dee2e6', paddingBottom: '8px' }}>
            Papers Referenced
          </h3>
          <div>
            {brief.papers.map((paperInfo, index) => (
              <div 
                key={index}
                style={{
                  marginBottom: '16px',
                  padding: '16px',
                  backgroundColor: '#f8f9fa',
                  borderRadius: '4px',
                  border: '1px solid #e9ecef'
                }}
              >
                <h4 style={{ margin: '0 0 8px' }}>{paperInfo.title}</h4>
                <div style={{ fontSize: '0.9em', marginBottom: '8px' }}>
                  <strong>Authors:</strong> {paperInfo.authors.join(', ')}
                </div>
                <p>{paperInfo.summary}</p>
                
                {paperInfo.key_findings && paperInfo.key_findings.length > 0 && (
                  <div style={{ marginTop: '8px' }}>
                    <strong>Key Findings:</strong>
                    <ul style={{ margin: '4px 0 0 0', paddingLeft: '20px' }}>
                      {paperInfo.key_findings.map((finding, i) => (
                        <li key={i}>{finding}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                <div style={{ marginTop: '12px' }}>
                  <a 
                    href={paperInfo.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    style={{
                      color: '#007bff',
                      textDecoration: 'none',
                    }}
                  >
                    View Source
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div style={{ marginTop: '32px', textAlign: 'right' }}>
        <button
          onClick={onClose}
          style={{
            padding: '8px 16px',
            backgroundColor: '#6c757d',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '14px',
          }}
        >
          Close
        </button>
      </div>
    </div>
  );
};

export default ResearchBrief;