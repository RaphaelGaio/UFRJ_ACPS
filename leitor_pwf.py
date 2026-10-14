import pandas as pd


def _ler_float(texto, padrao=0.0):
    s = texto.strip()
    return float(s) if s else padrao


def _ler_int(texto, padrao=0):
    s = texto.strip()
    return int(s) if s else padrao


def ler_arquivo_pwf(caminho_arquivo, incluir_dcsc=True):
    """Lê os blocos TITU, DCTE, DBAR, DLIN, DCSC e DSHL de um arquivo .PWF."""
    with open(caminho_arquivo, "r", encoding="latin-1") as arquivo:
        linhas_arq = arquivo.readlines()

    titulo = "Sistema de Potencia (.PWF)"
    constantes = {"BASE": 100.0}
    barras = []
    ramos = []
    shunts_linha = []

    bloco_atual = None
    for linha_bruta in linhas_arq:
        linha = linha_bruta.rstrip("\r\n")
        cmd = linha.strip().upper()

        if linha.startswith("("):
            continue

        if cmd == "99999":
            bloco_atual = None
            continue
        if cmd == "FIM":
            break

        if bloco_atual is None:
            token = cmd.split()[0] if cmd else ""
            if token in (
                "TITU", "DCTE", "DBAR", "DLIN", "DCSC", "DSHL",
                "DOPC", "DGER", "DCAR", "DGLT", "DARE", "DVCO",
                "DMOT", "DGBT",
            ):
                bloco_atual = token
            continue

        l_pad = linha.ljust(80)

        if bloco_atual == "TITU":
            if linha.strip():
                titulo = linha.strip()
            bloco_atual = None

        elif bloco_atual == "DCTE":
            for col in range(0, min(len(l_pad), 72), 12):
                mn = l_pad[col:col + 5].strip()
                val_str = l_pad[col + 5:col + 12].strip()
                if mn and val_str:
                    try:
                        constantes[mn] = float(val_str)
                    except ValueError:
                        pass

        elif bloco_atual == "DBAR":
            oper = l_pad[5:6].strip()
            if oper == "E":
                continue
            estado = l_pad[6:7].strip() or "L"
            if estado == "D":
                continue

            num = _ler_int(l_pad[0:5])
            tipo_raw = l_pad[7:8].strip()
            tipo = int(tipo_raw) if tipo_raw.isdigit() else 0
            nome = l_pad[10:22].strip()

            v_str = l_pad[24:28].strip()
            v_pu = (float(v_str) if "." in v_str else float(v_str) / 1000.0) if v_str else 1.0
            ang_deg = _ler_float(l_pad[28:32], 0.0)
            pg_mw = _ler_float(l_pad[32:37], 0.0)
            qg_mvar = _ler_float(l_pad[37:42], 0.0)
            pl_mw = _ler_float(l_pad[58:63], 0.0)
            ql_mvar = _ler_float(l_pad[63:68], 0.0)
            sh_mvar = _ler_float(l_pad[68:73], 0.0)

            barras.append({
                "Barra": num,
                "Nome": nome,
                "Tipo": tipo,
                "V_pu": v_pu,
                "Ang_ini_deg": ang_deg,
                "PG_MW": pg_mw,
                "QG_MVAr": qg_mvar,
                "PL_MW": pl_mw,
                "QL_MVAr": ql_mvar,
                "Sh_MVAr": sh_mvar,
            })

        elif bloco_atual == "DLIN":
            oper = l_pad[7:8].strip()
            estado = l_pad[17:18].strip() or "L"
            if oper == "E" or estado == "D":
                continue

            de = _ler_int(l_pad[0:5])
            para = _ler_int(l_pad[10:15])
            nc = _ler_int(l_pad[15:17], 1)
            r_pct = _ler_float(l_pad[20:26], 0.0)
            x_pct = _ler_float(l_pad[26:32], 0.0)
            b_mvar = _ler_float(l_pad[32:38], 0.0)
            tap_str = l_pad[38:43].strip()
            tap = float(tap_str) if tap_str else 1.0
            tem_tap = bool(tap_str)

            ramos.append({
                "De": de,
                "Para": para,
                "Nc": nc,
                "Origem": "DLIN",
                "r_pu": r_pct / 100.0,
                "x_pu": x_pct / 100.0,
                "b_mvar": b_mvar,
                "tap_tipo": "t:1" if tem_tap else "-",
                "tap_val": tap,
            })

        elif bloco_atual == "DCSC" and incluir_dcsc:
            oper = l_pad[6:7].strip()
            estado = l_pad[16:17].strip() or "L"
            if oper == "E" or estado == "D":
                continue

            de = _ler_int(l_pad[0:5])
            para = _ler_int(l_pad[9:14])
            nc = _ler_int(l_pad[14:16], 1)
            xv_pct = _ler_float(l_pad[37:43], 0.0)

            ramos.append({
                "De": de,
                "Para": para,
                "Nc": nc,
                "Origem": "DCSC",
                "r_pu": 0.0,
                "x_pu": xv_pct / 100.0,
                "b_mvar": 0.0,
                "tap_tipo": "-",
                "tap_val": 1.0,
            })

        elif bloco_atual == "DSHL":
            oper = l_pad[6:7].strip()
            if oper == "E":
                continue
            de = _ler_int(l_pad[0:5])
            para = _ler_int(l_pad[9:14])
            nc = _ler_int(l_pad[14:16], 1)
            sh_de = _ler_float(l_pad[17:23], 0.0)
            sh_pa = _ler_float(l_pad[23:29], 0.0)
            ed = l_pad[30:31].strip() or "L"
            ep = l_pad[33:34].strip() or "L"
            shunts_linha.append({
                "De": de,
                "Para": para,
                "Nc": nc,
                "sh_de_mvar": sh_de if ed != "D" else 0.0,
                "sh_pa_mvar": sh_pa if ep != "D" else 0.0,
            })

    s_base = constantes.get("BASE", 100.0)
    df_barras = pd.DataFrame(barras).sort_values("Barra").reset_index(drop=True)
    df_ramos = pd.DataFrame(ramos)
    df_ramos["b_pu"] = df_ramos["b_mvar"] / s_base
    df_shl = pd.DataFrame(shunts_linha)

    return titulo, s_base, constantes, df_barras, df_ramos, df_shl
