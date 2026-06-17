"""
Paso D — Agente LangChain + Gemini con Tool 1 (Chroma) y Tool 2 (MySQL).

Devuelve RecomendacionProducto (Pydantic).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from src.agent.config import get_gemini_model_name
from src.agent.schemas import RecomendacionProducto, SYSTEM_PROMPT_RECOMENDACION
from src.agent.tools import get_all_agent_tools
from src.model.settings import get_google_api_key


@dataclass
class AgentRunResult:
    """Resultado de una ejecución del agente."""

    consulta: str
    recomendacion: RecomendacionProducto
    pasos: list[str] = field(default_factory=list)
    mensajes: list[BaseMessage] = field(default_factory=list)


def get_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=get_gemini_model_name(),
        google_api_key=get_google_api_key(),
        temperature=0.2,
    )


def build_agent():
    """Crea el grafo del agente ReAct con salida estructurada."""
    return create_agent(
        model=get_llm(),
        tools=get_all_agent_tools(),
        system_prompt=SYSTEM_PROMPT_RECOMENDACION,
        response_format=RecomendacionProducto,
    )


def _extract_pasos(messages: list[BaseMessage]) -> list[str]:
    pasos: list[str] = []
    for msg in messages:
        if isinstance(msg, AIMessage) and msg.tool_calls:
            for call in msg.tool_calls:
                name = call.get("name", "tool")
                args = call.get("args", {})
                pasos.append(f"-> Llamó `{name}` con {args}")
        if isinstance(msg, ToolMessage):
            preview = str(msg.content)
            if len(preview) > 220:
                preview = preview[:220] + "..."
            pasos.append(f"<- Resultado `{msg.name}`: {preview}")
    return pasos


def _parse_recomendacion(result: dict) -> RecomendacionProducto:
    if "structured_response" in result and result["structured_response"] is not None:
        data = result["structured_response"]
        if isinstance(data, RecomendacionProducto):
            return data
        return RecomendacionProducto.model_validate(data)

    messages = result.get("messages", [])
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            content = msg.content
            if isinstance(content, dict):
                return RecomendacionProducto.model_validate(content)
            if isinstance(content, str) and content.strip():
                try:
                    return RecomendacionProducto.from_json(content)
                except (json.JSONDecodeError, ValueError):
                    pass
    raise ValueError(
        "El agente no devolvió una RecomendacionProducto válida. "
        "Revisa cuota de Gemini o los logs de herramientas."
    )


def ejecutar_agente(consulta: str) -> AgentRunResult:
    """
    Ejecuta el agente con la consulta del usuario.

    Ejemplo:
        ejecutar_agente(
            "Busco un producto de audio recomendable por usuarios y que cueste menos de 600 dólares"
        )
    """
    agent = build_agent()
    result = agent.invoke({"messages": [HumanMessage(content=consulta)]})
    messages = result.get("messages", [])
    recomendacion = _parse_recomendacion(result)

    return AgentRunResult(
        consulta=consulta,
        recomendacion=recomendacion,
        pasos=_extract_pasos(messages),
        mensajes=messages,
    )
