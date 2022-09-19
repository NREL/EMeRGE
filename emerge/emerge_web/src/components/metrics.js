import { Component } from "react";
import {MetricsPageMenu} from "./menus";
import DeckGL from '@deck.gl/react';
import {ScatterplotLayer} from '@deck.gl/layers';
import {LineLayer} from '@deck.gl/layers';
import {GeoJsonLayer} from '@deck.gl/layers';
import {Map} from 'react-map-gl';
import Plotly from 'plotly.js-dist';
import config from '../config';


class SARDI_Metrics extends Component {

    constructor(){
        super()
    }

    componentDidMount(){
        
        fetch(config.base_url + '/metrics/system_metrics')
        .then(response => 
                response.json())
        .then((data)=>{

            var mod_data = data.map((d)=>  [{
                domain: { x: [0, 1], y: [0, 1] },
                value: d.value,
                title: { text: d.name },
                type: "indicator",
                mode: "gauge+number",
                gauge: {
                    axis: { range: [null, 100]},
                    bordercolor: "white"
                }
            }]
            );
    
            var layout = { 
                width: 200, 
                height: 200, 
                margin: { t: 0, b: 0, l:0, r:0},
                'plot_bgcolor': '#0F1728', 
                'paper_bgcolor': '#0F1728',
                font: {color: "#ffffff"}
            };
            Plotly.newPlot('sardi_voltage', mod_data[0], layout);
            Plotly.newPlot('sardi_line', mod_data[1], layout);
            Plotly.newPlot('sardi_transformer', mod_data[2], layout);
            Plotly.newPlot('sardi_aggregated', mod_data[3], layout);
        
        })
        .catch(error=>{
            console.log(error);
        });
        
    }

    render() {
        return (
            <div class="grid grid-cols-2 place-items-center 2xl:grid-cols-3 items-center mx-10 my-10 gap-y-2">
          
                <div class="grid grid-cols-1 place-items-center mb-10">
                    <div id="sardi_voltage" class="">
                    </div>
                    <p class="text-white px-3 text-center">Average percentage number of customers 
                    affected by voltage violation.</p>
                </div>
                <div class="grid grid-cols-1 place-items-center mb-10">
                    <div id="sardi_line" class="">
                    </div>
                    <p class="text-white px-3 text-center">Average percentage number of customer affected by 
                    line thermal violation.</p>
                </div>

                <div class="grid grid-cols-1 place-items-center mb-10"> 
                    <div id="sardi_transformer" class="">
                    </div>
                    <p class="text-white px-3 text-center">Average percentage number of customer 
                    affected by transformer thermal violation</p>
                </div>

                <div class="grid grid-cols-1 place-items-center mb-10"> 
                    <div id="sardi_aggregated" class="">
                    </div>
                    <p class="text-white px-3 text-center">Average percentage number of customer affected by 
                    both voltage and thermal violation</p>
                </div>
            </div>
        )
    }
    
}

class LLRIMap extends Component {
  
    constructor(props) {
        super(props)

    }

    render() {

        // Viewport settings
        const INITIAL_VIEW_STATE = {
        longitude: this.props.center.longitude,
        latitude: this.props.center.latitude,
        zoom: 15,
        pitch:0,
        bearing: 0
        };

        const layers = new LineLayer({id: 'llri-line-layer', 
            data: this.props.llri,
            getSourcePosition: d => d.coordinates[0],
            getTargetPosition: d => d.coordinates[1],
            pickable: true,
            getWidth: d=> 3,
            getColor: d => [d.data*255/this.props.max_llri, 140, 255]
            })

        return (
            <DeckGL
                initialViewState={INITIAL_VIEW_STATE}
                controller={true}
                layers={layers}
            >
                <Map 
                mapboxAccessToken={config.mapbox_token} 
                mapStyle="mapbox://styles/mapbox/dark-v10"
                />
            </DeckGL>
        );

}


}

class NodeMap extends Component {
  
    constructor(props) {
        super(props)

    }

    render() {

        // Viewport settings
        const INITIAL_VIEW_STATE = {
        longitude: this.props.center.longitude,
        latitude: this.props.center.latitude,
        zoom: 15,
        pitch:0,
        bearing: 0
        };

    
        const layer1 = new ScatterplotLayer({id: 'scatter-layer', 
            data: this.props.data,
            getPosition: d => d.coordinates,
            getRadius: d => d.data*20,
            intensity: 1,
            radiusPixels: 80,
            threshold: 0.5,
            pickable: true,
            opacity: 0.8,
            stroked: true,
            filled: true,
            radiusScale: 10,
            radiusMinPixels: 0,
            radiusMaxPixels: 100,
            lineWidthMinPixels: 1,
            getFillColor: d => [255, 140, 0],
            })
        const layer2 = new GeoJsonLayer({id: 'edge-geojson-layer', 
            data: this.props.edge.data,
            filled: true,
            pointType: 'circle',
            lineWidthScale: 1,
            lineWidthMinPixels: 1,
            getFillColor: d => [255, 0, 0],
            getLineColor: d => [255, 255, 255],
            getLineWidth: 1,
            })


        return (
            <DeckGL
                initialViewState={INITIAL_VIEW_STATE}
                controller={true}
                layers={[layer2, layer1]}
            >
                <Map 
                mapboxAccessToken={config.mapbox_token} 
                mapStyle="mapbox://styles/mapbox/dark-v10"
                />
            </DeckGL>
        );

}


}


class MetricPage extends Component {

    constructor(){
        super()
        this.state = {
            nvri: [],
            llri: [],
            tlri: [],
            max_llri:0,
            edges: {"data": []},
            option: {
                'value': 'nvri'
            },
            center : {'longitude': 0, 'latitude': 0}
        }
        
        fetch(config.base_url + '/map_center')
        .then(response => 
                response.json())
        .then((data)=>{
            this.setState({"center": data})

        })
        .catch(error=>{
            console.log(error);
        });

        fetch(config.base_url + '/assets/geojsons/lines')
        .then(response => 
                response.json())
        .then((data)=>{
            
            this.setState({"edges": data})

        })
        .catch(error=>{
            console.log(error);
        });

        fetch(config.base_url + '/metrics/timeseries/nvri')
        .then(response => 
                response.json())
        .then((data)=>{
            this.setState({"nvri": data})

        })
        .catch(error=>{
            console.log(error);
        });

        fetch(config.base_url + '/metrics/timeseries/tlri')
        .then(response => 
                response.json())
        .then((data)=>{
            this.setState({"tlri": data})

        })
        .catch(error=>{
            console.log(error);
        });

        fetch( config.base_url + '/metrics/timeseries/llri')
        .then(response => 
                response.json())
        .then((data)=>{
            this.setState({"llri": data})
            let llri_values = data.map((d)=> parseFloat(d.data))
            this.setState({'max_llri': Math.max(...llri_values).toFixed(2)})
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
            
            component = <div class="w-3/4 relative border-l bg-slate-900 h-screen overflow-scroll">
                            <SARDI_Metrics/>
                        </div>;
        } else if(this.state.option.value === 'nvri'){

            component =  <div class="w-3/4 relative border-l max-h-screen">
                            <NodeMap data={this.state.nvri} edge={this.state.edges} center={this.state.center}/>
                        </div>;
        } else if(this.state.option.value === 'tlri'){

            component =  <div class="w-3/4 relative border-l max-h-screen">
                            <NodeMap data={this.state.tlri} edge={this.state.edges} center={this.state.center}/>
                        </div>;
        } else if(this.state.option.value === 'llri'){
            component = <div class="w-3/4 relative border-l max-h-screen">
                            <LLRIMap llri={this.state.llri} max_llri={this.state.max_llri} center={this.state.center}/>
                        </div>

        }
        return (
            
            <div class="flex">
                <div class="w-1/4 overflow-scroll h-screen">
                    <MetricsPageMenu 
                    max_llri={this.state.max_llri}
                    option={this.state.option} 
                    handleChange={this.handleChange}/>
                </div>
                
                {component}
            </div>
        )
    }
    
}

export default MetricPage