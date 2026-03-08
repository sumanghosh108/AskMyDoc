import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// Environment variable validation
function validateEnvironment() {
  const requiredVars = {
    VITE_API_BASE_URL: import.meta.env.VITE_API_BASE_URL,
    VITE_API_TIMEOUT: import.meta.env.VITE_API_TIMEOUT,
  };

  const missing: string[] = [];
  const invalid: string[] = [];

  // Check for missing variables
  Object.entries(requiredVars).forEach(([key, value]) => {
    if (!value) {
      missing.push(key);
    }
  });

  // Validate VITE_API_BASE_URL format
  if (requiredVars.VITE_API_BASE_URL) {
    try {
      new URL(requiredVars.VITE_API_BASE_URL);
    } catch {
      invalid.push(`VITE_API_BASE_URL: Invalid URL format`);
    }
  }

  // Validate VITE_API_TIMEOUT is a positive number
  if (requiredVars.VITE_API_TIMEOUT) {
    const timeout = Number(requiredVars.VITE_API_TIMEOUT);
    if (isNaN(timeout) || timeout <= 0) {
      invalid.push(`VITE_API_TIMEOUT: Must be a positive number`);
    }
  }

  // Report errors
  if (missing.length > 0 || invalid.length > 0) {
    const errors: string[] = [];
    
    if (missing.length > 0) {
      errors.push(`Missing required environment variables: ${missing.join(', ')}`);
    }
    
    if (invalid.length > 0) {
      errors.push(`Invalid environment variables:\n  ${invalid.join('\n  ')}`);
    }

    console.error('Environment Configuration Error:\n', errors.join('\n'));
    throw new Error(
      `Environment configuration error. Please check your .env.local file.\n${errors.join('\n')}`
    );
  }

  // Log successful configuration in development
  if (import.meta.env.DEV) {
    console.log('Environment configuration validated:', {
      apiBaseUrl: requiredVars.VITE_API_BASE_URL,
      apiTimeout: `${requiredVars.VITE_API_TIMEOUT}ms`,
    });
  }
}

// Validate environment before rendering
validateEnvironment();

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
