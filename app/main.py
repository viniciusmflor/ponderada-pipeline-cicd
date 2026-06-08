"""
ASIS TaxTech Lab — FastAPI Application
API para exercicio de Business Drivers com bugs intencionais.
Cada endpoint possui versao "quebrada" (v1) e "corrigida" (v2).
"""
import os
import uuid
import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, UTC
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text
from jose import jwt

from app.database import engine, get_db, Base
from app.models import Produto, NotaFiscal, ItemNota
from app.schemas import (
    NotaFiscalResponse,
    Token, LoginRequest,
)

SECRET_KEY = os.getenv("SECRET_KEY", "asis-lab-secret-key-2026")
ALGORITHM = "HS256"

logger = logging.getLogger("asis_taxtech")
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_database()
    yield


app = FastAPI(
    title="ASIS TaxTech Lab",
    description="Lab de Business Drivers — ES09 Inteli",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    request.state.correlation_id = correlation_id
    start = time.time()
    response: Response = await call_next(request)
    duration = time.time() - start
    response.headers["X-Correlation-ID"] = correlation_id
    response.headers["X-Response-Time"] = f"{duration:.4f}s"
    return response


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "asis-taxtech-lab"}


# DRIVER 1 — VOLUMETRIA

@app.get("/v1/notas", response_model=list[NotaFiscalResponse])
def listar_notas_v1(db: Session = Depends(get_db)):
    """BUG: retorna todas as notas sem paginacao."""
    notas = db.query(NotaFiscal).all()
    for nota in notas:
        _ = nota.itens
    return notas


@app.get("/v2/notas", response_model=list[NotaFiscalResponse])
def listar_notas_v2(
    limit: int = Query(default=20, le=100, ge=1),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """CORRECAO: paginacao com limit/offset e eager loading."""
    notas = (
        db.query(NotaFiscal)
        .options(joinedload(NotaFiscal.itens))
        .order_by(NotaFiscal.id)
        .offset(offset)
        .limit(limit)
        .all()
    )
    return notas


# DRIVER 4 — SEGURANCA

@app.get("/v1/notas/busca")
def buscar_notas_v1(
    cnpj: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """BUG: SQL Injection via f-string."""
    if cnpj:
        try:
            query = f"SELECT * FROM notas_fiscais WHERE emitente_cnpj = '{cnpj}'"
            result = db.execute(text(query))
            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]
        except Exception:
            raise HTTPException(status_code=500, detail="Erro interno ao processar CNPJ")
    return []


@app.get("/v2/notas/busca")
def buscar_notas_v2(
    cnpj: Optional[str] = Query(
        None,
        min_length=14,
        max_length=14,
        pattern=r"^\d{14}$",
    ),
    db: Session = Depends(get_db),
):
    """CORRECAO: validacao de input + query parametrizada."""
    if cnpj:
        notas = (
            db.query(NotaFiscal)
            .filter(NotaFiscal.emitente_cnpj == cnpj)
            .all()
        )
        return [
            {
                "id": n.id,
                "numero": n.numero,
                "emitente_cnpj": n.emitente_cnpj,
                "valor_total": n.valor_total,
                "status": n.status,
            }
            for n in notas
        ]
    return []


# AUTENTICACAO JWT

USERS_DB = {
    "admin": "$2b$12$izGYjDkO01WodczNc4vcnOvda9LarOBS/3pupsCTKiS8F304jD/gm",
}


@app.post("/v2/auth/token", response_model=Token)
def login(credentials: LoginRequest):
    from passlib.context import CryptContext
    pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

    hashed = USERS_DB.get(credentials.username)
    if not hashed or not pwd_ctx.verify(credentials.password, hashed):
        raise HTTPException(status_code=401, detail="Credenciais invalidas")

    token = jwt.encode(
        {
            "sub": credentials.username,
            "exp": datetime.now(UTC) + timedelta(hours=1),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return Token(access_token=token)


@app.get("/v2/notas/protegido")
def endpoint_protegido(request: Request, db: Session = Depends(get_db)):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token nao fornecido")

    token = auth.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalido ou expirado")

    return {
        "message": "Acesso autorizado",
        "user": payload.get("sub"),
        "notas_count": db.query(NotaFiscal).count(),
    }


# SEED DE DADOS

def seed_database():
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        if db.query(Produto).count() > 0:
            return

        produtos = []
        for i in range(1, 11):
            p = Produto(
                codigo=f"PROD-{i:04d}",
                descricao=f"Produto Fiscal {i}",
                ncm=f"{10000000 + i}",
                preco_unitario=round(50.0 + i * 12.5, 2),
                estoque=100 + i * 10,
            )
            db.add(p)
            produtos.append(p)
        db.flush()

        for i in range(1, 201):
            nf = NotaFiscal(
                numero=f"NF-{i:06d}",
                emitente_cnpj=f"{11222333000100 + (i % 5):014d}",
                destinatario_cnpj=f"{44555666000100 + (i % 8):014d}",
                valor_total=round(100.0 + i * 7.5, 2),
                status=["emitida", "autorizada", "cancelada"][i % 3],
                data_emissao=datetime(2026, 1, 1) + timedelta(hours=i),
            )
            db.add(nf)
            db.flush()

            for j in range(1, (i % 3) + 2):
                prod = produtos[(i + j) % len(produtos)]
                db.add(ItemNota(
                    nota_id=nf.id,
                    produto_id=prod.id,
                    quantidade=j * 2,
                    valor_unitario=prod.preco_unitario,
                    valor_total=prod.preco_unitario * j * 2,
                ))

        db.commit()
        logger.info("Seed concluido: 10 produtos, 200 notas fiscais")
    except Exception as e:
        db.rollback()
        logger.error(f"Erro no seed: {e}")
    finally:
        db.close()
