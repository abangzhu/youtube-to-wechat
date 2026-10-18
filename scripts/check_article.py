#!/usr/bin/env python3
"""Read-only article checks. Findings are not a judgment of factual accuracy.

This lightweight Markdown scanner protects fences, indented code, block quotes,
headings, inline code, direct quotations and URLs. It is not a complete parser.
"""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

FENCE = re.compile(r'^ {0,3}(`{3,}|~{3,})(.*)$')
HEADING = re.compile(r'^ {0,3}#{1,6}\s+')
INLINE_CODE = re.compile(r'(`+)(?!`)((?:(?!\n[ \t]*\n).)*?)(?<!`)\1(?!`)', re.DOTALL)
QUOTATION = re.compile(r'“[^”]*”|「[^」]*」|『[^』]*』|"[^"\n]*"')
URL = re.compile(r'(?:https?://|mailto:)\S+')
IMAGE_START = re.compile(r'!\[(?:\\.|[^\]\n])*\]\(\s*')
PLACEHOLDER = re.compile(r'\[图\s*[:：]|\[TODO\s*[:：]|<TODO>')
STYLE = re.compile(r'值得注意的是|综上所述|让我们看看|深入探讨')


def mask(text):
    return re.sub(r'[^\n]', ' ', text)


def protected_text(lines):
    """Mask protected regions in source order, preserving diagnostic lines.

    A comment cannot start inside code, nor can a fence start in a comment.
    Inline code may cross a line break, but not an empty paragraph boundary.
    """
    text = '\n'.join(lines)
    result = []
    pos = 0
    unclosed_fence = None

    def line_end(start):
        newline = text.find('\n', start)
        return len(text) if newline < 0 else newline + 1

    while pos < len(text):
        end = None
        if pos == 0 or text[pos - 1] == '\n':
            next_line = line_end(pos)
            line = text[pos:next_line].rstrip('\n')
            marker = FENCE.match(line)
            if line.startswith(('    ', '\t')) or line.lstrip().startswith('>'):
                end = next_line
            elif marker:
                end = next_line
                closed = False
                while end < len(text):
                    next_end = line_end(end)
                    closing = FENCE.match(text[end:next_end].rstrip('\n'))
                    end = next_end
                    if closing and closing[1][0] == marker[1][0] and len(closing[1]) >= len(marker[1]) and not closing[2].strip():
                        closed = True
                        break
                if not closed:
                    unclosed_fence = text.count('\n', 0, pos) + 1
        if end is None and text.startswith('<!--', pos):
            closing = text.find('-->', pos + 4)
            end = len(text) if closing < 0 else closing + 3
        if end is None and text[pos] == '`':
            span = INLINE_CODE.match(text, pos)
            if span:
                end = span.end()
            else:
                # An unmatched run is literal; do not retry from its suffix.
                run = re.match(r'`+', text[pos:])[0]
                result.append(run)
                pos += len(run)
                continue
        if end is not None:
            result.append(mask(text[pos:end]))
            pos = end
        else:
            result.append(text[pos])
            pos += 1
    return ''.join(result).split('\n'), unclosed_fence


def images(line):
    """Yield inline image destinations, with balanced/escaped parentheses.

    Unsupported syntax is left for semantic review, never truncated into a
    false missing-file error. Reference-style images require separate review.
    """
    for match in IMAGE_START.finditer(line):
        pos = match.end()
        start = pos
        depth = 0
        angle = pos < len(line) and line[pos] == '<'
        if angle:
            pos += 1
            start = pos
        while pos < len(line):
            char = line[pos]
            if char == '\\' and pos + 1 < len(line):
                pos += 2
                continue
            if angle:
                if char == '>':
                    break
            elif char == '(':
                depth += 1
            elif char == ')':
                if depth == 0:
                    break
                depth -= 1
            elif char.isspace() and depth == 0:
                break
            pos += 1
        if pos >= len(line) or depth:
            continue
        destination = line[start:pos]
        tail_start = pos + 1 if angle else pos
        tail = re.match(r"\s*(?:[\"'][^\n]*?[\"']\s*)?\)", line[tail_start:])
        if not tail or not destination:
            continue
        destination = re.sub(r'\\([\\`*{}\[\]()#+\-.!_<> ])', r'\1', destination)
        yield match.start(), tail_start + tail.end(), destination


def narrative_text(line):
    """Mask protected inline contents without modifying the source."""
    for start, end, _ in reversed(list(images(line))):
        line = line[:start] + mask(line[start:end]) + line[end:]
    line = re.sub(r'\]\([^\n]*?\)', ']', line)
    line = URL.sub('', line)
    return QUOTATION.sub('', line)


def check_article(path, stage='draft'):
    """Return serializable error/warning records; never write to path."""
    if stage not in {'draft', 'awaiting-title', 'ready'}:
        raise ValueError('Unknown delivery stage')
    path = Path(path)
    lines = path.read_text(encoding='utf-8-sig').splitlines()
    findings = []
    delivery_severity = 'warning' if stage == 'draft' else 'error'

    def add(severity, code, line, message):
        findings.append({'severity': severity, 'code': code, 'line': line, 'message': message})

    first = next(((n, line) for n, line in enumerate(lines, 1) if line.strip()), (1, ''))
    if stage == 'ready' and not re.match(r'^ {0,3}#\s+\S', first[1]):
        add('error', 'missing_title', first[0], 'ready 阶段需要首个非空行为已确认的 H1 标题。')

    masked_lines, unclosed_fence = protected_text(lines)
    source_found = False
    for number, line in enumerate(masked_lines, 1):
        for _, _, destination in images(QUOTATION.sub('', line)):
            uri = urlsplit(destination)
            if uri.scheme or uri.netloc:
                continue  # No network fetches; remote availability needs separate verification.
            local = Path(unquote(uri.path))
            if not local.is_absolute():
                local = path.parent / local
            if not local.is_file():
                add(delivery_severity, 'missing_image', number, f'本地图片不存在：{destination}')
        prose = narrative_text(line)
        if re.match(r'^\s*内容来源\s*[,，:：]', prose):
            source_found = True
        if PLACEHOLDER.search(prose):
            add(delivery_severity, 'placeholder', number, '仍有未完成的图片或 TODO 占位。')
        if HEADING.match(line):
            continue
        for match in STYLE.finditer(prose):
            add('warning', 'style_candidate', number, f'检查“{match[0]}”是否提供信息；有意义时可以保留。')
    if unclosed_fence:
        add('error', 'unclosed_fence', unclosed_fence, '代码围栏未闭合。')
    if not source_found and stage != 'draft':
        add('error', 'missing_source', len(lines) or 1, '缺少正文中的“内容来源”注记。')
    return findings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('article', type=Path)
    parser.add_argument('--stage', choices=['draft', 'awaiting-title', 'ready'], default='draft')
    parser.add_argument('--format', choices=['text', 'json'], default='text')
    args = parser.parse_args(argv)
    try:
        findings = check_article(args.article, args.stage)
    except (OSError, UnicodeError, ValueError) as exc:
        parser.error(str(exc))
    errors = sum(item['severity'] == 'error' for item in findings)
    warnings = sum(item['severity'] == 'warning' for item in findings)
    if args.format == 'json':
        print(json.dumps({'stage': args.stage, 'errors': errors, 'warnings': warnings, 'findings': findings}, ensure_ascii=False, indent=2))
    else:
        for item in findings:
            print(f"{item['severity']} {args.article}:{item['line']} [{item['code']}] {item['message']}")
        print(f'{errors} error(s), {warnings} candidate(s); source file unchanged.')
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
