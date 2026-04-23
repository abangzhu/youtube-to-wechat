#!/usr/bin/env python3
"""Parse VTT subtitle files: strip timestamps, HTML tags, and deduplicate lines."""
import re
import sys
import os
import glob


def parse_vtt(content: str) -> str:
    result = []
    prev = None
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.startswith(('WEBVTT', 'Kind:', 'Language:', 'NOTE')):
            continue
        if re.match(r'\d{2}:\d{2}:\d{2}[.,]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[.,]\d{3}', line):
            continue
        if re.match(r'^\d+$', line):
            continue
        line = re.sub(r'<[^>]+>', '', line).strip()
        if line and line != prev:
            result.append(line)
            prev = line
    return '\n'.join(result)


def main():
    if len(sys.argv) < 2:
        print("Usage: python parse_vtt.py <directory_or_vtt_file>")
        sys.exit(1)

    target = sys.argv[1]
    if os.path.isdir(target):
        files = glob.glob(os.path.join(target, '*.vtt'))
    else:
        files = glob.glob(target)

    if not files:
        print(f"No VTT files found at: {target}")
        sys.exit(1)

    for vtt_path in files:
        with open(vtt_path, encoding='utf-8') as f:
            content = f.read()
        parsed = parse_vtt(content)
        out_path = re.sub(r'\.vtt$', '_parsed.txt', vtt_path)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(parsed)
        print(f"Saved: {out_path} ({len(parsed)} chars)")


if __name__ == '__main__':
    main()
