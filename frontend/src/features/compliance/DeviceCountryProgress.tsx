/**
 * Device / Country Progress View
 * Summarizes certification progress per device and country with gap counts.
 */

import { useEffect, useMemo, useState } from 'react';
import { Card, Table, Tag, Spin, message, Tooltip } from 'antd';
import { InfoCircleOutlined, CheckCircleOutlined } from '@ant-design/icons';
import apiClient from '../../services/api';
import { API_ENDPOINTS } from '../../config/api.config';
import { ComplianceRecord, GapAnalysisResponse } from '../../types/models.types';
import { formatDate } from '../../utils/formatters';

interface DeviceCountryProgressProps {
  records: ComplianceRecord[];
  tenantId: string | null;
  onDrillDown?: (filters: { deviceId?: string; countryId?: number; status?: string }) => void;
}

// Device Row (Level 1)
type DeviceRow = {
  key: string;
  device_id: string;
  device_name: string;
  country_count: number;
  total_req: number;
  total_gaps: number;
  total_active: number;
  total_pending: number;
  countries: CountryRow[];
};

// Country Row (Level 2)
type CountryRow = {
  key: string; // device_id-country_id
  country_id: number;
  country_name: string;
  active: number;
  expiring: number;
  expired: number;
  pending: number;
  total_required?: number;
  gaps_found?: number;
  nearest_expiry?: string;
  device_id: string; // Needed for drill-down
};

function DeviceCountryProgress({ records, tenantId, onDrillDown }: DeviceCountryProgressProps) {
  const [gapMap, setGapMap] = useState<Record<string, GapAnalysisResponse>>({});
  const [loadingGaps, setLoadingGaps] = useState(false);

  // Expansion State
  const [expandedDeviceKeys, setExpandedDeviceKeys] = useState<React.Key[]>([]);
  const [expandedCountryKeys, setExpandedCountryKeys] = useState<React.Key[]>([]);

  const handleDeviceExpand = (expanded: boolean, record: any) => {
    setExpandedDeviceKeys(expanded ? [record.key] : []);
  };

  const handleCountryExpand = (expanded: boolean, record: any) => {
    setExpandedCountryKeys(expanded ? [record.key] : []);
  };

  // Group by Device -> Country
  const deviceRows: DeviceRow[] = useMemo(() => {
    const deviceMap = new Map<string, DeviceRow>();

    // 1. First pass: Identify all Device+Country pairs from records
    const pairMap = new Map<string, CountryRow>();

    records.forEach((r) => {
      const pairKey = `${r.device_id}-${r.country_id}`;

      if (!pairMap.has(pairKey)) {
        pairMap.set(pairKey, {
          key: pairKey,
          country_id: r.country_id,
          country_name: r.country_name || `Country ${r.country_id}`,
          active: 0,
          expiring: 0,
          expired: 0,
          pending: 0,
          device_id: r.device_id,
          // Stats to be filled
        });
      }

      const row = pairMap.get(pairKey)!;
      if (r.status === 'ACTIVE') row.active++;
      else if (r.status === 'EXPIRING') row.expiring++;
      else if (r.status === 'EXPIRED') row.expired++;
      else if (r.status === 'PENDING') row.pending++;

      // Track expiry
      if (r.expiry_date) {
        if (!row.nearest_expiry || r.expiry_date < row.nearest_expiry) {
          row.nearest_expiry = r.expiry_date;
        }
      }
    });

    // 2. Second pass: Aggregate into Devices
    pairMap.forEach((countryRow) => {
      const devId = countryRow.device_id;
      // Find device name from one of the records (or lookup) - simplified here
      const devName = records.find(r => r.device_id === devId)?.device_name || devId;

      if (!deviceMap.has(devId)) {
        deviceMap.set(devId, {
          key: devId,
          device_id: devId,
          device_name: devName,
          country_count: 0,
          total_req: 0,
          total_gaps: 0,
          total_active: 0,
          total_pending: 0,
          countries: []
        });
      }

      const devRow = deviceMap.get(devId)!;
      devRow.countries.push(countryRow);
      devRow.country_count++;
      devRow.total_active += countryRow.active;
      devRow.total_pending += countryRow.pending;
      // Stats from Gap Analysis (Async) will be summed later or shown as '-'
    });

    return Array.from(deviceMap.values());
  }, [records]);

  // Fetch gap analysis for ALL pairs
  useEffect(() => {
    const fetchGaps = async () => {
      // Collect all pairs needed
      const pairsToFetch: { device_id: string, country_id: number }[] = [];
      deviceRows.forEach(d => {
        d.countries.forEach(c => {
          pairsToFetch.push({ device_id: d.device_id, country_id: c.country_id });
        });
      });

      if (!tenantId || pairsToFetch.length === 0) {
        setGapMap({});
        return;
      }
      setLoadingGaps(true);
      try {
        const responses = await Promise.all(
          pairsToFetch.map(async (pair) => {
            const response = await apiClient.post<GapAnalysisResponse>(
              `${API_ENDPOINTS.gapAnalysis}?tenant_id=${tenantId}`,
              { device_id: pair.device_id, country_id: pair.country_id }
            );
            return { key: `${pair.device_id}-${pair.country_id}`, data: response.data };
          })
        );
        const mapped: Record<string, GapAnalysisResponse> = {};
        responses.forEach((r) => {
          mapped[r.key] = r.data;
        });
        setGapMap(mapped);
      } catch (error: any) {
        console.error(error);
      } finally {
        setLoadingGaps(false);
      }
    };
    fetchGaps();
  }, [deviceRows, tenantId]);

  // Enrich data with gap info
  const enrichedDeviceRows = useMemo(() => {
    return deviceRows.map(dev => {
      let devTotalReq = 0;
      let devTotalGaps = 0;

      const enrichedCountries = dev.countries.map(c => {
        const gap = gapMap[c.key];
        if (gap) {
          c.total_required = gap.total_required;
          c.gaps_found = gap.gaps_found;
          devTotalReq += gap.total_required;
          devTotalGaps += gap.gaps_found;
        }
        return c;
      });

      return {
        ...dev,
        total_req: devTotalReq,
        total_gaps: devTotalGaps,
        countries: enrichedCountries
      };
    });
  }, [deviceRows, gapMap]);


  // LEVEL 3: Certifications Table
  const renderCertificationsTable = (countryRow: CountryRow) => {
    const gapInfo = gapMap[countryRow.key];
    if (!gapInfo || !gapInfo.results) return <Spin />;

    const columns = [
      { title: 'Certification', dataIndex: 'certification_name', key: 'certification_name' },
      { title: 'Technology', dataIndex: 'technology', key: 'technology' },
      {
        title: 'Status',
        key: 'status',
        render: (_: any, item: any) => {
          if (item.has_gap) return <Tag color="error">MISSING</Tag>;

          const status = item.status || 'COMPLIANT';
          let color = 'success';
          if (status === 'EXPIRING') color = 'warning'; // Orange
          else if (status === 'EXPIRED') color = 'error'; // Red
          else if (status === 'PENDING') color = 'blue';  // Blue

          return <Tag color={color}>{status}</Tag>;
        }
      }
    ];

    return (
      <Table
        columns={columns}
        dataSource={gapInfo.results}
        pagination={false}
        size="small"
        rowKey={(item: any) => `${item.certification_id}-${item.technology}`}
        scroll={{ x: 'max-content' }}
      />
    );
  };

  // LEVEL 2: Countries Table
  const renderCountriesTable = (deviceRow: DeviceRow) => {
    const countryRenderer = (status: string, val: number, row: CountryRow, color?: string) => {
      if (val === 0) return <span style={{ color: '#ccc' }}>-</span>;
      return (
        <Tag
          color={color}
          style={{ cursor: onDrillDown ? 'pointer' : 'default', minWidth: 40, textAlign: 'center' }}
          onClick={(e) => {
            e.stopPropagation();
            onDrillDown?.({ deviceId: row.device_id, countryId: row.country_id, status });
          }}
        >
          {val}
        </Tag>
      );
    };

    const columns = [
      { title: 'Country', dataIndex: 'country_name', key: 'country' },
      {
        title: (
          <span>
            Req. Papers {' '}
            <Tooltip title="Total certifications required">
              <InfoCircleOutlined style={{ color: '#1890ff' }} />
            </Tooltip>
          </span>
        ),
        dataIndex: 'total_required',
        key: 'req',
        render: (val: number) => val ?? <Spin size="small" />
      },
      {
        title: 'Gaps',
        dataIndex: 'gaps_found',
        key: 'gaps',
        render: (val: number | undefined) => {
          if (val === undefined) return <Spin size="small" />;
          if (val === 0) return <Tag color="success"><CheckCircleOutlined /> Done</Tag>;
          return <Tag color="error">{val} Missing</Tag>;
        }
      },
      {
        title: 'Pending',
        dataIndex: 'pending',
        key: 'pending',
        render: (val: number, r: CountryRow) => countryRenderer('PENDING', val, r, 'blue')
      },
      {
        title: 'Expiring',
        dataIndex: 'expiring',
        key: 'expiring',
        render: (val: number, r: CountryRow) => countryRenderer('EXPIRING', val, r, 'warning')
      },
      {
        title: 'Expired',
        dataIndex: 'expired',
        key: 'expired',
        render: (val: number, r: CountryRow) => countryRenderer('EXPIRED', val, r, 'error')
      },
      {
        title: 'Active',
        dataIndex: 'active',
        key: 'active',
        render: (val: number, r: CountryRow) => countryRenderer('ACTIVE', val, r, 'success')
      },
    ];

    return (
      <Table
        columns={columns}
        dataSource={deviceRow.countries}
        pagination={false}
        rowKey="key"
        scroll={{ x: 'max-content' }}
        expandable={{
          expandedRowRender: renderCertificationsTable,
          expandedRowKeys: expandedCountryKeys,
          onExpand: handleCountryExpand
        }}
        onRow={(record) => ({
          onClick: () => {
            const isExpanded = expandedCountryKeys.includes(record.key);
            handleCountryExpand(!isExpanded, record);
          },
          style: { cursor: 'pointer' }
        })}
      />
    );
  };

  // LEVEL 1: Device Table Columns
  const deviceColumns = [
    { title: 'Device Model', dataIndex: 'device_name', key: 'device_name', width: '25%' },
    { title: 'Current Markets', dataIndex: 'country_count', key: 'markets', render: (val: number) => <Tag color="blue">{val} Countries</Tag> },
    { title: 'Total Req. Papers', dataIndex: 'total_req', key: 'total_req', render: (val: number) => val },
    { title: 'Global Gaps', dataIndex: 'total_gaps', key: 'total_gaps', render: (val: number) => val > 0 ? <Tag color="error">{val}</Tag> : <Tag color="success">All Compliant</Tag> },
    { title: 'Total Pending', dataIndex: 'total_pending', key: 'total_pending' },
  ];

  return (
    <Table
      columns={deviceColumns}
      dataSource={enrichedDeviceRows}
      loading={loadingGaps}
      rowKey="key"
      expandable={{
        expandedRowRender: renderCountriesTable,
        expandedRowKeys: expandedDeviceKeys,
        onExpand: handleDeviceExpand
      }}
      pagination={false}
      size="middle"
      sticky={true}
      scroll={{ x: 'max-content' }}
      onRow={(record) => ({
        onClick: () => {
          const isExpanded = expandedDeviceKeys.includes(record.key);
          handleDeviceExpand(!isExpanded, record);
        },
        style: { cursor: 'pointer' }
      })}
    />
  );
}

export default DeviceCountryProgress;


