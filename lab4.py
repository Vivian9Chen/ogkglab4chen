import os
import re
from collections import deque
from PIL import Image, ImageDraw

W, H = 960, 540

def read_points(path):
    pts = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = re.split(r"[,\s]+", line)
            if len(parts) < 2:
                continue
            try:
                pts.append((int(parts[0]), int(parts[1])))
            except ValueError:
                continue
    return pts

def connected_components(points):
    S = set((x, y) for x, y in points if 0 <= x < W and 0 <= y < H)
    visited = set()
    comps = []
    neigh = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
    for p in S:
        if p in visited:
            continue
        q = deque([p])
        visited.add(p)
        comp = []
        while q:
            x, y = q.popleft()
            comp.append((x, y))
            for dx, dy in neigh:
                np_ = (x + dx, y + dy)
                if np_ in S and np_ not in visited:
                    visited.add(np_)
                    q.append(np_)
        comps.append(comp)
    return comps

def centroids(components):
    centers = []
    for comp in components:
        sx = 0
        sy = 0
        for x, y in comp:
            sx += x
            sy += y
        centers.append((sx / len(comp), sy / len(comp)))
    return centers

def to_img(x, y):
    return int(x), int((H - 1) - y)

def main():
    base = os.path.dirname(os.path.abspath(__file__))
    in_path = os.path.join(base, "DS5.txt")
    out_img = os.path.join(base, "result_voronoi.png")
    out_centers = os.path.join(base, "centers.txt")

    pts = read_points(in_path)
    comps = connected_components(pts)
    centers = centroids(comps)

    with open(out_centers, "w", encoding="utf-8") as f:
        for cx, cy in centers:
            f.write(f"{cx:.6f} {cy:.6f}\n")

    img = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(img)

    for x, y in pts:
        if 0 <= x < W and 0 <= y < H:
            xi, yi = to_img(x, y)
            draw.point((xi, yi), fill=(230, 230, 230))

    if len(centers) > 0:
        owner = [[-1] * W for _ in range(H)]
        for y in range(H):
            for x in range(W):
                best = 0
                best_d = (x - centers[0][0]) ** 2 + (y - centers[0][1]) ** 2
                for i in range(1, len(centers)):
                    dx = x - centers[i][0]
                    dy = y - centers[i][1]
                    d = dx * dx + dy * dy
                    if d < best_d:
                        best_d = d
                        best = i
                owner[y][x] = best

        for y in range(H - 1):
            for x in range(W - 1):
                if owner[y][x] != owner[y][x + 1] or owner[y][x] != owner[y + 1][x]:
                    draw.point((x, y), fill=(0, 0, 255))

    r = 2
    for cx, cy in centers:
        if 0 <= cx < W and 0 <= cy < H:
            xi, yi = to_img(cx, cy)
            draw.ellipse([xi - r, yi - r, xi + r, yi + r], outline=(0, 0, 255), width=1)

    img.save(out_img)

if __name__ == "__main__":
    main()