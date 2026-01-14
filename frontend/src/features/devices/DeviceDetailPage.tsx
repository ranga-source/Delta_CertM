
/**
 * Device Detail Page
 * ==================
 * Overview of a specific device, including:
 * - Basic Info (Model, SKU, Desc)
 * - Technologies
 * - Target Markets
 * - Compliance Status Summary
 */

import { useParams, useNavigate } from 'react-router-dom';
import { Card, Descriptions, Tag, Button, Table, Typography, Space, Spin, Empty } from 'antd';
import { EditOutlined, ArrowLeftOutlined, SafetyCertificateOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import apiClient from '../../services/api';
import { API_ENDPOINTS } from '../../config/api.config';
import { QUERY_KEYS } from '../../services/queryClient';
import { useAppSelector } from '../../app/store';
import { ComplianceRecord, Device } from '../../types/models.types';
import DeviceCountryProgress from '../compliance/DeviceCountryProgress';

const { Title, Text } = Typography;

function DeviceDetailPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const currentTenantId = useAppSelector(state => state.tenant.currentTenantId);

    // 1. Fetch Device Details
    const { data: device, isLoading: isLoadingDevice } = useQuery({
        queryKey: QUERY_KEYS.device(id || ''),
        queryFn: async () => {
            const response = await apiClient.get<Device>(`${API_ENDPOINTS.device(id!)}?tenant_id=${currentTenantId}`);
            return response.data;
        },
        enabled: !!id && !!currentTenantId,
    });

    // 2. Fetch Compliance Records for this Device
    // We can filter by device_id
    const { data: complianceRecords, isLoading: isLoadingRecords } = useQuery({
        queryKey: QUERY_KEYS.complianceRecords(currentTenantId || '', { device_id: id }),
        queryFn: async () => {
            const response = await apiClient.get<ComplianceRecord[]>(
                `${API_ENDPOINTS.complianceRecords}?tenant_id=${currentTenantId}&device_id=${id}`
            );
            return response.data;
        },
        enabled: !!id && !!currentTenantId,
    });

    if (isLoadingDevice) return <Spin />;
    if (!device) return <Empty description="Device not found" />;

    // Columns for Compliance Summary
    const columns = [
        {
            title: 'Country',
            dataIndex: 'country_name',
            key: 'country',
            render: (text: string) => <Text strong>{text}</Text>,
        },
        {
            title: 'Certification',
            dataIndex: 'certification_name',
            key: 'certification',
        },
        {
            title: 'Status',
            dataIndex: 'status',
            key: 'status',
            render: (status: string) => {
                let color = 'default';
                if (status === 'ACTIVE' || status === 'COMPLIANT') color = 'success';
                else if (status === 'EXPIRING') color = 'warning';
                else if (status === 'EXPIRED' || status === 'MISSING') color = 'error';
                else if (status === 'PENDING') color = 'processing';

                return <Tag color={color}>{status || 'PENDING'}</Tag>;
            },
        },
        {
            title: 'Expiry',
            dataIndex: 'expiry_date',
            key: 'expiry',
            render: (date: string) => date ? new Date(date).toLocaleDateString() : '-',
        },
        {
            title: 'Action',
            key: 'action',
            render: (_: any, record: ComplianceRecord) => (
                <Button type="link" onClick={() => navigate(`/compliance/${record.id}`)}>View</Button>
            )
        }
    ];

    // Format Target Countries (handling ALL vs Specific)
    const targetCountriesDisplay = (device.target_countries && device.target_countries[0] !== 'ALL')
        ? device.target_countries.map(c => <Tag key={c}>{c}</Tag>)
        : <Tag color="blue">Global (All Markets)</Tag>;

    return (
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
            {/* Header / Actions */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Space>
                    <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/devices')}>Back</Button>
                    <Title level={2} style={{ margin: 0 }}>{device.model_name}</Title>
                </Space>
                <Button
                    type="primary"
                    icon={<EditOutlined />}
                    onClick={() => navigate(`/devices/${id}/edit`)}
                >
                    Edit Device
                </Button>
            </div>

            {/* Device Information Card */}
            <Card title="Device Information" bordered={false}>
                <Descriptions bordered column={{ xxl: 4, xl: 3, lg: 3, md: 2, sm: 1, xs: 1 }}>
                    <Descriptions.Item label="Model Name">{device.model_name}</Descriptions.Item>
                    <Descriptions.Item label="SKU">{device.sku || '-'}</Descriptions.Item>
                    <Descriptions.Item label="Target Markets">
                        {targetCountriesDisplay}
                    </Descriptions.Item>
                    <Descriptions.Item label="Technologies" span={3}>
                        {device.technologies?.map(tech => (
                            <Tag color="cyan" key={tech.id}>{tech.name}</Tag>
                        ))}
                    </Descriptions.Item>
                    <Descriptions.Item label="Description" span={3}>
                        {device.description || 'No description provided.'}
                    </Descriptions.Item>
                </Descriptions>
            </Card>

            {/* Compliance Summary Widget */}
            {complianceRecords && complianceRecords.length > 0 && (
                <DeviceCountryProgress
                    records={complianceRecords}
                    tenantId={currentTenantId}
                    onDrillDown={(filters) => {
                        console.log("Drill down", filters);
                        // Optional: scroll to table or filter table
                    }}
                />
            )}

            {/* Compliance Details Table */}
            <Card
                title={<Space><SafetyCertificateOutlined /> Compliance Details</Space>}
                bordered={false}
            >
                <Table
                    dataSource={complianceRecords}
                    columns={columns}
                    rowKey="id"
                    loading={isLoadingRecords}
                    pagination={false}
                    locale={{ emptyText: <Empty description="No compliance records found. Run Gap Analysis to generate requirements." /> }}
                />
            </Card>
        </Space>
    );
}

export default DeviceDetailPage;
