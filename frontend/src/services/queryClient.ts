/**
 * React Query Configuration
 * =========================
 * Configures TanStack Query for server state management.
 * 
 * Features:
 * - 5-minute stale time for most queries
 * - Automatic background refetching
 * - Error handling with retry logic
 * - Cache management
 */

import { QueryClient } from '@tanstack/react-query';
import { API_ENDPOINTS } from '../config/api.config';

/**
 * Create and configure React Query client
 */
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Stale time: Data considered fresh for 5 minutes
      staleTime: 5 * 60 * 1000,

      // Cache time: Keep unused data in cache for 10 minutes
      gcTime: 10 * 60 * 1000,

      // Retry failed requests
      retry: 1,

      // Refetch on window focus (disabled for better UX)
      refetchOnWindowFocus: false,

      // Refetch on reconnect
      refetchOnReconnect: true,
    },
    mutations: {
      // Retry failed mutations once
      retry: 1,
    },
  },
});

/**
 * Query Keys
 * ==========
 * Centralized query keys for cache management and invalidation.
 * 
 * Usage:
 *   useQuery({ queryKey: QUERY_KEYS.technologies, queryFn: fetchTechnologies })
 */
export const QUERY_KEYS = {
  // Global Data
  technologies: ['technologies'] as const,
  technology: (id: number) => ['technologies', id] as const,
  countries: ['countries'] as const,
  country: (id: number) => ['countries', id] as const,
  certifications: ['certifications'] as const,
  certification: (id: number) => ['certifications', id] as const,
  regulatoryRules: (filters?: {
    technology_id?: number;
    country_id?: number;
    certification_id?: number;
  }) => ['regulatoryRules', filters] as const,

  // Tenants
  tenants: ['tenants'] as const,
  tenant: (id: string) => ['tenants', id] as const,
  notificationRules: (tenantId: string) => ['notificationRules', tenantId] as const,

  // Devices
  devices: (tenantId: string) => ['devices', tenantId] as const,
  device: (id: string) => ['devices', 'detail', id] as const,
  deviceTechnologies: (id: string) => ['devices', id, 'technologies'] as const,

  // Compliance
  complianceRecords: (tenantId: string, filters?: {
    device_id?: string;
    country_id?: number;
    status?: string;
  }) => ['complianceRecords', tenantId, filters] as const,
  complianceRecord: (id: string) => ['complianceRecords', 'detail', id] as const,
  gapAnalysis: (deviceId: string, countryId: number) =>
    ['gapAnalysis', deviceId, countryId] as const,

  // Tasks
  complianceTasks: (recordId: string) => ['complianceTasks', recordId] as const,
  complianceTask: (taskId: string) => ['complianceTasks', 'detail', taskId] as const,
  complianceTaskNotes: (taskId: string) => ['complianceTaskNotes', taskId] as const,
};

