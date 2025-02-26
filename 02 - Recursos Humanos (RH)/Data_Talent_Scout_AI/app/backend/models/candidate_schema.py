from pydantic import BaseModel

# Modelo Pydantic para o JSON de saída
class Candidate(BaseModel):
    Nome: str
    Contato: str
    Descricao: str
    Score_de_adequacao: int
    Analise_SWOT: str