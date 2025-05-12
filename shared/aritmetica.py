import configuracao as conf
from astropy.time import Time
from astropy.coordinates import EarthLocation, Angle
import astropy.units as u


def converter_angulo_para_passos(angulo: float):
    return int(angulo / conf.RESOLUCAO_ATUADOR)


def ra_to_hour_angle(ra_graus):
    observador = EarthLocation(
        lat=conf.LATITUDE*u.deg, lon=conf.LONGITUDE*u.deg, height=conf.ELEVACAO*u.m)

    tempo_atual = Time.now()

    lst = tempo_atual.sidereal_time('apparent', longitude=observador.lon)

    ra_graus = ra_graus * u.deg

    ra = Angle(ra_graus)

    ra_horas = ra.to(u.hourangle)

    ha = lst - ra_horas

    ha = ha.wrap_at(24 * u.hour)

    ha_graus = ha.to(u.deg)

    return ha_graus.wrap_at(360 * u.deg).value
