from sqlalchemy import Column, Integer, String, Float, Date, Enum as SQLAlchemyEnum, DateTime
from sqlalchemy.sql import func
from database.database import Base


class EmployeeModel(Base):
    """
    Modelo de dados para representar um funcionário no banco de dados.

    Atributos:
        job_requirement_id (Integer): Identificador único do requerimento do cargo, chave primária.
        job_requeriments (String): Requisitos do cargo para recrutamento de funcionario.
    """

    __tablename__ = "job_requeriments_log"

    job_requirement_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    job_requeriments = Column(String)
    created_at = Column(DateTime(timezone=True), default=func.now(), index=True)