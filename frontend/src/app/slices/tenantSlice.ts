/**
 * Tenant Slice
 * ============
 * Manages current tenant context for data isolation.
 * 
 * State:
 * - currentTenantId: UUID of the currently selected tenant
 * - tenants: List of available tenants (cached)
 * 
 * Actions:
 * - setCurrentTenant: Switch active tenant
 * - setTenants: Update tenants list
 */

import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { Tenant } from '../../types/models.types';

interface TenantState {
  currentTenantId: string | null;
  tenants: Tenant[];
}

const initialState: TenantState = {
  currentTenantId: localStorage.getItem('currentTenantId') || null,
  tenants: [],
};

const tenantSlice = createSlice({
  name: 'tenant',
  initialState,
  reducers: {
    /**
     * Set the current active tenant
     * Persists to localStorage for session continuity
     */
    setCurrentTenant: (state, action: PayloadAction<string | null>) => {
      state.currentTenantId = action.payload;
      if (action.payload) {
        localStorage.setItem('currentTenantId', action.payload);
      } else {
        localStorage.removeItem('currentTenantId');
      }
    },
    
    /**
     * Update the list of available tenants
     */
    setTenants: (state, action: PayloadAction<Tenant[]>) => {
      state.tenants = action.payload;
      
      // Auto-select first tenant if none selected
      if (!state.currentTenantId && action.payload.length > 0) {
        const firstActiveTenant = action.payload.find(t => t.is_active);
        if (firstActiveTenant) {
          state.currentTenantId = firstActiveTenant.id;
          localStorage.setItem('currentTenantId', firstActiveTenant.id);
        }
      }
    },
  },
});

export const { setCurrentTenant, setTenants } = tenantSlice.actions;
export default tenantSlice.reducer;


