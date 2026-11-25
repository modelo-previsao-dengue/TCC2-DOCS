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
Gera tambem, com os dados corrigidos da v4:
  - figuras/resultados/fig_cobertura_inmet.png, a partir de
    data/model_ready_v4/42_integration_report.json (cobertura climatica por ano);
  - figuras/resultados/fig_delta_serie_longa.png, a partir de
    models/regression_v4/metrics_por_mesorregiao_v4.csv (ganho da serie longa);
  - figuras/resultados/fig_curva_aprendizado.png, a partir de
    data/model_ready_v4/51_learning_curve_report.json;
  - figuras/resultados/fig_psi_por_ano.png, a partir de
    models/regression_v4/data_drift_psi_v4.csv;
  - figuras/resultados/fig_variantes.png, fig_walkforward.png e fig_f1_por_classe.png, a partir
    dos relatorios 46, 47 e 54 em data/model_ready_v4/;
  - figuras/resultados/fig_baselines_v4.png e fig_shap_realista.png, a partir dos relatorios
    57, 58 e 59 (lidos do working tree ou, se ausentes, de origin/main).

    python scripts/gerar_figuras.py [--modelo-previsao CAMINHO] [--so-novas]
"""

import argparse
import json
import subprocess
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter, MultipleLocator
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


def fig_cobertura_inmet(rel42):
    """Cobertura climatica por ano (relatorio do script 42), no tamanho final da pagina."""
    cob = {int(a): v for a, v in rel42["cobertura_por_ano"].items()}
    anos = sorted(cob)
    vals = [cob[a] for a in anos]
    faixas = [("#d73027", "abaixo de 50%", lambda v: v < 50),
              ("#fdae61", "de 50% a 80%", lambda v: 50 <= v < 80),
              ("#1a9850", "80% ou mais", lambda v: v >= 80)]
    cores = [next(c for c, _, f in faixas if f(v)) for v in vals]
    with plt.rc_context({"font.size": 10}):
        fig, ax = plt.subplots(figsize=(6.3, 3.4))
        ax.bar(anos, vals, color=cores, width=0.75)
        ax.axhline(80, ls="--", color="#555555", lw=1)
        ax.set_xticks(anos, [str(a) for a in anos], rotation=90, fontsize=9)
        ax.set_ylim(0, 105)
        ax.set_ylabel("Mesorregião-semanas com clima (%)")
        ax.set_xlabel("Ano epidemiológico")
        ax.grid(axis="y", alpha=0.3)
        ax.spines[["top", "right"]].set_visible(False)
        legenda = [Patch(color=c, label=r) for c, r, _ in faixas]
        legenda.append(Line2D([], [], ls="--", color="#555555", label="limiar de 80%"))
        ax.legend(handles=legenda, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=4,
                  fontsize=9, frameon=False)
        fig.tight_layout()
        fig.savefig(FIG_DIR / "fig_cobertura_inmet.png", dpi=300)
    plt.close(fig)


def fig_delta_serie_longa(metricas_meso):
    """Ganho de R2_log da serie longa (B - A, clima enriquecido) nas 137 mesorregioes."""
    piv = pd.read_csv(metricas_meso).pivot_table(index="cod_mesorregiao", columns="modelo", values="R2_log")
    g = (piv["Var B: INMET enriquecido"] - piv["Var A: INMET enriquecido"]).dropna()
    g = g.sort_values(ascending=False)
    sinal = FuncFormatter(lambda v, _: "0" if abs(v) < 1e-9 else f"{v:+.2f}".replace(".", ","))
    with plt.rc_context({"font.size": 10}):
        fig, ax = plt.subplots(figsize=(6.3, 3.6))
        ax.bar(range(len(g)), g.values, width=1.0,
               color=["#1a9850" if v > 0 else "#d73027" for v in g.values])
        ax.axhline(0, color="#333333", lw=0.8)
        ax.set_xlim(-1, len(g))
        ax.set_xticks([])
        ax.set_xlabel(f"Mesorregiões, em ordem decrescente de ganho (n = {len(g)})")
        ax.set_ylabel(r"$\Delta R^2_{\log}$ (série longa $-$ curta)")
        ax.yaxis.set_major_formatter(sinal)
        ax.grid(axis="y", alpha=0.3)
        ax.spines[["top", "right"]].set_visible(False)
        ax.legend(handles=[Patch(color="#1a9850", label=f"ganho com a série longa ({int((g > 0).sum())})"),
                           Patch(color="#d73027", label=f"perda com a série longa ({int((g < 0).sum())})")],
                  loc="upper right", fontsize=9, frameon=False)
        fig.tight_layout()
        fig.savefig(FIG_DIR / "fig_delta_serie_longa.png", dpi=300)
    plt.close(fig)


def fig_curva_aprendizado(rel51):
    """R2_log no teste por tamanho da janela de treino (relatorio do script 51)."""
    jan = sorted(rel51["windows"], key=lambda w: w["n_years"])
    anos = [w["n_years"] for w in jan]
    r2 = [w["R2_log"] for w in jan]
    tres = FuncFormatter(lambda v, _: f"{v:.3f}".replace(".", ","))
    with plt.rc_context({"font.size": 10}):
        fig, ax = plt.subplots(figsize=(6.3, 3.4))
        ax.plot(anos, r2, marker="o", color="#2166ac", lw=1.8)
        for x, y in zip(anos, r2):
            ax.annotate(f"{y:.3f}".replace(".", ","), (x, y), xytext=(0, 7), textcoords="offset points",
                        ha="center", fontsize=9)
        ax.set_xticks(anos, [str(n) for n in anos])
        ax.set_xlabel("Anos de treino (todas as janelas terminam em 2022)")
        ax.yaxis.set_major_locator(MultipleLocator(0.002))
        ax.set_ylabel(r"$R^2_{\log}$ no teste")
        ax.yaxis.set_major_formatter(tres)
        ax.set_ylim(min(r2) - 0.002, max(r2) + 0.003)
        ax.grid(alpha=0.3)
        ax.spines[["top", "right"]].set_visible(False)
        fig.tight_layout()
        fig.savefig(FIG_DIR / "fig_curva_aprendizado.png", dpi=300)
    plt.close(fig)


def fig_psi_por_ano(psi_csv):
    """PSI medio das 20 variaveis mais importantes, por ano do treino (script 50)."""
    m = pd.read_csv(psi_csv).groupby("ano")["PSI"].mean()
    dec = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))
    with plt.rc_context({"font.size": 10}):
        fig, ax = plt.subplots(figsize=(6.3, 3.4))
        ax.bar(m.index, m.values, color="#4393c3", width=0.75)
        ax.axhline(0.25, ls="--", color="#d73027", lw=1.1)
        ax.axhline(0.10, ls="--", color="#f4a582", lw=1.1)
        ax.set_xticks(m.index, [str(a) for a in m.index], rotation=90, fontsize=9)
        ax.set_xlabel("Ano do treino (variante B)")
        ax.set_ylabel("PSI médio (20 variáveis)")
        ax.yaxis.set_major_formatter(dec)
        ax.grid(axis="y", alpha=0.3)
        ax.spines[["top", "right"]].set_visible(False)
        ax.legend(handles=[Line2D([], [], ls="--", color="#d73027", label="0,25: mudança relevante"),
                           Line2D([], [], ls="--", color="#f4a582", label="0,10: mudança moderada")],
                  loc="upper right", fontsize=9, frameon=False)
        fig.tight_layout()
        fig.savefig(FIG_DIR / "fig_psi_por_ano.png", dpi=300)
    plt.close(fig)


VARIANTES = {"A": ("A: janela curta (4 anos)", "#92c5de", "o"),
             "B": ("B: série longa (22 anos)", "#2166ac", "s"),
             "C": ("C: série longa ponderada", "#d6604d", "^")}
CONJUNTOS = {"sinan_only": "Só SINAN", "inmet_bruto": "+ INMET bruto", "inmet_enriquecido": "+ INMET enriquecido"}
TRES = FuncFormatter(lambda v, _: f"{v:.3f}".replace(".", ","))
DUAS = FuncFormatter(lambda v, _: f"{v:.2f}".replace(".", ","))


def fig_variantes(rel46):
    """R2_log no teste com IC 95% por bootstrap: 3 variantes x 3 conjuntos (script 46)."""
    m = rel46["modelos"]
    with plt.rc_context({"font.size": 10}):
        fig, ax = plt.subplots(figsize=(6.3, 3.4))
        for k, (v, (rot, cor, mk)) in enumerate(VARIANTES.items()):
            xs = [i + (k - 1) * 0.22 for i in range(len(CONJUNTOS))]
            ys = [m[f"{v}_{c}"]["R2_log"] for c in CONJUNTOS]
            lo = [y - m[f"{v}_{c}"]["R2_log_CI95_lo"] for y, c in zip(ys, CONJUNTOS)]
            hi = [m[f"{v}_{c}"]["R2_log_CI95_hi"] - y for y, c in zip(ys, CONJUNTOS)]
            ax.errorbar(xs, ys, yerr=[lo, hi], fmt=mk, color=cor, ms=6, capsize=3, lw=1.2, label=rot)
        ax.set_xticks(range(len(CONJUNTOS)), list(CONJUNTOS.values()))
        ax.set_xlabel("Conjunto de atributos")
        ax.set_ylabel(r"$R^2_{\log}$ no teste")
        ax.yaxis.set_major_formatter(TRES)
        ax.grid(axis="y", alpha=0.3)
        ax.spines[["top", "right"]].set_visible(False)
        ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=3, fontsize=8.5, frameon=False)
        fig.tight_layout()
        fig.savefig(FIG_DIR / "fig_variantes.png", dpi=300)
    plt.close(fig)


def fig_walkforward(rel47):
    """R2_log por ano de teste no walk-forward, clima enriquecido (script 47)."""
    with plt.rc_context({"font.size": 10}):
        fig, ax = plt.subplots(figsize=(6.3, 3.3))
        for v, (rot, cor, mk) in VARIANTES.items():
            folds = rel47["modelos"][f"{v}_inmet_enriquecido"]["folds"]
            anos = [f["test_years"][0] for f in folds]
            ax.plot(anos, [f["R2_log"] for f in folds], marker=mk, color=cor, lw=1.6, ms=6, label=rot)
        ax.set_xticks(anos, [str(a) if a != 2026 else "2026\n(até a sem. 12)" for a in anos])
        ax.set_xlabel("Ano de teste (treino até o ano anterior)")
        ax.set_ylabel(r"$R^2_{\log}$")
        ax.yaxis.set_major_formatter(DUAS)
        ax.grid(alpha=0.3)
        ax.spines[["top", "right"]].set_visible(False)
        ax.legend(loc="lower left", fontsize=8.5, frameon=False)
        fig.tight_layout()
        fig.savefig(FIG_DIR / "fig_walkforward.png", dpi=300)
    plt.close(fig)


def fig_f1_por_classe(rel54):
    """F1 por nivel de risco do classificador, clima enriquecido (script 54)."""
    classes = [("baixo", "Baixo"), ("moderado", "Moderado"), ("alto", "Alto"), ("surto", "Muito alto")]
    with plt.rc_context({"font.size": 10}):
        fig, ax = plt.subplots(figsize=(6.3, 3.3))
        for k, (v, (rot, cor, _)) in enumerate(VARIANTES.items()):
            f1 = rel54["modelos"][f"{v}_inmet_enriquecido"]["f1_per_class"]
            xs = [i + (k - 1) * 0.26 for i in range(len(classes))]
            ax.bar(xs, [f1[c] for c, _ in classes], width=0.26, color=cor, label=rot)
        ax.set_xticks(range(len(classes)), [r for _, r in classes])
        ax.set_xlabel("Nível de risco")
        ax.set_ylabel("F1 no teste")
        ax.set_ylim(0, 1)
        ax.yaxis.set_major_formatter(DUAS)
        ax.grid(axis="y", alpha=0.3)
        ax.spines[["top", "right"]].set_visible(False)
        ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=3, fontsize=8.5, frameon=False)
        fig.tight_layout()
        fig.savefig(FIG_DIR / "fig_f1_por_classe.png", dpi=300)
    plt.close(fig)


BASELINES_V4 = [
    ("Persistência", "persistencia"),
    ("Média móvel\n(4 semanas)", "media_movel_4"),
    ("Sazonal\n(ano anterior)", "sazonal"),
    ("Climatologia", "climatologia"),
    ("Ridge", "ridge_ar"),
    ("XGBoost\nrealista", "realista"),
]
MENOS = FuncFormatter(lambda v, _: f"{v:.2f}".replace(".", ",").replace("-", "−"))


def fig_baselines_v4(rel57, rel58, rel59):
    """R2 nas duas escalas: baselines ingenuos (57), climatologia e Ridge (59) e XGBoost realista (58)."""
    m = dict(rel57["teste_agregado"])
    m["climatologia"] = rel59["climatologia"]["teste_agregado"]
    m["ridge_ar"] = rel59["ridge_ar"]["teste_agregado"]
    m["realista"] = rel58["cenarios"]["realista"]["teste_agregado"]
    r2l = [m[k]["R2_log"] for _, k in BASELINES_V4]
    r2 = [m[k]["R2"] for _, k in BASELINES_V4]
    x = np.arange(len(BASELINES_V4))
    with plt.rc_context({"font.size": 10}):
        fig, ax = plt.subplots(figsize=(6.3, 3.6))
        ax.bar(x - 0.2, r2l, 0.4, label=r"$R^2_{\log}$ (escala logarítmica)", color="#2166ac")
        ax.bar(x + 0.2, r2, 0.4, label=r"$R^2$ (escala original)", color="#d6604d")
        for xi, (a, b) in enumerate(zip(r2l, r2)):
            ax.text(xi - 0.2, max(a, 0) + 0.02, f"{a:.2f}".replace(".", ","), ha="center", fontsize=8)
            yb = b + 0.02 if b >= 0 else b - 0.09
            ax.text(xi + 0.2, yb, f"{b:.2f}".replace(".", ",").replace("-", "−"), ha="center", fontsize=8)
        ax.axhline(0, color="black", lw=0.6)
        ax.set_xticks(x, [r for r, _ in BASELINES_V4], fontsize=8.5)
        ax.set_ylabel(r"$R^2$ no teste")
        ax.yaxis.set_major_formatter(MENOS)
        ax.set_ylim(-0.85, 1.05)
        ax.grid(axis="y", alpha=0.3)
        ax.spines[["top", "right"]].set_visible(False)
        ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, fontsize=8.5, frameon=False)
        fig.tight_layout()
        fig.savefig(FIG_DIR / "fig_baselines_v4.png", dpi=300)
    plt.close(fig)


NOMES_SHAP = {
    "notificacoes": "Notificações (t)",
    "notificacoes_lag_1w": "Notificações (t−1)",
    "notificacoes_lag_2w": "Notificações (t−2)",
    "notificacoes_lag_6w": "Notificações (t−6)",
    "notificacoes_diff_1w": "Diferença semanal",
    "notificacoes_pct_change_1w": "Variação % semanal",
    "notificacoes_media_movel_2_4w": "Média de t−2 a t−4",
    "notificacoes_media_movel_4_8w": "Média de t−4 a t−8",
    "week_of_year_cos": "Semana do ano (cos)",
    "week_of_year_sin": "Semana do ano (sen)",
    "qt_confirmados_provaveis": "Confirmados ou prováveis (t)",
    "prop_confirmado_provavel": "Prop. confirmados ou prováveis (t)",
    "atraso_notificacao_medio_dias": "Atraso médio da notificação",
}
CONSOLIDADOS = {"qt_confirmados_provaveis", "prop_confirmado_provavel"}


def fig_shap_realista(rel58):
    """Top 10 do SHAP medio absoluto: modelo completo (266) e realista (203), script 58."""
    paineis = [("completo", "Modelo completo\n(266 atributos)"),
               ("realista", "Modelo realista\n(203 atributos)")]
    with plt.rc_context({"font.size": 9}):
        fig, axes = plt.subplots(1, 2, figsize=(6.3, 3.6), sharex=True)
        for ax, (chave, titulo) in zip(axes, paineis):
            top = rel58["cenarios"][chave]["shap_top10"][::-1]
            nomes = [NOMES_SHAP.get(t["feature"], t["feature"]) for t in top]
            cores = ["#d6604d" if t["feature"] in CONSOLIDADOS else "#2166ac" for t in top]
            ax.barh(range(len(top)), [t["shap_mean_abs"] for t in top], color=cores)
            ax.set_yticks(range(len(top)), nomes, fontsize=8)
            ax.set_title(titulo, fontsize=9)
            ax.xaxis.set_major_formatter(DUAS)
            ax.grid(axis="x", alpha=0.3)
            ax.spines[["top", "right"]].set_visible(False)
        fig.supxlabel("Valor SHAP absoluto médio (escala logarítmica do alvo)", fontsize=9)
        fig.legend(handles=[Patch(color="#d6604d", label="Depende da consolidação do SINAN"),
                            Patch(color="#2166ac", label="Disponível na semana t")],
                   loc="upper center", ncol=2, fontsize=8, frameon=False)
        fig.tight_layout(rect=(0, 0, 1, 0.93))
        fig.savefig(FIG_DIR / "fig_shap_realista.png", dpi=300)
    plt.close(fig)


def contagem_clima(csv, chave):
    piv = pd.read_csv(csv).pivot_table(index=chave, columns="modelo", values="R2_log")
    ganho = piv["Var B: INMET enriquecido"] - piv["Var B: SINAN-only"]
    return {"melhor_com_clima": int((ganho > 0).sum()), "total": int(len(ganho)),
            "maior_ganho": round(float(ganho.max()), 3), "maior_perda": round(float(ganho.min()), 3)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo-previsao", default=str(MONO.parent.parent / "MODELO-PREVISAO"))
    ap.add_argument("--so-novas", action="store_true",
                    help="gera apenas as figuras refeitas na revisao (cobertura, ganho da serie longa, "
                         "curva de aprendizado e PSI)")
    args = ap.parse_args()
    mp = Path(args.modelo_previsao).resolve()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    DADOS_DIR.mkdir(parents=True, exist_ok=True)

    rel42 = json.loads((mp / "data" / "model_ready_v4" / "42_integration_report.json")
                       .read_text(encoding="utf-8"))
    fig_cobertura_inmet(rel42)
    fig_delta_serie_longa(mp / "models" / "regression_v4" / "metrics_por_mesorregiao_v4.csv")
    fig_curva_aprendizado(json.loads((mp / "data" / "model_ready_v4" / "51_learning_curve_report.json")
                                     .read_text(encoding="utf-8")))
    fig_psi_por_ano(mp / "models" / "regression_v4" / "data_drift_psi_v4.csv")
    rel = lambda n: json.loads((mp / "data" / "model_ready_v4" / n).read_text(encoding="utf-8"))
    fig_variantes(rel("46_regression_v4_report.json"))
    fig_walkforward(rel("47_walkforward_v4_report.json"))
    fig_f1_por_classe(rel("54_classification_v4_report.json"))
    rel_main = lambda n: (rel(n) if (mp / "data" / "model_ready_v4" / n).exists() else json.loads(
        subprocess.check_output(["git", "-C", str(mp), "show", f"origin/main:data/model_ready_v4/{n}"])))
    rel57, rel58 = rel_main("57_avaliacao_modelos_salvos_v4_report.json"), rel_main("58_vazamento_temporal_report.json")
    fig_baselines_v4(rel57, rel58, rel_main("59_baselines_avancados_report.json"))
    fig_shap_realista(rel58)
    if args.so_novas:
        return

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
