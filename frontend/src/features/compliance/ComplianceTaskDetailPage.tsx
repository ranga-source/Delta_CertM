/**
 * Compliance Task Detail Page
 * Shows full task details and note history in a tree/timeline view.
 *
 * Modified to support direct access via ?record_id=... (Auto-selects first task)
 */

import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { Card, Descriptions, Tag, Button, Timeline, Form, Input, message, Spin, Empty, Typography } from 'antd';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import dayjs from 'dayjs';
import apiClient from '../../services/api';
import { API_ENDPOINTS } from '../../config/api.config';
import { QUERY_KEYS } from '../../services/queryClient';
import { ComplianceTask, ComplianceTaskNote, TaskStatus } from '../../types/models.types';
import { ArrowLeftOutlined, ClockCircleOutlined } from '@ant-design/icons';
import { useAppSelector } from '../../app/store';
import { useEffect, useState } from 'react';

const statusColor: Record<TaskStatus, string> = {
    TODO: 'default',
    IN_PROGRESS: 'processing',
    DONE: 'success',
};

function ComplianceTaskDetailPage() {
    const { taskId: paramTaskId } = useParams();
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const tenantId = useAppSelector(state => state.tenant.currentTenantId);
    const [messageApi, contextHolder] = message.useMessage();

    // Context: We might have a taskId (URL param) OR a record_id (Query param)
    // If we have taskId, we can find record_id from the task.
    // If we only have record_id, we need to find the List first, then pick the first task.

    const queryRecordId = searchParams.get('record_id');

    // 1. If we have taskId, fetch that specific task to get its record_id (and details)
    const { data: specificTask, isLoading: specificTaskLoading } = useQuery({
        queryKey: QUERY_KEYS.complianceTask(paramTaskId || ''),
        queryFn: async () => {
            const resp = await apiClient.get<ComplianceTask>(
                `${API_ENDPOINTS.complianceTask(paramTaskId!)}?tenant_id=${tenantId}`
            );
            return resp.data;
        },
        enabled: !!paramTaskId && !!tenantId,
    });

    // Determine effective Record ID
    const effectiveRecordId = specificTask?.record_id || queryRecordId;

    // 2. Fetch Sibling Tasks (Sidebar) - Needs Record ID
    const { data: taskList, isLoading: listLoading } = useQuery({
        queryKey: QUERY_KEYS.complianceTasks(effectiveRecordId || ''),
        queryFn: async () => {
            const resp = await apiClient.get<ComplianceTask[]>(
                `${API_ENDPOINTS.complianceTasks(effectiveRecordId!)}?tenant_id=${tenantId}`
            );
            return resp.data;
        },
        enabled: !!effectiveRecordId && !!tenantId,
    });

    // Determine Active Task ID
    // If param exists, use it.
    // If not, use first from list.
    const activeTaskId = paramTaskId || (taskList && taskList.length > 0 ? taskList[0].id : null);

    // 3. Fetch Selected Task Details (if no param but auto-selected)
    // We reuse specificTask if it matches, otherwise fetch fresh if needed (or rely on list data if sufficient?)
    // List data might be partial. Better to fetch full details if we auto-selected.
    const { data: selectedTaskDetails, isLoading: detailsLoading } = useQuery({
        queryKey: QUERY_KEYS.complianceTask(activeTaskId || ''),
        queryFn: async () => {
            if (specificTask && specificTask.id === activeTaskId) return specificTask;
            const resp = await apiClient.get<ComplianceTask>(
                `${API_ENDPOINTS.complianceTask(activeTaskId!)}?tenant_id=${tenantId}`
            );
            return resp.data;
        },
        enabled: !!activeTaskId && !!tenantId && (!specificTask || specificTask.id !== activeTaskId),
        initialData: specificTask?.id === activeTaskId ? specificTask : undefined
    });

    // 4. Fetch Notes for Active Task
    const { data: notes, isLoading: notesLoading } = useQuery({
        queryKey: QUERY_KEYS.complianceTaskNotes(activeTaskId || ''),
        queryFn: async () => {
            const resp = await apiClient.get<ComplianceTaskNote[]>(
                `${API_ENDPOINTS.complianceTaskNotes(activeTaskId!)}?tenant_id=${tenantId}`
            );
            return resp.data;
        },
        enabled: !!activeTaskId && !!tenantId,
    });

    const addNoteMutation = useMutation({
        mutationFn: async ({ note, author }: { note: string; author?: string }) => {
            const resp = await apiClient.post<ComplianceTaskNote>(
                `${API_ENDPOINTS.complianceTaskNotes(activeTaskId!)}?tenant_id=${tenantId}`,
                { note, author }
            );
            return resp.data;
        },
        onSuccess: () => {
            messageApi.success('Note added successfully');
            queryClient.invalidateQueries({ queryKey: QUERY_KEYS.complianceTask(activeTaskId!) });
            queryClient.invalidateQueries({ queryKey: QUERY_KEYS.complianceTaskNotes(activeTaskId!) });
        },
        onError: (error: any) => {
            messageApi.error(error?.response?.data?.detail || 'Failed to add note');
        },
    });

    // Loading State
    if (specificTaskLoading || listLoading && !taskList) {
        return <Spin style={{ marginTop: 40, display: 'block', margin: 'auto' }} />;
    }

    // Empty State (No tasks found for this record)
    if (taskList && taskList.length === 0) {
        return (
            <div style={{ padding: 24, maxWidth: 800, margin: '0 auto' }}>
                {contextHolder}
                <Button
                    icon={<ArrowLeftOutlined />}
                    onClick={() => navigate('/compliance?tab=records#records-list')}
                    style={{ marginBottom: 16 }}
                >
                    Back to Compliance Records
                </Button>
                <Card>
                    <Empty
                        image={Empty.PRESENTED_IMAGE_SIMPLE}
                        description="No tasks found for this compliance record."
                    >
                        <Button type="primary" onClick={() => navigate(`/compliance/${effectiveRecordId}`)}>
                            Go to Record Details to Create Task
                        </Button>
                    </Empty>
                </Card>
            </div>
        );
    }

    // If we have a list but no active task ID (shouldn't happen due to auto-select logic unless list empty)
    if (!activeTaskId && !listLoading) {
        return <Empty description="Task not found" />;
    }

    const currentTask = selectedTaskDetails || (taskList?.find(t => t.id === activeTaskId));

    return (
        <div style={{ padding: 24, maxWidth: 1400, margin: '0 auto' }}>
            {contextHolder}
            <Button
                icon={<ArrowLeftOutlined />}
                onClick={() => navigate('/compliance?tab=records#records-list')}
                style={{ marginBottom: 16 }}
            >
                Back to Compliance Records
            </Button>

            <div style={{ display: 'grid', gridTemplateColumns: '280px 1fr 400px', gap: 24, alignItems: 'start' }}>
                {/* Left Col: Tasks List Sidebar */}
                <Card title={`Tasks (${taskList?.length || 0})`} className="shadow-sm" bordered={false} bodyStyle={{ padding: '12px 0' }}>
                    <div style={{ maxHeight: 'calc(100vh - 250px)', overflowY: 'auto' }}>
                        {taskList?.map(t => (
                            <div
                                key={t.id}
                                onClick={() => navigate(`/compliance/tasks/${t.id}`)}
                                style={{
                                    padding: '12px 16px',
                                    borderLeft: t.id === activeTaskId ? '4px solid #1890ff' : '4px solid transparent',
                                    background: t.id === activeTaskId ? '#e6f7ff' : 'transparent',
                                    cursor: 'pointer',
                                    borderBottom: '1px solid #f0f0f0',
                                    transition: 'all 0.2s'
                                }}
                            >
                                <div style={{ fontWeight: t.id === activeTaskId ? 600 : 400, marginBottom: 4 }}>
                                    {t.title}
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <Tag color={statusColor[t.status]} style={{ marginRight: 0, fontSize: 10, lineHeight: '18px' }}>
                                        {t.status}
                                    </Tag>
                                    <span style={{ fontSize: 11, color: '#999' }}>
                                        {dayjs(t.created_at).format('MMM D')}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </Card>

                {/* Middle Col: Task Metadata */}
                <Card
                    title="Task Details"
                    className="shadow-sm"
                    bordered={false}
                    loading={detailsLoading && !currentTask}
                >
                    {currentTask ? (
                        <Descriptions column={1} bordered>
                            <Descriptions.Item label="Title">
                                <span style={{ fontWeight: 600, fontSize: 16 }}>{currentTask.title}</span>
                            </Descriptions.Item>
                            <Descriptions.Item label="Status">
                                <Tag color={statusColor[currentTask.status]}>{currentTask.status}</Tag>
                            </Descriptions.Item>
                            <Descriptions.Item label="Assignee">
                                {currentTask.assignee || 'Unassigned'}
                            </Descriptions.Item>
                            <Descriptions.Item label="Created At">
                                {dayjs(currentTask.created_at).format('MMMM D, YYYY h:mm A')}
                            </Descriptions.Item>
                            <Descriptions.Item label="Description">
                                <div style={{ whiteSpace: 'pre-wrap' }}>{currentTask.description || '-'}</div>
                            </Descriptions.Item>
                        </Descriptions>
                    ) : (
                        <Empty description="Select a task" />
                    )}
                </Card>

                {/* Right Col: Timeline/Notes */}
                <Card title="Activity & Notes" className="shadow-sm" bordered={false}>
                    <div style={{ maxHeight: 500, overflowY: 'auto', padding: '0 12px' }}>
                        <Timeline mode="left">
                            {notes && notes.length > 0 ? (
                                notes.map((note) => (
                                    <Timeline.Item
                                        key={note.id}
                                        dot={<ClockCircleOutlined style={{ fontSize: '16px' }} />}
                                        color="blue"
                                    >
                                        <Card size="small" style={{ marginBottom: 4 }} bordered={false}>
                                            <div style={{ whiteSpace: 'pre-wrap', marginBottom: 6 }}>{note.note}</div>
                                            <div style={{ fontSize: 12, color: '#999' }}>
                                                {note.author || 'User'} • {dayjs(note.created_at).format('MMM D, h:mm A')}
                                            </div>
                                        </Card>
                                    </Timeline.Item>
                                ))
                            ) : (
                                <div style={{ textAlign: 'center', color: '#999', padding: 20 }}>No notes yet.</div>
                            )}
                        </Timeline>
                    </div>

                    <div style={{ marginTop: 24, borderTop: '1px solid #eee', paddingTop: 16 }}>
                        <Form layout="vertical" onFinish={(values) => {
                            addNoteMutation.mutate({ note: values.note, author: values.author });
                        }}>
                            <Form.Item
                                name="author"
                                label="Your Name"
                                style={{ marginBottom: 12 }}
                                rules={[{ required: true, message: 'Please enter your name' }]}
                            >
                                <Input placeholder="e.g. John Doe" />
                            </Form.Item>
                            <Form.Item
                                name="note"
                                label="Add New Note"
                                style={{ marginBottom: 12 }}
                                rules={[{ required: true, message: 'Please enter a note' }]}
                            >
                                <Input.TextArea rows={3} placeholder="Type your update here..." />
                            </Form.Item>
                            <Form.Item>
                                <Button type="primary" htmlType="submit" loading={addNoteMutation.isPending} block>
                                    Post Note
                                </Button>
                            </Form.Item>
                        </Form>
                    </div>
                </Card>
            </div>
        </div>
    );
}

export default ComplianceTaskDetailPage;
