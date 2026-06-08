"""
Schemas Pydantic — validacao e serializacao de dados da API.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ProdutoBase(BaseModel):
    codigo: str
    descricao: str
    ncm: str
    preco_unitario: float
    estoque: int = 0


class ProdutoCreate(ProdutoBase):
    pass


class ProdutoResponse(ProdutoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    version: int


class ItemNotaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    produto_id: int
    quantidade: int
    valor_unitario: float
    valor_total: float


class NotaFiscalBase(BaseModel):
    numero: str
    emitente_cnpj: str
    destinatario_cnpj: str
    valor_total: float
    status: str = "emitida"


class NotaFiscalResponse(NotaFiscalBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    data_emissao: datetime
    itens: list[ItemNotaResponse] = []


class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
