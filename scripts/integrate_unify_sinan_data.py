#!/usr/bin/env python3
"""Integra e unifica o dataset semanal de SINAN com a base climática do INMET.

Entradas:
- MODELO-PREVISAO/data/processed/sinan/normalized_recorte_brasilia_2022_2024.parquet
- MODELO-PREVISAO/data/processed/sinan/weekly_features_brasilia_2022_2024.csv
- MODELO-PREVISAO/data/processed/sinan/cluster_assignments_brasilia_2022_2024.csv
- MODELO-PREVISAO/data/processed/sinan/cluster_assignments_profile_brasilia_2022_2024.csv
- TCC1-DOCS/data_processed/inmet_2022_2024.csv

Saídas:
- TCC2-DOCS/docs/IntegracaoUnificacaoDadosSINAN/evidencias/*.csv|json|md
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
SINAN_DIR = WORKSPACE / "MODELO-PREVISAO" / "data" / "processed" / "sinan"
INMET_PATH = WORKSPACE / "TCC1-DOCS" / "data_processed" / "inmet_2022_2024.csv"
TCC1_UNIFIED_PATH = WORKSPACE / "TCC1-DOCS" / "data_processed" / "dataset_unificado.csv"
OUTPUT_DIR = ROOT / "docs" / "IntegracaoUnificacaoDadosSINAN" / "evidencias"

SOURCE_LINEAGE = {
    "sinan_portal_home": {
        "url": "https://portalsinan.saude.gov.br/",
        "role": "portal institucional do SINAN",
        "notes": "Usado para validar a estrutura oficial do sistema e a existência da área de dados epidemiológicos.",
    },
    "sinan_epidemiological_data_portal": {
        "url": "https://portalsinan.saude.gov.br/dados-epidemiologicos-SINAN",
        "role": "página oficial de dados epidemiológicos do SINAN",
        "notes": "Aponta para tabulações DATASUS e organiza o acesso por grupos de doenças/agravos.",
    },
    "opendatasus_dengue_catalog": {
        "url": "https://opendatasus.saude.gov.br/dataset/arboviroses-dengue",
        "role": "catálogo oficial dos microdados de dengue",
        "notes": "Lista recursos anuais CSV/JSON/XML e dicionário de dados do agravo dengue.",
    },
    "sinan_dengue_dictionary": {
        "url": "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SINAN/Dengue/dic_dados_dengue.pdf",
        "role": "dicionário de dados oficial do dengue",
        "notes": "Base para interpretação dos campos clínicos, temporais e territoriais usados no processamento.",
    },
    "basedosdados_sinan": {
        "url": "https://basedosdados.org/dataset/f51134c2-5ab9-4bbc-882f-f1034603147a",
        "role": "catálogo alternativo e camada tratada do SINAN",
        "notes": "Confirma cobertura temporal ampla do SINAN e serve como referência de disponibilidade tratada, mas a integração desta task usa microdado oficial processado localmente.",
    },
    "tcc1_unified_dataset": {
        "path": str(TCC1_UNIFIED_PATH),
        "role": "base unificada entregue no TCC1",
        "notes": "Usada para validar alinhamento temporal e coerência do dataset integrado gerado nesta task.",
    },
    "tcc1_inmet_daily": {
        "path": str(INMET_PATH),
        "role": "base climática diária consolidada do TCC1",
        "notes": "Fonte climática real agregada para semana epidemiológica na integração.",
    },
    "sinan_processed_weekly": {
        "path": str(SINAN_DIR / "weekly_features_brasilia_2022_2024.csv"),
        "role": "agregação semanal do SINAN produzida na task anterior",
        "notes": "Contém notificações e atributos clínico-epidemiológicos agregados por semana.",
    },
}


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def week_start_sunday(series: pd.Series) -> pd.Series:
    return series - pd.to_timedelta((series.dt.dayofweek + 1) % 7, unit="D")


def ano_semana_to_week_start(ano_semana: str) -> pd.Timestamp:
    ano_semana = str(ano_semana)
    year = int(ano_semana[:4])
    week = int(ano_semana[4:])
    jan4 = pd.Timestamp(year=year, month=1, day=4)
    first_epi_week_start = jan4 - pd.to_timedelta((jan4.dayofweek + 1) % 7, unit="D")
    return first_epi_week_start + pd.to_timedelta((week - 1) * 7, unit="D")


def load_sinan_weekly() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    normalized = pd.read_parquet(SINAN_DIR / "normalized_recorte_brasilia_2022_2024.parquet")
    weekly = pd.read_csv(SINAN_DIR / "weekly_features_brasilia_2022_2024.csv")
    cluster_intensity = pd.read_csv(SINAN_DIR / "cluster_assignments_brasilia_2022_2024.csv")
    cluster_profile = pd.read_csv(SINAN_DIR / "cluster_assignments_profile_brasilia_2022_2024.csv")

    normalized["DT_SIN_PRI_PARSED"] = pd.to_datetime(normalized["DT_SIN_PRI_PARSED"], errors="coerce")
    sinan_calendar = (
        normalized.dropna(subset=["ANO_SEMANA", "DT_SIN_PRI_PARSED"])
        .groupby("ANO_SEMANA", as_index=False)
        .agg(
            dt_sin_pri_min=("DT_SIN_PRI_PARSED", "min"),
            dt_sin_pri_max=("DT_SIN_PRI_PARSED", "max"),
        )
    )
    sinan_calendar["week_start"] = sinan_calendar["ANO_SEMANA"].astype(str).map(ano_semana_to_week_start)

    weekly["ANO_SEMANA"] = weekly["ANO_SEMANA"].astype(str)
    cluster_intensity["ANO_SEMANA"] = cluster_intensity["ANO_SEMANA"].astype(str)
    cluster_profile["ANO_SEMANA"] = cluster_profile["ANO_SEMANA"].astype(str)
    sinan_calendar["ANO_SEMANA"] = sinan_calendar["ANO_SEMANA"].astype(str)

    weekly = weekly.merge(sinan_calendar, on="ANO_SEMANA", how="left")
    weekly = weekly.merge(
        cluster_intensity[["ANO_SEMANA", "CLUSTER", "CLUSTER_LABEL"]].rename(
            columns={"CLUSTER": "cluster_intensity_id", "CLUSTER_LABEL": "cluster_intensity_label"}
        ),
        on="ANO_SEMANA",
        how="left",
    )
    weekly = weekly.merge(
        cluster_profile[["ANO_SEMANA", "CLUSTER", "CLUSTER_LABEL"]].rename(
            columns={"CLUSTER": "cluster_profile_id", "CLUSTER_LABEL": "cluster_profile_label"}
        ),
        on="ANO_SEMANA",
        how="left",
    )

    return normalized, weekly, sinan_calendar


def load_inmet_weekly() -> pd.DataFrame:
    inmet = pd.read_csv(INMET_PATH)
    inmet["date"] = pd.to_datetime(inmet["date"], errors="coerce")
    inmet = inmet.rename(columns={"umidity_mean": "humidity_mean"})
    inmet["week_start"] = week_start_sunday(inmet["date"])

    weekly = (
        inmet.groupby("week_start", as_index=False)
        .agg(
            inmet_days=("date", "count"),
            rain_sum=("rain", "sum"),
            rain_mean=("rain", "mean"),
            temp_mean=("temp_mean", "mean"),
            temp_min=("temp_min", "min"),
            temp_max=("temp_max", "max"),
            humidity_mean=("humidity_mean", "mean"),
            pressure_mean=("pressure", "mean"),
            wind_speed_mean=("wind_speed", "mean"),
        )
        .sort_values("week_start")
        .reset_index(drop=True)
    )

    weekly["temp_range"] = weekly["temp_max"] - weekly["temp_min"]
    weekly["rain_nonzero_days"] = (
        inmet.assign(rain_flag=inmet["rain"].gt(0))
        .groupby("week_start")["rain_flag"]
        .sum()
        .reset_index(drop=True)
        .astype(int)
    )
    return weekly


def build_tcc1_comparison(unified: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, object]]:
    tcc1 = pd.read_csv(TCC1_UNIFIED_PATH)
    tcc1["data"] = pd.to_datetime(tcc1["data"], errors="coerce")

    comparison = tcc1.merge(
        unified[
            [
                "week_start",
                "ANO_SEMANA",
                "NOTIFICACOES",
                "rain_sum",
                "temp_mean",
                "humidity_mean",
                "pressure_mean",
            ]
        ],
        left_on="data",
        right_on="week_start",
        how="inner",
        validate="1:1",
    )
    comparison["casos_minus_notificacoes"] = comparison["casos_dengue"] - comparison["NOTIFICACOES"]
    comparison["casos_minus_notificacoes_abs"] = comparison["casos_minus_notificacoes"].abs()
    comparison["chuva_minus_rain_sum"] = comparison["chuva"] - comparison["rain_sum"]
    comparison["temperatura_minus_temp_mean"] = comparison["temperatura_media"] - comparison["temp_mean"]
    comparison["umidade_minus_humidity_mean"] = comparison["umidade"] - comparison["humidity_mean"]
    comparison["pressao_minus_pressure_mean"] = comparison["pressao"] - comparison["pressure_mean"]

    summary = {
        "overlap_weeks": int(len(comparison)),
        "tcc1_rows": int(len(tcc1)),
        "new_unified_rows": int(len(unified)),
        "date_min": str(comparison["data"].min().date()),
        "date_max": str(comparison["data"].max().date()),
        "totals": {
            "tcc1_cases_total": int(comparison["casos_dengue"].sum()),
            "new_notifications_total": int(comparison["NOTIFICACOES"].sum()),
            "total_difference": int(comparison["casos_dengue"].sum() - comparison["NOTIFICACOES"].sum()),
        },
        "correlations": {
            "casos_dengue_vs_notificacoes": round(float(comparison["casos_dengue"].corr(comparison["NOTIFICACOES"])), 6),
            "chuva_vs_rain_sum": round(float(comparison["chuva"].corr(comparison["rain_sum"])), 6),
            "temperatura_media_vs_temp_mean": round(float(comparison["temperatura_media"].corr(comparison["temp_mean"])), 6),
            "umidade_vs_humidity_mean": round(float(comparison["umidade"].corr(comparison["humidity_mean"])), 6),
            "pressao_vs_pressure_mean": round(float(comparison["pressao"].corr(comparison["pressure_mean"])), 6),
        },
        "absolute_differences": {
            "equal_case_weeks": int(comparison["casos_minus_notificacoes_abs"].eq(0).sum()),
            "max_case_difference": int(comparison["casos_minus_notificacoes_abs"].max()),
            "mean_case_difference": round(float(comparison["casos_minus_notificacoes_abs"].mean()), 4),
        },
    }
    return comparison, summary


def build_unified_dataset() -> tuple[pd.DataFrame, Dict[str, object], pd.DataFrame, pd.DataFrame]:
    normalized, sinan_weekly, sinan_calendar = load_sinan_weekly()
    inmet_weekly = load_inmet_weekly()

    unified = sinan_weekly.merge(inmet_weekly, on="week_start", how="left", validate="1:1")
    unified = unified.sort_values(["ANO_EPI", "SEMANA_EPI"]).reset_index(drop=True)
    tcc1_comparison, tcc1_summary = build_tcc1_comparison(unified)

    key_columns = [
        "ANO_SEMANA",
        "week_start",
        "NOTIFICACOES",
        "rain_sum",
        "temp_mean",
        "humidity_mean",
        "pressure_mean",
        "wind_speed_mean",
        "cluster_intensity_label",
        "cluster_profile_label",
    ]
    missingness_rows: List[Dict[str, object]] = []
    total = len(unified)
    for column in unified.columns:
        missing = int(unified[column].isna().sum())
        missingness_rows.append(
            {
                "column": column,
                "dtype": str(unified[column].dtype),
                "missing_count": missing,
                "missing_pct": round((missing / total) * 100, 4) if total else 0.0,
                "unique_values": int(unified[column].nunique(dropna=True)),
                "is_key_column": column in key_columns,
            }
        )
    missingness = pd.DataFrame(missingness_rows).sort_values(["missing_pct", "column"], ascending=[False, True]).reset_index(drop=True)

    summary = {
        "scope": {
            "municipality_name": "Brasilia",
            "municipality_code": "5300108",
            "uf": "DF",
            "years": [2022, 2023, 2024],
        },
        "record_counts": {
            "sinan_normalized_rows": int(len(normalized)),
            "sinan_weekly_rows": int(len(sinan_weekly)),
            "inmet_weekly_rows": int(len(inmet_weekly)),
            "unified_rows": int(len(unified)),
            "unified_columns": int(len(unified.columns)),
        },
        "join_quality": {
            "sinan_weeks_without_inmet": int(unified["rain_sum"].isna().sum()),
            "full_match_pct": round(float((1 - unified["rain_sum"].isna().mean()) * 100), 4),
            "duplicated_ano_semana": int(unified["ANO_SEMANA"].duplicated().sum()),
            "duplicated_week_start": int(unified["week_start"].duplicated().sum()),
        },
        "temporal_coverage": {
            "min_week_start": str(unified["week_start"].min().date()),
            "max_week_start": str(unified["week_start"].max().date()),
            "min_ano_semana": str(unified["ANO_SEMANA"].min()),
            "max_ano_semana": str(unified["ANO_SEMANA"].max()),
        },
        "key_missingness_pct": {
            column: round(float(unified[column].isna().mean() * 100), 4)
            for column in key_columns
            if column in unified.columns
        },
        "tcc1_alignment": tcc1_summary,
    }

    return unified, summary, missingness, tcc1_comparison


def write_markdown_summary(unified: pd.DataFrame, summary: Dict[str, object]) -> Path:
    output_path = OUTPUT_DIR / "relatorio_integracao_unificacao_sinan.md"
    lines = [
        "# Relatório de Integração e Unificação de Dados - SINAN",
        "",
        "## Escopo",
        "",
        "- Recorte: Brasília/DF",
        "- Código de referência: 5300108",
        "- Período: 2022-2024",
        "",
        "## Fontes integradas",
        "",
        "- SINAN processado semanalmente a partir do microdado oficial",
        "- INMET diário agregado para semana epidemiológica compatível",
        "- Base unificada do TCC1 usada como referência de alinhamento",
        "",
        "## Volumetria",
        "",
        f"- Linhas semanais do dataset final: {summary['record_counts']['unified_rows']}",
        f"- Colunas do dataset final: {summary['record_counts']['unified_columns']}",
        f"- Cobertura temporal: {summary['temporal_coverage']['min_week_start']} até {summary['temporal_coverage']['max_week_start']}",
        "",
        "## Qualidade da junção",
        "",
        f"- Semanas do SINAN sem correspondência climática: {summary['join_quality']['sinan_weeks_without_inmet']}",
        f"- Percentual de match completo: {summary['join_quality']['full_match_pct']}%",
        f"- `ANO_SEMANA` duplicado no dataset final: {summary['join_quality']['duplicated_ano_semana']}",
        f"- `week_start` duplicado no dataset final: {summary['join_quality']['duplicated_week_start']}",
        "",
        "## Estrutura final",
        "",
        "O dataset unificado final contém:",
        "",
        "- atributos semanais do SINAN",
        "- calendário epidemiológico",
        "- clusters de intensidade e perfil clínico",
        "- variáveis climáticas semanais do INMET",
        "",
        "## Principais colunas climáticas integradas",
        "",
        "- `rain_sum`",
        "- `rain_mean`",
        "- `temp_mean`",
        "- `temp_min`",
        "- `temp_max`",
        "- `temp_range`",
        "- `humidity_mean`",
        "- `pressure_mean`",
        "- `wind_speed_mean`",
        "- `rain_nonzero_days`",
        "",
        "## Alinhamento com o TCC1",
        "",
        f"- Semanas sobrepostas com `dataset_unificado.csv`: {summary['tcc1_alignment']['overlap_weeks']}",
        f"- Correlação entre `casos_dengue` do TCC1 e `NOTIFICACOES` do novo dataset: {summary['tcc1_alignment']['correlations']['casos_dengue_vs_notificacoes']}",
        f"- Total do TCC1: {summary['tcc1_alignment']['totals']['tcc1_cases_total']}",
        f"- Total do novo dataset: {summary['tcc1_alignment']['totals']['new_notifications_total']}",
        f"- Diferença total: {summary['tcc1_alignment']['totals']['total_difference']}",
        "",
        "A diferença de total não invalida a integração: ela reflete que o TCC1 usou uma base agregada anterior, enquanto esta task integra o recorte semanal reconstruído a partir do microdado bruto processado do SINAN.",
    ]
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def main() -> None:
    ensure_output_dir()
    unified, summary, missingness, tcc1_comparison = build_unified_dataset()

    unified_csv = OUTPUT_DIR / "dataset_unificado_sinan_inmet_brasilia_2022_2024.csv"
    unified.to_csv(unified_csv, index=False)

    quality_json = OUTPUT_DIR / "quality_summary_integracao_unificacao_sinan.json"
    quality_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    missingness_csv = OUTPUT_DIR / "quality_missingness_integracao_unificacao_sinan.csv"
    missingness.to_csv(missingness_csv, index=False)

    tcc1_comparison_csv = OUTPUT_DIR / "comparacao_com_tcc1_dataset_unificado.csv"
    tcc1_comparison.to_csv(tcc1_comparison_csv, index=False)

    source_lineage_json = OUTPUT_DIR / "source_lineage_integracao_unificacao_sinan.json"
    source_lineage_json.write_text(json.dumps(SOURCE_LINEAGE, indent=2, ensure_ascii=False), encoding="utf-8")

    schema_json = OUTPUT_DIR / "schema_dataset_unificado_sinan_inmet.json"
    schema_payload = {
        "columns": [
            {
                "name": column,
                "dtype": str(unified[column].dtype),
            }
            for column in unified.columns
        ]
    }
    schema_json.write_text(json.dumps(schema_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    report_path = write_markdown_summary(unified, summary)

    manifest = {
        "generated_files": {
            "dataset_unificado_csv": str(unified_csv),
            "quality_summary_json": str(quality_json),
            "quality_missingness_csv": str(missingness_csv),
            "tcc1_comparison_csv": str(tcc1_comparison_csv),
            "source_lineage_json": str(source_lineage_json),
            "schema_json": str(schema_json),
            "report_md": str(report_path),
        }
    }
    manifest_path = OUTPUT_DIR / "artifact_manifest_integracao_unificacao_sinan.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    print("[done] integração/unificação concluída")
    for key, value in manifest["generated_files"].items():
        print(f"  - {key}: {value}")


if __name__ == "__main__":
    main()
