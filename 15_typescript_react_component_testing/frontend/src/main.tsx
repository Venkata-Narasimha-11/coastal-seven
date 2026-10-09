import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

async function enableMocking() {
  // If ?mock=true query parameter is present, activate browser MSW worker
  if (typeof window !== 'undefined' && window.location.search.includes('mock=true')) {
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
