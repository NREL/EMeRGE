# Solar Nodal Hosting Capacity Analysis

You can run nodal hosting capacity analysis using emerge cli. Here is an example json config file you can use to run the simulation.

Make sure to define load shape for solar profile in the master dss file.

```json
{
    "start_time": "2023-01-08T00:00:00+00:00",
    "end_time": "2023-01-15T00:00:00+00:00",
    "profile_start_time": "2023-01-01T00:00:00+00:00",
    "resolution_min": 60, 
    "step_kw": 1000,
    "max_kw": 20000,
    "num_core": 10,
    "pv_profile": "PV_Profile",
    "export_sqlite_path": "hosting_capacity.db",
    "master_dss_file": "master_with_loadshapes.dss"
}
```

You can use following command to run nodal hosting capacity.

```bash
emerge nodal-hosting-analysis -c config.json
```