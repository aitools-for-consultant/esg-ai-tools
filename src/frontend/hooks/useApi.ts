import { useState, useEffect, useCallback } from 'react';
import { ApiResponse } from '../types/types';

/**
 * Custom hook for API data fetching
 * @param fetchFn The async function to fetch data
 * @param initialData Optional initial data
 * @param deps Optional dependencies array for fetching
 * @returns API response state and refetch function
 */
export function useApiGet<T, P = void>(
  fetchFn: (params?: P) => Promise<T>,
  initialData?: T,
  deps: any[] = []
): [ApiResponse<T>, (params?: P) => Promise<void>] {
  const [state, setState] = useState<ApiResponse<T>>({
    data: initialData,
    loading: true,
    error: undefined,
  });

  const fetchData = useCallback(async (params?: P) => {
    setState(prev => ({ ...prev, loading: true }));
    try {
      const data = await fetchFn(params);
      setState({ data, loading: false, error: undefined });
    } catch (error) {
      console.error('API error:', error);
      setState({ 
        data: initialData, 
        loading: false, 
        error: error instanceof Error ? error.message : 'Unknown error' 
      });
    }
  }, [fetchFn, initialData]);

  useEffect(() => {
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  return [state, fetchData];
}

/**
 * Custom hook for API mutations (POST, PUT, DELETE)
 * @param mutationFn The async function to call
 * @returns API response state and mutation function
 */
export function useApiMutation<T, P = void>(
  mutationFn: (params: P) => Promise<T>
): [ApiResponse<T>, (params: P) => Promise<T | undefined>] {
  const [state, setState] = useState<ApiResponse<T>>({
    data: undefined,
    loading: false,
    error: undefined,
  });

  const mutate = useCallback(async (params: P): Promise<T | undefined> => {
    setState(prev => ({ ...prev, loading: true }));
    try {
      const data = await mutationFn(params);
      setState({ data, loading: false, error: undefined });
      return data;
    } catch (error) {
      console.error('API mutation error:', error);
      setState({ 
        data: undefined, 
        loading: false, 
        error: error instanceof Error ? error.message : 'Unknown error' 
      });
      return undefined;
    }
  }, [mutationFn]);

  return [state, mutate];
}