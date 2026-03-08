import math
from datetime import datetime, timezone
import erfa
import shared.configuracao as conf


def converter_angulo_para_passos(angulo: float):
    return int(angulo / conf.RESOLUCAO_ATUADOR)


def ra_to_hour_angle(ra_graus):
    utc_now = datetime.now(timezone.utc)

    dj1, dj2 = erfa.dtf2d(
        "UTC",
        utc_now.year,
        utc_now.month,
        utc_now.day,
        utc_now.hour,
        utc_now.minute,
        utc_now.second + (utc_now.microsecond / 1_000_000.0),
    )

    # Sem acesso a DUT1, assume UT1 ~= UTC.
    ut1_1, ut1_2 = dj1, dj2
    tai1, tai2 = erfa.utctai(dj1, dj2)
    tt1, tt2 = erfa.taitt(tai1, tai2)

    rnpb = erfa.pnm06a(tt1, tt2)
    gast = erfa.gst06(ut1_1, ut1_2, tt1, tt2, rnpb)
    lst = erfa.anp(gast + math.radians(conf.LONGITUDE))

    ra_rad = math.radians(ra_graus % 360)
    ha = erfa.anp(lst - ra_rad)

    return math.degrees(ha)


def calcular_diferenca_angular(atual: float, destino: float) -> float:
    atual = atual % 360
    destino = destino % 360

    diferenca = destino - atual

    if diferenca > 180:
        diferenca -= 360
    elif diferenca < -180:
        diferenca += 360

    return diferenca
