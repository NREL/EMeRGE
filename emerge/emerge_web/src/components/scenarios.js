import { Component } from "react";
import { ScenarioPageMenu } from "./menus";
import config from '../config';
import Plotly from 'plotly.js-dist';


class AssetTimeseriesMetrics extends Component {
    
    constructor(props) {
        super(props)

    }

    componentDidUpdate(){
        var layout = {
            title: this.props.title, 
            xaxis: {
                title: "PV penetration (%)"
            },
            yaxis: {
                title: this.props.y_label
            }
        };
        Plotly.newPlot('asset_timeseries', this.props.data, layout);
    }

    render() {
        
        return (
                <div>
                    <div id="asset_timeseries">
                    </div>
                </div>

        )
    }

}



class ScenarioPage extends Component {

    constructor(){
        super()
        this.state = {
            option: {
                'value': 'system'
            },
            nvri: null,
            tlri: null,
            llri: null,
            system: null,
            total_energy: null,
            total_pv_energy: null
        }
    
    }
    componentDidMount () {

        fetch( config.base_url + '/scenarios/system_metrics')
        .then(response => 
                response.json())
        .then((data)=>{
            
            this.setState({"system": data})
        })
        .catch(error=>{
            console.log(error);
        });

        fetch( config.base_url + '/scenarios/timeseries_asset/NVRI')
        .then(response => 
                response.json())
        .then((data)=>{
            this.setState({"nvri": data})
        })
        .catch(error=>{
            console.log(error);
        });
        fetch( config.base_url + '/scenarios/timeseries_asset/TLRI')
        .then(response => 
                response.json())
        .then((data)=>{
            this.setState({"tlri": data})
        })
        .catch(error=>{
            console.log(error);
        });
        fetch( config.base_url + '/scenarios/timeseries_asset/LLRI')
        .then(response => 
                response.json())
        .then((data)=>{
            this.setState({"llri": data})
        })
        .catch(error=>{
            console.log(error);
        });
        fetch( config.base_url + '/scenarios/timeseries/TotalEnergy')
        .then(response => 
                response.json())
        .then((data)=>{
            this.setState({"total_energy": data})
        })
        .catch(error=>{
            console.log(error);
        });
        fetch( config.base_url + '/scenarios/timeseries/TotalPVGeneration')
        .then(response => 
                response.json())
        .then((data)=>{
            this.setState({"total_pv_energy": data})
        })
        .catch(error=>{
            console.log(error);
        });

    }

    handleChange = (event) => {
      
        this.setState({
            option : {
                value: event.target.value
            }
        })
    }

    render() {
        let component;

        if (this.state.option.value === 'system'){
            
            component = <div class="p-5 w-4/5 h-5/6">
                            <AssetTimeseriesMetrics name="NVRI" data={this.state.system}
                            title='Comparing SARDI metrics across scenarios'
                            y_label='Average Risk (%-customer-hours)'/>
                        </div>;
        }
        else if (this.state.option.value === 'nvri'){
            
            component = <div class="p-5 w-4/5 h-5/6">
                            <AssetTimeseriesMetrics name="NVRI" data={this.state.nvri}
                            title='Comparing time series asset risk metrics'
                            y_label="Weighted depth of violation"/>
                        </div>;
        }

        else if (this.state.option.value === 'tlri'){
            
            component = <div class="p-5 w-4/5 h-5/6">
                            <AssetTimeseriesMetrics name="TLRI" data={this.state.tlri}
                            title='Comparing time series asset risk metrics'
                            y_label="Weighted depth of violation"/>
                        </div>;
        }

        else if (this.state.option.value === 'llri'){
            
            component = <div class="p-5 w-4/5 h-5/6">
                            <AssetTimeseriesMetrics name="LLRI" data={this.state.llri}
                            title='Comparing time series asset risk metrics'
                            y_label="Weighted depth of violation"/>
                        </div>;
        }

        else if (this.state.option.value === 'total_energy'){
            
            component = <div class="p-5 w-4/5 h-5/6">
                            <AssetTimeseriesMetrics name="Total_Energy" data={this.state.total_energy}
                            title='Comparing total substation energy'
                            y_label="MWhr or Mvarhr"/>
                        </div>;
        }

        else if (this.state.option.value === 'total_pv_energy'){
            
            component = <div class="p-5 w-4/5 h-5/6">
                            <AssetTimeseriesMetrics name="Total_PV_Energy" data={this.state.total_pv_energy}
                            title='Comparing total PV energy'
                            y_label="MWhr or Mvarhr"/>
                        </div>;
        }


        return (

            <div class="flex">
                <div class="w-1/4 overflow-scroll h-screen">
                    <ScenarioPageMenu 
                    option={this.state.option}
                    handleChange={this.handleChange}
                    />
                </div>
                
                {component}

            </div>
        )
    }
}

export default ScenarioPage