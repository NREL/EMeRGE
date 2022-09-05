""" Module for testing sceanrios."""
from pathlib import Path
import shutil

from emerge.scenarios import pv_scenario
from emerge.scenarios import data_model
from emerge.scenarios import strategy
from emerge.scenarios import opendss_writer


def test_distributed_pv_scenarios():
    """Test function for generating distributed pv scenarions."""

    list_of_customers = [
        data_model.CustomerModel(name="customer1", kw=10.0, distance=1),
        data_model.CustomerModel(name="customer2", kw=5.0, distance=5),
        data_model.CustomerModel(name="customer3", kw=3.4, distance=2),
        data_model.CustomerModel(name="customer4", kw=7.7, distance=20),
        data_model.CustomerModel(name="customer5", kw=9.8, distance=12),
    ]

    config = data_model.PVScenarioConfig(
        pct_resolution=10, num_of_penetration=3, max_num_of_samples=2
    )
    strategy_ = strategy.FarSelectionStrategy()
    scenario_instance = pv_scenario.DistributedPVScenario(
        list_of_customers, config
    )
    scenarios = scenario_instance.create_pv_scenarios_for_feeder(strategy_)
    for scenario in scenarios:
        assert scenario.pvs[0].customer == "customer4"


def test_export_of_opendss_scenarios():
    """Test function for exporting scenarios in opendss format."""

    pvscenarios = [
        data_model.DistPVScenarioModel(
            name="scenario_0_3.59_1",
            sample_id=0,
            pv_penetration=10.0,
            pvs=[
                data_model.PVModel(
                    name="customer_4_pv", kw=3.59, customer="customer_4"
                )
            ],
        ),
        data_model.DistPVScenarioModel(
            name="scenario_0_7.18_2",
            sample_id=0,
            pv_penetration=20.0,
            pvs=[
                data_model.PVModel(
                    name="customer_4_pv", kw=3.59, customer="customer_4"
                ),
                data_model.PVModel(
                    name="customer_5_pv", kw=3.59, customer="customer_5"
                ),
            ],
        ),
    ]

    mapper_object = [
        data_model.LoadMetadataModel(
            name="customer_4", bus="bus1.2.0", num_phase=1, kv=0.415
        ),
        data_model.LoadMetadataModel(
            name="customer_5", bus="bus2.1.2.3", num_phase=3, kv=0.415
        ),
    ]

    output_path = Path("./output")
    output_path.mkdir(exist_ok=True)
    writer_object = opendss_writer.OpenDSSPVScenarioWriter(
        pvscenarios, output_path
    )
    writer_object.write(mapper_object)
    shutil.rmtree(output_path)
