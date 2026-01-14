/**
 * Gap Analysis Results Table
 * Displays analysis results with color-coded status
 */

import { Table, Tag, Button, Space, message, Drawer, Typography, Image, Tooltip } from 'antd';
import { CheckCircleOutlined, WarningOutlined, CloseCircleOutlined, TagsOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { GapAnalysisResultItem } from '../../types/models.types';
import { formatDate } from '../../utils/formatters';
import { ColumnsType } from 'antd/es/table';
import apiClient from '../../services/api';
import { API_ENDPOINTS } from '../../config/api.config';
import { QUERY_KEYS } from '../../services/queryClient';

const { Title, Text, Paragraph } = Typography;

interface GapResultsTableProps {
  results: GapAnalysisResultItem[];
  deviceId: string;
  countryId: number;
  tenantId: string | null;
}

function GapResultsTable({ results, deviceId, countryId, tenantId }: GapResultsTableProps) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [creatingCertId, setCreatingCertId] = useState<number | null>(null);
  const [createdCertIds, setCreatedCertIds] = useState<Set<number>>(new Set());

  // Drawer state
  const [labelDrawerVisible, setLabelDrawerVisible] = useState(false);
  const [selectedLabel, setSelectedLabel] = useState<GroupedResult | null>(null);

  type GroupedResult = {
    certification_id: number;
    certification_name: string;
    technologies: string[];
    has_gap: boolean;
    status?: string;
    expiry_date?: string;
    compliance_record_id?: string;
    branding_image_url?: string;
    labeling_requirements?: string;
    open_tasks_count?: number;
  };

  // Group results by certification so each cert shows all technologies in one row
  const groupedResults: GroupedResult[] = Object.values(
    results.reduce<Record<number, GroupedResult>>((acc, item) => {
      const existing = acc[item.certification_id];
      if (!existing) {
        acc[item.certification_id] = {
          certification_id: item.certification_id,
          certification_name: item.certification_name,
          technologies: [item.technology],
          has_gap: item.has_gap,
          status: item.status,
          expiry_date: item.expiry_date,
          compliance_record_id: item.compliance_record_id,
          branding_image_url: item.branding_image_url,
          labeling_requirements: item.labeling_requirements,
          open_tasks_count: item.open_tasks_count || 0,
        };
        return acc;
      }
      // Merge technologies and keep unique
      if (!existing.technologies.includes(item.technology)) {
        existing.technologies.push(item.technology);
      }
      // If any entry has a gap, mark the certification as gap
      existing.has_gap = existing.has_gap || item.has_gap;
      // Prefer a non-empty status/expiry if present
      existing.status = existing.status || item.status;
      existing.expiry_date = existing.expiry_date || item.expiry_date;
      return acc;
    }, {})
  );

  const createRecordMutation = useMutation({
    mutationFn: async (certificationId: number) => {
      if (!tenantId) {
        throw new Error('Tenant not selected');
      }
      const payload = {
        device_id: deviceId,
        country_id: countryId,
        certification_id: certificationId,
        status: 'PENDING',
      };
      const response = await apiClient.post(
        `${API_ENDPOINTS.complianceRecords}?tenant_id=${tenantId}`,
        payload
      );
      return response.data;
    },
    onSuccess: (_data, certificationId) => {
      message.success('Compliance record created');
      setCreatedCertIds((prev) => {
        const next = new Set(prev);
        next.add(certificationId);
        return next;
      });
      if (tenantId) {
        // Invalidate all compliance record queries for this tenant (prefix match)
        // This ensures both the main dashboard and device-specific lists are refreshed
        queryClient.invalidateQueries({ queryKey: ['complianceRecords', tenantId] });
      }
    },
    onError: (error: any) => {
      message.error(error?.response?.data?.detail || 'Failed to create compliance record');
    },
    onSettled: () => {
      setCreatingCertId(null);
    },
  });

  const handleCreateRecord = (record: GroupedResult) => {
    if (creatingCertId) return;
    setCreatingCertId(record.certification_id);
    createRecordMutation.mutate(record.certification_id);
  };

  const showLabelInfo = (record: GroupedResult) => {
    setSelectedLabel(record);
    setLabelDrawerVisible(true);
  };

  const createTaskMutation = useMutation({
    mutationFn: async (recordId: string) => {
      const payload = {
        title: 'Compliance Testing', // Default title
        description: 'Initiated from Gap Analysis',
        status: 'TODO',
        record_id: recordId
      };
      const response = await apiClient.post(
        `${API_ENDPOINTS.complianceTasks(recordId)}?tenant_id=${tenantId}`,
        payload
      );
      return response.data;
    },
    onSuccess: (data) => {
      message.success('Testing Task Created');
      // Navigate to the task details or record details
      navigate(`/compliance/${data.record_id}`);
    },
    onError: (error: any) => {
      message.error('Failed to create task');
    }
  });

  const handleCreateTask = (recordId: string) => {
    createTaskMutation.mutate(recordId);
  }

  const columns: ColumnsType<GroupedResult> = [
    {
      title: 'Certification',
      dataIndex: 'certification_name',
      key: 'certification_name',
      width: 200,
    },
    {
      title: 'Technology',
      dataIndex: 'technologies',
      key: 'technologies',
      width: 200,
      render: (techs: string[]) => techs.join(', '),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status, record) => {
        if (record.has_gap) {
          return <Tag color="error" icon={<CloseCircleOutlined />}>MISSING</Tag>;
        }

        const colorMap: Record<string, string> = {
          ACTIVE: 'success',
          EXPIRING: 'warning',
          EXPIRED: 'error',
          PENDING: 'default',
        };

        return <Tag color={colorMap[status] || 'default'}>{status}</Tag>;
      },
    },
    {
      title: 'Expiry Date',
      dataIndex: 'expiry_date',
      key: 'expiry_date',
      width: 120,
      render: (date) => formatDate(date),
    },
    {
      title: 'Action',
      key: 'action',
      width: 250, // Increased width
      render: (_, record) => {
        const alreadyCreated = createdCertIds.has(record.certification_id) || !!record.compliance_record_id;
        const actionButtons = [];

        // Label Button
        actionButtons.push(
          <Button
            key="label"
            size="small"
            icon={<TagsOutlined />}
            onClick={() => showLabelInfo(record)}
            title="View Label Requirements"
          >
            Label
          </Button>
        );

        if (record.has_gap && !alreadyCreated) {
          actionButtons.push(
            <Button
              key="create"
              type="primary"
              size="small"
              loading={creatingCertId === record.certification_id && createRecordMutation.isPending}
              onClick={() => handleCreateRecord(record)}
            >
              Create Record
            </Button>
          );
        } else if (alreadyCreated && record.compliance_record_id) {
          actionButtons.push(
            <Button
              key="view"
              size="small"
              onClick={() => navigate(`/compliance/${record.compliance_record_id}`)}
            >
              Details
            </Button>
          );
        }

        return <Space>{actionButtons}</Space>;
      },
    },
  ];

  return (
    <>
      <Table
        columns={columns}
        dataSource={groupedResults}
        rowKey={(record) => `${record.certification_id}`}
        pagination={false}
        scroll={{ x: 800 }}
        rowClassName={(record) => {
          if (record.has_gap) return 'table-row-expired';
          if (record.status === 'ACTIVE') return 'table-row-active';
          if (record.status === 'EXPIRING') return 'table-row-expiring';
          if (record.status === 'PENDING') return 'table-row-pending';
          return '';
        }}
      />

      <Drawer
        title={`Label Requirements: ${selectedLabel?.certification_name}`}
        placement="right"
        width={500}
        onClose={() => setLabelDrawerVisible(false)}
        open={labelDrawerVisible}
      >
        {selectedLabel && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {selectedLabel.branding_image_url ? (
              <div style={{ position: 'relative' }}>
                <Title level={5}>Label Artwork</Title>
                <div style={{ padding: '20px', border: '1px dashed #d9d9d9', borderRadius: '4px', textAlign: 'center', background: '#fafafa', position: 'relative', overflow: 'hidden' }}>
                  {selectedLabel.status !== 'ACTIVE' && (
                    <div style={{
                      position: 'absolute',
                      top: '50%',
                      left: '50%',
                      transform: 'translate(-50%, -50%) rotate(-45deg)',
                      fontSize: '48px',
                      fontWeight: 'bold',
                      color: 'rgba(200, 0, 0, 0.2)',
                      zIndex: 10,
                      pointerEvents: 'none',
                      userSelect: 'none'
                    }}>
                      DRAFT
                    </div>
                  )}
                  <Image
                    src={selectedLabel.branding_image_url}
                    alt="Label Mark"
                    style={{ maxHeight: '150px', objectFit: 'contain', opacity: selectedLabel.status !== 'ACTIVE' ? 0.7 : 1 }}
                  />
                </div>
                {selectedLabel.status !== 'ACTIVE' && (
                  <div style={{ marginTop: 8, color: '#faad14' }}>
                    <WarningOutlined /> Warning: Certification not active. Do not print this label.
                  </div>
                )}
              </div>
            ) : (
              <div>
                <Title level={5}>Label Artwork</Title>
                <Text type="secondary">No official artwork available for this certification.</Text>
              </div>
            )}

            <div>
              <Title level={5}>Placement & Requirements</Title>
              {selectedLabel.labeling_requirements ? (
                <div style={{ background: '#f5f5f5', padding: '16px', borderRadius: '8px', whiteSpace: 'pre-wrap' }}>
                  {selectedLabel.labeling_requirements}
                </div>
              ) : (<Text type="secondary">No specific placement requirements available.</Text>
              )}
            </div>
          </div>
        )}
      </Drawer>
    </>
  );
}

export default GapResultsTable;


