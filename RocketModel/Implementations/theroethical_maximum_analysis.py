from FluidProperties.ideal_properties import AirPropertiesIdeal, WaterPropertiesIdeal
from RocketModel.abstract_classes import AbstractRocketStatus, AbstractRocketGeometry
import matplotlib.pyplot as plt
import scipy.optimize as opt
import numpy as np


class RocketGeometryTrial(AbstractRocketGeometry):

    def get_free_surface_h(self, fill_perc):
        pass


class RocketStatusTrial(AbstractRocketStatus):

    def calculate_external_forces(self):
        pass

    def get_dt(self):
        pass

    def calculate_m_dot(self):
        pass

    def get_report_dict(self) -> dict:
        return {}

    @property
    def liquid_properties_class(self):

        return WaterPropertiesIdeal

    @property
    def gas_properties_class(self):

        return AirPropertiesIdeal


def calculate_w_exp(P_value, T_value, fill_value):

    rs = RocketStatusTrial(P_0=P_value, T_0=T_value, fill_start=fill_value, geometry=RocketGeometryTrial())
    return rs.w_exp


def calculate_opt_fill(P_value, T_value, best_fill=0.3):

    return float(opt.minimize(

        lambda fill_value: -calculate_w_exp(P_value, T_value, float(fill_value)),
        np.array(best_fill),
        bounds=[(0, 1)],
        tol=10 ** -10

    ).x)


# noinspection PyUnresolvedReferences
def print_fill_list(max_P, min_P, n_points=10):

    T_in = 25
    P_in_list = np.logspace(0.0, 2.0, num=n_points) / 100 * (max_P - min_P) + min_P
    fill_list = np.array(range(0, 100)) / 100

    best_fill_list = list()
    w_exp_list = list()

    for P_in in P_in_list:

        z_max_list = list()
        fill_start_list = list()

        best_fill = 0.
        best_z = 0.

        for fill in fill_list:

            w_exp = calculate_w_exp(P_in, T_in, fill)

            if not w_exp == 0:

                fill_start_list.append(fill)
                z_max_list.append(w_exp)

                if best_z < w_exp:
                    best_z = w_exp
                    best_fill = fill

        plt.plot(fill_start_list, z_max_list, label="P = {} [bar]".format(round(P_in * 10 - 1, 2)))

        opt_fill = calculate_opt_fill(P_in, T_in, best_fill)
        best_fill_list.append(opt_fill)
        w_exp_list.append(calculate_w_exp(P_in, T_in, opt_fill))

    plt.plot(best_fill_list, w_exp_list, label="optimal")

    plt.xlabel("Fill [%]")
    plt.ylabel("Expansion Work [J]")

    plt.yscale("log")
    plt.legend()
    plt.show()


# noinspection PyUnresolvedReferences
def print_w_exp_and_fill(max_P, min_P, n_points=100):

    T_in = 25
    P_in_list = np.logspace(0.0, 2.0, num=n_points) / 100 * (max_P - min_P) + min_P

    best_fill_list = list()
    w_exp_list = list()

    for P_in in P_in_list:

        opt_fill = calculate_opt_fill(P_in, T_in, 0.6)
        best_fill_list.append(opt_fill)
        w_exp_list.append(calculate_w_exp(P_in, T_in, opt_fill))

    plt.plot(P_in_list * 10 / 1.01325, np.array(w_exp_list))

    plt.xlabel("P / P amb [-]")
    plt.xscale("log")

    plt.ylabel("Max Expansion Work [J]")
    plt.yscale("log")
    plt.show()

    plt.plot(P_in_list * 10 / 1.01325, best_fill_list)
    plt.xlabel("P / P amb [-]")
    plt.ylabel("Best Fill [%]")
    plt.xscale("log")
    plt.show()


if __name__ == "__main__":

    P_amb = 0.101325
    print_fill_list(100 * P_amb, P_amb, n_points=10)
    print_w_exp_and_fill(100 * P_amb, P_amb, n_points=100)