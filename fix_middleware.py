#!/usr/bin/env python3
"""
Patch script to fix the middleware.py bug where JSONResponse is not handled properly
"""
import re

middleware_file = "/app/backend/open_webui/utils/middleware.py"

# Read the file
with open(middleware_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the problematic code
old_code = '''            res = await generate_image_prompt(
                request,
                {
                    "model": form_data["model"],
                    "messages": messages,
                },
                user,
            )

            response = res["choices"][0]["message"]["content"]'''

new_code = '''            res = await generate_image_prompt(
                request,
                {
                    "model": form_data["model"],
                    "messages": messages,
                },
                user,
            )

            # Handle JSONResponse errors from generate_image_prompt
            if isinstance(res, JSONResponse):
                return res

            response = res["choices"][0]["message"]["content"]'''

# Replace the code
if old_code in content:
    content = content.replace(old_code, new_code)
    print("✓ Patch applied successfully")

    # Write back
    with open(middleware_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✓ File saved")
else:
    print("✗ Pattern not found - maybe already patched or code has changed")
