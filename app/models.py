"""
Modelos SQLAlchemy — mapeamento objeto-relacional das tabelas.
"""
from datetime import datetime, UTC
from sqlalchemy import (
    Column, Integer, String, Float, DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from app.database import Base


class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, nullable=False)
    descricao = Column(String(200), nullable=False)
    ncm = Column(String(8), nullable=False)
    preco_unitario = Column(Float, nullable=False)
    estoque = Column(Integer, default=0)
    version = Column(Integer, default=0, nullable=False)

    itens = relationship("ItemNota", back_populates="produto")


class NotaFiscal(Base):
    __tablename__ = "notas_fiscais"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(20), unique=True, nullable=False)
    emitente_cnpj = Column(String(14), nullable=False, index=True)
    destinatario_cnpj = Column(String(14), nullable=False)
    valor_total = Column(Float, nullable=False)
    status = Column(String(20), default="emitida")
    data_emissao = Column(DateTime, default=lambda: datetime.now(UTC))

    itens = relationship("ItemNota", back_populates="nota", lazy="select")


class ItemNota(Base):
    __tablename__ = "itens_nota"

    id = Column(Integer, primary_key=True, index=True)
    nota_id = Column(Integer, ForeignKey("notas_fiscais.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade = Column(Integer, nullable=False)
    valor_unitario = Column(Float, nullable=False)
    valor_total = Column(Float, nullable=False)

    nota = relationship("NotaFiscal", back_populates="itens")
    produto = relationship("Produto", back_populates="itens")
