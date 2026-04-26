#!/usr/bin/env python3
"""Clusteriza atributos meteorológicos do INMET e seleciona representantes.

O pipeline parte de uma série climática semanal derivada da base consolidada,
expande atributos com lags e janelas móveis e, em seguida, aplica
clusterização hierárquica para reduzir redundância.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform
from sklearn.preprocessing import StandardScaler


def _first_existing_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for name in candidates:
        if name in df.columns:
            return name
    return None


def _derive_dew_point(temp_c: pd.Series, rel_humidity: pd.Series) -> pd.Series:
    # Aproximação de Magnus-Tetens para ponto de orvalho em graus Celsius.
    rh = rel_humidity.clip(lower=1.0, upper=100.0)
    a = 17.27
    b = 237.7
    gamma = np.log(rh / 100.0) + (a * temp_c) / (b + temp_c)
    return (b * gamma) / (a - gamma)


def _max_consecutive_true(values: pd.Series) -> int:
    longest = 0
    current = 0
    for flag in values.fillna(False).astype(bool):
        if flag:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return int(longest)


def load_inputs(input_path: Path) -> pd.DataFrame:
    df = pd.read_csv(input_path, parse_dates=["date"])
    required = {
        "temp_mean",
        "temp_min",
        "temp_max",
        "rain",
        "pressure",
        "wind_speed",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Colunas ausentes na base de entrada: {sorted(missing)}")

    humidity_col = _first_existing_column(df, ["umidity_mean", "humidity_mean", "umid_mean", "ur"])
    if humidity_col is None:
        raise ValueError("A base precisa conter uma coluna de umidade média (umidity_mean/humidity_mean/umid_mean/ur).")
    if humidity_col != "humidity_mean":
        df = df.rename(columns={humidity_col: "humidity_mean"})

    humidity_min_col = _first_existing_column(df, ["humidity_min", "umidity_min", "umid_min", "ur_min"])
    if humidity_min_col and humidity_min_col != "humidity_min":
        df = df.rename(columns={humidity_min_col: "humidity_min"})

    humidity_max_col = _first_existing_column(df, ["humidity_max", "umidity_max", "umid_max", "ur_max"])
    if humidity_max_col and humidity_max_col != "humidity_max":
        df = df.rename(columns={humidity_max_col: "humidity_max"})

    dew_col = _first_existing_column(df, ["dew_point", "ponto_orvalho", "dew_temp"])
    if dew_col and dew_col != "dew_point":
        df = df.rename(columns={dew_col: "dew_point"})

    radiation_col = _first_existing_column(df, ["radiation", "solar_radiation", "radiacao_global"])
    if radiation_col and radiation_col != "radiation":
        df = df.rename(columns={radiation_col: "radiation"})

    sunshine_col = _first_existing_column(df, ["insolation", "sunshine", "insolacao"])
    if sunshine_col and sunshine_col != "insolation":
        df = df.rename(columns={sunshine_col: "insolation"})

    wind_gust_col = _first_existing_column(df, ["wind_gust", "rajada_vento", "wind_gust_speed"])
    if wind_gust_col and wind_gust_col != "wind_gust":
        df = df.rename(columns={wind_gust_col: "wind_gust"})

    return df.sort_values("date").reset_index(drop=True)


def aggregate_weekly(df: pd.DataFrame) -> pd.DataFrame:
    weekly_start = df["date"] - pd.to_timedelta((df["date"].dt.dayofweek + 1) % 7, unit="D")
    df = df.copy()
    df["week_start"] = weekly_start
    df["rain_heavy_day"] = df["rain"].ge(10.0)
    df["dry_day"] = df["rain"].le(1.0)

    if "dew_point" not in df.columns:
        df["dew_point"] = _derive_dew_point(df["temp_mean"], df["humidity_mean"])

    agg_map: dict[str, tuple[str, str]] = {
        "rain": ("rain", "sum"),
        "temp_mean": ("temp_mean", "mean"),
        "temp_min": ("temp_min", "min"),
        "temp_max": ("temp_max", "max"),
        "humidity_mean": ("humidity_mean", "mean"),
        "pressure": ("pressure", "mean"),
        "wind_speed": ("wind_speed", "mean"),
        "dew_point_mean": ("dew_point", "mean"),
        "rain_heavy_days": ("rain_heavy_day", "sum"),
    }

    if "humidity_min" in df.columns:
        agg_map["humidity_min"] = ("humidity_min", "min")
    if "humidity_max" in df.columns:
        agg_map["humidity_max"] = ("humidity_max", "max")
    if "radiation" in df.columns:
        agg_map["radiation_mean"] = ("radiation", "mean")
    if "insolation" in df.columns:
        agg_map["insolation_sum"] = ("insolation", "sum")
    if "wind_gust" in df.columns:
        agg_map["wind_gust_max"] = ("wind_gust", "max")

    weekly = (
        df.groupby("week_start", as_index=False)
        .agg(**agg_map)
        .sort_values("week_start")
        .reset_index(drop=True)
    )
    dry_spell = (
        df.groupby("week_start")["dry_day"]
        .apply(_max_consecutive_true)
        .rename("dry_spell_max_days")
        .reset_index()
    )
    weekly = weekly.merge(dry_spell, on="week_start", how="left")

    return weekly


def expand_features(df: pd.DataFrame) -> pd.DataFrame:
    expanded = df.copy()

    expanded["temp_range"] = expanded["temp_max"] - expanded["temp_min"]
    expanded["rain_ma4"] = expanded["rain"].rolling(4, min_periods=1).mean()
    expanded["rain_ma8"] = expanded["rain"].rolling(8, min_periods=1).mean()
    expanded["rain_cum4"] = expanded["rain"].rolling(4, min_periods=1).sum()
    expanded["rain_cum8"] = expanded["rain"].rolling(8, min_periods=1).sum()
    expanded["temp_ma4"] = expanded["temp_mean"].rolling(4, min_periods=1).mean()
    expanded["temp_ma8"] = expanded["temp_mean"].rolling(8, min_periods=1).mean()
    expanded["humidity_ma4"] = expanded["humidity_mean"].rolling(4, min_periods=1).mean()
    expanded["pressure_ma4"] = expanded["pressure"].rolling(4, min_periods=1).mean()
    expanded["wind_ma4"] = expanded["wind_speed"].rolling(4, min_periods=1).mean()

    if "dew_point_mean" in expanded.columns:
        expanded["dew_point_ma4"] = expanded["dew_point_mean"].rolling(4, min_periods=1).mean()
    if "radiation_mean" in expanded.columns:
        expanded["radiation_ma4"] = expanded["radiation_mean"].rolling(4, min_periods=1).mean()
    if "insolation_sum" in expanded.columns:
        expanded["insolation_ma4"] = expanded["insolation_sum"].rolling(4, min_periods=1).mean()
    if "rain_heavy_days" in expanded.columns:
        expanded["rain_heavy_days_ma4"] = expanded["rain_heavy_days"].rolling(4, min_periods=1).mean()
    if "dry_spell_max_days" in expanded.columns:
        expanded["dry_spell_max_days_ma4"] = expanded["dry_spell_max_days"].rolling(4, min_periods=1).mean()

    if {"humidity_max", "humidity_min"}.issubset(expanded.columns):
        expanded["humidity_range"] = expanded["humidity_max"] - expanded["humidity_min"]

    if "temp_mean" in expanded.columns and "humidity_mean" in expanded.columns:
        expanded["temp_humidity_interaction"] = expanded["temp_mean"] * expanded["humidity_mean"]
    if "rain" in expanded.columns and "temp_mean" in expanded.columns:
        expanded["rain_temp_interaction"] = expanded["rain"] * expanded["temp_mean"]

    lag_cols = [
        col
        for col in [
            "rain",
            "temp_mean",
            "temp_min",
            "temp_max",
            "humidity_mean",
            "humidity_min",
            "humidity_max",
            "dew_point_mean",
            "radiation_mean",
            "insolation_sum",
            "pressure",
            "wind_speed",
            "wind_gust_max",
            "rain_heavy_days",
            "dry_spell_max_days",
        ]
        if col in expanded.columns
    ]
    for col in lag_cols:
        for lag in [1, 2, 4, 8, 12]:
            expanded[f"{col}_lag{lag}"] = expanded[col].shift(lag)

    return expanded


def classify_family(feature_name: str) -> str:
    name = feature_name.lower()
    if "rain" in name or "precip" in name:
        return "precipitacao"
    if "humidity" in name or "umid" in name or "dew" in name or "orvalho" in name:
        return "umidade"
    if "temp" in name or "range" in name:
        return "temperatura"
    if "radiation" in name or "radiacao" in name or "insolation" in name or "insolacao" in name:
        return "radiacao"
    if "pressure" in name:
        return "pressao"
    if "wind" in name:
        return "vento"
    return "outros"


def feature_priority(feature_name: str) -> float:
    name = feature_name.lower()
    score = 0.0

    if "rain" in name or "precip" in name:
        score += 5.0
    elif "humidity" in name or "umid" in name or "dew" in name or "orvalho" in name:
        score += 4.8
    elif "temp" in name or "range" in name:
        score += 4.5
    elif "radiation" in name or "radiacao" in name or "insolation" in name or "insolacao" in name:
        score += 3.6
    elif "pressure" in name:
        score += 2.2
    elif "wind" in name:
        score += 1.8

    if "range" in name:
        score += 0.4
    if any(token in name for token in ["ma4", "cum4"]):
        score += 0.7
    if any(token in name for token in ["ma8", "cum8"]):
        score += 0.5
    if any(token in name for token in ["lag2", "lag4", "lag8"]):
        score += 0.8
    if any(token in name for token in ["lag1", "lag12"]):
        score += 0.3
    if any(token in name for token in ["heavy", "dry_spell", "extreme"]):
        score += 0.5

    return score


def cluster_and_select(df: pd.DataFrame, distance_threshold: float = 0.55) -> tuple[pd.DataFrame, dict[str, int]]:
    features = df.select_dtypes(include=[np.number]).copy()
    features = features.fillna(features.mean(numeric_only=True))

    scaler = StandardScaler()
    scaled = pd.DataFrame(
        scaler.fit_transform(features),
        columns=features.columns,
        index=features.index,
    )

    corr = scaled.corr().abs().fillna(0)
    np.fill_diagonal(corr.values, 0)
    dist = 1 - corr
    linkage_matrix = linkage(squareform(dist.values, checks=False), method="average")
    cluster_ids = fcluster(linkage_matrix, t=distance_threshold, criterion="distance")

    rows = []
    feature_cluster_map: dict[str, int] = {}
    for cluster_id in np.unique(cluster_ids):
        members = [name for name, cid in zip(features.columns, cluster_ids) if cid == cluster_id]
        if not members:
            continue

        for member in members:
            feature_cluster_map[member] = int(cluster_id)

        rep = max(
            members,
            key=lambda name: (
                feature_priority(name),
                -features[name].isna().sum(),
            ),
        )

        rows.append(
            {
                "cluster_id": int(cluster_id),
                "representative": rep,
                "family": classify_family(rep),
                "priority_score": feature_priority(rep),
                "cluster_size": len(members),
                "members": ", ".join(members),
            }
        )

    clusters = pd.DataFrame(rows).sort_values(["priority_score", "cluster_size"], ascending=[False, False])

    return clusters.reset_index(drop=True), feature_cluster_map


def select_family_features(df: pd.DataFrame, feature_cluster_map: dict[str, int]) -> pd.DataFrame:
    quotas = {
        "precipitacao": 2,
        "temperatura": 2,
        "umidade": 1,
        "radiacao": 1,
        "pressao": 1,
        "vento": 1,
    }

    rows = []
    numeric_features = list(df.select_dtypes(include=[np.number]).columns)

    for family, quota in quotas.items():
        candidates = [name for name in numeric_features if classify_family(name) == family]
        candidates = sorted(
            candidates,
            key=lambda name: (
                feature_priority(name),
                -feature_cluster_map.get(name, 0),
            ),
            reverse=True,
        )

        chosen: list[str] = []
        used_clusters: set[int] = set()

        for candidate in candidates:
            cluster_id = feature_cluster_map.get(candidate, -1)
            if cluster_id not in used_clusters or len(chosen) < quota:
                chosen.append(candidate)
                used_clusters.add(cluster_id)
            if len(chosen) >= quota:
                break

        if not chosen and candidates:
            chosen.append(candidates[0])

        for feature in chosen:
            rows.append(
                {
                    "representative": feature,
                    "family": family,
                    "priority_score": feature_priority(feature),
                    "cluster_id": feature_cluster_map.get(feature, -1),
                }
            )

    recommended = pd.DataFrame(rows)
    recommended = recommended.sort_values(["priority_score", "family"], ascending=[False, True])
    recommended = recommended.drop_duplicates(subset=["representative"]).reset_index(drop=True)
    return recommended


def build_report(clusters: pd.DataFrame, recommended: pd.DataFrame, weekly: pd.DataFrame) -> str:
    lines = []
    lines.append("# Seleção de atributos meteorológicos do INMET")
    lines.append("")
    lines.append("## Resumo")
    lines.append(f"- Observações semanais: {len(weekly)}")
    lines.append(f"- Clusters encontrados: {len(clusters)}")
    lines.append(f"- Atributos recomendados: {len(recommended)}")
    lines.append("")
    lines.append("## Atributos recomendados")
    for _, row in recommended.iterrows():
        lines.append(
            f"- {row['representative']} | família: {row['family']} | score: {row['priority_score']:.1f} | cluster {row['cluster_id']}"
        )
    lines.append("")
    lines.append("## Critério metodológico")
    lines.append(
        "A clusterização reduz redundância entre variáveis correlacionadas e a seleção final prioriza precipitação, temperatura e umidade, pois são os fatores mais coerentes com a literatura sobre reprodução do Aedes aegypti e dinâmica da dengue."
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Clusterização e seleção de atributos do INMET")
    parser.add_argument(
        "--input",
        default="data_processed/inmet_2022_2024.csv",
        help="Arquivo CSV consolidado do INMET em base diária",
    )
    parser.add_argument(
        "--output-dir",
        default="data_processed/inmet_feature_selection",
        help="Diretório de saída para os resultados",
    )
    parser.add_argument(
        "--distance-threshold",
        type=float,
        default=0.55,
        help="Limiar da clusterização hierárquica",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    input_path = root / args.input
    output_dir = root / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    daily = load_inputs(input_path)
    weekly = aggregate_weekly(daily)
    expanded = expand_features(weekly)

    clusters, feature_cluster_map = cluster_and_select(expanded, distance_threshold=args.distance_threshold)
    recommended = select_family_features(expanded, feature_cluster_map)

    clusters_path = output_dir / "clusters_inmet.csv"
    recommended_path = output_dir / "selected_features_inmet.csv"
    report_path = output_dir / "report.md"

    clusters.to_csv(clusters_path, index=False)
    recommended.to_csv(recommended_path, index=False)
    report_path.write_text(build_report(clusters, recommended, weekly), encoding="utf-8")

    print(f"Base semanal: {len(weekly)} observações")
    print(f"Clusters: {len(clusters)}")
    print(f"Atributos recomendados: {len(recommended)}")
    print("\nSelecionados:")
    for _, row in recommended.iterrows():
        print(f"- {row['representative']} ({row['family']}, score={row['priority_score']:.1f})")
    print(f"\nArquivos gerados em: {output_dir}")


if __name__ == "__main__":
    main()