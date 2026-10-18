#!/usr/bin/env python3
"""Create readable transcripts and lossless cue records without changing sources."""
import argparse
import glob
import html
import json
import os
from pathlib import Path
import re
import tempfile


TIME_PATTERN = r'(?:\d{2,}:)?[0-5]\d:[0-5]\d[.,]\d{3}'
TIMESTAMP_RE = re.compile(
    rf'(?P<start>{TIME_PATTERN})[ \t]+-->[ \t]+'
    rf'(?P<end>{TIME_PATTERN})(?:[ \t]+(?P<settings>.*))?'
)


def display_timestamp(raw_timestamp: str) -> str:
    """Format a VTT timestamp for human-readable transcript anchors."""
    if not re.fullmatch(TIME_PATTERN, raw_timestamp):
        raise ValueError(f'Invalid timestamp: {raw_timestamp}')
    parts = raw_timestamp.replace(',', '.').split('.')[0].split(':')
    if len(parts) == 3 and parts[0] == '00':
        parts = parts[1:]
    return ':'.join(parts)


def _milliseconds(timestamp):
    parts = timestamp.replace(',', '.').replace('.', ':').split(':')
    hours, minutes, seconds, milliseconds = map(int, ['0'] * (4 - len(parts)) + parts)
    return ((hours * 60 + minutes) * 60 + seconds) * 1000 + milliseconds


def parse_cues(content: str) -> list[dict]:
    """Preserve each cue's id, exact times, settings and unmodified payload.

    Payload includes original line endings. Metadata blocks are not cues;
    the original VTT remains the authoritative record of the entire document.
    """
    if not isinstance(content, str):
        raise TypeError('VTT content must be a string')
    blocks, block = [], []
    for line in content.removeprefix('\ufeff').splitlines(keepends=True):
        # A WebVTT separator is an empty line, not a payload line containing spaces.
        if not line.rstrip('\r\n'):
            if block:
                blocks.append(block)
                block = []
        else:
            block.append(line)
    if block:
        blocks.append(block)

    if not blocks or not re.fullmatch(r'WEBVTT(?:[ \t].*)?', blocks[0][0].rstrip('\r\n')):
        raise ValueError('Missing WEBVTT header')
    if any('-->' in line for line in blocks[0]):
        raise ValueError('WEBVTT header must be separated from cues by a blank line')

    cues = []
    for index, lines in enumerate(blocks[1:], start=2):
        first = lines[0].rstrip('\r\n')
        if re.match(r'^NOTE(?:[ \t]|$)', first) or first in ('STYLE', 'REGION'):
            continue
        timing_index = 0 if '-->' in first else 1
        timing = lines[timing_index].rstrip('\r\n') if len(lines) > timing_index else ''
        match = TIMESTAMP_RE.fullmatch(timing)
        if not match:
            raise ValueError(f'Invalid cue timing in block {index}: {timing or first!r}')
        if _milliseconds(match['end']) <= _milliseconds(match['start']):
            raise ValueError(f'Cue end must be after start in block {index}')
        cues.append({
            'id': first if timing_index else None,
            'start': match['start'],
            'end': match['end'],
            'settings': match['settings'] or '',
            'payload': ''.join(lines[timing_index + 1:]),
        })
    return cues


def _render_cues(cues, keep_timestamps):
    result = []
    for cue in cues:
        prefix = f"[{display_timestamp(cue['start'])}] " if keep_timestamps else ''
        for line in cue['payload'].splitlines():
            # Strip VTT markup before decoding entities, so &lt; is still speech.
            text = html.unescape(re.sub(r'<[^>]+>', '', line)).strip()
            if text:
                result.append(prefix + text)
    return '\n'.join(result)


def parse_vtt(content: str, keep_timestamps: bool = False) -> str:
    """Render every cue in order; never deduplicate independent utterances."""
    return _render_cues(parse_cues(content), keep_timestamps)


def _same_path(first, second):
    return first.resolve() == second.resolve() or (
        first.exists() and second.exists() and first.samefile(second)
    )


def _prepare_outputs(target, keep_timestamps, overwrite):
    target_path = Path(target)
    if target_path.is_dir():
        files = sorted(path for path in target_path.iterdir() if path.suffix.lower() == '.vtt')
    elif target_path.is_file():
        # yt-dlp commonly includes [video-id] in literal filenames.
        files = [target_path]
    else:
        files = sorted(map(Path, glob.glob(target)))
    if not files:
        raise ValueError(f'No VTT files found at: {target}')
    for path in files:
        if path.suffix.lower() != '.vtt' or not path.is_file():
            raise ValueError(f'Only .vtt input files are supported: {path}')

    outputs = []
    for path in files:
        try:
            # read_text() performs newline conversion; evidence must retain CRLF.
            cues = parse_cues(path.read_bytes().decode('utf-8'))
        except (UnicodeError, ValueError) as error:
            raise ValueError(f'{path}: {error}') from error
        suffix = '_timestamped.txt' if keep_timestamps else '_parsed.txt'
        outputs.extend([
            (path.with_name(path.stem + suffix), _render_cues(cues, keep_timestamps)),
            (path.with_name(path.stem + '_cues.json'), json.dumps(cues, ensure_ascii=False, indent=2) + '\n'),
        ])

    # Validate the entire batch before creating or replacing any target.
    for index, (output, _) in enumerate(outputs):
        if any(_same_path(output, source) for source in files):
            raise ValueError(f'Output aliases an input file: {output}')
        if any(_same_path(output, other) for other, _ in outputs[:index]):
            raise ValueError(f'Output paths collide: {output}')
        if output.is_dir():
            raise ValueError(f'Output is a directory: {output}')
        if os.path.lexists(output) and not overwrite:
            raise ValueError(f'Output already exists: {output}; use --overwrite to replace it')
    return outputs


def _write_outputs(outputs, overwrite):
    staged = []
    try:
        for output, content in outputs:
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='',
                                             dir=output.parent, delete=False) as stream:
                staged.append((Path(stream.name), output, len(content)))
                stream.write(content)
        for temporary, output, length in staged:
            if overwrite:
                os.replace(temporary, output)
            else:
                # Exclusive creation also protects an output created after preflight.
                os.link(temporary, output)
                temporary.unlink()
            print(f'Saved: {output} ({length} chars)')
    finally:
        for temporary, _, _ in staged:
            temporary.unlink(missing_ok=True)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='Create plain text transcripts and lossless *_cues.json records from VTT.',
    )
    parser.add_argument('target', help='Directory, VTT file, or glob pattern')
    parser.add_argument(
        '--keep-timestamps',
        action='store_true',
        help='Prefix each caption line with its VTT start timestamp',
    )
    parser.add_argument('--overwrite', action='store_true', help='Replace existing generated outputs')
    args = parser.parse_args(argv)
    try:
        outputs = _prepare_outputs(args.target, args.keep_timestamps, args.overwrite)
        _write_outputs(outputs, args.overwrite)
    except (OSError, ValueError) as error:
        parser.exit(1, f'Error: {error}\n')


if __name__ == '__main__':
    main()
