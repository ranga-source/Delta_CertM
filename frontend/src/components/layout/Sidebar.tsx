/**
 * Sidebar Component
 * =================
 * Navigation sidebar with menu items.
 * 
 * Features:
 * - Collapsible sidebar
 * - Active route highlighting
 * - Responsive (drawer on mobile)
 */

import { Layout, Menu } from 'antd';
import {
  DashboardOutlined,
  ApiOutlined,
  MobileOutlined,
  SafetyOutlined,
  SettingOutlined,
  TeamOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAppSelector, useAppDispatch } from '../../app/store';
import { toggleSidebar } from '../../app/slices/uiSlice';
import './Sidebar.css';

const { Sider } = Layout;

function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useAppDispatch();
  const collapsed = useAppSelector(state => state.ui.sidebarCollapsed);

  /**
   * Menu items configuration
   */
  const menuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
    },
    {
      key: '/gap-analysis',
      icon: <ApiOutlined />, // Changed icon to avoid duplicate
      label: 'Gap Analysis',
    },
    {
      key: '/devices',
      icon: <MobileOutlined />,
      label: 'Devices',
    },
    {
      key: '/compliance',
      icon: <SafetyOutlined />,
      label: 'Compliance',
    },
    {
      key: 'admin',
      icon: <SettingOutlined />,
      label: 'Admin',
      children: [
        {
          key: '/admin/global-data',
          icon: <ApiOutlined />,
          label: 'Global Data',
        },
        {
          key: '/admin/tenants',
          icon: <TeamOutlined />,
          label: 'Tenants',
        },
      ],
    },
  ];

  /**
   * Handle menu item click
   */
  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  /**
   * Get current selected key from location
   */
  const getSelectedKey = () => {
    return location.pathname;
  };

  /**
   * Get open keys for submenus
   */
  const getOpenKeys = () => {
    if (location.pathname.startsWith('/admin')) {
      return ['admin'];
    }
    return [];
  };

  return (
    <Sider
      collapsible
      collapsed={collapsed}
      onCollapse={() => dispatch(toggleSidebar())}
      breakpoint="md"
      className="app-sider"
      theme="light"
      width={200}
      collapsedWidth={80}
    >
      <div style={{ height: 'calc(100% - 48px)', overflowY: 'auto', overflowX: 'hidden' }}>
        <Menu
          mode="inline"
          selectedKeys={[getSelectedKey()]}
          defaultOpenKeys={getOpenKeys()}
          items={menuItems}
          onClick={handleMenuClick}
          style={{ height: '100%', borderRight: 0 }}
        />
      </div>
    </Sider>
  );
}

export default Sidebar;


