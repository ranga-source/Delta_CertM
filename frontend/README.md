# TAMSys Frontend

Multi-Tenant Certification Management System - React Frontend

## Tech Stack

- **Framework**: Vite + React 18 + TypeScript
- **UI Library**: Ant Design 5.x (SHINE BLUE theme)
- **State Management**: Redux Toolkit
- **API Management**: TanStack Query (React Query)
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Styling**: Separate CSS files + Ant Design theming

## Features

### 1. Gap Analysis (CORE FEATURE)
- Select device and target country
- Analyze missing certifications
- View detailed compliance gaps
- Color-coded status indicators

### 2. Device Management
- List all devices
- Create/edit devices
- Technology tagging
- Search and filter

### 3. Compliance Dashboard
- Overview statistics
- Status filtering
- Compliance records table
- Expiry tracking

### 4. Admin Features
- Global data management
- Tenant management
- Notification rules

### 5. Responsive Design
- Desktop (1920px+)
- Tablet (768px-1919px)
- Mobile (< 768px)

## Quick Start

### Prerequisites
- Node.js 18+
- Backend API running on http://localhost:8000

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Environment Variables

Create a `.env` file:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_NAME=TAMSys
```

## Project Structure

```
src/
├── app/                    # Redux store
│   ├── store.ts
│   └── slices/
├── assets/
│   └── styles/             # Global CSS
├── components/
│   ├── layout/             # Layout components
│   └── common/             # Reusable components
├── features/               # Feature modules
│   ├── gap-analysis/       # CORE FEATURE
│   ├── devices/
│   ├── compliance/
│   ├── admin/
│   └── tenants/
├── services/               # API services
├── hooks/                  # Custom hooks
├── types/                  # TypeScript types
├── config/                 # Configuration
├── utils/                  # Utilities
├── App.tsx                 # Root component
└── main.tsx                # Entry point
```

## Design Guidelines

### Theme
- Primary Color: SHINE BLUE (#1890ff)
- Light theme
- Professional and plain design
- Minimal animations

### Styling
- Separate CSS files (per component)
- 8px spacing grid
- Responsive breakpoints
- No infinite scrolling (pagination instead)

### Status Colors
- MISSING/EXPIRED: Red
- ACTIVE: Green
- EXPIRING/PENDING: Orange

## Development

### Code Organization
- Hybrid approach: Common components shared, features separated
- Each feature has its own API hooks
- Separate CSS files for all components
- Crystal clear comments throughout

### State Management
- Redux Toolkit for global state (tenant, UI)
- React Query for server state (API data)
- Local state for component-specific data

### API Integration
- Axios with interceptors
- Automatic error handling
- Toast notifications
- Request/response logging

## Building for Production

```bash
npm run build
```

The build artifacts will be in the `dist/` directory.

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

1. Follow the existing code style
2. Add comments for complex logic
3. Test responsive design
4. Update types when changing models

## License

Proprietary
