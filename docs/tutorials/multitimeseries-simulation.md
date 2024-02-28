# Multi Timeseries Simulation

If you need to run multi timeseries simulation for a given opendss model and export some metrics you can use `multit-imeseries-simulation` command available through emerge cli utility.

```cmd
emerge multi-timeseries-simulation -c emerge_timeseries_config.json -sf <scenario-folder> -nc 3
```

Note `multi-timeseries-simulation` command takes json file as configuration file. If you need json schema for this configuration file, you can run following command. Other two inputs are path to scenario folder. A scenario folder should contain `.dss` files where each `.dss` file considered independent single scenario. The last argument is number of cores for parallel simulation.

```cmd
emerge create-schemas
```

Above command creates multiple json schemas. For `timeseries-simulation` command please use schema with name `emerge_timeseries_simulation_schema.json`.  If you are using vscode then you can pass `-vc` flag like below.

```cmd
emerge create-schemas -vc true
```