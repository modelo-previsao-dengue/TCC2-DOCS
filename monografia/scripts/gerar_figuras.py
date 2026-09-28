#!/usr/bin/env python3
"""Figuras e numeros derivados da monografia, lidos do MODELO-PREVISAO.

Os relatorios JSON da pipeline v3 (scripts 20-33 do MODELO-PREVISAO) ja trazem
a maior parte dos numeros do texto. Este script calcula o que eles nao trazem
(desempenho por ano de teste, recorte do Distrito Federal, contagem de UFs e
mesorregioes em que o clima ajuda) e gera as figuras que comparam o XGBoost
com os baselines. Tudo vai para figuras/resultados/ e dados/fatos_derivados.json,
com o commit do MODELO-PREVISAO registrado para rastreabilidade.

Precisa do ambiente do MODELO-PREVISAO (xgboost, pandas, matplotlib):
    <MODELO-PREVISAO>/.venv/bin/python scripts/gerar_figuras.py [--modelo-previsao CAMINHO]
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
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, r2_score

MONO = Path(__file__).resolve().parent.parent
FIG_DIR = MONO / "figuras" / "resultados"
DADOS_DIR = MONO / "dados"

VIRGULA = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))
COD_MESO_DF = 5301  # Distrito Federal: uma unica mesorregiao
ANOS_TESTE = [2024, 2025, 2026]
COR = {"real": "#222222", "C": "#1f77b4", "A": "#9ecae1", "persistencia": "#d62728",
       "media_movel_4": "#ff9896", "sazonal": "#c7c7c7", "B": "#6baed6"}


def commit_de(repo):
    try:
        return subprocess.check_output(["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
                                       text=True).strip()
    except Exception:
        return None


def carregar(mp):
    dados = mp / "data" / "model_ready_v3"
    test = pd.read_parquet(dados / "test_v3.parquet")
    test = test.sort_values(["cod_mesorregiao", "ano", "semana_epidemiologica"]).reset_index(drop=True)
    schema = pd.read_csv(dados / "feature_schema_v3.csv")
    sinan = schema.loc[schema["category"] == "sinan", "feature"].tolist()
    bruto = schema.loc[schema["category"] == "inmet_bruto", "feature"].tolist()
    enriq = schema.loc[schema["category"].isin(
        ["inmet_lag_bio", "inmet_mm_bio", "inmet_anomalia"]), "feature"].tolist()
    feats = {"A": sinan, "B": sinan + bruto, "C": sinan + bruto + enriq}
    arquivos = {"A": "model_a_sinan_only", "B": "model_b_inmet_bruto", "C": "model_c_inmet_enriquecido"}
    prev = {}
    for k, nome in arquivos.items():
        m = xgb.XGBRegressor()
        m.load_model(str(mp / "models" / "regression_v3" / f"{nome}.ubj"))
        prev[k] = np.maximum(np.expm1(m.predict(test[feats[k]])), 0)
    prev["persistencia"] = test["notificacoes"].to_numpy(dtype=float)
    return test, prev


def metricas(y, p):
    return {
        "R2": round(float(r2_score(y, p)), 4),
        "R2_log": round(float(r2_score(np.log1p(y), np.log1p(p))), 4),
        "MAE": round(float(mean_absolute_error(y, p)), 2),
        "soma_real": int(round(y.sum())),
        "soma_prevista": int(round(p.sum())),
    }


def por_ano(test, prev):
    y = test["notificacoes_t4"].to_numpy(dtype=float)
    out = {}
    for ano in ANOS_TESTE:
        s = (test["ano"] == ano).to_numpy()
        out[str(ano)] = {k: metricas(y[s], p[s]) for k, p in prev.items()}
        topo = s & (y > np.quantile(y[s], 0.95))
        out[str(ano)]["razao_prevista_real_top5pct"] = {
            k: round(float(p[topo].sum() / y[topo].sum()), 3) for k, p in prev.items()}
    return out


def recorte_df(test, prev):
    s = (test["cod_mesorregiao"] == COD_MESO_DF).to_numpy()
    y = test["notificacoes_t4"].to_numpy(dtype=float)
    return {"n_semanas": int(s.sum()), **{k: metricas(y[s], p[s]) for k, p in prev.items()}}


def clima_por_mesorregiao(test, prev):
    y = np.log1p(test["notificacoes_t4"].to_numpy(dtype=float))
    melhores = 0
    for cod, idx in test.groupby("cod_mesorregiao").indices.items():
        if r2_score(y[idx], np.log1p(prev["C"][idx])) > r2_score(y[idx], np.log1p(prev["A"][idx])):
            melhores += 1
    return {"mesorregioes_C_melhor_que_A_R2_log": melhores,
            "mesorregioes_total": int(test["cod_mesorregiao"].nunique())}


def fig_baselines(comparacao):
    rot = {"baseline: persistencia": "Persistência\n(semana t)",
           "baseline: media_movel_4": "Média móvel\n(4 semanas)",
           "baseline: sazonal": "Sazonal\n(ano anterior)",
           "XGBoost A: SINAN-only": "XGBoost A\n(SINAN)",
           "XGBoost B: INMET bruto": "XGBoost B\n(+ INMET bruto)",
           "XGBoost C: INMET enriquecido": "XGBoost C\n(+ INMET enriq.)"}
    df = comparacao.set_index("modelo").loc[list(rot)]
    x = np.arange(len(df))
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.bar(x - 0.2, df["R2_log"], 0.4, label="R² (escala log)", color="#6baed6")
    ax.bar(x + 0.2, df["R2"], 0.4, label="R² (escala original)", color="#d62728")
    for xi, (a, b) in enumerate(zip(df["R2_log"], df["R2"])):
        ax.text(xi - 0.2, max(a, 0) + 0.02, f"{a:.2f}".replace(".", ","), ha="center", fontsize=8)
        ax.text(xi + 0.2, max(b, 0) + 0.02, f"{b:.2f}".replace(".", ","), ha="center", fontsize=8)
    ax.axhline(0, color="black", lw=0.6)
    ax.set_xticks(x, [rot[m] for m in df.index], fontsize=9)
    ax.set_ylabel("R²")
    ax.yaxis.set_major_formatter(VIRGULA)
    ax.set_ylim(-0.8, 1.05)
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig_baselines_vs_xgboost.png", dpi=300)
    plt.close(fig)


def fig_serie_nacional(test, prev):
    t = test[["ano", "semana_epidemiologica"]].copy()
    t["real"] = test["notificacoes_t4"].to_numpy(dtype=float)
    t["C"] = prev["C"]
    t["persistencia"] = prev["persistencia"]
    serie = t.groupby(["ano", "semana_epidemiologica"])[["real", "C", "persistencia"]].sum().reset_index()
    x = np.arange(len(serie))
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(x, serie["real"] / 1e3, color=COR["real"], lw=2, label="Notificações observadas (t+4)")
    ax.plot(x, serie["C"] / 1e3, color=COR["C"], lw=1.6, label="XGBoost C (SINAN + INMET enriquecido)")
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


def fig_cobertura(mp):
    rel = json.loads((mp / "data" / "model_ready_v3" / "23_integration_report.json").read_text(encoding="utf-8"))
    cob = rel["cobertura_por_ano"]
    anos = list(cob)
    fig, ax = plt.subplots(figsize=(8, 3.6))
    barras = ax.bar(anos, [cob[a] for a in anos], color="#6baed6")
    for b, a in zip(barras, anos):
        ax.text(b.get_x() + b.get_width() / 2, cob[a] + 0.8, f"{cob[a]:.1f}".replace(".", ","),
                ha="center", fontsize=8)
    ax.set_ylim(0, 105)
    ax.set_ylabel("Mesorregião-semanas com clima (%)")
    ax.set_xlabel("Ano epidemiológico")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig_cobertura_inmet_ano.png", dpi=300)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo-previsao", default=str(MONO.parent.parent / "MODELO-PREVISAO"))
    mp = Path(ap.parse_args().modelo_previsao).resolve()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    DADOS_DIR.mkdir(parents=True, exist_ok=True)

    test, prev = carregar(mp)
    comparacao = pd.read_csv(mp / "models" / "baselines_v3" / "comparison.csv")
    fatos = {
        "modelo_previsao_commit": commit_de(mp),
        "n_teste": int(len(test)),
        "por_ano": por_ano(test, prev),
        "distrito_federal": recorte_df(test, prev),
        **clima_por_mesorregiao(test, prev),
    }
    uf = pd.read_csv(mp / "models" / "regression_v3" / "metrics_por_uf_v3.csv")
    piv = uf.pivot(index="uf", columns="modelo", values="R2_log")
    fatos["ufs_C_melhor_que_A_R2_log"] = int((piv["C: INMET enriquecido"] > piv["A: SINAN-only"]).sum())
    fatos["ufs_total"] = int(len(piv))

    fig_baselines(comparacao)
    fig_serie_nacional(test, prev)
    fig_cobertura(mp)
    (DADOS_DIR / "fatos_derivados.json").write_text(
        json.dumps(fatos, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(fatos, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
