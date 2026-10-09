import { useState, useEffect } from 'react';

/**
 * Generic debounce hook.
 * Delay updates to a value until a specified timeout has passed.
 * Demonstrates generic typing in custom React hooks: <T>(value: T, delay: number): T
 */
export function useDebounce<T>(value: T, delay: number = 400): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

export default useDebounce;
