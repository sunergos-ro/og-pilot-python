"""
OG Pilot Template Tags

Django template tags for generating OG Pilot images.

Usage in templates:
    {% load og_pilot_tags %}

    <!-- Generate image URL -->
    {% og_pilot_image template="blog_post" title="My Post" as og_url %}
    <meta property="og:image" content="{{ og_url }}" />

    <!-- Or use the simple tag directly -->
    <meta property="og:image" content="{% og_pilot_url template='default' title='Hello' %}" />
"""

import time
from typing import Any

from django import template

import og_pilot

register = template.Library()


@register.simple_tag
def og_pilot_url(
    title: str,
    template: str = "default",
    iat: int | None = None,
    **kwargs: Any,
) -> str:
    """
    Generate an OG Pilot image URL.

    Args:
        title: The title for the OG image (required)
        template: Template name to use (default: "default")
        iat: Issue time for cache busting. If not provided, uses current day.
        **kwargs: Additional template parameters

    Returns:
        The generated image URL

    Example:
        {% og_pilot_url title="My Page Title" template="blog_post" author="John" %}
    """
    params = {
        "template": template,
        "title": title,
        **kwargs,
    }

    # Use current day for cache busting if not provided
    if iat is None:
        # Round to start of day for daily cache busting
        iat = int(time.time()) // 86400 * 86400

    result = og_pilot.create_image(params, iat=iat)
    # create_image returns str when json_response=False (the default)
    return str(result)


@register.simple_tag
def og_pilot_image(
    title: str,
    template: str = "default",
    iat: int | None = None,
    **kwargs: Any,
) -> str:
    """
    Alias for og_pilot_url for semantic clarity.

    Example:
        {% og_pilot_image title="My Blog Post" template="blog" as og_url %}
    """
    return str(og_pilot_url(title=title, template=template, iat=iat, **kwargs))


@register.inclusion_tag("og_pilot/meta_tags.html")
def og_pilot_meta_tags(
    title: str,
    description: str = "",
    template: str = "default",
    site_name: str = "",
    **kwargs: Any,
) -> dict[str, str]:
    """
    Render complete Open Graph meta tags with OG Pilot image.

    Args:
        title: Page title
        description: Page description
        template: OG Pilot template name
        site_name: Site name for og:site_name
        **kwargs: Additional template parameters

    Returns:
        Context dict for the template

    Example:
        {% og_pilot_meta_tags title="My Page" description="Description" %}
    """
    image_url = og_pilot_url(title=title, template=template, **kwargs)

    return {
        "title": title,
        "description": description,
        "image_url": image_url,
        "site_name": site_name,
    }
