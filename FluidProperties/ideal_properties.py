from FluidProperties.abstract_class import AbstractFluidProperties
from abc import ABC, abstractmethod
import numpy as np


class IdealProperties(AbstractFluidProperties, ABC):

    def __init__(self, initial_volume, P_0, T_0):

        super().__init__(initial_volume, P_0, T_0)

        self.P_0 *= 1000    # MPa -> kPa
        self.T_0 += 273.15  # °C -> K

        self.__P = self.P_0
        self.__T = self.T_0

        self.__mass = self.vol * self.get_variable("rho")

    @property
    def mass(self):

        return self.__mass

    @mass.setter
    def mass(self, new_mass):

        old_mass = self.__mass

        if new_mass < 0:

            self.__mass = 0

        else:

            self.__mass = new_mass

        if type(old_mass) is float:

            d_mass = self.__mass - old_mass

            if not d_mass == 0:

                self.on_mass_update()

    def get_variable(self, variable_name: str):

        if variable_name == "rho":

            return self.rho

        elif variable_name == "P":

            return self.__P / 10 ** 3  # kPa -> MPa

        elif variable_name == "T":

            return self.__T - 273.15  # K -> °C

        else:

            try:

                return self.properties[variable_name]

            except:

                return None

    def set_variable(self, variable_name: str, value):

        if variable_name == "rho":

            pass

        elif variable_name == "P":

            self.__P = value * 10 ** 3  # MPa -> kPa

        elif variable_name == "T":

            self.__T = value + 273.15  # °C -> K

    @abstractmethod
    def on_mass_update(self):

        pass

    @property
    @abstractmethod
    def rho(self):

        pass

    @property
    @abstractmethod
    def properties(self):

        return {

            "gamma": 1.4,
            "R": 0.287

        }


class AirPropertiesIdeal(IdealProperties):

    def __init__(self, initial_volume, P_0, T_0):

        super().__init__(initial_volume, P_0, T_0)

        self.name = "Air"

    def on_vol_update(self, d_vol):

        gamma = self.properties["gamma"]
        self.set_variable("P", self.P_0 * np.power(self.vol / self.V_0, - gamma) / 10 ** 3)
        self.set_variable("T", self.T_0 * np.power(self.vol / self.V_0, 1 - gamma) - 273.15)

    def on_mass_update(self):

        rho = self.mass / self.vol
        R = self.properties["R"]
        T = self.get_variable("T") + 273.15

        self.set_variable("P", rho * R * T / 10 ** 3)

    @property
    def rho(self):

        P = self.get_variable("P") * 1000
        T = self.get_variable("T") + 273.15
        return P / (self.properties["R"] * T)

    @property
    def properties(self):

        return {

            "gamma": 1.4,
            "R": 0.287

        }


class WaterPropertiesIdeal(IdealProperties):

    def __init__(self, initial_volume, P_0, T_0):
        super().__init__(initial_volume, P_0, T_0)

        self.name = "Water"
        self.__mass = self.vol * self.get_variable("rho")

    def on_vol_update(self, d_vol):
        pass

    def on_mass_update(self):

        self.vol = self.mass / self.rho

    @property
    def rho(self):
        return self.properties["rho"]

    @property
    def properties(self):

        return {

            "rho": 997

        }


if __name__ == "__main__":

    ip = AirPropertiesIdeal(initial_volume=1, P_0=0.1, T_0=25)
    print(ip.get_variable("rho"))