/**
 * Ant Design Theme Configuration
 * ==============================
 * Defines the visual theme for TAMSys application.
 * 
 * Requirements:
 * - Light theme
 * - SHINE BLUE (#1890ff) as primary color
 * - Professional and plain design
 */

import type { ThemeConfig } from 'antd';

export const theme: ThemeConfig = {
  token: {
    // Primary Color - SHINE BLUE
    colorPrimary: '#1890ff',
    
    // Background Colors
    colorBgContainer: '#ffffff',
    colorBgLayout: '#f5f5f5',
    
    // Border Radius - Professional, not too rounded
    borderRadius: 4,
    
    // Typography
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    fontSize: 14,
    
    // Spacing
    controlHeight: 32,
    
    // Shadows - Subtle for professional look
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
  },
  
  components: {
    // Layout Component
    Layout: {
      headerBg: '#ffffff',
      headerColor: '#000000',
      headerHeight: 64,
      headerPadding: '0 24px',
      siderBg: '#f5f5f5',
      bodyBg: '#ffffff',
    },
    
    // Table Component
    Table: {
      headerBg: '#fafafa',
      headerColor: '#000000',
      rowHoverBg: '#f5f8ff',
    },
    
    // Button Component
    Button: {
      primaryColor: '#ffffff',
      controlHeight: 32,
    },
    
    // Card Component
    Card: {
      headerBg: '#ffffff',
      boxShadow: '0 1px 4px rgba(0, 0, 0, 0.08)',
    },
    
    // Menu Component
    Menu: {
      itemBg: 'transparent',
      itemSelectedBg: '#e6f4ff',
      itemSelectedColor: '#1890ff',
    },
  },
};


