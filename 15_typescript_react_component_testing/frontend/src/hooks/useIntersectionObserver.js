import { useEffect, useRef } from 'react';

/**
 * Custom hook to detect when an element intersects the viewport.
 * Perfect for infinite scroll sentinels and lazy image triggers.
 *
 * @param {Function} onIntersect Callback invoked when element becomes visible
 * @param {Object} options IntersectionObserver configuration
 * @returns {React.MutableRefObject} Ref to attach to target sentinel DOM element
 */
export function useIntersectionObserver(onIntersect, { threshold = 0.1, root = null, rootMargin = '150px', enabled = true } = {}) {
  const targetRef = useRef(null);

  useEffect(() => {
    if (!enabled) return;

    const target = targetRef.current;
    if (!target) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            onIntersect();
          }
        });
      },
      {
        threshold,
        root,
        rootMargin,
      }
    );

    observer.observe(target);

    return () => {
      observer.unobserve(target);
      observer.disconnect();
    };
  }, [onIntersect, enabled, threshold, root, rootMargin]);

  return targetRef;
}
