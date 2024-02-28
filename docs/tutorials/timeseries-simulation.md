# Timeseries Simulation

If you need to run timeseries simulation for a given opendss model and export some metrics you can use `timeseries-simulation` command available through emerge cli utility.

```cmd
emerge timeseries-simulation -c emerge_timeseries_config.json
```

Note `timeseries-simulation` command takes json file as configuration file. If you need json schema for this configuration file, you can run following command.

```cmd
emerge create-schemas
```

Above command creates multiple json schemas. For `timeseries-simulation` command please use schema with name `emerge_timeseries_simulation_schema.json`.  If you are using vscode then you can pass `-vc` flag like below.

```cmd
emerge create-schemas -vc true
```