#!/usr/bin/env python3
"""Hibonite Hook — neon sapphire swing-hook climber for ElbowOS. Python 3 + pygame."""
import math, os, random, subprocess, sys
from pathlib import Path

PLAY = "--play" in sys.argv
if not PLAY:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame

W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get("ELBOWOS_MP4", str(Path(__file__).resolve().parent / "HIBONITE_HOOK_ElbowOS.mp4"))
TITLE, HANDLE = "HIBONITE HOOK", "x.com/ElbowOS"
INK, TEAL, MINT, LIME, GOLD, CORAL, CREAM = (
    (22, 10, 6), (48, 118, 255), (150, 206, 255), (90, 230, 255),
    (255, 168, 64), (255, 92, 48), (255, 236, 214),
)

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        flags = 0 if PLAY else pygame.HIDDEN
        try:
            self.screen = pygame.display.set_mode((W, H), flags)
        except pygame.error:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            pygame.display.quit()
            pygame.display.init()
            self.screen = pygame.display.set_mode((W, H), pygame.HIDDEN)
        self.font = pygame.font.SysFont("DejaVu Sans", 64, bold=True)
        self.small = pygame.font.SysFont("DejaVu Sans", 36, bold=True)
        self.tiny = pygame.font.SysFont("DejaVu Sans", 28, bold=True)
        self.reset()

    def reset(self):
        self.t = 0
        self.score = 0
        self.combo = 1
        self.banner = "SWING"
        self.banner_t = 40
        self.hooks = []
        self.orbs = []
        self.sparks = []
        self.trail = []
        y = 520
        side = 1
        for i in range(18):
            x = 300 + side * 210 + (i % 3) * 18
            self.hooks.append({"x": x, "y": y, "hot": 0})
            self.orbs.append({"x": (x + 540) / 2 + side * 40, "y": y + 150, "alive": True})
            y += 300
            side *= -1
        self.anchor = self.hooks[0]
        self.attached = True
        self.angle = 0.55
        self.omega = 0.0
        self.length = 230
        self.vx = self.vy = 0.0
        self.px = self.anchor["x"] + math.sin(self.angle) * self.length
        self.py = self.anchor["y"] + math.cos(self.angle) * self.length
        self.cam = 0.0
        self.caught = 0
        random.seed(7)

    def gem_pos(self):
        if self.attached:
            self.px = self.anchor["x"] + math.sin(self.angle) * self.length
            self.py = self.anchor["y"] + math.cos(self.angle) * self.length
        return self.px, self.py

    def release(self):
        if not self.attached:
            return
        self.attached = False
        self.vx = math.cos(self.angle) * self.length * self.omega
        self.vy = -math.sin(self.angle) * self.length * self.omega
        self.banner, self.banner_t = "RELEASE", 18
        self.burst(self.px, self.py, LIME, 10)

    def try_catch(self):
        best, bd = None, 78
        for h in self.hooks:
            if h is self.anchor:
                continue
            d = math.hypot(h["x"] - self.px, h["y"] - self.py)
            if d < bd and h["y"] < self.py + 40:
                best, bd = h, d
        if not best:
            return
        dx, dy = self.px - best["x"], self.py - best["y"]
        self.angle = math.atan2(dx, dy)
        self.length = max(150, min(280, bd))
        # tangential speed becomes omega
        tx, ty = math.cos(self.angle), -math.sin(self.angle)
        self.omega = (self.vx * tx + self.vy * ty) / self.length
        self.anchor = best
        self.attached = True
        best["hot"] = 12
        self.caught += 1
        self.score += 100 * self.combo
        self.combo = min(8, self.combo + 1)
        self.banner, self.banner_t = f"HOOK x{self.combo}", 22
        self.burst(best["x"], best["y"], GOLD, 16)

    def burst(self, x, y, col, n):
        for _ in range(n):
            a = random.random() * math.tau
            s = random.uniform(2, 8)
            self.sparks.append([x, y, math.cos(a) * s, math.sin(a) * s, col, 18])

    def auto(self):
        nxt = None
        for h in self.hooks:
            if h["y"] > self.anchor["y"] + 80:
                nxt = h
                break
        if self.attached and nxt:
            toward = 1 if nxt["x"] > self.anchor["x"] else -1
            # release at the back of the swing so the kick flies toward the next hook
            if toward * self.angle < -0.35 and toward * self.omega > 0.012:
                self.release()
        elif not self.attached and self.vy > 0 and self.py > self.anchor["y"] + 180:
            self.try_catch()

    def step(self, keys=None):
        self.t += 1
        if keys is not None:
            if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
                if self.attached and self._pulse:
                    self.release()
            self._pulse = not (keys[pygame.K_SPACE] or keys[pygame.K_UP])
        else:
            self.auto()
        if self.attached:
            self.omega += -(0.42 / self.length) * math.sin(self.angle)
            self.omega *= 0.998
            self.angle += self.omega
            self.gem_pos()
        else:
            self.vy += 0.55
            self.px += self.vx
            self.py += self.vy
            self.vx *= 0.998
            if self.px < 120:
                self.px, self.vx = 120, abs(self.vx) * 0.7
            if self.px > W - 120:
                self.px, self.vx = W - 120, -abs(self.vx) * 0.7
            self.try_catch()
            if self.py > self.anchor["y"] + 720:
                self.combo = 1
                self.attached = True
                self.angle, self.omega = 0.4, 0
                self.banner, self.banner_t = "REHOOK", 20
        for o in self.orbs:
            if o["alive"] and math.hypot(o["x"] - self.px, o["y"] - self.py) < 46:
                o["alive"] = False
                self.score += 40 * self.combo
                self.burst(o["x"], o["y"], MINT, 12)
                self.banner, self.banner_t = "GEM", 16
        self.trail.append((self.px, self.py))
        self.trail = self.trail[-16:]
        for s in self.sparks:
            s[0] += s[2]
            s[1] += s[3]
            s[5] -= 1
        self.sparks = [s for s in self.sparks if s[5] > 0]
        target = self.py - 980
        self.cam += (target - self.cam) * 0.08
        if self.banner_t:
            self.banner_t -= 1

    def draw(self):
        surf = self.screen
        surf.fill(INK)
        cam = self.cam
        for i in range(14):
            yy = int((i * 160 - cam * 0.35) % (H + 160) - 80)
            pygame.draw.circle(surf, (48, 28, 16), (80 + (i * 97) % 900, yy), 50, 2)
        # cave walls
        pygame.draw.rect(surf, (62, 32, 16), (0, 0, 90, H))
        pygame.draw.rect(surf, (62, 32, 16), (W - 90, 0, 90, H))
        for i in range(22):
            sy = int(i * 110 - cam) % (H + 110) - 40
            pygame.draw.polygon(surf, CORAL, [(90, sy), (128, sy + 18), (90, sy + 36)])
            pygame.draw.polygon(surf, CORAL, [(W - 90, sy + 50), (W - 128, sy + 68), (W - 90, sy + 86)])
        for h in self.hooks:
            hy = h["y"] - cam
            if -80 < hy < H + 80:
                col = GOLD if h["hot"] else TEAL
                pygame.draw.circle(surf, col, (int(h["x"]), int(hy)), 28, 5)
                pygame.draw.circle(surf, CREAM, (int(h["x"]), int(hy)), 8)
                h["hot"] = max(0, h["hot"] - 1)
        for o in self.orbs:
            if not o["alive"]:
                continue
            oy = o["y"] - cam
            if -40 < oy < H + 40:
                pygame.draw.circle(surf, MINT, (int(o["x"]), int(oy)), 16)
                pygame.draw.circle(surf, CREAM, (int(o["x"]), int(oy)), 6)
        if len(self.trail) > 2:
            pts = [(int(x), int(y - cam)) for x, y in self.trail]
            pygame.draw.lines(surf, (70, 140, 255), False, pts, 6)
        ax, ay = self.anchor["x"], self.anchor["y"] - cam
        gx, gy = self.px, self.py - cam
        pygame.draw.line(surf, LIME, (int(ax), int(ay)), (int(gx), int(gy)), 4)
        gem = []
        for k in range(6):
            a = self.t * 0.08 + k * math.tau / 6
            gem.append((gx + math.cos(a) * 26, gy + math.sin(a) * 26))
        pygame.draw.polygon(surf, TEAL, gem)
        pygame.draw.polygon(surf, MINT, gem, 3)
        pygame.draw.circle(surf, CREAM, (int(gx), int(gy)), 7)
        for s in self.sparks:
            pygame.draw.circle(surf, s[4], (int(s[0]), int(s[1] - cam)), max(1, s[5] // 4))
        bar = pygame.Surface((W, 200), pygame.SRCALPHA)
        bar.fill((22, 10, 6, 190))
        surf.blit(bar, (0, 0))
        title = self.font.render(TITLE, True, LIME)
        surf.blit(title, title.get_rect(center=(W // 2, 78)))
        sc = self.small.render(f"SCORE  {self.score}", True, GOLD)
        surf.blit(sc, sc.get_rect(center=(W // 2, 142)))
        foot = pygame.Surface((W, 120), pygame.SRCALPHA)
        foot.fill((22, 10, 6, 190))
        surf.blit(foot, (0, H - 120))
        handle = self.small.render(HANDLE, True, CREAM)
        surf.blit(handle, handle.get_rect(center=(W // 2, H - 64)))
        if self.banner_t:
            b = self.tiny.render(self.banner, True, CORAL)
            surf.blit(b, b.get_rect(center=(W // 2, 188)))
        return surf

    def play_interactive(self):
        clock = pygame.time.Clock()
        self._pulse = True
        running = True
        while running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                    running = False
            self.step(pygame.key.get_pressed())
            self.draw()
            pygame.display.flip()
            clock.tick(FPS)
        pygame.quit()

    def record(self):
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
            "-preset", "veryfast", "-movflags", "+faststart", OUT,
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        frames = FPS * SECS
        try:
            for _ in range(frames):
                self.step()
                raw = pygame.image.tostring(self.draw(), "RGB")
                proc.stdin.write(raw)
        finally:
            proc.stdin.close()
        err = proc.stderr.read().decode("utf-8", "ignore")
        rc = proc.wait()
        if rc != 0:
            raise SystemExit(f"ffmpeg failed ({rc}):\n{err[-1200:]}")
        print("wrote", OUT)
        pygame.quit()

def main():
    g = Game()
    if PLAY:
        g.play_interactive()
    else:
        g.record()

if __name__ == "__main__":
    main()
