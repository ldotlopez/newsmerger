import os

PACKAGE_NAME = "newsmerger"

# Plain output (no colors, markup or progress bars) for cron, logs and pipes.
DISABLE_RICH = os.environ.get("DISABLE_RICH", "0").lower() not in ("0", "false", "")
