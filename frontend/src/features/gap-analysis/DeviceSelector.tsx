/**
 * Device Selector Component
 */

import { Select, Spin } from 'antd';
import { useQuery } from '@tanstack/react-query';
import apiClient from '../../services/api';
import { API_ENDPOINTS } from '../../config/api.config';
import { QUERY_KEYS } from '../../services/queryClient';
import { Device } from '../../types/models.types';

interface DeviceSelectorProps {
  value: string | null;
  onChange: (value: string | null) => void;
  tenantId: string | null;
}

function DeviceSelector({ value, onChange, tenantId }: DeviceSelectorProps) {
  const { data: devices, isLoading } = useQuery({
    queryKey: QUERY_KEYS.devices(tenantId || ''),
    queryFn: async () => {
      const response = await apiClient.get<Device[]>(
        `${API_ENDPOINTS.devices}?tenant_id=${tenantId}`
      );
      return response.data;
    },
    enabled: !!tenantId,
  });
  
  return (
    <div>
      <label className="input-label">Step 1: Select Device</label>
      <Select
        showSearch
        placeholder="Select a device"
        value={value}
        onChange={onChange}
        loading={isLoading}
        style={{ width: '100%' }}
        size="large"
        notFoundContent={isLoading ? <Spin size="small" /> : 'No devices found'}
        filterOption={(input, option) =>
          (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
        }
        options={devices?.map(device => ({
          label: `${device.model_name}${device.sku ? ` (${device.sku})` : ''}`,
          value: device.id,
        })) || []}
      />
    </div>
  );
}

export default DeviceSelector;


