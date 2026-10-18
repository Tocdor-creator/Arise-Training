# ⚔ ARISE — Shadow Training

App/site de **treino de calistenia em casa** com a estética do **Sistema de Solo Leveling**: níveis, ranks (E → D → C → B → A → S → Nível Nacional → Monarca), EXP por exercício, cadência guiada por metrônomo e **Missão Diária progressiva** (ex.: prancha de 1:00 hoje → 1:10 amanhã se você conseguir).

- **Backend:** Python 3 + Flask + SQLite (roda no Termux do celular, sem compilar nada)
- **Frontend:** SPA em HTML/CSS/JS puro (sem build), instalável na tela inicial
- **Exercícios e GIFs:** [ExerciseDB](https://oss.exercisedb.dev) (API pública e gratuita, sem chave)

## Como funciona

### 1. Despertar (cadastro)
Nome de caçador, usuário/senha → **peso, altura, idade, sexo** (calcula IMC) → **objetivo** (perder gordura, massa, força, resistência, saúde) + barra fixa sim/não + baixo impacto → **Teste de Despertar** (máximo de flexões, agachamentos, prancha em segundos e barras).

Com isso o Sistema escolhe o **tier inicial** de cada árvore de exercícios. Idade ≥ 55 ou IMC ≥ 32 sugere automaticamente o modo *baixo impacto* (remove saltos).

### 2. Árvores de habilidade (progressões)
7 cadeias, cada uma do mais fácil ao mais difícil — com GIF da ExerciseDB:

| Cadeia | Atributo | Exemplo de progressão |
|---|---|---|
| Empurrar | STR | parede → inclinada → joelhos → clássica → diamante → declinada → arqueiro → palma → parada de mão → **um braço** |
| Puxar | STR | remada com toalha → … → remada invertida → (com barra) chin-up → pull-up → L → arqueiro → **muscle-up** |
| Pernas | AGI | agachamento com apoio → livre → afundo → búlgaro → … → sissy → unilateral → **pistol** |
| Posterior & Glúteos | AGI | ponte → ponte com marcha → unilateral → pés elevados → **nórdico** |
| Núcleo | VIT | crunch → dead bug → bicicleta → … → V-sit → L-sit → (barra) elevação de pernas → **front lever** |
| Condicionamento | VIT | joelho alto → polichinelo → escalador → urso → patinador → **burpee** |
| Tríceps & Mergulho | STR | mergulho no chão → cadeira → coreano → **paralelas** |

Cada exercício tem **rank próprio** (E→D→C→B→A→S). Batendo a meta em todas as séries, o exercício sobe um rank e a meta de repetições aumenta. Ao chegar em **S (dominado)** você evolui para o próximo tier — desde que seu **nível de jogador** alcance o exigido (tier × 3). Ou seja: quanto mais você sobe de nível, mais difíceis ficam os exercícios.

### 3. Dungeon (treino do dia)
Alterna **Portão Azul** (empurrar/pernas/núcleo/cardio…) e **Portão Vermelho** (puxar/posterior/núcleo/pernas…). Número de exercícios e séries crescem com o nível (4 → 5 → 6 exercícios; +1 série no nível 20 e 45).

Séries, repetições, descanso e **cadência** dependem do objetivo:

| Objetivo | Reps | Cadência (desce-segura-sobe) | Descanso |
|---|---|---|---|
| Perder gordura | 12–20 | 1-0-1 | 40s |
| Ganhar massa | 8–15 | 3-1-1 | 75s |
| Força & habilidades | 5–10 | 2-1-1 | 120s |
| Resistência | 15–25 | 1-0-1 | 30s |
| Saúde geral | 10–15 | 2-0-2 | 60s |

**Modo cadência:** metrônomo com bipes (DESCE / SEGURA / SOBE), anel animado e voz contando as repetições. Rende **+15% EXP** e +1 PER. Exercícios de tempo (prancha, L-sit, cardio) usam cronômetro.

### 4. Missão Diária — "Preparação para se tornar forte"
Todo dia: **Prancha** + uma missão rotativa (flexões/abdominais/agachamentos no total do dia, ou cadeira na parede).
- ✅ Conseguiu → ganha EXP e a meta de amanhã **sobe** (prancha +10s).
- ❌ Falhou → meta mantida; 2 falhas seguidas → o Sistema reduz a meta.
- Completar tudo → bônus de EXP, +1 INT e **sequência 🔥**. A sequência multiplica o EXP das missões (+5%/dia, até ×2) e dos treinos (+3%/dia, até ×1,3).
- Pulou um dia → **Zona de Penalidade**: sequência zerada e missão extra (3 min de joelho alto).

### 5. Modo gestante 🤰
Opção no cadastro e no Perfil (para sexo feminino/outro): informe a **semana de gestação** e confirme a **liberação médica** (obrigatória). A semana avança sozinha com o calendário. Baseado nas recomendações gerais do ACOG/OMS para gestação sem complicações:

- **Árvores próprias** (o progresso normal fica guardado e volta quando o modo é desligado): flexão escapular/parede/inclinada, remada com toalha, meio agachamento → agachamento com apoio, abdução de quadril em pé/de lado, báscula pélvica, prancha lateral nos joelhos, marcha na parede, passos laterais, mergulho sentada.
- **Nunca**: saltos, crunch/abdominais, inversões, barra, exercícios de equilíbrio arriscado.
- **A partir da semana 13**: sem exercícios deitada de barriga para cima (ponte, dead bug, báscula deitada).
- **3º trimestre (28+)**: sem flexão inclinada baixa e sem afundo.
- **Intensidade moderada**: máx. 3 séries, 8–15 reps, cadência 2-0-2 sem pausas (não prender a respiração), descanso ≥ 60s, até 5 exercícios.
- **Missões**: Assoalho pélvico (Kegel) fixa + caminhada / cadeira na parede / agachamentos com apoio / flexões na parede, **com teto de meta** e **sem zona de penalidade**.
- Sinais de alerta para parar (sangramento, contrações, tontura, dor no peito etc.) aparecem no cadastro, na dungeon e dicas de hidratação no descanso.

> O app não substitui o acompanhamento do obstetra.

### 6. Outras telas
- **Status:** nível, rank, título, HP/MP, EXP, atributos (+3 pontos livres por nível para distribuir).
- **Habilidades:** árvores completas; exercícios bloqueados aparecem em silhueta. Dá para voltar a um tier já superado (dia de dor).
- **Arquivo:** 371 exercícios de peso corporal da ExerciseDB com GIF, filtro por parte do corpo, busca ao vivo na API e botão para sincronizar o catálogo.
- **Histórico:** EXP por dungeon, gráfico de peso, recordes das missões.

## Rodar no PC

```
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python app.py
```
Abra http://localhost:5050

## Servidor caseiro (celular com Termux)

Instalado em `~/arise-training` no Galaxy Z Flip5 (Tailscale `100.98.189.36`), porta **5050**.

```
sh ~/arise-training/servidor.sh iniciar | parar | reiniciar | status | log
```

Acesse de qualquer aparelho na sua Tailnet: **http://100.98.189.36:5050** — no Chrome do celular use ⋮ → *Adicionar à tela inicial* para virar app.

Para atualizar a partir do PC: `powershell -File deploy.ps1`

## Dados
- `arise.db` — SQLite com jogadores, progresso e histórico (faça backup de vez em quando)
- `cache/gifs/` — GIFs baixados da ExerciseDB (o app funciona offline depois do primeiro download)
- `data/exercisedb_bodyweight.json` — snapshot do catálogo da API
