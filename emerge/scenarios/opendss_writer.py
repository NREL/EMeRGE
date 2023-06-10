""" Module for managing export of scenarions in opendss format. """

from typing import List
from pathlib import Path

from emerge.scenarios import data_model


class OpenDSSPVScenarioWriter:
    """Writer class for exporting scenario in opendss format.

    Attributes:
        scenarios (List[data_model.DistPVScenarioModel]): List of pv
            scenarios
        output_path (str): Output path for writing the scenarios.
    """

    def __init__(
        self, scenarios: List[data_model.DistPVScenarioModel], output_path: str
    ):
        """Constructor for `OpenDSSPVScenarioWriter` class.

        Args:
            scenarios (List[data_model.DistPVScenarioModel]): List of pv
                scenarios
            output_path (str): Output path for writing the scenarios.
        """

        self.scenarios = scenarios
        self.output_path = Path(output_path)
        self.output_path.mkdir(exist_ok=True, parents=True)

    def write(self, load_mapper_model: List[data_model.LoadMetadataModel])-> None:
        """Method for writing the scenarios.
        
        Args:
            load_mapper_model (List[data_model.LoadMetadataModel]): List of load 
                metadata model.
        """

        for scenario in self.scenarios:
            scenario_folder = self.output_path / scenario.name
            scenario_folder.mkdir()

            pv_models = []
            pv_models.append(
                f"! PV Scenario for {scenario.pv_penetration} kW total size, Sample {scenario.sample_id} \n"
            )
            pv_models.append(
                f"==============================================PV SCENARIO FILE====================================\n\n"
            )

            for pv in scenario.pvs:
                mapper = next(
                    filter(lambda d: d.name == pv.customer, load_mapper_model)
                )
                pv_models.append(
                    f"new pvsystem.{pv.name.replace('.', '_')} phases={mapper.num_phase} bus1={mapper.bus} kv={mapper.kv} irradiance=1 pmpp={pv.kw} kva={pv.kw} conn=wye %cutin=0.1 %cutout=0.1 vmaxpu=1.2\n"
                )

            pvsystems_path = scenario_folder / "PVSystems.dss"
            with open(pvsystems_path, "w") as f:
                f.writelines(pv_models)
