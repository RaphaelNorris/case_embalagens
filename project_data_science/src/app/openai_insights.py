"""
OpenAI Insights Module
=====================

This module provides AI-powered insights for production productivity predictions
using OpenAI's GPT models to generate contextual analysis and recommendations.
"""

from typing import Any, Dict, List, Optional, Tuple

import openai
import pandas as pd
import streamlit as st


# Default API key provided by user for fallback usage in the Streamlit UI
DEFAULT_OPENAI_API_KEY = (
    "sk-proj-2_-R0BMnvyJawABVunxuJdA6yqiHvAOWhCp8181kfJcXMGvcersBdT_Sw_Fawxd-"
    "HNH6QogwGCT3BlbkFJy-n7w0-C2yL6hjhmTXru2NuVBAUElu9dmVc1jvbNIds2oam_Vq9hgq7q4QMzRdDYwQerxO1IgA"
)

INSIGHTS_PERSONA_DESCRIPTION = (
    "Identidade: você é um Analista de Performance Industrial que domina o processo de conversão na Adami (flexo e corte & vinco) "
    "e transforma outputs do modelo em recomendações práticas para comercial, produção, desenvolvimento e diretoria. "
    "Contexto que você domina: trade-offs técnicos vs. velocidade, dinâmica comercial (precificação/competitividade), limitações de chão de fábrica "
    "e argumentos técnicos de PCP. Sua missão: traduzir as predições em decisões acionáveis (aceitar/recusar/ajustar preço, priorizar projetos, justificar capacidade), "
    "sempre quantificando em caixas/hora, custo de tempo de máquina ou impacto financeiro. "
    "Princípios de comunicação: traduza linguagem estatística em impacto operacional, contextualize no processo físico, quantifique em termos práticos, "
    "priorize acionabilidade, trate incertezas explicitamente e destaque limitações não modeladas. "
    "Regras de ouro: nunca use jargão estatístico sem explicar, diferencie flexo vs corte & vinco quando relevante, conecte achados às etapas físicas, "
    "seja honesto sobre variáveis não modeladas e aplique exemplos numéricos realistas do contexto Adami."
)

PROJECT_CONTEXT = (
    "Contexto de negócio: Adami, fabricante de embalagens de papelão ondulado, enfrenta precificação por quilo que ignora produtividade, "
    "resultando em perda de itens produtivos (5k–30k cx/h) para concorrentes, sobrecarga de itens improdutivos e impossibilidade de precificar o tempo de máquina. "
    "Impacto financeiro: margem perdida em itens produtivos vendidos abaixo do valor, custos operacionais altos em itens improdutivos e recusa de pedidos "
    "que poderiam ser lucrativos. Meta do modelo: classificar itens como PRODUTIVOS/IMPRODUTIVOS na conversão, estimar caixas/hora e identificar as principais features "
    "dimensionais, tipo de onda (B, C, D, BC, DC), gramaturas, número de cores, arranjos e tratamentos (furos, alças, janelas, resina) que impactam produtividade. "
    "Decisões habilitadas: (1) Comercial – aceitar/recusar orçamentos ou ajustar preço; (2) Desenvolvimento – priorizar projetos com melhor perfil produtivo; "
    "(3) Produção – argumentar capacidade e sequenciamento; (4) Financeiro – precificar incluindo custo de ocupação. "
    "Características do processo: etapa de conversão (chapa → caixa acabada); flexo produz 1 chapa/caixa, corte & vinco usa múltiplas caixas por ciclo e ferramental. "
    "Ruídos conhecidos: qualidade variável da chapa, desgaste de ferramental, variação entre operadores e pequenas diferenças de matéria-prima. "
    "Stakeholders: comercial quer argumentos para precificar, produção busca performance, desenvolvimento avalia viabilidade, diretoria quer competitividade/margem. "
    "Cenário atual sem modelo: decisões empíricas, recusas por achismo, falta de argumentos quantitativos e impossibilidade de estimar produtividade em desenvolvimento. "
    "Frequência de uso: diário (precificação), semanal (novos itens), mensal/trimestral (revisões). "
    "Incerteza: quando faltam dados ou há variabilidade alta, destacar intervalos e sugerir pilotos/lotes conservadores; reconhecer efeitos não modelados (desgaste de faca etc.)."
)


class ProductivityInsightsGenerator:
    """Generate AI-powered insights for productivity predictions."""

    def __init__(self, api_key: str, model: str = "gpt-4o"):
        """Initialize the insights generator.

        Parameters
        ----------
        api_key : str
            OpenAI API key
        model : str
            OpenAI model to use for generating insights
        """
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model

    def generate_prediction_insights(
        self,
        prediction_data: Dict[str, Any],
        machine_type: str,
        input_features: Dict[str, Any],
        top_features: Optional[List[Tuple[str, float]]] = None,
    ) -> str:
        """Generate insights for a single prediction.

        Parameters
        ----------
        prediction_data : dict
            Prediction results including probability and class
        machine_type : str
            Type of machine (flexo or cv)
        input_features : dict
            Input features used for prediction
        top_features : list, optional
            Top contributing features with their SHAP values

        Returns
        -------
        str
            Generated insights text
        """
        context = self._prepare_context(
            prediction_data, machine_type, input_features, top_features
        )

        prompt = f"""
        CONTEXTO OPERACIONAL DA ADAMI:
        {context}

        SOBRE O PROJETO:
        {PROJECT_CONTEXT}

        Escreva em texto puro (sem negrito, itálico ou marcação Markdown) e siga este template:
        Resumo Executivo: síntese em até 3 frases sobre a predição e impacto.
        Drivers Principais: listar até 5 fatores com explicação curta.
        Ações Prioritárias: três recomendações numeradas, orientadas a operação/fabricação.
        Riscos e Oportunidades: separar em Riscos e Oportunidades com bullets simples.
        Próximos Passos: até 3 passos com responsáveis sugeridos e horizonte temporal.

        Reforce a conexão com custo, prazo, consumo de papel/celulose e metas ESG sempre que fizer sentido.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            f"{INSIGHTS_PERSONA_DESCRIPTION} "
                            "Use linguagem clara, objetiva e orientada a ganhos operacionais. "
                            "Mantenha foco em produtividade, estabilidade da linha flexo/CV e responsabilidade ambiental."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_completion_tokens=2000,
            )

            return response.choices[0].message.content

        except Exception as e:
            error_msg = f"Erro ao gerar insights: {str(e)}"
            print(f"[OpenAI Insights] {error_msg}")
            return error_msg

    def generate_batch_insights(
        self, results_df: pd.DataFrame, machine_type: str
    ) -> str:
        """Generate insights for batch predictions.

        Parameters
        ----------
        results_df : pd.DataFrame
            DataFrame with prediction results
        machine_type : str
            Type of machine (flexo or cv)

        Returns
        -------
        str
            Generated batch insights text
        """
        total_orders = len(results_df)

        if "pred_m3_por_hora" in results_df.columns:
            avg_density = results_df["pred_m3_por_hora"].mean()
            median_density = results_df["pred_m3_por_hora"].median()
            density_p90 = results_df["pred_m3_por_hora"].quantile(0.9)
            piece_volume_mean = (
                results_df["volume_peca_m3"].mean()
                if "volume_peca_m3" in results_df.columns
                else None
            )
            total_volume_est = (
                results_df["volume_total_estimado_m3"].sum()
                if "volume_total_estimado_m3" in results_df.columns
                else None
            )
            total_time_str = "N/D"
            if "pred_tempo_horas" in results_df.columns:
                total_time = results_df["pred_tempo_horas"].sum()
                total_time_str = f"{total_time:,.2f}"

            piece_volume_str = (
                f"{piece_volume_mean:,.4f}" if piece_volume_mean is not None else "N/D"
            )
            total_volume_est_str = (
                f"{total_volume_est:,.2f}" if total_volume_est is not None else "N/D"
            )

            context = f"""
            ANÁLISE DE LOTE - MÁQUINA {machine_type.upper()}:
            - Total de pedidos: {total_orders}
            - m³/h médio: {avg_density:,.2f}
            - Mediana e P90: {median_density:,.2f} | {density_p90:,.2f}
            - Volume médio por peça (m³): {piece_volume_str}
            - Volume total estimado (m³): {total_volume_est_str}
            - Tempo agregado projetado (h): {total_time_str}
            """

            prompt = f"""
            Analise este lote de estimativas de throughput (m³/h) para a Adami e forneça insights estratégicos:

            {context}

            SOBRE O PROJETO:
            {PROJECT_CONTEXT}

            Escreva em texto puro (sem negrito/itálico). Estruture assim:
            Panorama do Lote: visão macro com métricas críticas, gargalos e impacto em PCP/logística.
            Padrões Observados: bullets com correlações entre clusters, throughput previsto e variáveis geométricas.
            Prioridades de Atuação: lista numerada destacando células/máquinas/pedidos com maior potencial ou risco (considerando m³/h e volume financeiro).
            Riscos e Oportunidades: duas listas simples (Riscos / Oportunidades) conectando com custo, atendimento e ESG.
            Plano de Monitoramento: sugestões objetivas de indicadores e cadência de acompanhamento.

            Utilize linguagem consultiva e direcione as recomendações para líderes de produção, manutenção e PCP.
            """
        else:
            high_prod_count = (results_df["classe_prevista"] == 1).sum()
            high_prod_rate = high_prod_count / total_orders
            avg_probability = results_df["prob_produtivo"].mean()

            low_prob_orders = results_df[results_df["prob_produtivo"] < 0.5]
            high_prob_orders = results_df[results_df["prob_produtivo"] > 0.8]

            context = f"""
            ANÁLISE DE LOTE - MÁQUINA {machine_type.upper()}:
            - Total de pedidos: {total_orders}
            - Pedidos com alta produtividade prevista: {high_prod_count} ({high_prod_rate:.1%})
            - Probabilidade média: {avg_probability:.1%}
            - Pedidos com baixa probabilidade (<50%): {len(low_prob_orders)}
            - Pedidos com alta probabilidade (>80%): {len(high_prob_orders)}
            """

            prompt = f"""
            Analise este lote de predições de produtividade industrial para a Adami e forneça insights estratégicos:

            {context}

            SOBRE O PROJETO:
            {PROJECT_CONTEXT}

            Escreva em texto puro (sem negrito/itálico). Estruture assim:
            Panorama do Lote: visão macro com métricas críticas, gargalos e impacto em PCP/logística.
            Padrões Observados: bullets com correlações entre clusters, classes e variáveis geométricas.
            Prioridades de Atuação: lista numerada destacando células/máquinas/pedidos prioritários e por quê.
            Riscos e Oportunidades: duas listas simples (Riscos / Oportunidades) conectando com custo, atendimento e ESG.
            Plano de Monitoramento: sugestões objetivas de indicadores e cadência de acompanhamento.

            Utilize linguagem consultiva e direcione as recomendações para líderes de produção, manutenção e PCP.
            """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            f"{INSIGHTS_PERSONA_DESCRIPTION} "
                            "Foque em insights táticos e estratégicos para gestores de produção e PCP."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_completion_tokens=5000,
            )

            return response.choices[0].message.content

        except Exception as e:
            error_msg = f"Erro ao gerar insights do lote: {str(e)}"
            print(f"[OpenAI Insights] {error_msg}")
            return error_msg

    def _prepare_context(
        self,
        prediction_data: Dict[str, Any],
        machine_type: str,
        input_features: Dict[str, Any],
        top_features: Optional[List[Tuple[str, float]]] = None,
    ) -> str:
        """Prepare context string for AI analysis."""

        prob = prediction_data.get("prob_produtivo")
        prediction = prediction_data.get("classe_prevista")
        predicted_density = prediction_data.get("pred_m3_por_hora")
        predicted_total = prediction_data.get("volume_total_estimado_m3")
        qt_pedida = prediction_data.get("qt_pedida")

        if predicted_density is not None:
            density_str = f"{predicted_density:,.2f}"
            total_str = (
                f"{predicted_total:,.2f}" if predicted_total is not None else "N/D"
            )
            context = f"""
            TIPO DE MÁQUINA: {machine_type.upper()}
            THROUGHPUT PREVISTO: {density_str} m³/h
            VOLUME TOTAL ESTIMADO: {total_str} m³
            QUANTIDADE PEDIDA: {qt_pedida if qt_pedida is not None else "N/D"}

            CARACTERÍSTICAS DO PEDIDO:
            """
        else:
            context = f"""
            TIPO DE MÁQUINA: {machine_type.upper()}
            PREDIÇÃO: {"Alta Produtividade" if prediction == 1 else "Baixa Produtividade"}
            PROBABILIDADE: {prob:.1% if prob is not None else "N/D"}

            CARACTERÍSTICAS DO PEDIDO:
            """

        for key, value in input_features.items():
            if key in ["VL_COMPRIMENTO", "VL_LARGURA", "VL_GRAMATURA"]:
                context += f"- {key}: {value} mm\n"
            elif key in ["QT_NRCORES", "QT_PEDIDA", "QT_ARRANJO"]:
                context += f"- {key}: {value}\n"
            else:
                context += f"- {key}: {value}\n"

        if top_features:
            context += "\nPRINCIPAIS FATORES INFLUENCIADORES:\n"
            for feature, importance in top_features[:5]:
                context += f"- {feature}: {importance:.3f}\n"

        cluster_cols = [
            k for k in prediction_data.keys() if k.startswith("PROB_CLUSTER_")
        ]
        if cluster_cols:
            context += "\nANÁLISE DE CLUSTERS:\n"
            for col in cluster_cols:
                cluster_num = col.split("_")[-1]
                prob_cluster = prediction_data[col]
                context += f"- Cluster {cluster_num}: {prob_cluster:.1%}\n"

        return context


def get_openai_insights_component() -> Tuple[bool, Optional[str]]:
    """Create OpenAI configuration component in sidebar.

    Returns
    -------
    tuple
        (enable_insights, api_key) where enable_insights is bool and api_key is str or None
    """
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🤖 IA Insights")

    enable_insights = st.sidebar.checkbox(
        "Ativar Insights com IA", help="Gera análises inteligentes usando OpenAI GPT"
    )

    api_key = None
    if enable_insights:
        api_key = st.sidebar.text_input(
            "OpenAI API Key",
            type="password",
            help="Insira sua chave da API OpenAI para ativar insights inteligentes",
        )

        if not api_key:
            if DEFAULT_OPENAI_API_KEY:
                st.sidebar.info("ℹ️ Usando API Key padrão pré-configurada.")
                api_key = DEFAULT_OPENAI_API_KEY
            else:
                st.sidebar.warning("⚠️ API Key necessária para ativar insights")
                return False, None

    return enable_insights, api_key


def display_ai_insights(
    insights_generator: ProductivityInsightsGenerator,
    prediction_data: Dict[str, Any],
    machine_type: str,
    input_features: Dict[str, Any],
    top_features: Optional[List[Tuple[str, float]]] = None,
):
    """Display AI-generated insights in the Streamlit app.

    Parameters
    ----------
    insights_generator : ProductivityInsightsGenerator
        Configured insights generator
    prediction_data : dict
        Prediction results
    machine_type : str
        Type of machine
    input_features : dict
        Input features used for prediction
    top_features : list, optional
        Top contributing features
    """
    st.subheader("🤖 Análise Inteligente")

    with st.spinner("Gerando insights com IA..."):
        insights = insights_generator.generate_prediction_insights(
            prediction_data, machine_type, input_features, top_features
        )

    if not isinstance(insights, str) or not insights.strip():
        print(f"[OpenAI Insights] Resposta vazia ou inválida: {insights!r}")
        st.warning("Não foi possível gerar insights neste momento.")
        return
    if insights.strip().lower().startswith("erro ao gerar insights"):
        print(f"[OpenAI Insights] {insights}")
        st.error(insights)
        return
    if insights.strip().lower().startswith("não foi possível"):
        print(f"[OpenAI Insights] {insights}")
        st.warning(
            "Não foi possível gerar insights neste momento. "
            "Verifique o console/logs para detalhes."
        )
        return

    st.markdown(
        f"""
    <div class="ai-insights">
        <div style="background: white; color: black; padding: 1rem; border-radius: 5px; margin-top: 1rem;">
            {insights.replace(chr(10), "<br>")}
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def display_batch_ai_insights(
    insights_generator: ProductivityInsightsGenerator,
    results_df: pd.DataFrame,
    machine_type: str,
):
    """Display AI-generated insights for batch predictions.

    Parameters
    ----------
    insights_generator : ProductivityInsightsGenerator
        Configured insights generator
    results_df : pd.DataFrame
        DataFrame with prediction results
    machine_type : str
        Type of machine
    """
    st.subheader("🤖 Análise Inteligente do Lote")

    with st.spinner("Gerando insights do lote com IA..."):
        insights = insights_generator.generate_batch_insights(results_df, machine_type)

    if not isinstance(insights, str) or not insights.strip():
        print(f"[OpenAI Insights] Resposta vazia ou inválida (lote): {insights!r}")
        st.warning("Não foi possível gerar insights para o lote neste momento.")
        return
    if insights.strip().lower().startswith("erro ao gerar insights"):
        print(f"[OpenAI Insights] {insights}")
        st.error(insights)
        return
    if insights.strip().lower().startswith("não foi possível"):
        print(f"[OpenAI Insights] {insights}")
        st.warning(
            "Não foi possível gerar insights para o lote neste momento. "
            "Verifique o console/logs para detalhes."
        )
        return

    st.markdown(
        f"""
    <div class="ai-insights">
        <h4>💡 Insights Estratégicos do Lote</h4>
            {insights.replace(chr(10), "<br>")}
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )
