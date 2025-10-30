### **4. Associação de Paradas com OPs**

**Esclarecimento crítico:**
> "Não existe associação entre evento de Parada com evento de Produção. Toda vez que um evento é classificado como Ajuste (código 1), o operador informa qual será a próxima ordem e o sistema encerra a ordem anterior. Todas as paradas entre 2 eventos de Ajuste pertencem à ordem anterior."

**Regra de associação:**
1. Ordenar eventos por **MAQUINA**, **INICIO**, **FIM**
2. Eventos com `CODIGOPARADAOUCONV = 1` (Ajuste) delimitam OPs
3. Paradas entre dois Ajustes pertencem à OP anterior


**Status**:


-----------



**Status**

--------------



