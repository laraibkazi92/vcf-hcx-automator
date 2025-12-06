# VCF HCX Automator - Backend

Backend service for automating VCF VMware HCX workflows.

## Installation

```bash
# Install in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

## Configuration

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

## Usage

### CLI Commands

```bash
# Test connection to VCF/HCX
vcf-hcx test-connection

# List available sites
vcf-hcx list-sites

# Create a migration
vcf-hcx create-migration source-site destination-site vm1 vm2 --migration-type v2v

# Check migration status
vcf-hcx migration-status mig-123

# Show current configuration
vcf-hcx show-config
```

### API Server

```bash
# Start the API server
litestar run --host 127.0.0.1 --port 8000

# Or using the module
python -m vcf_hcx_automator.app
```

#### API Endpoints

- `GET /health` - Health check
- `GET /sites` - List HCX sites
- `POST /migrations` - Create migration
- `GET /migrations/{migration_id}` - Get migration status

## Development

```bash
# Run tests
pytest

# Format code
black src tests

# Lint code
ruff check src tests

# Type checking
mypy src
```

## Project Structure

```
backend/
├── src/vcf_hcx_automator/
│   ├── __init__.py
│   ├── main.py          # CLI entry point
│   ├── app.py           # Litestar application
│   ├── config/          # Configuration management
│   ├── models/          # Data models (msgspec)
│   ├── services/        # Business logic
│   └── cli/             # CLI commands (cyclopts)
├── tests/               # Test suite
└── pyproject.toml       # Project configuration
```