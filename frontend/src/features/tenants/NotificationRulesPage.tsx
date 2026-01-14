/**
 * Notification Rules Page
 */

import { Card } from 'antd';
import { useParams } from 'react-router-dom';

function NotificationRulesPage() {
  const { tenantId } = useParams();
  
  return (
    <Card title={`Notification Rules for Tenant ${tenantId}`}>
      <p>Notification rules management (Coming soon)</p>
    </Card>
  );
}

export default NotificationRulesPage;


