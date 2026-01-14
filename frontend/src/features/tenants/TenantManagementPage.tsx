/**
 * Tenant Management Page
 */

import { Card, Table, Button, Space, Tag } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import apiClient from '../../services/api';
import { API_ENDPOINTS } from '../../config/api.config';
import { QUERY_KEYS } from '../../services/queryClient';
import { Tenant } from '../../types/models.types';
import { useState } from 'react';
import { TenantFormModal } from './components/TenantFormModal';

function TenantManagementPage() {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingTenant, setEditingTenant] = useState<Tenant | null>(null);

  const handleAdd = () => {
    setEditingTenant(null);
    setIsModalVisible(true);
  };

  const handleEdit = (tenant: Tenant) => {
    setEditingTenant(tenant);
    setIsModalVisible(true);
  };

  const handleCancel = () => {
    setIsModalVisible(false);
    setEditingTenant(null);
  };
  const { data: tenants, isLoading } = useQuery({
    queryKey: QUERY_KEYS.tenants,
    queryFn: async () => {
      const response = await apiClient.get<Tenant[]>(API_ENDPOINTS.tenants);
      return response.data;
    },
  });

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Contact Email',
      dataIndex: 'contact_email',
      key: 'contact_email',
    },
    {
      title: 'Status',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (active: boolean) => (
        <Tag color={active ? 'success' : 'default'}>
          {active ? 'Active' : 'Inactive'}
        </Tag>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: Tenant) => (
        <Space>
          <Button size="small" onClick={() => handleEdit(record)}>Edit</Button>
          <Button size="small">Rules</Button>
        </Space>
      ),
    },
  ];

  return (
    <Card
      title="Tenant Management"
      extra={
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          Add Tenant
        </Button>
      }
    >
      <Table
        columns={columns}
        dataSource={tenants}
        rowKey="id"
        loading={isLoading}
        pagination={{ pageSize: 10 }}
      />
      <TenantFormModal
        visible={isModalVisible}
        onCancel={handleCancel}
        editingTenant={editingTenant}
      />
    </Card>
  );
}

export default TenantManagementPage;


