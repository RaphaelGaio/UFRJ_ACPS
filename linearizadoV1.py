import math

# =====================================================================
# 1. CONFIGURAÇÕES DE EXECUÇÃO E CRITÉRIO DE CONVERGÊNCIA
# =====================================================================
S_base = 100.0              # Base do sistema em MVA
slack_bus_idx = 0           # Indice da Barra Slack no Python (0 = Barra 1, 1 = Barra 2, 2 = Barra 3)

CONSIDERAR_PERDAS = True    # True = Calcula Fluxo DC iterativo com perdas | False = Sem perdas
MISMATCH_TOL = 0.0001       # (Requisito 3) Variavel para definir a tolerancia do mismatch
MAX_ITER = 15               # (Requisito 2) Limite maximo de iteracoes
CRITERIO_MISMATCH = 'theta' # 'theta' = max|th_novo - th_ant| (rad) ou 'P' = max|P_novo - P_ant| (p.u.)

# =====================================================================
# 2. ENTRADA DE DADOS DO SISTEMA (Antigo dados.py)
# =====================================================================
# Ordem Linhas: [De, Para, r, x, b_total, tap_tipo, tap_val]
dados_linhas = [
    [1, 2, 0.200,  0.400, 0.400,   '-', 1.0], 
    [1, 3, 0.100,  0.250, 0.200,   '-', 1.0], 
    [2, 3, 0.000,  0.200, 0.000, 't:1', 1.1]
]

# Ordem Barras: [Barra, PG(MW), QG(MVAr), PL(MW), QL(MVAr), V_esp, PG_MIN, PG_MAX, CG_str]
dados_barras = [
    [1,    0.0,   0.0,  100.0,  20.0,  '1<0',  50.0, 500.0, '6.PG1+0,04.PG1^2'],
    [2,    0.0,   0.0,  100.0,   0.0,    '-',  50.0, 200.0, '9.PG2+0,06.PG2^2'],
    [3,  100.0,   0.0,  300.0, 100.0,   1.05,   0.0, 100.0, '8.PG3+0,02.PG3^2']
]


# =====================================================================
# 3. FUNÇÕES MATEMÁTICAS E IMPRESSÃO AUXILIAR
# =====================================================================
def resolver_sistema_linear(A, B):
    """Resolve o sistema linear A * x = B via Eliminacao de Gauss com pivoteamento parcial."""
    n = len(B)
    M = []
    for i in range(n):
        M.append(A[i][:] + [B[i]])

    for i in range(n):
        max_el = abs(M[i][i])
        max_row = i
        for k in range(i + 1, n):
            if abs(M[k][i]) > max_el:
                max_el = abs(M[k][i])
                max_row = k

        M[i], M[max_row] = M[max_row], M[i]

        for k in range(i + 1, n):
            if M[i][i] == 0:
                continue
            c = -M[k][i] / M[i][i]
            for j in range(i, n + 1):
                M[k][j] += c * M[i][j]

    x = [0.0 for _ in range(n)]
    for i in range(n - 1, -1, -1):
        if M[i][i] == 0:
            x[i] = 0.0
        else:
            x[i] = M[i][n] / M[i][i]
        for k in range(i - 1, -1, -1):
            M[k][n] -= M[k][i] * x[i]
    return x


def imprimir_matriz(matriz):
    for linha in matriz:
        str_linha = ""
        for val in linha:
            str_linha += "%9.4f " % val
        print("[" + str_linha.strip() + "]")


def imprimir_matriz_complexa(matriz):
    for linha in matriz:
        str_linha = ""
        for val in linha:
            sinal = "+" if val.imag >= 0 else "-"
            str_linha += "%8.4f %sj%8.4f   " % (val.real, sinal, abs(val.imag))
        print("[" + str_linha.strip() + "]")


def imprimir_equacao_dc(titulo, P, B, res, barras_reduzidas):
    print("\no " + titulo)
    n = len(P)
    for i in range(n):
        b_idx = barras_reduzidas[i] + 1
        linha = "[ %8.4f ] " % P[i]
        linha += "=" if i == n // 2 else " "
        linha += " ["
        for j in range(n):
            linha += "%8.4f " % B[i][j]
        linha += "] "
        linha += "[ th_%d ] " % b_idx
        linha += "=> " if i == n // 2 else "   "
        linha += "[ th_%d ] = [ %8.4f ] rad (%7.3f graus)" % (b_idx, res[i], math.degrees(res[i]))
        print(linha)


# =====================================================================
# 4. CONSTRUÇÃO DA MATRIZ YBARRA E MATRIZ B'
# =====================================================================
def calcular_ybarra_com_detalhes(dados_linhas, num_barras):
    print("\n" + "=" * 60)
    print("CONSTRUCAO DA MATRIZ YBARRA")
    print("=" * 60)
    Ybus = [[complex(0, 0) for _ in range(num_barras)] for _ in range(num_barras)]

    print("  > Admitancias em serie (y = 1/z) e shunt (jb/2):")
    for linha in dados_linhas:
        k = int(linha[0])
        m = int(linha[1])
        r, x, b = linha[2], linha[3], linha[4]
        z = complex(r, x)
        y = 1.0 / z if z != complex(0, 0) else complex(0, 0)
        sh = complex(0, b / 2.0)
        sinal_y = "+" if y.imag >= 0 else "-"
        print("    Linha %d-%d : y_%d%d = %8.4f %s j%8.4f  |  y_sh = j%8.4f" % (k, m, k, m, y.real, sinal_y, abs(y.imag), sh.imag))

    for linha in dados_linhas:
        i = int(linha[0]) - 1
        j = int(linha[1]) - 1
        r, x, b = linha[2], linha[3], linha[4]
        tipo, t_val = linha[5], linha[6]
        if tipo == 't:1':
            t_i, t_j = t_val, 1.0
        elif tipo == '1:t':
            t_i, t_j = 1.0, t_val
        else:
            t_i, t_j = 1.0, 1.0

        z_serie = complex(r, x)
        y_serie = 1.0 / z_serie if z_serie != complex(0, 0) else complex(0, 0)
        y_shunt = complex(0, b / 2.0)

        if i == j:
            Ybus[i][i] += y_serie + y_shunt
        else:
            Ybus[i][i] += (t_i ** 2) * y_serie + y_shunt
            Ybus[j][j] += (t_j ** 2) * y_serie + y_shunt
            Ybus[i][j] -= (t_i * t_j) * y_serie
            Ybus[j][i] -= (t_i * t_j) * y_serie

    print("\n  > Elementos da Diagonal Principal (Y_ii):")
    for i in range(num_barras):
        sinal_y = "+" if Ybus[i][i].imag >= 0 else "-"
        print("    Y_%d%d = %8.4f %s j%8.4f" % (i + 1, i + 1, Ybus[i][i].real, sinal_y, abs(Ybus[i][i].imag)))

    print("\n  > Elementos Fora da Diagonal (Y_ij = -y_ij * t_i * t_j):")
    for i in range(num_barras):
        for j in range(i + 1, num_barras):
            if Ybus[i][j] != complex(0, 0):
                sinal_y = "+" if Ybus[i][j].imag >= 0 else "-"
                print("    Y_%d%d = Y_%d%d = %8.4f %s j%8.4f" % (i + 1, j + 1, j + 1, i + 1, Ybus[i][j].real, sinal_y, abs(Ybus[i][j].imag)))

    print("\n  [ Matriz Ybarra Final ]")
    imprimir_matriz_complexa(Ybus)
    return Ybus


def construir_e_detalhar_matriz_B(dados_linhas, num_barras, slack_bus):
    print("\n" + "=" * 60)
    print("CONSTRUCAO DA MATRIZ B' (FLUXO DC)")
    print("=" * 60)

    B_linha = [[0.0 for _ in range(num_barras)] for _ in range(num_barras)]
    for linha in dados_linhas:
        i = int(linha[0]) - 1
        j = int(linha[1]) - 1
        x = linha[3]
        b_serie = 1.0 / x if x != 0 else 0.0
        if i != j:
            B_linha[i][j] -= b_serie
            B_linha[j][i] -= b_serie
            B_linha[i][i] += b_serie
            B_linha[j][j] += b_serie

    for i in range(num_barras):
        if i == slack_bus:
            continue
        termos_var, termos_val, soma = [], [], 0.0
        for linha in dados_linhas:
            k, m, x = int(linha[0]) - 1, int(linha[1]) - 1, linha[3]
            if k == m or x == 0:
                continue
            if k == i or m == i:
                viz = m if k == i else k
                idx1, idx2 = min(i, viz) + 1, max(i, viz) + 1
                termos_var.append("1/x_%d%d" % (idx1, idx2))
                termos_val.append("1/%.4f" % x)
                soma += 1.0 / x
        if termos_var:
            print("  B'%d%d = %s = %s = %8.4f" % (i + 1, i + 1, " + ".join(termos_var), " + ".join(termos_val), soma))

    for i in range(num_barras):
        if i == slack_bus:
            continue
        for j in range(i + 1, num_barras):
            if j == slack_bus:
                continue
            termos_var, termos_val, soma = [], [], 0.0
            for linha in dados_linhas:
                k, m, x = int(linha[0]) - 1, int(linha[1]) - 1, linha[3]
                if k == m or x == 0:
                    continue
                if (k == i and m == j) or (k == j and m == i):
                    idx1, idx2 = min(k, m) + 1, max(k, m) + 1
                    termos_var.append("-1/x_%d%d" % (idx1, idx2))
                    termos_val.append("-1/%.4f" % x)
                    soma -= 1.0 / x
            if termos_var:
                print("  B'%d%d = B'%d%d = %s = %s = %8.4f" % (i + 1, j + 1, j + 1, i + 1, " + ".join(termos_var), " + ".join(termos_val), soma))

    print("\n  [ Matriz B' Completa ]")
    imprimir_matriz(B_linha)
    return B_linha


# =====================================================================
# 5. CÁLCULO DO FLUXO DC, PERDAS E CONVERGÊNCIA
# =====================================================================
def resolver_passo_dc(B_linha, num_barras, P_inj, slack_bus, titulo):
    B_reduzida = []
    P_reduzido = []
    barras_reduzidas = []

    for i in range(num_barras):
        if i == slack_bus:
            continue
        barras_reduzidas.append(i)
        P_reduzido.append(P_inj[i])
        linha_reduzida = []
        for j in range(num_barras):
            if j == slack_bus:
                continue
            linha_reduzida.append(B_linha[i][j])
        B_reduzida.append(linha_reduzida)

    theta_reduzido = resolver_sistema_linear(B_reduzida, P_reduzido)

    theta = [0.0 for _ in range(num_barras)]
    idx = 0
    for k in range(num_barras):
        if k == slack_bus:
            theta[k] = 0.0
        else:
            theta[k] = theta_reduzido[idx]
            idx += 1

    imprimir_equacao_dc(titulo, P_reduzido, B_reduzida, theta_reduzido, barras_reduzidas)
    return theta


def calcular_perdas(dados_linhas, theta, P_inj_base, num_barras, iteracao):
    print("\no Calculo das Perdas (Iteracao %d)" % iteracao)
    # Parte sempre do P_inj_base (PG - PL inicial) para descontar a nova estimativa de perdas
    P_inj_novo = [val for val in P_inj_base]
    perdas_ramos = {}

    str_g = "  Condutancias: "
    for linha in dados_linhas:
        k, m = int(linha[0]) - 1, int(linha[1]) - 1
        r, x = linha[2], linha[3]
        if k == m or (r == 0 and x == 0):
            continue
        denom = (r ** 2 + x ** 2)
        g_km = r / denom if denom != 0 else 0.0
        str_g += "g_%d%d = %.4f ; " % (k + 1, m + 1, g_km)
    print(str_g[:-3])

    for linha in dados_linhas:
        k, m = int(linha[0]) - 1, int(linha[1]) - 1
        r, x = linha[2], linha[3]
        if k == m or (r == 0 and x == 0):
            continue
        denom = (r ** 2 + x ** 2)
        g_km = r / denom if denom != 0 else 0.0

        perdas_km_pu = g_km * ((theta[k] - theta[m]) ** 2)
        perdas_ramos[(k, m)] = perdas_km_pu
        print("  Perdas_%d%d = %.4f * (%.4f - (%.4f))^2 = %.6f pu" % (k + 1, m + 1, g_km, theta[k], theta[m], perdas_km_pu))

    print("\no Alocacao das Perdas nas Barras (Iteracao %d)" % iteracao)
    perdas_por_barra = [0.0 for _ in range(num_barras)]
    for i in range(num_barras):
        ramos_conectados = []
        soma_perdas = 0.0
        for (k, m), perda in perdas_ramos.items():
            if i == k or i == m:
                ramos_conectados.append("Perdas_%d%d" % (k + 1, m + 1))
                soma_perdas += perda
        if len(ramos_conectados) > 0:
            perda_alocada = soma_perdas / 2.0
            perdas_por_barra[i] = perda_alocada
            str_eq = "  Perdas_%d = " % (i + 1)
            if len(ramos_conectados) > 1:
                str_eq += "(" + " + ".join(ramos_conectados) + ") / 2"
            else:
                str_eq += ramos_conectados[0] + " / 2"
            str_eq += " = %.6f pu" % perda_alocada
            print(str_eq)
            P_inj_novo[i] -= perda_alocada

    return P_inj_novo, perdas_por_barra


def calcular_fluxos_ramos(dados_linhas, theta, S_base):
    print("\n" + "=" * 60)
    print("CALCULO DOS FLUXOS FINAIS NOS RAMOS (P_km = Theta_km / x_km)")
    print("=" * 60)
    fluxos = {}
    for linha in dados_linhas:
        k = int(linha[0]) - 1
        m = int(linha[1]) - 1
        x = linha[3]
        if k == m or x == 0:
            continue
        P_km_pu = (theta[k] - theta[m]) / x
        P_km_mw = P_km_pu * S_base
        fluxos[(k, m)] = P_km_pu
        print("  P_%d%d = (%.4f - (%.4f)) / %.4f = %8.4f pu  (%8.2f MW)" % (k + 1, m + 1, theta[k], theta[m], x, P_km_pu, P_km_mw))
    return fluxos


def alocar_geracao_swing(slack_bus, fluxos, perdas_por_barra, dados_barras, S_base):
    print("\n" + "=" * 60)
    print("ALOCACAO DE GERACAO NA BARRA SWING (Barra %d)" % (slack_bus + 1))
    print("=" * 60)
    PL_swing = 0.0
    for barra in dados_barras:
        if (int(barra[0]) - 1) == slack_bus:
            PL_swing = barra[3]
            break

    perdas_swing_mw = perdas_por_barra[slack_bus] * S_base
    termos_str, vals_str = [], []
    soma_mw = 0.0

    for (k, m), fluxo_pu in fluxos.items():
        if k == slack_bus:
            fluxo_mw = fluxo_pu * S_base
            termos_str.append("P_%d%d" % (k + 1, m + 1))
            vals_str.append("%.4f" % fluxo_mw)
            soma_mw += fluxo_mw
        elif m == slack_bus:
            fluxo_mw = -fluxo_pu * S_base
            termos_str.append("P_%d%d" % (m + 1, k + 1))
            vals_str.append("%.4f" % fluxo_mw)
            soma_mw += fluxo_mw

    termos_str.append("Perdas_%d" % (slack_bus + 1))
    vals_str.append("%.4f" % perdas_swing_mw)
    soma_mw += perdas_swing_mw

    termos_str.append("PL_%d" % (slack_bus + 1))
    vals_str.append("%.4f" % PL_swing)
    soma_mw += PL_swing

    eq_str = "  P_G%d = " % (slack_bus + 1) + " + ".join(termos_str)
    val_str = " = " + " + ".join(vals_str) + " = %.4f MW" % soma_mw
    print(eq_str)
    print("      " + val_str)


# =====================================================================
# 6. ROTINA PRINCIPAL COM CONTROLE DE CONVERGÊNCIA
# =====================================================================
def executar_simulacao():
    max_de = max([linha[0] for linha in dados_linhas])
    max_para = max([linha[1] for linha in dados_linhas])
    max_bus = max([barra[0] for barra in dados_barras])
    num_barras = int(max(max_de, max_para, max_bus))

    print("=" * 60)
    print("SISTEMA DE POTENCIA - FLUXO DC CONSOLIDADO")
    print("=" * 60)
    print("Modo: %s | Tolerancia Mismatch (%s): %g | Max Iter: %d" % (
        "COM PERDAS" if CONSIDERAR_PERDAS else "SEM PERDAS",
        CRITERIO_MISMATCH, MISMATCH_TOL, MAX_ITER))

    # 1. Montagem da Ybarra e Matriz B'
    Ybus = calcular_ybarra_com_detalhes(dados_linhas, num_barras)
    B_linha = construir_e_detalhar_matriz_B(dados_linhas, num_barras, slack_bus_idx)

    # 2. Vetor de Potencia Injetada Inicial (Sem Perdas)
    P_inj_inicial = [0.0 for _ in range(num_barras)]
    for barra in dados_barras:
        indice = int(barra[0]) - 1
        P_inj_inicial[indice] = (barra[1] - barra[3]) / S_base

    # 3. Solucao Inicial (Fluxo DC Sem Perdas)
    print("\n" + "=" * 60)
    print("SOLUCAO BASE - FLUXO DC SEM PERDAS")
    print("=" * 60)
    theta_atual = resolver_passo_dc(B_linha, num_barras, P_inj_inicial, slack_bus_idx, "Flow DC sem perdas (Base)")
    P_inj_atual = [val for val in P_inj_inicial]
    perdas_por_barra = [0.0 for _ in range(num_barras)]

    # Se for configurado SEM perdas, encerra aqui (sistema linear direto)
    if not CONSIDERAR_PERDAS:
        print("\n[STATUS]: Fluxo DC sem perdas calculado diretamente (Convergido).")
        fluxos = calcular_fluxos_ramos(dados_linhas, theta_atual, S_base)
        alocar_geracao_swing(slack_bus_idx, fluxos, perdas_por_barra, dados_barras, S_base)
        return True

    # 4. Loop Iterativo para Fluxo DC com Perdas
    print("\n" + "=" * 60)
    print("PROCESSO ITERATIVO - FLUXO DC COM PERDAS")
    print("=" * 60)

    convergiu = False
    for it in range(1, MAX_ITER + 1):
        print("\n" + "-" * 60)
        print("ITERACAO %d de %d" % (it, MAX_ITER))
        print("-" * 60)

        # Atualiza perdas usando os angulos atuais e subtrai do P_inj_inicial
        P_inj_novo, perdas_por_barra = calcular_perdas(dados_linhas, theta_atual, P_inj_inicial, num_barras, it)

        # Calcula os novos angulos considerando as perdas atualizadas
        theta_novo = resolver_passo_dc(B_linha, num_barras, P_inj_novo, slack_bus_idx, "Flow DC com perdas (Iter %d)" % it)

        # Calculo dos Mismatches (nas barras exceto a Slack)
        erros_theta = []
        erros_P = []
        for i in range(num_barras):
            if i == slack_bus_idx:
                continue
            erros_theta.append(abs(theta_novo[i] - theta_atual[i]))
            erros_P.append(abs(P_inj_novo[i] - P_inj_atual[i]))

        mismatch_theta = max(erros_theta) if erros_theta else 0.0
        mismatch_P = max(erros_P) if erros_P else 0.0

        if CRITERIO_MISMATCH == 'P':
            mismatch_avaliado = mismatch_P
            nome_crit = "Delta_P"
        else:
            mismatch_avaliado = mismatch_theta
            nome_crit = "Delta_Theta"

        print("\no Verificacao de Mismatch (Iteracao %d):" % it)
        print("  Max |Delta_Theta| = %.6f rad" % mismatch_theta)
        print("  Max |Delta_P|     = %.6f pu" % mismatch_P)
        print("  Criterio avaliado (%s): %.6f <= %.6f ?" % (nome_crit, mismatch_avaliado, MISMATCH_TOL))

        # Atualiza vetores para a proxima iteracao
        theta_atual = [val for val in theta_novo]
        P_inj_atual = [val for val in P_inj_novo]

        # Requisito 1: Verifica se mismatch <= valor definido
        if mismatch_avaliado <= MISMATCH_TOL:
            convergiu = True
            print("\n" + "=" * 60)
            print("[CONVERGIU] Sistema convergiu na iteracao %d! (%s = %.6f <= %.6f)" % (
                it, nome_crit, mismatch_avaliado, MISMATCH_TOL))
            print("=" * 60)
            break

    # Requisito 2: Caso atinja o limite maximo de iteracoes sem convergir, retorna que diverge
    if not convergiu:
        print("\n" + "=" * 60)
        print("[DIVERGIU] O sistema NAO convergiu apos o limite de %d iteracoes!" % MAX_ITER)
        print("Ultimo mismatch (%s) = %.6f > Tolerancia (%.6f)" % (nome_crit, mismatch_avaliado, MISMATCH_TOL))
        print("=" * 60)
        return False

    # 5. Calculo Final de Fluxos e Geracao na Barra Swing (apenas se convergiu)
    fluxos = calcular_fluxos_ramos(dados_linhas, theta_atual, S_base)
    alocar_geracao_swing(slack_bus_idx, fluxos, perdas_por_barra, dados_barras, S_base)
    return True


# Executa o programa
executar_simulacao()