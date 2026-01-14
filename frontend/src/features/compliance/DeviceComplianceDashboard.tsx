
import React, { useState, useMemo } from 'react';
import { Layout, Menu, Input, List, Typography, Card, Row, Col, Tag, Button, Empty, Spin, Avatar, Progress, Space } from 'antd';
import {
    DashboardOutlined,
    BarChartOutlined,
    HistoryOutlined,
    SearchOutlined,
    CheckCircleOutlined,
    WarningOutlined,
    StopOutlined,
    InfoCircleOutlined,
    GlobalOutlined
} from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import apiClient from '../../services/api';
import { API_ENDPOINTS } from '../../config/api.config';
import { QUERY_KEYS } from '../../services/queryClient';
import { useAppSelector } from '../../app/store';
import { Device, ComplianceRecord, ComplianceStatus } from '../../types/models.types';
import { GlobalComplianceMap } from './components/dashboard/GlobalComplianceMap';
import { formatDate, getStatusColor } from '../../utils/formatters';

const { Sider, Content } = Layout;
const { Title, Text } = Typography;

const DeviceComplianceDashboard: React.FC = () => {
    const navigate = useNavigate();
    const currentTenantId = useAppSelector(state => state.tenant.currentTenantId);
    const [selectedDeviceId, setSelectedDeviceId] = useState<string | null>(null); // null means "All"
    const [searchTerm, setSearchTerm] = useState('');

    // --- Data Fetching ---

    // 1. Fetch Devices (Sidebar)
    const { data: devices = [], isLoading: isLoadingDevices } = useQuery({
        queryKey: QUERY_KEYS.devices(currentTenantId || ''),
        queryFn: async () => {
            const response = await apiClient.get<Device[]>(`${API_ENDPOINTS.devices}?tenant_id=${currentTenantId}`);
            return response.data;
        },
        enabled: !!currentTenantId,
    });

    // 2. Fetch Compliance Records (For Stats & "Latest Info")
    const { data: records = [], isLoading: isLoadingRecords } = useQuery({
        queryKey: QUERY_KEYS.complianceRecords(currentTenantId || ''),
        queryFn: async () => {
            const response = await apiClient.get<ComplianceRecord[]>(`${API_ENDPOINTS.complianceRecords}?tenant_id=${currentTenantId}&limit=1000`);
            return response.data;
        },
        enabled: !!currentTenantId,
    });

    // --- Derived Data ---

    const filteredDevices = useMemo(() => {
        return devices.filter(d =>
            d.model_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            d.sku?.toLowerCase().includes(searchTerm.toLowerCase())
        );
    }, [devices, searchTerm]);

    const selectedDevice = useMemo(() =>
        devices.find(d => d.id === selectedDeviceId),
        [devices, selectedDeviceId]);

    // Filter records based on selection
    const activeRecords = useMemo(() => {
        if (!selectedDeviceId) return records;
        return records.filter(r => r.device_id === selectedDeviceId);
    }, [records, selectedDeviceId]);

    // "Latest Info" - Find the most relevant record (e.g., most recently created or expiring soon)
    const latestRecord = useMemo(() => {
        if (!activeRecords.length) return null;
        // Logic: Sort by updated_at desc (most recently modified first)
        return [...activeRecords].sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())[0];
    }, [activeRecords]);

    // Stats
    const stats = useMemo(() => {
        const total = activeRecords.length;
        const active = activeRecords.filter(r => r.status === ComplianceStatus.ACTIVE).length;
        const expiring = activeRecords.filter(r => r.status === ComplianceStatus.EXPIRING).length;
        const expired = activeRecords.filter(r => r.status === ComplianceStatus.EXPIRED).length;
        const pending = activeRecords.filter(r => r.status === ComplianceStatus.PENDING).length;

        // Labeling Stats
        const labelingDone = activeRecords.filter(r => r.labeling_status === 'DONE').length;
        const labelingPending = activeRecords.filter(r => r.labeling_status !== 'DONE' && r.status === ComplianceStatus.ACTIVE).length;

        let overallStatus = 'No Data';
        let statusColor = '#d9d9d9';

        if (expired > 0) {
            overallStatus = 'Non-Compliant';
            statusColor = '#ff4d4f';
        } else if (expiring > 0) {
            overallStatus = 'Attention Needed';
            statusColor = '#faad14';
        } else if (active > 0) {
            overallStatus = 'Compliant';
            statusColor = '#52c41a';
        } else if (pending > 0) {
            overallStatus = 'Pending';
            statusColor = '#1890ff'; // Blue for Pending
        } else {
            overallStatus = 'No Data';
            statusColor = '#d9d9d9';
        }

        return { total, active, expiring, expired, pending, labelingDone, labelingPending, overallStatus, statusColor };
    }, [activeRecords]);


    // Tech stats for fleet overview
    const techStats = useMemo(() => {
        const techCounts: Record<string, number> = {};
        devices.forEach(d => {
            d.technologies?.forEach((t: any) => {
                techCounts[t.name] = (techCounts[t.name] || 0) + 1;
            });
        });

        return Object.entries(techCounts)
            .sort(([, a], [, b]) => b - a)
            .slice(0, 10) // Top 10
            .map(([name, count]) => ({ name, count }));
    }, [devices]);

    // Map device IDs to their compliance status color
    const deviceStatusColors = useMemo(() => {
        const statusMap: Record<string, string> = {};

        devices.forEach(device => {
            const deviceRecords = records.filter(r => r.device_id === device.id);

            const hasExpired = deviceRecords.some(r => r.status === ComplianceStatus.EXPIRED);
            const hasExpiring = deviceRecords.some(r => r.status === ComplianceStatus.EXPIRING);
            const hasActive = deviceRecords.some(r => r.status === ComplianceStatus.ACTIVE);
            const hasPending = deviceRecords.some(r => r.status === ComplianceStatus.PENDING);

            if (hasExpired) {
                statusMap[device.id] = '#ff4d4f'; // Red
            } else if (hasExpiring) {
                statusMap[device.id] = '#faad14'; // Orange
            } else if (hasActive) {
                statusMap[device.id] = '#52c41a'; // Green
            } else if (hasPending) {
                statusMap[device.id] = '#1890ff'; // Blue for Pending
            } else {
                statusMap[device.id] = '#d9d9d9'; // Grey for No Data
            }
        });

        return statusMap;
    }, [devices, records]);


    const handleCountryClick = (countryName: string) => {
        if (!selectedDeviceId) return;

        // Find record for this device and country
        const record = activeRecords.find(r =>
            r.country_name === countryName ||
            (r.country_name === "USA" && countryName === "United States of America") ||
            (r.country_name === "United States" && countryName === "United States of America") ||
            (r.country_name === "UK" && countryName === "United Kingdom")
        );

        if (record) {
            navigate(`/compliance/${record.id}`);
        }
    };

    return (
        <Layout style={{ height: 'calc(100vh - 160px)', background: '#f0f2f5', overflow: 'hidden' }} hasSider>
            {/* ... Sider omitted for brevity ... */}
            <Sider
                width={280}
                theme="light"
                style={{
                    borderRight: '1px solid #e8e8e8',
                    height: '100%',
                    overflow: 'hidden'
                }}
            >
                <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                    <div style={{ padding: '12px 20px 10px 20px', flexShrink: 0 }}>
                        <Title level={5} style={{ marginBottom: 16, marginTop: 4, paddingBottom: 12, borderBottom: '1px solid #f0f0f0', color: '#595959', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Device Monitor</Title>
                        <Input
                            prefix={<SearchOutlined style={{ color: '#bfbfbf' }} />}
                            placeholder="Search..."
                            allowClear
                            size="small"
                            style={{ borderRadius: 4, background: '#fafafa' }}
                            value={searchTerm}
                            onChange={e => setSearchTerm(e.target.value)}
                        />
                    </div>

                    <div style={{ flex: 1, overflowY: 'auto', padding: '0 20px 20px 20px' }}>
                        <List
                            itemLayout="horizontal"
                            dataSource={[{ id: 'all', model_name: 'All Devices' } as Device, ...filteredDevices]}
                            split={false}
                            renderItem={(item) => {
                                const isAll = item.id === 'all';
                                const isSelected = isAll ? !selectedDeviceId : selectedDeviceId === item.id;
                                const statusColor = !isAll ? (deviceStatusColors[item.id] || '#52c41a') : '#52c41a';

                                return (
                                    <List.Item
                                        style={{
                                            padding: '8px 12px',
                                            borderRadius: '4px',
                                            cursor: 'pointer',
                                            backgroundColor: isSelected ? '#e6f7ff' : 'transparent',
                                            marginBottom: 2,
                                            border: isSelected ? '1px solid #bae7ff' : '1px solid transparent',
                                            transition: 'all 0.2s ease',
                                        }}
                                        onClick={() => setSelectedDeviceId(isAll ? null : item.id)}
                                        onMouseEnter={(e) => { if (!isSelected) e.currentTarget.style.background = '#fafafa'; }}
                                        onMouseLeave={(e) => { if (!isSelected) e.currentTarget.style.background = 'transparent'; }}
                                    >
                                        <div style={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                                            <div style={{
                                                flex: 1,
                                                fontWeight: isSelected ? 600 : 500,
                                                color: isSelected ? '#1890ff' : '#262626',
                                            }}>
                                                {item.model_name}
                                            </div>
                                            {!isAll && (
                                                <div style={{
                                                    width: 6,
                                                    height: 6,
                                                    borderRadius: '50%',
                                                    backgroundColor: statusColor,
                                                    boxShadow: `0 0 0 1px ${statusColor}33`
                                                }} />
                                            )}
                                        </div>
                                    </List.Item>
                                );
                            }}
                        />
                    </div>
                </div>
            </Sider>

            <Layout style={{ padding: '16px', height: '100%', overflow: 'hidden' }}>
                <Content style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                    <div style={{ marginBottom: 12, flexShrink: 0 }}>
                        <div style={{ display: 'flex', alignItems: 'center' }}>
                            <div>
                                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                                    <Title level={4} style={{ margin: 0 }}>{selectedDevice ? selectedDevice.model_name : 'Fleet Overview'}</Title>
                                    <Tag color={stats.statusColor} style={{ margin: 0 }}>{stats.overallStatus.toUpperCase()}</Tag>
                                </div>
                                <Text type="secondary">{selectedDevice ? selectedDevice.sku : `${devices.length} devices total`}</Text>
                            </div>
                        </div>
                    </div>

                    <Row gutter={[16, 16]} style={{ flex: 1, height: '100%' }}>
                        {/* LEFT COLUMN - Compact Widgets */}
                        <Col xs={24} lg={6} style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: 16, overflowY: 'auto', paddingRight: 4, paddingBottom: 32 }}>
                            {/* Latest Info Widget */}
                            <Card
                                size="small"
                                title={
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                        <span><DashboardOutlined style={{ color: '#1890ff', marginRight: 6 }} />Latest Activity</span>
                                        {latestRecord && (
                                            <span style={{ fontWeight: 400, color: '#8c8c8c' }}>
                                                {new Date(latestRecord.updated_at).toLocaleString()}
                                            </span>
                                        )}
                                    </div>
                                }
                                bordered={false}
                                variant="borderless"
                                style={{ borderRadius: 8, boxShadow: '0 1px 2px rgba(0,0,0,0.03)' }}
                                bodyStyle={{ padding: '12px' }}
                            >
                                {latestRecord ? (
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                                        {!selectedDevice && (
                                            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #f0f0f0', paddingBottom: 8 }}>
                                                <Text type="secondary">Device</Text>
                                                <Text strong>{devices.find(d => d.id === latestRecord.device_id)?.model_name || 'Unknown'}</Text>
                                            </div>
                                        )}
                                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                            <Text type="secondary">Authority</Text>
                                            <Text strong>{latestRecord.certification_name}</Text>
                                        </div>
                                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                            <Text type="secondary">Country</Text>
                                            <Text strong>{latestRecord.country_name || latestRecord.country_id}</Text>
                                        </div>
                                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                            <Text type="secondary">Status</Text>
                                            <Tag style={{ margin: 0 }} color={getStatusColor(latestRecord.status)}>{latestRecord.status}</Tag>
                                        </div>
                                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                            <Text type="secondary">Labeling</Text>
                                            <Space direction="vertical" align="end" size={0}>
                                                <Tag style={{ margin: 0 }} color={latestRecord.labeling_status === 'DONE' ? 'green' : 'blue'}>
                                                    {latestRecord.labeling_status || 'PENDING'}
                                                </Tag>
                                                {latestRecord.labeling_updated_at && (
                                                    <span style={{ fontSize: '10px', color: '#8c8c8c' }}>
                                                        {new Date(latestRecord.labeling_updated_at).toLocaleString()}
                                                    </span>
                                                )}
                                            </Space>
                                        </div>
                                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                            <Text type="secondary">Expiry</Text>
                                            <Text>{formatDate(latestRecord.expiry_date)}</Text>
                                        </div>
                                    </div>
                                ) : <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="No data" />}
                            </Card>

                            {/* Compliance Summary Widget */}
                            <Card
                                size="small"
                                title={<span><BarChartOutlined style={{ color: '#1890ff', marginRight: 6 }} />Summary</span>}
                                bordered={false}
                                variant="borderless"
                                style={{ borderRadius: 8, boxShadow: '0 1px 2px rgba(0,0,0,0.03)' }}
                                bodyStyle={{ padding: '12px' }}
                            >
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                        <Text>Total</Text>
                                        <Text strong>{stats.total}</Text>
                                    </div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                        <Text>Active</Text>
                                        <Text strong style={{ color: '#52c41a' }}>{stats.active}</Text>
                                    </div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                        <Text>Pending</Text>
                                        <Text strong style={{ color: '#1890ff' }}>{stats.pending}</Text>
                                    </div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                        <Text>Expiring</Text>
                                        <Text strong style={{ color: '#faad14' }}>{stats.expiring}</Text>
                                    </div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                        <Text>Expired</Text>
                                        <Text strong style={{ color: '#ff4d4f' }}>{stats.expired}</Text>
                                    </div>
                                </div>
                            </Card>

                            {/* Labeling Overview Widget */}
                            <Card
                                size="small"
                                title={<span><CheckCircleOutlined style={{ color: '#52c41a', marginRight: 6 }} />Labeling</span>}
                                bordered={false}
                                variant="borderless"
                                style={{ borderRadius: 8, boxShadow: '0 1px 2px rgba(0,0,0,0.03)' }}
                                bodyStyle={{ padding: '12px' }}
                            >
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                        <Text type="secondary">Completed</Text>
                                        <Tag color="success" style={{ margin: 0 }}>{stats.labelingDone}</Tag>
                                    </div>
                                    <Progress
                                        percent={stats.active > 0 ? Math.round((stats.labelingDone / stats.active) * 100) : 0}
                                        size="small"
                                        strokeColor="#52c41a"
                                    />
                                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                        <Text type="secondary">Action Needed</Text>
                                        <Text strong style={{ color: stats.labelingPending > 0 ? '#faad14' : '#8c8c8c' }}>
                                            {stats.labelingPending}
                                        </Text>
                                    </div>
                                </div>
                            </Card>

                            {/* Tech Widget */}
                            <Card
                                size="small"
                                title={<span><InfoCircleOutlined style={{ color: '#1890ff', marginRight: 6 }} />Details</span>}
                                bordered={false}
                                variant="borderless"
                                style={{
                                    borderRadius: 8,
                                    boxShadow: '0 1px 2px rgba(0,0,0,0.03)',
                                }}
                                bodyStyle={{ padding: '12px' }}
                            >
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                                    <div>
                                        <Text type="secondary" style={{ marginBottom: 4, display: 'block' }}>
                                            {selectedDevice ? 'CONNECTED TECHNOLOGIES' : 'TOP TECHNOLOGIES'}
                                        </Text>

                                        {selectedDevice ? (
                                            selectedDevice.technologies && selectedDevice.technologies.length > 0 ? (
                                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                                                    {selectedDevice.technologies.slice(0, 50).map((t: any) => (
                                                        <span key={t.id} style={{
                                                            background: '#f0f5ff',
                                                            color: '#2f54eb',
                                                            border: '1px solid #adc6ff',
                                                            padding: '2px 8px',
                                                            borderRadius: '4px',
                                                            fontWeight: 500
                                                        }}>
                                                            {t.name}
                                                        </span>
                                                    ))}
                                                </div>
                                            ) : <Text type="secondary" style={{ fontStyle: 'italic' }}>No technologies listed</Text>
                                        ) : (
                                            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                                                {techStats.map(t => (
                                                    <div key={t.name}>
                                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 2 }}>
                                                            <span style={{ color: '#595959' }}>{t.name}</span>
                                                            <span style={{ fontWeight: 600 }}>{t.count}</span>
                                                        </div>
                                                        <Progress
                                                            percent={(t.count / devices.length) * 100}
                                                            size="small"
                                                            showInfo={false}
                                                            strokeColor="#1890ff"
                                                            trailColor="#f5f5f5"
                                                            style={{ margin: 0, lineHeight: 1 }}
                                                        />
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </Card>
                        </Col>

                        {/* RIGHT COLUMN - MAP (Takes remaining space) */}
                        <Col xs={24} lg={18} style={{ height: '100%' }}>
                            <Card
                                size="small"
                                bordered={false}
                                variant="borderless"
                                style={{ borderRadius: 8, height: '100%', boxShadow: '0 1px 2px rgba(0,0,0,0.03)', display: 'flex', flexDirection: 'column' }}
                                bodyStyle={{ flex: 1, padding: 0, overflow: 'hidden', position: 'relative' }}
                            >
                                <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0 }}>
                                    <GlobalComplianceMap
                                        records={activeRecords}
                                        isLoading={isLoadingRecords}
                                        onCountryClick={handleCountryClick}
                                        mode={selectedDeviceId ? 'DEVICE' : 'OVERVIEW'}
                                    />
                                </div>
                            </Card>
                        </Col>
                    </Row>
                </Content>
            </Layout>
        </Layout>
    );
};

export default DeviceComplianceDashboard;
