import React from 'react';
import { SystemStatus as SystemStatusType } from '../types/types';
import { useApiMutation } from '../hooks/useApi';
import { startScheduler, stopScheduler, collectPapers, processPapers } from '../services/api';

interface SystemStatusProps {
  status: SystemStatusType;
  onRefresh: () => void;
}

/**
 * Component to display system status and scheduler controls
 */
const SystemStatus: React.FC<SystemStatusProps> = ({ status, onRefresh }) => {
  const [startState, startSchedulerFn] = useApiMutation(startScheduler);
  const [stopState, stopSchedulerFn] = useApiMutation(stopScheduler);
  const [collectState, collectPapersFn] = useApiMutation(collectPapers);
  const [processState, processPapersFn] = useApiMutation(() => processPapers(10));

  // Format date for display
  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Never';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    } catch (error) {
      return dateString;
    }
  };

  // Handle start scheduler
  const handleStart = async () => {
    await startSchedulerFn();
    onRefresh();
  };

  // Handle stop scheduler
  const handleStop = async () => {
    await stopSchedulerFn();
    onRefresh();
  };

  // Handle collect papers
  const handleCollect = async () => {
    await collectPapersFn();
    onRefresh();
  };

  // Handle process papers
  const handleProcess = async () => {
    await processPapersFn();
    onRefresh();
  };

  const isAnyLoading = startState.loading || stopState.loading || collectState.loading || processState.loading;

  return (
    <div style={{
      backgroundColor: '#fff',
      borderRadius: '8px',
      padding: '24px',
      boxShadow: '0 2px 5px rgba(0,0,0,0.05)',
      marginBottom: '32px',
    }}>
      <h2 style={{ marginTop: 0, marginBottom: '16px', color: '#343a40' }}>
        System Status
      </h2>
      
      <div style={{ marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
          <div style={{ 
            width: '12px', 
            height: '12px', 
            borderRadius: '50%', 
            backgroundColor: status.running ? '#28a745' : '#dc3545',
            marginRight: '8px'
          }}></div>
          <span style={{ fontWeight: 'bold' }}>
            Scheduler: {status.running ? 'Running' : 'Stopped'}
          </span>
        </div>
        
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', marginTop: '16px' }}>
          <button
            onClick={handleStart}
            disabled={status.running || isAnyLoading}
            style={{
              padding: '8px 16px',
              backgroundColor: status.running ? '#6c757d' : '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: status.running || isAnyLoading ? 'not-allowed' : 'pointer',
              opacity: status.running || isAnyLoading ? 0.7 : 1,
              fontSize: '14px',
              fontWeight: 'bold',
            }}
          >
            Start Scheduler
          </button>
          
          <button
            onClick={handleStop}
            disabled={!status.running || isAnyLoading}
            style={{
              padding: '8px 16px',
              backgroundColor: !status.running ? '#6c757d' : '#dc3545',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: !status.running || isAnyLoading ? 'not-allowed' : 'pointer',
              opacity: !status.running || isAnyLoading ? 0.7 : 1,
              fontSize: '14px',
              fontWeight: 'bold',
            }}
          >
            Stop Scheduler
          </button>
          
          <button
            onClick={handleCollect}
            disabled={isAnyLoading}
            style={{
              padding: '8px 16px',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: isAnyLoading ? 'not-allowed' : 'pointer',
              opacity: isAnyLoading ? 0.7 : 1,
              fontSize: '14px',
              fontWeight: 'bold',
            }}
          >
            Collect Papers Now
          </button>
          
          <button
            onClick={handleProcess}
            disabled={isAnyLoading}
            style={{
              padding: '8px 16px',
              backgroundColor: '#17a2b8',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: isAnyLoading ? 'not-allowed' : 'pointer',
              opacity: isAnyLoading ? 0.7 : 1,
              fontSize: '14px',
              fontWeight: 'bold',
            }}
          >
            Process Papers Now
          </button>
        </div>
      </div>
      
      <div style={{ 
        backgroundColor: '#f8f9fa',
        padding: '16px',
        borderRadius: '4px',
        marginBottom: '16px'
      }}>
        <h3 style={{ margin: '0 0 12px', fontSize: '18px' }}>Last Run Statistics</h3>
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          <div>
            <h4 style={{ margin: '0 0 8px', fontSize: '16px' }}>Collection</h4>
            <div style={{ fontSize: '14px', color: '#495057' }}>
              <div><strong>Last Run:</strong> {formatDate(status.last_collection)}</div>
              {status.collection_stats && (
                <>
                  <div><strong>Total Collected:</strong> {status.collection_stats.total} papers</div>
                  <div><strong>From arXiv:</strong> {status.collection_stats.arxiv} papers</div>
                  <div><strong>From SSRN:</strong> {status.collection_stats.ssrn} papers</div>
                </>
              )}
            </div>
          </div>
          
          <div>
            <h4 style={{ margin: '0 0 8px', fontSize: '16px' }}>Processing</h4>
            <div style={{ fontSize: '14px', color: '#495057' }}>
              <div><strong>Last Run:</strong> {formatDate(status.last_processing)}</div>
              {status.processing_stats && (
                <>
                  <div><strong>Summarized:</strong> {status.processing_stats.summarized} papers</div>
                  <div><strong>Embedded:</strong> {status.processing_stats.embedded} papers</div>
                  <div><strong>Errors:</strong> {status.processing_stats.errors}</div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
      
      {isAnyLoading && (
        <div style={{
          padding: '12px',
          backgroundColor: '#e2f3fc',
          color: '#0c5460',
          borderRadius: '4px',
          marginTop: '16px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
        }}>
          <div style={{ 
            width: '16px', 
            height: '16px', 
            border: '3px solid rgba(12,84,96,0.2)',
            borderTop: '3px solid #0c5460',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
          }} />
          <span>Operation in progress...</span>
        </div>
      )}
      
      {(startState.error || stopState.error || collectState.error || processState.error) && (
        <div style={{
          padding: '12px',
          backgroundColor: '#f8d7da',
          color: '#721c24',
          borderRadius: '4px',
          marginTop: '16px',
        }}>
          <strong>Error: </strong>
          {startState.error || stopState.error || collectState.error || processState.error}
        </div>
      )}
    </div>
  );
};

export default SystemStatus;