import matplotlib.pyplot as plt
import numpy as np
import glob as gb
from scipy.interpolate import interp1d
from matplotlib.ticker import FormatStrFormatter
import os

e_start = np.loadtxt(os.getcwd() + r"\swv_input_params/" + "e_start.txt")
e_end = np.loadtxt(os.getcwd() + r"\swv_input_params/" + "e_end.txt")
freq_log_min = np.loadtxt(os.getcwd() + r"\swv_input_params/" + "log_freq_min.txt")
freq_log_max = np.loadtxt(os.getcwd() + r"\swv_input_params/" + "log_freq_max.txt")


def two_d_plot(k):
    path = os.getcwd() + "/data"
    files = gb.glob(path + "/*.txt")
    z2 = []
    e_new = np.linspace(e_start, e_end, 50)
    freq_log_lst = np.linspace(freq_log_min, freq_log_max, 50)

    x, y = np.meshgrid(freq_log_lst, e_new)
    for n, file in enumerate(files):
        j = np.loadtxt(file)
        j_truncated = [np.average(l) for i, l in enumerate(np.reshape(j, (-1, 10)), 1) if i % 10 == 0]
        forward = np.array([x for i, x in enumerate(j_truncated) if i % 2 == 0])
        backward = np.array([x for i, x in enumerate(j_truncated) if i % 2 != 0])
        swv_response = - 10**6*(forward - backward)/10**freq_log_lst[n]
        e_range = np.linspace(np.max(e_new), np.min(e_new), len(swv_response))
        m = interp1d(e_range, swv_response)
        z = m(e_new)
        z2.append(np.array(z))

    z3 = np.transpose(z2)

    font = {'family': 'serif', 'serif': 'Calibri', 'weight': 'bold', 'size': 12}
    plt.rc('font', **font)

    fig, ax = plt.subplots(1, 1, figsize=(6, 5))
    cont = plt.contourf(x, y, z3, 300, cmap='jet')
    ax.set_xlabel('log[$f$(Hz)]', weight='bold')
    ax.set_ylabel('E, V vs NHE', weight='bold')
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    cbar = fig.colorbar(cont, ax=ax, format="%.1f")
    cbar.set_label('\u2206 $j$/$f$, \u00B5C/cm\u00B2', weight='bold')
    plt.tight_layout()
    plt.savefig(str(k) + "2d.png", dpi=1000)
    # plt.show()


def plot_three_d(k):
    path = os.getcwd() + "/data"
    files = gb.glob(path + "/*.txt")
    z2 = []
    e_new = np.linspace(e_start, e_end, 50)
    freq_log_lst = np.linspace(freq_log_min, freq_log_max, 50)

    x, y = np.meshgrid(freq_log_lst, e_new)
    for n, file in enumerate(files):
        j = np.loadtxt(file)
        j_truncated = [np.average(l) for i, l in enumerate(np.reshape(j, (-1, 10)), 1) if i % 10 == 0]
        forward = np.array([x for i, x in enumerate(j_truncated) if i % 2 == 0])
        backward = np.array([x for i, x in enumerate(j_truncated) if i % 2 != 0])
        swv_response = - 10**6*(forward - backward)/10**freq_log_lst[n]
        e_range = np.linspace(np.max(e_new), np.min(e_new), len(swv_response))
        m = interp1d(e_range, swv_response)
        z = m(e_new)
        z2.append(np.array(z))

    z3 = np.transpose(z2)

    font = {'family': 'serif', 'serif': 'Calibri', 'weight': 'bold', 'size': 12}
    plt.rc('font', **font)
    fig = plt.figure(figsize=(6, 5))
    ax = fig.gca(projection="3d")
    surf = ax.plot_surface(x, y, z3, cmap='seismic')
    ax.set_xlabel('log[$f$(Hz)]', weight='bold')
    ax.set_ylabel('E, V vs NHE', weight='bold')
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    cbar = fig.colorbar(surf, ax=ax, format="%.1f")
    cbar.set_label('\u2206 $j$/$f$, \u00B5C/cm\u00B2', weight='bold')
    plt.tight_layout()
    plt.savefig(str(k)+"3d.png", dpi=1000)
    # plt.show()














