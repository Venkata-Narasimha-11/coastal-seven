import { setupWorker } from 'msw/browser';
import { handlers } from './handlers';

/**
 * MSW Worker instance for client-side browser mocking.
 */
export const worker = setupWorker(...handlers);
