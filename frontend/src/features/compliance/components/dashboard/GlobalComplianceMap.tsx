import React, { useMemo, useState } from 'react';
import { ComposableMap, Geographies, Geography, Graticule, Sphere } from 'react-simple-maps';
import { scaleLinear } from 'd3-scale';
import { Typography, Spin, Empty } from 'antd';
import { useQuery } from '@tanstack/react-query';
import apiClient from '../../../../services/api';
import { API_ENDPOINTS } from '../../../../config/api.config';
import { QUERY_KEYS } from '../../../../services/queryClient';
import { useAppSelector } from '../../../../app/store';
import { ComplianceRecord } from '../../../../types/models.types';

const { Title } = Typography;

// Standard world map topojson
const GEO_URL = "https://unpkg.com/world-atlas@2.0.2/countries-110m.json";

// --- Color Logic for OVERVIEW Mode (Ratio) ---
const colorScale = scaleLinear<string>()
    .domain([0, 0.5, 1])
    .range(["#ff4d4f", "#faad14", "#52c41a"]); // Red -> Orange -> Green

// --- Color Logic for DEVICE Mode (Categorical) ---
const getStatusColor = (status: string) => {
    switch (status) {
        case 'ACTIVE': return '#52c41a';    // Green
        case 'PENDING': return '#1890ff';   // Blue
        case 'EXPIRING': return '#faad14';  // Orange
        case 'EXPIRED': return '#ff4d4f';   // Red
        default: return '#D6D6DA';          // Grey
    }
};

const getStatusPriority = (status: string) => {
    switch (status) {
        case 'EXPIRED': return 4;
        case 'EXPIRING': return 3;
        case 'PENDING': return 2;
        case 'ACTIVE': return 1;
        default: return 0;
    }
};

interface GlobalComplianceMapProps {
    records?: ComplianceRecord[];
    isLoading?: boolean;
    onCountryClick?: (countryName: string) => void;
    mode?: 'OVERVIEW' | 'DEVICE'; // New prop
}

export const GlobalComplianceMap: React.FC<GlobalComplianceMapProps> = ({
    records: propRecords,
    isLoading: propIsLoading,
    onCountryClick,
    mode = 'OVERVIEW' // Default to Overview
}) => {
    const currentTenantId = useAppSelector(state => state.tenant.currentTenantId);
    const [tooltipContent, setTooltipContent] = useState("");
    const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });

    const { data: fetchedRecords, isLoading: isFetching } = useQuery({
        queryKey: QUERY_KEYS.complianceRecords(currentTenantId || ''),
        queryFn: async () => {
            if (!currentTenantId) return [];
            const url = `${API_ENDPOINTS.complianceRecords}?tenant_id=${currentTenantId}`;
            const response = await apiClient.get<ComplianceRecord[]>(url);
            return response.data;
        },
        enabled: !!currentTenantId && !propRecords, // Only fetch if no records passed
    });

    const records = propRecords || fetchedRecords || [];
    const isLoading = propIsLoading !== undefined ? propIsLoading : isFetching;

    // Derived Data based on Mode
    const countryData = useMemo(() => {
        if (!records) return [];

        if (mode === 'OVERVIEW') {
            // --- OVERVIEW MODE Logic (Ratio) ---
            const statusByCountry: Record<string, { total: number, compliant: number }> = {};
            records.forEach(r => {
                const country = r.country_name;
                if (!country) return;
                if (!statusByCountry[country]) statusByCountry[country] = { total: 0, compliant: 0 };

                statusByCountry[country].total++;
                if (r.status === 'ACTIVE') {
                    statusByCountry[country].compliant++;
                }
            });

            return Object.keys(statusByCountry).map(country => {
                const stats = statusByCountry[country];
                const ratio = stats.total > 0 ? stats.compliant / stats.total : 0;
                return {
                    name: country,
                    status: ratio,      // Number (Ratio)
                    type: 'ratio',
                    total: stats.total,
                    compliant: stats.compliant
                };
            });

        } else {
            // --- DEVICE MODE Logic (Categorical) ---
            const statusByCountry: Record<string, string> = {};
            records.forEach(r => {
                const country = r.country_name;
                if (!country) return;

                const currentStatus = statusByCountry[country];
                const newStatus = r.status;

                // Worst status wins
                if (!currentStatus || getStatusPriority(newStatus) > getStatusPriority(currentStatus)) {
                    statusByCountry[country] = newStatus;
                }
            });

            return Object.entries(statusByCountry).map(([name, status]) => ({
                name,
                status,          // String (Category)
                type: 'category'
            }));
        }
    }, [records, mode]); // Recalculate if mode changes

    return (
        <div style={{ background: '#fff', borderRadius: '12px', border: '1px solid #f0f0f0', height: '100%', display: 'flex', flexDirection: 'column', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' }}>
            <div style={{
                padding: '0 24px',
                height: '56px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                zIndex: 10,
                borderBottom: '1px solid #f0f0f0',
                background: '#fff',
                borderTopLeftRadius: '12px',
                borderTopRightRadius: '12px'
            }}>
                <div style={{ fontWeight: 600, color: '#262626', fontSize: '15px' }}>Global Compliance Coverage</div>

                {mode === 'OVERVIEW' ? (
                    // OVERVIEW LEGEND
                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><div style={{ width: 8, height: 8, borderRadius: '50%', background: '#52c41a' }} /> <span style={{ color: '#595959', fontSize: '12px' }}>Compliant</span></div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><div style={{ width: 8, height: 8, borderRadius: '50%', background: '#faad14' }} /> <span style={{ color: '#595959', fontSize: '12px' }}>Partial</span></div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><div style={{ width: 8, height: 8, borderRadius: '50%', background: '#ff4d4f' }} /> <span style={{ color: '#595959', fontSize: '12px' }}>Non-Compliant</span></div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><div style={{ width: 8, height: 8, borderRadius: '50%', background: '#D6D6DA' }} /> <span style={{ color: '#595959', fontSize: '12px' }}>No Data</span></div>
                    </div>
                ) : (
                    // DEVICE LEGEND
                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><div style={{ width: 8, height: 8, borderRadius: '50%', background: '#52c41a' }} /> <span style={{ color: '#595959', fontSize: '12px' }}>Active</span></div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><div style={{ width: 8, height: 8, borderRadius: '50%', background: '#ff4d4f' }} /> <span style={{ color: '#595959', fontSize: '12px' }}>Expired</span></div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><div style={{ width: 8, height: 8, borderRadius: '50%', background: '#faad14' }} /> <span style={{ color: '#595959', fontSize: '12px' }}>Expiring</span></div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><div style={{ width: 8, height: 8, borderRadius: '50%', background: '#1890ff' }} /> <span style={{ color: '#595959', fontSize: '12px' }}>Pending</span></div>
                    </div>
                )}
            </div>

            <div style={{ flex: 1, position: 'relative', width: '100%', overflow: 'hidden' }}>
                {isLoading ? (
                    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                        <Spin />
                    </div>
                ) : (
                    <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
                        <ComposableMap
                            projectionConfig={{
                                rotate: [-10, 0, 0],
                                scale: 155
                            }}
                            style={{ width: "100%", height: "100%", maxHeight: '600px' }}
                        >
                            <Sphere stroke="#E4E5E6" strokeWidth={0.5} id="sphere" fill="#f8f9fa" />
                            <Graticule stroke="#E4E5E6" strokeWidth={0.5} />

                            <Geographies geography={GEO_URL}>
                                {({ geographies }: { geographies: any[] }) =>
                                    geographies.map((geo) => {
                                        // Match by Name
                                        const d = countryData.find((s) =>
                                            s.name === geo.properties.name ||
                                            (s.name === "United States" && geo.properties.name === "United States of America") ||
                                            (s.name === "USA" && geo.properties.name === "United States of America") ||
                                            (s.name === "UK" && geo.properties.name === "United Kingdom")
                                        );

                                        // Determine Color and Tooltip based on data type
                                        let fillColor = "#E4E5E6";
                                        let tooltipText = `${geo.properties.name}: No Data`;

                                        if (d) {
                                            if (mode === 'OVERVIEW' && d.type === 'ratio') {
                                                fillColor = colorScale(d.status as number);
                                                const compliant = (d as any).compliant;
                                                const total = (d as any).total;
                                                tooltipText = `${d.name}: ${compliant}/${total} Compliant`;
                                            } else if (mode === 'DEVICE' && d.type === 'category') {
                                                fillColor = getStatusColor(d.status as string);
                                                tooltipText = `${d.name}: ${d.status}`;
                                            }
                                        }

                                        return (
                                            <Geography
                                                key={geo.rsmKey}
                                                geography={geo}
                                                fill={fillColor}
                                                stroke="#FFFFFF"
                                                strokeWidth={0.5}
                                                onClick={() => {
                                                    if (onCountryClick) {
                                                        onCountryClick(geo.properties.name);
                                                    }
                                                }}
                                                onMouseEnter={() => {
                                                    setTooltipContent(tooltipText);
                                                }}
                                                onMouseMove={(e) => {
                                                    setTooltipPosition({ x: e.pageX, y: e.pageY });
                                                }}
                                                onMouseLeave={() => {
                                                    setTooltipContent("");
                                                }}
                                                style={{
                                                    default: { outline: "none", transition: 'fill 0.3s ease' },
                                                    hover: { fill: "#2f54eb", outline: "none", cursor: onCountryClick ? 'pointer' : 'default' },
                                                    pressed: { outline: "none" },
                                                }}
                                            />
                                        );
                                    })
                                }
                            </Geographies>
                        </ComposableMap>

                        {tooltipContent && (
                            <div style={{
                                position: 'fixed',
                                top: tooltipPosition.y + 15,
                                left: tooltipPosition.x + 15,
                                background: 'rgba(0, 0, 0, 0.85)',
                                color: '#fff',
                                padding: '8px 14px',
                                borderRadius: '8px',
                                fontSize: '13px',
                                pointerEvents: 'none',
                                zIndex: 9999,
                                boxShadow: '0 4px 15px rgba(0,0,0,0.25)',
                                transition: 'opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                                whiteSpace: 'nowrap',
                                fontWeight: 500,
                                backdropFilter: 'blur(4px)',
                                border: '1px solid rgba(255,255,255,0.15)'
                            }}>
                                {tooltipContent}
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};
