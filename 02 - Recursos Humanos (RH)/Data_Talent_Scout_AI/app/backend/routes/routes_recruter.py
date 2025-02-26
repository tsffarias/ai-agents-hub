import os
import logging
import uvicorn
from dotenv import load_dotenv
from fastapi import APIRouter, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models.recruter_schema import JobRequirements
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import SerperDevTool

# Importando schema
from models.candidate_schema import Candidate

# Configuração inicial
load_dotenv()
logger = logging.getLogger(__name__)

# Configuração do FastAPI Router
router = APIRouter()

# Inicialização do modelo LLM
def initialize_llm() -> LLM:
    return LLM(
        model='ollama/deepseek-r1:8b',
        base_url='http://localhost:11434',
        temperature=0.1,
        api_base="http://localhost:11434",
        api_key=None
    )

# ============================== #
#   Definição de Agents e Tools
# ============================== #
def create_researcher_agent(llm: LLM) -> Agent:
    serper_api_key = os.getenv("SERPER_API_KEY")
    search_tool = SerperDevTool(api_key=serper_api_key)

    return Agent(
        role='Recrutador Senior de Dados',
        goal='Encontrar os melhores perfis de dados para trabalhar baseados nos requisitos da vaga',
        backstory=(
            "Especialista em Recrutamento Técnico para Dados com 10 anos de experiência, "
            "domínio avançado de técnicas de busca em LinkedIn e GitHub, "
            "certificado em People Analytics pelo MIT."
        ),
        verbose=True,
        memory=True,
        model=llm,
        tools=[search_tool]
    )

def create_validator_agent(llm: LLM) -> Agent:
    return Agent(
        role='Validador de Candidatos',
        goal='Validar e enriquecer os dados brutos dos candidatos encontrados',
        backstory=(
            "Expert em análise de perfis profissionais, com foco em identificar informações relevantes "
            "para avaliar a adequação dos candidatos às vagas de dados."
        ),
        verbose=True,
        memory=True,
        model=llm
    )

def create_ranker_agent(llm: LLM) -> Agent:
    return Agent(
        role='Classificador de Candidatos',
        goal='Classificar e ranquear os candidatos conforme os requisitos da vaga',
        backstory=(
            "Especialista em avaliação de perfis profissionais, utiliza critérios objetivos e subjetivos "
            "para atribuir um score de adequação a cada candidato."
        ),
        verbose=True,
        memory=True,
        model=llm
    )

def create_formatter_agent(llm: LLM) -> Agent:
    return Agent(
        role='Formatador de Candidatos',
        goal='Formatar os dados processados em um JSON válido conforme o modelo especificado',
        backstory=(
            "Expert em transformação de dados, responsável por estruturar e formatar as informações "
            "para apresentação final, garantindo compatibilidade com os padrões esperados."
        ),
        verbose=True,
        memory=True,
        model=llm
    )

# ============================== #
#       Definição de Tasks
# ============================== #
def create_research_task(agent: Agent, job_requirements: str) -> Task:
    return Task(
        description=(
            "Realize uma pesquisa completa para encontrar candidatos potenciais para o cargo especificado. "
            "Utilize obrigatoriamente o LinkedIn como fonte principal. "
            f"Requisitos da vaga: {job_requirements}"
        ),
        expected_output=(
            "Retorne APENAS um JSON VÁLIDO contendo os 5 melhores candidatos potenciais no LinkedIn. "
            "Não inclua markdown ou qualquer outro formato de código. "
            "Formato esperado:\n"
            "[\n"
            "    {\n"
            '        "Nome": "Nome do Candidato",\n'
            '        "Contato": "URL do LinkedIn",\n'
            '        "Descricao": "Breve descrição do perfil destacando qualificações, experiência e localização",\n'
            '        "Score_de_adequacao": "Número que indica o quanto o candidato está alinhado (1-10)",\n'
            '        "Analise_SWOT": "Forças, Fraquezas, Oportunidades e Ameaças do candidato"\n'
            "    }\n"
            "]"
        ),
        tools=agent.tools,
        agent=agent
    )

def create_validation_task(agent: Agent) -> Task:
    return Task(
        description=(
            "Valide e enriqueça os dados brutos dos candidatos encontrados, garantindo que as informações "
            "estão completas e corretas para o processo seletivo."
        ),
        expected_output="Retorne os dados validados dos candidatos em formato JSON.",
        agent=agent
    )

def create_ranking_task(agent: Agent) -> Task:
    return Task(
        description=(
            "Classifique os candidatos validados atribuindo um score de adequação de 1 a 10 para cada perfil, "
            "baseando-se nos requisitos da vaga e nas informações disponíveis."
        ),
        expected_output="Retorne os candidatos classificados com seus respectivos scores em formato JSON.",
        agent=agent
    )

def create_formatting_task(agent: Agent) -> Task:
    return Task(
        description=(
            "Formate os dados finais dos candidatos em um JSON válido conforme o modelo esperado. "
            "Cada candidato deve ter os campos: Nome, Contato, Descricao, Score_de_adequacao e Analise_SWOT."
        ),
        expected_output="Retorne um JSON válido conforme o modelo Candidate do Pydantic.",
        output_json=Candidate,  # Especifica que o output deve estar de acordo com o modelo Candidate
        agent=agent
    )

@router.post("/research_candidates")
async def research_candidates(req: JobRequirements):
    try:
        llm = initialize_llm()

        # Criação dos agentes
        researcher = create_researcher_agent(llm)
        validator = create_validator_agent(llm)
        ranker = create_ranker_agent(llm)
        formatter = create_formatter_agent(llm)

        # Criação das tarefas
        research_task = create_research_task(researcher, req.job_requirements)
        validation_task = create_validation_task(validator)
        ranking_task = create_ranking_task(ranker)
        formatting_task = create_formatting_task(formatter)

        # Criação da crew com todos os agentes e tarefas em sequência
        crew = Crew(
            agents=[researcher, validator, ranker, formatter],
            tasks=[research_task, validation_task, ranking_task, formatting_task],
            process=Process.sequential
        )

        result = crew.kickoff(inputs={'job_requirements': req.job_requirements})
        return {"result": result}
    
    except Exception as e:
        logger.error(f"Erro na pesquisa: {str(e)}")
        return {
            "status": "error",
            "message": "Falha no processo de recrutamento",
            "details": str(e)
        }, status.HTTP_500_INTERNAL_SERVER_ERROR

# Rodar o servidor com Uvicorn
if __name__ == "__main__":
    print(">>>>>>>>>>>> version V0.1.0")
    uvicorn.run("routes.routes_recruter:router", host="0.0.0.0", port=8000, reload=True)
