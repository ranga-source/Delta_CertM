
import React, { useState } from 'react';
import { Card, Col, Row, Typography, Modal, Descriptions, Tag, Button, Empty, Spin } from 'antd';
import { useQuery } from '@tanstack/react-query';
import { EyeOutlined, DownloadOutlined } from '@ant-design/icons';
import apiClient from '../../services/api';
import { LabelDetailModal } from './LabelDetailModal';

const { Meta } = Card;
const { Title, Text, Paragraph } = Typography;

interface LabelRequirements {
    min_height?: string;
    clear_space?: string;
    content?: string;
    color?: string;
    placement?: string;
    [key: string]: any;
}

interface CertificationLabel {
    id: number;
    name: string;
    authority: string;
    description?: string;
    requirements?: LabelRequirements;
    image_url?: string;
    vector_url?: string;
    country_id?: number | null;
}

const fetchLabels = async (): Promise<CertificationLabel[]> => {
    const response = await apiClient.get('/global/labels');
    return response.data;
};

const LabellingTab: React.FC = () => {
    const [selectedLabel, setSelectedLabel] = useState<CertificationLabel | null>(null);

    const { data: labels = [], isLoading } = useQuery<CertificationLabel[]>({
        queryKey: ['labels'],
        queryFn: fetchLabels,
    });

    if (isLoading) return <div style={{ padding: 40, textAlign: 'center' }}><Spin size="large" /></div>;

    if (!labels.length) return <Empty description="No label data available" />;

    return (
        <div style={{ padding: '20px 0' }}>
            <Row gutter={[16, 16]}>
                {labels.map((label) => (
                    <Col xs={24} sm={12} md={8} lg={6} key={label.id}>
                        <Card
                            hoverable
                            cover={
                                <div style={{
                                    height: 160,
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    padding: 20,
                                    backgroundColor: '#fafafa',
                                    borderBottom: '1px solid #f0f0f0'
                                }}>
                                    <img
                                        alt={label.name}
                                        src={label.image_url || 'https://via.placeholder.com/150?text=No+Image'}
                                        style={{
                                            maxWidth: '100%',
                                            maxHeight: '100%',
                                            objectFit: 'contain'
                                        }}
                                    />
                                </div>
                            }
                            onClick={() => setSelectedLabel(label)}
                        >
                            <Meta
                                title={label.name}
                                description={
                                    <div style={{
                                        whiteSpace: 'nowrap',
                                        overflow: 'hidden',
                                        textOverflow: 'ellipsis'
                                    }}>
                                        {label.authority}
                                    </div>
                                }
                            />
                        </Card>
                    </Col>
                ))}
            </Row>

            <LabelDetailModal
                label={selectedLabel}
                open={!!selectedLabel}
                onClose={() => setSelectedLabel(null)}
            />
        </div>
    );
};

export default LabellingTab;
