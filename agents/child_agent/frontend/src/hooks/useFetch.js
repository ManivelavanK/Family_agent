import { useState, useEffect, useCallback } from 'react';
import { useApp } from '../context/AppContext';

/**
 * Generic data fetching hook with auto-refresh when global refresh token changes.
 */
export function useFetch(fetchFn, deps = []) {
  const { refreshToken } = useApp();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchFn();
      setData(result);
    } catch (e) {
      setError(e?.response?.data?.detail || e.message || 'Unknown error');
    } finally {
      setLoading(false);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [refreshToken, ...deps]);

  useEffect(() => { load(); }, [load]);

  return { data, loading, error, reload: load };
}

/**
 * Convenience hook for async mutations (create/update/delete).
 */
export function useMutation(mutFn, { onSuccess } = {}) {
  const [loading, setLoading] = useState(false);
  const [error, setError]   = useState(null);

  const mutate = useCallback(async (...args) => {
    setLoading(true);
    setError(null);
    try {
      const result = await mutFn(...args);
      if (onSuccess) await onSuccess(result);
      return result;
    } catch (e) {
      setError(e?.response?.data?.detail || e.message || 'Unknown error');
      throw e;
    } finally {
      setLoading(false);
    }
  }, [mutFn, onSuccess]);

  return { mutate, loading, error };
}
