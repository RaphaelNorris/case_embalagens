import pandas as pd

def corrigir_tarefcon_relacoes(df_tarefcon: pd.DataFrame) -> pd.DataFrame:
    """
    Corrige e infere relacionamentos de pedido/item/cliente na tabela TAREFCON.
    
    Regras:
      - Se CD_OP contém 'pedido/item' e ID_PEDIDO e ID_ITEM estão '-1',
        extrai os valores de CD_OP e preenche.
      - Atualiza CD_OP no formato 'ID_PEDIDO/ID_ITEM' (quando ambos válidos).
      - Propaga ID_IDCLIENTE a partir de combinações únicas (pedido + item).
    """

    df = df_tarefcon.copy()

    # === 1️⃣ Corrigir ID_PEDIDO e ID_ITEM com base em CD_OP ===
    mask = (
        (df['CD_OP'] != '-1')
        & (df['ID_PEDIDO'] == '-1')
        & (df['ID_ITEM'] == '-1')
    )

    # Separar CD_OP no formato PEDIDO/ITEM
    split_df = df.loc[mask, 'CD_OP'].astype(str).str.split('/', expand=True)

    if not split_df.empty and split_df.shape[1] >= 2:
        df.loc[mask, 'ID_PEDIDO'] = split_df[0]
        df.loc[mask, 'ID_ITEM'] = split_df[1]

    # === 2️⃣ Atualizar CD_OP para refletir o formato correto ===
    mask_op_valid = df['CD_OP'] != '-1'
    df.loc[mask_op_valid, 'CD_OP'] = (
        df['ID_PEDIDO'].astype(str) + '/' + df['ID_ITEM'].astype(str)
    )

    # === 3️⃣ Mapear cliente por (ID_PEDIDO, ID_ITEM) ===
    map_clientes = (
        df.loc[df['ID_IDCLIENTE'] != -1, ['ID_PEDIDO', 'ID_ITEM', 'ID_IDCLIENTE']]
        .drop_duplicates(subset=['ID_PEDIDO', 'ID_ITEM'])
        .set_index(['ID_PEDIDO', 'ID_ITEM'])['ID_IDCLIENTE']
        .to_dict()
    )

    # === 4️⃣ Preencher ID_IDCLIENTE ausentes com base no mapa ===
    df['ID_IDCLIENTE'] = df.apply(
        lambda row: map_clientes.get((row['ID_PEDIDO'], row['ID_ITEM']), row['ID_IDCLIENTE']),
        axis=1
    )

    return df