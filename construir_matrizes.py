import numpy as np


def construir_ybarra(df_barras, df_ramos, df_shl, s_base, map_idx, incluir_shunts=True):
    n = len(df_barras)
    y_bus = np.zeros((n, n), dtype=complex)

    for _, ramo in df_ramos.iterrows():
        i = map_idx[int(ramo["De"])]
        j = map_idx[int(ramo["Para"])]
        z_serie = complex(ramo["r_pu"], ramo["x_pu"])
        y_serie = 1.0 / z_serie if z_serie != 0j else 0j
        y_shunt = 1j * (ramo["b_pu"] / 2.0)

        tap_val = float(ramo["tap_val"])
        if ramo["tap_tipo"] == "t:1":
            t_i, t_j = tap_val, 1.0
        elif ramo["tap_tipo"] == "1:t":
            t_i, t_j = 1.0, tap_val
        else:
            t_i, t_j = 1.0, 1.0

        if i == j:
            y_bus[i, i] += y_serie + y_shunt
        else:
            y_bus[i, i] += (t_i ** 2) * y_serie + y_shunt
            y_bus[j, j] += (t_j ** 2) * y_serie + y_shunt
            y_bus[i, j] -= (t_i * t_j) * y_serie
            y_bus[j, i] -= (t_i * t_j) * y_serie

    if incluir_shunts:
        for _, barra in df_barras.iterrows():
            if barra["Sh_MVAr"] != 0.0:
                idx = map_idx[int(barra["Barra"])]
                y_bus[idx, idx] += 1j * (barra["Sh_MVAr"] / s_base)

        if not df_shl.empty:
            for _, shunt in df_shl.iterrows():
                i = map_idx[int(shunt["De"])]
                j = map_idx[int(shunt["Para"])]
                y_bus[i, i] += 1j * (shunt["sh_de_mvar"] / s_base)
                y_bus[j, j] += 1j * (shunt["sh_pa_mvar"] / s_base)

    return y_bus


def construir_matriz_B(df_barras, df_ramos, map_idx):
    n = len(df_barras)
    b_linha = np.zeros((n, n), dtype=float)

    for _, ramo in df_ramos.iterrows():
        i = map_idx[int(ramo["De"])]
        j = map_idx[int(ramo["Para"])]
        x = float(ramo["x_pu"])
        if i != j and x != 0.0:
            b_serie = 1.0 / x
            b_linha[i, j] -= b_serie
            b_linha[j, i] -= b_serie
            b_linha[i, i] += b_serie
            b_linha[j, j] += b_serie

    return b_linha
