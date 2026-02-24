# OG Pilot Python

> [!IMPORTANT]  
> An active [OG Pilot](https://ogpilot.com?ref=og-pilot-python) subscription is required to use this package.

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
    domain="example.com",
    # strip_extensions=True,
)

# Generate an image URL
image_url = og_pilot.create_image(
    template="blog_post",
    title="How to Build Amazing OG Images",
    description="A complete guide to social media previews",
    author_name="Jane Smith",
)

print(image_url)
# https://cdn.ogpilot.com/image.png
```

The SDK sends a signed `POST` request to `https://ogpilot.com/api/v1/images?token=...`,
follows redirects automatically, and returns the final image URL (or JSON when `json_response=True`).
If generation fails (config/request/validation/etc.), it logs an error and returns a fail-safe fallback:
`None` for URL mode, `{"image_url": None}` for JSON mode.

### Using Environment Variables

The SDK automatically reads from environment variables:

```bash
export OG_PILOT_API_KEY="your-api-key"
export OG_PILOT_DOMAIN="example.com"
```

```python
import og_pilot

# No configuration needed - uses env vars
url = og_pilot.create_image(title="My Page")
```

### Cache Busting with `iat`

By default, OG Pilot caches images indefinitely. Use `iat` (issued at) to refresh the cache:

```python
import time
from datetime import datetime

# Using Unix timestamp
url = og_pilot.create_image(
    title="My Post",
    template="blog_post",
    iat=int(time.time())  # Changes daily
)

# Using datetime
url = og_pilot.create_image(
    title="My Post",
    template="blog_post",
    iat=datetime.now()
)
```

### Template helpers

`create_image` defaults to the `page` template when `template` is omitted.

Use these helpers to force a specific template:

- `og_pilot.create_blog_post_image(...)`
- `og_pilot.create_podcast_image(...)`
- `og_pilot.create_product_image(...)`
- `og_pilot.create_event_image(...)`
- `og_pilot.create_book_image(...)`
- `og_pilot.create_company_image(...)`
- `og_pilot.create_portfolio_image(...)`

```python
image_url = og_pilot.create_blog_post_image(
    title="How to Build Amazing OG Images",
    author_name="Jane Smith",
    publish_date="2024-01-15"
)
```

### Get JSON Metadata

```python
data = og_pilot.create_image(
    title="Hello OG Pilot",
    template="page",
    json_response=True
)
print(data)  # {"url": "...", "width": 1200, "height": 630, ...}
```

## Path Handling

The `path` parameter enhances OG Pilot analytics by tracking which OG images perform better across different pages on your site. By capturing the request path, you get granular insights into click-through rates and engagement for each OG image.

The client automatically injects a `path` parameter on every request:

| Option | Behavior |
|--------|----------|
| `default=False` | Uses the current request path when available (via request context or env vars), then falls back to `/` |
| `default=True` | Forces the `path` parameter to `/`, regardless of the current request (unless `path` is provided explicitly) |
| `path="/..."` | Uses the provided path verbatim (normalized to start with `/`), overriding auto-resolution |

### Automatic Framework Detection

The SDK automatically detects the current request path from popular frameworks - **no middleware setup required** for most cases:

**Flask** - Works automatically, no setup needed:

```python
from flask import Flask
import og_pilot

app = Flask(__name__)
og_pilot.configure(api_key="...", domain="example.com")

@app.route('/blog/<slug>')
def blog_post(slug):
    # Path is automatically captured from flask.request
    url = og_pilot.create_image(title="My Post", template="blog_post")
    return render_template('post.html', og_image=url)
```

**Django with django-crequest** - Install `django-crequest` for automatic detection:

```bash
pip install django-crequest
```

```python
# settings.py
MIDDLEWARE = [
    # ...
    'crequest.middleware.CrequestMiddleware',
]
```

Then it works automatically in your views:

```python
import og_pilot

def blog_post(request, slug):
    # Path is automatically captured
    url = og_pilot.create_image(title="My Post", template="blog_post")
    return render(request, 'post.html', {'og_image': url})
```

### Manual Setup (Optional)

If automatic detection doesn't work for your setup, you can manually set the request context:

**Django Middleware (without django-crequest):**

```python
from og_pilot import set_current_request, clear_current_request

class OgPilotMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        set_current_request({'url': request.get_full_path()})
        try:
            return self.get_response(request)
        finally:
            clear_current_request()
```

**FastAPI:**

```python
from og_pilot import set_current_request, clear_current_request

@app.middleware("http")
async def og_pilot_middleware(request: Request, call_next):
    set_current_request({'url': str(request.url.path)})
    try:
        return await call_next(request)
    finally:
        clear_current_request()
```

**Using with_request_context:**

```python
from og_pilot import with_request_context, create_image

url = with_request_context(
    {'url': '/blog/my-post'},
    lambda: create_image(title="My Blog Post", template="blog_post")
)
```

### Manual Path Override

```python
url = og_pilot.create_image(
    template="page",
    title="Hello OG Pilot",
    path="/pricing?plan=pro"
)
```

### Default Path

```python
url = og_pilot.create_image(
    template="blog_post",
    title="Default OG Image",
    default=True
)
# path is set to "/"
```

### Strip extensions

When `strip_extensions` is enabled, the client removes file extensions from the
last segment of every resolved path. This ensures that `/docs`, `/docs.md`,
`/docs.php`, and `/docs.html` all resolve to `"/docs"`, so analytics are
consolidated under a single path regardless of the URL extension.

Multiple extensions are also stripped (`/archive.tar.gz` becomes `/archive`).
Dotfiles like `/.hidden` are left unchanged. Query strings are preserved.

```python
og_pilot.configure(
    api_key="your-api-key",
    domain="example.com",
    strip_extensions=True,
)

# All of these resolve to path "/docs":
og_pilot.create_image(title="Docs", path="/docs")
og_pilot.create_image(title="Docs", path="/docs.md")
og_pilot.create_image(title="Docs", path="/docs.php")

# Nested paths work too: /blog/my-post.html → /blog/my-post
# Query strings are preserved: /docs.md?ref=main → /docs?ref=main
# Dotfiles are unchanged: /.hidden stays /.hidden
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
    # 'STRIP_EXTENSIONS': True,
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
    <meta property="og:image" content="{% og_pilot_url title=page.title template='page' %}" />

    <!-- Option 3: Complete meta tags (requires template) -->
    {% og_pilot_meta_tags title=page.title description=page.description template="blog_post" %}
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
| `strip_extensions` | - | `True` | Strip file extensions from resolved paths (see [Strip extensions](#strip-extensions)) |

## Error Handling

`create_image` is fail-safe and does not raise errors to your application.
On failures (config, request, validation, or JSON parsing), it logs at error level and returns:

- URL mode (`json_response=False`): `None`
- JSON mode (`json_response=True`): `{"image_url": None}`

```python
import logging
from og_pilot import create_image

logging.basicConfig(level=logging.ERROR)

url = create_image(title="My Post", template="blog_post")
if url is None:
    # Handle fallback
    ...

data = create_image(title="My Post", template="blog_post", json_response=True)
assert data == {"image_url": None} or "url" in data
```

## API Reference

### Module-level Functions

- `og_pilot.configure(**kwargs)` - Configure the global client
- `og_pilot.reset_config()` - Reset to default configuration
- `og_pilot.get_config()` - Get the current configuration
- `og_pilot.client()` - Get a client using global config
- `og_pilot.create_client(**kwargs)` - Create a new client with custom config
- `og_pilot.create_image(params, *, json_response=False, iat=None, headers=None, default=False, **kwargs)` - Generate image URL via signed `POST /api/v1/images` (defaults to `page` template). Fail-safe on errors: returns `None` (URL mode) or `{"image_url": None}` (JSON mode) and logs at error level.
- `og_pilot.create_blog_post_image(...)`
- `og_pilot.create_podcast_image(...)`
- `og_pilot.create_product_image(...)`
- `og_pilot.create_event_image(...)`
- `og_pilot.create_book_image(...)`
- `og_pilot.create_company_image(...)`
- `og_pilot.create_portfolio_image(...)`

### Client Class

```python
from og_pilot import Client, Configuration

config = Configuration(api_key="...", domain="...")
client = Client(config)

# Generate URL
url = client.create_image(
    params={"template": "page", "title": "Hello"},
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
