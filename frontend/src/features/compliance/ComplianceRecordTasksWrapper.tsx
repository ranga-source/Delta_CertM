/**
 * Compliance Record Tasks Wrapper
 * ===============================
 * Redirects to the first task of a record, or shows an empty state.
 * This acts as the entry point for "View Tasks" from the dashboard.
 */

import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Spin, Card, Button, Empty, Typography } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import apiClient from '../../services/api';
import { API_ENDPOINTS } from '../../config/api.config';
import { QUERY_KEYS } from '../../services/queryClient';
import { ComplianceTask } from '../../types/models.types';
import { useAppSelector } from '../../app/store';

function ComplianceRecordTasksWrapper() {
    const { recordId } = useParams();
    const navigate = useNavigate();
    const tenantId = useAppSelector(state => state.tenant.currentTenantId);

    const { data: tasks, isLoading } = useQuery({
        queryKey: QUERY_KEYS.complianceTasks(recordId || ''),
        queryFn: async () => {
            const resp = await apiClient.get<ComplianceTask[]>(
                `${API_ENDPOINTS.complianceTasks(recordId!)}?tenant_id=${tenantId}`
            );
            return resp.data;
        },
        enabled: !!recordId && !!tenantId,
    });

    useEffect(() => {
        if (tasks && tasks.length > 0) {
            // Redirect to the first task (most recent or first in list)
            // Usually tasks are ordered by creation or priority. Backend order is preserved.
            navigate(`/compliance/tasks/${tasks[0].id}`, { replace: true });
        }
    }, [tasks, navigate]);

    if (isLoading) {
        return <Spin style={{ marginTop: 50, display: 'block', margin: 'auto' }} />;
    }

    // If we are here, it means no tasks were found (or still loading first render before redirect)
    // We check tasks length to be sure.
    if (tasks && tasks.length > 0) {
        return <Spin style={{ marginTop: 50, display: 'block', margin: 'auto' }} tip="Redirecting..." />;
    }

    return (
        <div style={{ padding: 24, paddingBottom: 50, maxWidth: 800, margin: '0 auto' }}>
            <Button
                icon={<ArrowLeftOutlined />}
                onClick={() => navigate('/compliance?tab=records')}
                style={{ marginBottom: 16 }}
            >
                Back to Records
            </Button>

            <Card title="Compliance Tasks">
                <Empty
                    image={Empty.PRESENTED_IMAGE_SIMPLE}
                    description={
                        <div style={{ padding: 20 }}>
                            <Typography.Title level={4}>No Tasks Found</Typography.Title>
                            <Typography.Paragraph>
                                There are no active tasks for this compliance record.
                            </Typography.Paragraph>
                            <Button type="primary" onClick={() => navigate(`/compliance/${recordId}`)}>
                                Go to Record Details to Create Task
                            </Button>
                        </div>
                    }
                />
            </Card>
        </div>
    );
}

export default ComplianceRecordTasksWrapper;
