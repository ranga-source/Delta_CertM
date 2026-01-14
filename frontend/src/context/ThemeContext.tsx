import React, { createContext, useContext, useState, ReactNode } from 'react';
import { ConfigProvider } from 'antd';
import { theme as defaultTheme } from '../config/theme.config';

interface ThemeContextType {
    fontSize: number;
    increaseFontSize: () => void;
    decreaseFontSize: () => void;
    resetFontSize: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const useTheme = () => {
    const context = useContext(ThemeContext);
    if (!context) {
        throw new Error('useTheme must be used within a ThemeProvider');
    }
    return context;
};

export const ThemeProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [fontSize, setFontSize] = useState(14); // Default Ant Design base font size

    const increaseFontSize = () => setFontSize(prev => Math.min(prev + 2, 18));
    const decreaseFontSize = () => setFontSize(prev => Math.max(prev - 2, 12));
    const resetFontSize = () => setFontSize(14);

    // Merge dynamic font size with default theme
    const dynamicTheme = {
        ...defaultTheme,
        token: {
            ...defaultTheme.token,
            fontSize: fontSize,
            // Scale other related metrics if needed, e.g. controlHeight?
            // For now, fontSize is the primary request.
        },
    };

    return (
        <ThemeContext.Provider value={{ fontSize, increaseFontSize, decreaseFontSize, resetFontSize }}>
            <ConfigProvider theme={dynamicTheme}>
                {children}
            </ConfigProvider>
        </ThemeContext.Provider>
    );
};
