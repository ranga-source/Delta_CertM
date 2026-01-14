import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { Typography, Spin, Empty } from 'antd';
import { useQuery } from '@tanstack/react-query';
import apiClient from '../../../../services/api';
import { API_ENDPOINTS } from '../../../../config/api.config';
import { QUERY_KEYS } from '../../../../services/queryClient';
import { useAppSelector } from '../../../../app/store';
import { ComplianceRecord } from '../../../../types/models.types';

const { Title } = Typography;

export const ComplianceStatsChart: React.FC = () => {
    const currentTenantId = useAppSelector(state => state.tenant.currentTenantId);

    const { data: records, isLoading } = useQuery({
        queryKey: QUERY_KEYS.complianceRecords(currentTenantId || ''),
        queryFn: async () => {
            if (!currentTenantId) return [];
            // Fetch ALL records for stats
            const url = `${API_ENDPOINTS.complianceRecords}?tenant_id=${currentTenantId}`;
            const response = await apiClient.get<ComplianceRecord[]>(url);
            return response.data;
        },
        enabled: !!currentTenantId,
    });

    const chartData = React.useMemo(() => {
        if (!records) return [];

        let active = 0;
        let pending = 0;
        let expired = 0;
        let missing = 0;

        records.forEach(r => {
            const status = r.status.toUpperCase();
            if (status === 'ACTIVE') active++;
            else if (status === 'IN_PROGRESS' || status === 'PENDING') pending++;
            else if (status === 'EXPIRED') expired++;
            else if (status === 'DRAFT' || status === 'MISSING') missing++;
        });

        const total = active + pending + expired + missing;
        if (total === 0) return [];

        return [
            { name: 'Active', value: active, color: '#52c41a' },
            { name: 'Pending', value: pending, color: '#faad14' },
            { name: 'Expired', value: expired, color: '#ff4d4f' },
            { name: 'Draft/Missing', value: missing, color: '#d9d9d9' },
        ].filter(d => d.value > 0); // Only show segments with data
    }, [records]);

    const totalRecords = React.useMemo(() => records?.length || 0, [records]);

    return (
        <div style={{ background: '#fff', padding: '24px', borderRadius: '12px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)', height: '100%', border: '1px solid #f0f0f0' }}>
            <Title level={5} style={{ marginBottom: '24px', color: '#595959', textTransform: 'uppercase', letterSpacing: '1px', fontSize: '13px' }}>Certification Status</Title>
            {isLoading ? (
                <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 250 }}>
                    <Spin />
                </div>
            ) : chartData.length > 0 ? (
                <div style={{ width: '100%', height: 280, position: 'relative' }}>
                    <div style={{
                        position: 'absolute',
                        top: '50%',
                        left: '50%',
                        transform: 'translate(-50%, -50%)',
                        textAlign: 'center',
                        marginTop: '-18px'
                    }}>
                        <div style={{ fontSize: '24px', fontWeight: 700, color: '#262626' }}>{totalRecords}</div>
                        <div style={{ fontSize: '12px', color: '#8c8c8c', textTransform: 'uppercase' }}>Total</div>
                    </div>
                    <ResponsiveContainer>
                        <PieChart>
                            <Pie
                                data={chartData}
                                cx="50%"
                                cy="50%"
                                innerRadius={70}
                                outerRadius={85}
                                paddingAngle={8}
                                dataKey="value"
                                cornerRadius={4}
                            >
                                {chartData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.color} stroke="none" />
                                ))}
                            </Pie>
                            <Tooltip
                                contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                            />
                            <Legend
                                verticalAlign="bottom"
                                height={36}
                                iconType="circle"
                                formatter={(value) => <span style={{ color: '#595959', fontSize: '12px' }}>{value}</span>}
                            />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
            ) : (
                <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 250 }}>
                    <Empty description="No data available" image={Empty.PRESENTED_IMAGE_SIMPLE} />
                </div>
            )}
        </div>
    );
};
