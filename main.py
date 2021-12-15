from FluidProperties.REFPROP_properties import WaterProperties, AirProperties
from FluidProperties.ideal_properties import WaterPropertiesIdeal, AirPropertiesIdeal
import matplotlib.pyplot as plt
import numpy as np


class BottleGeometry:

    def __init__(self):

        self.Cd = 0.5

        self.d_max = 0.08
        self.d_nozzle = 0.025
        self.A_max = np.pi*np.power(self.d_max/2, 2)
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


class RocketStatus:

    def __init__(self, P_0, fill_start):

        self.geom = BottleGeometry()
        self.P_in = P_0

        liquid_volume = self.geom.V_bottle * fill_start
        gas_volume = self.geom.V_bottle * (1 - fill_start)

        self.liquid = self.liquid_properties_class(liquid_volume, P_0, 25)
        self.gas = self.gas_properties_class(gas_volume, P_0, 25)

    def step(self, dt, m_dot):

        m_out = m_dot * dt

        self.liquid.vol -= m_out / self.liquid.get_variable("rho")
        self.gas.vol = self.geom.V_bottle - self.liquid.vol

    @property
    def liquid_properties_class(self):

        return WaterProperties

    @property
    def gas_properties_class(self):

        return AirProperties

    @property
    def m_tot(self):

        mass = self.geom.m_bottle
        for fluid in [self.liquid, self.gas]:

            mass += fluid.mass

        return mass


class RocketStatusIdeal:

    def __init__(self, P_0, fill_start):

        self.geom = BottleGeometry()
        self.P_in = P_0

        liquid_volume = self.geom.V_bottle * fill_start
        gas_volume = self.geom.V_bottle * (1 - fill_start)

        self.liquid = self.liquid_properties_class(liquid_volume, P_0, 25)
        self.gas = self.gas_properties_class(gas_volume, P_0, 25)

    def step(self, dt, m_dot):

        m_out = m_dot * dt

        self.liquid.vol -= m_out / self.liquid.get_variable("rho")
        self.gas.vol = self.geom.V_bottle - self.liquid.vol

    @property
    def liquid_properties_class(self):

        return WaterPropertiesIdeal

    @property
    def gas_properties_class(self):

        return AirPropertiesIdeal

    @property
    def m_tot(self):

        mass = self.geom.m_bottle
        for fluid in [self.liquid, self.gas]:

            mass += fluid.mass

        return mass


if __name__ == '__main__':

    P_0 = 1
    rs = RocketStatus(P_0, 0.3)
    rs_ideal = RocketStatusIdeal(P_0, 0.3)

    v_0 = rs.gas.vol

    P_list = [P_0]
    P_ideal = [P_0]
    vol_list = [v_0]

    for i in range(10000):

        rs.step(0.05, 1)
        rs_ideal.step(0.05, 1)

        vol_list.append(rs.gas.vol)
        P_ideal.append(rs_ideal.gas.get_variable("P"))
        P_list.append(rs.gas.get_variable("P"))

    plt.plot(vol_list, P_list, label="refprop")
    plt.plot(vol_list, P_ideal, label="ideal gas")
    plt.legend()
    plt.show()