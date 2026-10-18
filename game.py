"""Regras do "Sistema": níveis, ranks, XP, geração de treino e missões diárias."""
import json
import math
from datetime import date, timedelta

from exercises import (CHAINS, SPLITS, MISSIONS, ROTATING_MISSIONS, PENALTY_MISSION,
                       chain_exercises, full_chain, EXERCISE_BY_KEY, ALL_MISSIONS, PRENATAL_MISSIONS,
                       PRENATAL_MAIN_MISSION, PRENATAL_ROTATING, THIRD_TRIMESTER_WEEK)

# ---------------------------------------------------------------- ranks / níveis

PLAYER_RANKS = [
    # (nível mínimo, código, nome, título)
    (1, "E", "Rank E", "O Mais Fraco da Humanidade"),
    (10, "D", "Rank D", "Aquele que Despertou"),
    (20, "C", "Rank C", "Caçador de Lobos"),
    (30, "B", "Rank B", "Matador de Cavaleiros"),
    (45, "A", "Rank A", "Senhor da Masmorra"),
    (60, "S", "Rank S", "Necromante"),
    (80, "N", "Nível Nacional", "Soberano"),
    (100, "M", "Monarca", "Monarca das Sombras"),
]

EXERCISE_RANKS = ["E", "D", "C", "B", "A"]  # nível 1..5 do exercício; dominado = S
MAX_EX_LEVEL = 5
STAT_POINTS_PER_LEVEL = 3
STATS = ["STR", "AGI", "VIT", "PER", "INT"]


def xp_to_next(level):
    return int(60 * level ** 1.3 + 40)


def player_rank(level):
    cur = PLAYER_RANKS[0]
    for r in PLAYER_RANKS:
        if level >= r[0]:
            cur = r
    nxt = next((r for r in PLAYER_RANKS if r[0] > level), None)
    return {"code": cur[1], "name": cur[2], "title": cur[3],
            "next_code": nxt[1] if nxt else None, "next_level": nxt[0] if nxt else None}


def exercise_rank(level, mastered):
    return "S" if mastered else EXERCISE_RANKS[min(level, MAX_EX_LEVEL) - 1]


def tier_required_level(tier):
    """Nível do jogador exigido para *desbloquear por evolução* um tier."""
    return max(1, (tier - 1) * 3)


# ---------------------------------------------------------------- objetivos

GOALS = {
    "emagrecer": {"name": "Perder gordura", "reps": (12, 20), "time": (30, 60), "sets": 3, "rest": 40,
                  "tempo": [1, 0, 1, 0]},
    "massa": {"name": "Ganhar massa muscular", "reps": (8, 15), "time": (20, 45), "sets": 3, "rest": 75,
              "tempo": [3, 1, 1, 0]},
    "forca": {"name": "Força & habilidades", "reps": (5, 10), "time": (15, 40), "sets": 4, "rest": 120,
              "tempo": [2, 1, 1, 0]},
    "resistencia": {"name": "Resistência / condicionamento", "reps": (15, 25), "time": (40, 75), "sets": 3,
                    "rest": 30, "tempo": [1, 0, 1, 0]},
    "saude": {"name": "Saúde geral / começar do zero", "reps": (10, 15), "time": (20, 45), "sets": 2,
              "rest": 60, "tempo": [2, 0, 2, 0]},
}
CARDIO_TIME = {"emagrecer": (40, 75), "resistencia": (45, 90), "massa": (25, 45), "forca": (20, 40),
               "saude": (20, 45)}


def bmi(user):
    try:
        h = user["height"] / 100
        return round(user["weight"] / (h * h), 1)
    except (TypeError, ZeroDivisionError):
        return None


def bmi_label(v):
    if v is None:
        return "—"
    if v < 18.5:
        return "Abaixo do peso"
    if v < 25:
        return "Peso normal"
    if v < 30:
        return "Sobrepeso"
    return "Obesidade"


def suggest_low_impact(age, weight, height):
    try:
        b = weight / ((height / 100) ** 2)
    except (TypeError, ZeroDivisionError):
        b = 0
    return (age or 0) >= 55 or b >= 32


# ---------------------------------------------------------------- gestação

def preg_week(user):
    """Semana de gestação atual (calculada a partir de preg_start) ou None."""
    try:
        if not user["pregnant"] or not user["preg_start"]:
            return None
        return max(1, (date.today() - date.fromisoformat(user["preg_start"])).days // 7)
    except (KeyError, IndexError, ValueError):
        return None


def trimester(week):
    return None if week is None else 1 if week <= 13 else 2 if week < THIRD_TRIMESTER_WEEK else 3


def chain_list(user, chain_key):
    return chain_exercises(chain_key, user["has_bar"], user["low_impact"], preg_week(user))


def chain_slot(user, chain_key):
    """Na gestação o progresso fica numa cadeia separada; ao sair do modo, volta ao normal."""
    return ("pn_" + chain_key) if preg_week(user) is not None else chain_key


# ---------------------------------------------------------------- avaliação inicial

def _band(value, cuts):
    """cuts = [(limite_exclusivo, tier), ...]; retorna o tier da primeira faixa."""
    for limit, tier in cuts:
        if value < limit:
            return tier
    return cuts[-1][1] + 1


def initial_tiers(user):
    """Tier inicial de cada cadeia com base no Teste de Despertar -> {chain: (ex_key, tier)}."""
    if preg_week(user) is not None:
        push = _band(user["a_push"] or 0, [(1, 1), (8, 2), (20, 3)])
        legs = _band(user["a_squat"] or 0, [(10, 1), (20, 2), (35, 3)])
        tiers = {"push": push, "legs": legs, "core": 1, "pull": 2 if push >= 3 else 1, "cardio": 1,
                 "dips": 1, "posterior": 1}
        return _resolve_tiers(user, tiers)
    push = _band(user["a_push"] or 0, [(1, 1), (4, 2), (8, 3), (16, 4), (26, 5), (41, 6)])
    legs = _band(user["a_squat"] or 0, [(10, 1), (25, 2), (40, 3), (60, 4)])
    core = _band(user["a_plank"] or 0, [(20, 1), (45, 2), (90, 3), (150, 4)])
    b = bmi(user) or 22
    if user["has_bar"]:
        pulls = user["a_pull"] or 0
        if pulls == 0:
            pull = 5 if push >= 4 else max(1, push - 1)
        else:
            pull = _band(pulls, [(4, 8), (9, 9), (15, 10)])
    else:
        pull = max(1, min(push - 1, 5))
    if user["low_impact"] or (user["age"] or 0) >= 50 or b >= 30:
        cardio = 1
    elif user["goal"] in ("emagrecer", "resistencia"):
        cardio = 3
    else:
        cardio = 2
    tiers = {"push": push, "legs": legs, "core": core, "pull": pull, "cardio": cardio,
             "dips": max(1, min(push - 2, 3)), "posterior": max(1, min(legs, 3))}
    return _resolve_tiers(user, tiers)


def _resolve_tiers(user, tiers):
    out = {}
    for ck, t in tiers.items():
        lst = chain_list(user, ck)
        t = max(1, min(t, len(lst)))
        out[ck] = (lst[t - 1][1]["key"], t)
    return out


def seed_chains(db, user, overwrite=True):
    """Grava o tier inicial de cada cadeia (no slot normal ou de gestante)."""
    verb = "INSERT OR REPLACE" if overwrite else "INSERT OR IGNORE"
    tiers = initial_tiers(user)
    for ck, (key, _t) in tiers.items():
        db.execute(f"{verb} INTO chains(user_id, chain, ex_key) VALUES (?,?,?)",
                   (user["id"], chain_slot(user, ck), key))
    return tiers


def mission_start_targets(user):
    def r5(x):
        return int(round(x / 5.0) * 5)
    plank = user["a_plank"] or 0
    return {
        "plank": max(15, min(r5(plank * 0.8), 120)) if plank else MISSIONS["plank"]["start"],
        "wall_sit": MISSIONS["wall_sit"]["start"],
        "pushups": max(10, min(r5((user["a_push"] or 0) * 2), 100)) or 10,
        "squats": max(20, min(r5((user["a_squat"] or 0) * 1.5), 150)),
        "situps": MISSIONS["situps"]["start"],
        **{k: m["start"] for k, m in PRENATAL_MISSIONS.items()},
    }


# ---------------------------------------------------------------- estado de cadeias

def current_in_chain(db, user, chain_key):
    """(tier, exercise, lista_filtrada) do exercício atual da cadeia.

    Se o exercício salvo saiu da lista (ex.: usuário removeu a barra fixa),
    cai para o maior tier disponível que ainda existe abaixo dele.
    """
    lst = chain_list(user, chain_key)
    slot = chain_slot(user, chain_key)
    row = db.execute("SELECT ex_key FROM chains WHERE user_id=? AND chain=?", (user["id"], slot)).fetchone()
    key = row["ex_key"] if row else lst[0][1]["key"]
    for tier, ex in lst:
        if ex["key"] == key:
            return tier, ex, lst
    full = [e["key"] for e in full_chain(chain_key, preg_week(user) is not None)]
    pos = full.index(key) if key in full else 0
    best = lst[0]
    for tier, ex in lst:
        if full.index(ex["key"]) <= pos:
            best = (tier, ex)
    db.execute("INSERT OR REPLACE INTO chains(user_id, chain, ex_key) VALUES (?,?,?)",
               (user["id"], slot, best[1]["key"]))
    return best[0], best[1], lst


def ex_progress(db, user_id, ex_key):
    row = db.execute("SELECT * FROM exercise_progress WHERE user_id=? AND ex_key=?", (user_id, ex_key)).fetchone()
    if row:
        return dict(row)
    return {"user_id": user_id, "ex_key": ex_key, "level": 1, "mastered": 0, "xp": 0, "best": 0, "sessions": 0}


def save_progress(db, p):
    db.execute("""INSERT OR REPLACE INTO exercise_progress(user_id, ex_key, level, mastered, xp, best, sessions)
                  VALUES (:user_id,:ex_key,:level,:mastered,:xp,:best,:sessions)""", p)


def ex_type(ex):
    return ex.get("type", "reps")


def prescription(user, chain_key, ex, tier, prog):
    """Séries, meta, cadência e descanso de um exercício para este jogador."""
    goal = GOALS.get(user["goal"], GOALS["saude"])
    typ = ex_type(ex)
    if preg_week(user) is not None:
        lo, hi = (60, 150) if chain_key == "cardio" else (20, 40) if typ == "time" else (8, 15)
    elif chain_key == "cardio" and typ == "time":
        lo, hi = CARDIO_TIME.get(user["goal"], (30, 60))
    elif typ == "time":
        lo, hi = goal["time"]
    else:
        lo, hi = goal["reps"]
    if chain_key == "posterior" and typ == "reps" and preg_week(user) is None:
        lo, hi = lo + 2, hi + 4  # glúteos toleram mais volume
    lvl = min(prog["level"], MAX_EX_LEVEL)
    target = lo + round((hi - lo) * (lvl - 1) / (MAX_EX_LEVEL - 1))
    if prog["mastered"]:
        target = hi
    if typ == "time":
        target = int(round(target / 5.0) * 5)

    level = user["level"]
    sets = goal["sets"] + (1 if level >= 20 else 0) + (1 if level >= 45 else 0)
    rest = goal["rest"]
    if level >= 30:
        rest = int(rest * 0.85)
    tempo = list(goal["tempo"])
    if ex.get("impact") or chain_key == "cardio":
        tempo = [1, 0, 1, 0]  # explosivo
    if preg_week(user) is not None:
        # Gestação: intensidade moderada, sem pausas isométricas (evita prender a
        # respiração), no máximo 3 séries e descanso de pelo menos 60s.
        sets = min(3, 2 + (1 if level >= 20 else 0))
        rest = max(60, min(goal["rest"], 90))
        tempo = [2, 0, 2, 0]
    return {"sets": sets, "target": target, "range": [lo, hi], "type": typ, "tempo": tempo, "rest": rest}


def exercise_card(db, user, chain_key, tier, ex, lst, prog=None):
    prog = prog or ex_progress(db, user["id"], ex["key"])
    nxt = lst[tier][1] if tier < len(lst) else None
    return {
        "key": ex["key"], "name": ex["name"], "db": ex["db"], "cue": ex["cue"],
        "chain": chain_key, "chain_name": CHAINS[chain_key]["name"], "stat": CHAINS[chain_key]["stat"],
        "tier": tier, "tiers": len(lst), "impact": bool(ex.get("impact")), "bar": bool(ex.get("bar")),
        "level": prog["level"], "mastered": bool(prog["mastered"]),
        "rank": exercise_rank(prog["level"], prog["mastered"]), "best": prog["best"], "xp": prog["xp"],
        "next": {"name": nxt["name"], "key": nxt["key"], "req_level": tier_required_level(tier + 1)} if nxt else None,
    }


# ---------------------------------------------------------------- treino do dia

def exercise_count(level):
    return 4 if level < 10 else 5 if level < 30 else 6


def build_workout(db, user):
    split = "A" if user["sessions"] % 2 == 0 else "B"
    week = preg_week(user)
    n = exercise_count(user["level"]) if week is None else min(5, exercise_count(user["level"]))
    chosen = SPLITS[split][:n]
    if user["goal"] in ("emagrecer", "resistencia") and "cardio" not in chosen:
        chosen[-1] = "cardio"
    items = []
    for ck in chosen:
        tier, ex, lst = current_in_chain(db, user, ck)
        prog = ex_progress(db, user["id"], ex["key"])
        card = exercise_card(db, user, ck, tier, ex, lst, prog)
        card.update(prescription(user, ck, ex, tier, prog))
        items.append(card)
    db.commit()
    est = sum(i["sets"] * ((i["target"] if i["type"] == "time" else i["target"] * sum(i["tempo"])) + i["rest"])
              for i in items)
    return {"split": split, "gate": "Portão " + ("Azul" if split == "A" else "Vermelho"),
            "exercises": items, "estimated_min": max(10, round(est / 60)),
            "goal": GOALS.get(user["goal"], GOALS["saude"])["name"],
            "streak_bonus": streak_multiplier(user["streak"]),
            "pregnancy": {"week": week, "trimester": trimester(week)} if week is not None else None}


def streak_multiplier(streak):
    return round(1 + min(streak or 0, 10) * 0.03, 2)


def grant_xp(db, user, amount):
    """Soma XP, processa level ups. Retorna lista de níveis alcançados."""
    level, xp, points = user["level"], user["xp"] + amount, user["stat_points"]
    ups = []
    while xp >= xp_to_next(level):
        xp -= xp_to_next(level)
        level += 1
        points += STAT_POINTS_PER_LEVEL
        ups.append(level)
    db.execute("UPDATE users SET level=?, xp=?, total_xp=total_xp+?, stat_points=? WHERE id=?",
               (level, xp, amount, points, user["id"]))
    return ups


def complete_workout(db, user, payload):
    today = date.today().isoformat()
    cadence = bool(payload.get("cadence_used"))
    split = payload.get("split", "A")
    breakdown, evolutions, blocked, stat_gain = [], [], [], {s: 0 for s in STATS}
    base_xp = 0.0
    done_count = 0
    for item in payload.get("exercises", []):
        key = item.get("key")
        if key not in EXERCISE_BY_KEY:
            continue
        ck, ex = EXERCISE_BY_KEY[key]
        tier, cur, lst = current_in_chain(db, user, ck)
        if cur["key"] != key:
            continue  # exercício não é mais o atual da cadeia; ignora
        prog = ex_progress(db, user["id"], key)
        pres = prescription(user, ck, ex, tier, prog)
        sets = [max(0, int(s)) for s in item.get("sets", []) if str(s).lstrip("-").isdigit()][:10]
        if not sets or sum(sets) == 0:
            continue
        done_count += 1
        volume = sum(sets) / (3.0 if pres["type"] == "time" else 1.0)
        weight = 1 + 0.2 * (tier - 1)
        xp = volume * weight * (1.15 if cadence else 1.0)
        base_xp += xp
        cleared = len(sets) >= pres["sets"] and all(s >= pres["target"] for s in sets[:pres["sets"]])
        prog["xp"] += int(volume)
        prog["best"] = max(prog["best"], max(sets))
        prog["sessions"] += 1
        old_rank = exercise_rank(prog["level"], prog["mastered"])
        if cleared:
            stat_gain[CHAINS[ck]["stat"]] += 1
            if prog["level"] < MAX_EX_LEVEL:
                prog["level"] += 1
            elif not prog["mastered"]:
                prog["mastered"] = 1
        save_progress(db, prog)
        new_rank = exercise_rank(prog["level"], prog["mastered"])
        entry = {"key": key, "name": ex["name"], "xp": round(xp), "cleared": cleared,
                 "target": pres["target"], "sets": sets, "type": pres["type"],
                 "rank_from": old_rank, "rank_to": new_rank}
        # evolução: dominou o exercício -> próximo tier
        if prog["mastered"] and tier < len(lst):
            nxt = lst[tier][1]
            req = tier_required_level(tier + 1)
            if user["level"] >= req:
                db.execute("INSERT OR REPLACE INTO chains(user_id, chain, ex_key) VALUES (?,?,?)",
                           (user["id"], chain_slot(user, ck), nxt["key"]))
                evolutions.append({"chain": CHAINS[ck]["name"], "from": ex["name"], "to": nxt["name"],
                                   "db": nxt["db"]})
            else:
                blocked.append({"chain": CHAINS[ck]["name"], "to": nxt["name"], "req_level": req})
        breakdown.append(entry)

    if done_count == 0:
        return {"error": "Nenhuma série registrada."}

    session_bonus = 30 + 10 * done_count
    mult = streak_multiplier(user["streak"])
    total = int(round((base_xp + session_bonus) * mult))
    if cadence:
        stat_gain["PER"] += 1
    ups = grant_xp(db, user, total)
    db.execute(f"""UPDATE users SET sessions=sessions+1,
                   str=str+?, agi=agi+?, vit=vit+?, per=per+?, int=int+? WHERE id=?""",
               (stat_gain["STR"], stat_gain["AGI"], stat_gain["VIT"], stat_gain["PER"], stat_gain["INT"],
                user["id"]))
    db.execute("""INSERT INTO workouts(user_id, day, split, xp, duration_s, cadence_used, data)
                  VALUES (?,?,?,?,?,?,?)""",
               (user["id"], today, split, total, int(payload.get("duration_s") or 0), int(cadence),
                json.dumps(breakdown, ensure_ascii=False)))
    db.commit()
    return {"xp": total, "base_xp": round(base_xp), "session_bonus": session_bonus, "multiplier": mult,
            "cadence_bonus": cadence, "exercises": breakdown, "evolutions": evolutions, "blocked": blocked,
            "level_ups": ups, "stat_gain": {k: v for k, v in stat_gain.items() if v}}


# ---------------------------------------------------------------- missões diárias

def mission_state(db, user_id, key):
    row = db.execute("SELECT * FROM missions WHERE user_id=? AND mkey=?", (user_id, key)).fetchone()
    return dict(row) if row else None


def ensure_today_quests(db, user):
    today = date.today()
    ts = today.isoformat()
    rows = db.execute("SELECT * FROM daily WHERE user_id=? AND day=?", (user["id"], ts)).fetchall()
    if rows:
        return
    # Penalidade: pulou a missão diária de ontem (e já existia ontem)
    created = date.fromisoformat(user["created_at"][:10])
    yesterday = (today - timedelta(days=1)).isoformat()
    penalty = False
    pregnant = preg_week(user) is not None
    if created < today:
        y = db.execute("""SELECT COUNT(*) c, SUM(status='done') d FROM daily
                          WHERE user_id=? AND day=? AND mkey!='penalty'""", (user["id"], yesterday)).fetchone()
        if not y["c"] or (y["d"] or 0) < y["c"]:
            penalty = not pregnant  # gestante: sem missão de penalidade, só zera a sequência
            db.execute("UPDATE users SET streak=0 WHERE id=?", (user["id"],))
    if pregnant:
        main_key = PRENATAL_MAIN_MISSION
        rotating = PRENATAL_ROTATING[today.toordinal() % len(PRENATAL_ROTATING)]
    else:
        main_key = "plank"
        rotating = ROTATING_MISSIONS[today.toordinal() % len(ROTATING_MISSIONS)]
    init_missions(db, user)  # garante o estado das missões novas em contas antigas
    for key in (main_key, rotating):
        st = mission_state(db, user["id"], key)
        db.execute("INSERT INTO daily(user_id, day, mkey, target, status) VALUES (?,?,?,?, 'pending')",
                   (user["id"], ts, key, st["target"]))
    if penalty:
        db.execute("INSERT INTO daily(user_id, day, mkey, target, status) VALUES (?,?,?,?, 'pending')",
                   (user["id"], ts, "penalty", PENALTY_MISSION["target"]))
    db.commit()


def mission_def(key):
    if key == "penalty":
        return PENALTY_MISSION
    return ALL_MISSIONS[key]


def mission_xp(key, target, streak):
    m = mission_def(key)
    base = 15 + target / 2 if m["type"] == "time" else 10 + target * 0.6
    return int(round(base * (1 + min(streak or 0, 20) * 0.05)))


def today_quests(db, user):
    ensure_today_quests(db, user)
    user = db.execute("SELECT * FROM users WHERE id=?", (user["id"],)).fetchone()
    rows = db.execute("SELECT * FROM daily WHERE user_id=? AND day=? ORDER BY mkey='penalty' DESC, rowid",
                      (user["id"], date.today().isoformat())).fetchall()
    out = []
    for r in rows:
        m = mission_def(r["mkey"])
        st = mission_state(db, user["id"], r["mkey"]) if r["mkey"] != "penalty" else None
        out.append({"key": r["mkey"], "name": m["name"], "type": m["type"], "target": r["target"],
                    "status": r["status"], "xp": r["xp"] or mission_xp(r["mkey"], r["target"], user["streak"]),
                    "desc": m["desc"], "db": m.get("db"), "icon": m.get("icon"),
                    "step": m.get("step"), "best": st["best"] if st else None,
                    "penalty": r["mkey"] == "penalty"})
    main = [q for q in out if not q["penalty"]]
    return {"quests": out, "all_done": bool(main) and all(q["status"] == "done" for q in main),
            "penalty": any(q["penalty"] and q["status"] != "done" for q in out),
            "streak": user["streak"], "reward_mult": round(1 + min(user["streak"] or 0, 20) * 0.05, 2)}


def resolve_quest(db, user, key, success):
    ts = date.today().isoformat()
    ensure_today_quests(db, user)
    row = db.execute("SELECT rowid, * FROM daily WHERE user_id=? AND day=? AND mkey=?", (user["id"], ts, key)).fetchone()
    if not row:
        return {"error": "Missão não encontrada para hoje."}
    if row["status"] == "done":
        return {"error": "Missão já concluída."}
    result = {"key": key, "success": success, "xp": 0, "level_ups": [], "quest_complete": False}
    if key == "penalty":
        if success:
            xp = 20
            db.execute("UPDATE daily SET status='done', xp=? WHERE rowid=?", (xp, row["rowid"]))
            result["xp"] = xp
            result["level_ups"] = grant_xp(db, user, xp)
        db.commit()
        return result

    m = ALL_MISSIONS[key]
    st = mission_state(db, user["id"], key)
    if success:
        xp = mission_xp(key, row["target"], user["streak"])
        new_target = row["target"] + m["step"]
        if m.get("cap"):  # missões de gestante têm teto de segurança
            new_target = min(new_target, m["cap"])
        db.execute("UPDATE daily SET status='done', xp=? WHERE rowid=?", (xp, row["rowid"]))
        db.execute("UPDATE missions SET target=?, fails=0, best=MAX(best, ?), completed=completed+1 "
                   "WHERE user_id=? AND mkey=?", (new_target, row["target"], user["id"], key))
        result.update(xp=xp, next_target=new_target, level_ups=grant_xp(db, user, xp))
    else:
        fails = st["fails"] + 1
        new_target = st["target"]
        if fails >= 2:  # dois fracassos seguidos -> o Sistema reduz a meta
            new_target = max(m["min"], st["target"] - m["step"])
            fails = 0
        db.execute("UPDATE daily SET status='failed' WHERE rowid=?", (row["rowid"],))
        db.execute("UPDATE missions SET target=?, fails=? WHERE user_id=? AND mkey=?",
                   (new_target, fails, user["id"], key))
        result["next_target"] = new_target
    db.commit()

    # Todas as missões principais concluídas -> recompensa + sequência
    user = db.execute("SELECT * FROM users WHERE id=?", (user["id"],)).fetchone()
    main = db.execute("SELECT status FROM daily WHERE user_id=? AND day=? AND mkey!='penalty'",
                      (user["id"], ts)).fetchall()
    if success and main and all(r["status"] == "done" for r in main):
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        streak = (user["streak"] + 1) if user["last_quest_day"] == yesterday else 1
        bonus = int(round(25 * (1 + min(streak, 20) * 0.05)))
        db.execute("""UPDATE users SET streak=?, best_streak=MAX(best_streak, ?), last_quest_day=?,
                      int=int+1 WHERE id=?""", (streak, streak, ts, user["id"]))
        result["level_ups"] += grant_xp(db, user, bonus)
        result.update(quest_complete=True, bonus=bonus, streak=streak)
        db.commit()
    return result


def init_missions(db, user):
    targets = mission_start_targets(user)
    for key, t in targets.items():
        db.execute("INSERT OR IGNORE INTO missions(user_id, mkey, target, fails, best, completed) "
                   "VALUES (?,?,?,0,0,0)", (user["id"], key, t))


# ---------------------------------------------------------------- status

def status(db, user):
    r = player_rank(user["level"])
    b = bmi(user)
    return {
        "id": user["id"], "username": user["username"], "name": user["name"],
        "level": user["level"], "xp": user["xp"], "xp_next": xp_to_next(user["level"]),
        "total_xp": user["total_xp"], "rank": r, "stat_points": user["stat_points"],
        "stats": {"STR": user["str"], "AGI": user["agi"], "VIT": user["vit"], "PER": user["per"],
                  "INT": user["int"]},
        "streak": user["streak"], "best_streak": user["best_streak"], "sessions": user["sessions"],
        "profile": {"weight": user["weight"], "height": user["height"], "age": user["age"], "sex": user["sex"],
                    "goal": user["goal"], "goal_name": GOALS.get(user["goal"], GOALS["saude"])["name"],
                    "has_bar": bool(user["has_bar"]), "low_impact": bool(user["low_impact"]),
                    "bmi": b, "bmi_label": bmi_label(b),
                    "pregnant": bool(user["pregnant"]), "preg_week": preg_week(user),
                    "trimester": trimester(preg_week(user))},
        "hp": 100 + user["vit"] * 10 + user["level"] * 5,
        "mp": 50 + user["int"] * 10 + user["level"] * 3,
    }


def skills_tree(db, user):
    out = []
    for ck, c in CHAINS.items():
        cur_tier, cur, lst = current_in_chain(db, user, ck)
        items = []
        for tier, ex in lst:
            prog = ex_progress(db, user["id"], ex["key"])
            state = "current" if tier == cur_tier else ("done" if tier < cur_tier else "locked")
            card = exercise_card(db, user, ck, tier, ex, lst, prog)
            card["state"] = state
            card["req_level"] = tier_required_level(tier)
            items.append(card)
        out.append({"key": ck, "name": c["name"], "stat": c["stat"], "icon": c["icon"],
                    "tier": cur_tier, "tiers": len(lst), "exercises": items})
    db.commit()
    return out
