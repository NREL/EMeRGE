import { Component } from "react";
import { ScenarioPageMenu } from "./menus";
import config from '../config';
import Plotly from 'plotly.js-dist';


class ScenarioPage extends Component {

    componentDidMount(){
        
        fetch( config.base_url + '/scenarios/system_metrics')
        .then(response => 
                response.json())
        .then((data)=>{
            console.log(data)
            var layout = {
                title: 'Comparing SARDI metrics across scenarios', 
                xaxis: {
                    title: "PV penetration (%)"
                },
                yaxis: {
                    title: "Average Risk (%-customer-hours)"
                }
            };

            
            Plotly.newPlot('myDiv', data, layout);
        })
        .catch(error=>{
            console.log(error);
        });

        
    }

    render() {
        return (

            <div class="flex">
                <div class="w-1/4">
                    <ScenarioPageMenu />
                </div>

                <div id="myDiv" class="w-3/4">
                </div>

            </div>
        )
    }
}

export default ScenarioPage