#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable

PROPERTY_RE = re.compile(r'\(property\s+"((?:\\.|[^"\\])*)"\s+"((?:\\.|[^"\\])*)"', re.S)
AT_RE = re.compile(r'\(at\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)(?:\s+([-+0-9.eE]+))?\)')
LIB_ID_RE = re.compile(r'\(lib_id\s+"((?:\\.|[^"\\])*)"\)')


def _unescape(value: str) -> str:
    return value.replace(r'\"', '"').replace(r'\\', '\\')


def _paren_delta(text: str) -> int:
    delta = 0
    in_string = False
    escaped = False
    for ch in text:
        if in_string:
            if escaped:
                escaped = False
            elif ch == '\\':
                escaped = True
            elif ch == '"':
                in_string = False
        else:
            if ch == '"':
                in_string = True
            elif ch == '(':
                delta += 1
            elif ch == ')':
                delta -= 1
    return delta


def top_level_symbol_blocks(text: str) -> Iterable[str]:
    """Yield placed symbol blocks directly below the kicad_sch root.

    Library symbols inside lib_symbols are deeper and are intentionally ignored.
    """
    lines = text.splitlines(keepends=True)
    depth = 0
    collecting = False
    start_depth = None
    block: list[str] = []

    for line in lines:
        stripped = line.lstrip()
        if not collecting and depth == 1 and stripped.startswith('(symbol'):
            collecting = True
            start_depth = depth
            block = [line]
            depth += _paren_delta(line)
            if depth == start_depth:
                yield ''.join(block)
                collecting = False
                block = []
            continue

        if collecting:
            block.append(line)
            depth += _paren_delta(line)
            if depth == start_depth:
                yield ''.join(block)
                collecting = False
                block = []
            continue

        depth += _paren_delta(line)

    if collecting:
        raise ValueError('Unterminated top-level symbol block')
    if depth != 0:
        raise ValueError(f'Unbalanced S-expression, final depth {depth}')


@dataclass(frozen=True)
class Symbol:
    sheet: str
    reference: str
    value: str
    footprint: str
    fields: dict[str, str]
    lib_id: str
    x: str
    y: str
    rotation: str


def read_symbols(path: Path) -> list[Symbol]:
    text = path.read_text(encoding='utf-8')
    symbols: list[Symbol] = []
    for block in top_level_symbol_blocks(text):
        fields = {_unescape(k): _unescape(v) for k, v in PROPERTY_RE.findall(block)}
        reference = fields.get('Reference', '').strip()
        if not reference:
            continue
        at = AT_RE.search(block)
        lib_id = LIB_ID_RE.search(block)
        symbols.append(Symbol(
            sheet=path.name,
            reference=reference,
            value=fields.get('Value', '').strip(),
            footprint=fields.get('Footprint', '').strip(),
            fields=fields,
            lib_id=_unescape(lib_id.group(1)) if lib_id else '',
            x=at.group(1) if at else '',
            y=at.group(2) if at else '',
            rotation=(at.group(3) or '0') if at else '',
        ))
    return symbols


def discover_schematics(root: Path) -> list[Path]:
    return sorted(p for p in root.glob('*.kicad_sch') if p.is_file())


def is_power_symbol(ref: str) -> bool:
    return ref.startswith('#')


def is_dnp(fields: dict[str, str]) -> bool:
    value = fields.get('DNP', '').strip().lower()
    return value in {'1', 'yes', 'true', 'dnp', 'do not populate', 'not assembled'}
