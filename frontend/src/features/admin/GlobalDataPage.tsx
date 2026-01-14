/**
 * Global Data Management Page
 * ===========================
 * Renders seeded global master data (technologies, countries,
 * certifications, and regulatory rules) in responsive tabbed tables.
 * All data is fetched live from the backend so seed_data.py results
 * are immediately visible without manual refreshes.
 */

import React, { useMemo, useState } from 'react';
import { Card, Tabs, Table, Tag, Alert, Typography, Input, Space, Button } from 'antd';
import { ApiOutlined, GlobalOutlined, SafetyOutlined, SettingOutlined, SearchOutlined, BookOutlined, PictureOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import apiClient from '../../services/api';
import { API_ENDPOINTS } from '../../config/api.config';
import { QUERY_KEYS } from '../../services/queryClient';
import { Technology, Country, Certification, RegulatoryRule } from '../../types/models.types';
import GlossaryTab from './KB/GlossaryTab';
import LabellingTab from './LabellingTab';
import { CountryDetailDrawer } from './KB/CountryDetailDrawer';
import './GlobalDataPage.css';
import { LabelDetailModal } from './LabelDetailModal';
import { Tooltip, Popover } from 'antd'; // Added Popover, Tooltip already implicit if used

interface CertificationLabel {
  id: number;
  name: string;
  authority: string;
  description?: string;
  image_url?: string;
  country_id?: number | null;
  requirements?: {
    region?: string;
    [key: string]: any;
  };
}

const { Paragraph, Text } = Typography;

// EU Countries for Regional Label Logic
const EU_COUNTRIES = [
  'Germany', 'France', 'Italy', 'Spain', 'Netherlands', 'Sweden',
  'Belgium', 'Austria', 'Poland', 'Czech Republic', 'Portugal', 'Greece',
  'Hungary', 'Ireland', 'Romania', 'Finland', 'Denmark',
  'Turkey', 'Switzerland'
];

function GlobalDataPage() {
  const [searchText, setSearchText] = useState('');

  // Drawer state
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [selectedCountry, setSelectedCountry] = useState<Country | null>(null);

  // Create state for selected label to show in modal
  const [selectedLabel, setSelectedLabel] = useState<CertificationLabel | null>(null);



  // Expansion State for Regulatory Matrix
  const [expandedRegKeys, setExpandedRegKeys] = useState<React.Key[]>([]);

  const handleRegExpand = (expanded: boolean, record: any) => {
    const keys = expanded
      ? [...expandedRegKeys, record.id]
      : expandedRegKeys.filter(k => k !== record.id);
    setExpandedRegKeys(keys);
  };

  // Expansion State for Technologies
  const [expandedTechKeys, setExpandedTechKeys] = useState<React.Key[]>([]);

  const handleTechExpand = (expanded: boolean, record: any) => {
    const keys = expanded
      ? [...expandedTechKeys, record.id]
      : expandedTechKeys.filter(k => k !== record.id);
    setExpandedTechKeys(keys);
  };
  const handleViewCountry = (country: Country) => {
    setSelectedCountry(country);
    setDrawerVisible(true);
  };


  /**
   * Fetch all technologies seeded in the backend.
   * Uses React Query for caching and loading state management.
   */
  const {
    data: technologies = [],
    isLoading: technologiesLoading,
    isError: technologiesError,
  } = useQuery({
    queryKey: QUERY_KEYS.technologies,
    queryFn: async () => {
      const response = await apiClient.get<Technology[]>(`${API_ENDPOINTS.technologies}?limit=1000`);
      return response.data;
    },
  });

  /**
   * Fetch all countries seeded in the backend.
   */
  const {
    data: countries = [],
    isLoading: countriesLoading,
    isError: countriesError,
  } = useQuery({
    queryKey: QUERY_KEYS.countries,
    queryFn: async () => {
      const response = await apiClient.get<Country[]>(`${API_ENDPOINTS.countries}?limit=1000`);
      return response.data;
    },
  });

  /**
   * Fetch all certifications seeded in the backend.
   */
  const {
    data: certifications = [],
    isLoading: certificationsLoading,
    isError: certificationsError,
  } = useQuery({
    queryKey: QUERY_KEYS.certifications,
    queryFn: async () => {
      const response = await apiClient.get<Certification[]>(`${API_ENDPOINTS.certifications}?limit=1000`);
      return response.data;
    },
  });

  /**
   * Fetch all regulatory rules seeded in the backend.
   */
  const {
    data: regulatoryRules = [],
    isLoading: rulesLoading,
    isError: rulesError,
  } = useQuery({
    queryKey: QUERY_KEYS.regulatoryRules(),
    queryFn: async () => {
      const response = await apiClient.get<RegulatoryRule[]>(`${API_ENDPOINTS.regulatoryMatrix}?limit=5000`);
      return response.data;
    },
  });

  /**
   * Fetch Certification Labels for Matrix Display
   */
  const { data: labels = [] } = useQuery({
    queryKey: ['labels'],
    queryFn: async () => {
      const response = await apiClient.get<CertificationLabel[]>('/global/labels');
      return response.data;
    },
  });

  /**
   * Build quick lookup maps to convert IDs to user-friendly labels.
   */
  const technologyLookup = useMemo(() => {
    const map = new Map<number, string>();
    technologies.forEach((item) => map.set(item.id, item.name));
    return map;
  }, [technologies]);

  const countryLookup = useMemo(() => {
    const map = new Map<number, string>();
    countries.forEach((item) => map.set(item.id, `${item.name} (${item.iso_code})`));
    return map;
  }, [countries]);

  const certificationLookup = useMemo(() => {
    const map = new Map<number, string>();
    certifications.forEach((item) => map.set(item.id, item.name));
    return map;
  }, [certifications]);

  /**
   * Enrich regulatory rules with friendly labels for display.
   */
  const regulatoryRows = useMemo(() => {
    return regulatoryRules.map((rule) => ({
      ...rule,
      technologyLabel:
        rule.technology_name ||
        technologyLookup.get(rule.technology_id) ||
        `Technology #${rule.technology_id}`,
      countryLabel:
        rule.country_name ||
        countryLookup.get(rule.country_id) ||
        `Country #${rule.country_id}`,
      certificationLabel:
        rule.certification_name ||
        certificationLookup.get(rule.certification_id) ||
        `Certification #${rule.certification_id}`,
    }));
  }, [regulatoryRules, technologyLookup, countryLookup, certificationLookup]);

  // --- Filtering Logic ---

  const filteredTechnologies = useMemo(() => {
    if (!searchText) return technologies;
    const lower = searchText.toLowerCase();
    return technologies.filter(t =>
      t.name.toLowerCase().includes(lower) ||
      (t.description && t.description.toLowerCase().includes(lower))
    );
  }, [technologies, searchText]);

  const filteredCountries = useMemo(() => {
    if (!searchText) return countries;
    const lower = searchText.toLowerCase();
    return countries.filter(c =>
      c.name.toLowerCase().includes(lower) ||
      c.iso_code.toLowerCase().includes(lower)
    );
  }, [countries, searchText]);

  const filteredCertifications = useMemo(() => {
    if (!searchText) return certifications;
    const lower = searchText.toLowerCase();
    return certifications.filter(c =>
      c.name.toLowerCase().includes(lower) ||
      (c.authority_name && c.authority_name.toLowerCase().includes(lower)) ||
      (c.description && c.description.toLowerCase().includes(lower))
    );
  }, [certifications, searchText]);

  const filteredRegulatoryRules = useMemo(() => {
    if (!searchText) return regulatoryRows;
    const lower = searchText.toLowerCase();
    return regulatoryRows.filter(r =>
      r.technologyLabel.toLowerCase().includes(lower) ||
      r.countryLabel.toLowerCase().includes(lower) ||
      r.certificationLabel.toLowerCase().includes(lower) ||
      (r.notes && r.notes.toLowerCase().includes(lower))
    );
  }, [regulatoryRows, searchText]);


  // --- Grouping Logic for Technologies ---

  const groupedTechnologies = useMemo(() => {
    if (!filteredTechnologies.length) return [];

    const groups: Record<string, Technology[]> = {
      'Wi-Fi': [],
      'Bluetooth': [],
      'Cellular': [],
      'LPWAN': [],
      'Other': []
    };

    filteredTechnologies.forEach(tech => {
      const name = tech.name.toLowerCase();
      if (name.includes('wi-fi') || name.includes('wifi') || name.includes('802.11')) {
        groups['Wi-Fi'].push(tech);
      } else if (name.includes('bluetooth') || name.includes('ble')) {
        groups['Bluetooth'].push(tech);
      } else if (name.includes('lte') || name.includes('5g') || name.includes('4g') || name.includes('gsm') || name.includes('nb-iot') || name.includes('cat-m')) {
        groups['Cellular'].push(tech);
      } else if (name.includes('lora') || name.includes('sigfox') || name.includes('zigbee') || name.includes('thread') || name.includes('z-wave')) {
        groups['LPWAN'].push(tech);
      } else {
        groups['Other'].push(tech);
      }
    });

    // Transform into tree structure for AntD Table
    return Object.entries(groups)
      .filter(([_, techs]) => techs.length > 0) // Only show groups with items
      .map(([groupName, techs], index) => ({
        id: `group-${index}`,
        name: `${groupName} (${techs.length})`,
        description: `Group for ${groupName} technologies`,
        children: techs,
        isGroup: true
      }));
  }, [filteredTechnologies]);


  // --- Grouping Logic for Regulatory Rules ---

  const groupedRegulatoryRules = useMemo(() => {
    if (!filteredRegulatoryRules.length) return [];

    // Group by Country Name
    const groups: Record<string, any[]> = {};

    filteredRegulatoryRules.forEach(rule => {
      const country = rule.countryLabel;
      if (!groups[country]) {
        groups[country] = [];
      }
      groups[country].push(rule);
    });

    // Sort countries alphabetically
    return Object.entries(groups)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([countryName, rules], index) => {
        // Find country_id from the first rule (assuming rules exist)
        const countryId = rules[0]?.country_id;

        // Find applicable labels for this country
        // 1. Exact Country Match
        // 2. Regional Match (EU)
        // Note: countryName here includes ISO code "Germany (DEU)", so we look up raw name
        const rawCountry = countries.find(c => c.id === countryId);
        const realName = rawCountry?.name || countryName;
        const isEU = EU_COUNTRIES.includes(realName);

        const applicableLabels = labels.filter(l => {
          const isCountryMatch = l.country_id === countryId;
          const isRegionMatch = isEU && l.requirements?.region === 'EU';
          return isCountryMatch || isRegionMatch;
        });


        return {
          id: `reg-group-${index}`,
          technologyLabel: '',
          countryLabel: `${countryName} (${rules.length})`,
          countryName: countryName, // Store raw name for tooltip if needed
          labels: applicableLabels, // Attach labels to group
          certificationLabel: '',
          is_mandatory: false,
          notes: `Regulatory rules for ${countryName}`,
          created_at: '',
          children: rules,
          isGroup: true
        };
      });
  }, [filteredRegulatoryRules, labels, countries]);

  /**
   * Column definitions for the technologies table.
   */
  const technologyColumns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: any) => {
        if (record.isGroup) {
          return <Text strong>{text}</Text>;
        }
        return <span style={{ paddingLeft: 8 }}>{text}</span>;
      }
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      render: (value: string | undefined) => value || '—',
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (value: string | undefined, record: any) => {
        if (record.isGroup) return '';
        return value;
      }
    },
  ];

  /**
   * Column definitions for the countries table.
   */
  const countryColumns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'ISO Code',
      dataIndex: 'iso_code',
      key: 'iso_code',
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
    },
  ];

  /**
   * Column definitions for the certifications table.
   */
  const certificationColumns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Authority',
      dataIndex: 'authority_name',
      key: 'authority_name',
      render: (value: string | undefined) => value || '—',
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      render: (value: string | undefined) => value || '—',
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
    },
  ];

  /**
   * Column definitions for the regulatory matrix table.
   */
  const regulatoryColumns = [
    {
      title: 'Country',
      dataIndex: 'countryLabel',
      key: 'countryLabel',
      onCell: (record: any) => ({
        colSpan: record.isGroup ? 6 : 1,
      }),
      render: (text: string, record: any) => {
        if (record.isGroup) {
          return (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span className="group-header-text">{text}</span>
              {record.labels && record.labels.length > 0 && (
                <Space size="small" style={{ marginRight: 16 }}>
                  {record.labels.map((l: CertificationLabel) => (
                    <Popover
                      key={l.id}
                      title={<Text strong>{l.name}</Text>}
                      content={
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 8, maxWidth: 200 }}>
                          <Text type="secondary">{l.authority}</Text>
                          <Button
                            size="small"
                            type="primary"
                            onClick={(e) => {
                              e.stopPropagation(); // Prevent row expand
                              setSelectedLabel(l);
                            }}
                          >
                            View
                          </Button>
                        </div>
                      }
                    >
                      <div style={{
                        width: 30,
                        height: 20,
                        display: 'flex',
                        cursor: 'pointer',
                        alignItems: 'center',
                        justifyContent: 'center',
                        background: '#fff',
                        border: '1px solid #d9d9d9',
                        borderRadius: 2,
                        overflow: 'hidden'
                      }}>
                        <img
                          src={l.image_url}
                          alt={l.name}
                          style={{ maxWidth: '100%', maxHeight: '100%' }}
                        />
                      </div>
                    </Popover>
                  ))}
                </Space>
              )}
            </div>
          );
        }
        return null;
      }
    },
    {
      title: 'Technology',
      dataIndex: 'technologyLabel',
      key: 'technologyLabel',
      onCell: (record: any) => ({
        colSpan: record.isGroup ? 0 : 1,
      }),
    },
    {
      title: 'Certification',
      dataIndex: 'certificationLabel',
      key: 'certificationLabel',
      onCell: (record: any) => ({
        colSpan: record.isGroup ? 0 : 1,
      }),
    },
    {
      title: 'Mandatory',
      dataIndex: 'is_mandatory',
      key: 'is_mandatory',
      onCell: (record: any) => ({
        colSpan: record.isGroup ? 0 : 1,
      }),
      render: (mandatory: boolean, record: any) => {
        if (record.isGroup) return null;
        return (
          <Tag color={mandatory ? 'blue' : 'default'}>
            {mandatory ? 'Yes' : 'Optional'}
          </Tag>
        );
      },
    },
    {
      title: 'Notes',
      dataIndex: 'notes',
      key: 'notes',
      onCell: (record: any) => ({
        colSpan: record.isGroup ? 0 : 1,
      }),
      render: (value: string | undefined, record: any) => {
        return value || '—';
      },
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      onCell: (record: any) => ({
        colSpan: record.isGroup ? 0 : 1,
      }),
      render: (value: string | undefined, record: any) => {
        if (record.isGroup) return '';
        return value;
      }
    },
  ];

  /**
   * Helper to render a standardized error banner when any tab fails.
   */
  const renderError = (condition: boolean, label: string) =>
    condition ? (
      <Alert
        type="error"
        message={`Unable to load ${label}`}
        description={`Please confirm the backend is running and that seed_data.py has been executed. (${label})`}
        showIcon
        className="global-alert"
      />
    ) : null;

  /**
   * Tab items rendered inside the main card.
   */
  const items = [
    {
      key: 'technologies',
      label: (
        <span className="global-tab-label">
          <ApiOutlined />
          Technologies ({filteredTechnologies.length})
        </span>
      ),
      children: (
        <div className="global-tab-content">
          {renderError(technologiesError, 'technologies')}
          <Table
            columns={technologyColumns}
            dataSource={groupedTechnologies}
            rowKey="id"
            loading={technologiesLoading}
            pagination={false}
            expandable={{
              expandedRowKeys: expandedTechKeys,
              onExpand: handleTechExpand,
              rowExpandable: (record) => record.isGroup,
            }}
            onRow={(record) => ({
              className: record.isGroup ? 'group-row-clickable' : '',
              onClick: (e) => {
                if (record.isGroup) {
                  const isExpanded = expandedTechKeys.includes(record.id);
                  handleTechExpand(!isExpanded, record);
                }
              },
              style: { cursor: record.isGroup ? 'pointer' : 'default' }
            })}
          />
        </div>
      ),
    },
    {
      key: 'countries',
      label: (
        <span className="global-tab-label">
          <GlobalOutlined />
          Countries ({filteredCountries.length})
        </span>
      ),
      children: (
        <div className="global-tab-content">
          {renderError(countriesError, 'countries')}
          <Table
            columns={countryColumns}
            dataSource={filteredCountries}
            rowKey="id"
            loading={countriesLoading}
            pagination={{
              defaultPageSize: 10,
              showSizeChanger: true,
              showQuickJumper: false,
              pageSizeOptions: ['10', '20', '50', '100'],
              responsive: true
            }}
          />
        </div>
      ),
    },
    {
      key: 'certifications',
      label: (
        <span className="global-tab-label">
          <SafetyOutlined />
          Certifications ({filteredCertifications.length})
        </span>
      ),
      children: (
        <div className="global-tab-content">
          {renderError(certificationsError, 'certifications')}
          <Table
            columns={certificationColumns}
            dataSource={filteredCertifications}
            rowKey="id"
            loading={certificationsLoading}
            pagination={{ pageSize: 6, responsive: true }}
          />
        </div>
      ),
    },
    {
      key: 'rules',
      label: (
        <span className="global-tab-label">
          <SettingOutlined />
          Regulatory Matrix ({filteredRegulatoryRules.length})
        </span>
      ),
      children: (
        <div className="global-tab-content">
          {renderError(rulesError, 'regulatory rules')}
          <Table
            columns={regulatoryColumns}
            dataSource={groupedRegulatoryRules}
            rowKey="id"
            loading={rulesLoading}
            pagination={false}
            expandable={{
              expandedRowKeys: expandedRegKeys,
              onExpand: handleRegExpand,
              rowExpandable: (record) => record.isGroup,
            }}
            onRow={(record) => ({
              className: record.isGroup ? 'group-row-clickable' : '',
              onClick: (e) => {
                if (record.isGroup) {
                  // Prevent toggling if checking selection or other interactive elements if any
                  // But here we just want expand
                  const isExpanded = expandedRegKeys.includes(record.id);
                  handleRegExpand(!isExpanded, record);
                }
              },
              style: { cursor: record.isGroup ? 'pointer' : 'default' }
            })}
            rowClassName={(record) => record.isGroup ? 'group-row' : ''}
          />
        </div>
      ),
    },
    {
      key: 'glossary',
      label: (
        <span className="global-tab-label">
          <BookOutlined />
          Glossary
        </span>
      ),
      children: <GlossaryTab searchQuery={searchText} />,
    },
    {
      key: 'labelling',
      label: (
        <span className="global-tab-label">
          <PictureOutlined />
          Labelling
        </span>
      ),
      children: <LabellingTab />,
    },
  ];



  return (
    <>
      <Card
        title="Global Data Management"
        className="global-data-card"
        extra={
          <Space>
            <Input
              placeholder="Search global data..."
              prefix={<SearchOutlined />}
              allowClear
              value={searchText}
              onChange={e => setSearchText(e.target.value)}
              style={{ width: 250 }}
            />
            <Paragraph className="global-card-note" style={{ marginBottom: 0 }}>
              <Text strong>Data source:</Text> Seeded via backend/seed_data.py
            </Paragraph>
          </Space>
        }
      >
        <Tabs items={items} destroyOnHidden />
      </Card>

      <CountryDetailDrawer
        visible={drawerVisible}
        onClose={() => setDrawerVisible(false)}
        country={selectedCountry}
      />

      <LabelDetailModal
        label={selectedLabel}
        open={!!selectedLabel}
        onClose={() => setSelectedLabel(null)}
      />


    </>
  );
}

export default GlobalDataPage;

