import datetime
import json
import math
import os
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request

EMAIL = "me@parsa222.lol"
SITE = "parsa222.lol"
TOP_REPOS = 10

API = "https://api.github.com/graphql"
OUT = pathlib.Path("dist")
README = pathlib.Path("README.md")
PANEL_START = "<!--START:panel-->"
PANEL_END = "<!--END:panel-->"

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
BASE = {
    "dark": {"card": "#161b22", "fg": "#e6edf3", "muted": "#8b949e", "line": "#30363d"},
    "light": {"card": "#f6f8fa", "fg": "#1f2328", "muted": "#59636e", "line": "#d1d9e0"},
}
LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3,
          "FOURTH_QUARTILE": 4}
NULL_LANG = ["#8b949e", "#6e7681", "#57606a", "#768390", "#424a53", "#909dab"]
FONT = "ui-sans-serif,-apple-system,'Segoe UI',Roboto,'Helvetica Neue',sans-serif"

ICONS = {
    "mail": '<path d="m22 7-8.991 5.727a2 2 0 0 1-2.009 0L2 7"/>'
            '<rect x="2" y="4" width="20" height="16" rx="2"/>',
    "globe": '<circle cx="12" cy="12" r="10"/>'
             '<path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/>',
    "pr": '<circle cx="5" cy="6" r="3"/><path d="M5 9v12"/><circle cx="19" cy="18" r="3"/>'
          '<path d="m15 9-3-3 3-3"/><path d="M12 6h5a2 2 0 0 1 2 2v7"/>',
}
OCTI_REPO = ("M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5"
             "a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05"
             "A2.495 2.495 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8Z"
             "M5 12.25a.25.25 0 0 1 .25-.25h3.5a.25.25 0 0 1 .25.25v3.25a.25.25 0 0 1-.4.2"
             "l-1.45-1.087a.249.249 0 0 0-.3 0L5.4 15.7a.25.25 0 0 1-.4-.2Z")

GITBLOCK_TOP = (32, [0x00000000, 0x00000000, 0x01c001c0, 0x06300630, 0x0a080a08, 0x12081208,
                     0x11041104, 0x11841184, 0x12c412c4, 0x0d780d78, 0x0aa80aa8, 0x07500750,
                     0x01e001e0, 0x00000000, 0x00000000, 0x00000000])
GITBLOCK_SIDE = (32, [0x00000000] * 15 + [0xaaaaaaaa])
ANGLE = 30
BLOCK_W = 780
RADAR_W, RADAR_H = 308, 234
PIE_W, PIE_H = 468, 234
RANGE = ["1", "10", "100", "1K", "10K"]

GRID_W = 400.0
SOURCES = {
    "snake": {"origin": (2, 2), "cell": 12, "pitch": 16},
    "grid": {"origin": (10, 10), "cell": 10, "pitch": 13},
    "game": {"origin": (0, 15), "cell": 20, "pitch": 22},
    "life": {"origin": (30, 20), "cell": 11, "pitch": 14},
}
CARDS = ["grid", "blocks", "radar", "pie", "badge-repos", "badge-lang-1", "badge-lang-2",
         "badge-lang-3", "badge-lang-4", "badge-email", "badge-site"]
TILES = {
    "snake": ["snake.svg", "snake-light.svg"],
    "grid": ["grid.svg", "grid-light.svg"],
    "game": ["game.svg", "game-light.svg"],
    "life": ["life.svg", "life-light.svg"],
}

QUERY_MAIN = """
query ($login: String!) {
  user(login: $login) {
    createdAt
    contributionsCollection {
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
QUERY_WINDOW = """
query ($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      totalRepositoryContributions
      commitContributionsByRepository(maxRepositories: 100) {
        repository { nameWithOwner stargazerCount owner { login } }
        contributions { totalCount }
      }
    }
  }
}
"""


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def f2(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def shade(hex_color, factor):
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % tuple(min(255, round(c * factor)) for c in (r, g, b))


def luminance(hex_color):
    h = hex_color.lstrip("#")
    chan = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in chan]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def best_text(bg):
    return "#ffffff" if contrast("#ffffff", bg) >= contrast("#0d1117", bg) else "#0d1117"


def text_width(s, size):
    narrow = sum(c in "iljtfrI.,:;'|! " for c in s)
    wide = sum(c in "MWmw@%" for c in s)
    return size * (0.58 * len(s) - 0.22 * narrow + 0.20 * wide)


def clip(s, n=16):
    return s if len(s) <= n else s[:n - 1] + "…"


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


def lang_color(info, rank):
    return info["color"] or NULL_LANG[rank % len(NULL_LANG)]


def theme_for(palette, mode):
    return {**BASE[mode], "cells": PALETTES[palette][mode]}


def post(token, query, **variables):
    body = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(API, data=body, headers={
        "Authorization": f"bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "profile-gen",
    })
    for attempt in range(4):
        try:
            payload = json.loads(urllib.request.urlopen(req, timeout=30).read())
            break
        except (urllib.error.URLError, TimeoutError) as e:
            code = getattr(e, "code", 503)
            if attempt == 3 or code not in (429, 500, 502, 503, 504):
                raise
            time.sleep(2 ** attempt)
    if "errors" in payload:
        raise SystemExit("graphql: " + json.dumps(payload["errors"]))
    return payload["data"]["user"]


def year_windows(created_at, now=None):
    start = datetime.datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    now = now or datetime.datetime.now(datetime.timezone.utc)
    step, tick = datetime.timedelta(days=365), datetime.timedelta(seconds=1)
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    out, cur = [], start
    while cur <= now:
        out.append((cur.strftime(fmt), min(cur + step - tick, now).strftime(fmt)))
        cur += step
    return out


def shape(main, windows, login):
    cal = main["contributionsCollection"]["contributionCalendar"]
    weeks = [[{"level": LEVELS[d["contributionLevel"]], "count": d["contributionCount"],
               "weekday": d["weekday"]} for d in w["contributionDays"]]
             for w in cal["weeks"]]

    langs = {}
    nodes = main["repositories"]["nodes"]
    if len(nodes) >= 100:
        print("WARNING: hit the 100-repo cap, language totals are short")
    for node in nodes:
        for edge in node["languages"]["edges"]:
            entry = langs.setdefault(edge["node"]["name"],
                                     {"size": 0, "color": edge["node"]["color"]})
            entry["size"] += edge["size"]

    radar = dict.fromkeys(["Commit", "Issue", "PullReq", "Review", "Repo"], 0)
    keys = ["totalCommitContributions", "totalIssueContributions",
            "totalPullRequestContributions", "totalPullRequestReviewContributions",
            "totalRepositoryContributions"]
    repos = {}
    for w in windows:
        cc = w["contributionsCollection"]
        for name, key in zip(radar, keys):
            radar[name] += cc[key]
        by_repo = cc["commitContributionsByRepository"]
        if len(by_repo) >= 100:
            print("WARNING: hit the 100-repo cap on commitContributionsByRepository, "
                  "panel may be short")
        for r in by_repo:
            full = r["repository"]["nameWithOwner"]
            entry = repos.setdefault(full, {"name": full,
                                            "owner": r["repository"]["owner"]["login"],
                                            "count": 0})
            entry["count"] += r["contributions"]["totalCount"]
            entry["stars"] = r["repository"]["stargazerCount"]

    ordered = sorted(repos.values(), key=lambda r: (-r["stars"], -r["count"], r["name"].lower()))
    external = [r for r in ordered if r["owner"].lower() != login.lower()]

    return {
        "total": cal["totalContributions"],
        "weeks": weeks,
        "panel": external,
        "external_count": len(external),
        "langs": sorted(langs.items(), key=lambda kv: -kv[1]["size"]),
        "radar": radar,
        "repos": main["repositories"]["totalCount"],
    }


def grid_box(key, weeks):
    s = SOURCES[key]
    ox, oy = s["origin"]
    return ox, oy, (weeks - 1) * s["pitch"] + s["cell"], 6 * s["pitch"] + s["cell"]


def root_tag(svg):
    return re.search(r"""<svg(?:"[^"]*"|'[^']*'|[^"'>])*>""", svg).group(0)


def parse_viewbox(svg):
    head = root_tag(svg)
    m = re.search(r"""\bviewBox=["']\s*([-\d.]+)[ ,]+([-\d.]+)[ ,]+([-\d.]+)[ ,]+([-\d.]+)""",
                  head)
    if m:
        return tuple(float(g) for g in m.groups())
    w = re.search(r"""\bwidth=["']([\d.]+)""", head)
    h = re.search(r"""\bheight=["']([\d.]+)""", head)
    if not (w and h):
        raise SystemExit("tile SVG has neither a viewBox nor width/height")
    return 0.0, 0.0, float(w.group(1)), float(h.group(1))


def tile_box(boxes, vbs):
    L = R = T = B = gh = 0.0
    for key, (gx, gy, gw, gz) in boxes.items():
        vx, vy, vw, vh = vbs[key]
        k = GRID_W / gw
        L = max(L, (gx - vx) * k)
        R = max(R, (vx + vw - gx - gw) * k)
        T = max(T, (gy - vy) * k)
        B = max(B, (vy + vh - gy - gz) * k)
        gh = max(gh, gz * k)
    return {"L": L, "T": T, "w": L + GRID_W + R, "h": T + gh + B}


def retile(svg, key, weeks, box):
    gx, gy, gw, _ = grid_box(key, weeks)
    k = GRID_W / gw
    vb = (gx - box["L"] / k, gy - box["T"] / k, box["w"] / k, box["h"] / k)
    head = root_tag(svg)
    start = svg.index(head)
    stripped = re.sub(r"""\s+(viewBox|width|height|preserveAspectRatio)=("[^"]*"|'[^']*')""",
                      "", head[:-1])
    stripped += (f' viewBox="{f2(vb[0])} {f2(vb[1])} {f2(vb[2])} {f2(vb[3])}"'
                 f' width="{f2(box["w"])}" height="{f2(box["h"])}"'
                 ' preserveAspectRatio="xMidYMid meet" data-retiled="1">')
    body = re.sub(r'<rect width="100%" height="100%"[^>]*/>', "", svg[start + len(head):],
                  count=1)
    return svg[:start] + stripped + body


def badge_svg(label, value, theme, accent, icon="", dot="", style="raised"):
    FS, H, P, R = 11, 26, 9, 6
    ico = 17 if (icon or dot) else 0
    lw = (text_width(label, FS) if label else 0) + P * 2 + ico
    vw = text_width(value, FS) + P * 2
    W = lw + vw
    mid = H / 2 + 4

    defs, under, over = [], [], []
    lab_fill = theme["muted"]
    val_fill = best_text(shade(accent, 0.94))

    if style == "raised":
        defs.append(f'<linearGradient id="gl" x1="0" y1="0" x2="0" y2="1">'
                    f'<stop offset="0" stop-color="{theme["line"]}"/>'
                    f'<stop offset="1" stop-color="{shade(theme["line"], 0.72)}"/></linearGradient>'
                    f'<linearGradient id="gv" x1="0" y1="0" x2="0" y2="1">'
                    f'<stop offset="0" stop-color="{shade(accent, 1.28)}"/>'
                    f'<stop offset="1" stop-color="{accent}"/></linearGradient>')
        under.append(f'<rect y="2" width="{f2(W)}" height="{H - 2}" rx="{R}" '
                     f'fill="{shade(accent, 0.45)}"/>')
        under.append(f'<rect width="{f2(lw + R)}" height="{H - 2}" rx="{R}" fill="url(#gl)"/>')
        under.append(f'<path d="M{f2(lw)} 0h{f2(vw - R)}a{R} {R} 0 0 1 {R} {R}v{H - 2 - 2 * R}'
                     f'a{R} {R} 0 0 1 -{R} {R}h-{f2(vw - R)}z" fill="url(#gv)"/>')
        over.append(f'<path d="M{R} 0.5h{f2(W - 2 * R)}" stroke="#ffffff" '
                    f'stroke-opacity="0.28"/>')
    elif style == "gradient":
        defs.append(f'<linearGradient id="gv" x1="0" y1="0" x2="1" y2="1">'
                    f'<stop offset="0" stop-color="{shade(accent, 1.25)}"/>'
                    f'<stop offset="1" stop-color="{shade(accent, 0.62)}"/></linearGradient>')
        under.append(f'<rect width="{f2(W)}" height="{H}" rx="{R}" fill="{theme["line"]}"/>')
        under.append(f'<path d="M{f2(lw)} 0h{f2(vw - R)}a{R} {R} 0 0 1 {R} {R}v{H - 2 * R}'
                     f'a{R} {R} 0 0 1 -{R} {R}h-{f2(vw - R)}z" fill="url(#gv)"/>')
    else:
        under.append(f'<rect x="0.5" y="0.5" width="{f2(W - 1)}" height="{H - 1}" rx="{R}" '
                     f'fill="none" stroke="{accent}"/>')
        under.append(f'<path d="M{f2(lw)} 0.5v{H - 1}" stroke="{accent}"/>')
        val_fill = accent

    mark = ""
    if icon:
        ix = P if label else (lw - 12) / 2
        mark = (f'<g transform="translate({f2(ix)},{(H - 12) / 2}) scale(0.5)" fill="none" '
                f'stroke="{lab_fill}" stroke-width="2.4" stroke-linecap="round" '
                f'stroke-linejoin="round">{ICONS[icon]}</g>')
    elif dot:
        mark = f'<circle cx="{P + 4}" cy="{H / 2}" r="4" fill="{dot}"/>'

    lab = (f'<text x="{f2(P + ico)}" y="{f2(mid)}" font-family="{FONT}" font-size="{FS}" '
           f'fill="{lab_fill}">{esc(label)}</text>' if label else "")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H}" \
viewBox="0 0 {f2(W)} {H}" role="img" aria-label="{esc(label or icon)}: {esc(value)}">
<defs>{"".join(defs)}</defs>{"".join(under)}{mark}{lab}{"".join(over)}
<text x="{f2(lw + P)}" y="{f2(mid)}" font-family="{FONT}" font-size="{FS}" \
fill="{val_fill}" font-weight="600">{esc(value)}</text>
</svg>"""


def link_badges(theme, accent):
    return {
        "badge-email.svg": badge_svg("", EMAIL, theme, accent, icon="mail", style="outline"),
        "badge-site.svg": badge_svg("", SITE, theme, accent, icon="globe", style="outline"),
    }


def badges(data, theme, accent):
    out = {"badge-repos.svg": badge_svg("contributed in", f"{data['external_count']} repos",
                                        theme, accent, icon="pr", style="raised")}
    langs = data["langs"][:4]
    for rank in range(1, 5):
        if rank <= len(langs):
            name, info = langs[rank - 1]
            colour = lang_color(info, rank - 1)
            svg = badge_svg(name.lower(), human_bytes(info["size"]), theme, colour,
                            dot=colour, style="gradient")
        else:
            svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1" '
                   'viewBox="0 0 1 1" role="presentation"></svg>')
        out[f"badge-lang-{rank}.svg"] = svg
    return out


def grid_svg(weeks, theme):
    s = SOURCES["grid"]
    cell, pitch, pad = s["cell"], s["pitch"], s["origin"][0]
    n = len(weeks)
    W = n * pitch - (pitch - cell) + pad * 2
    H = 7 * pitch - (pitch - cell) + pad * 2

    cells, css = [], []
    for x, week in enumerate(weeks):
        pct = round(x / max(1, n - 1) * 60, 2)
        css.append(f"@keyframes k{x}{{0%,{pct}%{{opacity:0}}{min(pct + 4, 100)}%,100%"
                   f"{{opacity:1}}}}.w{x}{{animation-name:k{x}}}")
        for day in week:
            cells.append(f'<rect class="c w{x}" x="{pad + x * pitch}" '
                         f'y="{pad + day["weekday"] * pitch}" width="{cell}" height="{cell}" '
                         f'rx="2" fill="{theme["cells"][day["level"]]}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" '
            f'height="{H}" role="img" aria-label="contribution calendar">'
            f'<style>.c{{animation-duration:4200ms;animation-timing-function:ease-out;'
            f'animation-iteration-count:1;animation-fill-mode:both}}{"".join(css)}</style>'
            f'{"".join(cells)}</svg>')


def face_pattern(pid, pat, bg, fg):
    width, bitmap = pat
    d = "".join(f"M{x} {y}h1v1h-1z" for y, bits in enumerate(bitmap) for x in range(width)
                if bits & (1 << (width - x - 1)))
    return (f'<pattern id="{pid}" x="0" y="0" width="{width}" height="{len(bitmap)}" '
            f'patternUnits="userSpaceOnUse">'
            f'<rect width="{width}" height="{len(bitmap)}" fill="{bg}"/>'
            f'<path fill="{fg}" d="{d}"/></pattern>')


def blocks_svg(data, theme):
    c, weeks = theme["cells"], data["weeks"]
    n = len(weeks)
    W, K = BLOCK_W, BLOCK_W / 1280
    dx = W / 64
    dy = dx * math.tan(math.radians(ANGLE))
    dxx, dyy = dx * 0.9, dy * 0.9

    tallest = max((d["count"] for wk in weeks for d in wk), default=0)
    head = math.ceil(math.log10(tallest / 20 + 1) * 144 + 3) + 14
    foot = round(46 * K) + 18
    off_x, off_y = dx * 7, float(head)
    H = math.ceil(off_y + (n + 5) * dy + foot)

    defs = []
    for lvl in range(5):
        top, stud = c[lvl], shade(c[lvl], 0.5 if lvl else 1.6)
        defs.append(face_pattern(f"p{lvl}t", GITBLOCK_TOP, top, stud))
        defs.append(face_pattern(f"p{lvl}l", GITBLOCK_SIDE, shade(top, 0.84), shade(stud, 0.84)))
        defs.append(face_pattern(f"p{lvl}r", GITBLOCK_SIDE, shade(top, 0.70), shade(stud, 0.70)))

    tw, sw = GITBLOCK_TOP[0], GITBLOCK_SIDE[0]
    s_top = dxx / tw
    s_side = math.hypot(dxx, dyy) / sw
    skew_x = math.degrees(math.atan(dxx / 2 / dyy))

    bars = []
    for week, days in enumerate(weeks):
        for day in days:
            dow, lvl = day["weekday"], day["level"]
            h = math.log10(day["count"] / 20 + 1) * 144 + 3
            bx = off_x + (week - dow) * dx
            by = off_y + (week + dow) * dy
            grow = rise = ""
            if lvl:
                grow = (f'<animateTransform attributeName="transform" type="translate" '
                        f'values="{f2(bx)} {f2(by - 3)};{f2(bx)} {f2(by - h)}" dur="3s" '
                        f'repeatCount="1"/>')
                rise = (f'<animate attributeName="height" '
                        f'values="{f2(3 / s_side)};{f2(h / s_side)}" dur="3s" repeatCount="1"/>')
            bars.append(
                f'<g transform="translate({f2(bx)} {f2(by - h)})">{grow}'
                f'<rect width="{tw}" height="{tw}" fill="url(#p{lvl}t)" '
                f'transform="skewY({-ANGLE}) skewX({f2(skew_x)}) '
                f'scale({s_top:.4f} {2 * dyy / tw:.4f})"/>'
                f'<rect width="{sw}" height="{f2(h / s_side)}" fill="url(#p{lvl}l)" '
                f'transform="skewY({ANGLE}) scale({dxx / sw:.4f} {s_side:.4f})">{rise}</rect>'
                f'<rect width="{sw}" height="{f2(h / s_side)}" fill="url(#p{lvl}r)" '
                f'transform="translate({f2(dxx)} {f2(dyy)}) skewY({-ANGLE}) '
                f'scale({dxx / sw:.4f} {s_side:.4f})">{rise}</rect></g>')

    bottom, big, small = H - 20 * K, 32 * K, 24 * K
    n_total, n_repos = f"{data['total']:,}", f"{data['repos']:,}"
    label_total, label_repos = "contributions in the last year", "public repos"
    x0 = (W - (text_width(n_total, big) + 8 * K + text_width(label_total, small) + 60 * K
               + 42 * K + text_width(n_repos, big) + 8 * K + text_width(label_repos, small))) / 2
    x_label = x0 + text_width(n_total, big) + 8 * K
    x_icon = x_label + text_width(label_total, small) + 60 * K
    x_repos = x_icon + 42 * K
    x_label2 = x_repos + text_width(n_repos, big) + 8 * K

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" \
font-family="{FONT}" role="img" aria-label="{data['total']} contributions in the last year as 3d blocks">
<defs>{"".join(defs)}</defs>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" fill="{theme['card']}" stroke="{theme['line']}"/>
{"".join(bars)}
<text x="{f2(x0)}" y="{f2(bottom)}" font-size="{f2(big)}" font-weight="bold" fill="{theme['fg']}">{n_total}</text>
<text x="{f2(x_label)}" y="{f2(bottom)}" font-size="{f2(small)}" fill="{theme['muted']}">{label_total}</text>
<g transform="translate({f2(x_icon)} {f2(bottom - 28 * K)}) scale({f2(2 * K)})">\
<path fill-rule="evenodd" d="{OCTI_REPO}" fill="{theme['fg']}"/></g>
<text x="{f2(x_repos)}" y="{f2(bottom)}" font-size="{f2(big)}" font-weight="bold" fill="{theme['fg']}">{n_repos}</text>
<text x="{f2(x_label2)}" y="{f2(bottom)}" font-size="{f2(small)}" fill="{theme['muted']}">{label_repos}</text>
</svg>"""


def radar_svg(data, theme, accent):
    w, h = RADAR_W, RADAR_H
    lv_n = len(RANGE)
    radius, cx, cy = (h / 2) * 0.8, w / 2, (h / 2) * 1.1
    items = list(data["radar"].items())
    n = len(items)

    def px(level, i):
        return f2(radius * (level / lv_n) * math.sin(i / n * math.tau))

    def py(level, i):
        return f2(radius * (level / lv_n) * -math.cos(i / n * math.tau))

    def to_level(v):
        return 0.8 if v < 1 else min(math.log10(v), 4) + 1

    dash = f'stroke="{theme["muted"]}" stroke-dasharray="4 4" stroke-width="1"'
    web = []
    for j in range(1, lv_n + 1):
        for i in range(n):
            web.append(f'<line x1="{px(j, i)}" y1="{py(j, i)}" x2="{px(j, i + 1)}" '
                       f'y2="{py(j, i + 1)}" {dash}/>')
    for i, label in enumerate(RANGE):
        web.append(f'<text x="{f2(radius / 50)}" y="{f2(-radius * ((i + 1) / lv_n))}" '
                   f'font-size="{f2(radius / 12)}" fill="{theme["muted"]}">{label}</text>')
    for i, (name, value) in enumerate(items):
        web.append(f'<line x1="{px(1, i)}" y1="{py(1, i)}" x2="{px(lv_n, i)}" '
                   f'y2="{py(lv_n, i)}" {dash}/>'
                   f'<text x="{px(1.25 * lv_n, i)}" y="{py(1.17 * lv_n, i)}" '
                   f'font-size="{f2(radius / 7.5)}" text-anchor="middle" '
                   f'dominant-baseline="middle" fill="{theme["fg"]}">{esc(name)}'
                   f'<title>{value}</title></text>')

    pts = " ".join(f"{px(to_level(v), i)},{py(to_level(v), i)}"
                   for i, (_, v) in enumerate(items))
    pts0 = " ".join(f"{px(0.8, i)},{py(0.8, i)}" for i in range(n))

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" \
font-family="{FONT}" role="img" aria-label="contributions by kind, all time">
<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="14" fill="{theme['card']}" stroke="{theme['line']}"/>
<g transform="translate({f2(cx)} {f2(cy)})">{"".join(web)}
<polygon points="{pts}" fill="{accent}" fill-opacity="0.5" stroke="{accent}" stroke-width="4">
<animate attributeName="points" values="{pts0};{pts}" dur="3s" repeatCount="1"/></polygon>
</g></svg>"""


def pie_svg(data, theme):
    w, h = PIE_W, PIE_H
    top = [(name, info["size"], lang_color(info, i))
           for i, (name, info) in enumerate(data["langs"][:5])]
    rest = sum(info["size"] for _, info in data["langs"][5:])
    if rest > 0:
        top.append(("other", rest, "#444444"))
    total = sum(size for _, size, _ in top) or 1

    radius = h / 2
    ro, ri = radius - radius / 10, radius / 2
    row, steps = 8, 5
    offset = (row - len(top)) / 2 + 0.5
    fs = h / row / 1.5

    def anim(i):
        values = ";".join(str(0 if j < i else min((j - i) / steps, 1))
                          for j in range(len(top) + steps))
        return f'<animate attributeName="fill-opacity" values="{values}" dur="3s" repeatCount="1"/>'

    def pt(r, a):
        return f"{r * math.sin(a):.2f} {-r * math.cos(a):.2f}"

    arcs, keys, angle = [], [], 0.0
    for i, (name, size, colour) in enumerate(top):
        a0 = angle
        angle += size / total * math.tau
        a1 = min(angle, a0 + math.tau - 1e-4)
        big = 1 if a1 - a0 > math.pi else 0
        d = (f"M{pt(ro, a0)}A{ro} {ro} 0 {big} 1 {pt(ro, a1)}"
             f"L{pt(ri, a1)}A{ri} {ri} 0 {big} 0 {pt(ri, a0)}Z")
        arcs.append(f'<path d="{d}" fill="{colour}" stroke="{theme["card"]}" stroke-width="2">'
                    f'<title>{esc(name)} {human_bytes(size)}</title>{anim(i)}</path>')
        ly = (i + offset) * (h / row)
        keys.append(f'<rect x="0" y="{f2(ly - fs / 2)}" width="{f2(fs)}" height="{f2(fs)}" '
                    f'fill="{colour}" stroke="{theme["card"]}">{anim(i)}</rect>'
                    f'<text x="{f2(fs * 1.2)}" y="{f2(ly)}" dominant-baseline="middle" '
                    f'font-size="{f2(fs)}" fill="{theme["fg"]}">{esc(clip(name))}'
                    f'<title>{esc(name)}</title>{anim(i)}</text>')

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" \
font-family="{FONT}" role="img" aria-label="languages by size">
<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="14" fill="{theme['card']}" stroke="{theme['line']}"/>
<g transform="translate({f2(radius * 2.1)} 0)">{"".join(keys)}</g>
<g transform="translate({f2(radius)} {f2(radius)})">{"".join(arcs)}</g></svg>"""


def panel_html(data):
    rows = []
    for r in data["panel"][:TOP_REPOS]:
        url = f"https://github.com/{esc(r['name'])}"
        src = f"https://github.com/{esc(r['owner'])}.png?size=64"
        stars = f' ⭐ {human_count(r["stars"])}' if r.get("stars") else ""
        rows.append(f'<tr><td width="34"><a href="{url}"><img src="{src}" width="26" height="26" '
                    f'align="absmiddle" alt=""></a></td><td><a href="{url}">{esc(r["name"])}</a>'
                    f'{stars}</td><td align="right">{r["count"]}</td></tr>')
    if not rows:
        rows.append('<tr><td colspan="3">no external contributions yet</td></tr>')
    return (f"{PANEL_START}\n"
            f'<table>\n<tr><td colspan="2"><sub><b>CONTRIBUTED IN</b></sub></td>'
            f'<td align="right"><sub>commits, all time</sub></td></tr>\n'
            + "\n".join(rows) + f"\n</table>\n{PANEL_END}")


def write_panel(block):
    with README.open("r", encoding="utf-8", newline="") as fh:
        old = fh.read()
    if PANEL_START not in old or PANEL_END not in old:
        raise SystemExit(f"README.md has no {PANEL_START} ... {PANEL_END} block")
    if old.index(PANEL_END) < old.index(PANEL_START):
        raise SystemExit(f"README.md has {PANEL_END} before {PANEL_START}")
    pattern = re.escape(PANEL_START) + r".*?" + re.escape(PANEL_END)
    new, count = re.subn(pattern, lambda _: block, old, flags=re.S)
    if count != 1:
        raise SystemExit(f"README.md panel block matched {count} times, expected 1")
    if new == old:
        return False
    with README.open("w", encoding="utf-8", newline="") as fh:
        fh.write(new)
    return True


def build(data, palette):
    files = {}
    for mode in ("dark", "light"):
        t = theme_for(palette, mode)
        accent, ink = PALETTES[palette][mode][3], PALETTES[palette][mode][4]
        sfx = "" if mode == "dark" else "-light"
        files[f"grid{sfx}.svg"] = grid_svg(data["weeks"], t)
        files[f"blocks{sfx}.svg"] = blocks_svg(data, t)
        files[f"radar{sfx}.svg"] = radar_svg(data, t, ink)
        files[f"pie{sfx}.svg"] = pie_svg(data, t)
        links = link_badges(BASE[mode], accent if mode == "dark" else ink)
        for name, svg in {**badges(data, BASE[mode], accent), **links}.items():
            files[name.replace(".svg", f"{sfx}.svg")] = svg
    return files


def retile_all(weeks_n):
    missing = [f for files in TILES.values() for f in files if not (OUT / f).exists()]
    if missing:
        raise SystemExit(f"retile: missing {', '.join(missing)} in {OUT}/, "
                         "every tile needs a dark and a light file")
    expected = {f for files in TILES.values() for f in files}
    expected |= {f"{c}{sfx}.svg" for c in CARDS for sfx in ("", "-light")}
    stray = sorted(p.name for p in OUT.iterdir() if p.name not in expected)
    if stray:
        raise SystemExit(f"retile: unexpected files in {OUT}/: {', '.join(stray)}")
    for key, files in TILES.items():
        if 'data-retiled="1"' in (OUT / files[0]).read_text():
            raise SystemExit(f"retile: {files[0]} is already retiled, start from a clean dist/")

    vbs = {k: parse_viewbox((OUT / v[0]).read_text()) for k, v in TILES.items()}
    boxes = {k: grid_box(k, weeks_n) for k in TILES}
    box = tile_box(boxes, vbs)
    print(f"tile window {box['w']:.1f} x {box['h']:.1f}, calendar {GRID_W:.0f} wide")
    for key, files in TILES.items():
        for f in files:
            path = OUT / f
            path.write_text(retile(path.read_text(), key, weeks_n, box))
            print(f"retiled {f}")


def main():
    OUT.mkdir(exist_ok=True)
    if "--retile" in sys.argv:
        return retile_all(int(os.environ.get("WEEKS", "53")))

    palette = os.environ.get("CARD_PALETTE", "blueprint-amber")
    login = os.environ["GITHUB_REPOSITORY_OWNER"]
    token = os.environ["GITHUB_TOKEN"]

    main_data = post(token, QUERY_MAIN, login=login)
    windows = [post(token, QUERY_WINDOW, login=login, **{"from": a, "to": b})
               for a, b in year_windows(main_data["createdAt"])]
    print(f"{login}: joined {main_data['createdAt'][:10]}, {len(windows)} year windows")

    data = shape(main_data, windows, login)
    print(f"{data['total']} contributions this year, {data['external_count']} external repos, "
          f"{len(data['langs'])} languages, {data['repos']} public repos")
    print("all time: " + ", ".join(f"{k} {v}" for k, v in data["radar"].items()))

    for name, svg in build(data, palette).items():
        (OUT / name).write_text(svg)
        print(f"{name:22} {len(svg) // 1024:>4} KB")

    print("README panel " + ("updated" if write_panel(panel_html(data)) else "unchanged"))

    weeks = len(data["weeks"])
    print(f"WEEKS={weeks}")
    if env_file := os.environ.get("GITHUB_ENV"):
        with open(env_file, "a") as fh:
            fh.write(f"WEEKS={weeks}\n")


if __name__ == "__main__":
    main()
