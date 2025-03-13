/**
 * TypeScript interfaces for the ESG & Finance AI Research Assistant frontend
 */

// Paper interface
export interface Paper {
  id: string;
  title: string;
  abstract: string;
  authors: string[];
  url: string;
  pdf_url: string;
  published_date: string;
  source: string;
  categories: string[];
  retrieved_date: string;
  embedding_id?: string;
  summary?: PaperSummary;
  similarity?: number;
}

// Paper Summary interface
export interface PaperSummary {
  id: number;
  paper_id: string;
  summary: string;
  esg_relevance_score: number;
  finance_relevance_score: number;
  key_findings: string[];
  keywords: string[];
  created_date: string;
}

// Research Brief interface
export interface ResearchBrief {
  query: string;
  papers: PaperInfo[];
  brief: string;
  timestamp: string;
  error?: string;
  message?: string;
}

// Paper info for research brief
export interface PaperInfo {
  title: string;
  authors: string[];
  summary: string;
  key_findings: string[];
  url: string;
}

// System Status interface
export interface SystemStatus {
  running: boolean;
  last_collection: string | null;
  last_processing: string | null;
  collection_stats: CollectionStats;
  processing_stats: ProcessingStats;
}

// Collection Stats interface
export interface CollectionStats {
  arxiv: number;
  ssrn: number;
  total: number;
  timestamp: string;
  error?: string;
}

// Processing Stats interface
export interface ProcessingStats {
  summarized: number;
  embedded: number;
  errors: number;
  timestamp: string;
  error?: string;
}

// Search Query interface
export interface SearchQuery {
  query: string;
  limit?: number;
}

// API response types
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  loading: boolean;
}

// Pagination params
export interface PaginationParams {
  limit: number;
  offset: number;
}

// Paper filter params
export interface PaperFilterParams extends PaginationParams {
  category?: string;
  query?: string;
}