"""XeFM frecency ジャンプ (~/.xefm/extensions/frecent_jump.py)

訪問したディレクトリを「頻度 × 新しさ」でスコア化して記録し、
filter ダイアログ（migemo 対応）から選んで現在のペインで開く。
標準の History / Favorites とは独立（互いに干渉しない）。
"""
import json
import os
import time

from frecent_jump.state import state_path

STORE = state_path("frecency.json")
MAX_ENTRIES = 2000

_data = None  # {path: [count, last_visit_epoch]}


def _load():
    global _data
    if _data is None:
        try:
            with open(STORE, encoding="utf-8") as f:
                _data = json.load(f)
        except Exception:
            _data = {}
    return _data


def _save():
    try:
        os.makedirs(os.path.dirname(STORE), exist_ok=True)
        with open(STORE, "w", encoding="utf-8") as f:
            json.dump(_data, f, ensure_ascii=False)
    except Exception:
        pass


def score(count, last, now=None):
    """zoxide 方式: 訪問回数に、最終訪問からの経過時間で重みを掛ける。"""
    age = (now or time.time()) - last
    if age < 3600:
        w = 4
    elif age < 86400:
        w = 2
    elif age < 7 * 86400:
        w = 0.5
    else:
        w = 0.25
    return count * w


def record(path):
    path = str(path)
    if path.endswith(":") or "://" in path:  # pttimer: 等の仮想フォルダは除外
        return
    data = _load()
    count, _ = data.get(path, [0, 0])
    data[path] = [count + 1, time.time()]
    if len(data) > MAX_ENTRIES:
        now = time.time()
        for p, _v in sorted(data.items(), key=lambda kv: score(*kv[1], now))[:200]:
            del data[p]
    _save()


# ---- XeFM 連携 -------------------------------------------------------------

def on_directory_changed(ctx, event):
    record(event.new_path)


def frecent_jump(ctx):
    data = _load()
    now = time.time()
    here = str(ctx.pane.path)
    ranked = sorted((p for p in data if p != here),
                    key=lambda p: score(*data[p], now), reverse=True)
    if not ranked:
        ctx.message("frecent-jump: まだ履歴がありません")
        return

    def on_result(index):
        if index is None:
            return
        target = ranked[index]
        if not os.path.isdir(target):          # 消えたフォルダは履歴から外す
            data.pop(target, None)
            _save()
            ctx.message(f"frecent-jump: 見つからないため履歴から削除: {target}")
            return
        ctx.pane.cd(target)

    ctx.choose("Frecent Directories", ranked, type="filter", on_result=on_result)
