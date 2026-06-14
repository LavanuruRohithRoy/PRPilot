import { useCallback, useEffect, useState } from 'react';

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

interface UseApiReturn<T> extends UseApiState<T> {
  refetch: () => void;
}

/**
 * Generic hook for fetching data from the API.
 * @param fetcher — async function that returns the data
 * @param deps — optional dependency array to trigger re-fetch (like useEffect)
 */
export function useApi<T>(
  fetcher: () => Promise<T>,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  deps: any[] = [],
): UseApiReturn<T> {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: true,
    error: null,
  });

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const stableFetcher = useCallback(fetcher, deps);

  const run = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const data = await stableFetcher();
      setState({ data, loading: false, error: null });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      setState({ data: null, loading: false, error: message });
    }
  }, [stableFetcher]);

  useEffect(() => {
    run();
  }, [run]);

  return { ...state, refetch: run };
}

/**
 * Simple lazy hook — returns a trigger function rather than auto-fetching.
 */
export function useLazyApi<TArgs extends unknown[], TResult>(
  fetcher: (...args: TArgs) => Promise<TResult>,
): {
  execute: (...args: TArgs) => Promise<TResult | null>;
  loading: boolean;
  error: string | null;
  data: TResult | null;
} {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<TResult | null>(null);

  const execute = useCallback(
    async (...args: TArgs): Promise<TResult | null> => {
      setLoading(true);
      setError(null);
      try {
        const result = await fetcher(...args);
        setData(result);
        return result;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Unknown error';
        setError(message);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [fetcher],
  );

  return { execute, loading, error, data };
}
