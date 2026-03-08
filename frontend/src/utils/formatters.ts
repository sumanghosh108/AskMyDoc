// Formatting utilities for dates, numbers, and other display values

import { format, formatDistanceToNow } from 'date-fns';

/**
 * Formats a date for display
 * 
 * @param date - Date to format
 * @param formatString - Optional format string (default: 'PPpp')
 * @returns Formatted date string
 */
export function formatDate(date: Date, formatString = 'PPpp'): string {
  return format(date, formatString);
}

/**
 * Formats a date as relative time (e.g., "2 hours ago")
 * 
 * @param date - Date to format
 * @returns Relative time string
 */
export function formatRelativeTime(date: Date): string {
  return formatDistanceToNow(date, { addSuffix: true });
}

/**
 * Formats latency in milliseconds for display
 * 
 * @param latencyMs - Latency in milliseconds
 * @returns Formatted latency string
 */
export function formatLatency(latencyMs: number): string {
  if (latencyMs < 1000) {
    return `${Math.round(latencyMs)}ms`;
  }
  return `${(latencyMs / 1000).toFixed(2)}s`;
}

/**
 * Formats a number with commas for thousands
 * 
 * @param num - Number to format
 * @returns Formatted number string
 */
export function formatNumber(num: number): string {
  return num.toLocaleString();
}

/**
 * Formats a percentage value
 * 
 * @param value - Value between 0 and 1 (or 0 and 100 if asPercentage is true)
 * @param decimals - Number of decimal places (default: 1)
 * @param asPercentage - Whether input is already a percentage (default: false)
 * @returns Formatted percentage string
 */
export function formatPercentage(
  value: number,
  decimals = 1,
  asPercentage = false
): string {
  const percentage = asPercentage ? value : value * 100;
  return `${percentage.toFixed(decimals)}%`;
}

/**
 * Formats file size in bytes to human-readable format
 * 
 * @param bytes - File size in bytes
 * @returns Formatted file size string
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}
