# Hibonite Hook

Full-colour Python 3 neon sapphire swing-hook arcade for ElbowOS.

Swing a sapphire gem on a rope through an umber spike shaft. Release at the back of the arc, catch the next copper ring, and scoop the ice orbs between hooks. Space / Up releases. Esc quits.

This is an original pendulum-hook game. It is not a Nintendo ROM, not an emulator, and it does not use trademarked characters.

## Play

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 hibonite_hook.py --play
```

Needs Python 3.10+ and a desktop window (pygame + SDL).

## Record a 9:16 reel

```bash
python3 hibonite_hook.py --record
```

Writes a 15 second 1080x1920 H.264 MP4 next to the script (libx264, yuv420p, CRF 20, +faststart). Headless runs use the SDL dummy video driver and still encode.

## Links

* Featured account: https://x.com/ElbowOS
* Drive reel: https://drive.google.com/file/d/1Ae93EPxAIIL5oMSImyWcVB7JJcfpLNaI/view?usp=drivesdk
* Repo: https://github.com/ApacheAde/elbowos-hibonite-hook
