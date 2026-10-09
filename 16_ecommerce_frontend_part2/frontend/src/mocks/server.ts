import { setupServer } from 'msw/node';
import { handlers } from './handlers';

/**
 * MSW Server instance for Vitest / Node test environment.
 * Intercepts outbound requests during test execution.
 */
export const server = setupServer(...handlers);
