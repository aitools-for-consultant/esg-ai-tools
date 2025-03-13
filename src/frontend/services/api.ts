/**
 * API service for the ESG & Finance AI Research Assistant frontend
 */

import { 
  Paper, PaperFilterParams, ResearchBrief, 
  SystemStatus, CollectionStats, ProcessingStats,
  SearchQuery
} from '../types/types';

// API base URL - should be configurable for different environments
const API_BASE_URL = 'http://localhost:5000/api';

/**
 * Get system status
 * @returns Promise with system status
 */
export const getSystemStatus = async (): Promise<SystemStatus> => {
  const response = await fetch(`${API_BASE_URL}/status`);
  if (!response.ok) {
    throw new Error(`Failed to get system status: ${response.statusText}`);
  }
  return await response.json();
};

/**
 * Start the scheduler
 * @returns Promise with success status
 */
export const startScheduler = async (): Promise<{ success: boolean }> => {
  const response = await fetch(`${API_BASE_URL}/scheduler/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!response.ok) {
    throw new Error(`Failed to start scheduler: ${response.statusText}`);
  }
  return await response.json();
};

/**
 * Stop the scheduler
 * @returns Promise with success status
 */
export const stopScheduler = async (): Promise<{ success: boolean }> => {
  const response = await fetch(`${API_BASE_URL}/scheduler/stop`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!response.ok) {
    throw new Error(`Failed to stop scheduler: ${response.statusText}`);
  }
  return await response.json();
};

/**
 * Get papers with optional filtering
 * @param params Filter parameters
 * @returns Promise with array of papers
 */
export const getPapers = async (params: PaperFilterParams): Promise<Paper[]> => {
  const queryParams = new URLSearchParams();
  if (params.limit) queryParams.append('limit', params.limit.toString());
  if (params.offset) queryParams.append('offset', params.offset.toString());
  if (params.category) queryParams.append('category', params.category);
  if (params.query) queryParams.append('query', params.query);
  
  const response = await fetch(`${API_BASE_URL}/papers?${queryParams}`);
  if (!response.ok) {
    throw new Error(`Failed to get papers: ${response.statusText}`);
  }
  return await response.json();
};

/**
 * Get a specific paper by ID
 * @param paperId Paper ID
 * @returns Promise with paper details
 */
export const getPaperById = async (paperId: string): Promise<Paper> => {
  const response = await fetch(`${API_BASE_URL}/paper/${paperId}`);
  if (!response.ok) {
    throw new Error(`Failed to get paper: ${response.statusText}`);
  }
  return await response.json();
};

/**
 * Collect papers from sources
 * @returns Promise with collection statistics
 */
export const collectPapers = async (): Promise<CollectionStats> => {
  const response = await fetch(`${API_BASE_URL}/collect`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!response.ok) {
    throw new Error(`Failed to collect papers: ${response.statusText}`);
  }
  return await response.json();
};

/**
 * Process papers with AI
 * @param limit Maximum number of papers to process
 * @returns Promise with processing statistics
 */
export const processPapers = async (limit: number = 10): Promise<ProcessingStats> => {
  const response = await fetch(`${API_BASE_URL}/process`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ limit }),
  });
  if (!response.ok) {
    throw new Error(`Failed to process papers: ${response.statusText}`);
  }
  return await response.json();
};

/**
 * Generate a research brief based on a query
 * @param query The research query
 * @returns Promise with research brief
 */
export const generateBrief = async (query: string): Promise<ResearchBrief> => {
  const response = await fetch(`${API_BASE_URL}/brief`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  });
  if (!response.ok) {
    throw new Error(`Failed to generate brief: ${response.statusText}`);
  }
  return await response.json();
};

/**
 * Search for papers by semantic similarity
 * @param searchQuery The search query and limit
 * @returns Promise with array of similar papers
 */
export const searchPapers = async (searchQuery: SearchQuery): Promise<Paper[]> => {
  const response = await fetch(`${API_BASE_URL}/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(searchQuery),
  });
  if (!response.ok) {
    throw new Error(`Failed to search papers: ${response.statusText}`);
  }
  return await response.json();
};