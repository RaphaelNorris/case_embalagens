# Execute isso em um notebook para verificar
import pickle
from pathlib import Path

# Verificar modelo CV
cv_path = Path("/home/adami/Projeto_IA_AMCOM/project_data_science/src/model/cv_model_artifacts.pkl")
if cv_path.exists():
    with open(cv_path, "rb") as f:
        cv_model = pickle.load(f)

    print("=== MODELO CV ===")
    print(f"Tipo do classificador: {type(cv_model['classifier'])}")
    print(f"Chaves disponíveis: {list(cv_model.keys())}")
    if "model_type" in cv_model:
        print(f"Model type salvo: {cv_model['model_type']}")
else:
    print("Modelo CV não encontrado")

# Verificar modelo Flexo
flexo_path = Path("/home/adami/Projeto_IA_AMCOM/project_data_science/src/model/flexo_model_artifacts.pkl")
if flexo_path.exists():
    with open(flexo_path, "rb") as f:
        flexo_model = pickle.load(f)

    print("\n=== MODELO FLEXO ===")
    print(f"Tipo do classificador: {type(flexo_model['classifier'])}")
    print(f"Chaves disponíveis: {list(flexo_model.keys())}")
    if "model_type" in flexo_model:
        print(f"Model type salvo: {flexo_model['model_type']}")
else:
    print("Modelo Flexo não encontrado")
