#!/usr/bin/env python
# ABOUTME: CLI for Nano Banana Pro image generation and editing
# ABOUTME: Usage: nb.py [options] "prompt" OR nb.py -f prompt.txt [-i input.jpg] [-o output.png]

import argparse
import base64
import os
import sys
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO


def get_api_key():
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable")
        sys.exit(1)
    return api_key


def load_prompt(args):
    """Load prompt from file or command line args."""
    if args.file:
        prompt_path = Path(args.file)
        if not prompt_path.exists():
            print(f"Error: Prompt file not found: {args.file}")
            sys.exit(1)
        return prompt_path.read_text().strip()
    elif args.prompt:
        return " ".join(args.prompt)
    else:
        return "a cute cat"


def is_url(path):
    """Check if path is a URL."""
    parsed = urlparse(path)
    return parsed.scheme in ("http", "https")


def detect_mime_type(data, url_or_path, content_type=None):
    """Detect image mime type from content-type header, file extension, or image data."""
    extension_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".bmp": "image/bmp",
        ".tiff": "image/tiff",
        ".tif": "image/tiff",
    }

    # Try content-type header first (for URLs)
    if content_type:
        mime = content_type.split(";")[0].strip().lower()
        if mime.startswith("image/"):
            return mime

    # Try file extension
    parsed = urlparse(url_or_path)
    path = parsed.path if parsed.scheme else url_or_path
    suffix = Path(path).suffix.lower()
    if suffix in extension_map:
        return extension_map[suffix]

    # Fall back to PIL detection
    try:
        img = Image.open(BytesIO(data))
        format_map = {
            "JPEG": "image/jpeg",
            "PNG": "image/png",
            "GIF": "image/gif",
            "WEBP": "image/webp",
            "BMP": "image/bmp",
            "TIFF": "image/tiff",
        }
        if img.format in format_map:
            return format_map[img.format]
    except Exception:
        pass

    return "image/jpeg"  # Default fallback


def load_image_from_url(url):
    """Fetch image from URL and return as base64 with mime type."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "NanoBanana/1.0"}
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read()
            content_type = response.headers.get("Content-Type")
            mime_type = detect_mime_type(data, url, content_type)
            return base64.b64encode(data).decode("utf-8"), mime_type
    except urllib.error.URLError as e:
        print(f"Error: Failed to fetch image from URL: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def load_image_from_file(file_path):
    """Load image from local file and return as base64 with mime type."""
    path = Path(file_path)
    if not path.exists():
        print(f"Error: Image file not found: {file_path}")
        sys.exit(1)

    with open(path, "rb") as f:
        data = f.read()

    mime_type = detect_mime_type(data, file_path)
    return base64.b64encode(data).decode("utf-8"), mime_type


def load_image(image_source):
    """Load image from URL or local file and return as base64 with mime type."""
    if is_url(image_source):
        return load_image_from_url(image_source)
    else:
        return load_image_from_file(image_source)


def save_output(part, output_path):
    """Save image from response part."""
    data = part.inline_data.data
    if isinstance(data, str):
        data = base64.b64decode(data)

    image = Image.open(BytesIO(data))
    image.save(output_path)
    print(f"Saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Nano Banana Pro - AI Image Generation & Editing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate from prompt
  nb.py "a raccoon holding a sign that says hello"

  # Generate from prompt file
  nb.py -f prompt.txt

  # Edit an existing image (local file)
  nb.py -i photo.jpg "add sunglasses to the person"

  # Edit an image from URL
  nb.py -i "https://example.com/photo.jpg" "make it a watercolor painting"

  # Specify output file
  nb.py -o result.png "a beautiful sunset"

  # Use Nano Banana Flash (faster, cheaper)
  nb.py --flash "a cute cat"
"""
    )
    parser.add_argument("prompt", nargs="*", help="The prompt text")
    parser.add_argument("-f", "--file", help="Read prompt from file")
    parser.add_argument("-i", "--input", help="Input image for editing (local path or URL)")
    parser.add_argument("-o", "--output", default="output.png", help="Output file (default: output.png)")
    parser.add_argument("--flash", action="store_true", help="Use Nano Banana (2.5 Flash) instead of Pro")
    parser.add_argument("--list-models", action="store_true", help="List available image models")

    args = parser.parse_args()

    if args.list_models:
        client = genai.Client(api_key=get_api_key())
        print("Available image models:")
        for model in client.models.list():
            if "image" in model.name.lower() or "banana" in model.display_name.lower():
                print(f"  {model.name} - {model.display_name}")
        return

    prompt_text = load_prompt(args)
    print(f"Prompt: {prompt_text[:100]}{'...' if len(prompt_text) > 100 else ''}")

    contents = []
    if args.input:
        image_data, mime_type = load_image(args.input)
        print(f"Input image: {args.input}")
        contents.append(types.Part.from_bytes(
            data=base64.b64decode(image_data),
            mime_type=mime_type
        ))
    contents.append(prompt_text)

    pro_model = "gemini-3-pro-image-preview"
    flash_model = "gemini-2.5-flash-image"
    pro_timeout_ms = 45_000
    flash_timeout_ms = 60_000

    def generate_with_model(model_name, timeout_ms):
        client = genai.Client(
            api_key=get_api_key(),
            http_options=types.HttpOptions(timeout=timeout_ms)
        )
        return client.models.generate_content(
            model=model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"]
            )
        )

    response = None
    if args.flash:
        print(f"Model: {flash_model}")
        response = generate_with_model(flash_model, flash_timeout_ms)
    else:
        print(f"Model: {pro_model} (45s timeout, fallback: {flash_model})")
        try:
            response = generate_with_model(pro_model, pro_timeout_ms)
            print("Pro: success")
        except Exception as e:
            err_str = str(e).lower()
            if "timeout" in err_str or "deadline" in err_str or "timed out" in err_str:
                print(f"Pro: timeout, falling back to Flash...")
            else:
                print(f"Pro: {type(e).__name__}, falling back to Flash...")
            response = generate_with_model(flash_model, flash_timeout_ms)

    image_saved = False
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            save_output(part, args.output)
            image_saved = True
        elif hasattr(part, "text") and part.text:
            print(f"Response: {part.text}")

    if not image_saved:
        print("Warning: No image in response")


if __name__ == "__main__":
    main()
