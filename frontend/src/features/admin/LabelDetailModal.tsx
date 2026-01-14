
import React from 'react';
import { Modal, Descriptions, Typography, Button } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import { CertificationLabel } from '../../types/models.types';

const { Title } = Typography;

interface LabelDetailModalProps {
    label: CertificationLabel | null;
    onClose: () => void;
    open: boolean;
}

export const LabelDetailModal: React.FC<LabelDetailModalProps> = ({ label, onClose, open }) => {
    return (
        <Modal
            title={<Title level={4}>{label?.name}</Title>}
            open={open}
            onCancel={onClose}
            footer={[
                <Button key="close" onClick={onClose}>
                    Close
                </Button>,
                label?.vector_url && (
                    <Button
                        key="download"
                        type="primary"
                        icon={<DownloadOutlined />}
                        href={label.vector_url}
                        target="_blank"
                    >
                        Download Vector
                    </Button>
                )
            ]}
            width={700}
        >
            {label && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
                    <div style={{
                        textAlign: 'center',
                        padding: 20,
                        border: '1px solid #eee',
                        borderRadius: 8,
                        backgroundColor: '#fff'
                    }}>
                        <img
                            src={label.image_url}
                            alt={label.name}
                            style={{ maxHeight: 200, maxWidth: '100%' }}
                        />
                    </div>

                    <Descriptions bordered column={1}>
                        <Descriptions.Item label="Authority">{label.authority}</Descriptions.Item>
                        <Descriptions.Item label="Description">{label.description}</Descriptions.Item>
                    </Descriptions>

                    {label.requirements && (
                        <div>
                            <Title level={5}>Marking Requirements</Title>
                            <Descriptions bordered size="small" column={1}>
                                {Object.entries(label.requirements).map(([key, val]) => (
                                    <Descriptions.Item
                                        key={key}
                                        label={<span style={{ textTransform: 'capitalize' }}>{key.replace('_', ' ')}</span>}
                                    >
                                        {val}
                                    </Descriptions.Item>
                                ))}
                            </Descriptions>
                        </div>
                    )}
                </div>
            )}
        </Modal>
    );
};
