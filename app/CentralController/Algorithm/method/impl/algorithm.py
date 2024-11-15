import numpy as np
from scipy import signal

from Algorithm.method.impl.functions import get_template_list, cca, get_filter, cca_q


class CCA(object):
    def __init__(self, frequency_set, data_len=None, template_list=None):
        self.frequency_set = frequency_set
        if data_len:
            self.target_list = get_template_list(np.asarray(self.frequency_set), data_len)
        elif template_list is not None:
            self.target_list = template_list
        else:
            self.target_list = []

    def fit(self, data):
        if len(self.target_list) == 0:
            self.target_list = get_template_list(np.asarray(self.frequency_set), data.shape[-1])
        p = []
        for template in self.target_list:
            rho = cca(data, np.asarray(template)[:, :data.shape[1]].T)
            p.append(rho)
        result = p.index(max(p))
        result = result + 1
        return result, p


class FBCCA(CCA):
    def __init__(self, frequency_set, data_len=None, filter_num=5, step=8, wp_min=6, wp_max=90, template_list=None):
        super().__init__(frequency_set, data_len, template_list)
        self.step = step
        self.wp_min = wp_min
        self.wp_max = wp_max
        self.wp_list = [wp_min + i * step for i in range(filter_num)]

    def fit(self, data):
        if len(self.target_list) == 0:
            self.target_list = get_template_list(np.asarray(self.frequency_set), data.shape[-1])
        cor_u = np.zeros(len(self.target_list))
        for k in range(len(self.wp_list)):
            p1 = [self.wp_list[k], self.wp_max]
            s1 = [self.wp_list[k] - 2, self.wp_max + 10]
            fb, fa = get_filter(p1, s1)
            data_temp = signal.filtfilt(fb, fa, data)
            q_temp = np.linalg.qr(data_temp.T)[0]
            cor_u += cca_q(q_temp, self.target_list, np.power(k + 1, -1.25) + 0.25)

        predict = np.argmax(cor_u) + 1
        return predict, cor_u
