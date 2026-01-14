/**
 * Compliance Record Detail Page
 * Shows full compliance record info with document download link.
 */

import { useEffect } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { Card, Descriptions, Button, Space, Spin, Tag, message, Typography, Image } from 'antd';
import { useQuery, useMutation } from '@tanstack/react-query';
import apiClient from '../../services/api';
import { API_ENDPOINTS } from '../../config/api.config';
import { QUERY_KEYS } from '../../services/queryClient';
import { useAppSelector } from '../../app/store';
import { ComplianceRecord, CertificationLabel } from '../../types/models.types';
import { formatDate, formatDateTime, getStatusColor } from '../../utils/formatters';
import ComplianceTasksPanel from './ComplianceTasksPanel';
import { ComplianceStepper } from './components/ComplianceStepper';

function ComplianceRecordDetailPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { recordId } = useParams();
  const tenantId = useAppSelector(state => state.tenant.currentTenantId);

  // Fetch the selected compliance record.
  const { data: record, isLoading } = useQuery({
    queryKey: QUERY_KEYS.complianceRecord(recordId || ''),
    queryFn: async () => {
      const response = await apiClient.get<ComplianceRecord>(
        `${API_ENDPOINTS.complianceRecord(recordId!)}?tenant_id=${tenantId}`
      );
      return response.data;
    },
    enabled: !!recordId && !!tenantId,
  });

  // Fetch certification labels for matching
  const { data: labels } = useQuery<CertificationLabel[]>({
    queryKey: ['global_labels'],
    queryFn: async () => {
      const response = await apiClient.get<CertificationLabel[]>(`${API_ENDPOINTS.globalLabels}`);
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
  });

  // Find matching label
  // Find matching label using fuzzy logic
  const matchingLabel = record && labels?.find(l => {
    const certName = record.certification_name?.toLowerCase() || '';
    const labelName = l.name.toLowerCase();

    // 1. Exact or Partial Name Match
    // Matches "CE" with "CE Mark", "FCC" with "FCC Label", "KC" with "KC Mark"
    if (labelName === certName || labelName.includes(certName) || certName.includes(labelName)) return true;

    // 2. Explicit Mappings
    if (certName === 'telec' && labelName.includes('giteki')) return true;
    if (certName.includes('fcc') && labelName.includes('fcc')) return true;
    if (certName === 'wpc' && labelName.includes('bis')) return false; // WPC != BIS. Explicitly exclude if ambiguous.

    // 3. Country Match + Region Match
    if (l.requirements?.region === 'EU' && record.certification_name === 'CE') return true;

    // 4. Fallback: If country matches and we haven't ruled it out
    // (Use with caution if multiple labels exist per country)
    if (l.country_id === record.country_id) {
      // If it's the only label for that country, likely good.
      return true;
    }

    return false;
  });

  // Fetch a presigned document URL when user clicks download.
  const downloadMutation = useMutation<any, Error, string>({
    mutationFn: async (docType: string) => {
      const response = await apiClient.get(
        `${API_ENDPOINTS.downloadDocument(recordId!)}?tenant_id=${tenantId}&doc_type=${docType}`
      );
      return response.data;
    },
    onSuccess: (data: any) => {
      if (data?.document_url) {
        window.open(data.document_url, '_blank');
      } else {
        message.warning('No download URL available');
      }
    },
    onError: (error: any) => {
      message.error(error?.response?.data?.detail || 'Failed to get download link');
    },
  });

  // Fetch labeling picture URL if exists
  const { data: labelPictureUrl } = useQuery({
    queryKey: ['label_picture', recordId],
    queryFn: async () => {
      const response = await apiClient.get(
        `${API_ENDPOINTS.downloadDocument(recordId!)}?tenant_id=${tenantId}&doc_type=label_picture`
      );
      return response.data.document_url as string;
    },
    enabled: !!recordId && !!tenantId && !!record?.labeling_picture_filename,
  });

  // Handle scroll to section if query param is present
  const searchParams = new URLSearchParams(location.search);
  const scrollTo = searchParams.get('scrollTo');

  useEffect(() => {
    if (scrollTo === 'labeling' && record && matchingLabel) {
      setTimeout(() => {
        const element = document.getElementById('labeling-section');
        if (element) {
          element.scrollIntoView({ behavior: 'smooth' });
        }
      }, 500); // Delay for card render
    }
  }, [scrollTo, record, matchingLabel]);


  if (isLoading) {
    return <Spin style={{ marginTop: 32 }} />;
  }

  if (!record) {
    return <Card title="Compliance Record"><p>Record not found.</p></Card>;
  }

  return (
    <Card
      title="Compliance Record Details"
      extra={
        <Space>
          <Button onClick={() => navigate('/compliance?tab=records#records-list')}>Back</Button>
          <Button type="primary" onClick={() => navigate(`/compliance/${recordId}/edit`)}>
            Edit
          </Button>
        </Space>
      }
    >
      <div style={{ marginBottom: 24 }}>
        <ComplianceStepper status={record.status} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 400px', gap: '24px' }}>
        <div>
          <Card title="Details" bordered={false} className="shadow-sm">
            <Descriptions column={1} bordered>
              <Descriptions.Item label="Device">{record.device_name || record.device_id}</Descriptions.Item>
              <Descriptions.Item label="Country">{record.country_name || record.country_id}</Descriptions.Item>
              <Descriptions.Item label="Certification">{record.certification_name || record.certification_id}</Descriptions.Item>
              <Descriptions.Item label="Status">
                <Tag color={getStatusColor(record.status)}>{record.status}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Labeling Status">
                <Space direction="vertical" size={0}>
                  <Tag color={record.labeling_status === 'DONE' ? 'green' : 'blue'}>
                    {record.labeling_status || 'PENDING'}
                  </Tag>
                  {record.labeling_updated_at && (
                    <span style={{ fontSize: '11px', color: '#8c8c8c' }}>
                      Last updated: {formatDateTime(record.labeling_updated_at)}
                    </span>
                  )}
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="Expiry Date">{formatDate(record.expiry_date)}</Descriptions.Item>
              <Descriptions.Item label="Certificate Number">{record.certificate_number || '-'}</Descriptions.Item>
              <Descriptions.Item label="Document">
                {record.document_filename ? (
                  <Space>
                    <span>{record.document_filename}</span>
                    <Button
                      type="link"
                      onClick={() => downloadMutation.mutate('certificate')}
                      loading={downloadMutation.isPending && downloadMutation.variables === 'certificate'}
                    >
                      Download
                    </Button>
                  </Space>
                ) : (
                  '-'
                )}
              </Descriptions.Item>
              <Descriptions.Item label="Test Report">
                {record.test_report_filename ? (
                  <Space>
                    <span>{record.test_report_filename}</span>
                    <Button
                      type="link"
                      onClick={() => downloadMutation.mutate('test_report')}
                      loading={downloadMutation.isPending && downloadMutation.variables === 'test_report'}
                    >
                      Download
                    </Button>
                  </Space>
                ) : (
                  '-'
                )}
              </Descriptions.Item>
              <Descriptions.Item label="Created At">{formatDate(record.created_at)}</Descriptions.Item>
              <Descriptions.Item label="Updated At">{formatDate(record.updated_at)}</Descriptions.Item>
            </Descriptions>
          </Card>

          {/* Labeling Info - Show only if ACTIVE and label exists */}
          {record.status === 'ACTIVE' && matchingLabel && (
            <Card id="labeling-section" title="Labelling Requirements" bordered={false} className="shadow-sm" style={{ marginTop: 24 }}>
              <div style={{ display: 'grid', gridTemplateColumns: labelPictureUrl ? '1fr 300px' : '1fr', gap: '24px' }}>
                <div>
                  <div style={{ textAlign: 'center', marginBottom: 16 }}>
                    {matchingLabel.image_url ? (
                      <img src={matchingLabel.image_url} alt={matchingLabel.name} style={{ maxHeight: 100, maxWidth: '100%' }} />
                    ) : (
                      <div style={{ padding: 20, background: '#f5f5f5', borderRadius: 8 }}>No Image</div>
                    )}
                    <div style={{ marginTop: 8, fontWeight: 'bold' }}>{matchingLabel.name}</div>
                  </div>

                  <Descriptions column={1} size="small" bordered>
                    {matchingLabel.requirements?.min_height && (
                      <Descriptions.Item label="Min Size">{matchingLabel.requirements.min_height}</Descriptions.Item>
                    )}
                    {matchingLabel.requirements?.placement && (
                      <Descriptions.Item label="Placement">{matchingLabel.requirements.placement}</Descriptions.Item>
                    )}
                    {matchingLabel.requirements?.content && (
                      <Descriptions.Item label="Content">{matchingLabel.requirements.content}</Descriptions.Item>
                    )}
                    {matchingLabel.requirements?.visibility && (
                      <Descriptions.Item label="Visibility">{matchingLabel.requirements.visibility}</Descriptions.Item>
                    )}
                  </Descriptions>

                  {matchingLabel.description && (
                    <div style={{ marginTop: 16, color: '#666', fontSize: 12 }}>
                      {matchingLabel.description}
                    </div>
                  )}
                </div>

                {labelPictureUrl && (
                  <div style={{ borderLeft: '1px solid #f0f0f0', paddingLeft: 24 }}>
                    <Typography.Title level={5} style={{ fontSize: '14px', marginBottom: 16 }}>Uploaded Label Proof</Typography.Title>
                    <div style={{ background: '#fafafa', borderRadius: 8, padding: 12, textAlign: 'center', border: '1px dashed #d9d9d9' }}>
                      {record.labeling_picture_mime_type?.includes('pdf') ? (
                        <div style={{ padding: '20px 0' }}>
                          <Typography.Text type="secondary" style={{ display: 'block', marginBottom: 12 }}>PDF Document</Typography.Text>
                          <Button
                            type="primary"
                            icon={<Typography.Text style={{ color: 'white' }}>📄</Typography.Text>}
                            onClick={() => window.open(labelPictureUrl, '_blank')}
                          >
                            View PDF
                          </Button>
                        </div>
                      ) : (
                        <Image
                          src={labelPictureUrl}
                          alt="Uploaded Label"
                          style={{ maxWidth: '100%', borderRadius: 4, cursor: 'pointer' }}
                        />
                      )}
                      <div style={{ marginTop: 8, fontSize: '11px', color: '#8c8c8c' }}>
                        {record.labeling_picture_filename}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </Card>
          )}
        </div>

        <div>
          {record.status !== 'ACTIVE' && (
            <ComplianceTasksPanel
              recordId={record.id}
              tenantId={tenantId}
              recordStatus={record.status}
              initialProgress={record.task_progress_percent}
            />
          )}
        </div>
      </div>
    </Card >
  );
}

export default ComplianceRecordDetailPage;


