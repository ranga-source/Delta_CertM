/**
 * Gap Analysis Page - THE CORE FEATURE
 * =====================================
 * Identifies missing certifications for a device in a target country.
 * 
 * User Flow:
 * 1. Select Device
 * 2. Select Target Country
 * 3. Click "Analyze"
 * 4. View results: Total Required, Gaps Found, Detailed table
 * 5. Take action on missing certifications
 */

import { useState } from 'react';
import { Card, Button, Row, Col, Statistic, message, Spin } from 'antd';
import { SafetyOutlined, WarningOutlined, CheckCircleOutlined, ReloadOutlined } from '@ant-design/icons';
import { useMutation } from '@tanstack/react-query';
import apiClient from '../../services/api';
import { API_ENDPOINTS } from '../../config/api.config';
import { useAppSelector } from '../../app/store';
import { GapAnalysisRequest, GapAnalysisResponse } from '../../types/models.types';
import DeviceSelector from './DeviceSelector';
import CountrySelector from './CountrySelector';
import GapResultsTable from './GapResultsTable';
import './GapAnalysisPage.css';

function GapAnalysisPage() {
  const currentTenantId = useAppSelector(state => state.tenant.currentTenantId);
  const [selectedDeviceId, setSelectedDeviceId] = useState<string | null>(null);
  const [selectedCountryId, setSelectedCountryId] = useState<number | null>(null);
  const [analysisResults, setAnalysisResults] = useState<GapAnalysisResponse | null>(null);

  /**
   * Gap Analysis Mutation
   */
  const gapAnalysisMutation = useMutation({
    mutationFn: async (request: GapAnalysisRequest) => {
      const response = await apiClient.post<GapAnalysisResponse>(
        `${API_ENDPOINTS.gapAnalysis}?tenant_id=${currentTenantId}`,
        request
      );
      return response.data;
    },
    onSuccess: (data) => {
      setAnalysisResults(data);
      message.success('Gap analysis completed successfully!');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Failed to perform gap analysis');
    },
  });

  /**
   * Handle Analyze button click
   */
  const handleAnalyze = () => {
    if (!currentTenantId) {
      message.warning('Please select a tenant first');
      return;
    }

    if (!selectedDeviceId) {
      message.warning('Please select a device');
      return;
    }

    if (!selectedCountryId) {
      message.warning('Please select a target country');
      return;
    }

    gapAnalysisMutation.mutate({
      device_id: selectedDeviceId,
      country_id: selectedCountryId,
    });
  };

  /**
   * Reset analysis
   */
  const handleReset = () => {
    setSelectedDeviceId(null);
    setSelectedCountryId(null);
    setAnalysisResults(null);
  };

  return (
    <div className="gap-analysis-page">
      <Card
        title={
          <div className="page-title">
            <SafetyOutlined />
            <span>Gap Analysis - Identify Missing Certifications</span>
          </div>
        }
        className="gap-analysis-card"
      >
        {/* Step 1 & 2: Device and Country Selection */}
        <Row gutter={[16, 16]} className="selection-section">
          <Col xs={24} md={12}>
            <DeviceSelector
              value={selectedDeviceId}
              onChange={setSelectedDeviceId}
              tenantId={currentTenantId}
            />
          </Col>
          <Col xs={24} md={12}>
            <CountrySelector
              value={selectedCountryId}
              onChange={setSelectedCountryId}
            />
          </Col>
        </Row>

        {/* Action Buttons */}
        <Row gutter={16} className="action-section">
          <Col>
            <Button
              type="primary"
              size="large"
              onClick={handleAnalyze}
              loading={gapAnalysisMutation.isPending}
              disabled={!selectedDeviceId || !selectedCountryId}
            >
              Analyze Compliance Gap
            </Button>
          </Col>
          {analysisResults && (
            <Col>
              <Button onClick={handleReset} size="large" icon={<ReloadOutlined />}>
                Reset
              </Button>
            </Col>
          )}
        </Row>

        {/* Loading State */}
        {gapAnalysisMutation.isPending && (
          <div className="loading-container">
            <Spin size="large" tip="Analyzing..." />
          </div>
        )}

        {/* Results Summary */}
        {analysisResults && !gapAnalysisMutation.isPending && (
          <>
            <div className="results-summary">
              <Row gutter={[16, 16]}>
                <Col xs={24} sm={8}>
                  <Card className="stat-card">
                    <Statistic
                      title="Total Required"
                      value={analysisResults.total_required}
                      prefix={<SafetyOutlined />}
                      styles={{ content: { color: '#1890ff' } }}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={8}>
                  <Card className="stat-card stat-card-warning">
                    <Statistic
                      title="Gaps Found"
                      value={analysisResults.gaps_found}
                      prefix={<WarningOutlined />}
                      styles={{ content: { color: analysisResults.gaps_found > 0 ? '#ff4d4f' : '#52c41a' } }}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={8}>
                  <Card className="stat-card stat-card-success">
                    <Statistic
                      title="Compliant"
                      value={analysisResults.total_required - analysisResults.gaps_found}
                      prefix={<CheckCircleOutlined />}
                      styles={{ content: { color: '#52c41a' } }}
                    />
                  </Card>
                </Col>
              </Row>
            </div>

            {/* Results Table */}
            <GapResultsTable
              results={analysisResults.results}
              deviceId={analysisResults.device_id}
              countryId={analysisResults.country_id}
              tenantId={currentTenantId}
            />
          </>
        )}
      </Card>
    </div>
  );
}

export default GapAnalysisPage;


