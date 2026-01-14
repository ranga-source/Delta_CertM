/**
 * API Configuration
 * =================
 * Centralizes all API endpoints and configuration.
 */

export const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://192.168.80.15:8000/api/v1',
  timeout: 30000, // 30 seconds
};

/**
 * API Endpoints
 * Organized by feature for easy maintenance
 */
export const API_ENDPOINTS = {
  // Global Data
  technologies: '/global/technologies',
  countries: '/global/countries',
  certifications: '/global/certifications',
  globalLabels: '/global/labels',
  regulatoryMatrix: '/global/regulatory-matrix',

  // Tenants
  tenants: '/tenants',
  notificationRules: (tenantId: string) => `/tenants/${tenantId}/notification-rules`,

  // Devices
  devices: '/devices',
  device: (id: string) => `/devices/${id}`,
  deviceTechnologies: (id: string) => `/devices/${id}/technologies`,

  // Compliance
  complianceRecords: '/compliance/records',
  complianceRecord: (id: string) => `/compliance/records/${id}`,
  gapAnalysis: '/compliance/gap-analysis',
  uploadDocument: (recordId: string) => `/compliance/records/${recordId}/document`,
  downloadDocument: (recordId: string) => `/compliance/records/${recordId}/document`,

  // Tasks
  complianceTasks: (recordId: string) => `/compliance/records/${recordId}/tasks`,
  complianceTask: (taskId: string) => `/compliance/tasks/${taskId}`,
  complianceTaskNotes: (taskId: string) => `/compliance/tasks/${taskId}/notes`,
};


