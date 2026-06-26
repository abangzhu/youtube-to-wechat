#!/usr/bin/env python3
"""Parse VTT subtitle files for article source drafts."""
import argparse
import re
import os
import glob


TIMESTAMP_RE = re.compile(
    r'(?P<start>\d{2}:\d{2}:\d{2}[.,]\d{3})\s*-->\s*'
    r'(?P<end>\d{2}:\d{2}:\d{2}[.,]\d{3})'
)


def display_timestamp(raw_timestamp: str) -> str:
    """Format a VTT timestamp for human-readable transcript anchors."""
    h, m, rest = raw_timestamp.replace(',', '.').split(':')
    s = rest.split('.')[0]
    if h == '00':
        return f'{m}:{s}'
    return f'{h}:{m}:{s}'


def parse_vtt(content: str, keep_timestamps: bool = False) -> str:
    result = []
    prev = None
    current_timestamp = None
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            current_timestamp = None
            continue
        if line.startswith(('WEBVTT', 'Kind:', 'Language:', 'NOTE')):
            continue

        timestamp_match = TIMESTAMP_RE.match(line)
        if timestamp_match:
            current_timestamp = display_timestamp(timestamp_match.group('start'))
            continue
        if re.match(r'^\d+$', line):
            continue

        line = re.sub(r'<[^>]+>', '', line).strip()
        if not line or line == prev:
            continue

        if keep_timestamps and current_timestamp:
            result.append(f'[{current_timestamp}] {line}')
        else:
            result.append(line)
        prev = line
    return '\n'.join(result)


def main():
    parser = argparse.ArgumentParser(
        description='Parse VTT subtitle files into plain text transcript drafts.',
    )
    parser.add_argument('target', help='Directory, VTT file, or glob pattern')
    parser.add_argument(
        '--keep-timestamps',
        action='store_true',
        help='Prefix each caption line with its VTT start timestamp',
    )
    args = parser.parse_args()

    target = args.target
    if os.path.isdir(target):
        files = glob.glob(os.path.join(target, '*.vtt'))
    else:
        files = glob.glob(target)

    if not files:
        print(f"No VTT files found at: {target}")
        raise SystemExit(1)

    for vtt_path in files:
        with open(vtt_path, encoding='utf-8') as f:
            content = f.read()
        parsed = parse_vtt(content, keep_timestamps=args.keep_timestamps)
        suffix = '_timestamped.txt' if args.keep_timestamps else '_parsed.txt'
        out_path = re.sub(r'\.vtt$', suffix, vtt_path)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(parsed)
        print(f"Saved: {out_path} ({len(parsed)} chars)")


if __name__ == '__main__':
    main()
