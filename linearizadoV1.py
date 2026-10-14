import numpy as np
import pandas as pd

from construir_matrizes import (
    construir_matriz_B,
    construir_ybarra,
)
from leitor_pwf import ler_arquivo_pwf

# =====================================================================
# 1. CONFIGURAÇÕES DE EXECUÇÃO E CRITÉRIO DE CONVERGÊNCIA
# =====================================================================
ARQUIVO_PWF = "IEEE14_ASP_261.pwf"

CONSIDERAR_PERDAS = True      # True = Fluxo DC iterativo com perdas | False = Fluxo DC sem perdas
MISMATCH_TOL = 1e-7           # (Requisito 3) Variavel para definir a tolerancia do mismatch
MAX_ITER = 20                 # (Requisito 2) Limite maximo de iteracoes antes de declarar divergencia
CRITERIO_MISMATCH = "theta"   # 'theta' = max|Delta_Theta| (rad) ou 'P' = max|Delta_P| (p.u.)

INCLUIR_DCSC = True           # Inclui Compensadores Serie Controlaveis (bloco DCSC) no modelo
INCLUIR_SHUNTS_YBUS = True    # Inclui shunts de barra (DBAR) e de linha (DSHL) na matriz Ybarra


def resolver_fluxo_dc(B_linha, P_inj, slack_idx):
    n = len(P_inj)
    mask = np.arange(n) != slack_idx
    B_red = B_linha[np.ix_(mask, mask)]
    P_red = P_inj[mask]

    theta = np.zeros(n, dtype=float)
    theta[mask] = np.linalg.solve(B_red, P_red)
    return theta


def calcular_perdas_ramos_e_barras(df_ramos, theta, P_inj_base, map_idx):
    n = len(theta)
    perdas_por_barra = np.zeros(n, dtype=float)
    perdas_ramos = []

    for _, r in df_ramos.iterrows():
        k = map_idx[int(r["De"])]
        m = map_idx[int(r["Para"])]
        res = float(r["r_pu"])
        x = float(r["x_pu"])
        denom = res**2 + x**2
        g_km = res / denom if (k != m and denom != 0.0) else 0.0

        perda_km_pu = g_km * ((theta[k] - theta[m]) ** 2)
        perdas_ramos.append(perda_km_pu)

        # Aloca 50% da perda do ramo para cada barra terminal
        perdas_por_barra[k] += perda_km_pu / 2.0
        perdas_por_barra[m] += perda_km_pu / 2.0

    P_inj_atualizado = P_inj_base - perdas_por_barra
    return P_inj_atualizado, perdas_por_barra, np.array(perdas_ramos)


# =====================================================================
# ROTINA PRINCIPAL COM CRITÉRIO DE CONVERGÊNCIA
# =====================================================================
def executar_fluxo_pwf():
    np.set_printoptions(linewidth=160, precision=4, suppress=True)
    pd.set_option("display.max_columns", 15)
    pd.set_option("display.width", 140)

    titulo, S_base, constantes, df_barras, df_ramos, df_shl = ler_arquivo_pwf(
        ARQUIVO_PWF, incluir_dcsc=INCLUIR_DCSC
    )

    num_barras = len(df_barras)
    map_idx = {int(b["Barra"]): idx for idx, b in df_barras.iterrows()}

    # Identifica a barra Slack (Tipo == 2 no DBAR)
    barras_slack = df_barras[df_barras["Tipo"] == 2]
    if barras_slack.empty:
        slack_idx = 0
        slack_num = int(df_barras.loc[0, "Barra"])
    else:
        slack_idx = int(barras_slack.index[0])
        slack_num = int(barras_slack.iloc[0]["Barra"])

    print("=" * 80)
    print(f"CASO PWF: {titulo}")
    print(f"S_base: {S_base:.1f} MVA | Total de Barras: {num_barras} | Barra Slack: {slack_num} (Indice {slack_idx})")
    print(f"Modo: {'COM PERDAS' if CONSIDERAR_PERDAS else 'SEM PERDAS'} | "
          f"Criterio ({CRITERIO_MISMATCH}): <= {MISMATCH_TOL:g} | Max Iter: {MAX_ITER}")
    print("=" * 80)

    # 1. Montagem das Matrizes Ybarra e B'
    Ybus = construir_ybarra(
        df_barras, df_ramos, df_shl, S_base, map_idx,
        incluir_shunts=INCLUIR_SHUNTS_YBUS,
    )
    B_linha = construir_matriz_B(df_barras, df_ramos, map_idx)

    # 2. Vetor de Potencia Ativa Injetada Inicial (Sem Perdas)
    P_inj_inicial = (df_barras["PG_MW"].to_numpy() - df_barras["PL_MW"].to_numpy()) / S_base

    # 3. Solucao Base: Fluxo DC Sem Perdas (Iteracao 0)
    theta_sem_perdas = resolver_fluxo_dc(B_linha, P_inj_inicial, slack_idx)
    theta_atual = theta_sem_perdas.copy()
    P_inj_atual = P_inj_inicial.copy()
    perdas_por_barra = np.zeros(num_barras, dtype=float)
    perdas_ramos_pu = np.zeros(len(df_ramos), dtype=float)

    # Caso configurado SEM perdas
    if not CONSIDERAR_PERDAS:
        print("\n[STATUS]: Fluxo DC sem perdas resolvido diretamente (Convergido).")
    else:
        # 4. Processo Iterativo para Fluxo DC com Perdas
        print("\n[2] ITERAÇÕES DO FLUXO DC COM PERDAS:", flush=True)
        print("-" * 80)
        print(f"{'Iter':>4} | {'Max |Delta_Theta| (rad)':>24} | {'Max |Delta_P| (p.u.)':>21} | {'Perda Total (MW)':>17} | {'Mismatch avaliado':>20} | {'Status'}", flush=True)
        print("-" * 80)

        convergiu = False
        mask_nao_slack = np.arange(num_barras) != slack_idx

        for it in range(1, MAX_ITER + 1):
            P_inj_novo, perdas_por_barra, perdas_ramos_pu = calcular_perdas_ramos_e_barras(
                df_ramos, theta_atual, P_inj_inicial, map_idx
            )
            theta_novo = resolver_fluxo_dc(B_linha, P_inj_novo, slack_idx)

            # Calcula os mismatches nas barras (exceto Slack)
            mismatch_theta = float(np.max(np.abs(theta_novo[mask_nao_slack] - theta_atual[mask_nao_slack])))
            mismatch_P = float(np.max(np.abs(P_inj_novo[mask_nao_slack] - P_inj_atual[mask_nao_slack])))

            if CRITERIO_MISMATCH.upper() == "P":
                mismatch_avaliado = mismatch_P
                nome_crit = "Delta_P"
            else:
                mismatch_avaliado = mismatch_theta
                nome_crit = "Delta_Theta"

            perda_total_mw = float(np.sum(perdas_ramos_pu) * S_base)
            atingiu_tol = mismatch_avaliado <= MISMATCH_TOL
            status_it = "CONVERGIU" if atingiu_tol else "Iterando..."

            print(
                f"{it:4d} | {mismatch_theta:24.8f} | {mismatch_P:21.8f} | "
                f"{perda_total_mw:17.4f} | {mismatch_avaliado:20.8f} | {status_it}",
                flush=True,
            )

            theta_atual = theta_novo.copy()
            P_inj_atual = P_inj_novo.copy()

            # Requisito 1: Se o mismatch <= MISMATCH_TOL, declara convergencia
            if atingiu_tol:
                convergiu = True
                print("-" * 80)
                print(f"[CONVERGIU] Solucao convergiu na iteracao {it}! "
                      f"({nome_crit} = {mismatch_avaliado:.8f} <= {MISMATCH_TOL:g})")
                break

        # Requisito 2: Se atingir o limite maximo de iteracoes sem convergir, retorna que diverge
        if not convergiu:
            print("-" * 80)
            print(f"[DIVERGIU] O sistema DIVERGIU (nao convergiu apos {MAX_ITER} iteracoes)!")
            print(f"Ultimo mismatch ({nome_crit}) = {mismatch_avaliado:.8f} > Tolerancia ({MISMATCH_TOL:g})")
            return False

    # 5. Calculo Final dos Fluxos nos Ramos e Alocacao de Geracao na Barra Slack
    fluxos_pu = []
    for idx_r, r in df_ramos.iterrows():
        k = map_idx[int(r["De"])]
        m = map_idx[int(r["Para"])]
        x = float(r["x_pu"])
        p_km = (theta_atual[k] - theta_atual[m]) / x if (k != m and x != 0.0) else 0.0
        fluxos_pu.append(p_km)
    fluxos_pu = np.array(fluxos_pu)

    # Balanco na Barra Slack (Swing)
    soma_fluxos_saindo_slack_mw = 0.0
    for idx_r, r in df_ramos.iterrows():
        k = map_idx[int(r["De"])]
        m = map_idx[int(r["Para"])]
        if k == slack_idx:
            soma_fluxos_saindo_slack_mw += fluxos_pu[idx_r] * S_base
        elif m == slack_idx:
            soma_fluxos_saindo_slack_mw -= fluxos_pu[idx_r] * S_base

    pl_slack_mw = float(df_barras.loc[slack_idx, "PL_MW"])
    perda_slack_mw = float(perdas_por_barra[slack_idx] * S_base)
    pg_slack_calc_mw = soma_fluxos_saindo_slack_mw + perda_slack_mw + pl_slack_mw

    # 6. Tabelas de Resultados Finais (Barras e Ramos)
    df_res_barras = pd.DataFrame({
        "Barra": df_barras["Barra"],
        "Nome": df_barras["Nome"],
        "Tipo": df_barras["Tipo"].map({2: "Slack", 1: "PV", 0: "PQ"}),
        "Theta_s/Perd(graus)": np.degrees(theta_sem_perdas),
        "Theta_Final(rad)": theta_atual,
        "Theta_Final(graus)": np.degrees(theta_atual),
        "Ang_PWF_AC(graus)": df_barras["Ang_ini_deg"],
        "PG_MW": df_barras["PG_MW"],
        "PL_MW": df_barras["PL_MW"],
        "Perda_Aloc(MW)": perdas_por_barra * S_base
    })
    df_res_barras.loc[slack_idx, "PG_MW"] = pg_slack_calc_mw

    df_res_ramos = pd.DataFrame({
        "De": df_ramos["De"],
        "Para": df_ramos["Para"],
        "Nc": df_ramos["Nc"],
        "Tipo": df_ramos["Origem"],
        "R(pu)": df_ramos["r_pu"],
        "X(pu)": df_ramos["x_pu"],
        "Fluxo(pu)": fluxos_pu,
        "Fluxo(MW)": fluxos_pu * S_base,
        "Perda(MW)": perdas_ramos_pu * S_base
    })

    print("\n" + "=" * 80)
    print("[3] DADOS DE ENTRADA:")
    print("=" * 80)
    print("Dados das barras:")
    print(df_barras.to_string(index=False, float_format=lambda x: f"{x:8.4f}"))

    print("\nDados dos ramos:")
    print(df_ramos.to_string(index=False, float_format=lambda x: f"{x:8.4f}"))

    print("\n" + "=" * 80)
    print("[4] RESULTADOS FINAIS POR BARRA (ÂNGULOS NODAIS E POTÊNCIAS):")
    print("=" * 80)
    print(df_res_barras.to_string(index=False, float_format=lambda x: f"{x:8.4f}"))

    print("\n" + "=" * 80)
    print("[5] FLUXO DE POTÊNCIA ATIVA E PERDAS NOS RAMOS:")
    print("=" * 80)
    print(df_res_ramos.to_string(index=False, float_format=lambda x: f"{x:8.4f}"))

    print("\n" + "=" * 80)
    print(f"[6] BALANÇO DE GERAÇÃO NA BARRA SLACK (BARRA {slack_num}):")
    print("=" * 80)
    print(f"  Soma dos Fluxos saindo da Barra {slack_num} : {soma_fluxos_saindo_slack_mw:10.4f} MW")
    print(f"  + Perdas alocadas na Barra {slack_num}      : {perda_slack_mw:10.4f} MW")
    print(f"  + Carga local (PL_{slack_num})              : {pl_slack_mw:10.4f} MW")
    print(f"  --------------------------------------------------------")
    print(f"  = Geracao Calculada (PG_{slack_num} DC)     : {pg_slack_calc_mw:10.4f} MW")
    print(f"  (Referencia PG_{slack_num} no arquivo .PWF   : {df_barras.loc[slack_idx, 'PG_MW']:10.4f} MW)")
    print(f"  Perda Total no Sistema            : {np.sum(perdas_ramos_pu) * S_base:10.4f} MW")
    print("=" * 80)

    return True


if __name__ == "__main__":
    executar_fluxo_pwf()