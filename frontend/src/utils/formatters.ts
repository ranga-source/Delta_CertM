/**
 * Formatting Utilities
 * ====================
 * Helper functions for formatting data for display.
 */

import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';

dayjs.extend(relativeTime);

/**
 * Format date to readable string
 * @param date Date string or Date object
 * @param format Format string (default: 'YYYY-MM-DD')
 */
export const formatDate = (date: string | Date | null | undefined, format: string = 'YYYY-MM-DD'): string => {
  if (!date) return '-';
  return dayjs(date).format(format);
};

/**
 * Format datetime to readable string
 * @param datetime Datetime string or Date object
 */
export const formatDateTime = (datetime: string | Date | null | undefined): string => {
  if (!datetime) return '-';
  return dayjs(datetime).format('YYYY-MM-DD HH:mm:ss');
};

/**
 * Get relative time (e.g., "2 hours ago", "in 3 days")
 * @param date Date string or Date object
 */
export const formatRelativeTime = (date: string | Date | null | undefined): string => {
  if (!date) return '-';
  return dayjs(date).fromNow();
};

/**
 * Calculate days until a date
 * @param date Target date
 * @returns Number of days (positive = future, negative = past)
 */
export const daysUntil = (date: string | Date | null | undefined): number => {
  if (!date) return 0;
  return dayjs(date).diff(dayjs(), 'day');
};

/**
 * Format compliance status to display text
 * @param status Compliance status enum value
 */
export const formatComplianceStatus = (status: string): string => {
  const statusMap: Record<string, string> = {
    PENDING: 'Pending',
    ACTIVE: 'Active',
    EXPIRING: 'Expiring Soon',
    EXPIRED: 'Expired',
    MISSING: 'Missing',
  };
  return statusMap[status] || status;
};

/**
 * Get status color for badges
 * @param status Compliance status
 */
export const getStatusColor = (status: string): string => {
  const colorMap: Record<string, string> = {
    PENDING: 'warning',
    ACTIVE: 'success',
    EXPIRING: 'warning',
    EXPIRED: 'error',
    MISSING: 'error',
  };
  return colorMap[status] || 'default';
};

/**
 * Format array of items to comma-separated string
 * @param items Array of items
 * @param key Optional key to extract from objects
 */
export const formatList = <T>(items: T[] | undefined, key?: keyof T): string => {
  if (!items || items.length === 0) return '-';
  
  if (key) {
    return items.map(item => item[key]).join(', ');
  }
  
  return items.join(', ');
};

/**
 * Truncate long text with ellipsis
 * @param text Text to truncate
 * @param maxLength Maximum length
 */
export const truncate = (text: string | undefined, maxLength: number = 50): string => {
  if (!text) return '-';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};


