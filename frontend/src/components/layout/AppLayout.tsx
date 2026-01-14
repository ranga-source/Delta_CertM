/**
 * App Layout Component
 * ====================
 * Main layout wrapper for the application.
 * 
 * Structure:
 * - Fixed Header (top)
 * - Fixed Sidebar (left)
 * - Content Area (center)
 * - Breadcrumbs
 * 
 * Features:
 * - Responsive layout
 * - Automatic sidebar collapse on mobile
 * - Outlet for nested routes
 */

import { Layout, Breadcrumb } from 'antd';
import { Outlet, useLocation, Link } from 'react-router-dom';
import Header from './Header';
import Sidebar from './Sidebar';
import { useAppSelector } from '../../app/store';
import './AppLayout.css';

const { Content } = Layout;

function AppLayout() {
  const location = useLocation();
  const collapsed = useAppSelector(state => state.ui.sidebarCollapsed);

  /**
   * Generate breadcrumb items from current location
   */
  const getBreadcrumbItems = () => {
    const pathSnippets = location.pathname.split('/').filter(i => i);

    const breadcrumbItems = [
      {
        title: <Link to="/">Home</Link>,
      },
    ];

    pathSnippets.forEach((snippet, index) => {
      const url = `/${pathSnippets.slice(0, index + 1).join('/')}`;
      const isLast = index === pathSnippets.length - 1;

      // Format the snippet for display
      const title = snippet
        .split('-')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');

      breadcrumbItems.push({
        title: isLast ? title : <Link to={url}>{title}</Link>,
      });
    });

    return breadcrumbItems;
  };

  return (
    <Layout className="app-layout">
      {/* Header - Fixed at top */}
      <Header />

      <Layout className="app-layout-content">
        {/* Sidebar - Fixed on left */}
        <Sidebar />

        {/* Main Content Area */}
        <Layout
          className="content-layout"
          style={{
            marginLeft: collapsed ? 80 : 200,
            marginTop: 64,
            transition: 'margin-left 0.2s',
          }}
        >
          <Content className="main-content">
            {/* Breadcrumbs */}
            <div className="breadcrumb-container">
              <Breadcrumb items={getBreadcrumbItems()} />
            </div>

            {/* Page Content - Rendered by React Router */}
            <div className="page-wrapper">
              <Outlet />
            </div>
          </Content>
        </Layout>
      </Layout>
    </Layout>
  );
}

export default AppLayout;


