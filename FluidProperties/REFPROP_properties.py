from REFPROPConnector import RefPropHandler, AbstractThermodynamicPoint
from FluidProperties.abstract_class import AbstractFluidProperties
from abc import ABC, abstractmethod


class ThermodynamicPoint(AbstractThermodynamicPoint):

    def __init__(self, refprop: RefPropHandler):
        super().__init__(refprop)

    def other_calculation(self):
        pass


class REFPROPProperties(AbstractFluidProperties, ABC):

    def __init__(self, initial_volume, P_0, T_0):

        super().__init__(initial_volume, P_0, T_0)

        thermo_class = self.thermo_point_class
        self.thermo_point = thermo_class(self.thermo_input)
        self.init_properties()

    def set_variable(self, variable_name: str, variable_value: float):

        self.thermo_point.set_variable(variable_name, variable_value)

    def get_variable(self, variable_name: str):

        return self.thermo_point.get_variable(variable_name)

    @property
    def mass(self):

        return self.vol * self.get_variable("rho")

    @mass.setter
    def mass(self, new_mass):
        pass

    @property
    def thermo_point_class(self):
        return ThermodynamicPoint

    @property
    @abstractmethod
    def thermo_input(self):
        pass

    @abstractmethod
    def init_properties(self):
        pass


class AirProperties(REFPROPProperties):

    def __init__(self, initial_volume, P_0, T_0):

        super().__init__(initial_volume, P_0, T_0)

        self.name = "Air"
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

    @property
    def thermo_input(self):
        return RefPropHandler(["Nitrogen", "Oxygen", "Argon"], [0.78, 0.21, 0.1])

    def init_properties(self):

        self.thermo_point.set_variable("P", self.P_0)
        self.thermo_point.set_variable("T", self.T_0)

    def on_vol_update(self, d_vol):

        new_h = self.get_variable("h") + self.calculate_dh(d_vol)
        new_rho = self.mass / self.vol

        self.set_variable("h", new_h)
        self.set_variable("rho", new_rho)

    def on_mass_update(self):

        new_rho = self.mass / self.vol
        self.set_variable("rho", new_rho)

    def calculate_dh(self, d_vol):

        return - self.get_variable("P") * d_vol / self.mass * 10 ** 3


class WaterProperties(REFPROPProperties):

    def __init__(self, initial_volume, P_0, T_0):

        super().__init__(initial_volume,P_0, T_0)

        self.name = "Water"

    @property
    def thermo_input(self):
        return RefPropHandler(["Water"], [1])

    def init_properties(self):

        self.thermo_point.set_variable("P", self.P_0)
        self.thermo_point.set_variable("T", self.T_0)

    def on_vol_update(self, d_vol):
        pass


if __name__ == '__main__':

    tp = AirProperties(initial_volume=1, P_0=1, T_0=25)
    print(tp.mass)

    tp = WaterProperties(initial_volume=1, P_0=1, T_0=25)
    print(tp.mass)