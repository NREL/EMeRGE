""" This module implements commad line interface for exporting
schemas and handling opt in vscode update."""

from pathlib import Path
from typing import List

import click
from pydantic import BaseModel
import pydantic

from emerge.scenarios import data_model
from emerge.utils import util
from emerge.cli.timeseries_simulation import TimeseriesSimulationInput


class SchemaItemModel(BaseModel):
    name: str
    model: pydantic._internal._model_construction.ModelMetaclass

    class Config:
        arbitrary_types_allowed = True


class SchemaManager:
    def __init__(self, schema_folder: str = ".vscode"):
        self.schema_folder = Path(schema_folder)
        self.schemas: List[SchemaItemModel] = []

    def add_schema(self, name: str, model: BaseModel):
        self.schemas.append(SchemaItemModel(name=name, model=model))

    def generate_and_save_schemas(self):
        if not self.schema_folder.exists():
            self.schema_folder.mkdir()

        for schema in self.schemas:
            json_schema = schema.model.model_json_schema()
            schema_file = self.schema_folder / f"{schema.name}.json"
            util.write_file(json_schema, schema_file)

    def configure_vscode_settings(self):
        vscode_settings_file = self.schema_folder / "settings.json"

        if not vscode_settings_file.exists():
            util.write_file({}, vscode_settings_file)

        settings = util.read_file(vscode_settings_file, use_json5=True)
        vscode_key = "json.schemas"

        if vscode_key not in settings:
            settings[vscode_key] = []

        for schema in self.schemas:
            updated_in_place = False
            schema_file = self.schema_folder / f"{schema.name}.json"

            for item in settings[vscode_key]:
                if schema.name in item.get("url", ""):
                    item["url"] = str(schema_file)
                    updated_in_place = True

            if not updated_in_place:
                settings[vscode_key].append({"fileMatch": ["*.json"], "url": str(schema_file)})

        util.write_file(settings, vscode_settings_file)


@click.command()
@click.option(
    "-vc",
    "--vscode",
    default=False,
    show_default=True,
    help="""Update JSON schemas in vscode settings. Note will create .vscode folder
    if not present in the current directory.""",
)
def create_schemas(vscode: bool):
    """Function to handle the JSON schemas for emerge package."""

    schema_manager = SchemaManager()
    schema_manager.add_schema("emerge_scenario_schema", data_model.DERScenarioConfigModel)
    schema_manager.add_schema("emerge_timeseries_simulation_schema", TimeseriesSimulationInput)
    schema_manager.generate_and_save_schemas()
    if vscode:
        schema_manager.configure_vscode_settings()
