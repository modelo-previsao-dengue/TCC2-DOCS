#!/usr/bin/env python3
"""Figuras e numeros derivados da monografia, lidos do MODELO-PREVISAO (pipeline v4).

Le os relatorios da v4 com o INMET corrigido:
  - data/model_ready_v4/57_avaliacao_modelos_salvos_v4_report.json, gerado por
    scripts/57_avaliacao_modelos_salvos_v4.py a partir dos modelos salvos do
    script 46 (baselines, desempenho por ano, momento do pico, direcao, DF);
  - models/regression_v4/57_serie_nacional_teste.csv (serie nacional do teste);
  - models/regression_v4/metrics_por_uf_v4.csv e metrics_por_mesorregiao_v4.csv.

Gera figuras/resultados/fig_baselines_vs_xgboost.png e fig_serie_nacional_teste.png
e dados/fatos_derivados.json, com o commit do MODELO-PREVISAO registrado.

    python scripts/gerar_figuras.py [--modelo-previsao CAMINHO]
"""

import argparse
import json
import subprocess
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
import pandas as pd

MONO = Path(__file__).resolve().parent.parent
FIG_DIR = MONO / "figuras" / "resultados"
DADOS_DIR = MONO / "dados"

VIRGULA = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))
COR = {"real": "#222222", "B": "#1f77b4", "A": "#9ecae1", "persistencia": "#d62728"}

ROTULOS = {
    "persistencia": "Persistência\n(semana t)",
    "media_movel_4": "Média móvel\n(4 semanas)",
    "sazonal": "Sazonal\n(ano anterior)",
    "A_sinan_only": "Janela curta\n(só SINAN)",
    "B_sinan_only": "Série longa\n(só SINAN)",
    "B_inmet_enriquecido": "Série longa\n(+ clima enriq.)",
}


def commit_de(repo):
    try:
        return subprocess.check_output(["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
                                       text=True).strip()
    except Exception:
        return None


def fig_baselines(agregado):
    nomes = list(ROTULOS)
    r2l = [agregado[n]["R2_log"] for n in nomes]
    r2 = [agregado[n]["R2"] for n in nomes]
    x = np.arange(len(nomes))
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.bar(x - 0.2, r2l, 0.4, label="R² (escala log)", color="#6baed6")
    ax.bar(x + 0.2, r2, 0.4, label="R² (escala original)", color="#d62728")
    for xi, (a, b) in enumerate(zip(r2l, r2)):
        ax.text(xi - 0.2, max(a, 0) + 0.02, f"{a:.2f}".replace(".", ","), ha="center", fontsize=8)
        ax.text(xi + 0.2, max(b, 0) + 0.02, f"{b:.2f}".replace(".", ","), ha="center", fontsize=8)
    ax.axhline(0, color="black", lw=0.6)
    ax.set_xticks(x, [ROTULOS[n] for n in nomes], fontsize=9)
    ax.set_ylabel("R²")
    ax.yaxis.set_major_formatter(VIRGULA)
    ax.set_ylim(-0.8, 1.05)
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig_baselines_vs_xgboost.png", dpi=300)
    plt.close(fig)


def fig_serie_nacional(serie):
    serie = serie.sort_values(["ano", "semana_epidemiologica"]).reset_index(drop=True)
    x = np.arange(len(serie))
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(x, serie["real"] / 1e3, color=COR["real"], lw=2, label="Notificações observadas (t+4)")
    ax.plot(x, serie["B_inmet_enriquecido"] / 1e3, color=COR["B"], lw=1.6,
            label="XGBoost, série longa + clima enriquecido")
    ax.plot(x, serie["persistencia"] / 1e3, color=COR["persistencia"], lw=1.2, ls="--",
            label="Persistência (valor da semana t)")
    inicio = serie.groupby("ano").head(1).index
    ax.set_xticks(inicio, [str(a) for a in serie.loc[inicio, "ano"]])
    for i in inicio[1:]:
        ax.axvline(i, color="gray", lw=0.5, ls=":")
    ax.set_xlabel("Semana epidemiológica de referência (conjunto de teste)")
    ax.set_ylabel("Notificações por semana (milhares)")
    ax.yaxis.set_major_formatter(VIRGULA)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig_serie_nacional_teste.png", dpi=300)
    plt.close(fig)


def contagem_clima(csv, chave):
    piv = pd.read_csv(csv).pivot_table(index=chave, columns="modelo", values="R2_log")
    ganho = piv["Var B: INMET enriquecido"] - piv["Var B: SINAN-only"]
    return {"melhor_com_clima": int((ganho > 0).sum()), "total": int(len(ganho)),
            "maior_ganho": round(float(ganho.max()), 3), "maior_perda": round(float(ganho.min()), 3)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo-previsao", default=str(MONO.parent.parent / "MODELO-PREVISAO"))
    mp = Path(ap.parse_args().modelo_previsao).resolve()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    DADOS_DIR.mkdir(parents=True, exist_ok=True)

    rel = json.loads((mp / "data" / "model_ready_v4" / "57_avaliacao_modelos_salvos_v4_report.json")
                     .read_text(encoding="utf-8"))
    serie = pd.read_csv(mp / "models" / "regression_v4" / "57_serie_nacional_teste.csv")

    fatos = {
        "modelo_previsao_commit": commit_de(mp),
        "n_teste": rel["n_teste"],
        "clima_por_uf_variante_B": contagem_clima(mp / "models" / "regression_v4" / "metrics_por_uf_v4.csv", "uf"),
        "clima_por_mesorregiao_variante_B": contagem_clima(
            mp / "models" / "regression_v4" / "metrics_por_mesorregiao_v4.csv", "cod_mesorregiao"),
        "pico_nacional_semana": {
            str(a): {c: int(g.loc[g[c].idxmax(), "semana_epidemiologica"])
                     for c in ("real", "B_inmet_enriquecido", "persistencia")}
            for a, g in serie.groupby("ano") if a in (2024, 2025)
        },
    }

    fig_baselines(rel["teste_agregado"])
    fig_serie_nacional(serie)
    (DADOS_DIR / "fatos_derivados.json").write_text(
        json.dumps(fatos, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(fatos, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
