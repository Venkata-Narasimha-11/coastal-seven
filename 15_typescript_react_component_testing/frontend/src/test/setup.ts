import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach, beforeAll, afterAll } from 'vitest';
import { server } from '../mocks/server';

// Start MSW server before all test suites run
beforeAll(() => {
  server.listen({ onUnhandledRequest: 'bypass' });
});

// Reset MSW handlers and clean up DOM after each individual test
afterEach(() => {
  cleanup();
  server.resetHandlers();
  localStorage.clear();
});

// Clean up and close MSW server after all test suites finish
afterAll(() => {
  server.close();
});
