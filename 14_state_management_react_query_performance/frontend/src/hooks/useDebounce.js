import { useState, useEffect } from 'react';

/**
 * Custom hook to debounce values (e.g. search queries) to avoid
 * hammering the server with API requests on every keystroke.
 *
 * @param {any} value Value to debounce
 * @param {number} delay Milliseconds to delay
 * @returns {any} Debounced value
 */
export function useDebounce(value, delay = 400) {
  const [debouncedValue, setDebouncedValue] = useState(value);

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
