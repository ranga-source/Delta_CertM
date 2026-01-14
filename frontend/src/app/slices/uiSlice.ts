/**
 * UI Slice
 * ========
 * Manages UI state across the application.
 * 
 * State:
 * - sidebarCollapsed: Whether sidebar is collapsed
 * - loading: Global loading state
 * 
 * Actions:
 * - toggleSidebar: Toggle sidebar collapse
 * - setSidebarCollapsed: Set sidebar state explicitly
 * - setLoading: Set global loading state
 */

import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface UIState {
  sidebarCollapsed: boolean;
  loading: boolean;
}

const initialState: UIState = {
  sidebarCollapsed: window.innerWidth < 768, // Collapsed on mobile by default
  loading: false,
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    /**
     * Toggle sidebar collapsed state
     */
    toggleSidebar: (state) => {
      state.sidebarCollapsed = !state.sidebarCollapsed;
    },
    
    /**
     * Set sidebar collapsed state explicitly
     */
    setSidebarCollapsed: (state, action: PayloadAction<boolean>) => {
      state.sidebarCollapsed = action.payload;
    },
    
    /**
     * Set global loading state
     */
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
  },
});

export const { toggleSidebar, setSidebarCollapsed, setLoading } = uiSlice.actions;
export default uiSlice.reducer;


