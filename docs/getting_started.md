
### <p style="color:teal;font-size:18px;font-weight:bold;width:max-content;border-bottom:2px solid blue;"> Step 1: Installation</p> 

In order to start using EMERGE make sure you have installed all the softwares and dependencies as pointed out in the `Welcome` page.

### <p style="color:teal;font-size:18px;font-weight:bold;width:max-content;border-bottom:2px solid blue;"> Step 2: Distribution Model </p> 

For this tutorial we are going to use the distribution model already present in the `emerge` repository. You will find the model in `examples/opendss` directory.

### <p style="color:teal;font-size:18px;font-weight:bold;width:max-content;border-bottom:2px solid blue;"> Step 3: Folder for storing emerge output data </p>  

Let's create an empty directory to store all the data emerge will generate in the upcoming steps. Let's call this folder `emerge_test_data`. Once you have created the folder let's open up a terminal and activate the python environment where emerge is installed. You will need to visit the folder that you created during the installation process which should contain `env` folder (if you have not changed the environment name) and run the command `env/Scripts/activate.bat` if you using windows command prompt or `source env/bin/activat` if you are using Mac or Linux terminal.

### <p style="color:teal;font-size:18px;font-weight:bold;width:max-content;border-bottom:2px solid blue;"> Step 4: Creating geojsons </p>

In this step we will use `create-geojsons` command. To see the full list of commands available you can execute the command `emerge --help`. Make sure you have activated the environment. 

`create-geojsons` command will create single json file for each asset type and this will be used to visualize different asset layers in the dashboard later on. Before running the command, let's create another folder insider `emerge_test_data` folder called `geojsons`. Now let's run the following the command. Make sure to update full path of `master.dss` file.

```cmd
emerge create-geojsons -m <>/emerge/opendss/master.dss -o geojsons
```

You should see following files in `geojsons` folder.

```tree
└── emerge_test_data
    └── geojsons
        ├── buses.json
        ├── lines.json
        ├── loads.json
        └── transformer.json
```

### <p style="color:teal;font-size:18px;font-weight:bold;width:max-content;border-bottom:2px solid blue;"> Step 5: Creating snapshot metrics </p>

In this step we will use `snapshot-metrics` command. This command will run a snapshot powerflow and extract basic technical parameters such as voltages, loadings which will be later displayed in the dashboard.

Execute following command to generate snapshot metrics. Make sure you are `emerge_test_folder` directory before you run this command and update full path of `master.dss` file.

```
emerge snapshot-metrics -m <>/emerge/opendss/master.dss -o snapshot.json
```

The folder structure now sould look like this.

```tree
└── emerge_test_data
    ├── geojsons
    |   ├── buses.json
    |   ├── lines.json
    |   ├── loads.json
    |   └── transformer.json
    └── snapshot.json
```

### <p style="color:teal;font-size:18px;font-weight:bold;width:max-content;border-bottom:2px solid blue;"> Step 6: Creating tie series metrics </p>

In this step we will use `compute-time-series-metrics` command. This command will run a time series powerflow and compute various risk metrics which will be later displayed in the dashboard.

Execute following command to generate risk metrics following time series powerflow simulation. Make sure you are in `emerge_test_folder` directory before you run this command and update full path of `master.dss` file. By default simulation will run for a day in 60 minute resolution. To learn more about the options run the command `emerge compute-time-series-metrics --help`.

```
emerge compute-time-series-metrics -m <>/emerge/opendss/master.dss -o timeseries.json
```

The folder structure now sould look like this.

```tree
└── emerge_test_data
    ├── geojsons
    |   ├── buses.json
    |   ├── lines.json
    |   ├── loads.json
    |   └── transformer.json
    ├── snapshot.json
    └── timeseries.json
```

### <p style="color:teal;font-size:18px;font-weight:bold;width:max-content;border-bottom:2px solid blue;"> Step 7: Creating PV deployment scenarios </p>

In this step we will use `generate-pv-scenarios-for-feeder` command. This command will create PV deployment scenarios on top of base distribution system model. Create folder named `pvscenarios` inside `emerge_test_data` folder.

Execute following command create PV deployment scenarios. Make sure you are in `emerge_test_folder` directory before you run this command and update full path of `master.dss` file. By default it will create 10 PV scenarios in the step of 10%. To learn more about the options run the command `emerge generate-pv-scenarios-for-feeder --help`.

```
emerge generate-pv-scenarios-for-feeder -m <>/emerge/opendss/master.dss -o scenarios
```

The folder structure now sould look like this.

```tree
└── emerge_test_data
    ├── geojsons
    |   ├── buses.json
    |   ├── lines.json
    |   ├── loads.json
    |   └── transformer.json
    ├── scenarios
    |   ├── scenario_0_10
    |   |   └── PVsystems.dss
    |   ├── scenario_0_20
    |   |   └── PVsystems.dss
    |   ├── scenario_0_30
    |   |   └── PVsystems.dss
    |   ├── scenario_0_40
    |   |   └── PVsystems.dss
    |   ├── scenario_0_50
    |   |   └── PVsystems.dss
    |   ├── scenario_0_60
    |   |   └── PVsystems.dss
    |   ├── scenario_0_70
    |   |   └── PVsystems.dss
    |   ├── scenario_0_80
    |   |   └── PVsystems.dss
    |   ├── scenario_0_90
    |   |   └── PVsystems.dss
    |   └── scenario_0_100
    |       └── PVsystems.dss
    ├── snapshot.json
    └── timeseries.json
```

### <p style="color:teal;font-size:18px;font-weight:bold;width:max-content;border-bottom:2px solid blue;"> Step 8: Computing time series metrics for all scenarios. </p>

In this step we will use `compute-multiscenario-time-series-metrics` command. This command run time series power flow simulation for all PV deployment scenarios in parallel. Create folder named `scenario_metrics` inside `emerge_test_data` folder.

Execute following to create metrics for all deployment scenarios. Make sure you are in `emerge_test_folder` directory before you run this command and update full path of `master.dss` file. By default it will run simulation for a day in hour resolution. To learn more about the options run the command `emerge compute-multiscenario-time-series-metrics --help`. Note in this we are using 4 cores in parallel. If your computer does not have 4 cores please reduce the number of cores used in parallel simulation.

```
emerge compute-multiscenario-time-series-metrics -m <>/emerge/opendss/master.dss -sf pvscenarios -o scenario_metrics -nc 4
```

The folder structure now sould look like this.

```tree
└── emerge_test_data
    ├── geojsons
    |   ├── buses.json
    |   ├── lines.json
    |   ├── loads.json
    |   └── transformer.json
    ├── scenarios
    |   ├── scenario_0_10
    |   |   └── PVsystems.dss
    |   ├── scenario_0_20
    |   |   └── PVsystems.dss
    |   ├── scenario_0_30
    |   |   └── PVsystems.dss
    |   ├── scenario_0_40
    |   |   └── PVsystems.dss
    |   ├── scenario_0_50
    |   |   └── PVsystems.dss
    |   ├── scenario_0_60
    |   |   └── PVsystems.dss
    |   ├── scenario_0_70
    |   |   └── PVsystems.dss
    |   ├── scenario_0_80
    |   |   └── PVsystems.dss
    |   ├── scenario_0_90
    |   |   └── PVsystems.dss
    |   └── scenario_0_100
    |       └── PVsystems.dss
    ├── scenario_metrics
    |   ├── scenario_0_10.json
    |   ├── scenario_0_10_convergence.csv
    |   ├── scenario_0_20.json
    |   ├── scenario_0_20_convergence.csv
    |   ├── scenario_0_30.json
    |   ├── scenario_0_30_convergence.csv
    |   ├── scenario_0_40.json
    |   ├── scenario_0_40_convergence.csv
    |   ├── scenario_0_50.json
    |   ├── scenario_0_50_convergence.csv
    |   ├── scenario_0_60.json
    |   ├── scenario_0_60_convergence.csv
    |   ├── scenario_0_70.json
    |   ├── scenario_0_70_convergence.csv
    |   ├── scenario_0_80.json
    |   ├── scenario_0_80_convergence.csv
    |   ├── scenario_0_90.json
    |   ├── scenario_0_90_convergence.csv
    |   ├── scenario_0_100.json
    |   └── scenario_0_100_convergence.csv
    ├── snapshot.json
    └── timeseries.json
```

### <p style="color:teal;font-size:18px;font-weight:bold;width:max-content;border-bottom:2px solid blue;"> Step 9: Updating the config.json </p>

Navigate to the `emerge/emerge/api` directory and update the content of config.json file.
The content of json file should look like this. Make sure to include the full path here and update the port of front end application if it is running in different port. By default should run in 3000 port.

```json
{
    "snapshot_metrics_db": "<>/emerge_test_data/snapshot.json",
    "timeseries_metrics_db": "<>/emerge_test_data/timeseries.json",
    "geojson_path": "<>/emerge_test_data/geojsons",
    "scenario_metrics_db": "<>/emerge_test_data/scenario_metrics",
    "ui_url": "http://localhost:3000"
}
```

### <p style="color:teal;font-size:18px;font-weight:bold;width:max-content;border-bottom:2px solid blue;"> Step 10: Run the python server </p>

You will need to cd into `emerge/emerge/api` directory and run the following command.

```
uvicorn main:app --reload
```

Keep this terminal running and open up a new terminal for next step.

### <p style="color:teal;font-size:18px;font-weight:bold;width:max-content;border-bottom:2px solid blue;"> Step 11: Run the front end </p>

You will need to cd into `emerge/emerge/emerge_web` directory and run the following command. It will take couple of seconds for the server start. Do not close the terminal and keep it running.

```
npm run start
```

### <p style="color:teal;font-size:18px;font-weight:bold;width:max-content;border-bottom:2px solid blue;"> Step 12: Explore the dashboard </p>

Now visit `localhost:3000` in your browser and you should see a dashboard.