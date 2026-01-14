/**
 * Compliance Tasks Panel
 * Shows tasks, progress, notes for a compliance record.
 */

import { useMemo, useState } from 'react';
import { Card, Progress, List, Tag, Button, Space, Form, Input, Select, Collapse, message, Modal } from 'antd';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import dayjs from 'dayjs';
import apiClient from '../../services/api';
import { API_ENDPOINTS } from '../../config/api.config';
import { QUERY_KEYS } from '../../services/queryClient';
import { ComplianceTask, ComplianceTaskNote, TaskStatus } from '../../types/models.types';
import { useNavigate } from 'react-router-dom';

type Props = {
  recordId: string;
  tenantId: string | null;
  recordStatus: string;
  initialProgress?: number;
};

const statusOptions = [
  { label: 'To Do', value: 'TODO' },
  { label: 'In Progress', value: 'IN_PROGRESS' },
  { label: 'Done', value: 'DONE' },
];

const statusColor: Record<TaskStatus, string> = {
  TODO: 'default',
  IN_PROGRESS: 'processing',
  DONE: 'success',
};

function TaskNotes({ taskId, tenantId, visible }: { taskId: string; tenantId: string | null; visible: boolean }) {
  const query = useQuery({
    queryKey: QUERY_KEYS.complianceTaskNotes(taskId),
    queryFn: async () => {
      const resp = await apiClient.get<ComplianceTaskNote[]>(
        `${API_ENDPOINTS.complianceTaskNotes(taskId)}?tenant_id=${tenantId}`
      );
      return resp.data;
    },
    enabled: visible && !!tenantId,
  });

  return (
    <List
      size="small"
      dataSource={query.data || []}
      loading={query.isFetching}
      renderItem={(note) => (
        <List.Item>
          <Space direction="vertical" size={2}>
            <div style={{ whiteSpace: 'pre-wrap' }}>{note.note}</div>
            <div style={{ fontSize: 12, color: '#888' }}>
              {note.author || 'User'} • {dayjs(note.created_at).format('YYYY-MM-DD HH:mm')}
            </div>
          </Space>
        </List.Item>
      )}
      locale={{ emptyText: 'No notes' }}
    />
  );
}

function ComplianceTasksPanel({ recordId, tenantId, recordStatus, initialProgress }: Props) {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const [drawerTask, setDrawerTask] = useState<ComplianceTask | null>(null);
  const [messageApi, contextHolder] = message.useMessage();

  const { data: tasks, isLoading } = useQuery({
    queryKey: QUERY_KEYS.complianceTasks(recordId),
    queryFn: async () => {
      const resp = await apiClient.get<ComplianceTask[]>(
        `${API_ENDPOINTS.complianceTasks(recordId)}?tenant_id=${tenantId}`
      );
      return resp.data;
    },
    enabled: !!recordId && !!tenantId,
  });

  const createTaskMutation = useMutation({
    mutationFn: async (values: any) => {
      const resp = await apiClient.post<ComplianceTask>(
        `${API_ENDPOINTS.complianceTasks(recordId)}?tenant_id=${tenantId}`,
        values
      );
      return resp.data;
    },
    onSuccess: () => {
      messageApi.success('Task created');
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.complianceTasks(recordId) });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.complianceRecord(recordId) });
      // Refresh global records list to update progress/counts
      queryClient.invalidateQueries({ queryKey: ['complianceRecords'] });
    },
    onError: (error: any) => {
      messageApi.error(error?.response?.data?.detail || 'Failed to create task');
    },
  });

  const updateTaskMutation = useMutation({
    mutationFn: async ({ taskId, data }: { taskId: string; data: any }) => {
      const resp = await apiClient.put<ComplianceTask>(
        `${API_ENDPOINTS.complianceTask(taskId)}?tenant_id=${tenantId}`,
        data
      );
      return resp.data;
    },
    onSuccess: (_data, vars) => {
      messageApi.success('Task status updated');
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.complianceTasks(recordId) });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.complianceTask(vars.taskId) });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.complianceRecord(recordId) });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.complianceTaskNotes(vars.taskId) });
      // Refresh global records list to update progress/counts
      queryClient.invalidateQueries({ queryKey: ['complianceRecords'] });
    },
    onError: (error: any) => {
      messageApi.error(error?.response?.data?.detail || 'Failed to update task');
    },
  });

  const addNoteMutation = useMutation({
    mutationFn: async ({ taskId, note }: { taskId: string; note: string }) => {
      const resp = await apiClient.post<ComplianceTaskNote>(
        `${API_ENDPOINTS.complianceTaskNotes(taskId)}?tenant_id=${tenantId}`,
        { note }
      );
      return resp.data;
    },
    onSuccess: (_data, vars) => {
      messageApi.success('Note added');
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.complianceTaskNotes(vars.taskId) });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.complianceTask(vars.taskId) });
    },
    onError: (error: any) => {
      messageApi.error(error?.response?.data?.detail || 'Failed to add note');
    },
  });

  const progressPercent = useMemo(() => {
    if (tasks && tasks.length > 0) {
      const done = tasks.filter(t => t.status === 'DONE').length;
      return Math.round((done / tasks.length) * 100);
    }
    return initialProgress ?? 0;
  }, [tasks, initialProgress]);

  const taskCounts = useMemo(() => {
    const counts = { total: 0, done: 0, in_progress: 0, pending: 0 };
    (tasks || []).forEach((t) => {
      counts.total += 1;
      if (t.status === 'DONE') counts.done += 1;
      else if (t.status === 'IN_PROGRESS') counts.in_progress += 1;
      else counts.pending += 1;
    });
    return counts;
  }, [tasks]);

  const disableCreate = recordStatus === 'ACTIVE';

  return (
    <div style={{ marginTop: 0 }}>
      {contextHolder}
      {/* Header Section */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h3 style={{ margin: 0 }}>Tasks ({taskCounts.total})</h3>
        {!disableCreate && (
          <Button type="primary" onClick={() => setDrawerTask({} as any)}> {/* Hack to trigger modal, using separate state would be cleaner but this works with existing drawer logic if we adapt it, or better: use a new state */}
            + Add Task
          </Button>
        )}
      </div>

      <Progress percent={progressPercent} strokeColor={{ '0%': '#108ee9', '100%': '#87d068' }} />

      <div style={{ marginTop: 16 }}>
        {!tasks || tasks.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '20px', color: '#999' }}>No tasks</div>
        ) : (
          tasks.map((task) => (
            <Card
              key={task.id}
              size="small"
              style={{ marginBottom: 12, borderRadius: 8 }}
              variant="borderless"
              className="border border-gray-100 shadow-sm" // Assuming tailwind or custom css exists? if not, stick to inline styles or just leave variant borderless and rely on antd default
              // Actually user has no tailwind mentioned. Let's use clean inline for safe border.
              styles={{ body: { padding: '12px' } }}
            // Manually adding border style since variant="borderless" removes it but we might want a light one
            >
              <div style={{ border: '1px solid #f0f0f0', borderRadius: 8, padding: 12 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                      <span style={{ fontWeight: 600, fontSize: 14 }}>{task.title}</span>
                      <Tag color={statusColor[task.status]} style={{ margin: 0 }}>{task.status}</Tag>
                    </div>
                    <div style={{ color: '#666', fontSize: 13, marginBottom: 8 }}>
                      {task.description}
                    </div>

                    <div style={{ display: 'flex', gap: 12, fontSize: 12, color: '#999' }}>
                      {task.assignee && <span>👤 {task.assignee}</span>}
                      <span>📅 {dayjs(task.created_at).format('MMM D')}</span>
                    </div>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8, alignItems: 'flex-end' }}>
                    <Select
                      size="small"
                      value={task.status}
                      style={{ width: 110 }}
                      onChange={(val) => updateTaskMutation.mutate({ taskId: task.id, data: { status: val } })}
                      options={statusOptions}
                    />
                    <Button
                      size="small"
                      type="text"
                      style={{ color: '#1890ff', padding: 0 }}
                      onClick={() => navigate(`/compliance/tasks/${task.id}`)}
                    >
                      View Details →
                    </Button>
                  </div>
                </div>
              </div>
            </Card>
          ))
        )}
      </div>

      {/* Create Task Modal */}
      <Modal
        title="Create New Task"
        open={!!drawerTask && !drawerTask.id} // Open if drawerTask is set but has no ID (new task)
        onCancel={() => setDrawerTask(null)}
        footer={null}
      >
        <Form layout="vertical" onFinish={(values) => {
          createTaskMutation.mutate(values);
          setDrawerTask(null);
        }}>
          <Form.Item label="Title" name="title" rules={[{ required: true, message: 'Enter title' }]}>
            <Input placeholder="e.g., Submit test report" />
          </Form.Item>
          <Form.Item label="Description" name="description">
            <Input.TextArea rows={3} placeholder="Describe the work" />
          </Form.Item>
          <Form.Item label="Assignee" name="assignee">
            <Input placeholder="Assignee name" />
          </Form.Item>
          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Button onClick={() => setDrawerTask(null)} style={{ marginRight: 8 }}>Cancel</Button>
            <Button type="primary" htmlType="submit" loading={createTaskMutation.isPending}>
              Create Task
            </Button>
          </Form.Item>
        </Form>
      </Modal>

      {/* View Task Drawer Removed - moved to dedicated page */}
    </div>
  );
}

export default ComplianceTasksPanel;


