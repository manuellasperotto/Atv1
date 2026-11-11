from __future__ import annotations

from datetime import date

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Fornecedor(Base):
    __tablename__ = "fornecedores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    contato: Mapped[str] = mapped_column(String(200), nullable=False)
    tipo: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)

    alimentos: Mapped[list["Alimento"]] = relationship(back_populates="fornecedor")


class Alimento(Base):
    __tablename__ = "alimentos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    categoria: Mapped[str] = mapped_column(String(100), nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    doado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    preco_venda: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    fornecedor_id: Mapped[int | None] = mapped_column(ForeignKey("fornecedores.id"), nullable=True)

    fornecedor: Mapped[Fornecedor | None] = relationship(back_populates="alimentos")


class Pessoa(Base):
    __tablename__ = "pessoas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    funcao: Mapped[str] = mapped_column(String(150), nullable=False)
    telefone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    disponibilidade: Mapped[str | None] = mapped_column(String(100), nullable=True)


class Festa(Base):
    __tablename__ = "festas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    data_festa: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    local: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    orcamento_estimado: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
