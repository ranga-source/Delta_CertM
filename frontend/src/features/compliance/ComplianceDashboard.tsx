/**
 * Compliance Dashboard
 * Overview of all compliance records with filtering
 */

import { useMemo, useState, useEffect } from 'react';
import { Typography, Card, Row, Col, Statistic, Table, Tag, Select, Button, Space, Tabs, Alert, Modal, message, Segmented } from 'antd';
import { SafetyOutlined, ClockCircleOutlined, WarningOutlined, CloseCircleOutlined, GlobalOutlined, CheckCircleOutlined, FileSyncOutlined, DownloadOutlined, ExportOutlined, CloseOutlined, AppstoreOutlined, BarsOutlined, BarChartOutlined, EyeOutlined, EditOutlined } from '@ant-design/icons';
import { ExpiringWatchlist } from './components/dashboard/ExpiringWatchlist';
import { ComplianceStatsChart } from './components/dashboard/ComplianceStatsChart';
import { GlobalComplianceMap } from './components/dashboard/GlobalComplianceMap';
import { useQuery } from '@tanstack/react-query';
import { useSearchParams, useNavigate, useLocation } from 'react-router-dom';
import apiClient from '../../services/api';
import { API_ENDPOINTS } from '../../config/api.config';
import { QUERY_KEYS } from '../../services/queryClient';
import { useAppSelector } from '../../app/store';
import { ComplianceRecord, ComplianceStatus } from '../../types/models.types';
import { formatDate, formatDateTime, getStatusColor } from '../../utils/formatters';
import DeviceCountryProgress from './DeviceCountryProgress';
import dayjs from 'dayjs';
import './compliance.css';

function ComplianceDashboard() {
  const currentTenantId = useAppSelector(state => state.tenant.currentTenantId);
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();

  // State for filters
  const [statusFilter, setStatusFilter] = useState<string | undefined>();
  const [deviceFilter, setDeviceFilter] = useState<string | undefined>(); // Helper for drill-down
  const [countryFilter, setCountryFilter] = useState<number | undefined>(); // Helper for drill-down
  const [activeTab, setActiveTab] = useState(searchParams.get('tab') || 'dashboard');
  const [isGroupedByDevice, setIsGroupedByDevice] = useState(false);
  const [expandedRowKeys, setExpandedRowKeys] = useState<React.Key[]>([]);

  // State for document preview
  const [previewDoc, setPreviewDoc] = useState<{ url: string; title: string; } | null>(null);

  const handlePreview = async (recordId: string, docType: 'certificate' | 'test_report', title: string) => {
    try {
      const response = await apiClient.get<{ document_url: string; expires_in: number }>(
        `${API_ENDPOINTS.downloadDocument(recordId)}?tenant_id=${currentTenantId}&doc_type=${docType}`
      );
      if (response.data.document_url) {
        setPreviewDoc({
          url: response.data.document_url,
          title: title
        });
      } else {
        message.error("No document URL returned");
      }
    } catch (e) {
      console.error("Failed to get document URL:", e);
      message.error("Failed to load document");
    }
  };

  // 1. Fetch Global Data for Stats (Unfiltered)
  const { data: allRecords } = useQuery({
    queryKey: QUERY_KEYS.complianceRecords(currentTenantId || ''),
    queryFn: async () => {
      if (!currentTenantId) return [];
      const url = `${API_ENDPOINTS.complianceRecords}?tenant_id=${currentTenantId}&limit=1000`; // Fetch all for stats
      const response = await apiClient.get<ComplianceRecord[]>(url);
      return response.data;
    },
    enabled: !!currentTenantId,
    staleTime: 5 * 60 * 1000,
  });

  // 2. Fetch Filtered Data for Table View
  const { data: records, isLoading } = useQuery({
    queryKey: QUERY_KEYS.complianceRecords(currentTenantId || '', { status: statusFilter, device_id: deviceFilter, country_id: countryFilter }),
    queryFn: async () => {
      let url = `${API_ENDPOINTS.complianceRecords}?tenant_id=${currentTenantId}&limit=1000`;
      if (statusFilter) url += `&status_filter=${statusFilter}`;
      if (deviceFilter) url += `&device_id=${deviceFilter}`;
      if (countryFilter) url += `&country_id=${countryFilter}`;

      const response = await apiClient.get<ComplianceRecord[]>(url);
      return response.data;
    },
    enabled: !!currentTenantId,
  });



  // Calculate stats from ALL records (ignoring current filters to keep dashboard stable)
  // Note: This requires a separate query or assuming 'records' contains enough data. 
  // Ideally, we stand up a /stats endpoint. For now, we use the current dataset.
  // Calculate stats from ALL records
  const stats = useMemo(() => {
    const source = allRecords || [];
    const uniqueCountries = new Set(source.map(r => r.country_name).filter(Boolean));
    const active = source.filter(r => r.status === ComplianceStatus.ACTIVE).length;
    const expired = source.filter(r => r.status === ComplianceStatus.EXPIRED).length;
    const pending = source.filter(r => r.status === ComplianceStatus.PENDING).length;

    // Recalculate expiring based on date if status isn't reliable yet
    const calculatedExpiring = source.filter(r => {
      if (!r.expiry_date || r.status === ComplianceStatus.EXPIRED) return false;
      const diff = dayjs(r.expiry_date).diff(dayjs(), 'day');
      return diff >= 0 && diff <= 30;
    }).length;
    const expiring = source.filter(r => r.status === ComplianceStatus.EXPIRING).length;

    return {
      markets: uniqueCountries.size,
      active,
      expiring: Math.max(expiring, calculatedExpiring),
      expired,
      gaps: expired + pending // Simplified gaps calculation
    };
  }, [allRecords]);

  const filteredRecords = useMemo(() => {
    if (!records) return [];
    // If backend sorting/filtering is used, 'records' is already filtered.
    // If we want purely client side filtering on top of a larger fetch:
    // return records.filter... 
    // Since we pass params to backend, 'records' IS the filtered list.
    // But for the stats to be correct, we shouldn't filter the MAIN query if we want global stats.
    // Compromise: We will rely on backend filtering for the List, but this breaks "Global Stats".
    // FIX: We will just display stats for the "Current View" or accept that without a separate stats endpoint, 
    // displaying stats based on filtered data is the expected behavior for this architecture.
    return records;
  }, [records]);

  const isExpiringSoon = (record: ComplianceRecord) => {
    if (!record.expiry_date) return false;
    const today = dayjs();
    const expiry = dayjs(record.expiry_date);
    const diff = expiry.diff(today, 'day');
    return diff >= 0 && diff <= 30;
  };

  const handleDrillDown = (filters: { deviceId?: string; countryId?: number; status?: string }) => {
    if (filters.deviceId) setDeviceFilter(filters.deviceId);
    if (filters.countryId) setCountryFilter(filters.countryId);
    if (filters.status) setStatusFilter(filters.status);
    setActiveTab('records');
  };

  const clearFilters = () => {
    setStatusFilter(undefined);
    setDeviceFilter(undefined);
    setCountryFilter(undefined);
  };

  // Grouped Data Derivation
  const groupedData = useMemo(() => {
    if (!isGroupedByDevice) return [];

    // Group records by device_id (or device_name)
    const groups: Record<string, ComplianceRecord[]> = {};
    filteredRecords.forEach(r => {
      const key = r.device_name || 'Unknown Device';
      if (!groups[key]) groups[key] = [];
      groups[key].push(r);
    });

    // Transform to array
    return Object.entries(groups).map(([deviceName, records]) => {
      return {
        key: deviceName,
        device_name: deviceName,
        total: records.length,
        active: records.filter(r => r.status === ComplianceStatus.ACTIVE).length,
        pending: records.filter(r => r.status === ComplianceStatus.PENDING).length,
        expiring: records.filter(r => r.status === ComplianceStatus.EXPIRING).length,
        expired: records.filter(r => r.status === ComplianceStatus.EXPIRED).length,
        childrenRecords: records, // Store records for nested table
      };
    });
  }, [filteredRecords, isGroupedByDevice]);

  // Group Columns
  const groupColumns = [
    { title: 'Device Name', dataIndex: 'device_name', key: 'device_name' },
    { title: 'Total Records', dataIndex: 'total', key: 'total' },
    { title: 'Active', dataIndex: 'active', key: 'active', render: (val: number) => val > 0 ? <Tag color="success">{val}</Tag> : '-' },
    { title: 'Pending', dataIndex: 'pending', key: 'pending', render: (val: number) => val > 0 ? <Tag color="warning">{val}</Tag> : '-' },
    { title: 'Expiring', dataIndex: 'expiring', key: 'expiring', render: (val: number) => val > 0 ? <Tag color="warning">{val}</Tag> : '-' },
    { title: 'Expired', dataIndex: 'expired', key: 'expired', render: (val: number) => val > 0 ? <Tag color="error">{val}</Tag> : '-' },
  ];

  const columns = [
    {
      title: 'Device',
      dataIndex: 'device_name',
      key: 'device_name',
      sorter: (a: any, b: any) => (a.device_name || '').localeCompare(b.device_name || ''),
    },
    {
      title: 'Country',
      dataIndex: 'country_name',
      key: 'country_name',
      sorter: (a: any, b: any) => (a.country_name || '').localeCompare(b.country_name || ''),
    },
    {
      title: 'Certification',
      dataIndex: 'certification_name',
      key: 'certification_name',
      sorter: (a: any, b: any) => (a.certification_name || '').localeCompare(b.certification_name || ''),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => <Tag color={getStatusColor(status)}>{status}</Tag>,
      sorter: (a: any, b: any) => (a.status || '').localeCompare(b.status || ''),
    },
    {
      title: 'Labeling',
      dataIndex: 'labeling_status',
      key: 'labeling_status',
      render: (status: string, record: ComplianceRecord) => (
        <Space direction="vertical" size={0}>
          <Tag color={status === 'DONE' ? 'green' : 'blue'} style={{ margin: 0 }}>
            {status || 'PENDING'}
          </Tag>
          {record.labeling_updated_at && (
            <span style={{ fontSize: '10px', color: '#8c8c8c' }}>
              {formatDateTime(record.labeling_updated_at)}
            </span>
          )}
        </Space>
      ),
      sorter: (a: any, b: any) => (a.labeling_status || '').localeCompare(b.labeling_status || ''),
    },
    {
      title: 'Task Progress',
      key: 'task_progress',
      render: (_: any, record: any) => {
        const percent = record.task_progress_percent ?? 0;
        if (record.status === ComplianceStatus.ACTIVE) return '-';
        return (
          <div
            style={{ cursor: 'pointer' }}
            onClick={() => navigate(`/compliance/tasks?record_id=${record.id}`)}
            title="Click to view tasks"
          >
            <Tag color="blue">{percent}%</Tag>
          </div>
        );
      },
      sorter: (a: any, b: any) => (a.task_progress_percent || 0) - (b.task_progress_percent || 0),
    },
    {
      title: 'Expiry Date',
      dataIndex: 'expiry_date',
      key: 'expiry_date',
      render: (date: string) => formatDate(date),
      sorter: (a: any, b: any) => new Date(a.expiry_date || 0).getTime() - new Date(b.expiry_date || 0).getTime(),
    },
    {
      title: 'Last Update',
      dataIndex: 'updated_at',
      key: 'updated_at',
      render: (date: string) => <span style={{ color: '#888' }}>{formatDateTime(date)}</span>,
      sorter: (a: any, b: any) => new Date(a.updated_at).getTime() - new Date(b.updated_at).getTime(),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: ComplianceRecord) => (
        <Space>
          <Button size="small" icon={<EyeOutlined />} onClick={() => navigate(`/compliance/${record.id}`)}>
            Details
          </Button>
          <Button
            size="small"
            icon={<BarChartOutlined />}
            onClick={() => navigate(`/compliance/tasks?record_id=${record.id}`)}
            title="View Compliance Tasks"
          >
            Tasks
          </Button>
          <Button size="small" icon={<EditOutlined />} onClick={() => navigate(`/compliance/${record.id}/edit`)}>Update</Button>
          {record.document_filename && (
            <Button
              size="small"
              icon={<FileSyncOutlined />}
              onClick={() => handlePreview(record.id, 'certificate', `Certificate: ${record.document_filename}`)}
            >
              Cert
            </Button>
          )}
          {record.test_report_filename && (
            <Button
              size="small"
              icon={<FileSyncOutlined />}
              onClick={() => handlePreview(record.id, 'test_report', `Test Report: ${record.test_report_filename}`)}
            >
              Report
            </Button>
          )}
        </Space>
      ),
    },
  ];

  // Handle scroll to section if hash is present
  useEffect(() => {
    if (location.hash === '#records-list') {
      // Small timeout to ensure DOM is ready and tab switch happened
      setTimeout(() => {
        const element = document.getElementById('records-list');
        if (element) {
          element.scrollIntoView({ behavior: 'smooth' });
        }
      }, 100);
    }
  }, [location.hash, activeTab]);

  return (
    <div style={{ height: 'calc(100vh - 140px)', display: 'flex', flexDirection: 'column', overflow: 'hidden', padding: '16px 24px' }}>
      <div style={{ flexShrink: 0, paddingBottom: '16px' }}>
        <Row gutter={[16, 16]}>
          <Col xs={12} sm={6}>
            <Card size="small" className="stat-card stat-card-markets">
              <Statistic
                title={<span className="stat-title">Markets</span>}
                value={stats.markets}
                prefix={<GlobalOutlined className="stat-icon" />}
                valueStyle={{ color: '#2f54eb', fontWeight: 700, fontSize: '24px' }}
              />
            </Card>
          </Col>
          <Col xs={12} sm={6}>
            <Card size="small" className="stat-card stat-card-active">
              <Statistic
                title={<span className="stat-title">Active</span>}
                value={stats.active}
                prefix={<CheckCircleOutlined className="stat-icon" />}
                valueStyle={{ color: '#52c41a', fontWeight: 700, fontSize: '24px' }}
              />
            </Card>
          </Col>
          <Col xs={12} sm={6}>
            <Card size="small" className="stat-card stat-card-expiring">
              <Statistic
                title={<span className="stat-title">Expiring</span>}
                value={stats.expiring}
                prefix={<WarningOutlined className="stat-icon" />}
                valueStyle={{ color: '#faad14', fontWeight: 700, fontSize: '24px' }}
              />
            </Card>
          </Col>
          <Col xs={12} sm={6}>
            <Card size="small" className="stat-card stat-card-gaps">
              <Statistic
                title={<span className="stat-title">Gaps</span>}
                value={stats.gaps}
                prefix={<FileSyncOutlined className="stat-icon" />}
                valueStyle={{ color: '#ff4d4f', fontWeight: 700, fontSize: '24px' }}
              />
            </Card>
          </Col>
        </Row>
      </div>

      <div style={{ flex: 1, minHeight: 0 }}>
        <Tabs
          activeKey={activeTab}
          onChange={(key) => {
            setActiveTab(key);
            const newUrl = new URL(window.location.href);
            newUrl.searchParams.set('tab', key);
            window.history.pushState({}, '', newUrl);
          }}
          style={{ height: '100%' }}
          className="compliance-tabs-fill"
          items={[
            {
              key: 'dashboard',
              label: (
                <Space size={8}>
                  <BarChartOutlined />
                  <span>Overview</span>
                </Space>
              ),
              children: (
                <div style={{ padding: '4px 12px 40px 0' }}>
                  <Row gutter={[16, 16]} style={{ minHeight: '100%' }}>
                    <Col xs={24} lg={10} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                      <ComplianceStatsChart />
                      <ExpiringWatchlist onViewAll={() => {
                        setStatusFilter(ComplianceStatus.EXPIRING);
                        setActiveTab('records');
                      }} />
                    </Col>
                    <Col xs={24} lg={14}>
                      <div style={{ height: '600px', minHeight: '100%' }}>
                        <GlobalComplianceMap />
                      </div>
                    </Col>
                  </Row>
                </div>
              ),
            },
            {
              key: 'progress',
              label: (
                <Space size={8}>
                  <FileSyncOutlined />
                  <span>Progress</span>
                </Space>
              ),
              children: (
                <div style={{ padding: '4px 8px 40px 0' }}>
                  <DeviceCountryProgress
                    records={allRecords || []}
                    tenantId={currentTenantId}
                    onDrillDown={handleDrillDown}
                  />
                </div>
              ),
            },
            {
              key: 'records',
              label: (
                <Space size={8}>
                  <BarsOutlined />
                  <span>Records</span>
                </Space>
              ),
              children: (
                <div style={{ padding: '4px 4px 40px 0' }}>
                  <Card
                    size="small"
                    title={<Space><BarsOutlined /><span>Compliance Records</span></Space>}
                    extra={
                      <Space wrap>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8, borderRight: '1px solid #f0f0f0', paddingRight: 12 }}>
                          <span style={{ fontSize: '12px', color: '#8c8c8c' }}>View:</span>
                          <Segmented
                            size="small"
                            options={[
                              { label: 'List', value: 'list', icon: <BarsOutlined /> },
                              { label: 'Group', value: 'group', icon: <AppstoreOutlined /> },
                            ]}
                            value={isGroupedByDevice ? 'group' : 'list'}
                            onChange={(val) => setIsGroupedByDevice(val === 'group')}
                          />
                        </div>

                        <Select
                          placeholder="Filter by status"
                          size="small"
                          style={{ width: 140 }}
                          value={statusFilter}
                          onChange={setStatusFilter}
                          allowClear
                          options={[
                            { label: 'Pending', value: 'PENDING' },
                            { label: 'Active', value: 'ACTIVE' },
                            { label: 'Expiring', value: 'EXPIRING' },
                            { label: 'Expired', value: 'EXPIRED' },
                          ]}
                        />

                        {deviceFilter && <Tag closable onClose={() => setDeviceFilter(undefined)}>D: {deviceFilter}</Tag>}
                        {countryFilter && <Tag closable onClose={() => setCountryFilter(undefined)}>C: {countryFilter}</Tag>}
                        {(statusFilter || deviceFilter || countryFilter) &&
                          <Button type="link" onClick={clearFilters} size="small" style={{ padding: 0 }}>Clear</Button>
                        }
                      </Space>
                    }
                    style={{ minHeight: '100%', borderRadius: '12px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)', border: '1px solid #f0f0f0' }}
                    bodyStyle={{ padding: 0 }}
                  >
                    <div>
                      {isGroupedByDevice ? (
                        <Table
                          columns={groupColumns}
                          dataSource={groupedData}
                          rowKey="key"
                          loading={isLoading}
                          pagination={false}
                          size="middle"
                          scroll={{ x: 'max-content' }}
                          onRow={(record) => ({
                            onClick: () => {
                              const key = record.key;
                              const newExpandedRowKeys = expandedRowKeys.includes(key)
                                ? expandedRowKeys.filter(k => k !== key)
                                : [...expandedRowKeys, key];
                              setExpandedRowKeys(newExpandedRowKeys);
                            },
                            style: { cursor: 'pointer' }
                          })}
                          expandable={{
                            expandedRowKeys: expandedRowKeys,
                            onExpandedRowsChange: (keys) => setExpandedRowKeys([...keys]),
                            expandedRowRender: (record) => (
                              <Table
                                columns={columns.filter(c => c.key !== 'device_name')}
                                dataSource={record.childrenRecords}
                                pagination={false}
                                size="small"
                                rowKey="id"
                                rowClassName={(record) => {
                                  if (record.status === ComplianceStatus.EXPIRED) return 'table-row-expired';
                                  // @ts-ignore
                                  if (record.status === ComplianceStatus.EXPIRING || (isExpiringSoon && isExpiringSoon(record))) return 'table-row-expiring';
                                  if (record.status === ComplianceStatus.ACTIVE) return 'table-row-active';
                                  return 'table-row-pending';
                                }}
                                onRow={(record) => ({
                                  onDoubleClick: () => {
                                    navigate(`/compliance/${record.id}`);
                                  },
                                  style: { cursor: 'pointer' }
                                })}
                              />
                            )
                          }}
                        />
                      ) : (
                        <Table
                          columns={columns}
                          dataSource={filteredRecords}
                          rowKey="id"
                          loading={isLoading}
                          pagination={false}
                          size="middle"
                          scroll={{ x: 'max-content' }}
                          rowClassName={(record) => {
                            if (record.status === ComplianceStatus.EXPIRED) return 'table-row-expired';
                            // @ts-ignore
                            if (record.status === ComplianceStatus.EXPIRING || (isExpiringSoon && isExpiringSoon(record))) return 'table-row-expiring';
                            if (record.status === ComplianceStatus.ACTIVE) return 'table-row-active';
                            return 'table-row-pending';
                          }}
                          onRow={(record) => ({
                            onDoubleClick: () => {
                              navigate(`/compliance/${record.id}`);
                            },
                            style: { cursor: 'pointer' }
                          })}
                        />
                      )}
                    </div>
                  </Card>
                </div>
              ),
            },
          ]}
        />
      </div>

      {/* Document Preview Modal */}
      <Modal
        title={
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>{previewDoc?.title || "Document Preview"}</span>
            <Space>
              <Button
                icon={<ExportOutlined />}
                onClick={() => previewDoc && window.open(previewDoc.url, '_blank')}
              >
                Open in New Tab
              </Button>
              <Button
                type="text"
                icon={<CloseOutlined />}
                onClick={() => setPreviewDoc(null)}
              />
            </Space>
          </div>
        }
        closable={false}
        open={!!previewDoc}
        onCancel={() => setPreviewDoc(null)}
        width={1000}
        centered
        footer={null}
      >
        {previewDoc && (
          <div style={{ height: '70vh', background: '#f0f0f0', borderRadius: 4, overflow: 'hidden' }}>
            <iframe
              src={previewDoc.url}
              style={{ width: '100%', height: '100%', border: 'none' }}
              title="PDF Preview"
            />
          </div>
        )}
      </Modal>
    </div>
  );
}

export default ComplianceDashboard;


