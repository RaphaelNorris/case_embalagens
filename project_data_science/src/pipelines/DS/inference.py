"""
Inference module for production productivity prediction.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import pickle
from pathlib import Path
import warnings

# Suppress sklearn warnings about feature names
warnings.filterwarnings(
    "ignore", message="X has feature names, but.*was fitted without feature names"
)

from . import data_processing
from src.logger import get_logger

logger = get_logger(__name__)


def process_pedidos_for_inference(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process pedidos data specifically for inference (less restrictive than training).

    Args:
        df: DataFrame with order data from Streamlit

    Returns:
        Processed DataFrame
    """
    df_proc = df.copy()

    # Create CD_OP if it doesn't exist
    if "CD_OP" not in df_proc.columns:
        df_proc["CD_OP"] = (
            df_proc["CD_PEDIDO"].astype(str) + "/" + df_proc["CD_ITEM"].astype(str)
        )

    # Basic column renaming (only if columns exist)
    rename_map = {
        "FL_EXIGELAUDO": "FL_TESTE_EXIGELAUDO",
        "VL_COLUNAMINIMO": "VL_COLUNAMINIMO",
        "QT_COBBINTMAXIMO": "VL_COBBINTMAXIMO",
        "VL_COMPRESSAO": "VL_COMPRESSAO",
        "VL_GRAMATURA": "VL_GRAMATURA",
        "CD_ESPELHO": "CAT_ESPELHO",
        "CD_FILME": "CAT_FILME",
        "CD_TIPOFT2": "FL_CONTROLE_ESPECIAL_IMPRESSAO",
        "VL_LAPINTERNO": "FL_LAP_INTERNO",
        "VL_LAPNOCOMP": "FL_LAP_NO_COMPR",
        "TX_COMPOSICAO": "CAT_COMPOSICAO",
    }

    for old_col, new_col in rename_map.items():
        if old_col in df_proc.columns:
            df_proc = df_proc.rename(columns={old_col: new_col})

    # Convert LAP flags to binary if they exist (SKIP if conversion fails)
    for col in ["FL_LAP_INTERNO", "FL_LAP_NO_COMPR"]:
        if col in df_proc.columns:
            try:
                df_proc[col] = (
                    pd.to_numeric(df_proc[col], errors="coerce")
                    .fillna(0)
                    .replace(-1, 0)
                    .astype(int)
                )
            except:
                df_proc[col] = 0  # Default value if conversion fails

    # Binary flag for FL_PROLONG_LAP if exists
    if "FL_PROLONG_LAP" in df_proc.columns:
        try:
            df_proc["FL_PROLONG_LAP"] = (
                pd.to_numeric(df_proc["FL_PROLONG_LAP"], errors="coerce").fillna(0) > 0
            ).astype(int)
        except:
            df_proc["FL_PROLONG_LAP"] = 0

    # Handle FL_CONTROLE_ESPECIAL_IMPRESSAO if exists (SKIP if conversion fails)
    if "FL_CONTROLE_ESPECIAL_IMPRESSAO" in df_proc.columns:
        try:
            df_proc["FL_CONTROLE_ESPECIAL_IMPRESSAO"] = (
                pd.to_numeric(
                    df_proc["FL_CONTROLE_ESPECIAL_IMPRESSAO"], errors="coerce"
                )
                .fillna(0)
                .astype(int)
            )
        except:
            df_proc["FL_CONTROLE_ESPECIAL_IMPRESSAO"] = 0

    # Convert numeric columns (SKIP if conversion fails)
    numeric_cols = [
        "FL_LAP_INTERNO",
        "FL_LAP_NO_COMPR",
        "FL_PROLONG_LAP",
        "QT_ARRANJO",
        "QT_NRCORES",
    ]
    for col in numeric_cols:
        if col in df_proc.columns:
            try:
                df_proc[col] = (
                    pd.to_numeric(df_proc[col], errors="coerce").fillna(0).astype(int)
                )
            except:
                df_proc[col] = 0  # Default value

    # Convert binary flag columns (S/N, Sim/Não) to 0/1
    binary_flag_cols = [
        "FL_AMARRADO",
        "FL_CHAPA",
        "FL_EXIGELAUDO",
        "FL_PALETIZADO",
        "FL_REFILADO",
        "FL_RESINAINTERNA",
        "FL_SUSPENSO",
        "FL_TESTE_EXIGELAUDO",
        "FL_SUSPOUCANCEL",
    ]
    true_values = {"1", "s", "sim", "y", "yes", "true"}
    for col in binary_flag_cols:
        if col in df_proc.columns:
            try:
                df_proc[col] = (
                    df_proc[col]
                    .apply(
                        lambda v: 1
                        if str(v).strip().lower() in true_values
                        else 0
                    )
                    .astype(int)
                )
            except Exception:
                df_proc[col] = 0

    # Aggregate color consumption if columns exist
    col_corr = ["QT_CONSUMOCOR1", "QT_CONSUMOCOR2", "QT_CONSUMOCOR3", "QT_CONSUMOCOR4"]
    existing_cor_cols = [c for c in col_corr if c in df_proc.columns]
    if existing_cor_cols:
        df_proc["VL_CONSUMO_COR_TOTAL"] = df_proc[existing_cor_cols].sum(axis=1)
        df_proc.drop(columns=existing_cor_cols, inplace=True)

    # Handle QT_PROLONGLAP if exists
    if "QT_PROLONGLAP" in df_proc.columns:
        try:
            df_proc["FL_PROLONGLAP"] = (
                pd.to_numeric(df_proc["QT_PROLONGLAP"], errors="coerce")
                .replace({50: 1, 30: 1})
                .fillna(0)
                .astype(int)
            )
            df_proc.drop(columns=["QT_PROLONGLAP"], inplace=True)
        except:
            pass  # Skip if fails

    # Create aggregated vinyl feature if vinco columns exist
    vinco_comp_cols = [c for c in df_proc.columns if c.startswith("VL_VINCOCOMP")]
    vinco_larg_cols = [c for c in df_proc.columns if c.startswith("VL_VINCOLARG")]
    if vinco_comp_cols or vinco_larg_cols:
        df_proc["VL_VINCOS_TOTAL_MM"] = df_proc[vinco_comp_cols].sum(axis=1) + df_proc[
            vinco_larg_cols
        ].sum(axis=1)

    # Dimension ratios if columns exist
    if {"VL_COMPRIMENTO", "VL_LARGURA"}.issubset(df_proc.columns):
        df_proc["RAZAO_CHAPA_COMP_LARG"] = df_proc["VL_COMPRIMENTO"] / df_proc[
            "VL_LARGURA"
        ].replace(0, np.nan)
        df_proc["RAZAO_CHAPA_COMP_LARG"] = df_proc["RAZAO_CHAPA_COMP_LARG"].replace(
            [np.inf, -np.inf], np.nan
        )

    if {"VL_COMPPECA", "VL_LARGPECA"}.issubset(df_proc.columns):
        df_proc["RAZAO_PECA_COMP_LARG"] = df_proc["VL_COMPPECA"] / df_proc[
            "VL_LARGPECA"
        ].replace(0, np.nan)
        df_proc["RAZAO_PECA_COMP_LARG"] = df_proc["RAZAO_PECA_COMP_LARG"].replace(
            [np.inf, -np.inf], np.nan
        )

    # Internal volume if columns exist
    vol_cols = {"VL_COMPRIMENTOINTERNO", "VL_LARGURAINTERNA", "VL_ALTURAINTERNA"}
    if vol_cols.issubset(df_proc.columns):
        df_proc["VOLUME_INTERNO"] = (
            df_proc["VL_COMPRIMENTOINTERNO"]
            * df_proc["VL_LARGURAINTERNA"]
            * df_proc["VL_ALTURAINTERNA"]
        ) / 1_000_000.0

    return df_proc


def predict_orders(
    orders_df: pd.DataFrame, model_artifacts: Dict[str, Any]
) -> pd.DataFrame:
    """
    Make predictions on new orders using trained model artifacts.

    Args:
        orders_df: DataFrame with order data
        model_artifacts: Dictionary containing all trained model components

    Returns:
        DataFrame with predictions and probabilities
    """

    logger.info("Input DataFrame shape: {orders_df.shape}")
    training_feature_order: list[str] = []
    task_type = str(model_artifacts.get("task_type", "classification")).lower()

    # 1. Process the orders data - USE INFERENCE-SPECIFIC PROCESSING
    try:
        # Try the inference-specific processing first
        pedidos_proc = process_pedidos_for_inference(orders_df)
        logger.info("Após process_pedidos_for_inference: {pedidos_proc.shape}")

        # If we still have no data, something is very wrong
        if pedidos_proc.shape[0] == 0:
            logger.warning(
                "Dados vazios após processamento - usando dados originais com processamento mínimo"
            )

            # Ensure we have CD_OP
            if "CD_OP" not in pedidos_proc.columns:
                pedidos_proc["CD_OP"] = (
                    pedidos_proc["CD_PEDIDO"].astype(str)
                    + "/"
                    + pedidos_proc["CD_ITEM"].astype(str)
                )

    except Exception as e:
        logger.info("Erro no processamento específico, usando dados originais: {str(e)}")
        pedidos_proc = orders_df.copy()

        # Ensure we have CD_OP
        if "CD_OP" not in pedidos_proc.columns:
            pedidos_proc["CD_OP"] = (
                pedidos_proc["CD_PEDIDO"].astype(str)
                + "/"
                + pedidos_proc["CD_ITEM"].astype(str)
            )

    # 2. Feature engineering (same as training)
    try:
        from . import feature_engineering

        pedidos_features = feature_engineering.create_geometric_features(pedidos_proc)
        logger.info("Após feature engineering: {pedidos_features.shape}")

        # If still no data, we have a fundamental problem
        if pedidos_features.shape[0] == 0:
            raise Exception("Nenhum dado restante após feature engineering")

    except Exception as e:
        raise Exception(f"Erro na criação de features: {str(e)}")

    # 3. Extract artifacts - access directly from model_artifacts
    try:
        gmm = model_artifacts.get("gmm")
        scaler = model_artifacts.get("scaler")
        pca = model_artifacts.get("pca")
        selected_features = model_artifacts.get("selected_features", [])
        if selected_features is None:
            selected_features = []
        elif not isinstance(selected_features, list):
            try:
                selected_features = list(selected_features)
            except TypeError:
                selected_features = [selected_features]
        exclude_features = model_artifacts.get("exclude_features", [])
        feature_cols = model_artifacts.get("feature_cols", [])
        cluster_k = model_artifacts.get("cluster_k", 3)
        model_type = model_artifacts.get("model_type", "unknown")
        estimator_key = "classifier" if task_type == "classification" else "regressor"
        estimator = model_artifacts.get(estimator_key)

        # Fallback for legacy artifacts without explicit task type
        if estimator is None and estimator_key == "regressor":
            estimator = model_artifacts.get("classifier")
        elif estimator is None and estimator_key == "classifier":
            estimator = model_artifacts.get("regressor")

        if gmm is None:
            raise KeyError("GMM model não encontrado nos artefatos")
        if estimator is None:
            raise KeyError("Modelo treinado não encontrado nos artefatos")

        estimator_type = type(estimator).__name__
        estimator_module = type(estimator).__module__

        # Check if it's CatBoost
        is_catboost = (
            "catboost" in estimator_module.lower()
            or "catboost" in estimator_type.lower()
            or model_type.lower() == "catboost"
        )

        logger.info("Artefatos carregados:")
        logger.info("   Modelo: {estimator_type} (module: {estimator_module})")
        logger.info("   Model type: {model_type} | Task: {task_type}")
        logger.info("   Is CatBoost: {is_catboost}")
        logger.info(
            f"   GMM={gmm is not None}, Scaler={scaler is not None}, PCA={pca is not None}"
        )

        if selected_features:
            training_feature_order = selected_features.copy()
        elif hasattr(estimator, "feature_names_in_"):
            try:
                training_feature_order = list(estimator.feature_names_in_)
            except Exception:
                training_feature_order = []

    except Exception as e:
        raise Exception(f"Erro ao extrair artefatos do modelo: {str(e)}")

    # 4. Prepare features for clustering
    try:
        # Use feature_cols from training if available
        if feature_cols and len(feature_cols) > 0:
            # Build matrix with full training feature set, filling missing columns
            X_clustering = pd.DataFrame(
                0.0, index=pedidos_features.index, columns=feature_cols
            )
            existing_cols = [
                col for col in feature_cols if col in pedidos_features.columns
            ]
            if existing_cols:
                X_clustering.loc[:, existing_cols] = pedidos_features[existing_cols]

            missing_cols = [col for col in feature_cols if col not in existing_cols]
            logger.info(
                f"Usando feature_cols do treinamento: {len(feature_cols)} total "
            )

            if missing_cols:
                logger.info("   Features ausentes preenchidas com 0: {missing_cols[:10]}")

            available_cols = feature_cols
        else:
            # Fallback to basic numeric columns
            basic_cols = [
                "VL_COMPRIMENTO",
                "VL_LARGURA",
                "VL_GRAMATURA",
                "QT_PEDIDA",
                "QT_NRCORES",
            ]
            available_cols = [
                col for col in basic_cols if col in pedidos_features.columns
            ]
            X_clustering = pedidos_features[available_cols].copy()
            logger.info("Usando {len(available_cols)} colunas básicas para clustering")

        # Handle missing values
        X_clustering = X_clustering.fillna(X_clustering.median())

        # Apply scaling and PCA
        if scaler is not None:
            X_clustering_scaled = pd.DataFrame(
                scaler.transform(
                    X_clustering.values
                ),  # Use .values to avoid feature name warnings
                columns=X_clustering.columns,
                index=X_clustering.index,
            )
            logger.info("Scaling aplicado")
        else:
            X_clustering_scaled = X_clustering

        if pca is not None:
            X_clustering_pca = pd.DataFrame(
                pca.transform(X_clustering_scaled.values),  # Use .values
                index=X_clustering_scaled.index,
            )
            X_clustering_pca.columns = [
                f"PC{i + 1}" for i in range(X_clustering_pca.shape[1])
            ]
            logger.info("PCA aplicado: {X_clustering_pca.shape[1]} componentes")
        else:
            X_clustering_pca = X_clustering_scaled

    except Exception as e:
        raise Exception(f"Erro na preparação das features para clustering: {str(e)}")

    # 5. Get cluster predictions and probabilities
    try:
        cluster_predictions = gmm.predict(X_clustering_pca.values)  # Use .values
        cluster_probabilities = gmm.predict_proba(
            X_clustering_pca.values
        )  # Use .values

        logger.info(
            f"Clustering realizado: {len(set(cluster_predictions))} clusters únicos"

        # Start with original features
        X_with_clusters = pedidos_features.copy()

        # Add cluster predictions as new feature
        X_with_clusters["cluster_pred"] = cluster_predictions

        # Add cluster probabilities as new features
        for i in range(cluster_k):
            X_with_clusters[f"PROB_CLUSTER_{i}"] = cluster_probabilities[:, i]

        logger.info(
            f"Features de cluster adicionadas: cluster_pred + {cluster_k} probabilidades"
        )
    except Exception as e:
        raise Exception(f"Erro na predição de clusters: {str(e)}")

    # 6. Prepare features for prediction
    try:
        categorical_features = ["TX_COMPOSICAO", "TX_TIPOABNT", "CAT_COMPOSICAO"]
        cluster_prob_cols = [f"PROB_CLUSTER_{i}" for i in range(cluster_k)]

        if training_feature_order:
            missing_training_features = [
                feat for feat in training_feature_order if feat not in X_with_clusters.columns
            ]

            if missing_training_features:
                logger.info(
                    f"{len(missing_training_features)} features do treinamento não estavam no pedido. Preenchendo com valores padrão."
                for feat in missing_training_features:
                    if is_catboost and feat in categorical_features:
                        X_with_clusters[feat] = "UNKNOWN"
                    else:
                        X_with_clusters[feat] = 0.0

            model_features = training_feature_order.copy()
            if missing_training_features:
                logger.info("   Features preenchidas: {missing_training_features}")
            logger.info(
                f"Usando ordem de features do treinamento: {len(model_features)} colunas"
        else:
            # Fallback to numeric features when we don't know the training subset
            exclude_from_prediction = [
                "CD_OP",
                "CD_PEDIDO",
                "CD_ITEM",
                "CD_FACA",
                "ID_CLIENTE",
                "ST_PEDIDO",
                "TX_DESCRSTATUSPEDIDO",
                "TX_DESCRTIPODOPEDIDO",
                "TX_DESCTIPOENTREGA",
                "CD_PALETE",
                "CD_TIPOFT2",
                "CD_REFERENCIA",
                "CD_ESPELHO",
                "CD_FILME",
                "DT_ENTREGA2",
                "DT_ENTREGAORIGINAL",
            ]

            numeric_cols = X_with_clusters.select_dtypes(include=[np.number]).columns
            model_features = [
                col for col in numeric_cols if col not in exclude_from_prediction
            ]
            logger.info(
                f"Usando features numéricas para predição: {len(model_features)}"

            for col in cluster_prob_cols:
                if col not in model_features:
                    model_features.append(col)

            if is_catboost:
                for cat_feat in categorical_features:
                    if cat_feat not in X_with_clusters.columns:
                        X_with_clusters[cat_feat] = "UNKNOWN"
                    if cat_feat not in model_features:
                        model_features.append(cat_feat)
                logger.info("Incluindo features categóricas para CatBoost")
            else:
                logger.info("Excluindo features categóricas para {estimator_type}")

        logger.info("Features finais para predição: {len(model_features)}")
        logger.info("   Features: {model_features}")

        # Create final feature matrix
        X_model = X_with_clusters[model_features].copy()

        # Handle missing values
        for col in X_model.columns:
            if X_model[col].dtype == "object":
                X_model[col] = X_model[col].fillna("UNKNOWN")
            else:
                X_model[col] = X_model[col].fillna(
                    X_model[col].median()
                )

        logger.info("   Shape final para modelo: {X_model.shape}")

        # Debug values for the first sample to help diagnose constant predictions
        if len(X_model) > 0:
            debug_row = X_model.iloc[0]
            logger.info("Amostra de valores usados no modelo (primeira linha):")
            for feat in model_features[: min(25, len(model_features))]:
                logger.info("   - {feat}: {debug_row[feat]}")

    except Exception as e:
        raise Exception(f"Erro na preparação das features para predição: {str(e)}")

    # 7. Make predictions using the trained estimator
    try:
        if is_catboost:
            prediction_input = X_model
        else:
            X_numeric = X_model.select_dtypes(include=[np.number])
            prediction_input = X_numeric.values

        results = X_with_clusters.copy()

        if task_type == "classification":
            logger.info("Executando fluxo de classificação")
            if is_catboost:
                logger.info("   ↳ CatBoost detectado - mantendo DataFrame com features categóricas")
                predictions = estimator.predict(prediction_input)
                try:
                    probabilities = estimator.predict_proba(prediction_input)
                    if probabilities.shape[1] == 2:
                        prob_produtivo = probabilities[:, 1]
                        logger.info("Probabilidades obtidas (classificação binária)")
                    else:
                        prob_produtivo = np.max(probabilities, axis=1)
                        logger.info("Probabilidades obtidas (classificação multi-classe)")
                except Exception as prob_error:
                    prob_produtivo = predictions.astype(float)
                    logger.info("predict_proba não disponível: {str(prob_error)}")
            else:
                logger.info("   ↳ Modelo não-CatBoost - usando apenas colunas numéricas")
                predictions = estimator.predict(prediction_input)
                try:
                    probabilities = estimator.predict_proba(prediction_input)
                    if probabilities.shape[1] == 2:
                        prob_produtivo = probabilities[:, 1]
                        logger.info("Probabilidades obtidas (classificação binária)")
                    else:
                        prob_produtivo = np.max(probabilities, axis=1)
                        logger.info("Probabilidades obtidas (classificação multi-classe)")
                except Exception as prob_error:
                    prob_produtivo = predictions.astype(float)
                    logger.info("predict_proba não disponível: {str(prob_error)}")

            results["classe_prevista"] = predictions
            results["prob_produtivo"] = prob_produtivo
            logger.info("Predições de classificação realizadas: {predictions}")

        else:
            logger.info("Executando fluxo de regressão (m³/h)")
            predictions = estimator.predict(prediction_input).astype(float)
            results["pred_m3_por_hora"] = predictions

            piece_volume_mm3 = pd.Series(
                np.nan, index=pedidos_features.index, dtype=float
            )
            if "VOLUME_INTERNO" in pedidos_features.columns:
                piece_volume_mm3 = pd.to_numeric(
                    pedidos_features["VOLUME_INTERNO"], errors="coerce"
                )

            dims_cols = {
                "VL_COMPRIMENTOINTERNO",
                "VL_LARGURAINTERNA",
                "VL_ALTURAINTERNA",
            }
            if dims_cols.issubset(pedidos_features.columns):
                dims = (
                    pd.to_numeric(
                        pedidos_features["VL_COMPRIMENTOINTERNO"], errors="coerce"
                    )
                    * pd.to_numeric(
                        pedidos_features["VL_LARGURAINTERNA"], errors="coerce"
                    )
                    * pd.to_numeric(
                        pedidos_features["VL_ALTURAINTERNA"], errors="coerce"
                    )
                )
                dims = dims.replace({0: np.nan})
                piece_volume_mm3 = piece_volume_mm3.fillna(dims)

            piece_volume_m3 = piece_volume_mm3 / 1_000_000_000.0
            results["volume_peca_m3"] = piece_volume_m3

            if "QT_PEDIDA" in pedidos_features.columns:
                qt_pedida = pd.to_numeric(
                    pedidos_features["QT_PEDIDA"], errors="coerce"
                )
            else:
                qt_pedida = pd.Series(
                    np.nan, index=pedidos_features.index, dtype=float
                )

            with np.errstate(divide="ignore", invalid="ignore"):
                caixas_por_hora = predictions / piece_volume_m3
            caixas_por_hora = pd.Series(caixas_por_hora, index=results.index)
            caixas_por_hora.replace([np.inf, -np.inf], np.nan, inplace=True)
            results["pred_caixas_por_hora"] = caixas_por_hora

            volume_total_m3 = piece_volume_m3 * qt_pedida
            results["volume_total_estimado_m3"] = volume_total_m3

            with np.errstate(divide="ignore", invalid="ignore"):
                tempo_estimado = volume_total_m3 / predictions
            tempo_estimado = pd.Series(tempo_estimado, index=results.index)
            tempo_estimado.replace([np.inf, -np.inf], np.nan, inplace=True)
            results["pred_tempo_horas"] = tempo_estimado

            logger.info("Predições de regressão realizadas: {predictions}")

        logger.info("Resultados criados: {results.shape}")

    except Exception as e:
        raise Exception(f"Erro na predição do modelo: {str(e)}")

    # 8. Add feature importance if available
    try:
        def _filter_cluster_features(feat_list):
            return [
                (name, score)
                for name, score in feat_list
                if not str(name).startswith("PROB_CLUSTER_") and str(name) != "cluster_pred"
            ]

        if hasattr(estimator, "feature_importances_"):
            importance_scores = estimator.feature_importances_
            feature_importance = list(zip(model_features, importance_scores))
            feature_importance.sort(key=lambda x: abs(x[1]), reverse=True)

            filtered_importance = _filter_cluster_features(feature_importance)
            top_n = min(8, len(filtered_importance))
            top_features = filtered_importance[:top_n]
            results["top_features"] = [str(top_features)] * len(results)
            logger.info("Feature importance adicionada (do modelo)")
        elif "feature_importance" in model_artifacts:
            if isinstance(model_artifacts["feature_importance"], pd.Series):
                importance_items = list(model_artifacts["feature_importance"].items())
                filtered_importance = _filter_cluster_features(importance_items)
                top_features = sorted(
                    filtered_importance, key=lambda x: abs(x[1]), reverse=True
                )[:8]
                results["top_features"] = [str(top_features)] * len(results)
                logger.info("Feature importance adicionada (dos artefatos)")
        else:
            logger.info("Feature importance não disponível")

    except Exception as e:
        logger.info("Erro ao adicionar feature importance: {str(e)}")

    # 9. Return relevant columns
    output_columns = [
        "CD_OP",
        "CD_PEDIDO",
        "CD_ITEM",
    ]

    if task_type == "classification":
        output_columns.extend(
            [
                "classe_prevista",
                "prob_produtivo",
            ]
        )
    else:
        regression_cols = [
            "pred_m3_por_hora",
            "pred_caixas_por_hora",
            "volume_peca_m3",
            "volume_total_estimado_m3",
            "pred_tempo_horas",
        ]
        for col in regression_cols:
            if col in results.columns:
                output_columns.append(col)

    # Add cluster columns
    output_columns.extend([f"PROB_CLUSTER_{i}" for i in range(cluster_k)])
    output_columns.append("cluster_pred")

    # Add feature importance if available
    if "top_features" in results.columns:
        output_columns.append("top_features")

    # Add any other relevant columns that exist
    for col in [
        "VL_COMPRIMENTO",
        "VL_LARGURA",
        "VL_GRAMATURA",
        "QT_NRCORES",
        "QT_PEDIDA",
        "TX_COMPOSICAO",
        "TX_TIPOABNT",
    ]:
        if col in results.columns and col not in output_columns:
            output_columns.append(col)

    # Filter to existing columns
    final_columns = [col for col in output_columns if col in results.columns]

    logger.info("Retornando {len(final_columns)} colunas")

    return results[final_columns]


def load_model_artifacts(model_path: Path) -> Dict[str, Any]:
    """Load model artifacts from pickle file."""
    try:
        with open(model_path, "rb") as f:
            artifacts = pickle.load(f)
        return artifacts
    except Exception as e:
        raise Exception(f"Erro ao carregar artefatos do modelo: {str(e)}")


def predict_single_order(
    order_data: Dict[str, Any], model_artifacts: Dict[str, Any]
) -> Dict[str, Any]:
    """Make prediction for a single order."""
    order_df = pd.DataFrame([order_data])
    results = predict_orders(order_df, model_artifacts)
    return results.iloc[0].to_dict()
