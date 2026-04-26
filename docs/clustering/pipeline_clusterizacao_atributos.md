# Pipeline prático em Python para clusterização de atributos meteorológicos

Este documento descreve uma estrategia simples e defensavel para reduzir redundancia entre atributos climaticos antes da modelagem preditiva. A ideia nao e substituir a selecao supervisionada, mas diminuir colinearidade e manter variaveis representativas.

## Objetivo

Agrupar atributos meteorologicos muito semelhantes e escolher um representante por grupo, preservando interpretabilidade e reduzindo a dimensionalidade do conjunto final.

## Fluxo sugerido

1. Padronizar os atributos meteorologicos e criar lags, medias moveis e acumulados.
2. Calcular a matriz de correlacao absoluta entre os atributos.
3. Converter a correlacao em distancia com `distance = 1 - |corr|`.
4. Aplicar clusterizacao hierarquica sobre as colunas.
5. Em cada cluster, escolher um representante com maior associacao ao alvo ou menor redundancia interna.
6. Validar o subconjunto final com validacao temporal e o modelo preditivo escolhido.

## Implementacao em Python

```python
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform
from sklearn.preprocessing import StandardScaler


def selecionar_representantes(df, features, target, max_dist=0.35):
    X = df[features].copy()
    X = X.replace([np.inf, -np.inf], np.nan).dropna(axis=1, how='all')
    features_validas = X.columns.tolist()

    scaler = StandardScaler()
    X_scaled = pd.DataFrame(
        scaler.fit_transform(X.fillna(X.mean())),
        columns=features_validas,
        index=X.index,
    )

    corr = X_scaled.corr().abs()
    dist = 1 - corr
    np.fill_diagonal(dist.values, 0)

    linkage_matrix = linkage(squareform(dist.values, checks=False), method='average')
    cluster_ids = fcluster(linkage_matrix, t=max_dist, criterion='distance')

    representantes = []
    for cluster_id in np.unique(cluster_ids):
        cluster_features = [f for f, c in zip(features_validas, cluster_ids) if c == cluster_id]
        if len(cluster_features) == 1:
            representantes.append(cluster_features[0])
            continue

        cor_target = (
            df[cluster_features + [target]]
            .corr(numeric_only=True)[target]
            .drop(target)
            .abs()
        )
        representantes.append(cor_target.idxmax())

    return representantes
```

## Critério de escolha dos representantes

- Manter a variavel com maior correlacao com o alvo dentro de cada cluster.
- Quando houver empate, preferir a variavel mais estavel temporalmente ou mais interpretavel.
- Evitar manter duas variaveis que medem o mesmo fenomeno em janelas temporais muito proximas.

## Exemplo de uso

```python
features_meteorologicas = [
    'precipitacao', 'temperatura_media', 'temperatura_max', 'temperatura_min',
    'umidade_media', 'vento_media', 'precipitacao_lag1', 'precipitacao_lag2'
]

cols_selecionadas = selecionar_representantes(
    df=df,
    features=features_meteorologicas,
    target='casos_dengue',
    max_dist=0.35
)

df_modelo = df[cols_selecionadas + ['casos_dengue', 'ibge_municipio', 'data']].copy()
```

## Como interpretar o resultado

Esse pipeline e util porque combina interpretabilidade com controle de redundancia. Em dados meteorologicos, isso e especialmente importante quando ha muitas variaveis defasadas e atributos altamente correlacionados.

## Observacao metodologica

A clusterizacao de atributos deve ser vista como uma etapa de reducao de redundancia. A selecao final ainda deve ser validada com o modelo preditivo e com validacao temporal, para evitar perda de informacao relevante.
