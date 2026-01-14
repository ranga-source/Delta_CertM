import React from 'react';
import { Table, Tag, Typography, Button, Spin, Empty } from 'antd';
import { Clock } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import dayjs from 'dayjs';
import apiClient from '../../../../services/api';
import { API_ENDPOINTS } from '../../../../config/api.config';
import { QUERY_KEYS } from '../../../../services/queryClient';
import { useAppSelector } from '../../../../app/store'; // Adjusted path to store
import { ComplianceRecord } from '../../../../types/models.types';

const { Title, Text } = Typography;

const columns = [
    {
        title: 'Device',
        dataIndex: 'device_name',
        key: 'device_name',
        render: (text: string) => <Text strong style={{ color: '#262626' }}>{text}</Text>,
        width: '25%',
    },
    {
        title: 'Country',
        dataIndex: 'country_name',
        key: 'country_name',
        width: '20%',
    },
    {
        title: 'Certification',
        dataIndex: 'certification_name',
        key: 'certification_name',
        width: '20%',
    },
    {
        title: 'Status',
        key: 'status',
        render: (_: any, record: ComplianceRecord) => {
            if (!record.expiry_date) return <Tag>No Date</Tag>;
            const today = dayjs();
            const expiry = dayjs(record.expiry_date);
            const daysLeft = expiry.diff(today, 'day');

            const isExpired = daysLeft < 0;
            const color = isExpired ? '#ff4d4f' : (daysLeft < 30 ? '#faad14' : '#52c41a');
            const bgColor = isExpired ? '#fff1f0' : (daysLeft < 30 ? '#fffbe6' : '#f6ffed');
            const borderColor = isExpired ? '#ffa39e' : (daysLeft < 30 ? '#ffe58f' : '#b7eb8f');

            return (
                <Tag
                    style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: 6,
                        color: color,
                        background: bgColor,
                        border: `1px solid ${borderColor}`,
                        borderRadius: '6px',
                        padding: '2px 10px',
                        fontWeight: 500
                    }}
                >
                    <Clock size={12} />
                    <span>{isExpired ? `${Math.abs(daysLeft)} days overdue` : `${daysLeft} days left`}</span>
                </Tag>
            );
        },
    },
];

interface ExpiringWatchlistProps {
    onViewAll?: () => void;
}

export const ExpiringWatchlist: React.FC<ExpiringWatchlistProps> = ({ onViewAll }) => {
    const navigate = useNavigate();
    const currentTenantId = useAppSelector(state => state.tenant.currentTenantId);

    const handleViewAll = () => {
        if (onViewAll) {
            onViewAll();
        } else {
            navigate('/compliance?tab=records');
        }
    };

    const { data: records, isLoading } = useQuery({
        queryKey: QUERY_KEYS.complianceRecords(currentTenantId || '', { status: 'EXPIRING' }),
        queryFn: async () => {
            if (!currentTenantId) return [];
            const url = `${API_ENDPOINTS.complianceRecords}?tenant_id=${currentTenantId}&status_filter=EXPIRING`;
            const response = await apiClient.get<ComplianceRecord[]>(url);
            return response.data;
        },
        enabled: !!currentTenantId,
    });

    const processedData = React.useMemo(() => {
        if (!records) return [];
        return [...records]
            .filter(r => r.expiry_date)
            .sort((a, b) => dayjs(a.expiry_date).valueOf() - dayjs(b.expiry_date).valueOf());
    }, [records]);

    return (
        <div style={{
            background: '#fff',
            borderRadius: '12px',
            boxShadow: '0 2px 12px rgba(0,0,0,0.06)',
            border: '1px solid #f0f0f0',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            minHeight: '400px'
        }}>
            <div style={{
                padding: '16px 24px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                borderBottom: '1px solid #f5f5f5',
                background: '#fafafa'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <Clock size={16} color="#ff4d4f" />
                    <Title level={5} style={{ margin: 0, color: '#262626', fontSize: '14px', fontWeight: 600 }}>
                        Expiring Watchlist
                    </Title>
                </div>
                <Button type="link" size="small" onClick={handleViewAll} style={{ fontWeight: 500, fontSize: '12px' }}>
                    View All
                </Button>
            </div>

            <div className="custom-watchlist-table" style={{ flex: 1, overflowY: 'auto' }}>
                {isLoading ? (
                    <div style={{ display: 'flex', justifyContent: 'center', padding: '60px' }}><Spin /></div>
                ) : processedData.length > 0 ? (
                    <Table
                        columns={columns}
                        dataSource={processedData}
                        pagination={false}
                        size="small"
                        rowKey="id"
                        onRow={(record) => ({
                            onClick: () => navigate(`/compliance/${record.id}`),
                            style: { cursor: 'pointer' }
                        })}
                    />
                ) : (
                    <div style={{ padding: '60px', textAlign: 'center' }}>
                        <Empty description="No expiring certificates found" image={Empty.PRESENTED_IMAGE_SIMPLE} />
                    </div>
                )}
            </div>
        </div>
    );
};
