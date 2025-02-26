from pydantic import BaseModel, ConfigDict
from typing import Optional

# Definir o modelo de entrada
class JobRequirements(BaseModel):
    """
    Modelo base para informações de recrutamento.

    Atributos:
        job_requirements (str): Requisitos do cargo para recrutamento de funcionario.
    """
    job_requirements: str