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
Supported templates: `page`, `blog_post`, `podcast`, `product`, `event`, `book`, `company`, `portfolio`, `github`.

Use these helpers to force a specific template:

- `og_pilot.create_blog_post_image(...)`
- `og_pilot.create_podcast_image(...)`
- `og_pilot.create_product_image(...)`
- `og_pilot.create_event_image(...)`
- `og_pilot.create_book_image(...)`
- `og_pilot.create_company_image(...)`
- `og_pilot.create_portfolio_image(...)`
- For `github`, use `og_pilot.create_image(template=\"github\", ...)` (no dedicated helper yet).

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

<!-- OG_SAMPLES_START -->
## OG Image Examples

All sample payloads set explicit `bg_color`, `text_color`, and logo/avatar URLs to avoid default branding fallbacks.

For templates that support custom images, this set includes both `with_custom_image` and `without_custom_image` variants. (`github` currently has no custom image slot.)

Avatar-style fields (for example `author_avatar_url`) use DiceBear Avataaars, e.g. `https://api.dicebear.com/7.x/avataaars/svg?seed=JaneSmith`.

### Sample Gallery

| Template | Variant | Preview |
|---|---|---|
| `page` | `with custom image` | ![page_with_custom_image](https://img.ogpilot.com/1f6oY498I6SiNfqGDjwdHLNpwmeU264t2OL0k7tY8Mw/plain/s3://og-pilot-development/eoo5v45d766hf22j4r2al60ktali) |
| `page` | `without custom image` | ![page_without_custom_image](https://img.ogpilot.com/9MZdTcTRyOoRqpTLll__EvDimmgojZESfZWokDqXeZM/plain/s3://og-pilot-development/wfa9es2wuvp6btjiriekk53swp6n) |
| `blog_post` | `with custom image` | ![blog_post_with_custom_image](https://img.ogpilot.com/RBBQZnBrAKcVmFjJg6UtNqX8P6nRRQdGLrlJNWYif7I/plain/s3://og-pilot-development/je7pj816exul9umhyszqpnbxelmd) |
| `blog_post` | `without custom image` | ![blog_post_without_custom_image](https://img.ogpilot.com/yP1B7OrLOy9Iu9JDSNk9Veys3ESCuCSBM9il2wq13V4/plain/s3://og-pilot-development/6aei8frvun6kvqojoor1hqack31y) |
| `podcast` | `with custom image` | ![podcast_with_custom_image](https://img.ogpilot.com/rzOOt7PWJ44OEwpKnntMLZaPvtl76DA3yRlj6B6N-Cc/plain/s3://og-pilot-development/fmkeblwertneuy4p82foeg5rfltl) |
| `podcast` | `without custom image` | ![podcast_without_custom_image](https://img.ogpilot.com/5UWWFG2J5bNRDOhDkN96ZG_g0XI9ULGDFgQkuVTjCYQ/plain/s3://og-pilot-development/yyhmo7lamj1n99i2n6dyttwungmq) |
| `product` | `with custom image` | ![product_with_custom_image](https://img.ogpilot.com/mzmHDMjyAX4VlpJanMT3zpmIJgSuClYI5eofhFpSJNQ/plain/s3://og-pilot-development/8ls2legb316l9vak40nu388uzy2t) |
| `product` | `without custom image` | ![product_without_custom_image](https://img.ogpilot.com/kK6d7xU3EWT5WKC6jKCw1rhJDmv9bwvRn2S-nShV4NA/plain/s3://og-pilot-development/52ns2l1ll7hjhfg0p3wn5c9pqtr5) |
| `event` | `with custom image` | ![event_with_custom_image](https://img.ogpilot.com/A7nxHkYs4xN4c1PhH2KQSWoB4ALwBdpP0HPiAss9_70/plain/s3://og-pilot-development/vjkdf6cx82dvdxmhiwtvrvkl976d) |
| `event` | `without custom image` | ![event_without_custom_image](https://img.ogpilot.com/elpfu28vJ57XCGx3npKhCwXqqJnPoqwCm8Aj5SLkWsM/plain/s3://og-pilot-development/vpte818nvtegc60ta98q7pmw91c8) |
| `book` | `with custom image` | ![book_with_custom_image](https://img.ogpilot.com/7pidSkvU_l0RzY9xBOLSa2x-jDWWvx14Gtv-KMDCGLw/plain/s3://og-pilot-development/cwnhb631ls2olk0yzkukmr5dnf7e) |
| `book` | `without custom image` | ![book_without_custom_image](https://img.ogpilot.com/FpMbBN15SLgaK9FEX07xXcT5dQIWyZkFdHaZ9i5wx3U/plain/s3://og-pilot-development/0rzisfn2qswdzsz641rl3s29ngu9) |
| `portfolio` | `with custom image` | ![portfolio_with_custom_image](https://img.ogpilot.com/gauiw2MMcNLLSFnQ07Hq3flv4S0L-89lnnjUOO0VgYU/plain/s3://og-pilot-development/qok04llq0ff3d2lherudwlhqxslm) |
| `portfolio` | `without custom image` | ![portfolio_without_custom_image](https://img.ogpilot.com/jVck9SDPlei0gaHq44_itLoVzn2wINrCP3XCTQF3SYs/plain/s3://og-pilot-development/jxa1s7dtibaeqamh0fsymwz7uqrx) |
| `company` | `with custom image` | ![company_with_custom_image](https://img.ogpilot.com/rji7hNgoxRM1KF2GofIO9gqXJQNg5CqlPWbhbGpR4FA/plain/s3://og-pilot-development/2xl6zi3zgjm74izr46efduzhmbrr) |
| `company` | `without custom image` | ![company_without_custom_image](https://img.ogpilot.com/PgGl9a6xPmG0Tn7qKmZZUczrv43cNLxzyISsbHG8_oE/plain/s3://og-pilot-development/6gmm6jg5r8ya27r3tr215edfd972) |
| `github` | `default` | ![github_activity](https://img.ogpilot.com/0dxm83dTyNCg5Dq_GZFT4SqsRyTWUO31d0HQwjIq0-A/plain/s3://og-pilot-development/jlhwskjsx08x56attaljw3ce0p65) |

### Parameters Used

<details>
<summary>Exact payloads for these samples</summary>

```json
[
  {
    "id": "page_with_custom_image",
    "template": "page",
    "variant": "with_custom_image",
    "params": {
      "title": "Acme Robotics Product Updates",
      "description": "See what shipped this week across the web app.",
      "logo_url": "https://www.google.com/s2/favicons?sz=128&domain_url=https%3A%2F%2Fwww.notion.so",
      "image_url": "https://images.unsplash.com/photo-1558655146-d09347e92766?w=1400&q=80",
      "bg_color": "#0B1220",
      "text_color": "#F8FAFC",
      "template": "page"
    },
    "image_url": "https://img.ogpilot.com/1f6oY498I6SiNfqGDjwdHLNpwmeU264t2OL0k7tY8Mw/plain/s3://og-pilot-development/eoo5v45d766hf22j4r2al60ktali"
  },
  {
    "id": "page_without_custom_image",
    "template": "page",
    "variant": "without_custom_image",
    "params": {
      "title": "Notion AI Workspace for Product Teams",
      "description": "Docs, specs, and roadmaps in one living workspace.",
      "logo_url": "https://www.google.com/s2/favicons?sz=128&domain_url=https%3A%2F%2Fwww.notion.so",
      "bg_color": "#111827",
      "text_color": "#E5E7EB",
      "template": "page"
    },
    "image_url": "https://img.ogpilot.com/9MZdTcTRyOoRqpTLll__EvDimmgojZESfZWokDqXeZM/plain/s3://og-pilot-development/wfa9es2wuvp6btjiriekk53swp6n"
  },
  {
    "id": "blog_post_with_custom_image",
    "template": "blog_post",
    "variant": "with_custom_image",
    "params": {
      "title": "How Stripe Reduced Checkout Abandonment by 18%",
      "logo_url": "https://www.google.com/s2/favicons?sz=128&domain_url=https%3A%2F%2Fstripe.com",
      "image_url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1400&q=80",
      "author_name": "Maya Patel",
      "author_avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=MayaPatel",
      "publish_date": "2026-02-24",
      "bg_color": "#0F172A",
      "text_color": "#F8FAFC",
      "template": "blog_post"
    },
    "image_url": "https://img.ogpilot.com/RBBQZnBrAKcVmFjJg6UtNqX8P6nRRQdGLrlJNWYif7I/plain/s3://og-pilot-development/je7pj816exul9umhyszqpnbxelmd"
  },
  {
    "id": "blog_post_without_custom_image",
    "template": "blog_post",
    "variant": "without_custom_image",
    "params": {
      "title": "Inside Vercel's Edge Rendering Playbook",
      "logo_url": "https://www.google.com/s2/favicons?sz=128&domain_url=https%3A%2F%2Fvercel.com",
      "author_name": "Daniel Kim",
      "author_avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=DanielKim",
      "publish_date": "2026-02-18",
      "bg_color": "#111827",
      "text_color": "#E5E7EB",
      "template": "blog_post"
    },
    "image_url": "https://img.ogpilot.com/yP1B7OrLOy9Iu9JDSNk9Veys3ESCuCSBM9il2wq13V4/plain/s3://og-pilot-development/6aei8frvun6kvqojoor1hqack31y"
  },
  {
    "id": "podcast_with_custom_image",
    "template": "podcast",
    "variant": "with_custom_image",
    "params": {
      "title": "Indie Hackers Podcast: Pricing Experiments That Worked",
      "logo_url": "https://www.google.com/s2/favicons?sz=128&domain_url=https%3A%2F%2Fwww.spotify.com",
      "image_url": "https://images.unsplash.com/photo-1478737270239-2f02b77fc618?w=1400&q=80",
      "episode_date": "2026-02-21",
      "bg_color": "#18181B",
      "text_color": "#FAFAFA",
      "template": "podcast"
    },
    "image_url": "https://img.ogpilot.com/rzOOt7PWJ44OEwpKnntMLZaPvtl76DA3yRlj6B6N-Cc/plain/s3://og-pilot-development/fmkeblwertneuy4p82foeg5rfltl"
  },
  {
    "id": "podcast_without_custom_image",
    "template": "podcast",
    "variant": "without_custom_image",
    "params": {
      "title": "Shopify Masters: Building a 7-Figure DTC Brand",
      "logo_url": "https://www.google.com/s2/favicons?sz=128&domain_url=https%3A%2F%2Fwww.shopify.com",
      "episode_date": "2026-02-19",
      "bg_color": "#0B1120",
      "text_color": "#E2E8F0",
      "template": "podcast"
    },
    "image_url": "https://img.ogpilot.com/5UWWFG2J5bNRDOhDkN96ZG_g0XI9ULGDFgQkuVTjCYQ/plain/s3://og-pilot-development/yyhmo7lamj1n99i2n6dyttwungmq"
  },
  {
    "id": "product_with_custom_image",
    "template": "product",
    "variant": "with_custom_image",
    "params": {
      "title": "Allbirds Tree Dasher 3",
      "logo_url": "https://www.google.com/s2/favicons?sz=128&domain_url=https%3A%2F%2Fwww.allbirds.com",
      "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=1400&q=80",
      "unique_selling_point": "Free shipping + 30-day returns",
      "bg_color": "#F8FAFC",
      "text_color": "#0F172A",
      "template": "product"
    },
    "image_url": "https://img.ogpilot.com/mzmHDMjyAX4VlpJanMT3zpmIJgSuClYI5eofhFpSJNQ/plain/s3://og-pilot-development/8ls2legb316l9vak40nu388uzy2t"
  },
  {
    "id": "product_without_custom_image",
    "template": "product",
    "variant": "without_custom_image",
    "params": {
      "title": "Bose QuietComfort Ultra",
      "logo_url": "https://www.google.com/s2/favicons?sz=128&domain_url=https%3A%2F%2Fwww.bose.com",
      "unique_selling_point": "Save $70 this weekend",
      "bg_color": "#111827",
      "text_color": "#F9FAFB",
      "template": "product"
    },
    "image_url": "https://img.ogpilot.com/kK6d7xU3EWT5WKC6jKCw1rhJDmv9bwvRn2S-nShV4NA/plain/s3://og-pilot-development/52ns2l1ll7hjhfg0p3wn5c9pqtr5"
  },
  {
    "id": "event_with_custom_image",
    "template": "event",
    "variant": "with_custom_image",
    "params": {
      "title": "Launch Week Berlin 2026",
      "logo_url": "https://www.google.com/s2/favicons?sz=128&domain_url=https%3A%2F%2Fwww.eventbrite.com",
      "image_url": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=1400&q=80",
      "event_date": "2026-06-12/2026-06-14",
      "event_location": "Station Berlin",
      "bg_color": "#1E1B4B",
      "text_color": "#F5F3FF",
      "template": "event"
    },
    "image_url": "https://img.ogpilot.com/A7nxHkYs4xN4c1PhH2KQSWoB4ALwBdpP0HPiAss9_70/plain/s3://og-pilot-development/vjkdf6cx82dvdxmhiwtvrvkl976d"
  },
  {
    "id": "event_without_custom_image",
    "template": "event",
    "variant": "without_custom_image",
    "params": {
      "title": "RubyConf Chicago 2026",
      "logo_url": "https://www.google.com/s2/favicons?sz=128&domain_url=https%3A%2F%2Frubyconf.org",
      "event_date": "2026-11-17",
      "event_location": "Chicago, IL",
      "bg_color": "#312E81",
      "text_color": "#EEF2FF",
      "template": "event"
    },
    "image_url": "https://img.ogpilot.com/elpfu28vJ57XCGx3npKhCwXqqJnPoqwCm8Aj5SLkWsM/plain/s3://og-pilot-development/vpte818nvtegc60ta98q7pmw91c8"
  },
  {
    "id": "book_with_custom_image",
    "template": "book",
    "variant": "with_custom_image",
    "params": {
      "title": "Designing APIs for Humans",
      "description": "A practical handbook for product-minded engineers.",
      "logo_url": "https://www.google.com/s2/favicons?sz=128&domain_url=https%3A%2F%2Fwww.oreilly.com",
      "image_url": "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=1400&q=80",
      "book_author": "Alex Turner",
      "book_series_number": "2",
      "book_genre": "Technology",
      "bg_color": "#172554",
      "text_color": "#EFF6FF",
      "template": "book"
    },
    "image_url": "https://img.ogpilot.com/7pidSkvU_l0RzY9xBOLSa2x-jDWWvx14Gtv-KMDCGLw/plain/s3://og-pilot-development/cwnhb631ls2olk0yzkukmr5dnf7e"
  },
  {
    "id": "book_without_custom_image",
    "template": "book",
    "variant": "without_custom_image",
    "params": {
      "title": "The Product Operating System",
      "description": "How modern teams ship with confidence.",
      "logo_url": "https://www.google.com/s2/favicons?sz=128&domain_url=https%3A%2F%2Fwww.penguinrandomhouse.com",
      "book_author": "Sofia Ramirez",
      "book_series_number": "1",
      "book_genre": "Business",
      "bg_color": "#1E293B",
      "text_color": "#F8FAFC",
      "template": "book"
    },
    "image_url": "https://img.ogpilot.com/FpMbBN15SLgaK9FEX07xXcT5dQIWyZkFdHaZ9i5wx3U/plain/s3://og-pilot-development/0rzisfn2qswdzsz641rl3s29ngu9"
  },
  {
    "id": "portfolio_with_custom_image",
    "template": "portfolio",
    "variant": "with_custom_image",
    "params": {
      "title": "Maya Chen • Product Designer",
      "description": "Fintech UX, design systems, and prototyping.",
      "logo_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=MayaChen&size=64",
      "image_url": "https://images.unsplash.com/photo-1557672172-298e090bd0f1?w=1400&q=80",
      "bg_color": "#1F2937",
      "text_color": "#F9FAFB",
      "template": "portfolio"
    },
    "image_url": "https://img.ogpilot.com/gauiw2MMcNLLSFnQ07Hq3flv4S0L-89lnnjUOO0VgYU/plain/s3://og-pilot-development/qok04llq0ff3d2lherudwlhqxslm"
  },
  {
    "id": "portfolio_without_custom_image",
    "template": "portfolio",
    "variant": "without_custom_image",
    "params": {
      "title": "Arjun Rao • Frontend Engineer",
      "description": "React performance, accessibility, and DX.",
      "logo_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=ArjunRao&size=64",
      "bg_color": "#0F172A",
      "text_color": "#E2E8F0",
      "template": "portfolio"
    },
    "image_url": "https://img.ogpilot.com/jVck9SDPlei0gaHq44_itLoVzn2wINrCP3XCTQF3SYs/plain/s3://og-pilot-development/jxa1s7dtibaeqamh0fsymwz7uqrx"
  },
  {
    "id": "company_with_custom_image",
    "template": "company",
    "variant": "with_custom_image",
    "params": {
      "title": "Notion",
      "description": "4 job openings",
      "logo_url": "https://www.google.com/s2/favicons?sz=128&domain_url=https%3A%2F%2Fwww.notion.so",
      "bg_color": "#111827",
      "text_color": "#F9FAFB",
      "template": "company"
    },
    "image_url": "https://img.ogpilot.com/rji7hNgoxRM1KF2GofIO9gqXJQNg5CqlPWbhbGpR4FA/plain/s3://og-pilot-development/2xl6zi3zgjm74izr46efduzhmbrr"
  },
  {
    "id": "company_without_custom_image",
    "template": "company",
    "variant": "without_custom_image",
    "params": {
      "title": "Linear",
      "description": "12 job openings",
      "company_logo_url": "https://www.google.com/s2/favicons?sz=256&domain_url=https%3A%2F%2Flinear.app",
      "bg_color": "#0B1220",
      "text_color": "#E5E7EB",
      "template": "company",
      "iss": "gitdigest.ai"
    },
    "image_url": "https://img.ogpilot.com/PgGl9a6xPmG0Tn7qKmZZUczrv43cNLxzyISsbHG8_oE/plain/s3://og-pilot-development/6gmm6jg5r8ya27r3tr215edfd972"
  },
  {
    "id": "github_activity",
    "template": "github",
    "variant": "default",
    "params": {
      "title": "rails/rails",
      "description": "Recent merged PRs, reviews, and commit activity.",
      "accent_color": "#22C55E",
      "bg_color": "#0B1220",
      "text_color": "#E5E7EB",
      "contributions": [
        {
          "date": "2025-10-28",
          "count": 6
        },
        {
          "date": "2025-11-01",
          "count": 3
        },
        {
          "date": "2025-11-05",
          "count": 9
        },
        {
          "date": "2025-11-08",
          "count": 12
        },
        {
          "date": "2025-11-12",
          "count": 7
        },
        {
          "date": "2025-11-16",
          "count": 11
        },
        {
          "date": "2025-11-20",
          "count": 5
        },
        {
          "date": "2025-11-24",
          "count": 14
        },
        {
          "date": "2025-11-28",
          "count": 8
        },
        {
          "date": "2025-12-02",
          "count": 4
        },
        {
          "date": "2025-12-06",
          "count": 10
        },
        {
          "date": "2025-12-10",
          "count": 15
        },
        {
          "date": "2025-12-14",
          "count": 6
        },
        {
          "date": "2025-12-18",
          "count": 9
        },
        {
          "date": "2025-12-22",
          "count": 13
        },
        {
          "date": "2025-12-26",
          "count": 4
        },
        {
          "date": "2025-12-30",
          "count": 7
        },
        {
          "date": "2026-01-03",
          "count": 11
        },
        {
          "date": "2026-01-07",
          "count": 16
        },
        {
          "date": "2026-01-11",
          "count": 12
        },
        {
          "date": "2026-01-15",
          "count": 6
        },
        {
          "date": "2026-01-19",
          "count": 8
        },
        {
          "date": "2026-01-23",
          "count": 14
        },
        {
          "date": "2026-01-27",
          "count": 9
        },
        {
          "date": "2026-01-31",
          "count": 5
        },
        {
          "date": "2026-02-04",
          "count": 13
        },
        {
          "date": "2026-02-08",
          "count": 17
        },
        {
          "date": "2026-02-12",
          "count": 10
        },
        {
          "date": "2026-02-16",
          "count": 7
        },
        {
          "date": "2026-02-20",
          "count": 12
        },
        {
          "date": "2026-02-24",
          "count": 9
        }
      ],
      "template": "github"
    },
    "image_url": "https://img.ogpilot.com/0dxm83dTyNCg5Dq_GZFT4SqsRyTWUO31d0HQwjIq0-A/plain/s3://og-pilot-development/jlhwskjsx08x56attaljw3ce0p65"
  }
]
```

</details>

<!-- OG_SAMPLES_END -->





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

### Strip query parameters

When `strip_query_parameters` is enabled, the client removes any query string from
the resolved path before building the signed payload. This keeps analytics
focused on the canonical path regardless of campaign, tracking, or pagination
parameters, and works together with `strip_extensions`.

```python
og_pilot.configure(
    api_key="your-api-key",
    domain="example.com",
    strip_query_parameters=True,
)

# All of these normalize to "/news" before the JWT is generated:
og_pilot.create_image(title="News", path="/news")
og_pilot.create_image(title="News", path="/news?utm_source=weekly")
og_pilot.create_image(title="News", path="https://example.com/news?ref=api")
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
    # 'STRIP_QUERY_PARAMETERS': True,
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
| `strip_query_parameters` | - | `False` | Drop query parameters from resolved paths before signing (see [Strip query parameters](#strip-query-parameters)) |

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
- `github` template: use `og_pilot.create_image(template=\"github\", ...)` (no dedicated helper yet).

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
