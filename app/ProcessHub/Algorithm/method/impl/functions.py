import numpy as np
from scipy import signal


def cca(data, template):
    data = data.T
    # qr分解,data:length*channel
    q_temp = np.linalg.qr(data)[0]

    template = template.T
    q_cs = np.linalg.qr(template)[0]
    data_svd = np.dot(q_temp.T, q_cs)
    [u, s, v] = np.linalg.svd(data_svd)
    weight = [1.25, 0.67, 0.5]
    rho = sum(s[:3] * weight[:len(s[:3])])
    return rho


def cca_q(q_temp, target_list, k):
    weight = [1.25, 0.67, 0.5]
    res = np.zeros(len(target_list))
    for idx in range(len(target_list)):
        data_svd = np.dot(q_temp.T, target_list[idx])
        s = np.linalg.svd(data_svd)[1]
        a = 0
        for i in range(min(len(s), 3)):
            a += s[i] * weight[i]
        res[idx] = k * a * a
    return res


def get_template_list(frequency_set, data_len, sample_rate=250, set_phase=True, multi_times=5, qr=True):
    if set_phase:
        phase_set = [i % 4 * 0.5 for i in range(len(frequency_set))]
    else:
        phase_set = [0] * len(frequency_set)

    n = np.arange(0, data_len) / sample_rate
    if qr:
        target_list = np.zeros((len(frequency_set), data_len, multi_times * 2))
    else:
        target_list = np.zeros((len(frequency_set), multi_times * 2, data_len))
    raw = np.zeros((multi_times * 2, data_len))
    for i in range(len(frequency_set)):
        for j in range(multi_times):
            raw[j * 2] = np.cos((j + 1) * frequency_set[i] * np.pi * 2 * n + phase_set[i] * np.pi)
            raw[j * 2 + 1] = np.sin((j + 1) * frequency_set[i] * np.pi * 2 * n + phase_set[i] * np.pi)
        if qr:
            target_list[i] = np.linalg.qr(raw.T)[0]
        else:
            target_list[i] = raw
    return target_list


def get_filter(wp, ws, sample_rate=250, output='ba'):
    wp = np.asarray(wp)
    ws = np.asarray(ws)
    if output == 'ba':
        fs = sample_rate / 2
        n, wn = signal.cheb1ord(wp / fs, ws / fs, 3, 45)
        [filter_b, filter_a] = signal.cheby1(n, 0.5, wn, btype='bandpass')
        return filter_b, filter_a
    elif output == 'sos':
        sos = signal.cheby1(15, 0.5, wp, btype='bandpass', output="sos", fs=sample_rate)
        return sos
