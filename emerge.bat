call conda activate emerge_v2
cd C:/Users/KDUWADI/Desktop/NREL_Projects/Tunishia/emerge_bat_script_test
emerge create-geojsons -m models/master.dss -o geojsons
emerge snapshot-metrics -m models/master.dss -o snapshot.json
emerge compute-time-series-metrics -m models/master.dss -o timeseries.json
emerge generate-pv-scenarios-for-feeder -m models/master.dss -o pvscenarios -lm 0.21
emerge compute-multiscenario-time-series-metrics -m models/master.dss -sf pvscenarios -o scenario_metrics_unity_pf -nc 2 -pn pvshape_july1
emerge compute-multiscenario-time-series-metrics -m models/master.dss -sf pvscenarios -o scenario_metrics_voltvar -nc 2 -vvar True -pn pvshape_july1
emerge compute-multiscenario-time-series-metrics -m models/master.dss -sf pvscenarios -o scenario_metrics_voltvar_nightoff -nc 2 -vvar True -nt False -pn pvshape_july1
pause