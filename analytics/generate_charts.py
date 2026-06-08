#!/usr/bin/env python3
"""Gera graficos a partir de metrics.csv."""

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

COLORS = {"success": "#2ecc71", "failure": "#e74c3c", "cancelled": "#95a5a6"}


def fig_workflow_duration(df, out):
    """1. Tempo total do pipeline por execucao."""
    runs = (df.drop_duplicates("run_id")
              .sort_values("run_number")
              .reset_index(drop=True))
    runs["label"] = runs["run_number"].astype(str) + ":" + runs["commit_short"]
    colors = runs["conclusion"].map(lambda c: COLORS.get(c, "#3498db"))
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(runs["label"], runs["workflow_duration"], color=colors, edgecolor="black")
    ax.set_xlabel("Run (numero:commit)")
    ax.set_ylabel("Duracao total (s)")
    ax.set_title("Tempo total do workflow por execucao")
    plt.xticks(rotation=60, ha="right")
    handles = [plt.Rectangle((0, 0), 1, 1, color=v) for v in COLORS.values()]
    ax.legend(handles, COLORS.keys(), title="conclusion")
    plt.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)


def fig_jobs_stacked(df, out):
    """2. Duracao por job empilhado por run."""
    jobs = (df.dropna(subset=["job_name", "job_duration"])
              .drop_duplicates(["run_id", "job_name"])
              [["run_number", "commit_short", "job_name", "job_duration"]])
    if jobs.empty:
        return
    pivot = jobs.pivot_table(index=["run_number", "commit_short"],
                              columns="job_name",
                              values="job_duration",
                              aggfunc="sum").fillna(0)
    fig, ax = plt.subplots(figsize=(12, 5))
    pivot.plot(kind="bar", stacked=True, ax=ax,
               colormap="tab10", edgecolor="black")
    ax.set_xlabel("Run (numero:commit)")
    ax.set_ylabel("Duracao (s) — empilhado por job")
    ax.set_title("Duracao por job, empilhada por execucao")
    plt.xticks(rotation=60, ha="right")
    plt.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)


def fig_success_failure(df, out):
    """3. Taxa de sucesso e falha."""
    runs = df.drop_duplicates("run_id")["conclusion"].value_counts()
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    runs.plot(kind="bar", ax=axes[0],
              color=[COLORS.get(c, "#3498db") for c in runs.index],
              edgecolor="black")
    axes[0].set_title("Contagem de runs por conclusion")
    axes[0].set_xlabel("conclusion")
    axes[0].set_ylabel("num de runs")
    runs.plot(kind="pie", ax=axes[1],
              colors=[COLORS.get(c, "#3498db") for c in runs.index],
              autopct="%1.0f%%", startangle=90)
    axes[1].set_title("Distribuicao %")
    axes[1].set_ylabel("")
    plt.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)


def fig_tests_vs_duration(df, out):
    """4. Relacao entre quantidade de testes e duracao."""
    runs = (df.drop_duplicates("run_id")
              .dropna(subset=["test_count", "workflow_duration"])
              .copy())
    runs["test_count"] = pd.to_numeric(runs["test_count"], errors="coerce")
    runs["workflow_duration"] = pd.to_numeric(runs["workflow_duration"], errors="coerce")
    runs = runs.dropna()
    if runs.empty:
        return
    fig, ax = plt.subplots(figsize=(8, 6))
    colors = runs["conclusion"].map(lambda c: COLORS.get(c, "#3498db"))
    ax.scatter(runs["test_count"], runs["workflow_duration"],
               c=colors, s=80, edgecolor="black")
    if len(runs) >= 2:
        coef = np.polyfit(runs["test_count"], runs["workflow_duration"], 1)
        xline = np.linspace(runs["test_count"].min(), runs["test_count"].max(), 50)
        ax.plot(xline, np.polyval(coef, xline), "k--", alpha=0.5,
                label=f"y = {coef[0]:.2f}x + {coef[1]:.1f}")
        ax.legend()
    ax.set_xlabel("Quantidade de testes")
    ax.set_ylabel("Duracao do workflow (s)")
    ax.set_title("Quantidade de testes vs duracao")
    plt.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)


def fig_step_boxplot(df, out):
    """5. Boxplot de duracao por step."""
    steps = df.dropna(subset=["step_name", "step_duration"]).copy()
    steps["step_duration"] = pd.to_numeric(steps["step_duration"], errors="coerce")
    steps = steps.dropna()
    if steps.empty:
        return
    top = steps["step_name"].value_counts().head(10).index.tolist()
    steps = steps[steps["step_name"].isin(top)]
    fig, ax = plt.subplots(figsize=(12, 5))
    steps.boxplot(column="step_duration", by="step_name", ax=ax)
    ax.set_xlabel("Step")
    ax.set_ylabel("Duracao (s)")
    ax.set_title("Distribuicao da duracao por step (top 10)")
    plt.suptitle("")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", default="metrics.csv")
    p.add_argument("--outdir", default="charts")
    args = p.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.csv)
    print(f"[i] {len(df)} linhas, {df['run_id'].nunique()} runs unicas")

    fig_workflow_duration(df, outdir / "01_tempo_total_pipeline.png")
    fig_jobs_stacked(df, outdir / "02_duracao_por_job.png")
    fig_success_failure(df, outdir / "03_taxa_sucesso_falha.png")
    fig_tests_vs_duration(df, outdir / "04_testes_vs_duracao.png")
    fig_step_boxplot(df, outdir / "05_boxplot_duracao_steps.png")
    print(f"[OK] 5 graficos em {outdir}/")


if __name__ == "__main__":
    main()
