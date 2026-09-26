import base64
import datetime
import http.client
import json
import math
import os
import pathlib
import re
import sys
import time
import urllib.parse
import urllib.request

EMAIL = "me@parsa222.lol"
SITE = "parsa222.lol"
TOP_REPOS = 10

API_URL = "https://api.github.com/graphql"
MAX_RESPONSE = 4 * 1024 * 1024
RETRY_STATUSES = (429, 500, 502, 503, 504)

DIST = pathlib.Path("dist")
TILE_DIR = os.environ.get("TILE_DIR", "")
RUN_DIR = DIST / TILE_DIR if TILE_DIR else DIST
README = pathlib.Path("README.md")
PANEL_START = "<!--START:panel-->"
PANEL_END = "<!--END:panel-->"
MODES = (("dark", ""), ("light", "-light"))

PALETTES = {
    "blueprint-amber": {"dark": ["#1c2331", "#193f7a", "#2265b5", "#d97706", "#fbbf24"],
                        "light": ["#ebedf0", "#cfe3ff", "#93c0f7", "#f59e0b", "#b45309"]},
    "blueprint": {"dark": ["#1c2331", "#193f7a", "#1f5fb0", "#3b8ff0", "#8fcaff"],
                  "light": ["#ebedf0", "#cfe3ff", "#93c0f7", "#4a90e2", "#1b5fb0"]},
    "matrix": {"dark": ["#1c261f", "#0e4a2b", "#0f7a40", "#12b356", "#3dff9a"],
               "light": ["#ebedf0", "#b7f5d0", "#5fd99a", "#12a15a", "#04613a"]},
    "violet": {"dark": ["#201d30", "#3a2878", "#5537b0", "#7c5ce0", "#c4b8f7"],
               "light": ["#ebedf0", "#e0d7fb", "#b9a6f5", "#8b6ce8", "#5b3cc4"]},
    "ember": {"dark": ["#292016", "#642708", "#92400e", "#d97706", "#fbbf24"],
              "light": ["#ebedf0", "#fde68a", "#fbbf24", "#d97706", "#92400e"]},
    "mono": {"dark": ["#1c2128", "#363c44", "#4d545d", "#8b949e", "#e6edf3"],
             "light": ["#ebedf0", "#d0d7de", "#9198a1", "#59636e", "#1f2328"]},
}
BASE_COLORS = {
    "dark": {"card": "#161b22", "fg": "#e6edf3", "muted": "#8b949e", "line": "#30363d"},
    "light": {"card": "#f6f8fa", "fg": "#1f2328", "muted": "#59636e", "line": "#d1d9e0"},
}
LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3,
          "FOURTH_QUARTILE": 4}
FALLBACK_LANGUAGE_COLORS = ["#8b949e", "#6e7681", "#57606a", "#768390", "#424a53", "#909dab"]
FONT = "ui-sans-serif,-apple-system,'Segoe UI',Roboto,'Helvetica Neue',sans-serif"

ICONS = {
    "mail": '<path d="m22 7-8.991 5.727a2 2 0 0 1-2.009 0L2 7"/>'
            '<rect x="2" y="4" width="20" height="16" rx="2"/>',
    "globe": '<circle cx="12" cy="12" r="10"/>'
             '<path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/>',
    "pr": '<circle cx="5" cy="6" r="3"/><path d="M5 9v12"/><circle cx="19" cy="18" r="3"/>'
          '<path d="m15 9-3-3 3-3"/><path d="M12 6h5a2 2 0 0 1 2 2v7"/>',
}
REPO_ICON = ("M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5"
             "a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05"
             "A2.495 2.495 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8Z"
             "M5 12.25a.25.25 0 0 1 .25-.25h3.5a.25.25 0 0 1 .25.25v3.25a.25.25 0 0 1-.4.2"
             "l-1.45-1.087a.249.249 0 0 0-.3 0L5.4 15.7a.25.25 0 0 1-.4-.2Z")

BRICK_TOP = (32, [0x00000000, 0x00000000, 0x01c001c0, 0x06300630, 0x0a080a08, 0x12081208,
                  0x11041104, 0x11841184, 0x12c412c4, 0x0d780d78, 0x0aa80aa8, 0x07500750,
                  0x01e001e0, 0x00000000, 0x00000000, 0x00000000])
BRICK_SIDE = (32, [0x00000000] * 15 + [0xaaaaaaaa])
ISO_ANGLE = 30
BLOCKS_WIDTH = 780
RADAR_WIDTH, RADAR_HEIGHT = 308, 234
RADAR_TICKS = ["1", "10", "100", "1K", "10K"]
RADAR_KINDS = {
    "Commit": "totalCommitContributions",
    "Issue": "totalIssueContributions",
    "PullReq": "totalPullRequestContributions",
    "Review": "totalPullRequestReviewContributions",
    "Repo": "totalRepositoryContributions",
}
PIE_WIDTH, PIE_HEIGHT = 468, 234

CALENDAR_WIDTH = 400.0
TILE_CALENDARS = {
    "snake": {"origin": (2, 2), "cell": 12, "pitch": 16},
    "grid": {"origin": (10, 10), "cell": 10, "pitch": 13},
    "game": {"origin": (0, 15), "cell": 20, "pitch": 22},
    "life": {"origin": (30, 20), "cell": 11, "pitch": 14},
}
TILES = {
    "snake": ["snake.svg", "snake-light.svg"],
    "grid": ["grid.svg", "grid-light.svg"],
    "game": ["game.svg", "game-light.svg"],
    "life": ["life.svg", "life-light.svg"],
}
CARD_NAMES = ["grid", "blocks", "radar", "pie", "badge-repos", "badge-lang-1", "badge-lang-2",
              "badge-lang-3", "badge-lang-4", "badge-email", "badge-site"]
CARD_NAMES += [f"avatar-{i}" for i in range(1, TOP_REPOS + 1)]
AVATAR_RING = {"dark": "#3d444d", "light": "#d1d9e0"}
AVATAR_TYPES = ("image/png", "image/jpeg", "image/gif", "image/webp")
EMPTY_SVG = ('<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1" '
             'viewBox="0 0 1 1" role="presentation"></svg>')

PROFILE_QUERY = """
query ($login: String!) {
  user(login: $login) {
    createdAt
    contributionsCollection {
      totalCommitContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionCount contributionLevel weekday } }
      }
    }
    repositories(first: 100, ownerAffiliations: OWNER, privacy: PUBLIC) {
      totalCount
      nodes { languages(first: 10) { edges { size node { name color } } } }
    }
  }
}
"""
YEAR_QUERY = """
query ($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      totalRepositoryContributions
      commitContributionsByRepository(maxRepositories: 100) {
        repository { nameWithOwner stargazerCount owner { login __typename } }
        contributions { totalCount }
      }
    }
  }
}
"""


def escape(text):
    return (str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def fmt(value):
    return f"{value:.2f}".rstrip("0").rstrip(".")


def rgb(color):
    digits = color.lstrip("#")
    return [int(digits[i:i + 2], 16) for i in (0, 2, 4)]


def shade(color, factor):
    return "#%02x%02x%02x" % tuple(min(255, round(channel * factor)) for channel in rgb(color))


def luminance(color):
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
              for c in (channel / 255 for channel in rgb(color))]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def text_color_on(background):
    white, black = "#ffffff", "#0d1117"
    return white if contrast(white, background) >= contrast(black, background) else black


def text_width(text, size):
    narrow = sum(c in "iljtfrI.,:;'|! " for c in text)
    wide = sum(c in "MWmw@%" for c in text)
    return size * (0.58 * len(text) - 0.22 * narrow + 0.20 * wide)


def truncate(text, limit=16):
    return text if len(text) <= limit else text[:limit - 1] + "…"


def human_count(n):
    if n < 1000:
        return str(n)
    if n < 100_000:
        return f"{n / 1000:.1f}".rstrip("0").rstrip(".") + "k"
    return f"{round(n / 1000)}k"


def human_bytes(n):
    if n >= 1024 ** 2:
        return f"{n / 1024 ** 2:.1f}MB"
    if n >= 1024:
        return f"{n / 1024:.0f}KB"
    return f"{n:.0f}B"


def language_color(info, rank):
    color = info["color"] or ""
    if re.fullmatch(r"#[0-9a-fA-F]{6}", color):
        return color
    return FALLBACK_LANGUAGE_COLORS[rank % len(FALLBACK_LANGUAGE_COLORS)]


def theme_colors(palette, mode):
    return {**BASE_COLORS[mode], "cells": PALETTES[palette][mode]}


def http_request(url, body=None, headers=None):
    request = urllib.request.Request(
        url, data=body, headers={"User-Agent": "profile-gen", **(headers or {})})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                content = response.read(MAX_RESPONSE)
                if len(content) == MAX_RESPONSE:
                    raise SystemExit(f"{url}: response over 4 MB")
                return response.headers.get_content_type(), content
        except (OSError, http.client.HTTPException) as error:
            status = getattr(error, "code", 503)
            if attempt == 3 or status not in RETRY_STATUSES:
                raise
            retry_after = (getattr(error, "headers", None) or {}).get("Retry-After", "")
            time.sleep(min(int(retry_after), 60) if retry_after.isdigit() else 2 ** attempt)


def graphql(token, query, **variables):
    body = json.dumps({"query": query, "variables": variables}).encode()
    headers = {"Authorization": f"bearer {token}", "Content-Type": "application/json"}
    payload = json.loads(http_request(API_URL, body, headers)[1])
    if "errors" in payload:
        raise SystemExit("graphql: " + json.dumps(payload["errors"]))
    return payload["data"]["user"]


def year_windows(created_at, now=None):
    start = datetime.datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    now = now or datetime.datetime.now(datetime.timezone.utc)
    year, second = datetime.timedelta(days=365), datetime.timedelta(seconds=1)
    iso = "%Y-%m-%dT%H:%M:%SZ"
    windows = []
    while start <= now:
        windows.append((start.strftime(iso), min(start + year - second, now).strftime(iso)))
        start += year
    return windows


def summarize(profile, years, login):
    calendar = profile["contributionsCollection"]["contributionCalendar"]
    weeks = [[{"level": LEVELS[day["contributionLevel"]], "count": day["contributionCount"],
               "weekday": day["weekday"]} for day in week["contributionDays"]]
             for week in calendar["weeks"]]

    languages = {}
    repositories = profile["repositories"]["nodes"]
    if len(repositories) >= 100:
        print("WARNING: hit the 100-repo cap, language totals are short")
    for repository in repositories:
        for edge in repository["languages"]["edges"]:
            language = languages.setdefault(edge["node"]["name"],
                                            {"size": 0, "color": edge["node"]["color"]})
            language["size"] += edge["size"]

    kinds = dict.fromkeys(RADAR_KINDS, 0)
    contributed = {}
    for year in years:
        collection = year["contributionsCollection"]
        for kind, field in RADAR_KINDS.items():
            kinds[kind] += collection[field]
        commits_by_repository = collection["commitContributionsByRepository"]
        if len(commits_by_repository) >= 100:
            print("WARNING: hit the 100-repo cap on commitContributionsByRepository, "
                  "panel may be short")
        for item in commits_by_repository:
            repository = item["repository"]
            entry = contributed.setdefault(repository["nameWithOwner"], {
                "name": repository["nameWithOwner"],
                "owner": repository["owner"]["login"],
                "org": repository["owner"]["__typename"] == "Organization",
                "count": 0,
            })
            entry["count"] += item["contributions"]["totalCount"]
            entry["stars"] = repository["stargazerCount"]

    ranked = sorted(contributed.values(),
                    key=lambda repo: (-repo["stars"], -repo["count"], repo["name"].lower()))
    external = [repo for repo in ranked if repo["owner"].lower() != login.lower()]

    return {
        "login": login,
        "total": calendar["totalContributions"],
        "commits": profile["contributionsCollection"]["totalCommitContributions"],
        "weeks": weeks,
        "contributed": external,
        "languages": sorted(languages.items(), key=lambda item: -item[1]["size"]),
        "kinds": kinds,
        "public_repos": profile["repositories"]["totalCount"],
    }


def calendar_box(tile, weeks):
    grid = TILE_CALENDARS[tile]
    x, y = grid["origin"]
    return x, y, (weeks - 1) * grid["pitch"] + grid["cell"], 6 * grid["pitch"] + grid["cell"]


def root_tag(svg):
    return re.search(r"""<svg(?:"[^"]*"|'[^']*'|[^"'>])*>""", svg).group(0)


def read_viewbox(svg):
    head = root_tag(svg)
    viewbox = re.search(
        r"""\bviewBox=["']\s*([-\d.]+)[ ,]+([-\d.]+)[ ,]+([-\d.]+)[ ,]+([-\d.]+)""", head)
    if viewbox:
        return tuple(float(value) for value in viewbox.groups())
    width = re.search(r"""\bwidth=["']([\d.]+)""", head)
    height = re.search(r"""\bheight=["']([\d.]+)""", head)
    if not (width and height):
        raise SystemExit("tile SVG has neither a viewBox nor width/height")
    return 0.0, 0.0, float(width.group(1)), float(height.group(1))


def common_frame(boxes, viewboxes):
    left = right = top = bottom = height = 0.0
    for tile, (x, y, width, grid_height) in boxes.items():
        vx, vy, vw, vh = viewboxes[tile]
        scale = CALENDAR_WIDTH / width
        left = max(left, (x - vx) * scale)
        right = max(right, (vx + vw - x - width) * scale)
        top = max(top, (y - vy) * scale)
        bottom = max(bottom, (vy + vh - y - grid_height) * scale)
        height = max(height, grid_height * scale)
    return {"left": left, "top": top,
            "width": left + CALENDAR_WIDTH + right, "height": top + height + bottom}


def retile(svg, tile, weeks, frame):
    x, y, width, _ = calendar_box(tile, weeks)
    scale = CALENDAR_WIDTH / width
    viewbox = (x - frame["left"] / scale, y - frame["top"] / scale,
               frame["width"] / scale, frame["height"] / scale)
    head = root_tag(svg)
    start = svg.index(head)
    new_head = re.sub(r"""\s+(viewBox|width|height|preserveAspectRatio)=("[^"]*"|'[^']*')""",
                      "", head[:-1])
    new_head += (f' viewBox="{" ".join(fmt(v) for v in viewbox)}"'
                 f' width="{fmt(frame["width"])}" height="{fmt(frame["height"])}"'
                 ' preserveAspectRatio="xMidYMid meet" data-retiled="1">')
    body = re.sub(r'<rect width="100%" height="100%"[^>]*/>', "", svg[start + len(head):],
                  count=1)
    return svg[:start] + new_head + body


def gradient(gradient_id, start, end, x2=0, y2=1):
    return (f'<linearGradient id="{gradient_id}" x1="0" y1="0" x2="{x2}" y2="{y2}">'
            f'<stop offset="0" stop-color="{start}"/>'
            f'<stop offset="1" stop-color="{end}"/></linearGradient>')


def right_tab(x, width, height, radius, fill):
    return (f'<path d="M{fmt(x)} 0h{fmt(width - radius)}a{radius} {radius} 0 0 1 {radius} {radius}'
            f'v{height - 2 * radius}a{radius} {radius} 0 0 1 -{radius} {radius}'
            f'h-{fmt(width - radius)}z" fill="{fill}"/>')


def badge_svg(label, value, theme, accent, icon="", dot="", style="raised"):
    size, height, pad, radius = 11, 26, 9, 6
    mark_width = 17 if (icon or dot) else 0
    label_width = (text_width(label, size) if label else 0) + pad * 2 + mark_width
    value_width = text_width(value, size) + pad * 2
    width = label_width + value_width
    baseline = height / 2 + 4
    label_color = theme["muted"]
    value_color = text_color_on(shade(accent, 0.94))

    defs, under, over = [], [], []
    if style == "raised":
        defs.append(gradient("gl", theme["line"], shade(theme["line"], 0.72)))
        defs.append(gradient("gv", shade(accent, 1.28), accent))
        under.append(f'<rect y="2" width="{fmt(width)}" height="{height - 2}" rx="{radius}" '
                     f'fill="{shade(accent, 0.45)}"/>')
        under.append(f'<rect width="{fmt(label_width + radius)}" height="{height - 2}" '
                     f'rx="{radius}" fill="url(#gl)"/>')
        under.append(right_tab(label_width, value_width, height - 2, radius, "url(#gv)"))
        over.append(f'<path d="M{radius} 0.5h{fmt(width - 2 * radius)}" stroke="#ffffff" '
                    f'stroke-opacity="0.28"/>')
    elif style == "gradient":
        defs.append(gradient("gv", shade(accent, 1.25), shade(accent, 0.62), x2=1))
        under.append(f'<rect width="{fmt(width)}" height="{height}" rx="{radius}" '
                     f'fill="{theme["line"]}"/>')
        under.append(right_tab(label_width, value_width, height, radius, "url(#gv)"))
    else:
        under.append(f'<rect x="0.5" y="0.5" width="{fmt(width - 1)}" height="{height - 1}" '
                     f'rx="{radius}" fill="none" stroke="{accent}"/>')
        under.append(f'<path d="M{fmt(label_width)} 0.5v{height - 1}" stroke="{accent}"/>')
        value_color = accent

    mark = ""
    if icon:
        icon_x = pad if label else (label_width - 12) / 2
        mark = (f'<g transform="translate({fmt(icon_x)},{(height - 12) / 2}) scale(0.5)" '
                f'fill="none" stroke="{label_color}" stroke-width="2.4" stroke-linecap="round" '
                f'stroke-linejoin="round">{ICONS[icon]}</g>')
    elif dot:
        mark = f'<circle cx="{pad + 4}" cy="{height / 2}" r="4" fill="{dot}"/>'

    label_text = ""
    if label:
        label_text = (f'<text x="{fmt(pad + mark_width)}" y="{fmt(baseline)}" font-family="{FONT}" '
                      f'font-size="{size}" fill="{label_color}">{escape(label)}</text>')

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height}" \
viewBox="0 0 {fmt(width)} {height}" role="img" aria-label="{escape(label or icon)}: {escape(value)}">
<defs>{"".join(defs)}</defs>{"".join(under)}{mark}{label_text}{"".join(over)}
<text x="{fmt(label_width + pad)}" y="{fmt(baseline)}" font-family="{FONT}" font-size="{size}" \
fill="{value_color}" font-weight="600">{escape(value)}</text>
</svg>"""


def link_badges(theme, accent):
    return {
        "badge-email.svg": badge_svg("", EMAIL, theme, accent, icon="mail", style="outline"),
        "badge-site.svg": badge_svg("", SITE, theme, accent, icon="globe", style="outline"),
    }


def stat_badges(data, theme, accent):
    files = {"badge-repos.svg": badge_svg("contributed in", f"{len(data['contributed'])} repos",
                                          theme, accent, icon="pr", style="raised")}
    top_languages = data["languages"][:4]
    for rank in range(1, 5):
        svg = EMPTY_SVG
        if rank <= len(top_languages):
            name, info = top_languages[rank - 1]
            color = language_color(info, rank - 1)
            svg = badge_svg(name.lower(), human_bytes(info["size"]), theme, color,
                            dot=color, style="gradient")
        files[f"badge-lang-{rank}.svg"] = svg
    return files


def grid_svg(weeks, theme):
    grid = TILE_CALENDARS["grid"]
    cell, pitch, pad = grid["cell"], grid["pitch"], grid["origin"][0]
    count = len(weeks)
    width = count * pitch - (pitch - cell) + pad * 2
    height = 7 * pitch - (pitch - cell) + pad * 2

    cells, keyframes = [], []
    for x, week in enumerate(weeks):
        appear = round(x / max(1, count - 1) * 60, 2)
        keyframes.append(f"@keyframes k{x}{{0%,{appear}%{{opacity:0}}{min(appear + 4, 100)}%,100%"
                         f"{{opacity:1}}}}.w{x}{{animation-name:k{x}}}")
        for day in week:
            cells.append(f'<rect class="c w{x}" x="{pad + x * pitch}" '
                         f'y="{pad + day["weekday"] * pitch}" width="{cell}" height="{cell}" '
                         f'rx="2" fill="{theme["cells"][day["level"]]}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'width="{width}" height="{height}" role="img" aria-label="contribution calendar">'
            f'<style>.c{{animation-duration:4200ms;animation-timing-function:ease-out;'
            f'animation-iteration-count:1;animation-fill-mode:both}}{"".join(keyframes)}</style>'
            f'{"".join(cells)}</svg>')


def bitmap_pattern(pattern_id, bitmap, background, ink):
    width, rows = bitmap
    path = "".join(f"M{x} {y}h1v1h-1z" for y, bits in enumerate(rows) for x in range(width)
                   if bits & (1 << (width - x - 1)))
    return (f'<pattern id="{pattern_id}" x="0" y="0" width="{width}" height="{len(rows)}" '
            f'patternUnits="userSpaceOnUse">'
            f'<rect width="{width}" height="{len(rows)}" fill="{background}"/>'
            f'<path fill="{ink}" d="{path}"/></pattern>')


def card_svg_tag(width, height, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'width="{width}" height="{height}" font-family="{FONT}" role="img" '
            f'aria-label="{label}">')


def card_frame(width, height, theme):
    return (f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="14" '
            f'fill="{theme["card"]}" stroke="{theme["line"]}"/>')


def svg_text(x, y, size, fill, content, bold=False):
    weight = ' font-weight="bold"' if bold else ""
    return (f'<text x="{fmt(x)}" y="{fmt(y)}" font-size="{fmt(size)}"{weight} '
            f'fill="{fill}">{content}</text>')


def bar_height(count):
    return math.log10(count / 20 + 1) * 144 + 3


def blocks_svg(data, theme):
    weeks = data["weeks"]
    width, scale = BLOCKS_WIDTH, BLOCKS_WIDTH / 1280
    step_x = width / 64
    step_y = step_x * math.tan(math.radians(ISO_ANGLE))
    face_x, face_y = step_x * 0.9, step_y * 0.9

    tallest = max((day["count"] for week in weeks for day in week), default=0)
    header = math.ceil(bar_height(tallest)) + 14
    footer = round(46 * scale) + 18
    origin_x, origin_y = step_x * 7, float(header)
    height = math.ceil(origin_y + (len(weeks) + 5) * step_y + footer)

    patterns = []
    for level, color in enumerate(theme["cells"]):
        stud = shade(color, 0.5 if level else 1.6)
        patterns.append(bitmap_pattern(f"p{level}t", BRICK_TOP, color, stud))
        patterns.append(bitmap_pattern(f"p{level}l", BRICK_SIDE,
                                       shade(color, 0.84), shade(stud, 0.84)))
        patterns.append(bitmap_pattern(f"p{level}r", BRICK_SIDE,
                                       shade(color, 0.70), shade(stud, 0.70)))

    top_size, side_size = BRICK_TOP[0], BRICK_SIDE[0]
    top_scale = face_x / top_size
    side_scale = math.hypot(face_x, face_y) / side_size
    skew = math.degrees(math.atan(face_x / 2 / face_y))

    bars = []
    for week, days in enumerate(weeks):
        for day in days:
            weekday, level = day["weekday"], day["level"]
            bar = bar_height(day["count"])
            x = origin_x + (week - weekday) * step_x
            y = origin_y + (week + weekday) * step_y
            grow = rise = ""
            if level:
                grow = (f'<animateTransform attributeName="transform" type="translate" '
                        f'values="{fmt(x)} {fmt(y - 3)};{fmt(x)} {fmt(y - bar)}" dur="3s" '
                        f'repeatCount="1"/>')
                rise = (f'<animate attributeName="height" '
                        f'values="{fmt(3 / side_scale)};{fmt(bar / side_scale)}" dur="3s" '
                        f'repeatCount="1"/>')
            bars.append(
                f'<g transform="translate({fmt(x)} {fmt(y - bar)})">{grow}'
                f'<rect width="{top_size}" height="{top_size}" fill="url(#p{level}t)" '
                f'transform="skewY({-ISO_ANGLE}) skewX({fmt(skew)}) '
                f'scale({top_scale:.4f} {2 * face_y / top_size:.4f})"/>'
                f'<rect width="{side_size}" height="{fmt(bar / side_scale)}" fill="url(#p{level}l)" '
                f'transform="skewY({ISO_ANGLE}) scale({face_x / side_size:.4f} {side_scale:.4f})">'
                f'{rise}</rect>'
                f'<rect width="{side_size}" height="{fmt(bar / side_scale)}" fill="url(#p{level}r)" '
                f'transform="translate({fmt(face_x)} {fmt(face_y)}) skewY({-ISO_ANGLE}) '
                f'scale({face_x / side_size:.4f} {side_scale:.4f})">{rise}</rect></g>')

    baseline, big, small = height - 20 * scale, 32 * scale, 24 * scale
    commits, repos = f"{data['commits']:,}", f"{data['public_repos']:,}"
    commits_label, repos_label = "commits in the last year", "public repos"
    commits_x = (width - (text_width(commits, big) + 8 * scale + text_width(commits_label, small)
                          + 60 * scale + 42 * scale + text_width(repos, big) + 8 * scale
                          + text_width(repos_label, small))) / 2
    commits_label_x = commits_x + text_width(commits, big) + 8 * scale
    icon_x = commits_label_x + text_width(commits_label, small) + 60 * scale
    repos_x = icon_x + 42 * scale
    repos_label_x = repos_x + text_width(repos, big) + 8 * scale

    label = f"{data['commits']} commits in the last year, contributions as 3d blocks"
    return "\n".join([
        card_svg_tag(width, height, label),
        f'<defs>{"".join(patterns)}</defs>',
        card_frame(width, height, theme),
        "".join(bars),
        svg_text(commits_x, baseline, big, theme["fg"], commits, bold=True),
        svg_text(commits_label_x, baseline, small, theme["muted"], commits_label),
        f'<g transform="translate({fmt(icon_x)} {fmt(baseline - 28 * scale)}) '
        f'scale({fmt(2 * scale)})"><path fill-rule="evenodd" d="{REPO_ICON}" '
        f'fill="{theme["fg"]}"/></g>',
        svg_text(repos_x, baseline, big, theme["fg"], repos, bold=True),
        svg_text(repos_label_x, baseline, small, theme["muted"], repos_label),
        "</svg>",
    ])


def radar_svg(data, theme, accent):
    width, height = RADAR_WIDTH, RADAR_HEIGHT
    rings = len(RADAR_TICKS)
    radius, center_x, center_y = (height / 2) * 0.8, width / 2, (height / 2) * 1.1
    kinds = list(data["kinds"].items())
    spokes = len(kinds)

    def x_at(ring, spoke):
        return fmt(radius * (ring / rings) * math.sin(spoke / spokes * math.tau))

    def y_at(ring, spoke):
        return fmt(radius * (ring / rings) * -math.cos(spoke / spokes * math.tau))

    def ring_for(value):
        return 0.8 if value < 1 else min(math.log10(value), 4) + 1

    dashed = f'stroke="{theme["muted"]}" stroke-dasharray="4 4" stroke-width="1"'
    web = []
    for ring in range(1, rings + 1):
        for spoke in range(spokes):
            web.append(f'<line x1="{x_at(ring, spoke)}" y1="{y_at(ring, spoke)}" '
                       f'x2="{x_at(ring, spoke + 1)}" y2="{y_at(ring, spoke + 1)}" {dashed}/>')
    for i, tick in enumerate(RADAR_TICKS):
        web.append(f'<text x="{fmt(radius / 50)}" y="{fmt(-radius * ((i + 1) / rings))}" '
                   f'font-size="{fmt(radius / 12)}" fill="{theme["muted"]}">{tick}</text>')
    for spoke, (name, value) in enumerate(kinds):
        web.append(f'<line x1="{x_at(1, spoke)}" y1="{y_at(1, spoke)}" '
                   f'x2="{x_at(rings, spoke)}" y2="{y_at(rings, spoke)}" {dashed}/>'
                   f'<text x="{x_at(1.25 * rings, spoke)}" y="{y_at(1.17 * rings, spoke)}" '
                   f'font-size="{fmt(radius / 7.5)}" text-anchor="middle" '
                   f'dominant-baseline="middle" fill="{theme["fg"]}">{escape(name)}'
                   f'<title>{value}</title></text>')

    points = " ".join(f"{x_at(ring_for(value), spoke)},{y_at(ring_for(value), spoke)}"
                      for spoke, (_, value) in enumerate(kinds))
    start_points = " ".join(f"{x_at(0.8, spoke)},{y_at(0.8, spoke)}" for spoke in range(spokes))

    return "\n".join([
        card_svg_tag(width, height, "contributions by kind, all time"),
        card_frame(width, height, theme),
        f'<g transform="translate({fmt(center_x)} {fmt(center_y)})">{"".join(web)}',
        f'<polygon points="{points}" fill="{accent}" fill-opacity="0.5" stroke="{accent}" '
        f'stroke-width="4">',
        f'<animate attributeName="points" values="{start_points};{points}" dur="3s" '
        f'repeatCount="1"/></polygon>',
        "</g></svg>",
    ])


def pie_svg(data, theme):
    width, height = PIE_WIDTH, PIE_HEIGHT
    slices = [(name, info["size"], language_color(info, i))
              for i, (name, info) in enumerate(data["languages"][:5])]
    rest = sum(info["size"] for _, info in data["languages"][5:])
    if rest > 0:
        slices.append(("other", rest, "#444444"))
    total = sum(size for _, size, _ in slices) or 1

    radius = height / 2
    outer, inner = radius - radius / 10, radius / 2
    rows, fade_steps = 8, 5
    first_row = (rows - len(slices)) / 2 + 0.5
    font_size = height / rows / 1.5

    def fade_in(i):
        values = ";".join(str(0 if j < i else min((j - i) / fade_steps, 1))
                          for j in range(len(slices) + fade_steps))
        return (f'<animate attributeName="fill-opacity" values="{values}" dur="3s" '
                f'repeatCount="1"/>')

    def point(r, angle):
        return f"{r * math.sin(angle):.2f} {-r * math.cos(angle):.2f}"

    arcs, legend, angle = [], [], 0.0
    for i, (name, size, color) in enumerate(slices):
        start = angle
        angle += size / total * math.tau
        end = min(angle, start + math.tau - 1e-4)
        large = 1 if end - start > math.pi else 0
        path = (f"M{point(outer, start)}A{outer} {outer} 0 {large} 1 {point(outer, end)}"
                f"L{point(inner, end)}A{inner} {inner} 0 {large} 0 {point(inner, start)}Z")
        arcs.append(f'<path d="{path}" fill="{color}" stroke="{theme["card"]}" stroke-width="2">'
                    f'<title>{escape(name)} {human_bytes(size)}</title>{fade_in(i)}</path>')
        row_y = (i + first_row) * (height / rows)
        legend.append(f'<rect x="0" y="{fmt(row_y - font_size / 2)}" width="{fmt(font_size)}" '
                      f'height="{fmt(font_size)}" fill="{color}" stroke="{theme["card"]}">'
                      f'{fade_in(i)}</rect>'
                      f'<text x="{fmt(font_size * 1.2)}" y="{fmt(row_y)}" dominant-baseline="middle" '
                      f'font-size="{fmt(font_size)}" fill="{theme["fg"]}">{escape(truncate(name))}'
                      f'<title>{escape(name)}</title>{fade_in(i)}</text>')

    return "\n".join([
        card_svg_tag(width, height, "languages by size"),
        card_frame(width, height, theme),
        f'<g transform="translate({fmt(radius * 2.1)} 0)">{"".join(legend)}</g>',
        f'<g transform="translate({fmt(radius)} {fmt(radius)})">{"".join(arcs)}</g></svg>',
    ])


def avatar_svg(content_type, image, is_org, ring):
    radius = 6 if is_org else 13
    encoded = base64.b64encode(image).decode()
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 26 26" width="26" height="26" '
            f'role="img" aria-label="avatar"><clipPath id="c"><rect width="26" height="26" '
            f'rx="{radius}"/></clipPath>'
            f'<image href="data:{content_type};base64,{encoded}" width="26" height="26" '
            f'clip-path="url(#c)"/><rect x="0.5" y="0.5" width="25" height="25" '
            f'rx="{radius - 0.5}" fill="none" stroke="{ring}"/></svg>')


def avatars(data):
    files = {}
    for i, repo in enumerate(data["contributed"][:TOP_REPOS], 1):
        owner = urllib.parse.quote(repo["owner"], safe="")
        content_type, image = http_request(f"https://github.com/{owner}.png?size=64")
        if content_type not in AVATAR_TYPES:
            raise SystemExit(f"avatar for {repo['owner']}: unexpected content type {content_type}")
        for mode, suffix in MODES:
            files[f"avatar-{i}{suffix}.svg"] = avatar_svg(content_type, image, repo["org"],
                                                         AVATAR_RING[mode])
    return files


def themed_image(dark_url, light_url, **attributes):
    extra = "".join(f' {name}="{value}"' for name, value in attributes.items())
    return (f'<picture><source media="(prefers-color-scheme: light)" srcset="{light_url}">'
            f'<img src="{dark_url}"{extra}></picture>')


def panel_html(data):
    raw = f"https://raw.githubusercontent.com/{data['login']}/{data['login']}"
    star = themed_image(f"{raw}/main/star.svg", f"{raw}/main/star-light.svg",
                        width=14, height=14, align="absmiddle", alt="stars")
    rows = []
    for i, repo in enumerate(data["contributed"][:TOP_REPOS], 1):
        url = f"https://github.com/{escape(repo['name'])}"
        avatar = themed_image(f"{raw}/output/avatar-{i}.svg", f"{raw}/output/avatar-{i}-light.svg",
                              width=26, height=26, align="absmiddle", alt="")
        stars = f' <code>{star} {human_count(repo["stars"])}</code>' if repo.get("stars") else ""
        rows.append(f'<tr><td><a href="{url}">{avatar}</a> <a href="{url}">{escape(repo["name"])}</a>'
                    f'{stars}</td><td align="right"><code>{repo["count"]}</code></td></tr>')
    if not rows:
        rows.append('<tr><td colspan="2">no external contributions yet</td></tr>')
    header = '<tr><th align="left">contributed in</th><th align="right">commits</th></tr>'
    return f"{PANEL_START}\n<table>\n{header}\n" + "\n".join(rows) + f"\n</table>\n{PANEL_END}"


def write_panel(block, login):
    with README.open("r", encoding="utf-8", newline="") as file:
        old = file.read()
    if old.count(PANEL_START) != 1 or old.count(PANEL_END) != 1:
        raise SystemExit(f"README.md needs exactly one {PANEL_START} and one {PANEL_END}")
    if old.index(PANEL_END) < old.index(PANEL_START):
        raise SystemExit(f"README.md has {PANEL_END} before {PANEL_START}")
    if "\r\n" in old:
        block = block.replace("\n", "\r\n")

    panel = re.escape(PANEL_START) + r".*?" + re.escape(PANEL_END)
    new = re.sub(panel, lambda _: block, old, flags=re.S)

    output_url = f"https://raw.githubusercontent.com/{login}/{login}/output/"
    run_url = output_url + (f"{TILE_DIR}/" if TILE_DIR else "")
    new = re.sub(re.escape(output_url) + r"(?:[0-9][0-9-]*/)?(?!profile\.webp)", run_url, new)

    if new == old:
        return False
    with README.open("w", encoding="utf-8", newline="") as file:
        file.write(new)
    return True


def build(data, palette):
    files = {}
    for mode, suffix in MODES:
        theme = theme_colors(palette, mode)
        accent, ink = PALETTES[palette][mode][3], PALETTES[palette][mode][4]
        files[f"grid{suffix}.svg"] = grid_svg(data["weeks"], theme)
        files[f"blocks{suffix}.svg"] = blocks_svg(data, theme)
        files[f"radar{suffix}.svg"] = radar_svg(data, theme, ink)
        files[f"pie{suffix}.svg"] = pie_svg(data, theme)
        links = link_badges(BASE_COLORS[mode], accent if mode == "dark" else ink)
        for name, svg in {**stat_badges(data, BASE_COLORS[mode], accent), **links}.items():
            files[name.replace(".svg", f"{suffix}.svg")] = svg
    return files


def retile_all(weeks):
    missing = [f for files in TILES.values() for f in files if not (RUN_DIR / f).exists()]
    if missing:
        raise SystemExit(f"retile: missing {', '.join(missing)} in {RUN_DIR}/, "
                         "every tile needs a dark and a light file")
    expected = {f for files in TILES.values() for f in files}
    expected |= {f"{card}{suffix}.svg" for card in CARD_NAMES for _, suffix in MODES}
    stray = sorted(p.name for p in RUN_DIR.iterdir() if p.name not in expected)
    if stray:
        raise SystemExit(f"retile: unexpected files in {RUN_DIR}/: {', '.join(stray)}")
    for files in TILES.values():
        if 'data-retiled="1"' in (RUN_DIR / files[0]).read_text():
            raise SystemExit(f"retile: {files[0]} is already retiled, start from a clean dist/")

    viewboxes = {tile: read_viewbox((RUN_DIR / files[0]).read_text())
                 for tile, files in TILES.items()}
    boxes = {tile: calendar_box(tile, weeks) for tile in TILES}
    frame = common_frame(boxes, viewboxes)
    print(f"tile window {frame['width']:.1f} x {frame['height']:.1f}, "
          f"calendar {CALENDAR_WIDTH:.0f} wide")
    for tile, files in TILES.items():
        for name in files:
            path = RUN_DIR / name
            path.write_text(retile(path.read_text(), tile, weeks, frame))
            print(f"retiled {name}")


def main():
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    if "--retile" in sys.argv:
        return retile_all(int(os.environ.get("WEEKS", "53")))

    action_tiles = {f for tile, files in TILES.items() if tile != "grid" for f in files}
    stray = sorted(p.name for p in RUN_DIR.iterdir() if p.name not in action_tiles)
    if stray:
        raise SystemExit(f"{RUN_DIR}/ should hold only the six tiles from the tile actions, "
                         f"found: {', '.join(stray)}")

    palette = os.environ.get("CARD_PALETTE", "blueprint-amber")
    login = os.environ["GITHUB_REPOSITORY_OWNER"]
    token = os.environ["GITHUB_TOKEN"]

    profile = graphql(token, PROFILE_QUERY, login=login)
    years = [graphql(token, YEAR_QUERY, login=login, **{"from": start, "to": end})
             for start, end in year_windows(profile["createdAt"])]
    print(f"{login}: joined {profile['createdAt'][:10]}, {len(years)} year windows")

    data = summarize(profile, years, login)
    print(f"{data['total']} contributions this year, {len(data['contributed'])} external repos, "
          f"{len(data['languages'])} languages, {data['public_repos']} public repos")
    print("all time: " + ", ".join(f"{kind} {count}" for kind, count in data["kinds"].items()))

    for name, svg in {**build(data, palette), **avatars(data)}.items():
        (RUN_DIR / name).write_text(svg)
        print(f"{name:22} {len(svg) // 1024:>4} KB")

    updated = write_panel(panel_html(data), login)
    print("README panel " + ("updated" if updated else "unchanged"))

    weeks = len(data["weeks"])
    print(f"WEEKS={weeks}")
    if env_file := os.environ.get("GITHUB_ENV"):
        with open(env_file, "a") as file:
            file.write(f"WEEKS={weeks}\n")


if __name__ == "__main__":
    main()
