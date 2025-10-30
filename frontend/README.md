# Auto.Mark Landing Page Frontend

React.js frontend application for the Auto.Mark AI Marketing Automation Platform landing page and onboarding system.

## Features

- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **TypeScript**: Full type safety and better developer experience
- **Component Library**: Reusable UI components with consistent design
- **API Integration**: Axios-based API client for backend communication
- **Analytics**: Built-in page view tracking and conversion analytics
- **Performance**: Optimized build with code splitting and lazy loading

## Tech Stack

- **React 19** with TypeScript
- **Tailwind CSS** for styling
- **Axios** for API communication
- **Lucide React** for icons
- **React Router** for navigation (ready for multi-page expansion)

## Getting Started

### Prerequisites

- Node.js 16+ 
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build

# Serve production build locally
npm run serve
```

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# API Configuration
REACT_APP_API_URL=http://localhost:8000

# Environment
REACT_APP_ENVIRONMENT=development
```

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── ui/             # Basic UI components (Button, Input, Card)
│   ├── layout/         # Layout components (Header, Footer, Layout)
│   └── common/         # Common components
├── pages/              # Page components
├── services/           # API services and clients
├── types/              # TypeScript type definitions
├── utils/              # Utility functions
└── App.tsx            # Main application component
```

## Component Library

### UI Components

- **Button**: Configurable button with variants, sizes, and loading states
- **Input**: Form input with validation and error handling
- **Card**: Container component with shadow and padding options

### Layout Components

- **Layout**: Main layout wrapper with header and footer
- **Header**: Responsive navigation with mobile menu
- **Footer**: Site footer with links and branding

## API Integration

The frontend communicates with the FastAPI backend through:

- **LandingPageAPI**: Main API service for landing page functionality
- **apiClient**: Configured Axios instance with interceptors
- **Type Safety**: Full TypeScript interfaces for all API responses

## Deployment

### Railway Deployment

The app is configured for Railway deployment with:

- `railway.json` configuration
- Production build optimization
- Static file serving with `serve`

### Build Process

```bash
npm run build    # Creates optimized production build
npm run serve    # Serves build locally for testing
```

## Development

### Adding New Components

1. Create component in appropriate directory
2. Export from index.ts file
3. Add TypeScript interfaces
4. Include in component library

### API Integration

1. Add types to `src/types/index.ts`
2. Add service methods to `src/services/landingPageApi.ts`
3. Use in components with proper error handling

### Styling

- Use Tailwind CSS utility classes
- Follow mobile-first responsive design
- Maintain consistent spacing and colors
- Use design system tokens from `tailwind.config.js`

## Performance

- Code splitting with React.lazy()
- Image optimization
- Bundle size monitoring
- Lighthouse performance targets: 90+

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Follow TypeScript strict mode
2. Use ESLint and Prettier
3. Write responsive, accessible components
4. Test on mobile devices
5. Maintain consistent code style