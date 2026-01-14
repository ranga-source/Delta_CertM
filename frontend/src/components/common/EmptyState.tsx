/**
 * Empty State Component
 */

import { Empty, Button } from 'antd';

interface EmptyStateProps {
  description?: string;
  actionText?: string;
  onAction?: () => void;
}

function EmptyState({ 
  description = 'No data available',
  actionText,
  onAction
}: EmptyStateProps) {
  return (
    <div className="empty-state">
      <Empty
        description={description}
        image={Empty.PRESENTED_IMAGE_SIMPLE}
      >
        {actionText && onAction && (
          <Button type="primary" onClick={onAction}>
            {actionText}
          </Button>
        )}
      </Empty>
    </div>
  );
}

export default EmptyState;


