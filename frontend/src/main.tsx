import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// Log environment configuration (non-blocking — uses defaults from apiClient.ts)
if (import.meta.env.DEV) {
  console.log('Environment configuration:', {
    apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000 (default)',
    apiTimeout: `${import.meta.env.VITE_API_TIMEOUT || '60000'}ms`,
  });
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
