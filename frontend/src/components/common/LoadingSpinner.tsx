/**
 * Loading Spinner Component
 */

import { Spin } from 'antd';

interface LoadingSpinnerProps {
  tip?: string;
  size?: 'small' | 'default' | 'large';
}

function LoadingSpinner({ tip = 'Loading...', size = 'large' }: LoadingSpinnerProps) {
  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '400px',
      width: '100%',
    }}>
      <Spin size={size} tip={tip} />
    </div>
  );
}

export default LoadingSpinner;


