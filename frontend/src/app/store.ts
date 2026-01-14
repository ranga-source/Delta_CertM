/**
 * Redux Store Configuration
 * =========================
 * Central state management using Redux Toolkit.
 * 
 * Store Slices:
 * - tenant: Current tenant context
 * - ui: UI state (sidebar, theme, etc.)
 * 
 * Future slices:
 * - auth: Keycloak authentication state
 * - notifications: Toast notifications queue
 */

import { configureStore } from '@reduxjs/toolkit';
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';
import tenantReducer from './slices/tenantSlice';
import uiReducer from './slices/uiSlice';

/**
 * Configure Redux store with all reducers
 */
export const store = configureStore({
  reducer: {
    tenant: tenantReducer,
    ui: uiReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore these action types for serialization check
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    }),
});

/**
 * Type definitions for TypeScript support
 */
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

/**
 * Typed hooks for use throughout the app
 * 
 * Usage:
 *   const dispatch = useAppDispatch();
 *   const tenantId = useAppSelector(state => state.tenant.currentTenantId);
 */
export const useAppDispatch: () => AppDispatch = useDispatch;
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;


