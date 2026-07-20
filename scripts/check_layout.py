#!/usr/bin/env python3
"""Render exact viewports and fail on readability, SVG, focus, or overflow defects."""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from pathlib import Path


DEFAULT_VIEWPORTS = [(1440, 900), (768, 1024), (375, 812)]
BROWSER_CANDIDATES = [
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
    Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
]

AUDIT_EXPRESSION = r"""
(() => {
  const errors = [];
  const warnings = [];
  const unique = values => [...new Set(values)];
  const width = window.innerWidth;
  const root = document.documentElement;
  const round = value => Math.round(value * 10) / 10;
  const label = el => {
    const id = el.id ? `#${el.id}` : '';
    const cls = typeof el.className === 'string' && el.className.trim()
      ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : '';
    return `${el.tagName.toLowerCase()}${id}${cls}`;
  };
  const visible = (el, style, rect) =>
    style.display !== 'none' && style.visibility !== 'hidden' &&
    Number(style.opacity) !== 0 && rect.width > 0 && rect.height > 0;
  const directText = el => Array.from(el.childNodes)
    .some(node => node.nodeType === Node.TEXT_NODE && node.textContent.trim());

  if (root.scrollWidth > width + 2) {
    errors.push(`horizontal overflow: document is ${root.scrollWidth}px at ${width}px viewport`);
  }

  document.querySelectorAll('body *').forEach(el => {
    if (['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE'].includes(el.tagName)) return;
    const style = getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    if (!visible(el, style, rect)) return;
    const hasText = directText(el);
    if (hasText) {
      const fontSize = parseFloat(style.fontSize);
      if (fontSize < 14 - 0.05) {
        errors.push(`small text: ${label(el)} is ${round(fontSize)}px`);
      }
      const headingMinimum = {H1: 32, H2: 24, H3: 18, H4: 16}[el.tagName];
      if (headingMinimum && fontSize < headingMinimum - 0.05) {
        errors.push(`heading below minimum: ${label(el)} is ${round(fontSize)}px; minimum is ${headingMinimum}px`);
      }
      const secondary = el.matches('.meta, .tag, .eyebrow, .why, nav a, small');
      const bodyText = ['P','LI','TD','TH','BLOCKQUOTE','FIGCAPTION','DD','DT'].includes(el.tagName);
      if (!secondary && bodyText && fontSize < 16 - 0.05) {
        errors.push(`body text below 16px: ${label(el)} is ${round(fontSize)}px`);
      }
      const lineHeight = parseFloat(style.lineHeight);
      if (bodyText && Number.isFinite(lineHeight) && lineHeight / fontSize < 1.5 - 0.01) {
        errors.push(`line-height below minimum: ${label(el)} is ${round(lineHeight / fontSize)}; minimum is 1.5`);
      }
      const clipsX = ['hidden', 'clip'].includes(style.overflowX) && el.scrollWidth > el.clientWidth + 1;
      const clipsY = ['hidden', 'clip'].includes(style.overflowY) && el.scrollHeight > el.clientHeight + 1;
      if ((clipsX || clipsY) && !el.closest('[data-visual-only]')) {
        errors.push(`text clipping: ${label(el)} scroll=${el.scrollWidth}x${el.scrollHeight} client=${el.clientWidth}x${el.clientHeight}`);
      }
      if (!el.closest('[data-visual-only], .visual-only, .visually-hidden, .sr-only')) {
        const range = document.createRange();
        range.selectNodeContents(el);
        const textRects = Array.from(range.getClientRects()).filter(item => item.width > 0 && item.height > 0);
        let ancestor = el.parentElement;
        while (ancestor && ancestor !== document.body) {
          const ancestorStyle = getComputedStyle(ancestor);
          const ancestorRect = ancestor.getBoundingClientRect();
          const clipsAncestorX = ['hidden', 'clip'].includes(ancestorStyle.overflowX) && textRects.some(item =>
            item.left < ancestorRect.left - 1 || item.right > ancestorRect.right + 1
          );
          const clipsAncestorY = ['hidden', 'clip'].includes(ancestorStyle.overflowY) && textRects.some(item =>
            item.top < ancestorRect.top - 1 || item.bottom > ancestorRect.bottom + 1
          );
          if (clipsAncestorX || clipsAncestorY) {
            errors.push(`text clipped by ancestor ${label(ancestor)}: ${label(el)}`);
            break;
          }
          ancestor = ancestor.parentElement;
        }
      }
    }
    if (!el.closest('[data-overflow-ok]') && (rect.left < -2 || rect.right > width + 2)) {
      errors.push(`horizontal overflow: ${label(el)} spans ${round(rect.left)}..${round(rect.right)} at ${width}px viewport`);
    }
  });

  const allVisualRoots = Array.from(document.querySelectorAll('[data-viz]'));
  const visibleVisualRoots = allVisualRoots.filter(el => {
    const style = getComputedStyle(el);
    return visible(el, style, el.getBoundingClientRect());
  });
  if (visibleVisualRoots.length < 2 || visibleVisualRoots.length > 5) {
    errors.push(`expected 2–5 visible major visuals, found ${visibleVisualRoots.length}`);
  }
  if (visibleVisualRoots.length !== allVisualRoots.length) {
    errors.push(`hidden data-viz roots do not count as major visuals`);
  }

  document.querySelectorAll('[data-viz-label]').forEach(el => {
    const style = getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    if (!visible(el, style, rect)) return;
    const text = el.textContent.trim().replace(/\s+/g, ' ');
    const fontSize = parseFloat(style.fontSize);
    if (fontSize < 16 - 0.05) {
      errors.push(`semantic label below 16px: "${text}" is ${round(fontSize)}px`);
    }
    const range = document.createRange();
    range.selectNodeContents(el);
    const lineTops = unique(Array.from(range.getClientRects())
      .filter(item => item.width > 0 && item.height > 0)
      .map(item => Math.round(item.top * 2) / 2));
    if (lineTops.length > 1) {
      errors.push(`semantic label wraps: "${text}"; use fewer columns, full-width, or vertical layout`);
    }
    const parentRect = el.parentElement ? el.parentElement.getBoundingClientRect() : rect;
    const overflowsBox = el.scrollWidth > el.clientWidth + 1 || el.scrollHeight > el.clientHeight + 1;
    const overflowsParent = rect.left < parentRect.left - 1 || rect.right > parentRect.right + 1;
    if (overflowsBox || overflowsParent) {
      errors.push(`semantic label overflow: "${text}"; widen the node or reduce columns without shrinking text`);
    }
  });

  document.querySelectorAll('[data-viz-renderer="svg"]').forEach(rootEl => {
    const svgs = rootEl.querySelectorAll('svg');
    if (svgs.length !== 1) {
      errors.push(`SVG renderer must contain exactly one svg: ${label(rootEl)}`);
      return;
    }
    const svg = svgs[0];
    const svgRect = svg.getBoundingClientRect();
    const rootRect = rootEl.getBoundingClientRect();
    const viewBox = svg.viewBox && svg.viewBox.baseVal;
    if (!svg.hasAttribute('viewBox') || !viewBox || viewBox.width <= 0 || viewBox.height <= 0) {
      errors.push(`SVG needs a non-empty viewBox: ${label(rootEl)}`);
    }
    if (svg.getAttribute('role') !== 'img') {
      errors.push(`SVG needs role="img": ${label(rootEl)}`);
    }
    const hasTitle = Boolean(svg.querySelector('title')?.textContent.trim());
    const hasDesc = Boolean(svg.querySelector('desc')?.textContent.trim());
    const refsResolve = value => Boolean(value) && value.trim().split(/\s+/).every(id => {
      const target = document.getElementById(id);
      return target && target.textContent.trim();
    });
    const equivalentName = refsResolve(svg.getAttribute('aria-labelledby'));
    const equivalentDesc = refsResolve(svg.getAttribute('aria-describedby'));
    if (!((hasTitle && hasDesc) || (equivalentName && equivalentDesc))) {
      errors.push(`SVG needs title/desc or equivalent ARIA associations: ${label(rootEl)}`);
    }
    if (svgRect.left < rootRect.left - 1 || svgRect.right > rootRect.right + 1) {
      errors.push(`SVG overflows its visual root: ${label(rootEl)} spans ${round(svgRect.left)}..${round(svgRect.right)}`);
    }
    svg.querySelectorAll('text:not([aria-hidden="true"])').forEach(textEl => {
      const text = textEl.textContent.trim().replace(/\s+/g, ' ');
      if (!textEl.hasAttribute('data-viz-label')) {
        errors.push(`informative SVG text lacks data-viz-label: "${text}"`);
      }
      const textRect = textEl.getBoundingClientRect();
      if (textRect.left < svgRect.left - 1 || textRect.right > svgRect.right + 1 ||
          textRect.top < svgRect.top - 1 || textRect.bottom > svgRect.bottom + 1) {
        errors.push(`SVG label outside viewBox: "${text}"`);
      }
      let ancestor = textEl.parentElement;
      while (ancestor && ancestor !== rootEl) {
        const ancestorStyle = getComputedStyle(ancestor);
        const ancestorRect = ancestor.getBoundingClientRect();
        const clipsX = ['hidden', 'clip'].includes(ancestorStyle.overflowX) &&
          (textRect.left < ancestorRect.left - 1 || textRect.right > ancestorRect.right + 1);
        const clipsY = ['hidden', 'clip'].includes(ancestorStyle.overflowY) &&
          (textRect.top < ancestorRect.top - 1 || textRect.bottom > ancestorRect.bottom + 1);
        if (clipsX || clipsY) {
          errors.push(`SVG label clipped by ${label(ancestor)}: "${text}"`);
          break;
        }
        ancestor = ancestor.parentElement;
      }
    });
  });

  document.querySelectorAll('[data-viz-renderer="source-image"]').forEach(rootEl => {
    const images = rootEl.querySelectorAll('img');
    if (images.length !== 1) {
      errors.push(`source-image renderer must contain exactly one img: ${label(rootEl)}`);
      return;
    }
    const img = images[0];
    if (!img.complete || img.naturalWidth <= 0 || img.naturalHeight <= 0) {
      errors.push(`source image failed to decode: ${label(rootEl)}`);
    }
    const hasIntrinsic = Boolean(img.getAttribute('width') && img.getAttribute('height'));
    const ratioNode = img.closest('[data-aspect-ratio]');
    const computedRatio = ratioNode ? getComputedStyle(ratioNode).aspectRatio : getComputedStyle(img).aspectRatio;
    if (!hasIntrinsic && (!computedRatio || computedRatio === 'auto')) {
      errors.push(`source image lacks intrinsic dimensions or a computed aspect ratio: ${label(rootEl)}`);
    }
  });

  if (width <= 375) {
    document.querySelectorAll('[data-deep-layout]').forEach(el => {
      const style = getComputedStyle(el);
      const tracks = style.gridTemplateColumns.trim().split(/\s+/).filter(Boolean);
      if (style.display === 'grid' && tracks.length > 1) {
        errors.push(`mobile deep layout must be single column: ${label(el)} has ${tracks.length} columns`);
      }
    });
    document.querySelectorAll('[data-deep-chapter]').forEach(chapter => {
      const visual = chapter.querySelector('[data-viz]');
      const explanation = chapter.querySelector('[data-role="explanation"]');
      if (visual && explanation && !(visual.compareDocumentPosition(explanation) & Node.DOCUMENT_POSITION_FOLLOWING)) {
        errors.push(`mobile deep reading order must place the visual before explanation: ${label(chapter)}`);
      }
    });
  }

  return {
    viewport: {width, height: window.innerHeight},
    errors: unique(errors),
    warnings: unique(warnings)
  };
})()
"""

FOCUS_COUNT_EXPRESSION = r"""
(() => {
  if (document.activeElement && document.activeElement !== document.body) document.activeElement.blur();
  const selector = 'a[href], button, input, select, textarea, summary, [tabindex]:not([tabindex="-1"])';
  const focusables = Array.from(document.querySelectorAll(selector)).filter(el => {
    const style = getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    return !el.hasAttribute('disabled') && style.display !== 'none' &&
      style.visibility !== 'hidden' && Number(style.opacity) !== 0 && rect.width > 0 && rect.height > 0;
  });
  return {
    count: focusables.length,
    positiveTabindex: focusables.filter(el => Number(el.getAttribute('tabindex')) > 0).map(el => el.outerHTML.slice(0, 120))
  };
})()
"""

FOCUS_STATE_EXPRESSION = r"""
(() => {
  const el = document.activeElement;
  if (!el || el === document.body || el === document.documentElement) return {active: false};
  const style = getComputedStyle(el);
  const outlineWidth = parseFloat(style.outlineWidth) || 0;
  const outlineVisible = style.outlineStyle !== 'none' && outlineWidth >= 2 &&
    style.outlineColor !== 'rgba(0, 0, 0, 0)' && style.outlineColor !== 'transparent';
  const shadowVisible = Boolean(style.boxShadow && style.boxShadow !== 'none');
  const id = el.id ? `#${el.id}` : '';
  const cls = typeof el.className === 'string' && el.className.trim()
    ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : '';
  const name = `${el.tagName.toLowerCase()}${id}${cls}`;
  const selector = 'a[href], button, input, select, textarea, summary, [tabindex]:not([tabindex="-1"])';
  const domIndex = Array.from(document.querySelectorAll(selector)).indexOf(el);
  return {
    active: true,
    name,
    fingerprint: `${domIndex}|${name}|${el.getAttribute('href') || ''}|${el.textContent.trim().slice(0, 80)}`,
    focusVisible: el.matches(':focus-visible'),
    indicatorVisible: outlineVisible || shadowVisible
  };
})()
"""


class _WebSocket:
    """Minimal RFC 6455 client sufficient for local Chrome DevTools traffic."""

    def __init__(self, url: str, timeout: float = 10.0) -> None:
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme != "ws" or not parsed.hostname or not parsed.port:
            raise ValueError(f"unsupported DevTools WebSocket URL: {url}")
        self.socket = socket.create_connection((parsed.hostname, parsed.port), timeout=timeout)
        self.socket.settimeout(timeout)
        self.buffer = bytearray()
        key = base64.b64encode(os.urandom(16)).decode("ascii")
        target = urllib.parse.urlunsplit(("", "", parsed.path, parsed.query, ""))
        request = (
            f"GET {target} HTTP/1.1\r\n"
            f"Host: {parsed.hostname}:{parsed.port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        )
        self.socket.sendall(request.encode("ascii"))
        response = self._read_until(b"\r\n\r\n")
        status = response.split(b"\r\n", 1)[0]
        if b" 101 " not in status:
            self.close()
            raise RuntimeError(f"DevTools WebSocket handshake failed: {status.decode('ascii', 'replace')}")

    def _read_until(self, marker: bytes) -> bytes:
        while marker not in self.buffer:
            chunk = self.socket.recv(65536)
            if not chunk:
                raise RuntimeError("DevTools WebSocket closed during handshake")
            self.buffer.extend(chunk)
        end = self.buffer.index(marker) + len(marker)
        result = bytes(self.buffer[:end])
        del self.buffer[:end]
        return result

    def _read_exact(self, size: int) -> bytes:
        while len(self.buffer) < size:
            chunk = self.socket.recv(65536)
            if not chunk:
                raise RuntimeError("DevTools WebSocket closed unexpectedly")
            self.buffer.extend(chunk)
        result = bytes(self.buffer[:size])
        del self.buffer[:size]
        return result

    def _send_frame(self, opcode: int, payload: bytes) -> None:
        mask = os.urandom(4)
        length = len(payload)
        if length <= 125:
            header = bytes((0x80 | opcode, 0x80 | length))
        elif length <= 65535:
            header = bytes((0x80 | opcode, 0x80 | 126)) + struct.pack("!H", length)
        else:
            header = bytes((0x80 | opcode, 0x80 | 127)) + struct.pack("!Q", length)
        masked = bytes(value ^ mask[index % 4] for index, value in enumerate(payload))
        self.socket.sendall(header + mask + masked)

    def send_text(self, text: str) -> None:
        self._send_frame(0x1, text.encode("utf-8"))

    def receive_text(self) -> str:
        fragments = bytearray()
        while True:
            first, second = self._read_exact(2)
            final = bool(first & 0x80)
            opcode = first & 0x0F
            masked = bool(second & 0x80)
            length = second & 0x7F
            if length == 126:
                length = struct.unpack("!H", self._read_exact(2))[0]
            elif length == 127:
                length = struct.unpack("!Q", self._read_exact(8))[0]
            mask = self._read_exact(4) if masked else b""
            payload = self._read_exact(length)
            if masked:
                payload = bytes(value ^ mask[index % 4] for index, value in enumerate(payload))
            if opcode == 0x8:
                raise RuntimeError("DevTools WebSocket closed")
            if opcode == 0x9:
                self._send_frame(0xA, payload)
                continue
            if opcode in {0x1, 0x0}:
                fragments.extend(payload)
                if final:
                    return fragments.decode("utf-8")

    def close(self) -> None:
        try:
            self._send_frame(0x8, b"")
        except OSError:
            pass
        finally:
            self.socket.close()


class _CDP:
    def __init__(self, websocket_url: str) -> None:
        self.websocket = _WebSocket(websocket_url)
        self.next_id = 1

    def call(self, method: str, params: dict | None = None) -> dict:
        request_id = self.next_id
        self.next_id += 1
        self.websocket.send_text(json.dumps({"id": request_id, "method": method, "params": params or {}}))
        while True:
            message = json.loads(self.websocket.receive_text())
            if message.get("id") != request_id:
                continue
            if "error" in message:
                raise RuntimeError(f"DevTools {method} failed: {message['error']}")
            return message.get("result", {})

    def close(self) -> None:
        self.websocket.close()


def find_browser() -> Path | None:
    """Return an installed Chromium-family browser, preferring Chrome."""
    for command in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge", "msedge"):
        found = shutil.which(command)
        if found:
            return Path(found)
    for candidate in BROWSER_CANDIDATES:
        if candidate.is_file():
            return candidate
    return None


def _debug_target(port: int, timeout: float = 10.0) -> str:
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=1) as response:
                targets = json.load(response)
            page = next(item for item in targets if item.get("type") == "page")
            return page["webSocketDebuggerUrl"]
        except (OSError, StopIteration, KeyError, json.JSONDecodeError) as exc:
            last_error = exc
            time.sleep(0.05)
    raise RuntimeError(f"Chrome DevTools target unavailable: {last_error}")


def _run_viewport(browser: Path, path: Path, viewport: tuple[int, int]) -> dict:
    width, height = viewport
    # Chromium child processes can briefly retain Windows cache handles after the
    # parent exits. Ignore cleanup-only lock races; the OS temp directory remains
    # the owner and the rendered audit result is unaffected.
    with tempfile.TemporaryDirectory(prefix="article-layout-", ignore_cleanup_errors=True) as folder:
        profile = Path(folder) / "profile"
        command = [
            str(browser),
            "--headless=new",
            "--disable-gpu",
            "--disable-background-networking",
            "--no-first-run",
            "--no-default-browser-check",
            "--allow-file-access-from-files",
            "--remote-allow-origins=*",
            "--remote-debugging-port=0",
            f"--user-data-dir={profile}",
            "about:blank",
        ]
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        process = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags,
        )
        cdp: _CDP | None = None
        try:
            active_port = profile / "DevToolsActivePort"
            deadline = time.monotonic() + 10
            port: int | None = None
            while port is None and time.monotonic() < deadline:
                if process.poll() is not None:
                    raise RuntimeError(f"browser exited before DevTools started: {process.returncode}")
                try:
                    lines = active_port.read_text(encoding="utf-8").splitlines()
                    if lines:
                        port = int(lines[0])
                        break
                except (FileNotFoundError, PermissionError, OSError, ValueError):
                    pass
                time.sleep(0.05)
            if port is None:
                raise RuntimeError("browser did not publish a readable DevToolsActivePort")
            cdp = _CDP(_debug_target(port))
            cdp.call("Page.enable")
            cdp.call("Runtime.enable")
            cdp.call(
                "Emulation.setDeviceMetricsOverride",
                {
                    "width": width,
                    "height": height,
                    "deviceScaleFactor": 1,
                    "mobile": False,
                    "screenWidth": width,
                    "screenHeight": height,
                },
            )
            cdp.call("Page.navigate", {"url": path.resolve().as_uri()})
            ready_deadline = time.monotonic() + 10
            while time.monotonic() < ready_deadline:
                ready = cdp.call(
                    "Runtime.evaluate",
                    {"expression": "document.readyState", "returnByValue": True},
                )
                if ready.get("result", {}).get("value") == "complete":
                    break
                time.sleep(0.05)
            else:
                raise RuntimeError("document did not finish loading")

            focus_count_eval = cdp.call(
                "Runtime.evaluate",
                {"expression": FOCUS_COUNT_EXPRESSION, "returnByValue": True, "awaitPromise": True},
            )
            focus_count_payload = focus_count_eval.get("result", {}).get("value")
            if not isinstance(focus_count_payload, dict):
                raise RuntimeError("focus probe returned no structured count")
            focus_errors: list[str] = []
            if focus_count_payload.get("positiveTabindex"):
                focus_errors.append("positive tabindex disrupts keyboard order")
            focus_count = int(focus_count_payload.get("count", 0))
            focus_seen: list[str] = []
            for _ in range(focus_count):
                key_params = {
                    "key": "Tab",
                    "code": "Tab",
                    "windowsVirtualKeyCode": 9,
                    "nativeVirtualKeyCode": 9,
                }
                cdp.call("Input.dispatchKeyEvent", {"type": "keyDown", **key_params})
                cdp.call("Input.dispatchKeyEvent", {"type": "keyUp", **key_params})
                focus_eval = cdp.call(
                    "Runtime.evaluate",
                    {"expression": FOCUS_STATE_EXPRESSION, "returnByValue": True, "awaitPromise": True},
                )
                focus_state = focus_eval.get("result", {}).get("value")
                if not isinstance(focus_state, dict) or not focus_state.get("active"):
                    focus_errors.append("keyboard focus left the document before visiting every focusable element")
                    break
                focus_seen.append(str(focus_state.get("fingerprint", focus_state.get("name", "unknown"))))
                if not focus_state.get("focusVisible") or not focus_state.get("indicatorVisible"):
                    focus_errors.append(
                        f"focus indicator is not visible for {focus_state.get('name', 'unknown element')}"
                    )
            if focus_count and len(set(focus_seen)) != focus_count:
                focus_errors.append(
                    f"keyboard focus order repeated or skipped elements: visited {len(set(focus_seen))}/{focus_count}"
                )
            cdp.call(
                "Runtime.evaluate",
                {"expression": "document.activeElement && document.activeElement.blur()", "returnByValue": True},
            )

            evaluation = cdp.call(
                "Runtime.evaluate",
                {"expression": AUDIT_EXPRESSION, "returnByValue": True, "awaitPromise": True},
            )
            result = evaluation.get("result", {})
            if result.get("subtype") == "error":
                raise RuntimeError(f"layout probe failed: {result.get('description', result)}")
            payload = result.get("value")
            if not isinstance(payload, dict):
                raise RuntimeError("layout probe returned no structured result")
            payload.setdefault("errors", []).extend(focus_errors)
            return payload
        finally:
            if cdp is not None:
                cdp.close()
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


def check_document(
    path: Path,
    *,
    browser: Path | None = None,
    viewports: list[tuple[int, int]] | None = None,
    allow_placeholders: bool = False,
) -> dict:
    source = path.read_text(encoding="utf-8")
    errors: list[str] = []
    warnings: list[str] = []
    if not allow_placeholders:
        placeholders = sorted(set(re.findall(r"\{\{[A-Z0-9_-]+\}\}", source)))
        if placeholders:
            return {"errors": ["unresolved template placeholders"], "warnings": [], "viewports": []}
    browser = browser or find_browser()
    if browser is None:
        raise FileNotFoundError("Chrome, Edge, or Chromium is required for rendered layout validation")
    results = []
    for viewport in viewports or DEFAULT_VIEWPORTS:
        result = _run_viewport(browser, path, viewport)
        results.append(result)
        actual = result["viewport"]
        if (actual["width"], actual["height"]) != viewport:
            errors.append(
                f"viewport mismatch: requested {viewport[0]}x{viewport[1]}, got {actual['width']}x{actual['height']}"
            )
        prefix = f"{actual['width']}x{actual['height']}"
        errors.extend(f"{prefix}: {message}" for message in result["errors"])
        warnings.extend(f"{prefix}: {message}" for message in result["warnings"])
    return {"errors": errors, "warnings": warnings, "viewports": results}


def _parse_viewport(value: str) -> tuple[int, int]:
    match = re.fullmatch(r"(\d+)x(\d+)", value.lower())
    if not match:
        raise argparse.ArgumentTypeError("viewport must use WIDTHxHEIGHT, for example 375x812")
    return int(match.group(1)), int(match.group(2))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path)
    parser.add_argument("--browser", type=Path)
    parser.add_argument("--viewport", action="append", type=_parse_viewport)
    parser.add_argument("--template", action="store_true", help="allow {{PLACEHOLDER}} tokens")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.html.is_file():
        print(f"ERROR: file not found: {args.html}", file=sys.stderr)
        return 2
    try:
        result = check_document(
            args.html,
            browser=args.browser,
            viewports=args.viewport,
            allow_placeholders=args.template,
        )
    except (FileNotFoundError, RuntimeError, UnicodeDecodeError, ValueError, OSError, subprocess.TimeoutExpired) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for message in result["errors"]:
            print(f"ERROR: {message}")
        for message in result["warnings"]:
            print(f"WARN: {message}")
        print(f"SUMMARY: {len(result['errors'])} error(s), {len(result['warnings'])} warning(s), {len(result['viewports'])} viewport(s)")
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
