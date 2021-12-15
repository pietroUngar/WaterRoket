from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
import scipy.constants as cst
import numpy as np


class AbstractRocketGeometry(ABC):

    def __init__(self):

        self.Cd = 0.5

        self.d_max = 0.08
        self.d_nozzle = 0.025
        self.A_max = np.pi * np.power(self.d_max / 2, 2)
        self.A_nozzle = np.pi * np.power(self.d_nozzle / 2, 2)

        self.m_bottle = 0.05
        self.V_bottle = 1.5

    @property
    def V_bottle(self):
        # convert l -> m^3
        return self.__V_bottle * 0.001

    @V_bottle.setter
    def V_bottle(self, volume):
        self.__V_bottle = volume

    @abstractmethod
    def get_free_surface_h(self, fill_perc):
        pass


class AbstractRocketStatus(ABC):

    def __init__(self, geometry:AbstractRocketGeometry, P_0, T_0, fill_start):

        self.geom = geometry

        self.P_in = P_0
        self.T_in = T_0
        self.P_amb = 0.101325

        self.__init_fluids(fill_start)
        self.__init_other_parameters()
        self.__calc_theoretical_h_max()
        self.__append_report_row()

    def __calc_theoretical_h_max(self):

        P_amb = 0.101325  # [Mpa]

        P_start = self.gas.get_variable("P")
        v_start = self.gas.vol

        try:

            gamma = self.gas.get_variable("gamma")

        except:

            gamma = 1.4

        fill_om = 1/np.power(gamma, 1/(gamma - 1))
        overall_max = abs(self.geom.V_bottle * P_start * (np.power(fill_om, gamma) - fill_om) / (1 - gamma)) * 10 ** 6

        v_end = np.min([self.geom.V_bottle, v_start * np.power(P_start / P_amb, 1 / gamma)])
        P_end = P_start * np.power(v_start / v_end, gamma)

        self.w_exp = abs((P_start * v_start - P_end * v_end) / (1 - gamma)) * 10 ** 6  # [MJ] -> [J]
        self.eta_exp = self.w_exp / overall_max

        if v_end == self.geom.V_bottle:

            self.max_z_theory = self.w_exp / (self.geom.m_bottle * cst.g)

        else:

            d_v = abs(v_end - self.geom.V_bottle)
            d_m = d_v * self.liquid.get_variable("rho")
            self.max_z_theory = self.w_exp / ((self.geom.m_bottle + d_m) * cst.g)

    def __init_fluids(self, fill_start):

        self.__fill_perc = fill_start
        liquid_volume = self.geom.V_bottle * fill_start
        gas_volume = self.geom.V_bottle * (1 - fill_start)

        self.liquid = self.liquid_properties_class(liquid_volume, self.P_in, self.T_in)
        self.gas = self.gas_properties_class(gas_volume, self.P_in, self.T_in)

    def __init_other_parameters(self):

        self.__time = 0.
        self.__calculate_m_dot()
        self.__dynamics_report = list()
        self.__dynamics = {

            "a": 0.,
            "v": 0.,
            "z": 0.

        }

    def calculate(self):

        while not self.has_landed:

            dt = self.get_dt()
            self.step(dt)

    def step(self, dt):

        self.__calculate_m_dot()
        self.__update_dynamics(dt)
        self.__update_pressures(dt)
        self.__append_report_row()

    def __calculate_m_dot(self):

        try:

            if not self.out_of_liquid:

                rho = self.liquid.get_variable("rho")

                DP_gas = (self.gas.get_variable("P") - self.P_amb) * 10 ** 6  # [MPa] -> [Pa]
                DP_acc = rho * (cst.g + self.__dynamics["a"]) * self.geom.get_free_surface_h(self.__fill_perc)
                DP_overall = DP_gas + DP_acc

            elif not self.out_of_gas:

                rho = self.gas.get_variable("rho")

                DP_gas = (self.gas.get_variable("P") - self.P_amb) * 10 ** 6  # [MPa] -> [Pa]
                DP_overall = DP_gas

            else:

                self.__m_dot = 0.
                return

            beta = self.evaluate_pressure_losses_beta()
            self.__m_dot = self.geom.A_nozzle * np.power(2 * rho * (1 + beta) * DP_overall, 1 / 2)

        except:

            self.__m_dot = 0.

    def __update_dynamics(self, dt):

        self.__time += dt
        v_0 = self.__dynamics["v"]

        self.__dynamics["a"] = self.__calculate_forces() / self.m_tot
        self.__dynamics["v"] += self.__dynamics["a"] * dt
        self.__dynamics["z"] += 1/2 * self.__dynamics["a"] * np.power(dt, 2) + v_0 * dt

    def __update_pressures(self, dt):

        m_out = self.__m_dot * dt

        if not self.out_of_liquid:

            self.liquid.vol -= m_out / self.liquid.get_variable("rho")
            self.gas.vol = self.geom.V_bottle - self.liquid.vol

        elif not self.out_of_gas:

            self.gas.mass -= m_out

        self.__fill_perc = self.liquid.vol / self.geom.V_bottle

    def __append_report_row(self):

        self.__dynamics_report.append({

            "time": self.__time,
            "m_dot": self.__m_dot,
            "level": self.__fill_perc,
            "pressure": self.gas.get_variable("P"),
            "dynamics": {

                "a": self.__dynamics["a"],
                "v": self.__dynamics["v"],
                "z": self.__dynamics["z"]

            }

        })
        self.__dynamics_report[-1].update(self.other_report_dict())

    def __calculate_forces(self):

        if not self.out_of_liquid:

            rho = self.liquid.get_variable("rho")

        else:

            rho = self.gas.get_variable("rho")

        v_exit = self.__m_dot / (self.geom.A_nozzle * rho) - self.__dynamics["v"]
        nozzle_force = v_exit * self.__m_dot
        gravity = self.m_tot * cst.g

        return nozzle_force - gravity + self.calculate_external_forces()

    def print_over_time(self, element_name="dynamics", dynamic_element="z"):

        t_list = list()
        y_list = list()

        for element in self.__dynamics_report:

            t_list.append(element["time"])

            if element_name == "dynamics":

                y_list.append(element[element_name][dynamic_element])

            else:

                y_list.append(element[element_name])

        plt.plot(t_list, y_list, label="optimal")

        plt.xlabel(self.__return_label("time"))
        plt.ylabel(self.__return_label(element_name, dynamic_element))
        plt.show()

    def __return_label(self, element_name, dynamic_element="z"):

        if element_name == "dynamics":

            if dynamic_element == "z":

                return "position [m]"

            elif dynamic_element == "v":

                return "velocity [m/s]"

            else:

                return "acceleration [m/s^2]"

        elif element_name == "time":

            return "time [s]"

        elif element_name == "m_dot":

            return "flow rate [kg/s]"

        elif element_name == "level":

            return "water level [%]"

        elif element_name == "pressure":

            return "internal pressure [MPa]"

        else:

            return element_name

    def evaluate_pressure_losses_beta(self):

        return 0.

    @abstractmethod
    def calculate_external_forces(self):
        pass

    @abstractmethod
    def get_dt(self):
        pass

    def other_report_dict(self) -> dict:
        return {}

    @property
    @abstractmethod
    def liquid_properties_class(self):

        pass

    @property
    @abstractmethod
    def gas_properties_class(self):

        pass

    @property
    def m_tot(self):

        mass = self.geom.m_bottle
        for fluid in [self.liquid, self.gas]:
            mass += fluid.mass

        return mass

    @property
    def has_landed(self):

        if self.__time == 0:

            return False

        else:

            return self.__dynamics["z"] <= 0.

    @property
    def out_of_liquid(self):

        if self.out_of_gas or self.liquid.vol <= 0:

            return True

        else:

            rho = self.liquid.get_variable("rho")
            DP_gas = (self.gas.get_variable("P") - self.P_amb)
            DP_acc = rho * (cst.g + self.__dynamics["a"]) * self.geom.get_free_surface_h(self.__fill_perc) / 10 ** 6

            return DP_gas + DP_acc <= 0

    @property
    def out_of_gas(self):

        return self.gas.get_variable("P") <= self.P_amb or self.gas.mass == 0