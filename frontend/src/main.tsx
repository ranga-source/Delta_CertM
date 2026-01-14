/**
 * Application Entry Point
 * =======================
 * Bootstraps the React application with all providers.
 * 
 * Providers (in order):
 * 1. Redux Provider - State management
 * 2. React Query Provider - Server state
 * 3. Ant Design ConfigProvider - Theme
 * 4. Router Provider - Routing
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider as ReduxProvider } from 'react-redux';
import { QueryClientProvider } from '@tanstack/react-query';
import App from './App';
import { store } from './app/store';
import { queryClient } from './services/queryClient';
import { ThemeProvider } from './context/ThemeContext';

// Import global styles
import './assets/styles/variables.css';
import './assets/styles/theme.css';
import './assets/styles/responsive.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ReduxProvider store={store}>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider>
          <App />
        </ThemeProvider>
      </QueryClientProvider>
    </ReduxProvider>
  </React.StrictMode>
);
