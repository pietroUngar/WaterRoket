from abc import ABC, abstractmethod


class AbstractFluidProperties(ABC):

    def __init__(self, initial_volume, P_0, T_0):

        self.name = ""

        self.__vol = initial_volume
        self.V_0 = initial_volume
        self.P_0 = P_0
        self.T_0 = T_0

    @abstractmethod
    def get_variable(self, variable_name: str):

        pass

    @abstractmethod
    def on_vol_update(self, d_vol):

        pass

    @property
    def vol(self):

        return self.__vol

    @vol.setter
    def vol(self, new_vol):

        old_vol = self.__vol

        if new_vol < 0:

            self.__vol = 0

        else:

            self.__vol = new_vol

        if type(old_vol) is float:

            d_vol = self.__vol - old_vol

            if not d_vol == 0:

                self.on_vol_update(d_vol)

    @property
    @abstractmethod
    def mass(self):
        pass

    @mass.setter
    @abstractmethod
    def mass(self, new_mass):
        pass