"""ARISE — Shadow Training. Servidor Flask + SQLite.

Rodar:  python app.py   (porta 5050, ou defina PORT)
"""
import json
import os
import secrets
import sqlite3
import threading
import time
import urllib.parse
from datetime import date, timedelta
import urllib.request
from functools import wraps

from flask import Flask, g, jsonify, request, send_from_directory, session, abort, Response
from werkzeug.security import check_password_hash, generate_password_hash

import game
from exercises import CHAINS, EXERCISE_BY_KEY, ALL_MISSIONS, PRENATAL_CHAINS

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE, "arise.db")
GIF_DIR = os.path.join(BASE, "cache", "gifs")
SNAPSHOT = os.path.join(BASE, "data", "exercisedb_bodyweight.json")
EXDB_API = "https://oss.exercisedb.dev/api/v1"
EXDB_MEDIA = "https://static.exercisedb.dev/media"
UA = {"User-Agent": "AriseTraining/1.0 (+self-hosted)"}

os.makedirs(GIF_DIR, exist_ok=True)


def secret_key():
    path = os.path.join(BASE, "secret.key")
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write(secrets.token_hex(32))
    return open(path).read().strip()


app = Flask(__name__, static_folder="static", static_url_path="/static")
app.secret_key = secret_key()
app.config.update(SESSION_COOKIE_SAMESITE="Lax", PERMANENT_SESSION_LIFETIME=60 * 60 * 24 * 90,
                  JSON_AS_ASCII=False)

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL COLLATE NOCASE,
    pw_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    weight REAL, height REAL, age INTEGER, sex TEXT,
    goal TEXT NOT NULL DEFAULT 'saude',
    has_bar INTEGER NOT NULL DEFAULT 0,
    low_impact INTEGER NOT NULL DEFAULT 0,
    a_push INTEGER DEFAULT 0, a_squat INTEGER DEFAULT 0, a_plank INTEGER DEFAULT 0, a_pull INTEGER DEFAULT 0,
    level INTEGER NOT NULL DEFAULT 1, xp INTEGER NOT NULL DEFAULT 0, total_xp INTEGER NOT NULL DEFAULT 0,
    stat_points INTEGER NOT NULL DEFAULT 0,
    str INTEGER NOT NULL DEFAULT 10, agi INTEGER NOT NULL DEFAULT 10, vit INTEGER NOT NULL DEFAULT 10,
    per INTEGER NOT NULL DEFAULT 10, int INTEGER NOT NULL DEFAULT 10,
    streak INTEGER NOT NULL DEFAULT 0, best_streak INTEGER NOT NULL DEFAULT 0, last_quest_day TEXT,
    sessions INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);
CREATE TABLE IF NOT EXISTS chains (
    user_id INTEGER NOT NULL, chain TEXT NOT NULL, ex_key TEXT NOT NULL,
    PRIMARY KEY (user_id, chain)
);
CREATE TABLE IF NOT EXISTS exercise_progress (
    user_id INTEGER NOT NULL, ex_key TEXT NOT NULL,
    level INTEGER NOT NULL DEFAULT 1, mastered INTEGER NOT NULL DEFAULT 0,
    xp INTEGER NOT NULL DEFAULT 0, best INTEGER NOT NULL DEFAULT 0, sessions INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, ex_key)
);
CREATE TABLE IF NOT EXISTS missions (
    user_id INTEGER NOT NULL, mkey TEXT NOT NULL, target INTEGER NOT NULL,
    fails INTEGER NOT NULL DEFAULT 0, best INTEGER NOT NULL DEFAULT 0, completed INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, mkey)
);
CREATE TABLE IF NOT EXISTS daily (
    user_id INTEGER NOT NULL, day TEXT NOT NULL, mkey TEXT NOT NULL,
    target INTEGER NOT NULL, status TEXT NOT NULL DEFAULT 'pending', xp INTEGER,
    UNIQUE (user_id, day, mkey)
);
CREATE TABLE IF NOT EXISTS workouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, day TEXT NOT NULL, split TEXT,
    xp INTEGER NOT NULL, duration_s INTEGER, cadence_used INTEGER, data TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);
CREATE TABLE IF NOT EXISTS body_log (
    user_id INTEGER NOT NULL, day TEXT NOT NULL, weight REAL, PRIMARY KEY (user_id, day)
);
CREATE TABLE IF NOT EXISTS login_attempts (ip TEXT PRIMARY KEY, fails INTEGER, until REAL);
"""


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys=ON")
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


MIGRATIONS = {  # colunas adicionadas depois da primeira versão
    "pregnant": "ALTER TABLE users ADD COLUMN pregnant INTEGER NOT NULL DEFAULT 0",
    "preg_start": "ALTER TABLE users ADD COLUMN preg_start TEXT",
}


def init_db():
    con = sqlite3.connect(DB_PATH)
    con.executescript(SCHEMA)
    cols = {r[1] for r in con.execute("PRAGMA table_info(users)")}
    for col, sql in MIGRATIONS.items():
        if col not in cols:
            con.execute(sql)
    con.commit()
    con.close()


def preg_fields(d, sex):
    """(pregnant, preg_start) a partir da semana de gestação informada."""
    if not d.get("pregnant") or sex == "M":
        return 0, None
    week = num(d.get("preg_week"), 1, 42, int)
    if week is None:
        raise ValueError("Informe a semana de gestação (1 a 42).")
    if not d.get("preg_clearance"):
        raise ValueError("Para o modo gestante, confirme que tem liberação do seu médico/obstetra.")
    return 1, (date.today() - timedelta(days=week * 7)).isoformat()


def current_user():
    uid = session.get("uid")
    if not uid:
        return None
    return get_db().execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()


def login_required(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        user = current_user()
        if not user:
            return jsonify({"error": "Não autenticado."}), 401
        return fn(user, *a, **kw)
    return wrapper


def num(v, lo, hi, cast=float, default=None):
    try:
        x = cast(v)
    except (TypeError, ValueError):
        return default
    return max(lo, min(hi, x))


# ------------------------------------------------------------------ páginas

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/manifest.webmanifest")
def manifest():
    return send_from_directory(app.static_folder, "manifest.webmanifest",
                               mimetype="application/manifest+json")


# ------------------------------------------------------------------ auth

def too_many_attempts(ip):
    row = get_db().execute("SELECT * FROM login_attempts WHERE ip=?", (ip,)).fetchone()
    return row and row["fails"] >= 5 and row["until"] > time.time()


def register_fail(ip):
    db = get_db()
    row = db.execute("SELECT * FROM login_attempts WHERE ip=?", (ip,)).fetchone()
    fails = (row["fails"] if row and row["until"] > time.time() else 0) + 1
    db.execute("INSERT OR REPLACE INTO login_attempts(ip, fails, until) VALUES (?,?,?)",
               (ip, fails, time.time() + 15 * 60))
    db.commit()


@app.post("/api/register")
def register():
    d = request.get_json(force=True) or {}
    username = (d.get("username") or "").strip()
    password = d.get("password") or ""
    name = (d.get("name") or username).strip()[:40]
    if len(username) < 3 or len(password) < 4:
        return jsonify({"error": "Usuário (mín. 3) e senha (mín. 4) obrigatórios."}), 400
    goal = d.get("goal") if d.get("goal") in game.GOALS else "saude"
    user = {
        "username": username[:30], "name": name, "pw_hash": generate_password_hash(password),
        "weight": num(d.get("weight"), 25, 350), "height": num(d.get("height"), 100, 250),
        "age": num(d.get("age"), 10, 100, int), "sex": d.get("sex") if d.get("sex") in ("M", "F", "O") else "O",
        "goal": goal, "has_bar": 1 if d.get("has_bar") else 0, "low_impact": 1 if d.get("low_impact") else 0,
        "a_push": num(d.get("a_push"), 0, 200, int, 0), "a_squat": num(d.get("a_squat"), 0, 500, int, 0),
        "a_plank": num(d.get("a_plank"), 0, 1200, int, 0), "a_pull": num(d.get("a_pull"), 0, 100, int, 0),
    }
    if not all([user["weight"], user["height"], user["age"]]):
        return jsonify({"error": "Informe peso, altura e idade."}), 400
    try:
        user["pregnant"], user["preg_start"] = preg_fields(d, user["sex"])
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    if user["pregnant"]:
        user["low_impact"] = 1
    db = get_db()
    try:
        cur = db.execute("""INSERT INTO users(username, pw_hash, name, weight, height, age, sex, goal, has_bar,
                            low_impact, a_push, a_squat, a_plank, a_pull, pregnant, preg_start)
                            VALUES (:username,:pw_hash,:name,:weight,:height,:age,:sex,:goal,:has_bar,
                            :low_impact,:a_push,:a_squat,:a_plank,:a_pull,:pregnant,:preg_start)""", user)
    except sqlite3.IntegrityError:
        return jsonify({"error": "Esse nome de usuário já existe."}), 409
    uid = cur.lastrowid
    row = db.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    # stats iniciais refletem o teste de despertar
    tiers = {ck: t for ck, (_k, t) in game.seed_chains(db, row).items()}
    db.execute("UPDATE users SET str=?, agi=?, vit=? WHERE id=?",
               (8 + tiers["push"] + tiers["pull"] // 2, 8 + tiers["legs"] + tiers["cardio"] // 2,
                8 + tiers["core"] + tiers["cardio"] // 2, uid))
    game.init_missions(db, row)
    db.execute("INSERT OR REPLACE INTO body_log(user_id, day, weight) VALUES (?, date('now','localtime'), ?)",
               (uid, user["weight"]))
    db.commit()
    session.permanent = True
    session["uid"] = uid
    user_row = db.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    return jsonify({"ok": True, "status": game.status(db, user_row), "skills": game.skills_tree(db, user_row)})


@app.post("/api/login")
def login():
    ip = request.remote_addr or "?"
    if too_many_attempts(ip):
        return jsonify({"error": "Muitas tentativas. Aguarde 15 minutos."}), 429
    d = request.get_json(force=True) or {}
    row = get_db().execute("SELECT * FROM users WHERE username=?", ((d.get("username") or "").strip(),)).fetchone()
    if not row or not check_password_hash(row["pw_hash"], d.get("password") or ""):
        register_fail(ip)
        return jsonify({"error": "Usuário ou senha inválidos."}), 401
    get_db().execute("DELETE FROM login_attempts WHERE ip=?", (ip,))
    get_db().commit()
    session.permanent = True
    session["uid"] = row["id"]
    return jsonify({"ok": True})


@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify({"ok": True})


# ------------------------------------------------------------------ jogador

@app.get("/api/me")
@login_required
def me(user):
    db = get_db()
    q = game.today_quests(db, user)
    user = current_user()  # streak pode ter sido zerado pela penalidade
    trained_today = db.execute("SELECT COUNT(*) FROM workouts WHERE user_id=? AND day=date('now','localtime')",
                               (user["id"],)).fetchone()[0]
    return jsonify({"status": game.status(db, user), "quests": q, "trained_today": trained_today > 0,
                    "goals": {k: v["name"] for k, v in game.GOALS.items()}})


@app.put("/api/profile")
@login_required
def update_profile(user):
    d = request.get_json(force=True) or {}
    db = get_db()
    fields = {
        "name": (d.get("name") or user["name"]).strip()[:40],
        "weight": num(d.get("weight"), 25, 350, default=user["weight"]),
        "height": num(d.get("height"), 100, 250, default=user["height"]),
        "age": num(d.get("age"), 10, 100, int, default=user["age"]),
        "goal": d.get("goal") if d.get("goal") in game.GOALS else user["goal"],
        "has_bar": 1 if d.get("has_bar", user["has_bar"]) else 0,
        "low_impact": 1 if d.get("low_impact", user["low_impact"]) else 0,
        "id": user["id"],
    }
    was_pregnant = game.preg_week(user) is not None
    if "pregnant" in d:
        try:
            fields["pregnant"], fields["preg_start"] = preg_fields(d, user["sex"])
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    else:
        fields["pregnant"], fields["preg_start"] = user["pregnant"], user["preg_start"]
    db.execute("""UPDATE users SET name=:name, weight=:weight, height=:height, age=:age, goal=:goal,
                  has_bar=:has_bar, low_impact=:low_impact, pregnant=:pregnant, preg_start=:preg_start
                  WHERE id=:id""", fields)
    new = db.execute("SELECT * FROM users WHERE id=?", (user["id"],)).fetchone()
    if (game.preg_week(new) is not None) != was_pregnant:
        # Mudou de modo: cria o tier inicial das árvores do novo modo (sem apagar
        # o progresso do outro) e refaz as missões pendentes de hoje.
        game.seed_chains(db, new, overwrite=False)
        db.execute("DELETE FROM daily WHERE user_id=? AND day=date('now','localtime') AND status='pending'",
                   (user["id"],))
    if fields["weight"] != user["weight"]:
        db.execute("INSERT OR REPLACE INTO body_log(user_id, day, weight) VALUES (?, date('now','localtime'), ?)",
                   (user["id"], fields["weight"]))
    if d.get("password"):
        if len(d["password"]) < 4:
            return jsonify({"error": "Senha muito curta."}), 400
        db.execute("UPDATE users SET pw_hash=? WHERE id=?", (generate_password_hash(d["password"]), user["id"]))
    db.commit()
    return jsonify({"ok": True, "status": game.status(db, current_user())})


@app.post("/api/stats/allocate")
@login_required
def allocate(user):
    stat = (request.get_json(force=True) or {}).get("stat", "")
    col = {"STR": "str", "AGI": "agi", "VIT": "vit", "PER": "per", "INT": "int"}.get(stat)
    if not col or user["stat_points"] <= 0:
        return jsonify({"error": "Sem pontos disponíveis."}), 400
    db = get_db()
    db.execute(f"UPDATE users SET {col}={col}+1, stat_points=stat_points-1 WHERE id=?", (user["id"],))
    db.commit()
    return jsonify({"ok": True, "status": game.status(db, current_user())})


# ------------------------------------------------------------------ treino

@app.get("/api/workout/today")
@login_required
def workout_today(user):
    return jsonify(game.build_workout(get_db(), user))


@app.post("/api/workout/complete")
@login_required
def workout_complete(user):
    db = get_db()
    res = game.complete_workout(db, user, request.get_json(force=True) or {})
    if "error" in res:
        return jsonify(res), 400
    new = current_user()
    res["status"] = game.status(db, new)
    res["rank_up"] = game.player_rank(user["level"])["code"] != game.player_rank(new["level"])["code"]
    return jsonify(res)


@app.get("/api/skills")
@login_required
def skills(user):
    return jsonify(game.skills_tree(get_db(), user))


@app.post("/api/skills/<chain>/select")
@login_required
def select_exercise(user, chain):
    """Permite voltar para um tier já dominado/anterior (ex.: dia de dor no joelho)."""
    key = (request.get_json(force=True) or {}).get("key")
    if chain not in CHAINS or key not in EXERCISE_BY_KEY or EXERCISE_BY_KEY[key][0] != chain:
        return jsonify({"error": "Exercício inválido."}), 400
    db = get_db()
    cur_tier, _, lst = game.current_in_chain(db, user, chain)
    tier = next((t for t, e in lst if e["key"] == key), None)
    if tier is None or tier > cur_tier:
        prog = game.ex_progress(db, user["id"], key)
        prev_key = lst[tier - 2][1]["key"] if tier and tier > 1 else None
        prev_mastered = prev_key and game.ex_progress(db, user["id"], prev_key)["mastered"]
        if tier is None or not (prog["sessions"] or prev_mastered) or user["level"] < game.tier_required_level(tier):
            return jsonify({"error": "Esse exercício ainda está bloqueado."}), 403
    db.execute("INSERT OR REPLACE INTO chains(user_id, chain, ex_key) VALUES (?,?,?)",
               (user["id"], game.chain_slot(user, chain), key))
    db.commit()
    return jsonify({"ok": True})


@app.get("/api/history")
@login_required
def history(user):
    db = get_db()
    rows = db.execute("SELECT * FROM workouts WHERE user_id=? ORDER BY id DESC LIMIT 60", (user["id"],)).fetchall()
    weights = db.execute("SELECT day, weight FROM body_log WHERE user_id=? ORDER BY day", (user["id"],)).fetchall()
    quests = db.execute("""SELECT day, SUM(status='done') done, COUNT(*) total FROM daily
                           WHERE user_id=? AND mkey!='penalty' GROUP BY day ORDER BY day DESC LIMIT 60""",
                        (user["id"],)).fetchall()
    missions = db.execute("SELECT * FROM missions WHERE user_id=?", (user["id"],)).fetchall()
    active_missions = (set(game.PRENATAL_ROTATING) | {game.PRENATAL_MAIN_MISSION}
                       if game.preg_week(user) is not None else set(game.ROTATING_MISSIONS) | {"plank"})
    return jsonify({
        "workouts": [{"id": r["id"], "day": r["day"], "split": r["split"], "xp": r["xp"],
                      "duration_s": r["duration_s"], "cadence": bool(r["cadence_used"]),
                      "exercises": json.loads(r["data"] or "[]")} for r in rows],
        "weights": [dict(w) for w in weights],
        "quests": [dict(q) for q in quests],
        "missions": [{"key": m["mkey"], "name": ALL_MISSIONS[m["mkey"]]["name"],
                      "type": ALL_MISSIONS[m["mkey"]]["type"], "target": m["target"], "best": m["best"],
                      "completed": m["completed"]}
                     for m in missions if m["mkey"] in ALL_MISSIONS and (m["completed"] or m["best"]
                                                                          or m["mkey"] in active_missions)],
    })


# ------------------------------------------------------------------ missões

@app.get("/api/quests/today")
@login_required
def quests_today(user):
    return jsonify(game.today_quests(get_db(), user))


@app.post("/api/quests/<key>")
@login_required
def quest_resolve(user, key):
    success = bool((request.get_json(force=True) or {}).get("success"))
    db = get_db()
    res = game.resolve_quest(db, user, key, success)
    if "error" in res:
        return jsonify(res), 400
    res["status"] = game.status(db, current_user())
    return jsonify(res)


# ------------------------------------------------------------------ ExerciseDB (API pública)

_snapshot_lock = threading.Lock()
_snapshot = None


def fetch_json(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429 and i < tries - 1:
                time.sleep(3 * (i + 1))
                continue
            raise
    return None


def slim(e):
    return {"id": e["exerciseId"], "name": e["name"], "bodyParts": e.get("bodyParts", []),
            "equipments": e.get("equipments", []), "target": e.get("targetMuscles", []),
            "secondary": e.get("secondaryMuscles", []),
            "instructions": [s.split(" ", 1)[1] if s.startswith("Step:") else s for s in e.get("instructions", [])]}


def load_snapshot():
    global _snapshot
    with _snapshot_lock:
        if _snapshot is None:
            try:
                with open(SNAPSHOT, encoding="utf-8") as f:
                    _snapshot = json.load(f)
            except (OSError, ValueError):
                _snapshot = []
        return _snapshot


@app.get("/api/library")
@login_required
def library(_user):
    part = request.args.get("part", "")
    q = (request.args.get("q") or "").strip().lower()
    items = load_snapshot()
    if part:
        items = [e for e in items if part in e["bodyParts"]]
    if q:
        items = [e for e in items if q in e["name"].lower()
                 or any(q in m for m in e["target"] + e["secondary"])]
    return jsonify({"count": len(items), "items": items[:120], "total": len(load_snapshot())})


@app.get("/api/library/search")
@login_required
def library_live(_user):
    """Busca ao vivo na ExerciseDB (qualquer equipamento)."""
    q = (request.args.get("q") or "").strip()
    if len(q) < 2:
        return jsonify({"items": []})
    try:
        d = fetch_json(f"{EXDB_API}/exercises?name={urllib.parse.quote(q)}&limit=40")
    except Exception as e:  # noqa: BLE001 - offline, rate-limit etc.
        return jsonify({"error": f"API indisponível: {e}"}), 502
    return jsonify({"items": [slim(e) for e in (d or {}).get("data", [])]})


@app.post("/api/library/sync")
@login_required
def library_sync(_user):
    """Baixa novamente todos os exercícios de peso corporal da ExerciseDB."""
    global _snapshot
    out, cursor = [], None
    try:
        for _ in range(40):
            url = f"{EXDB_API}/exercises?limit=100" + (f"&after={cursor}" if cursor else "")
            d = fetch_json(url, tries=6)
            out += [slim(e) for e in d["data"] if "bodyweight" in e.get("equipments", [])]
            if not d["meta"].get("hasNextPage"):
                break
            cursor = d["meta"]["nextCursor"]
            time.sleep(1.5)
    except Exception as e:  # noqa: BLE001
        return jsonify({"error": f"Falha ao sincronizar: {e}"}), 502
    os.makedirs(os.path.dirname(SNAPSHOT), exist_ok=True)
    with open(SNAPSHOT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    with _snapshot_lock:
        _snapshot = out
    return jsonify({"ok": True, "total": len(out)})


@app.get("/api/exercise/<ex_id>")
@login_required
def exercise_detail(_user, ex_id):
    for e in load_snapshot():
        if e["id"] == ex_id:
            return jsonify(e)
    try:
        d = fetch_json(f"{EXDB_API}/exercises/{urllib.parse.quote(ex_id)}")
        return jsonify(slim(d["data"]))
    except Exception:  # noqa: BLE001
        return jsonify({"error": "Detalhes indisponíveis offline."}), 404


@app.get("/gif/<ex_id>.gif")
def gif(ex_id):
    """GIF demonstrativo — baixado da ExerciseDB uma vez e servido do cache local."""
    if not ex_id.isalnum() or len(ex_id) > 16:
        abort(404)
    path = os.path.join(GIF_DIR, ex_id + ".gif")
    if not os.path.exists(path):
        try:
            with urllib.request.urlopen(urllib.request.Request(f"{EXDB_MEDIA}/{ex_id}.gif", headers=UA),
                                        timeout=20) as r:
                data = r.read()
            with open(path + ".tmp", "wb") as f:
                f.write(data)
            os.replace(path + ".tmp", path)
        except Exception:  # noqa: BLE001
            return Response(status=404)
    resp = send_from_directory(GIF_DIR, ex_id + ".gif", mimetype="image/gif")
    resp.headers["Cache-Control"] = "public, max-age=2592000"
    return resp


def prefetch_gifs():
    """Baixa em segundo plano os GIFs dos exercícios do app (para funcionar offline)."""
    ids = {ex["db"] for c in CHAINS.values() for ex in c["exercises"]}
    ids |= {ex["db"] for lst in PRENATAL_CHAINS.values() for ex in lst}
    ids |= {m["db"] for m in ALL_MISSIONS.values() if m.get("db")}
    ids.add("ealLwvX")
    for ex_id in sorted(ids):
        path = os.path.join(GIF_DIR, ex_id + ".gif")
        if os.path.exists(path):
            continue
        try:
            with urllib.request.urlopen(urllib.request.Request(f"{EXDB_MEDIA}/{ex_id}.gif", headers=UA),
                                        timeout=30) as r:
                data = r.read()
            with open(path, "wb") as f:
                f.write(data)
            time.sleep(0.5)
        except Exception:  # noqa: BLE001
            pass


init_db()

if __name__ == "__main__":
    threading.Thread(target=prefetch_gifs, daemon=True).start()
    port = int(os.environ.get("PORT", 5050))
    print(f"ARISE rodando em http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
