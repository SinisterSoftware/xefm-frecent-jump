"""状態ファイルの置き場所 (~/.xefm/state/)

extensions/ はコード置き場にして、履歴・キャッシュ・ログなど実行時に書かれるファイルは
~/.xefm/state/ に集める (バックアップ・git 管理から外しやすい)。
以前 extensions/ に作られていた同名ファイルは、最初の呼び出しで自動的に移す。
"""
import shutil
from pathlib import Path

XEFM_DIR = Path.home() / ".xefm"
STATE_DIR = XEFM_DIR / "state"


def state_path(name: str) -> str:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    new = STATE_DIR / name
    old = XEFM_DIR / "extensions" / name
    if not new.exists() and old.exists():
        try:
            shutil.move(str(old), str(new))
        except OSError:
            pass                      # 移せなくても動く (新しく作り直されるだけ)
    return str(new)
