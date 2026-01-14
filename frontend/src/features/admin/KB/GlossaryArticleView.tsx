import React from 'react';
import { Typography, Tag, Divider, Table } from 'antd';
import { GlossaryArticle } from '../../../types/models.types';

const { Title, Paragraph } = Typography;

interface GlossaryArticleViewProps {
    article: GlossaryArticle;
}

export default function GlossaryArticleView({ article }: GlossaryArticleViewProps) {
    return (
        <div style={{ padding: '0 24px', maxWidth: '900px' }}>
            {/* Header */}
            <div style={{ marginBottom: 24 }}>
                <Title level={2} style={{ marginBottom: 8 }}>{article.term}</Title>
                <div style={{ marginBottom: 16 }}>
                    <Tag color="#108ee9">{article.category}</Tag>
                </div>
                <Paragraph type="secondary" style={{ fontSize: '16px' }}>
                    {article.summary}
                </Paragraph>
            </div>

            <Divider />

            {/* Sections */}
            {article.sections.map((section, idx) => (
                <div key={idx} style={{ marginBottom: 32 }}>
                    {section.title && <Title level={3} style={{ marginTop: 0 }}>{section.title}</Title>}

                    {/* Paragraphs */}
                    {/* Paragraphs */}
                    {Array.isArray(section.content) ? (
                        section.content.map((para, pIdx) => (
                            <Paragraph key={pIdx} style={{ lineHeight: 1.8 }}>
                                {para}
                            </Paragraph>
                        ))
                    ) : (
                        section.content && (
                            <Paragraph style={{ lineHeight: 1.8 }}>
                                {section.content}
                            </Paragraph>
                        )
                    )}

                    {/* List Items */}
                    {section.listItems && (
                        <ul style={{ paddingLeft: 20, marginBottom: 16 }}>
                            {section.listItems.map((item, lIdx) => (
                                <li key={lIdx} style={{ marginBottom: 8, lineHeight: 1.6 }}>{item}</li>
                            ))}
                        </ul>
                    )}

                    {/* Images */}
                    {section.images && section.images.map((imgUrl, imgIdx) => (
                        <div key={imgIdx} style={{ marginBottom: 16, textAlign: 'center' }}>
                            <img
                                src={imgUrl}
                                alt={`Section image ${imgIdx + 1}`}
                                style={{ maxWidth: '100%', borderRadius: 8, border: '1px solid #f0f0f0' }}
                            />
                        </div>
                    ))}

                    {/* Table */}
                    {section.table && (
                        <Table
                            dataSource={section.table.rows.map((row, rIdx) => {
                                const obj: any = { key: rIdx };
                                section.table!.headers.forEach((h, hIdx) => {
                                    obj[h] = row[hIdx];
                                });
                                return obj;
                            })}
                            columns={section.table.headers.map(h => ({
                                title: h,
                                dataIndex: h,
                                key: h
                            }))}
                            pagination={false}
                            bordered
                            size="middle"
                            style={{ marginTop: 16 }}
                        />
                    )}
                </div>
            ))}
        </div>
    );
}
