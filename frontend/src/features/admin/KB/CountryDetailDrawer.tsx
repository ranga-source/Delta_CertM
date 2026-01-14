import React from 'react';
import { Drawer, Descriptions, Tag, Typography, Space, Divider, Alert } from 'antd';
import { GlobalOutlined, ThunderboltOutlined, InfoCircleOutlined, TagsOutlined } from '@ant-design/icons';
import { Country } from '../../../types/models.types';

const { Title, Text, Paragraph } = Typography;

interface CountryDetailDrawerProps {
    visible: boolean;
    onClose: () => void;
    country: Country | null;
}

export function CountryDetailDrawer({ visible, onClose, country }: CountryDetailDrawerProps) {
    if (!country) return null;

    const details = country.details as any; // Type assertion since frontend model might not be updated yet

    return (
        <Drawer
            title={
                <Space>
                    <GlobalOutlined />
                    {country.name} ({country.iso_code})
                </Space>
            }
            placement="right"
            width={500}
            onClose={onClose}
            open={visible}
        >
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>

                {/* Basic Info */}
                <div>
                    <Title level={5}>General Information</Title>
                    <Descriptions column={1} bordered size="small">
                        <Descriptions.Item label="ISO Code">{country.iso_code}</Descriptions.Item>
                        <Descriptions.Item label="Region">Global Market</Descriptions.Item>
                    </Descriptions>
                </div>

                {details ? (
                    <>
                        <Divider style={{ margin: 0 }} />

                        {/* Power Specs */}
                        <div>
                            <Title level={5}><Space><ThunderboltOutlined /> Power Specifications</Space></Title>
                            <div style={{ background: '#f0f5ff', padding: '16px', borderRadius: '8px', border: '1px solid #adc6ff' }}>
                                <Descriptions column={2} size="small">
                                    <Descriptions.Item label="Voltage">
                                        <Text strong>{details.voltage}</Text>
                                    </Descriptions.Item>
                                    <Descriptions.Item label="Frequency">
                                        <Text strong>{details.frequency}</Text>
                                    </Descriptions.Item>
                                </Descriptions>
                                <div style={{ marginTop: 12 }}>
                                    <Text type="secondary">Plug Types: </Text>
                                    {details.plug_types?.map((type: string) => (
                                        <Tag color="geekblue" key={type}>Type {type}</Tag>
                                    ))}
                                </div>
                            </div>
                        </div>

                        <Divider style={{ margin: 0 }} />

                        {/* Label Requirements */}
                        <div>
                            <Title level={5}><Space><TagsOutlined /> Labeling Requirements</Space></Title>
                            {details.label_requirements ? (
                                <div style={{ background: '#fffbe6', padding: '16px', borderRadius: '8px', border: '1px solid #ffe58f' }}>
                                    <Paragraph style={{ marginBottom: 0 }}>
                                        {details.label_requirements}
                                    </Paragraph>
                                </div>
                            ) : (
                                <Text type="secondary">No specific labeling requirements data available.</Text>
                            )}
                        </div>
                    </>
                ) : (
                    <Alert
                        message="No Detailed Data"
                        description="Detailed profile (Voltage, Plugs, Labeling) is not available for this country yet."
                        type="info"
                        showIcon
                    />
                )}

            </div>
        </Drawer>
    );
}
