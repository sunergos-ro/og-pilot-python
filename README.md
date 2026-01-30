# OG Pilot Python

A Python client for generating OG Pilot Open Graph images via signed JWTs, with first-class Django integration.

## Installation

```bash
pip install og-pilot
```

For Django integration:

```bash
pip install og-pilot[django]
```

## Quick Start

### Basic Usage

```python
import og_pilot

# Configure globally (reads from OG_PILOT_API_KEY and OG_PILOT_DOMAIN env vars by default)
og_pilot.configure(
    api_key="your-api-key",
    domain="example.com"
)

# Generate an image URL
image_url = og_pilot.create_image(
    template="blog_post",
    title="How to Build Amazing OG Images",
    description="A complete guide to social media previews",
    author_name="Jane Smith",
)

print(image_url)
# https://ogpilot.com/api/v1/images?token=eyJ...
```

### Using Environment Variables

The SDK automatically reads from environment variables:

```bash
export OG_PILOT_API_KEY="your-api-key"
export OG_PILOT_DOMAIN="example.com"
```

```python
import og_pilot

# No configuration needed - uses env vars
url = og_pilot.create_image(title="My Page", template="default")
```

### Cache Busting with `iat`

By default, OG Pilot caches images indefinitely. Use `iat` (issued at) to refresh the cache:

```python
import time
from datetime import datetime

# Using Unix timestamp
url = og_pilot.create_image(
    title="My Post",
    template="blog",
    iat=int(time.time())  # Changes daily
)

# Using datetime
url = og_pilot.create_image(
    title="My Post",
    template="blog",
    iat=datetime.now()
)
```

### Get JSON Metadata

```python
data = og_pilot.create_image(
    title="Hello OG Pilot",
    template="page",
    json=True
)
print(data)  # {"url": "...", "width": 1200, "height": 630, ...}
```

### Custom Client Instance

For multiple configurations or dependency injection:

```python
from og_pilot import create_client

client = create_client(
    api_key="your-api-key",
    domain="example.com",
    open_timeout=10,
    read_timeout=30,
)

url = client.create_image({"template": "default", "title": "Hello"})
```

## Django Integration

### 1. Add to Installed Apps

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'og_pilot.django',
]
```

### 2. Configure Settings

```python
# settings.py

# Option 1: Using settings dict
OG_PILOT = {
    'API_KEY': 'your-api-key',  # or use OG_PILOT_API_KEY env var
    'DOMAIN': 'example.com',     # or use OG_PILOT_DOMAIN env var
    # Optional:
    # 'BASE_URL': 'https://ogpilot.com',
    # 'OPEN_TIMEOUT': 5,
    # 'READ_TIMEOUT': 10,
}

# Option 2: Using environment variables (no settings needed)
# Just set OG_PILOT_API_KEY and OG_PILOT_DOMAIN
```

### 3. Verify Configuration

```bash
python manage.py og_pilot_check
python manage.py og_pilot_check --test  # Also sends a test request
```

### 4. Use in Templates

```html
{% load og_pilot_tags %}

<!DOCTYPE html>
<html>
<head>
    <!-- Option 1: Generate URL and use manually -->
    {% og_pilot_image title=page.title template="blog_post" as og_image_url %}
    <meta property="og:image" content="{{ og_image_url }}" />
    <meta property="og:title" content="{{ page.title }}" />

    <!-- Option 2: Simple tag (outputs URL directly) -->
    <meta property="og:image" content="{% og_pilot_url title=page.title template='default' %}" />

    <!-- Option 3: Complete meta tags (requires template) -->
    {% og_pilot_meta_tags title=page.title description=page.description template="blog" %}
</head>
<body>
    ...
</body>
</html>
```

### 5. Use in Views

```python
from django.shortcuts import render
import og_pilot

def blog_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    
    og_image_url = og_pilot.create_image(
        template="blog_post",
        title=post.title,
        description=post.excerpt,
        author_name=post.author.name,
        publish_date=post.published_at.strftime("%Y-%m-%d"),
    )
    
    return render(request, 'blog/post.html', {
        'post': post,
        'og_image_url': og_image_url,
    })
```

### Custom Meta Tags Template

Create `templates/og_pilot/meta_tags.html` in your project to customize the output of `{% og_pilot_meta_tags %}`:

```html
<!-- templates/og_pilot/meta_tags.html -->
<meta property="og:title" content="{{ title }}" />
<meta property="og:description" content="{{ description }}" />
<meta property="og:image" content="{{ image_url }}" />
<meta property="og:type" content="article" />
<meta property="og:site_name" content="{{ site_name }}" />

<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{{ title }}" />
<meta name="twitter:description" content="{{ description }}" />
<meta name="twitter:image" content="{{ image_url }}" />
```

## Configuration Options

| Option | Environment Variable | Default | Description |
|--------|---------------------|---------|-------------|
| `api_key` | `OG_PILOT_API_KEY` | None | Your OG Pilot API key (required) |
| `domain` | `OG_PILOT_DOMAIN` | None | Your registered domain (required) |
| `base_url` | - | `https://ogpilot.com` | OG Pilot API URL |
| `open_timeout` | - | `5` | Connection timeout (seconds) |
| `read_timeout` | - | `10` | Read timeout (seconds) |

## Error Handling

```python
from og_pilot import create_image
from og_pilot.exceptions import ConfigurationError, RequestError

try:
    url = create_image(title="My Post", template="blog")
except ConfigurationError as e:
    # Missing API key or domain
    print(f"Configuration error: {e}")
except RequestError as e:
    # API request failed
    print(f"Request error: {e}")
    if e.status_code:
        print(f"Status code: {e.status_code}")
except ValueError as e:
    # Missing required parameter (e.g., title)
    print(f"Validation error: {e}")
```

## API Reference

### Module-level Functions

- `og_pilot.configure(**kwargs)` - Configure the global client
- `og_pilot.reset_config()` - Reset to default configuration
- `og_pilot.get_config()` - Get the current configuration
- `og_pilot.client()` - Get a client using global config
- `og_pilot.create_client(**kwargs)` - Create a new client with custom config
- `og_pilot.create_image(params, *, json=False, iat=None, headers=None, **kwargs)` - Generate image URL

### Client Class

```python
from og_pilot import Client, Configuration

config = Configuration(api_key="...", domain="...")
client = Client(config)

# Generate URL
url = client.create_image(
    params={"template": "default", "title": "Hello"},
    json_response=False,  # Set True for JSON metadata
    iat=None,             # Optional cache busting timestamp
    headers={},           # Optional additional headers
)
```

## Development

```bash
# Clone the repository
git clone https://github.com/sunergos-ro/og-pilot-python.git
cd og-pilot-python

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check .

# Run type checker
mypy og_pilot
```

---

# Publishing to PyPI

This section explains how to publish the package to PyPI so users can install it with `pip install og-pilot`.

## Prerequisites

1. **Create PyPI Account**: Register at https://pypi.org/account/register/

2. **Create API Token**: Go to https://pypi.org/manage/account/token/ and create a token with "Upload packages" scope.

3. **Install Build Tools**:
   ```bash
   pip install build twine
   ```

## Publishing Steps

### 1. Update Version

Edit `pyproject.toml` and `og_pilot/__init__.py` to update the version number:

```python
# og_pilot/__init__.py
__version__ = "0.2.0"  # New version
```

```toml
# pyproject.toml
[project]
version = "0.2.0"
```

### 2. Build the Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build source distribution and wheel
python -m build
```

This creates:
- `dist/og_pilot-0.1.0.tar.gz` (source distribution)
- `dist/og_pilot-0.1.0-py3-none-any.whl` (wheel)

### 3. Test on TestPyPI (Optional but Recommended)

```bash
# Upload to TestPyPI first
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ og-pilot
```

### 4. Upload to PyPI

```bash
# Upload to production PyPI
twine upload dist/*
```

You'll be prompted for credentials:
- Username: `__token__`
- Password: Your PyPI API token (starts with `pypi-`)

### 5. Configure Credentials (Optional)

To avoid entering credentials each time, create `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-TOKEN-HERE

[testpypi]
username = __token__
password = pypi-YOUR-TESTPYPI-TOKEN-HERE
```

Then secure it:
```bash
chmod 600 ~/.pypirc
```

## Automated Publishing with GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    environment: release
    permissions:
      id-token: write  # Required for trusted publishing
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install build dependencies
        run: pip install build
      
      - name: Build package
        run: python -m build
      
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        # Uses trusted publishing - configure at pypi.org
```

### Setting Up Trusted Publishing

1. Go to your PyPI project: https://pypi.org/manage/project/og-pilot/settings/publishing/
2. Add a new publisher:
   - Owner: `sunergos-ro`
   - Repository: `og-pilot-python`
   - Workflow: `publish.yml`
   - Environment: `release`

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH` (e.g., `1.2.3`)
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes (backward compatible)

## Release Checklist

- [ ] Update version in `pyproject.toml` and `og_pilot/__init__.py`
- [ ] Update CHANGELOG (if you have one)
- [ ] Run tests: `pytest`
- [ ] Run linter: `ruff check .`
- [ ] Run type checker: `mypy og_pilot`
- [ ] Build: `python -m build`
- [ ] Test locally: `pip install dist/*.whl`
- [ ] Upload to TestPyPI (optional)
- [ ] Upload to PyPI
- [ ] Create GitHub release with tag `v0.1.0`

## License

MIT License - see [LICENSE](LICENSE) for details.
