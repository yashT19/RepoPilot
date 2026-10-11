from app.ai.embedding_service import EmbeddingService
from app.ai.llm_service import LLMService
from app.ai.prompt_builder import CodePromptBuilder
from app.ai.retriever import CodeRetriever
from app.ai.rag_service import RAGService

from app.agents.planner_agent import PlannerAgent
from app.agents.code_analysis_agent import CodeAnalysisAgent
from app.agents.code_modification_agent import CodeModificationAgent
from app.agents.code_review_agent import CodeReviewAgent
from app.agents.workflow import AgentWorkflow

from app.database.database import SessionLocal

from app.services.code_change_applier import CodeChangeApplier
from app.services.change_request_service import ChangeRequestService
from app.services.repository_processing_service import (
RepositoryProcessingService,
)
from app.agents.testing_agent import TestingAgent

class AppContainer:
    def __init__(self):

    # --------------------------------------------------
    # AI / Repository Processing
    # --------------------------------------------------

        self.embedding_service = EmbeddingService()

        self.processing_service = (
        RepositoryProcessingService()
    )

        self.vector_store = (
        self.processing_service.vector_store
    )

        self.retriever = CodeRetriever(
        embedding_service=self.embedding_service,
        vector_store=self.vector_store
    )

    # --------------------------------------------------
    # LLM / RAG
    # --------------------------------------------------

        self.llm_service = LLMService()

        self.prompt_builder = CodePromptBuilder()

        self.rag_service = RAGService(
        retriever=self.retriever,
        prompt_builder=self.prompt_builder,
        llm_service=self.llm_service
    )

    # --------------------------------------------------
    # Agents
    # --------------------------------------------------

        self.planner_agent = PlannerAgent(
        self.llm_service
    )

        self.code_analysis_agent = (
        CodeAnalysisAgent(
            llm_service=self.llm_service,
            retriever=self.retriever
        )
    )

        self.code_modification_agent = (
        CodeModificationAgent(
            llm_service=self.llm_service,
            retriever=self.retriever
        )
    )

        self.code_review_agent = (
        CodeReviewAgent(
            llm_service=self.llm_service,
            retriever=self.retriever
        )
    )
        # --------------------------------------------------
# Testing Agent
# --------------------------------------------------

        self.testing_agent = TestingAgent(
    llm_service=self.llm_service,
    retriever=self.retriever
)

    # --------------------------------------------------
    # Database Session
    # --------------------------------------------------

        self.db = SessionLocal()

    # --------------------------------------------------
    # Code Change Applier
    # --------------------------------------------------

        self.code_change_applier = (
        CodeChangeApplier()
    )

    # --------------------------------------------------
    # Change Request Service
    # --------------------------------------------------

        self.change_request_service = (
        ChangeRequestService(
            db=self.db,
            code_change_applier=(
                self.code_change_applier
            )
        )
    )

    # --------------------------------------------------
    # LangGraph Agent Workflow
    # --------------------------------------------------

        self.agent_workflow = AgentWorkflow(
        planner_agent=self.planner_agent,
        code_analysis_agent=(
            self.code_analysis_agent
        ),
        code_modification_agent=(
            self.code_modification_agent
        ),
        code_review_agent=(
            self.code_review_agent
        ),
        testing_agent=self.testing_agent,
        change_request_service=(
            self.change_request_service
        )
    )


container = AppContainer()
