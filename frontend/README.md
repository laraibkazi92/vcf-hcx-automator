# VCF HCX Automator - Frontend

Frontend application for managing VCF VMware HCX workflows built with React, TanStack Router, and TanStack Query.

## Installation

```bash
# Install dependencies
npm install

# or with pnpm
pnpm install

# or with yarn
yarn install
```

## Development

```bash
# Start development server
npm run dev

# or with pnpm
pnpm dev

# or with yarn
yarn dev
```

The application will be available at http://localhost:3000.

## Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Configuration

Create a `.env` file in the frontend directory:

```env
# API URL (optional, defaults to http://localhost:8000)
VITE_API_URL=http://localhost:8000
```

## Project Structure

```
frontend/
├── src/
│   ├── main.tsx          # Application entry point
│   ├── index.css         # Global styles
│   ├── lib/              # Utility functions and API client
│   │   ├── api.ts        # API client
│   │   └── utils.ts     # Utility functions
│   ├── components/       # Reusable components
│   └── routes/           # Route components
├── index.html            # HTML template
├── package.json          # Dependencies and scripts
├── vite.config.ts        # Vite configuration
├── tailwind.config.js    # Tailwind CSS configuration
└── tsconfig.json         # TypeScript configuration
```

## Technology Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **TanStack Router** - Type-safe routing
- **TanStack Query** - Server state management
- **Tailwind CSS** - Styling
- **Vite** - Build tool and dev server
- **Lucide React** - Icons

## Features

- Type-safe routing with TanStack Router
- Efficient data fetching with TanStack Query
- Responsive design with Tailwind CSS
- Modern development experience with Vite
- Full TypeScript support