import Configuracao.Configuracao as conf


def converter_angulo_para_passos(angulo):
    return int(angulo / conf.RESOLUCAO_ATUADOR)
