import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

async function enableMocking() {
  // Only enable MSW in development mode when ?mock=true query parameter is present
  if (import.meta.env.DEV && typeof window !== 'undefined' && window.location.search.includes('mock=true')) {
    const { worker } = await import('./mocks/browser');
    return worker.start({
      onUnhandledRequest: 'bypass',
    });
  }
}

enableMocking()
  .catch((err) => {
    console.warn('MSW browser worker skipped:', err);
  })
  .finally(() => {
    ReactDOM.createRoot(document.getElementById('root')!).render(
      <React.StrictMode>
        <App />
      </React.StrictMode>
    );
  });
