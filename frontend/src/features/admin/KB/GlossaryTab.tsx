
import React, { useState, useMemo, useEffect } from 'react';
import { Empty, Spin } from 'antd';
import { RightOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import apiClient from '../../../services/api';
import GlossaryArticleView from './GlossaryArticleView';
import { GlossaryArticle } from '../../../types/models.types';

// API Service
const fetchGlossaryTerms = async (): Promise<GlossaryArticle[]> => {
    const response = await apiClient.get('/global/glossary?limit=1000');
    return response.data;
};

const ALPHABET = "#ABCDEFGHIJKLMNOPQRSTUVWXYZ".split('');

interface GlossaryTabProps {
    searchQuery: string;
}

const GlossaryTab: React.FC<GlossaryTabProps> = ({ searchQuery }) => {
    const [selectedArticleId, setSelectedArticleId] = useState<string | null>(null);

    const { data: glossaryData = [], isLoading } = useQuery<GlossaryArticle[]>({
        queryKey: ['glossary'],
        queryFn: fetchGlossaryTerms,
        staleTime: 5 * 60 * 1000,
    });

    const filteredData = useMemo(() => {
        let data = glossaryData;
        if (searchQuery) {
            const lowerSearch = searchQuery.toLowerCase();
            data = glossaryData.filter(item =>
                item.term.toLowerCase().includes(lowerSearch) ||
                item.summary.toLowerCase().includes(lowerSearch) ||
                (item.region && item.region.toLowerCase().includes(lowerSearch))
            );
        }
        return data.sort((a, b) => a.term.localeCompare(b.term, undefined, { numeric: true, sensitivity: 'base' }));
    }, [glossaryData, searchQuery]);

    const selectedArticle = useMemo(() =>
        glossaryData.find(item => item.id === selectedArticleId),
        [glossaryData, selectedArticleId]);

    // Group available letters for logic
    const availableLetters = useMemo(() => {
        const letters = new Set<string>();
        filteredData.forEach(item => {
            const firstChar = item.term.charAt(0).toUpperCase();
            if (/[0-9]/.test(firstChar)) {
                letters.add('#');
            } else {
                letters.add(firstChar);
            }
        });
        return letters;
    }, [filteredData]);

    // ... existing logic ...

    const scrollToLetter = (letter: string) => {
        const targetItem = filteredData.find(item => {
            const firstChar = item.term.charAt(0).toUpperCase();
            if (letter === '#') return /[0-9]/.test(firstChar);
            return firstChar === letter;
        });

        if (targetItem) {
            const element = document.getElementById(`glossary-item-${targetItem.id}`);
            if (element) {
                element.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }
    };

    // Handle initial selection
    useEffect(() => {
        if (!selectedArticleId && glossaryData.length > 0) {
            setSelectedArticleId(glossaryData[0].id);
        }
    }, [glossaryData, selectedArticleId]);

    if (isLoading) return <div style={{ padding: 20, textAlign: 'center' }}><Spin /></div>;

    return (
        <div style={{ display: 'flex', height: 'calc(100vh - 280px)', border: '1px solid #f0f0f0', borderRadius: '8px' }}>
            {/* Sidebar List Container */}
            <div style={{
                width: '320px', // Increased slightly for nav bar
                borderRight: '1px solid #f0f0f0',
                display: 'flex',
                height: '100%'
            }}>
                {/* The List */}
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
                    {/* Removed Search Input */}

                    <div style={{ flex: 1, overflowY: 'auto' }}>
                        {filteredData.length > 0 ? (
                            <div style={{ paddingBottom: 16 }}>
                                {filteredData.map(item => (
                                    <div
                                        key={item.id}
                                        id={`glossary-item-${item.id}`}
                                        onClick={() => setSelectedArticleId(item.id)}
                                        style={{
                                            cursor: 'pointer',
                                            padding: '12px 16px',
                                            backgroundColor: selectedArticleId === item.id ? '#e6f7ff' : 'transparent',
                                            borderRight: selectedArticleId === item.id ? '2px solid #1890ff' : 'none',
                                            transition: 'all 0.3s',
                                            marginBottom: 4,
                                            // Add tiny letter header if it's the first of its kind? Optional, keeping simple for now.
                                        }}
                                    >
                                        <div style={{ width: '100%' }}>
                                            <div style={{ fontWeight: 500, marginBottom: 4 }}>{item.term}</div>
                                            <div style={{ fontSize: '12px', color: '#888', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                                                {item.region && (
                                                    <span style={{
                                                        backgroundColor: '#f0f5ff',
                                                        color: '#2f54eb',
                                                        padding: '0 6px',
                                                        borderRadius: '4px',
                                                        border: '1px solid #adc6ff'
                                                    }}>
                                                        {item.region}
                                                    </span>
                                                )}
                                                <span>{item.category}</span>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <Empty description="No terms found" />
                        )}
                    </div>
                </div>

                {/* A-Z Navigation Bar */}
                <div style={{
                    width: '30px',
                    borderLeft: '1px solid #f0f0f0',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center', // Center vertically
                    padding: '8px 0',
                    backgroundColor: '#fafafa',
                    fontSize: '11px',
                    overflowY: 'auto', // In case screen is too short
                    flexShrink: 0
                }}>
                    {ALPHABET.map(letter => {
                        const active = availableLetters.has(letter);
                        return (
                            <div
                                key={letter}
                                onClick={() => active && scrollToLetter(letter)}
                                style={{
                                    cursor: active ? 'pointer' : 'default',
                                    padding: '2px 0',
                                    color: active ? '#1890ff' : '#ccc',
                                    fontWeight: active ? 'bold' : 'normal',
                                    width: '100%',
                                    textAlign: 'center',
                                    userSelect: 'none'
                                }}
                            >
                                {letter}
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Content Area */}
            <div style={{ flex: 1, overflowY: 'auto', backgroundColor: '#fff' }}>
                {selectedArticle ? (
                    <GlossaryArticleView article={selectedArticle} />
                ) : (
                    <div style={{ padding: '40px', textAlign: 'center', color: '#999' }}>
                        Select a term to view details
                    </div>
                )}
            </div>
        </div >
    );
};

export default GlossaryTab;

