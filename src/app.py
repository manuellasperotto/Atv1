from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st
from sqlalchemy import select

from config import APP_ENV, MYSQL_URL
from database import get_session, init_db
from models import Alimento, Festa, Fornecedor, Pessoa

init_db()

st.set_page_config(page_title="Festa IFC", page_icon="🎉", layout="wide")


st.title("🎉 Gestão da Festa do IFC Campus Blumenau")
st.caption("Organize alimentos, fornecedores, colaboradores e preços de venda.")

if APP_ENV == "production" and MYSQL_URL:
    st.success("Conexão MySQL ativa para produção.")
else:
    st.info("Usando SQLite local para testes e desenvolvimento.")


@st.cache_data(show_spinner=False)
def load_summary():
    with get_session() as session:
        alimentos = session.execute(select(Alimento).order_by(Alimento.nome)).scalars().all()
        fornecedores = session.execute(select(Fornecedor).order_by(Fornecedor.nome)).scalars().all()
        pessoas = session.execute(select(Pessoa).order_by(Pessoa.nome)).scalars().all()
        festas = session.execute(select(Festa).order_by(Festa.data_festa)).scalars().all()

        total_venda = sum(item.quantidade * item.preco_venda for item in alimentos)
        alimentos_doados = sum(1 for item in alimentos if item.doado)
        total_pessoas = len(pessoas)
        total_fornecedores = len(fornecedores)
        total_festas = len(festas)

        return {
            "alimentos": alimentos,
            "fornecedores": fornecedores,
            "pessoas": pessoas,
            "festas": festas,
            "total_venda": total_venda,
            "alimentos_doados": alimentos_doados,
            "total_pessoas": total_pessoas,
            "total_fornecedores": total_fornecedores,
            "total_festas": total_festas,
        }


summary = load_summary()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Alimentos", len(summary["alimentos"]))
col2.metric("Fornecedores", summary["total_fornecedores"])
col3.metric("Pessoas", summary["total_pessoas"])
col4.metric("Receita estimada", f"R$ {summary['total_venda']:.2f}")


st.sidebar.title("Menu")
st.sidebar.caption("Dados da festa")


def render_alimentos_crud() -> None:
    with get_session() as session:
        edit_id = st.session_state.get("alimentos_edit_id")
        current = session.get(Alimento, edit_id) if edit_id else None

        fornecedores = session.execute(select(Fornecedor).order_by(Fornecedor.nome)).scalars().all()
        options = [(None, "Nenhum fornecedor")] + [(item.id, item.nome) for item in fornecedores]
        default_index = 0
        if current and current.fornecedor_id is not None:
            default_index = next((index for index, option in enumerate(options) if option[0] == current.fornecedor_id), 0)

        with st.form("form_alimentos", clear_on_submit=True):
            nome = st.text_input("Nome do alimento", value=current.nome if current else "")
            categoria = st.selectbox(
                "Categoria",
                ["salgado", "bebida", "doce", "outro"],
                index=["salgado", "bebida", "doce", "outro"].index(current.categoria) if current else 0,
            )
            quantidade = st.number_input("Quantidade", min_value=0, step=1, value=current.quantidade if current else 0)
            doado = st.checkbox("Item doado?", value=current.doado if current else False)
            fornecedor_choice = st.selectbox(
                "Fornecedor",
                options=options,
                format_func=lambda item: item[1],
                index=default_index,
            )
            preco_venda = st.number_input(
                "Preço de venda",
                min_value=0.0,
                value=current.preco_venda if current else 0.0,
                step=0.5,
                format="%.2f",
            )
            observacoes = st.text_area("Observações", value=current.observacoes if current else "")

            if st.form_submit_button("Salvar alimento" if current is None else "Atualizar alimento"):
                if current is None:
                    item = Alimento(
                        nome=nome,
                        categoria=categoria,
                        quantidade=int(quantidade),
                        doado=doado,
                        fornecedor_id=fornecedor_choice[0],
                        preco_venda=float(preco_venda),
                        observacoes=observacoes,
                    )
                    session.add(item)
                    st.success("Alimento cadastrado com sucesso!")
                else:
                    current.nome = nome
                    current.categoria = categoria
                    current.quantidade = int(quantidade)
                    current.doado = doado
                    current.fornecedor_id = fornecedor_choice[0]
                    current.preco_venda = float(preco_venda)
                    current.observacoes = observacoes
                    st.success("Alimento atualizado com sucesso!")

                session.commit()
                st.session_state.pop("alimentos_edit_id", None)
                st.rerun()

        st.subheader("Lista de alimentos")
        items = session.execute(select(Alimento).order_by(Alimento.nome)).scalars().all()
        if items:
            rows = [
                {
                    "Nome": item.nome,
                    "Categoria": item.categoria,
                    "Quantidade": item.quantidade,
                    "Doado": "Sim" if item.doado else "Não",
                    "Fornecedor": item.fornecedor.nome if item.fornecedor else "Nenhum",
                    "Preço de venda": f"R$ {item.preco_venda:.2f}",
                }
                for item in items
            ]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            for item in items:
                col_edit, col_del = st.columns([1, 1])
                with col_edit:
                    if st.button("Editar", key=f"edit_alimento_{item.id}"):
                        st.session_state["alimentos_edit_id"] = item.id
                        st.rerun()
                with col_del:
                    if st.button("Excluir", key=f"delete_alimento_{item.id}"):
                        session.delete(item)
                        session.commit()
                        st.success("Alimento removido com sucesso!")
                        st.rerun()
        else:
            st.info("Nenhum alimento cadastrado até o momento.")


def render_fornecedores_crud() -> None:
    with get_session() as session:
        edit_id = st.session_state.get("fornecedores_edit_id")
        current = session.get(Fornecedor, edit_id) if edit_id else None

        with st.form("form_fornecedores", clear_on_submit=True):
            nome = st.text_input("Nome do fornecedor", value=current.nome if current else "")
            contato = st.text_input("Contato", value=current.contato if current else "")
            tipo = st.selectbox(
                "Tipo",
                ["doacao", "insumo", "parceria"],
                index=["doacao", "insumo", "parceria"].index(current.tipo) if current else 0,
            )
            descricao = st.text_area("Descrição", value=current.descricao if current else "")

            if st.form_submit_button("Salvar fornecedor" if current is None else "Atualizar fornecedor"):
                if current is None:
                    fornecedor = Fornecedor(
                        nome=nome,
                        contato=contato,
                        tipo=tipo,
                        descricao=descricao,
                    )
                    session.add(fornecedor)
                    st.success("Fornecedor cadastrado com sucesso!")
                else:
                    current.nome = nome
                    current.contato = contato
                    current.tipo = tipo
                    current.descricao = descricao
                    st.success("Fornecedor atualizado com sucesso!")

                session.commit()
                st.session_state.pop("fornecedores_edit_id", None)
                st.rerun()

        st.subheader("Lista de fornecedores")
        fornecedores = session.execute(select(Fornecedor).order_by(Fornecedor.nome)).scalars().all()
        if fornecedores:
            rows = [
                {
                    "Nome": item.nome,
                    "Contato": item.contato,
                    "Tipo": item.tipo,
                    "Descrição": item.descricao or "-",
                }
                for item in fornecedores
            ]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            for item in fornecedores:
                col_edit, col_del = st.columns([1, 1])
                with col_edit:
                    if st.button("Editar", key=f"edit_fornecedor_{item.id}"):
                        st.session_state["fornecedores_edit_id"] = item.id
                        st.rerun()
                with col_del:
                    if st.button("Excluir", key=f"delete_fornecedor_{item.id}"):
                        session.delete(item)
                        session.commit()
                        st.success("Fornecedor removido com sucesso!")
                        st.rerun()
        else:
            st.info("Nenhum fornecedor cadastrado até o momento.")


def render_pessoas_crud() -> None:
    with get_session() as session:
        edit_id = st.session_state.get("pessoas_edit_id")
        current = session.get(Pessoa, edit_id) if edit_id else None

        with st.form("form_pessoas", clear_on_submit=True):
            nome = st.text_input("Nome da pessoa", value=current.nome if current else "")
            tipo = st.selectbox(
                "Tipo",
                ["aluno", "pai", "servidor", "voluntario"],
                index=["aluno", "pai", "servidor", "voluntario"].index(current.tipo) if current else 0,
            )
            funcao = st.text_input("Função", value=current.funcao if current else "")
            telefone = st.text_input("Telefone", value=current.telefone if current else "")
            disponibilidade = st.text_input("Disponibilidade", value=current.disponibilidade if current else "")

            if st.form_submit_button("Salvar pessoa" if current is None else "Atualizar pessoa"):
                if current is None:
                    pessoa = Pessoa(
                        nome=nome,
                        tipo=tipo,
                        funcao=funcao,
                        telefone=telefone,
                        disponibilidade=disponibilidade,
                    )
                    session.add(pessoa)
                    st.success("Pessoa cadastrada com sucesso!")
                else:
                    current.nome = nome
                    current.tipo = tipo
                    current.funcao = funcao
                    current.telefone = telefone
                    current.disponibilidade = disponibilidade
                    st.success("Pessoa atualizada com sucesso!")

                session.commit()
                st.session_state.pop("pessoas_edit_id", None)
                st.rerun()

        st.subheader("Lista de pessoas")
        pessoas = session.execute(select(Pessoa).order_by(Pessoa.nome)).scalars().all()
        if pessoas:
            rows = [
                {
                    "Nome": item.nome,
                    "Tipo": item.tipo,
                    "Função": item.funcao,
                    "Telefone": item.telefone or "-",
                    "Disponibilidade": item.disponibilidade or "-",
                }
                for item in pessoas
            ]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            for item in pessoas:
                col_edit, col_del = st.columns([1, 1])
                with col_edit:
                    if st.button("Editar", key=f"edit_pessoa_{item.id}"):
                        st.session_state["pessoas_edit_id"] = item.id
                        st.rerun()
                with col_del:
                    if st.button("Excluir", key=f"delete_pessoa_{item.id}"):
                        session.delete(item)
                        session.commit()
                        st.success("Pessoa removida com sucesso!")
                        st.rerun()
        else:
            st.info("Nenhuma pessoa cadastrada até o momento.")


def render_festas_crud() -> None:
    with get_session() as session:
        edit_id = st.session_state.get("festas_edit_id")
        current = session.get(Festa, edit_id) if edit_id else None

        with st.form("form_festas", clear_on_submit=True):
            nome = st.text_input("Nome da festa", value=current.nome if current else "")
            data_festa = st.date_input("Data da festa", value=current.data_festa if current else date.today())
            local = st.text_input("Local", value=current.local if current else "")
            descricao = st.text_area("Descrição", value=current.descricao if current else "")
            orcamento_estimado = st.number_input(
                "Orçamento estimado",
                min_value=0.0,
                value=current.orcamento_estimado if current else 0.0,
                step=50.0,
                format="%.2f",
            )

            if st.form_submit_button("Salvar festa" if current is None else "Atualizar festa"):
                if current is None:
                    festa = Festa(
                        nome=nome,
                        data_festa=data_festa,
                        local=local,
                        descricao=descricao,
                        orcamento_estimado=float(orcamento_estimado),
                    )
                    session.add(festa)
                    st.success("Festa cadastrada com sucesso!")
                else:
                    current.nome = nome
                    current.data_festa = data_festa
                    current.local = local
                    current.descricao = descricao
                    current.orcamento_estimado = float(orcamento_estimado)
                    st.success("Festa atualizada com sucesso!")

                session.commit()
                st.session_state.pop("festas_edit_id", None)
                st.rerun()

        st.subheader("Lista de festas")
        festas = session.execute(select(Festa).order_by(Festa.data_festa)).scalars().all()
        if festas:
            rows = [
                {
                    "Nome": item.nome,
                    "Data": item.data_festa.isoformat(),
                    "Local": item.local,
                    "Orçamento": f"R$ {item.orcamento_estimado:.2f}",
                    "Descrição": item.descricao or "-",
                }
                for item in festas
            ]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            for item in festas:
                col_edit, col_del = st.columns([1, 1])
                with col_edit:
                    if st.button("Editar", key=f"edit_festa_{item.id}"):
                        st.session_state["festas_edit_id"] = item.id
                        st.rerun()
                with col_del:
                    if st.button("Excluir", key=f"delete_festa_{item.id}"):
                        session.delete(item)
                        session.commit()
                        st.success("Festa removida com sucesso!")
                        st.rerun()
        else:
            st.info("Nenhuma festa cadastrada até o momento.")


page = st.sidebar.radio(
    "Navegação",
    ["Resumo", "Alimentos", "Fornecedores", "Pessoas", "Festa"],
)

if page == "Resumo":
    st.subheader("Resumo geral")
    st.write(
        "A festa estudantil precisa decidir os itens que serão comercializados, os insumos doados, "
        "a equipe de trabalho e os preços de venda. Os dados abaixo ajudam a organizar essa decisão."
    )
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Itens doados", summary["alimentos_doados"])
        st.metric("Total de festas cadastradas", summary["total_festas"])
    with col_b:
        st.metric("Receita estimada", f"R$ {summary['total_venda']:.2f}")
        st.metric("Fornecedores ativos", summary["total_fornecedores"])

    if summary["alimentos"]:
        dataframe = pd.DataFrame(
            [
                {
                    "Alimento": item.nome,
                    "Categoria": item.categoria,
                    "Quantidade": item.quantidade,
                    "Preço de venda": item.preco_venda,
                    "Doado": "Sim" if item.doado else "Não",
                }
                for item in summary["alimentos"]
            ]
        )
        st.dataframe(dataframe, use_container_width=True, hide_index=True)
    else:
        st.info("Ainda não há alimentos cadastrados.")

elif page == "Alimentos":
    render_alimentos_crud()
elif page == "Fornecedores":
    render_fornecedores_crud()
elif page == "Pessoas":
    render_pessoas_crud()
else:
    render_festas_crud()
