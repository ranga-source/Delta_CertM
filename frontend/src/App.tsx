/**
 * Root Application Component
 * ==========================
 * Main component that sets up routing and layout.
 */

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import ScrollToTop from './components/layout/ScrollToTop';
import AppLayout from './components/layout/AppLayout';
import GapAnalysisPage from './features/gap-analysis/GapAnalysisPage';
import DeviceListPage from './features/devices/DeviceListPage';
import DeviceFormPage from './features/devices/DeviceFormPage';
import DeviceDetailPage from './features/devices/DeviceDetailPage';
import ComplianceDashboard from './features/compliance/ComplianceDashboard';
import ComplianceRecordDetailPage from './features/compliance/ComplianceRecordDetailPage';
import ComplianceRecordTasksWrapper from './features/compliance/ComplianceRecordTasksWrapper';
import ComplianceTaskDetailPage from './features/compliance/ComplianceTaskDetailPage';
import ComplianceRecordEditPage from './features/compliance/ComplianceRecordEditPage';
import GlobalDataPage from './features/admin/GlobalDataPage';
import TenantManagementPage from './features/tenants/TenantManagementPage';
import NotificationRulesPage from './features/tenants/NotificationRulesPage';
import DeviceComplianceDashboard from './features/compliance/DeviceComplianceDashboard';

function App() {
  return (
    <BrowserRouter>
      <ScrollToTop />
      <Routes>
        <Route path="/" element={<AppLayout />}>
          {/* Default route - redirect to Gap Analysis (core feature) */}
          <Route index element={<Navigate to="/gap-analysis" replace />} />

          {/* Gap Analysis - THE CORE FEATURE */}
          <Route path="gap-analysis" element={<GapAnalysisPage />} />
          <Route path="dashboard" element={<DeviceComplianceDashboard />} />

          {/* Device Management */}
          <Route path="devices" element={<DeviceListPage />} />
          <Route path="devices/new" element={<DeviceFormPage />} />
          <Route path="devices/:id" element={<DeviceDetailPage />} />
          <Route path="devices/:id/edit" element={<DeviceFormPage />} />

          {/* Compliance */}
          <Route path="compliance" element={<ComplianceDashboard />} />
          <Route path="compliance/:recordId" element={<ComplianceRecordDetailPage />} />
          <Route path="compliance/:recordId/tasks" element={<ComplianceTaskDetailPage />} />
          <Route path="compliance/tasks" element={<ComplianceTaskDetailPage />} />
          <Route path="compliance/tasks/:taskId" element={<ComplianceTaskDetailPage />} />
          <Route path="compliance/:recordId/edit" element={<ComplianceRecordEditPage />} />

          {/* Admin */}
          <Route path="admin/global-data" element={<GlobalDataPage />} />
          <Route path="admin/tenants" element={<TenantManagementPage />} />

          {/* Tenant Notification Rules */}
          <Route path="tenants/:tenantId/notification-rules" element={<NotificationRulesPage />} />

          {/* 404 - Not Found */}
          <Route path="*" element={<Navigate to="/gap-analysis" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
