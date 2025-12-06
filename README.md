# VCF HCX Automator

A mono repo for automating VCF VMware HCX workflows with a powerful backend and modern frontend.

## Overview

This project consists of two main components:

- **Backend**: Python-based API service using Litestar, msgspec, and Cyclopts for HCX workflow automation
- **Frontend**: React application with TanStack Router and Query for managing HCX operations
- **Database**: Convex DB for data persistence (locally hosted)

## Quick Start

### Prerequisites

- Python 3.13+
- Node.js 18+
- Docker & Docker Compose

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd vcf-hcx-automator
   ```

2. **Start Convex DB**
   ```bash
   docker-compose up -d
   ```

3. **Set up the backend**
   ```bash
   cd backend
   pip install -e ".[dev]"
   
   # Create environment file
   cp .env.example .env
   # Edit .env with your VCF/HCX credentials
   ```

4. **Set up the frontend**
   ```bash
   cd frontend
   npm install
   ```

### Running the Application

1. **Start the backend API server**
   ```bash
   cd backend
   litestar run --host 127.0.0.1 --port 8000
   ```

2. **Start the frontend development server**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Use the CLI**
   ```bash
   cd backend
   vcf-hcx --help
   ```

## Project Structure

```
vcf-hcx-automator/
├── backend/                 # Python backend service
│   ├── src/vcf_hcx_automator/
│   │   ├── app.py          # Litestar application
│   │   ├── main.py         # CLI entry point
│   │   ├── config/         # Configuration management
│   │   ├── models/         # Data models (msgspec)
│   │   ├── services/       # Business logic
│   │   └── cli/           # CLI commands (cyclopts)
│   ├── tests/              # Test suite
│   └── pyproject.toml      # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── main.tsx        # Application entry point
│   │   ├── lib/            # API client and utilities
│   │   ├── components/     # Reusable components
│   │   └── routes/         # Route components
│   ├── package.json        # Node.js dependencies
│   └── vite.config.ts      # Vite configuration
├── docker-compose.yml      # Convex DB setup
└── README.md              # This file
```

## Technology Stack

### Backend
- **Python 3.13+** - Runtime
- **Litestar** - Modern ASGI web framework
- **msgspec** - Fast serialization and validation
- **Cyclopts** - Modern CLI framework
- **Pydantic Settings** - Configuration management
- **HTTPX** - Async HTTP client

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **TanStack Router** - Type-safe routing
- **TanStack Query** - Server state management
- **Tailwind CSS** - Utility-first styling
- **Vite** - Build tool and dev server

### Infrastructure
- **Convex DB** - Database and real-time sync
- **Docker Compose** - Local development environment

## API Endpoints

- `GET /health` - Health check
- `GET /sites` - List HCX sites
- `POST /migrations` - Create migration
- `GET /migrations/{migration_id}` - Get migration status

## CLI Commands

```bash
# Test connection to VCF/HCX
vcf-hcx test-connection

# List available sites
vcf-hcx list-sites

# Create a migration
vcf-hcx create-migration source-site destination-site vm1 vm2

# Check migration status
vcf-hcx migration-status mig-123

# Show configuration
vcf-hcx show-config
```

## Development

### Backend Development

```bash
cd backend

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src tests

# Lint code
ruff check src tests

# Type checking
mypy src
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Lint code
npm run lint
```

## Configuration

### Backend Environment Variables

Create a `.env` file in the backend directory:

```env
# VCF/HCX Configuration
VCF_HOST=https://your-vcf-host.example.com
VCF_USERNAME=your-username
VCF_PASSWORD=your-password
VCF_VERIFY_SSL=true

# API Configuration
API_HOST=127.0.0.1
API_PORT=8000
DEBUG=false

# Convex DB Configuration
CONVEX_URL=http://localhost:3210
CONVEX_TOKEN=your-convex-token

# Logging
LOG_LEVEL=INFO
```

### Frontend Environment Variables

Create a `.env` file in the frontend directory:

```env
# API URL (optional, defaults to http://localhost:8000)
VITE_API_URL=http://localhost:8000
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.