"""Camada de persistência em banco de dados na nuvem.

Utiliza SQLAlchemy para abstrair o acesso ao banco, permitindo conexão
com qualquer provedor de PostgreSQL em nuvem (Supabase, Neon, Railway,
ElephantSQL, etc.) através da variável de ambiente ``DATABASE_URL``.

Quando ``DATABASE_URL`` não está configurada o módulo opera em modo
*graceful-off*: todas as operações retornam silenciosamente sem erro,
garantindo que o dashboard continue funcional mesmo sem banco de dados.
"""

from __future__ import annotations

import datetime
import json
import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from config import DATABASE_URL

logger = logging.getLogger(__name__)

Base = declarative_base()

# ---------------------------------------------------------------------------
# Modelo — Histórico de Rotas
# ---------------------------------------------------------------------------

class HistoricoRota(Base):  # type: ignore[misc]
    """Registro de uma rota salva pelo usuário."""

    __tablename__ = "historico_rotas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(255), nullable=False, default="Sem nome")
    cidades_json = Column(Text, nullable=False)
    distancia_km = Column(Float, nullable=False, default=0.0)
    custo_total = Column(Float, nullable=False, default=0.0)
    custo_pedagio = Column(Float, nullable=False, default=0.0)
    co2_diesel_kg = Column(Float, nullable=False, default=0.0)
    tempo_estimado = Column(String(50), nullable=False, default="—")
    veiculo = Column(String(100), nullable=False, default="N/A")
    criado_em = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    # ------ helpers de serialização ------

    def get_cidades(self) -> list[str]:
        """Deserializa a lista de cidades armazenada como JSON."""
        try:
            return json.loads(self.cidades_json)
        except (json.JSONDecodeError, TypeError):
            return []

    @staticmethod
    def cidades_para_json(cidades: list[str]) -> str:
        """Serializa uma lista de cidades para JSON."""
        return json.dumps(cidades, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Engine & Session
# ---------------------------------------------------------------------------

_engine = None
_SessionLocal = None


def _get_engine():
    """Cria (ou reutiliza) o engine SQLAlchemy a partir de DATABASE_URL."""
    global _engine  # noqa: PLW0603
    if _engine is None:
        if not DATABASE_URL:
            return None
        _engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )
    return _engine


def _get_session_factory():
    """Retorna a factory de sessões, criando-a na primeira chamada."""
    global _SessionLocal  # noqa: PLW0603
    if _SessionLocal is None:
        engine = _get_engine()
        if engine is None:
            return None
        _SessionLocal = sessionmaker(bind=engine)
    return _SessionLocal


def inicializar_banco() -> bool:
    """Cria as tabelas no banco (caso ainda não existam).

    Retorna ``True`` se o banco está disponível, ``False`` caso contrário.
    """
    engine = _get_engine()
    if engine is None:
        logger.info("DATABASE_URL não configurada — modo offline.")
        return False
    try:
        Base.metadata.create_all(engine)
        logger.info("Banco de dados inicializado com sucesso.")
        return True
    except Exception:
        logger.exception("Falha ao inicializar o banco de dados.")
        return False


@contextmanager
def get_session() -> Generator[Session | None, None, None]:
    """Context manager que fornece uma sessão de banco de dados.

    Quando o banco não está configurado, devolve ``None``.
    """
    factory = _get_session_factory()
    if factory is None:
        yield None
        return
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# ---------------------------------------------------------------------------
# Operações CRUD
# ---------------------------------------------------------------------------

def salvar_rota(
    nome: str,
    cidades: list[str],
    distancia_km: float,
    custo_total: float,
    custo_pedagio: float,
    co2_diesel_kg: float,
    tempo_estimado: str,
    veiculo: str,
) -> bool:
    """Persiste uma rota no banco de dados.  Retorna ``True`` em caso de sucesso."""
    with get_session() as session:
        if session is None:
            return False
        registro = HistoricoRota(
            nome=nome,
            cidades_json=HistoricoRota.cidades_para_json(cidades),
            distancia_km=distancia_km,
            custo_total=custo_total,
            custo_pedagio=custo_pedagio,
            co2_diesel_kg=co2_diesel_kg,
            tempo_estimado=tempo_estimado,
            veiculo=veiculo,
        )
        session.add(registro)
    return True


def listar_rotas(limite: int = 20) -> list[dict]:
    """Retorna as últimas rotas salvas (mais recentes primeiro)."""
    with get_session() as session:
        if session is None:
            return []
        registros = (
            session.query(HistoricoRota)
            .order_by(HistoricoRota.criado_em.desc())
            .limit(limite)
            .all()
        )
        return [
            {
                "id": r.id,
                "nome": r.nome,
                "cidades": r.get_cidades(),
                "distancia_km": r.distancia_km,
                "custo_total": r.custo_total,
                "custo_pedagio": r.custo_pedagio,
                "co2_diesel_kg": r.co2_diesel_kg,
                "tempo_estimado": r.tempo_estimado,
                "veiculo": r.veiculo,
                "criado_em": r.criado_em.strftime("%d/%m/%Y %H:%M") if r.criado_em else "—",
            }
            for r in registros
        ]


def excluir_rota(rota_id: int) -> bool:
    """Remove uma rota pelo ID.  Retorna ``True`` em caso de sucesso."""
    with get_session() as session:
        if session is None:
            return False
        registro = session.query(HistoricoRota).filter_by(id=rota_id).first()
        if registro:
            session.delete(registro)
            return True
    return False
