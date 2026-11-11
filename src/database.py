from __future__ import annotations

from datetime import date

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from config import DATABASE_URL
from models import Alimento, Base, Festa, Fornecedor, Pessoa

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=False, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    seed_demo_data()


def get_session() -> Session:
    return SessionLocal()


def seed_demo_data() -> None:
    with SessionLocal() as session:
        if session.execute(select(Fornecedor.id)).first() is None:
            fornecedores = [
                Fornecedor(
                    nome="Padaria do Bairro",
                    contato="(47) 3333-1111",
                    tipo="doacao",
                    descricao="Contribui com pão e doces para a festa.",
                ),
                Fornecedor(
                    nome="Mercado Alfa",
                    contato="(47) 3333-2222",
                    tipo="insumo",
                    descricao="Fornece itens de apoio para a alimentação.",
                ),
            ]
            session.add_all(fornecedores)

        if session.execute(select(Alimento.id)).first() is None:
            session.add_all(
                [
                    Alimento(
                        nome="Cachorro-quente",
                        categoria="salgado",
                        quantidade=80,
                        doado=False,
                        preco_venda=12.0,
                        observacoes="Produto mais vendido na festa.",
                    ),
                    Alimento(
                        nome="Refrigerante",
                        categoria="bebida",
                        quantidade=200,
                        doado=True,
                        preco_venda=8.0,
                        observacoes="Doação da associação de pais.",
                    ),
                ]
            )

        if session.execute(select(Pessoa.id)).first() is None:
            session.add_all(
                [
                    Pessoa(
                        nome="Maria da Silva",
                        tipo="aluno",
                        funcao="Montagem",
                        telefone="(47) 99999-1111",
                        disponibilidade="Manhã e tarde",
                    ),
                    Pessoa(
                        nome="José Oliveira",
                        tipo="servidor",
                        funcao="Financeiro",
                        telefone="(47) 99999-2222",
                        disponibilidade="Tarde",
                    ),
                ]
            )

        if session.execute(select(Festa.id)).first() is None:
            session.add(
                Festa(
                    nome="Festa Estudantil IFC",
                    data_festa=date(2026, 11, 20),
                    local="Campus Blumenau",
                    descricao="Evento para arrecadar fundos para atividades estudantis.",
                    orcamento_estimado=2500.0,
                )
            )

        session.commit()
