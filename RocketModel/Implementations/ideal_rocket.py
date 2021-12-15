from FluidProperties.ideal_properties import WaterPropertiesIdeal, AirPropertiesIdeal
from RocketModel.abstract_classes import AbstractRocketStatus, AbstractRocketGeometry


class IdealRocketGeometry(AbstractRocketGeometry):

    def get_free_surface_h(self, fill_perc):

        return self.V_bottle / self.A_max * fill_perc


class IdealRocket(AbstractRocketStatus):

    def __init__(self, P_0, T_0, fill_start):

        geometry = IdealRocketGeometry()
        super().__init__(geometry, P_0, T_0, fill_start)

    def calculate_external_forces(self):
        return 0.

    def get_dt(self):

        if not self.out_of_liquid:

            return 0.000001

        if not self.out_of_gas:

            return 0.000001

        else:

            return 0.01

    def evaluate_pressure_losses_beta(self):

        return 0.

    @property
    def liquid_properties_class(self):
        return WaterPropertiesIdeal

    @property
    def gas_properties_class(self):
        return AirPropertiesIdeal


if __name__ == "__main__":

    ir = IdealRocket(P_0=1, T_0=25, fill_start=0.3)
    ir.calculate()
    ir.print_over_time()
    ir.print_over_time(dynamic_element="v")
    ir.print_over_time(dynamic_element="a")
    ir.print_over_time("pressure")
    ir.print_over_time("m_dot")