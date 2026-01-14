/**
 * Header Component
 * ================
 * Top navigation bar for the application.
 * 
 * Features:
 * - TAMSys branding
 * - Tenant selector dropdown
 * - Responsive design
 */

import { Layout, Select, Typography, Space, Button } from 'antd';
import { ApartmentOutlined, FontSizeOutlined } from '@ant-design/icons';
import { useAppDispatch, useAppSelector } from '../../app/store';
import { setCurrentTenant } from '../../app/slices/tenantSlice';
import { useQuery } from '@tanstack/react-query';
import apiClient from '../../services/api';
import { QUERY_KEYS } from '../../services/queryClient';
import { API_ENDPOINTS } from '../../config/api.config';
import { Tenant } from '../../types/models.types';
import { useTheme } from '../../context/ThemeContext';
import './Header.css';

const { Header: AntHeader } = Layout;
const { Title } = Typography;

function Header() {
  const dispatch = useAppDispatch();
  const currentTenantId = useAppSelector(state => state.tenant.currentTenantId);
  const { increaseFontSize, decreaseFontSize } = useTheme();

  /**
   * Fetch tenants list
   */
  const { data: tenants } = useQuery({
    queryKey: QUERY_KEYS.tenants,
    queryFn: async () => {
      const response = await apiClient.get<Tenant[]>(API_ENDPOINTS.tenants);
      return response.data;
    },
  });

  /**
   * Handle tenant selection change
   */
  const handleTenantChange = (tenantId: string) => {
    dispatch(setCurrentTenant(tenantId));
  };

  return (
    <AntHeader className="app-header">
      <div className="header-content">
        {/* Left: Branding */}
        <div className="header-brand">
          <ApartmentOutlined className="brand-icon" />
          <Title level={3} className="brand-title">
            TAMSys
          </Title>
          <span className="brand-subtitle">Certification Management</span>
        </div>

        {/* Right: Actions */}
        <Space className="header-actions">
          {/* Font Size Switcher */}
          <Space.Compact style={{ marginRight: 16 }}>
            <Button icon={<FontSizeOutlined />} onClick={increaseFontSize} title="Increase Font Size" />
            <Button icon={<FontSizeOutlined style={{ fontSize: '10px' }} />} onClick={decreaseFontSize} title="Decrease Font Size" />
          </Space.Compact>

          <span className="tenant-label">Tenant:</span>
          <Select
            className="tenant-selector"
            placeholder="Select Tenant"
            value={currentTenantId || undefined}
            onChange={handleTenantChange}
            style={{ width: 200 }}
            options={tenants?.filter(t => t.is_active).map(tenant => ({
              label: tenant.name,
              value: tenant.id,
            })) || []}
          />
        </Space>
      </div>
    </AntHeader>
  );
}

export default Header;

