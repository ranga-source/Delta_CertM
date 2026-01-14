/**
 * Device List Page
 * Displays all devices for the current tenant
 */

import { useState, useMemo } from 'react';
import { Card, Table, Button, Input, Space, message, Tag, Tooltip } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined, CheckCircleOutlined, CloseCircleOutlined, GlobalOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../../services/api';
import { API_ENDPOINTS } from '../../config/api.config';
import { QUERY_KEYS } from '../../services/queryClient';
import { useAppSelector } from '../../app/store';
import { Device, ComplianceRecord, ComplianceStatus } from '../../types/models.types';
import { useDebounce } from '../../hooks/useDebounce';

function DeviceListPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const currentTenantId = useAppSelector(state => state.tenant.currentTenantId);
  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearch = useDebounce(searchTerm, 300);

  // 1. Fetch Devices
  const { data: devices, isLoading: isLoadingDevices } = useQuery({
    queryKey: QUERY_KEYS.devices(currentTenantId || ''),
    queryFn: async () => {
      const response = await apiClient.get<Device[]>(
        `${API_ENDPOINTS.devices}?tenant_id=${currentTenantId}`
      );
      return response.data;
    },
    enabled: !!currentTenantId,
  });

  // 2. Fetch Compliance Records (for metrics)
  const { data: records = [] } = useQuery({
    queryKey: QUERY_KEYS.complianceRecords(currentTenantId || ''),
    queryFn: async () => {
      const response = await apiClient.get<ComplianceRecord[]>(`${API_ENDPOINTS.complianceRecords}?tenant_id=${currentTenantId}&limit=1000`);
      return response.data;
    },
    enabled: !!currentTenantId,
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`${API_ENDPOINTS.device(id)}?tenant_id=${currentTenantId}`);
    },
    onSuccess: () => {
      message.success('Device deleted successfully');
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.devices(currentTenantId || '') });
    },
  });

  const filteredDevices = devices?.filter(device =>
    device.model_name.toLowerCase().includes(debouncedSearch.toLowerCase()) ||
    device.sku?.toLowerCase().includes(debouncedSearch.toLowerCase())
  );

  // Helper to get stats for a device
  const getDeviceStats = (deviceId: string) => {
    const deviceRecords = records.filter(r => r.device_id === deviceId);
    const active = deviceRecords.filter(r => r.status === ComplianceStatus.ACTIVE).length;
    const expired = deviceRecords.filter(r => r.status === ComplianceStatus.EXPIRED).length;
    // Current markets = unique countries with at least one active certification
    const currentMarkets = new Set(
      deviceRecords
        .filter(r => r.status === ComplianceStatus.ACTIVE)
        .map(r => r.country_id)
    ).size;

    return { active, expired, currentMarkets };
  };

  const columns = [
    {
      title: 'Model Name',
      dataIndex: 'model_name',
      key: 'model_name',
      width: 250,
      render: (text: string, record: Device) => (
        <span style={{ fontWeight: 500, color: '#1890ff' }}>
          {text}
        </span>
      ),
    },
    {
      title: 'Targeted Markets',
      dataIndex: 'target_countries',
      key: 'target_countries',
      width: 150,
      render: (countries: string[]) => {
        if (!countries || countries.length === 0) return <span style={{ color: '#d9d9d9' }}>-</span>;
        if (countries.includes('ALL')) return <Tag color="blue">Global</Tag>;

        const displayLimit = 3;
        const displayCountries = countries.slice(0, displayLimit);
        const remaining = countries.length - displayLimit;

        return (
          <>
            {displayCountries.map(country => (
              <Tag key={country} style={{ marginRight: 4 }}>{country}</Tag>
            ))}
            {remaining > 0 && (
              <Tooltip title={countries.slice(displayLimit).join(', ')}>
                <Tag>+{remaining}</Tag>
              </Tooltip>
            )}
          </>
        );
      }
    },
    {
      title: 'Current Markets',
      key: 'current_markets',
      width: 150,
      render: (_: any, record: Device) => {
        const { currentMarkets } = getDeviceStats(record.id);
        return <span><GlobalOutlined style={{ marginRight: 6, color: '#1890ff' }} />{currentMarkets}</span>;
      }
    },
    {
      title: 'Active Certs',
      key: 'active_certs',
      width: 120,
      render: (_: any, record: Device) => {
        const { active } = getDeviceStats(record.id);
        return active > 0 ? <Tag icon={<CheckCircleOutlined />} color="success">{active}</Tag> : <span style={{ color: '#d9d9d9' }}>-</span>;
      }
    },
    {
      title: 'Expired Certs',
      key: 'expired_certs',
      width: 120,
      render: (_: any, record: Device) => {
        const { expired } = getDeviceStats(record.id);
        return expired > 0 ? <Tag icon={<CloseCircleOutlined />} color="error">{expired}</Tag> : <span style={{ color: '#d9d9d9' }}>-</span>;
      }
    },
    {
      title: 'Technologies',
      dataIndex: 'technologies',
      key: 'technologies',
      render: (technologies: any[]) => {
        if (!technologies || technologies.length === 0) {
          return '-';
        }
        const displayTechs = technologies.slice(0, 2);
        const remaining = technologies.length - 2;
        return (
          <>
            {displayTechs.map(tech => (
              <Tag key={tech.id} style={{ marginRight: 4 }}>{tech.name}</Tag>
            ))}
            {remaining > 0 && <Tag>+{remaining}</Tag>}
          </>
        );
      },
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: Device) => (
        <Space onClick={(e) => e.stopPropagation()}>
          <Button
            icon={<EditOutlined />}
            onClick={() => navigate(`/devices/${record.id}/edit`)}
          >
          </Button>
          <Button
            danger
            icon={<DeleteOutlined />}
            onClick={() => deleteMutation.mutate(record.id)}
          >
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <Card
      title="Devices"
      extra={
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => navigate('/devices/new')}
        >
          Add Device
        </Button>
      }
    >
      <Input
        placeholder="Search devices..."
        prefix={<SearchOutlined />}
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        style={{ marginBottom: 16, maxWidth: 400 }}
      />
      <Table
        columns={columns}
        dataSource={filteredDevices}
        rowKey="id"
        loading={isLoadingDevices}
        pagination={{ pageSize: 10 }}
        onRow={(record) => ({
          onClick: () => {
            navigate(`/devices/${record.id}`);
          },
          style: { cursor: 'pointer' },
        })}
      />
    </Card>
  );
}

export default DeviceListPage;


