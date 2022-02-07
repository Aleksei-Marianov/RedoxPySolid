import matplotlib.pyplot as plt
import numpy as np
import glob as gb
from scipy.interpolate import interp1d
from matplotlib.ticker import FormatStrFormatter
import os


# enter the width of plot (in volts) in "e_new"

def plot_two_d_corrected(path, fig_name=None):
    e_start = np.loadtxt(path + r"\swv_input_params/" + "e_start.txt")
    e_end = np.loadtxt(path + r"\swv_input_params/" + "e_end.txt")
    freq_log_min = np.loadtxt(path + r"\swv_input_params/" + "log_freq_min.txt")
    freq_log_max = np.loadtxt(path + r"\swv_input_params/" + "log_freq_max.txt")

    files = gb.glob(path + "/*.txt")
    z2 = []
    e_new = np.linspace(0.2, -0.3, 50)
    e_initial = np.linspace(e_start, e_end, 50)
    freq_log_lst = np.linspace(freq_log_min, freq_log_max, 50)

    x, y = np.meshgrid(freq_log_lst, e_new)
    for n, file in enumerate(files):
        j = np.loadtxt(file)
        j_truncated = [np.average(l) for i, l in enumerate(np.reshape(j, (-1, 10)), 1) if i % 10 == 0]
        forward = np.array([x for i, x in enumerate(j_truncated) if i % 2 == 0])
        backward = np.array([x for i, x in enumerate(j_truncated) if i % 2 != 0])
        swv_response = - 10**6*(forward - backward)/10**freq_log_lst[n]
        swv_response = swv_response - min(swv_response[10:])
        swv_response = [0 if dj < 0 else dj for dj in swv_response]
        e_range = np.linspace(np.max(e_initial), np.min(e_initial), len(swv_response))
        m = interp1d(e_range, swv_response)

        z = m(e_new)
        z2.append(np.array(z))

    z3 = np.transpose(z2)

    font = {'family': 'serif', 'serif': 'Calibri', 'weight': 'bold', 'size': 12}
    plt.rc('font', **font)

    fig, ax = plt.subplots(1, 1, figsize=(6, 5))

    cont = plt.contourf(x, y, z3, 200, cmap='jet')

    ax.set_xlabel('log[$f$(Hz)]', weight='bold')

    ax.set_ylabel('E, V vs NHE', weight='bold')
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    cbar = fig.colorbar(cont, ax=ax, format="%.1f")
    cbar.set_label('-\u2206 $j$/$f$, \u00B5C/cm\u00B2', weight='bold')

    # plt.subplots_adjust(0.15, 0.12, 0.95, 0.95)
    plt.tight_layout()
    if fig_name:
        plt.savefig(f"{fig_name}.png", dpi=1000)
        plt.show()
    else:
        plt.show()


# def plot_three_d_corrected(path):
#     files = gb.glob(path + "/*.txt")
#     z2 = []
#     e_new = np.linspace(e_start, e_end, 50)
#     freq_log_lst = np.linspace(freq_log_min, freq_log_max, 50)
#
#     x, y = np.meshgrid(freq_log_lst, e_new)
#     for n, file in enumerate(files):
#         j = np.loadtxt(file)
#         j_truncated = [np.average(l) for i, l in enumerate(np.reshape(j, (-1, 10)), 1) if i % 10 == 0]
#         forward = np.array([x for i, x in enumerate(j_truncated) if i % 2 == 0])
#         backward = np.array([x for i, x in enumerate(j_truncated) if i % 2 != 0])
#         swv_response = - 10**6*(forward - backward)/10**freq_log_lst[n]
#         swv_response = swv_response - swv_response[10]
#         swv_response = [0 if dj < 0 else dj for dj in swv_response]
#         e_range = np.linspace(np.max(e_new), np.min(e_new), len(swv_response))
#         m = interp1d(e_range, swv_response)
#         z = m(e_new)
#         z2.append(np.array(z))
#
#     z3 = np.transpose(z2)
#
#     font = {'family': 'serif', 'serif': 'Calibri', 'weight': 'bold', 'size': 12}
#     plt.rc('font', **font)
#
#     fig = plt.figure(figsize=(6, 5))
#     ax = fig.gca(projection="3d")
#
#     surf = ax.plot_surface(x, y, z3, cmap='jet')
#     ax.set_xlabel('log[$f$(Hz)]', weight='bold')
#     ax.set_ylabel('E, V vs NHE', weight='bold')
#     ax.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))
#     cbar = fig.colorbar(surf, ax=ax, format="%.1f")
#     cbar.set_label('-\u2206 $j$/$f$, \u00B5C/cm\u00B2', weight='bold')
#     plt.tight_layout()
#     # plt.savefig(str(k)+"3d.png", dpi=1000)
#     plt.show()


# def plot_two_d_with_dlc(path):
#     files = gb.glob(path + "/*.txt")
#     z2 = []
#     e_new = np.linspace(e_start, e_end, 50)
#     freq_log_lst = np.linspace(freq_log_min, freq_log_max, 50)
#
#     x, y = np.meshgrid(freq_log_lst, e_new)
#     for n, file in enumerate(files):
#         j = np.loadtxt(file)
#         j_truncated = [np.average(l) for i, l in enumerate(np.reshape(j, (-1, 10)), 1) if i % 10 == 0]
#         forward = np.array([x for i, x in enumerate(j_truncated) if i % 2 == 0])
#         backward = np.array([x for i, x in enumerate(j_truncated) if i % 2 != 0])
#         swv_response = - 10**6*(forward - backward)/10**freq_log_lst[n]
#         e_range = np.linspace(np.max(e_new), np.min(e_new), len(swv_response))
#         m = interp1d(e_range, swv_response)
#         z = m(e_new)
#         z2.append(np.array(z))
#
#     z3 = np.transpose(z2)
#
#     font = {'family': 'serif', 'serif': 'Calibri', 'weight': 'bold', 'size': 12}
#     plt.rc('font', **font)
#
#     fig, ax = plt.subplots(1, 1, figsize=(6, 5))
#     cont = plt.contourf(x, y, z3, 300, cmap='jet')
#     ax.set_xlabel('log[$f$(Hz)]', weight='bold')
#     ax.set_ylabel('E, V vs NHE', weight='bold')
#     ax.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))
#     cbar = fig.colorbar(cont, ax=ax, format="%.1f")
#     cbar.set_label('-\u2206 $j$/$f$, \u00B5C/cm\u00B2', weight='bold')
#     plt.tight_layout()
#     # plt.savefig("Fig_S_CoTPP_noncov.png", dpi=1000)
#     plt.show()
#
#
# def plot_three_d_with_dlc(path):
#     files = gb.glob(path + "/*.txt")
#     z2 = []
#     e_new = np.linspace(e_start, e_end, 50)
#     freq_log_lst = np.linspace(freq_log_min, freq_log_max, 50)
#
#     x, y = np.meshgrid(freq_log_lst, e_new)
#     for n, file in enumerate(files):
#         j = np.loadtxt(file)
#         j_truncated = [np.average(l) for i, l in enumerate(np.reshape(j, (-1, 10)), 1) if i % 10 == 0]
#         forward = np.array([x for i, x in enumerate(j_truncated) if i % 2 == 0])
#         backward = np.array([x for i, x in enumerate(j_truncated) if i % 2 != 0])
#         swv_response = - 10**6*(forward - backward)/10**freq_log_lst[n]
#         e_range = np.linspace(np.max(e_new), np.min(e_new), len(swv_response))
#         m = interp1d(e_range, swv_response)
#         z = m(e_new)
#         z2.append(np.array(z))
#
#     z3 = np.transpose(z2)
#
#     font = {'family': 'serif', 'serif': 'Calibri', 'weight': 'bold', 'size': 12}
#     plt.rc('font', **font)
#     fig = plt.figure(figsize=(6, 5))
#     ax = fig.gca(projection="3d")
#     surf = ax.plot_surface(x, y, z3, cmap='jet')
#     ax.set_xlabel('log[$f$(Hz)]', weight='bold')
#     ax.set_ylabel('E, V vs NHE', weight='bold')
#     ax.xaxis.set_major_formatter(FormatStrFormatter('%.3f'))
#     cbar = fig.colorbar(surf, ax=ax, format="%.1f")
#     cbar.set_label('\u2206 $j$/$f$, \u00B5C/cm\u00B2', weight='bold')
#     plt.tight_layout()
#     # plt.savefig(str(k)+"3d.png", dpi=1000)
#     plt.show()


path1 = r'C:\Aleksei_Marianov\swv_model\RedoxPySolid\Example_results\CoTPP-cov1'
# path2 = r'C:\Aleksei_Marianov\swv_model\hybrid_swv_model\Example_results\CoTPP-cov10'
# plot_three_d_corrected(path1)
# plot_three_d_corrected(path2)
plot_two_d_corrected(path1, fig_name=None)
# plot_two_d_corrected(path2, fig_name=None)
# plot_three_d_with_dlc(path)
# plot_two_d_with_dlc(path)








