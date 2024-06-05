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

    def __init__(self, scenarios: List[data_model.DistDERScenarioModel], output_path: str):
        """Constructor for `OpenDSSPVScenarioWriter` class.

        Args:
            scenarios (List[data_model.DistPVScenarioModel]): List of pv
                scenarios
            output_path (str): Output path for writing the scenarios.
        """

        self.scenarios = scenarios
        self.output_path = Path(output_path)
        self.output_path.mkdir(exist_ok=True, parents=True)

    def write(self, load_mapper_model: List[data_model.LoadMetadataModel], file_name: str) -> None:
        """Method for writing the scenarios.

        Args:
            load_mapper_model (List[data_model.LoadMetadataModel]): List of load
                metadata model.
            file_name (str): OpenDSS file name: e.g new_pvs.dss
        """
        for scenario in self.scenarios:
            scenario_folder = self.output_path / scenario.name

            if not scenario_folder.exists():
                scenario_folder.mkdir(parents=True, exist_ok=True)

            der_models = []
            der_models.append(
                f"! DER Scenario for {scenario.penetration} kW total size, Sample {scenario.sample_id} \n"
            )
            der_models.append(
                "==============================================DER SCENARIO FILE====================================\n\n"
            )

            for der in scenario.ders:
                mapper = next(filter(lambda d: d.name == der.customer.name, load_mapper_model))

                if der.der_type == data_model.DERType.solar:
                    der_models.append(
                        f"new pvsystem.{der.name.replace('.', '_')} phases={mapper.num_phase}"
                        f" bus1={mapper.bus} kv={mapper.kv} irradiance=1 pmpp={der.kw} kva={der.kw}"
                        f" conn=wye %cutin=0.1 %cutout=0.1 vmaxpu=1.2 yearly={der.profile}\n"
                    )
                elif der.der_type == data_model.DERType.load:
                    if der.kw != 0:
                        der_models.append(
                            f"new load.{der.name.replace('.', '_')} phases={mapper.num_phase}"
                            f" bus1={mapper.bus} kv={mapper.kv} kvar={0} kva={der.kw}"
                            f" yearly={der.profile}\n"
                        )
                else:
                    raise NotImplementedError(f"{der.der_type} has not been implementes.")

            der_path = scenario_folder / file_name
            with open(der_path, "w", encoding="utf-8") as file:
                file.writelines(der_models)
