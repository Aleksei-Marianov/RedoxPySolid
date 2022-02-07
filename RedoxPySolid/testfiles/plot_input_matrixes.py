import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.stats import norm, cauchy
import os
from matplotlib.ticker import FormatStrFormatter


def plot_input_matrixes_bar(path, fig_name=None):
    font = {'family': 'serif', 'serif': 'Arial', 'weight': 'bold', 'size': 11}
    plt.rc('font', **font)
    fig = plt.figure(figsize=(6, 5))
    ax1 = fig.add_subplot(projection='3d', azim=30, elev=25)
    colors = ['pink', 'yellow']
    width = 0.0072
    depth = 0.054
    contents = [os.path.join(path, item) for item in os.listdir(path) if item.startswith('kinetic_params')]
    bottom = []
    for i, folder in enumerate(contents):
        print(os.listdir(folder))
        files = [os.path.join(folder, f) for f in os.listdir(folder)]
        print(files)
        x, y, z = [np.transpose(np.loadtxt(f)) for f in files]
        potentials, ks, gs = x.ravel(), y.ravel(), z.ravel()
        for j, (g_s, e) in enumerate(zip(gs, potentials)):
            if g_s < 10 ** (-14) or e < -0.3 or e > 0.2:
                potentials[j] = 0
                ks[j] = 0
                gs[j] = 0
        potentials, ks, gs = potentials[potentials != 0], ks[ks != 0], gs[gs != 0]
        if i == 0:
            bottom = np.zeros_like(gs)
        else:
            bottom = gs
        print(len(bottom))

        ax1.bar3d(potentials, np.log10(ks), bottom, width, depth, 10 ** 12 * gs, color=colors[i], shade=True, edgecolor='black',
                  linewidth=0.1, alpha=0.6)

    ax1.grid(False)
    ax1.set_xlabel('E, V vs NHE', weight='bold')
    ax1.set_ylabel('log[k$^0$, s$^{-1}$]', weight='bold')
    ax1.set_zlabel('$\u0393$$_{EA}$, pmol/cm$^{-2}$', weight='bold')
    ax1.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    ax1.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    ax1.zaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    ax1.xaxis.pane.set_facecolor('lavender')
    ax1.yaxis.pane.set_facecolor('lavender')
    ax1.zaxis.pane.set_facecolor('lavender')
    ax1.xaxis.pane.set_edgecolor('black')
    ax1.yaxis.pane.set_edgecolor('black')
    ax1.zaxis.pane.set_edgecolor('black')
    ax1.set_xlim([-0.3, 0.2])
    plt.subplots_adjust(0, 0, 1, 1)
    if fig_name is not None:
        plt.savefig(str(fig_name) + '.png', dpi=1200)
        plt.show()
    else:
        plt.show()


plot_input_matrixes_bar(r'C:\Aleksei_Marianov\swv_model\hybrid_swv_model\2021-07-26 20_24_46.891178', fig_name=None)


# plot_input_matrixes_2d(r'C:\Aleksei_Marianov\swv_model\hybrid_swv_model\CoTPP_MWCNT')
# plot_input_matrixes_3d(r'C:\Aleksei_Marianov\swv_model\hybrid_swv_model\CoTPP_MWCNT')
# plot_input_matrixes_bar(r'C:\Aleksei_Marianov\swv_model\hybrid_swv_model\CoTPP_MWCNT', fig_name="CoTPP_MWCNT_bar_plot")