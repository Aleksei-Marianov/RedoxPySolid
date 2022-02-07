from hybrid_swv_model import input_parameters
from hybrid_swv_model import matrixes_of_kinetic_params
from hybrid_swv_model.start_computation import start_computation
from hybrid_swv_model import plot_data
from hybrid_swv_model.store_results import move_files
import numpy as np

# CoTPP/CC

# params = [{'type': 'lorentz',
#           'g_new': 0.130*10**(-9)+6*0.006*10**(-9),
#            'e0_new': -0.949,
#            'sigma_e_new': 0.15,
#            'k_new': 140,
#            'sigma_log_k_new': 0.03,
#            'a': 0.5},
#           {'type': 'lorentz',
#           'g_new': 0.20*10**(-9)+6*0.006*10**(-9),
#            'e0_new': -0.949,
#            'sigma_e_new': 0.08,
#            'k_new': 130,
#            'sigma_log_k_new': 0.04,
#            'a': 0.5},
#             {'type': 'lorentz',
#           'g_new': 0.097*10**(-9)+6*0.003*10**(-9),
#            'e0_new': -0.949,
#            'sigma_e_new': 0.07,
#            'k_new': 120,
#            'sigma_log_k_new': 0.04,
#              'a': 0.5},
#           {'type': 'lorentz',
#           'g_new': 0.025*10**(-9),
#            'e0_new': -0.949,
#            'sigma_e_new': 0.07,
#            'k_new': 95,
#            'sigma_log_k_new': 0.1,
#            'a': 0.5},
#           {'type': 'lorentz',
#           'g_new': 0.020*10**(-9),
#            'e0_new': -0.949,
#            'sigma_e_new': 0.07,
#            'k_new': 70,
#            'sigma_log_k_new': 0.1,
#            'a': 0.5},
#           {'type': 'lorentz',
#           'g_new': 0.26*10**(-9),
#            'e0_new': -0.949,
#            'sigma_e_new': 0.12,
#            'k_new': 50,
#            'sigma_log_k_new': 0.5,
#            'a': 0.5},
#             {'type': 'lorentz',
#           'g_new': 0.30*10**(-9),
#            'e0_new': -0.935,
#            'sigma_e_new': 0.12,
#            'k_new': 1,
#            'sigma_log_k_new': 0.7,
#              'a': 0.5},
#             {'type': 'lorentz',
#           'g_new': 0.20*10**(-9),
#            'e0_new': -0.830,
#            'sigma_e_new': 0.12,
#            'k_new': 1,
#            'sigma_log_k_new': 0.7,
#              'a': 0.5},
#             {'type': 'lorentz',
#           'g_new': 0.10*10**(-9),
#            'e0_new': -0.78,
#            'sigma_e_new': 0.12,
#            'k_new': 1,
#            'sigma_log_k_new': 0.7,
#              'a': 0.5},
#             {'type': 'lorentz',
#           'g_new': 0.1*10**(-9),
#            'e0_new': -0.64,
#            'sigma_e_new': 0.12,
#            'k_new': 1,
#            'sigma_log_k_new': 0.7,
#              'a': 0.5}
#           ]
#
# input_parameters.generate_swv_input_params(-0.5, -1.1, -0.01, 0.025, 0, 3, 12.8, 92*10**(-6))
# matrixes_of_kinetic_params.return_distribution(40, 40, True, [-1.5, -0.4], [1, 300], params, show_fig=False, fig_name=None)
# start_computation()
# move_files()
#

# CoTPP on MWCNTs
# params = [{'type': 'lorentz',
#           'g_new': 1.4*10**(-9),
#            'e0_new': -0.925,
#            'sigma_e_new': 0.025,
#            'k_new': 2.5,
#            'sigma_log_k_new': 0.05,
#            'a': 0.5},
#           {'type': 'lorentz',
#           'g_new': 1.4*10**(-9),
#            'e0_new': -0.945,
#            'sigma_e_new': 0.025,
#            'k_new': 3,
#            'sigma_log_k_new': 0.05,
#            'a': 0.5},
# {'type': 'lorentz',
#           'g_new': 4*10**(-9),
#            'e0_new': -0.95,
#            'sigma_e_new': 0.05,
#            'k_new': 0.4,
#            'sigma_log_k_new': 0.7,
#            'a': 0.5},
#           {'type': 'lorentz',
#           'g_new': 4*10**(-9),
#            'e0_new': -0.95,
#            'sigma_e_new': 0.05,
#            'k_new': 0.05,
#            'sigma_log_k_new': 0.7,
#            'a': 0.5},
#           {'type': 'lorentz',
#           'g_new': 0.9*10**(-9),
#            'e0_new': -0.95,
#            'sigma_e_new': 0.03,
#            'k_new': 35,
#            'sigma_log_k_new': 0.08,
#            'a': 0.5},
#
#             {'type': 'lorentz',
#              'g_new': 0.8*10**(-9),
#               'e0_new': -0.70,
#               'sigma_e_new': 0.01,
#               'k_new': 2,
#               'sigma_log_k_new': 0.15,
#               'a': 0.5},
#           ]
#
# input_parameters.generate_swv_input_params(-0.5, -1.1, -0.01, 0.025, -0.40, 3, 13.8, 10.76*10**(-3))
# matrixes_of_kinetic_params.return_distribution(50, 50, True, [-1.15, -0.65], [0.05, 50], params, show_fig=False, fig_name=None)
# start_computation()
# move_files()


# CoTPP-noncov positive_couple

# params = [{'type': 'normal',
#           'g_new': 0.11*10**(-9),
#            'e0_new': 0.12,
#            'sigma_e_new': 0.07,
#            'k_new': 0.05,
#            'sigma_log_k_new': 0.1,
#            'a': 0.1},
#             {'type': 'normal',
#           'g_new': 0.1*10**(-9),
#            'e0_new': -0.4,
#            'sigma_e_new': 0.18,
#            'k_new': 150,
#            'sigma_log_k_new': 0.12,
#             'a': 0.5},
#           ]
#
# input_parameters.generate_swv_input_params(0.5, -0.5, -0.01, 0.025, 0, 3, 12.8, 78*10**(-6))
# matrixes_of_kinetic_params.return_distribution(50, 50, True, [-0.4, 0.3], [0.05, 300], params, show_fig=False, fig_name=None)
# start_computation()
# move_files()

# CoTPP-cov1 positive couple

# params = [
#           {'type': 'normal',
#           'g_new': 1.3*10**(-9),
#            'e0_new': 0.05,
#            'sigma_e_new': 0.1,
#            'k_new': 0.05,
#            'sigma_log_k_new': 0.2,
#            'a': 0.1},
#     {'type': 'lorentz',
#           'g_new': 0.1038*10**(-9),
#            'e0_new': -0.12,
#            'sigma_e_new': 0.07,
#            'k_new': 180,
#            'sigma_log_k_new': 0.1,
#            'a': 0.5},
#             {'type': 'normal',
#           'g_new': 0.07*10**(-9),
#            'e0_new': -0.5,
#            'sigma_e_new': 0.18,
#            'k_new': 180,
#            'sigma_log_k_new': 0.12,
#             'a': 0.5}]
#
# input_parameters.generate_swv_input_params(0.5, -0.5, -0.01, 0.025, 0, 3, 12.8, 135*10**(-6))
# matrixes_of_kinetic_params.return_distribution(50, 50, True, [-0.4, 0.3], [0.05, 300], params, show_fig=False, fig_name=None)
# start_computation()
# move_files()

# CoTPP-cov5 positive couple

# params = [
#           {'type': 'normal',
#           'g_new': 0.60*10**(-9),
#            'e0_new': 0.045,
#            'sigma_e_new': 0.095,
#            'k_new': 0.05,
#            'sigma_log_k_new': 0.2,
#            'a': 0.1},
# {'type': 'normal',
#           'g_new': 0.12*10**(-9),
#            'e0_new': 0.035,
#            'sigma_e_new': 0.09,
#            'k_new': 0.1,
#            'sigma_log_k_new': 0.4,
#            'a': 0.1},
# {'type': 'normal',
#           'g_new': 0.12*10**(-9),
#            'e0_new': 0.020,
#            'sigma_e_new': 0.09,
#            'k_new': 0.5,
#            'sigma_log_k_new': 0.4,
#            'a': 0.1},
# {'type': 'normal',
#           'g_new': 0.11*10**(-9),
#            'e0_new': 0.010,
#            'sigma_e_new': 0.09,
#            'k_new': 2.5,
#            'sigma_log_k_new': 0.4,
#            'a': 0.1},
# {'type': 'normal',
#           'g_new': 0.075*10**(-9),
#            'e0_new': 0.00,
#            'sigma_e_new': 0.09,
#            'k_new': 10,
#            'sigma_log_k_new': 0.4,
#            'a': 0.5},
# {'type': 'normal',
#           'g_new': 0.075*10**(-9),
#            'e0_new': -0.05,
#            'sigma_e_new': 0.09,
#            'k_new': 50,
#            'sigma_log_k_new': 0.4,
#            'a': 0.5},
#     {'type': 'lorentz',
#           'g_new': 0.047*10**(-9),
#            'e0_new': -0.10,
#            'sigma_e_new': 0.05,
#            'k_new': 135,
#            'sigma_log_k_new': 0.1,
#            'a': 0.5},
#             {'type': 'normal',
#           'g_new': 0.14*10**(-9),
#            'e0_new': -0.45,
#            'sigma_e_new': 0.18,
#            'k_new': 170,
#            'sigma_log_k_new': 0.12,
#             'a': 0.5}]
#
# input_parameters.generate_swv_input_params(0.5, -0.5, -0.01, 0.025, 0, 3, 10.2, 155*10**(-6))
# matrixes_of_kinetic_params.return_distribution(50, 50, True, [-0.4, 0.3], [0.05, 300], params, show_fig=False, fig_name=None)
# start_computation()
# move_files()

# CoTPP-cov10 positive couple

params = [
          {'type': 'normal',
          'g_new': 0.85*10**(-9),
           'e0_new': 0.045,
           'sigma_e_new': 0.095,
           'k_new': 0.05,
           'sigma_log_k_new': 0.2,
           'a': 0.1},
            {'type': 'normal',
          'g_new': 0.028*10**(-9),
           'e0_new': 0.035,
           'sigma_e_new': 0.09,
           'k_new': 0.1,
           'sigma_log_k_new': 0.4,
           'a': 0.1},
            {'type': 'normal',
          'g_new': 0.028*10**(-9),
           'e0_new': 0.020,
           'sigma_e_new': 0.09,
           'k_new': 0.5,
           'sigma_log_k_new': 0.4,
           'a': 0.1},
            {'type': 'normal',
          'g_new': 0.028*10**(-9),
           'e0_new': 0.010,
           'sigma_e_new': 0.09,
           'k_new': 2.5,
           'sigma_log_k_new': 0.4,
           'a': 0.1},
          {'type': 'normal',
          'g_new': 0.01*10**(-9),
           'e0_new': -0.03,
           'sigma_e_new': 0.09,
           'k_new': 50,
           'sigma_log_k_new': 0.4,
           'a': 0.5},
          {'type': 'normal',
          'g_new': 0.01*10**(-9),
           'e0_new': -0.08,
           'sigma_e_new': 0.09,
           'k_new': 100,
           'sigma_log_k_new': 0.4,
           'a': 0.5},
          {'type': 'lorentz',
          'g_new': 0.035*10**(-9),
           'e0_new': -0.12,
           'sigma_e_new': 0.04,
           'k_new': 200,
           'sigma_log_k_new': 0.1,
           'a': 0.5},
            {'type': 'normal',
          'g_new': 0.10*10**(-9),
           'e0_new': -0.45,
           'sigma_e_new': 0.18,
           'k_new': 220,
           'sigma_log_k_new': 0.12,
            'a': 0.5}]

input_parameters.generate_swv_input_params(0.5, -0.5, -0.01, 0.025, 0, 3, 9.9, 125*10**(-6))
matrixes_of_kinetic_params.return_distribution(50, 50, (-0.4, 0.3), (0.05, 300), params, show_fig=False, fig_name=None)
start_computation()
move_files()