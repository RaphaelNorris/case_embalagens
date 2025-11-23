# 📊 Camadas de Dados - Medallion Architecture

Este projeto utiliza a arquitetura **Medallion** (Bronze → Silver → Gold) para organização de dados.

## 🏗️ Arquitetura

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌───────────┐
│   🥉 Raw    │────▶│  🥈 Trusted  │────▶│  🤖 ML      │────▶│  🥇 Gold  │
│  (Bronze)   │     │   (Silver)   │     │  Features   │     │ (Refined) │
└─────────────┘     └──────────────┘     └─────────────┘     └───────────┘
```

## 📁 Camadas

### 🥉 **01 - raw/** (Bronze)
Dados brutos sem transformações

### 🥈 **02 - trusted/** (Silver)
Dados limpos e validados

### 🤖 **03 - ml/** (ML)
Features engineeradas para modelos

### 🥇 **04 - refined/** (Gold)
Dados agregados para BI/analytics

## 📚 Ver Documentação Completa

Para detalhes sobre cada camada, consulte:
- `01 - raw/README.md`
- `02 - trusted/README.md`
- `03 - ml/README.md`
- `04 - refined/README.md`
