"""Catálogo de progressões de calistenia.

Cada "cadeia" (chain) é uma linha de evolução: o jogador começa num tier
(definido pelo teste de despertar) e sobe de tier ao dominar o exercício.
Os GIFs e as informações de músculos vêm da API pública ExerciseDB
(https://oss.exercisedb.dev) — `db` é o exerciseId lá.

type:   "reps" (repetições) ou "time" (segundos)
impact: exercício com salto — evitado no modo baixo impacto
bar:    precisa de barra fixa
"""

CHAINS = {
    "push": {
        "name": "Empurrar",
        "stat": "STR",
        "icon": "⚔",
        "exercises": [
            {"key": "wall_pushup", "name": "Flexão na Parede", "db": "LEH9jxP",
             "cue": "Corpo reto como uma prancha, peito vai até a parede e volta."},
            {"key": "incline_pushup", "name": "Flexão Inclinada", "db": "B1EVP9F",
             "cue": "Mãos num sofá/cadeira firme. Quanto mais baixo o apoio, mais difícil."},
            {"key": "knee_pushup", "name": "Flexão com Joelhos", "db": "ZOuKWir",
             "cue": "Joelhos no chão, quadril alinhado. Desça até o peito quase tocar o chão."},
            {"key": "pushup", "name": "Flexão Clássica", "db": "I4hDWkc",
             "cue": "Mãos um pouco além dos ombros, cotovelos a ~45°, abdômen travado."},
            {"key": "diamond_pushup", "name": "Flexão Diamante", "db": "soIB2rj",
             "cue": "Mãos juntas formando um diamante sob o peito. Foco em tríceps."},
            {"key": "decline_pushup", "name": "Flexão Declinada", "db": "i5cEhka",
             "cue": "Pés elevados num sofá/cadeira. Mais carga no peitoral superior e ombros."},
            {"key": "archer_pushup", "name": "Flexão Arqueiro", "db": "A9qxk2F",
             "cue": "Mãos bem abertas, desça para um lado mantendo o outro braço esticado."},
            {"key": "clap_pushup", "name": "Flexão com Palma", "db": "wigSg76", "impact": True,
             "cue": "Empurre explosivo, bata palma no ar e amorteça a queda."},
            {"key": "hspu", "name": "Flexão de Parada de Mão", "db": "rQxwMxO",
             "cue": "De cabeça para baixo apoiado na parede, desça a cabeça até perto do chão."},
            {"key": "one_arm_pushup", "name": "Flexão de Um Braço", "db": "MUic5zN",
             "cue": "Pernas afastadas para equilíbrio, um braço nas costas. Nível Monarca."},
        ],
    },
    "pull": {
        "name": "Puxar",
        "stat": "STR",
        "icon": "⛓",
        "exercises": [
            {"key": "towel_row", "name": "Remada em Pé com Toalha", "db": "uTv34oq",
             "cue": "Toalha presa na maçaneta, corpo inclinado para trás. Puxe o peito até as mãos."},
            {"key": "squat_towel_row", "name": "Remada Agachada com Toalha", "db": "BReCuOn",
             "cue": "Mesma remada partindo do agachamento — mais inclinação, mais carga."},
            {"key": "reverse_pushup", "name": "Elevação de Cotovelos", "db": "wbUYILZ",
             "cue": "Deitado de costas, empurre os cotovelos no chão para elevar o tronco."},
            {"key": "inverted_row_knees", "name": "Remada Invertida (joelhos dobrados)", "db": "VPPtusI",
             "cue": "Debaixo de uma mesa firme, segure a borda e puxe o peito até ela."},
            {"key": "inverted_row", "name": "Remada Invertida", "db": "uX3sUBz",
             "cue": "Mesma remada com pernas esticadas. Corpo reto do calcanhar à cabeça."},
            {"key": "single_towel_row", "name": "Remada Unilateral com Toalha", "db": "bKWbrTA",
             "cue": "Um braço só na toalha. Gire o tronco levemente ao puxar."},
            {"key": "scap_pullup", "name": "Retração Escapular na Barra", "db": "uTBt1HV", "bar": True,
             "cue": "Pendurado, braços esticados, puxe só as escápulas para baixo."},
            {"key": "chinup", "name": "Barra Supinada (Chin-up)", "db": "T2mxWqc", "bar": True,
             "cue": "Palmas para você, suba até o queixo passar a barra."},
            {"key": "pullup", "name": "Barra Fixa (Pull-up)", "db": "lBDjFxJ", "bar": True,
             "cue": "Palmas para frente, peito em direção à barra, sem balançar."},
            {"key": "l_pullup", "name": "Barra em L", "db": "d1GgzTU", "bar": True,
             "cue": "Pernas esticadas a 90° durante toda a barra."},
            {"key": "archer_pullup", "name": "Barra Arqueiro", "db": "72BC5Za", "bar": True,
             "cue": "Pegada bem aberta, suba em direção a uma das mãos."},
            {"key": "muscle_up", "name": "Muscle-up", "db": "yJUHKTn", "bar": True,
             "cue": "Barra explosiva e transição por cima da barra. Nível Monarca."},
        ],
    },
    "legs": {
        "name": "Pernas",
        "stat": "AGI",
        "icon": "⚡",
        "exercises": [
            {"key": "assisted_squat", "name": "Agachamento com Apoio", "db": "b63ZzGe",
             "cue": "Segure num batente de porta e agache fundo, calcanhares no chão."},
            {"key": "squat", "name": "Agachamento Livre", "db": "6YUfHPL",
             "cue": "Pés na largura dos ombros, quadril para trás, joelhos seguem a ponta dos pés."},
            {"key": "lunge", "name": "Avanço (Afundo)", "db": "kMzUs9Y",
             "cue": "Passo à frente, joelho de trás quase toca o chão. Alterne as pernas."},
            {"key": "split_squat", "name": "Agachamento Búlgaro no Chão", "db": "9E25EOx",
             "cue": "Posição de afundo fixa, suba e desça sem mexer os pés."},
            {"key": "curtsey_squat", "name": "Agachamento Cruzado", "db": "gUjqdei",
             "cue": "Cruze uma perna por trás da outra ao descer. Glúteo médio agradece."},
            {"key": "jump_squat", "name": "Agachamento com Salto", "db": "LIlE5Tn", "impact": True,
             "cue": "Agache e exploda para cima. Aterrisse macio, já descendo."},
            {"key": "jump_lunge", "name": "Afundo com Salto", "db": "PM1PZjg", "impact": True,
             "cue": "Troque as pernas no ar a cada repetição."},
            {"key": "sissy_squat", "name": "Sissy Squat", "db": "xdYPUtE",
             "cue": "Segure num apoio, joelhos à frente e tronco para trás. Quadríceps puro."},
            {"key": "single_leg_squat", "name": "Agachamento Unilateral (caixa)", "db": "C31LMnP",
             "cue": "Numa perna só, sente numa cadeira e levante sem impulso."},
            {"key": "pistol", "name": "Pistol Squat", "db": "nqs5HGV",
             "cue": "Agachamento completo numa perna, a outra esticada à frente."},
        ],
    },
    "posterior": {
        "name": "Posterior & Glúteos",
        "stat": "AGI",
        "icon": "🜂",
        "exercises": [
            {"key": "glute_bridge", "name": "Ponte de Glúteo", "db": "u0cNiij",
             "cue": "Deitado, pés no chão, eleve o quadril apertando os glúteos no topo."},
            {"key": "bridge_march", "name": "Ponte com Marcha", "db": "GibBPPg",
             "cue": "No topo da ponte, levante um joelho de cada vez sem deixar o quadril cair."},
            {"key": "single_leg_bridge", "name": "Ponte Unilateral", "db": "rmEukuS",
             "cue": "Uma perna esticada no ar, suba o quadril só com a outra."},
            {"key": "bench_glute_bridge", "name": "Ponte com Pés Elevados", "db": "aWedzZX",
             "cue": "Pés num sofá/cadeira — maior amplitude para posterior de coxa."},
            {"key": "nordic_floor", "name": "Nórdico Assistido", "db": "ZSY3MsL",
             "cue": "Joelhos no chão, pés presos sob o sofá. Desça devagar controlando."},
        ],
    },
    "core": {
        "name": "Núcleo",
        "stat": "VIT",
        "icon": "◈",
        "exercises": [
            {"key": "crunch", "name": "Abdominal Crunch", "db": "TFqbd8t",
             "cue": "Enrole a coluna tirando só as escápulas do chão. Sem puxar o pescoço."},
            {"key": "dead_bug", "name": "Dead Bug", "db": "iny3m5y",
             "cue": "Lombar colada no chão, estenda braço e perna opostos devagar."},
            {"key": "bicycle_crunch", "name": "Abdominal Bicicleta", "db": "1ZFqTDN",
             "cue": "Cotovelo em direção ao joelho oposto, pedalando no ar."},
            {"key": "reverse_crunch", "name": "Abdominal Reverso", "db": "nCU1Ekp",
             "cue": "Traga os joelhos ao peito tirando o quadril do chão."},
            {"key": "russian_twist", "name": "Russian Twist", "db": "XVDdcoj",
             "cue": "Tronco inclinado, pés fora do chão se conseguir, gire de lado a lado."},
            {"key": "leg_hip_raise", "name": "Elevação de Pernas e Quadril", "db": "9IxJdtC",
             "cue": "Pernas esticadas sobem e o quadril sai do chão no final."},
            {"key": "jackknife", "name": "Canivete (Jackknife)", "db": "mbkgB44",
             "cue": "Mãos e pés se encontram no alto ao mesmo tempo."},
            {"key": "v_sit", "name": "V-Sit", "db": "ZuXu4Eq", "type": "time",
             "cue": "Equilibre-se no glúteo com pernas e tronco formando um V."},
            {"key": "l_sit", "name": "L-Sit no Chão", "db": "UpWmA5E", "type": "time",
             "cue": "Mãos no chão (ou em livros), tire o corpo do chão com pernas esticadas."},
            {"key": "hanging_leg_raise", "name": "Elevação de Pernas na Barra", "db": "I3tsCnC", "bar": True,
             "cue": "Pendurado, suba as pernas esticadas até 90° sem balançar."},
            {"key": "front_lever", "name": "Front Lever", "db": "PkCN2lv", "bar": True, "type": "time",
             "cue": "Corpo horizontal pendurado na barra. Habilidade de rank S."},
        ],
    },
    "cardio": {
        "name": "Condicionamento",
        "stat": "VIT",
        "icon": "✦",
        "exercises": [
            {"key": "high_knee_wall", "name": "Joelho Alto na Parede", "db": "ealLwvX", "type": "time",
             "cue": "Mãos na parede, alterne joelhos para cima em ritmo constante."},
            {"key": "jumping_jack", "name": "Polichinelo", "db": "1g5bPpA", "type": "time", "impact": True,
             "cue": "Abra e feche pernas e braços no ritmo. Aterrisse na ponta dos pés."},
            {"key": "mountain_climber", "name": "Escalador", "db": "RJgzwny", "type": "time",
             "cue": "Em posição de prancha, traga os joelhos ao peito alternando rápido."},
            {"key": "bear_crawl", "name": "Caminhada do Urso", "db": "0Yz8WdV", "type": "time",
             "cue": "Quatro apoios com joelhos suspensos, ande para frente e para trás."},
            {"key": "skater_hops", "name": "Salto do Patinador", "db": "zfNHMN9", "type": "time", "impact": True,
             "cue": "Salte lateralmente de uma perna para a outra."},
            {"key": "burpee", "name": "Burpee", "db": "dK9394r", "impact": True,
             "cue": "Agacha, prancha, flexão opcional, volta e salta. O teste final do Sistema."},
            {"key": "jack_burpee", "name": "Burpee com Polichinelo", "db": "mr7pkqP", "impact": True,
             "cue": "Burpee completo seguido de um polichinelo."},
        ],
    },
    "dips": {
        "name": "Tríceps & Mergulho",
        "stat": "STR",
        "icon": "⬡",
        "exercises": [
            {"key": "floor_dip", "name": "Mergulho no Chão", "db": "7aVz15j",
             "cue": "Sentado, mãos atrás do quadril, empurre o chão estendendo os cotovelos."},
            {"key": "bench_dip_bent", "name": "Mergulho na Cadeira (joelhos dobrados)", "db": "RrLske5",
             "cue": "Mãos na borda de uma cadeira firme, desça até cotovelos a 90°."},
            {"key": "bench_dip", "name": "Mergulho na Cadeira (pernas esticadas)", "db": "X6C6i5Y",
             "cue": "Mesmo movimento com pernas esticadas — mais carga."},
            {"key": "korean_dip", "name": "Mergulho Coreano", "db": "rWoBmi5",
             "cue": "Mãos atrás do corpo numa barra/bancada alta. Exige mobilidade de ombro."},
            {"key": "chest_dip", "name": "Paralelas", "db": "9WTm7dq",
             "cue": "Em duas cadeiras firmes ou paralelas, desça o corpo todo e suba."},
        ],
    },
}

# Treino alterna entre dois "portões" de dungeon.
SPLITS = {
    "A": ["push", "legs", "core", "cardio", "dips", "posterior"],
    "B": ["pull", "posterior", "core", "legs", "push", "cardio"],
}

# Missões diárias progressivas. `step` é o quanto a meta sobe a cada sucesso.
MISSIONS = {
    "plank": {"name": "Prancha", "type": "time", "start": 30, "step": 10, "min": 15, "icon": "▬",
              "desc": "Prancha nos antebraços, corpo reto, sem deixar o quadril cair."},
    "wall_sit": {"name": "Cadeira na Parede", "type": "time", "start": 30, "step": 10, "min": 15, "db": "sVQCCeG",
                 "icon": "⊏", "desc": "Costas na parede, joelhos a 90°, segure a posição."},
    "pushups": {"name": "Flexões (total do dia)", "type": "reps", "start": 20, "step": 5, "min": 5, "db": "I4hDWkc",
                "icon": "⚔", "desc": "Some flexões ao longo do dia, em quantas séries quiser (joelhos valem)."},
    "situps": {"name": "Abdominais (total do dia)", "type": "reps", "start": 30, "step": 5, "min": 10, "db": "TFqbd8t",
               "icon": "◈", "desc": "Some abdominais ao longo do dia, em quantas séries quiser."},
    "squats": {"name": "Agachamentos (total do dia)", "type": "reps", "start": 30, "step": 10, "min": 10, "db": "6YUfHPL",
               "icon": "⚡", "desc": "Some agachamentos ao longo do dia, em quantas séries quiser."},
}
ROTATING_MISSIONS = ["pushups", "wall_sit", "squats", "situps"]

PENALTY_MISSION = {"key": "penalty", "name": "Sobreviver: Joelho Alto", "type": "time", "target": 180,
                   "db": "ealLwvX", "icon": "☠",
                   "desc": "Você não completou a missão de ontem. Corra no lugar com joelho alto por 3 minutos."}

# ------------------------------------------------------------------ modo gestante
# Baseado nas recomendações gerais do ACOG/OMS para exercício na gestação sem
# complicações: intensidade moderada, sem saltos/impacto, sem risco de queda,
# sem inversões, sem abdominais tipo crunch e evitando ficar deitada de barriga
# para cima (supine) a partir do 2º trimestre.
#   supine:   deitada de costas — só até a semana SUPINE_UNTIL_WEEK
#   no_third: evitado no 3º trimestre (barriga/equilíbrio)
SUPINE_UNTIL_WEEK = 12
THIRD_TRIMESTER_WEEK = 28

PRENATAL_CHAINS = {
    "push": [
        {"key": "pn_incline_scap", "name": "Flexão Escapular Inclinada", "db": "GdMa1ET",
         "cue": "Mãos num apoio alto (bancada/mesa firme), braços esticados. Aproxime e afaste as escápulas."},
        {"key": "pn_wall_pushup", "name": "Flexão na Parede", "db": "LEH9jxP",
         "cue": "Mãos na parede na altura do peito. Desça devagar expirando ao empurrar."},
        {"key": "pn_incline_pushup", "name": "Flexão Inclinada (sofá/mesa)", "db": "B1EVP9F",
         "cue": "Mãos num apoio firme na altura do quadril. Corpo reto, sem prender a respiração."},
        {"key": "pn_box_pushup", "name": "Flexão Inclinada Baixa", "db": "F7vjXqT", "no_third": True,
         "cue": "Apoio mais baixo (degrau/caixa firme). Evite no 3º trimestre."},
    ],
    "pull": [
        {"key": "pn_arm_open", "name": "Abertura de Braços (postura)", "db": "JF8AkMX",
         "cue": "Em pé, braços à frente, abra puxando as escápulas para trás. Ótimo para a postura."},
        {"key": "pn_towel_row", "name": "Remada em Pé com Toalha", "db": "uTv34oq",
         "cue": "Toalha presa na maçaneta, incline pouco o corpo e puxe expirando."},
        {"key": "pn_single_towel_row", "name": "Remada Unilateral com Toalha", "db": "bKWbrTA",
         "cue": "Um braço de cada vez, base firme com os pés afastados."},
    ],
    "legs": [
        {"key": "pn_half_squat", "name": "Meio Agachamento", "db": "ia6kIIl",
         "cue": "Desça só até a metade, como quem vai sentar, e suba expirando."},
        {"key": "pn_assisted_squat", "name": "Agachamento com Apoio", "db": "b63ZzGe",
         "cue": "Segure numa cadeira/batente, pés um pouco abertos, desça até onde for confortável."},
        {"key": "pn_squat", "name": "Agachamento Livre", "db": "6YUfHPL",
         "cue": "Pés afastados, pontas para fora. Tenha uma cadeira atrás para segurança."},
        {"key": "pn_squat_reach", "name": "Agachamento com Elevação dos Braços", "db": "QChZi3x",
         "cue": "Agache e, ao subir, eleve os braços. Movimento controlado, sem pressa."},
        {"key": "pn_split_squat", "name": "Afundo Estático com Apoio", "db": "9E25EOx", "no_third": True,
         "cue": "Uma mão na parede para equilíbrio. Evite no 3º trimestre."},
    ],
    "posterior": [
        {"key": "pn_leg_curl", "name": "Flexão de Joelho em Pé", "db": "C5jncD2",
         "cue": "Apoie as mãos na parede e leve o calcanhar em direção ao glúteo."},
        {"key": "pn_side_leg_raise", "name": "Abdução de Quadril em Pé", "db": "7WaDzyL",
         "cue": "Segure numa cadeira e eleve a perna para o lado, tronco reto."},
        {"key": "pn_side_lying_abd", "name": "Abdução Deitada de Lado", "db": "mQ1tBXn",
         "cue": "Deitada de lado (posição recomendada na gestação), eleve a perna de cima."},
        {"key": "pn_glute_bridge", "name": "Ponte de Glúteo", "db": "u0cNiij", "supine": True,
         "cue": "Deitada de costas — apenas no 1º trimestre."},
    ],
    "core": [
        {"key": "pn_standing_tilt", "name": "Báscula Pélvica em Pé", "db": "cuKYxhu",
         "cue": "Encaixe e solte o quadril suavemente, contraindo o abdômen profundo ao expirar."},
        {"key": "pn_pelvic_tilt", "name": "Báscula Pélvica Deitada", "db": "NKJ8o6x", "supine": True,
         "cue": "Deitada de costas — apenas no 1º trimestre."},
        {"key": "pn_dead_bug", "name": "Dead Bug Leve", "db": "iny3m5y", "supine": True,
         "cue": "Deitada de costas — apenas no 1º trimestre. Pare se a barriga formar um 'cone'."},
        {"key": "pn_side_plank", "name": "Prancha Lateral nos Joelhos", "db": "5VXmnV5", "type": "time",
         "cue": "De lado, apoiada no antebraço e nos joelhos. Respire o tempo todo."},
    ],
    "cardio": [
        {"key": "pn_march", "name": "Marcha na Parede", "db": "ealLwvX", "type": "time",
         "cue": "Mãos na parede, marche em ritmo confortável. Você deve conseguir conversar."},
        {"key": "pn_step", "name": "Passo à Frente e Atrás", "db": "fNGumX0", "type": "time",
         "cue": "Passos curtos e ritmados, sem saltar."},
        {"key": "pn_ski_step", "name": "Passo Lateral", "db": "5MRH8H2", "type": "time",
         "cue": "Passos laterais leves de um lado para o outro."},
    ],
    "dips": [
        {"key": "pn_floor_dip", "name": "Mergulho Sentada no Chão", "db": "7aVz15j",
         "cue": "Sentada, mãos atrás do quadril, estenda os cotovelos. Movimento curto."},
        {"key": "pn_chair_dip", "name": "Mergulho na Cadeira (joelhos dobrados)", "db": "RrLske5",
         "cue": "Cadeira encostada na parede. Desça pouco, sem forçar os ombros."},
    ],
}

PRENATAL_MISSIONS = {
    "kegel": {"name": "Assoalho Pélvico (Kegel)", "type": "reps", "start": 10, "step": 2, "min": 6, "cap": 30,
              "icon": "✿", "desc": "Contraia o assoalho pélvico por 3–5s e relaxe o mesmo tempo. Conte as contrações do dia."},
    "walk": {"name": "Caminhada", "type": "time", "start": 600, "step": 120, "min": 300, "cap": 1800, "db": "ealLwvX",
             "icon": "➶", "desc": "Caminhe em ritmo em que ainda consiga conversar (teste da fala)."},
    "pn_wall_sit": {"name": "Cadeira na Parede", "type": "time", "start": 20, "step": 5, "min": 10, "cap": 60,
                    "db": "sVQCCeG", "icon": "⊏", "desc": "Costas na parede, joelhos a ~90°, respirando sempre."},
    "pn_squats": {"name": "Agachamentos com Apoio (total)", "type": "reps", "start": 15, "step": 5, "min": 10,
                  "cap": 60, "db": "b63ZzGe", "icon": "⚡", "desc": "Some agachamentos com apoio ao longo do dia."},
    "pn_wall_pushups": {"name": "Flexões na Parede (total)", "type": "reps", "start": 10, "step": 3, "min": 6,
                        "cap": 40, "db": "LEH9jxP", "icon": "⚔", "desc": "Some flexões na parede ao longo do dia."},
}
PRENATAL_MAIN_MISSION = "kegel"
PRENATAL_ROTATING = ["walk", "pn_wall_sit", "pn_squats", "pn_wall_pushups"]
ALL_MISSIONS = {**MISSIONS, **PRENATAL_MISSIONS}


def full_chain(chain_key, pregnant=False):
    return PRENATAL_CHAINS[chain_key] if pregnant else CHAINS[chain_key]["exercises"]


def chain_exercises(chain_key, has_bar=False, low_impact=False, preg_week=None):
    """Lista de exercícios da cadeia filtrada pelo equipamento/restrições.

    `preg_week` (semana de gestação) ativa as árvores de gestante.
    Retorna tuplas (tier, exercise) com tier começando em 1.
    """
    pregnant = preg_week is not None
    out = []
    for ex in full_chain(chain_key, pregnant):
        if ex.get("bar") and not has_bar:
            continue
        if ex.get("impact") and (low_impact or pregnant):
            continue
        if pregnant and ex.get("supine") and preg_week > SUPINE_UNTIL_WEEK:
            continue
        if pregnant and ex.get("no_third") and preg_week >= THIRD_TRIMESTER_WEEK:
            continue
        out.append(ex)
    return list(enumerate(out, start=1))


EXERCISE_BY_KEY = {ex["key"]: (ck, ex) for ck, c in CHAINS.items() for ex in c["exercises"]}
EXERCISE_BY_KEY.update({ex["key"]: (ck, ex) for ck, lst in PRENATAL_CHAINS.items() for ex in lst})
