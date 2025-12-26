import math

SPEED_OF_LIGHT = 299792458  # m/s
FRECUENCY = 2.4e9  # Hz
Pt = 10  # W
Gt = 0  # unitless
Gr = 0  # unitless



def calc_Pr (d: float) -> float:
    """
    Calculate the received power (Pr) using the Friis transmission equation.

    :param d: Distance between transmitter and receiver in meters.
    :return: Received power in watts.
    """

    L = 20 * math.log10(d) + 20 * math.log10(FRECUENCY) + 20 * math.log10(4 * math.pi / SPEED_OF_LIGHT)
    Pr = Pt + Gt + Gr - L
    return 10 ** (Pr / 10)  # Convert dBm to mW

def calc_SNR (Pr: float, N0: float) -> float:
    """
    Calculate the Signal-to-Noise Ratio (SNR).

    :param Pr: Received power in watts.
    :param N0: Noise power spectral density in watts/Hz.
    :return: SNR in dB.
    """

    return 10 * math.log10(Pr / N0)  # Convert to dB

def check_SNR (SNR: float, rate: int) -> bool:
    level = {
        6 : -82,
        9 : -81,
        12: -79,
        18: -77,
        24: -74,
        36: -70,
        48: -66,
        54: -65
    }

    return SNR >= level[rate]+85
