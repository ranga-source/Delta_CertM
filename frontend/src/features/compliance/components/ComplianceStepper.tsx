import React from 'react';
import { Steps } from 'antd';
import {
    FileTextOutlined,
    SyncOutlined,
    SafetyCertificateOutlined,
    WarningOutlined
} from '@ant-design/icons';
import { ComplianceStatus } from '../../../types/models.types';

interface ComplianceStepperProps {
    status: ComplianceStatus;
}

export const ComplianceStepper: React.FC<ComplianceStepperProps> = ({ status }) => {

    const getStep = () => {
        switch (status) {
            case 'PENDING': return 1;
            case 'ACTIVE': return 2;
            case 'EXPIRING': return 2; // Still active, just warning
            case 'EXPIRED': return 3;
            default: return 0; // Assume draft or unknown
        }
    };

    const current = getStep();

    // Custom status for the final step if expired
    const finalStepStatus = status === 'EXPIRED' ? 'error' : (status === 'ACTIVE' || status === 'EXPIRING' ? 'finish' : 'wait');

    return (
        <Steps
            current={current}
            items={[
                {
                    title: 'Draft',
                    description: 'Record Created',
                    icon: <FileTextOutlined />,
                },
                {
                    title: 'In Progress',
                    description: 'Certification Processing',
                    icon: <SyncOutlined spin={status === 'PENDING'} />,
                },
                {
                    title: 'Active',
                    description: 'Certified & Valid',
                    icon: <SafetyCertificateOutlined />,
                    status: status === 'EXPIRING' ? 'process' : (status === 'ACTIVE' ? 'finish' : 'wait'),
                },
                {
                    title: status === 'EXPIRED' ? 'Expired' : 'Expiry',
                    description: 'Validity Ended',
                    icon: <WarningOutlined />,
                    status: status === 'EXPIRED' ? 'error' : 'wait'
                }
            ]}
        />
    );
};
