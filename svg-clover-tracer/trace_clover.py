#!/usr/bin/env python3
"""
trace_clover.py — SVG logo → CloverLoader.tsx pipeline
=======================================================
Converts a vectorized SVG logo (screenshot-traced or clean) into an animated
React CloverLoader component using potrace for silhouette tracing.

Requirements:
  brew install potrace
  pip install cairosvg pillow

Usage:
  python3 trace_clover.py input.svg
  python3 trace_clover.py input.svg --output-dir ./out --color '#62B77A' --preview
  python3 trace_clover.py input.svg --component-out ../src/ui/CloverLoader.tsx
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile


# ── Dependency checks ─────────────────────────────────────────────────────────

def check_dependencies():
    """Verify potrace, cairosvg, and pillow are available."""
    errors = []

    if subprocess.run(["which", "potrace"], capture_output=True).returncode != 0:
        errors.append("potrace not found — install with: brew install potrace")

    try:
        import cairosvg  # noqa: F401
    except ImportError:
        errors.append("cairosvg not found — install with: pip install cairosvg")

    try:
        from PIL import Image  # noqa: F401
    except ImportError:
        errors.append("pillow not found — install with: pip install pillow")

    if errors:
        print("❌ Missing dependencies:\n" + "\n".join(f"  • {e}" for e in errors))
        sys.exit(1)


# ── Step 1: SVG → PNG ─────────────────────────────────────────────────────────

def render_svg_to_png(svg_path: str, png_path: str, scale: int = 2) -> tuple[int, int]:
    """Render SVG to PNG at scale× resolution. Returns (width, height) of output."""
    import cairosvg

    # Read SVG to get native dimensions
    content = open(svg_path).read()
    w_match = re.search(r'width="([\d.]+)"', content)
    h_match = re.search(r'height="([\d.]+)"', content)
    native_w = float(w_match.group(1)) if w_match else 682
    native_h = float(h_match.group(1)) if h_match else 784

    out_w = int(native_w * scale)
    out_h = int(native_h * scale)

    cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=out_w, output_height=out_h)
    print(f"  ✓ Rendered PNG: {out_w}×{out_h}px → {png_path}")
    return out_w, out_h


# ── Step 2: PNG → binary BMP ──────────────────────────────────────────────────

def binarize_png(png_path: str, bmp_path: str) -> int:
    """Convert PNG to B&W BMP — green pixels → black, everything else → white.
    Returns the count of detected green (clover) pixels."""
    from PIL import Image

    img = Image.open(png_path).convert("RGBA")
    bw = Image.new("L", img.size, 255)
    pixels = img.load()
    bw_pixels = bw.load()
    w, h = img.size
    count = 0

    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            is_near_white = r > 220 and g > 220 and b > 220
            is_green = (
                a > 50
                and g > 100
                and g > r * 1.1
                and g > b * 1.05
                and not is_near_white
            )
            if is_green:
                bw_pixels[x, y] = 0
                count += 1

    bw.save(bmp_path)
    pct = 100 * count / (w * h)
    print(f"  ✓ Binarized: {count:,} green pixels ({pct:.1f}%) → {bmp_path}")
    return count


# ── Step 3: BMP → potrace SVG ─────────────────────────────────────────────────

def run_potrace(bmp_path: str, svg_path: str) -> str:
    """Run potrace to convert binary BMP to clean SVG. Returns the compound path string."""
    result = subprocess.run(
        [
            "potrace", "--svg",
            "--output", svg_path,
            "--turdsize", "30",
            "--alphamax", "1.0",
            "--opttolerance", "0.4",
            bmp_path,
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"❌ potrace failed:\n{result.stderr}")
        sys.exit(1)

    content = open(svg_path).read()
    paths = re.findall(r'd="([^"]+)"', content)
    if not paths:
        print("❌ potrace produced no paths")
        sys.exit(1)

    outer_path = " ".join(paths[0].replace("\n", " ").split())
    path_count = content.count("<path")
    print(f"  ✓ potrace → {path_count} path(s), {len(outer_path):,} chars → {svg_path}")
    return outer_path


# ── Step 4: Extract heart cutouts from original SVG ───────────────────────────

def extract_hearts(svg_path: str) -> list[dict]:
    """
    Extract the 4 inner heart paths from the original SVG.
    These are #FEFEFE-filled paths with translate() transforms (excluding background).
    Returns list of {translate, d} dicts sorted clockwise (top→right→bottom→left).
    """
    content = open(svg_path).read()

    matches = re.findall(
        r'<path d="([^"]+)" fill="#FEFEFE" transform="translate\(([^)]+)\)"[^/]*/>', content
    )

    hearts = []
    for d, trans in matches:
        trans = trans.strip()
        # Skip background rectangle (translate(0,0) with short path)
        if trans == "0,0" and len(d) < 200:
            continue
        d_clean = " ".join(d.split())
        hearts.append({"translate": trans, "d": d_clean})

    if not hearts:
        print("⚠️  No inner heart paths found (fill=#FEFEFE with translate). "
              "The SVG may not have separate heart paths — only the outer silhouette will be used.")
        return []

    # Sort clockwise: top → upper-right → lower-right → left
    def clockwise_key(h):
        parts = h["translate"].split(",")
        x, y = float(parts[0]), float(parts[1])
        if y < 200:
            return 0 if (300 < x < 450) else 1  # top=0, upper-right=1
        else:
            return 3 if x < 300 else 2  # left=3, lower-right=2

    hearts.sort(key=clockwise_key)
    print(f"  ✓ Extracted {len(hearts)} heart path(s):")
    for i, h in enumerate(hearts):
        print(f"    [{i}] translate({h['translate']}), delay={i}s, {len(h['d']):,} chars")

    return hearts


# ── Step 5: Generate CloverLoader.tsx ─────────────────────────────────────────

def generate_tsx(outer_path: str, hearts: list[dict], color: str, bg_color: str) -> str:
    """Generate the full CloverLoader.tsx component source."""
    outer_js = json.dumps(outer_path)

    if hearts:
        hearts_lines = "\n".join(
            f"  {{ translate: {json.dumps(h['translate'])}, d: {json.dumps(h['d'])} }},"
            for h in hearts
        )
        hearts_block = f"[{{\n{hearts_lines}\n}}]"  # unused — see below
        hearts_array = (
            "const HEARTS: { translate: string; d: string }[] = [\n"
            + "\n".join(
                f"  {{ translate: {json.dumps(h['translate'])}, d: {json.dumps(h['d'])} }},"
                for h in hearts
            )
            + "\n];"
        )
        hearts_section = hearts_array
        hearts_render = """
      {/* Heart cutouts — initially bgColor, beat sequentially to color */}
      {HEARTS.map(({ translate, d }, i) => (
        <g key={i} transform={`translate(${translate})`}>
          <path
            d={d}
            className={`clover-heart-${animId}`}
            fill={bgColor}
            style={{ animationDelay: `${i}s` }}
          />
        </g>
      ))}"""
        animation_style = f"""
        @keyframes clover-heart-${{animId}} {{
          0%    {{ fill: ${{bgColor}}; }}
          12.5% {{ fill: ${{color}}; }}
          23%   {{ fill: ${{color}}; }}
          25%   {{ fill: ${{bgColor}}; }}
          100%  {{ fill: ${{bgColor}}; }}
        }}
        .clover-heart-${{animId}} {{
          animation: clover-heart-${{animId}} 4s ease-in-out infinite;
        }}"""
    else:
        # Fallback: no hearts — use petal opacity animation
        hearts_section = ""
        hearts_render = ""
        animation_style = f"""
        @keyframes clover-leaf-${{animId}} {{
          0%    {{ opacity: 0.22; }}
          12.5% {{ opacity: 1; }}
          23%   {{ opacity: 1; }}
          25%   {{ opacity: 0.22; }}
          100%  {{ opacity: 0.22; }}
        }}
        .clover-petal-${{animId}} {{
          fill: {color};
          animation: clover-leaf-${{animId}} 4s ease-in-out infinite;
        }}"""

    tsx = f"""import React from 'react';

interface CloverLoaderProps {{
  size?: number;
  className?: string;
  color?: string;
  /** Background color — used as the "off" fill of each heart cutout. Default: white */
  bgColor?: string;
}}

// ── Real brand clover paths ──────────────────────────────────────────────────
// Generated by svg-clover-tracer. ViewBox: 0 0 682 784.
// Outer silhouette: potrace compound path (transform="translate(0,784) scale(0.05,-0.05)")
// Hearts: 4 inner cutouts from original SVG, clockwise from top (delay 0s/1s/2s/3s).

const OUTER_PATH: string =
  {outer_js};

{hearts_section}

/**
 * Animated four-leaf clover SVG loader using the real brand clover shape.
 * Each heart cutout fills in sequentially (bgColor → color → bgColor),
 * traversing the 4 leaves clockwise. Cycle: 4s, 1s per leaf.
 *
 * Generated by svg-clover-tracer — do not edit path data manually.
 */
export const CloverLoader: React.FC<CloverLoaderProps> = ({{
  size = 48,
  className = '',
  color = '{color}',
  bgColor = '{bg_color}',
}}) => {{
  const animId = React.useId().replace(/:/g, '_');

  return (
    <svg
      width={{size}}
      height={{Math.round(size * 784 / 682)}}
      viewBox="0 0 682 784"
      xmlns="http://www.w3.org/2000/svg"
      className={{className}}
      aria-label="Chargement"
      role="img"
    >
      <style>{{`{animation_style}
      `}}</style>

      {{/* Outer clover silhouette — potrace compound path */}}
      <g transform="translate(0,784) scale(0.05,-0.05)" fill={{color}} stroke="none">
        <path d={{OUTER_PATH}} />
      </g>
{hearts_render}
    </svg>
  );
}};
"""
    return tsx


# ── Step 6: Preview PNG ───────────────────────────────────────────────────────

def generate_preview(outer_path: str, hearts: list[dict], color: str, bg_color: str, png_path: str):
    """Generate a 5-state preview PNG showing all animation frames."""
    import cairosvg

    def make_state(active_idx):
        hearts_svg = "".join(
            f'<g transform="translate({h["translate"]})">'
            f'<path d="{h["d"]}" fill="{color if i == active_idx else bg_color}"/>'
            f'</g>'
            for i, h in enumerate(hearts)
        )
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 682 784" width="120" height="138">
  <g transform="translate(0,784) scale(0.05,-0.05)" fill="{color}" stroke="none">
    <path d="{outer_path}"/>
  </g>
  {hearts_svg}
</svg>'''

    labels = ["Base", "Feuille 1 (haut)", "Feuille 2", "Feuille 3", "Feuille 4"]
    n = 1 + len(hearts)
    total_w = n * 144
    combined = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_w} 200" width="{total_w}" height="200">'
    combined += f'<rect width="{total_w}" height="200" fill="#f5f5f5"/>'

    for col, active in enumerate([-1] + list(range(len(hearts)))):
        x = col * 144
        combined += f'<g transform="translate({x}, 8)">{make_state(active)}</g>'
        label = labels[col] if col < len(labels) else f"Feuille {col}"
        combined += f'<text x="{x + 60}" y="158" font-size="8" text-anchor="middle" fill="#666">{label}</text>'

    combined += "</svg>"

    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
        f.write(combined.encode())
        tmp = f.name

    cairosvg.svg2png(url=tmp, write_to=png_path, output_width=total_w, output_height=200)
    os.unlink(tmp)
    print(f"  ✓ Preview PNG → {png_path}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Convert a vectorized SVG logo into an animated CloverLoader.tsx React component."
    )
    parser.add_argument("input", help="Path to the source SVG file")
    parser.add_argument("--output-dir", default="./output", help="Directory for intermediate and output files (default: ./output)")
    parser.add_argument("--color", default="#62B77A", help="Clover fill color (default: #62B77A)")
    parser.add_argument("--bg-color", default="white", help="Heart background color (default: white)")
    parser.add_argument("--preview", action="store_true", help="Open preview PNG after generation")
    parser.add_argument("--component-out", default=None, help="If set, copy the generated CloverLoader.tsx to this path")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"❌ File not found: {args.input}")
        sys.exit(1)

    print("🔍 Checking dependencies...")
    check_dependencies()

    os.makedirs(args.output_dir, exist_ok=True)
    base = args.output_dir

    svg_in = os.path.abspath(args.input)
    png_path = os.path.join(base, "clover_render.png")
    bmp_path = os.path.join(base, "clover_binary.bmp")
    potrace_svg = os.path.join(base, "clover_clean.svg")
    preview_png = os.path.join(base, "clover_preview.png")
    tsx_out = os.path.join(base, "CloverLoader.tsx")

    print(f"\n📂 Source: {svg_in}")
    print(f"📂 Output: {os.path.abspath(base)}/\n")

    print("Step 1 — Render SVG → PNG")
    render_svg_to_png(svg_in, png_path)

    print("\nStep 2 — Binarize PNG")
    binarize_png(png_path, bmp_path)

    print("\nStep 3 — potrace → clean SVG")
    outer_path = run_potrace(bmp_path, potrace_svg)

    print("\nStep 4 — Extract heart cutouts")
    hearts = extract_hearts(svg_in)

    print("\nStep 5 — Generate CloverLoader.tsx")
    tsx = generate_tsx(outer_path, hearts, args.color, args.bg_color)
    with open(tsx_out, "w") as f:
        f.write(tsx)
    print(f"  ✓ CloverLoader.tsx → {tsx_out} ({len(tsx):,} chars)")

    print("\nStep 6 — Generate preview PNG")
    if hearts:
        generate_preview(outer_path, hearts, args.color, args.bg_color, preview_png)
    else:
        print("  ⚠️  Skipped (no hearts found)")
        preview_png = None

    if args.component_out:
        import shutil
        shutil.copy(tsx_out, args.component_out)
        print(f"\n  ✓ Copied → {args.component_out}")

    print("\n✅ Done!")
    print(f"   CloverLoader.tsx : {tsx_out}")
    if preview_png:
        print(f"   Preview PNG      : {preview_png}")

    if args.preview and preview_png:
        subprocess.run(["open", preview_png])


if __name__ == "__main__":
    main()
