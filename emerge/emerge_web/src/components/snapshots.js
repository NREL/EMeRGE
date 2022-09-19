import { Component } from "react";
import {SnapshotsPageMenu} from "./menus";
import DeckGL from '@deck.gl/react';
import {HeatmapLayer} from '@deck.gl/aggregation-layers';
import {LineLayer} from '@deck.gl/layers';
import Plotly from 'plotly.js-dist';
import {Map} from 'react-map-gl';
import config from '../config';

class SnapshotLineLoadingHeatmap extends Component {
  
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

        const layers = new LineLayer({id: 'line-loading-layer', 
            data: this.props.line_loading,
            getSourcePosition: d => d.coordinates[0],
            getTargetPosition: d => d.coordinates[1],
            pickable: true,
            getWidth: d=> 3,
            getColor: d => [255, d.data*255, 255]
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

class SnapshotHeatmap extends Component {
  
    constructor(props) {
        super(props)
    }

    render() {
        const INITIAL_VIEW_STATE = {
            longitude: this.props.center.longitude,
            latitude: this.props.center.latitude,
            zoom: 15,
            pitch:0,
            bearing: 0
        };

    
        const layers = new HeatmapLayer({id: 'heatmap-layer', 
            data: this.props.data,
            getPosition: d => d.coordinates,
            getWeight: d =>d.weight,
            colorRange: [[255, 255, 255, 255], [255, 0, 0, 255]],
            intensity: 1,
            radiusPixels: 30,
            threshold: 0.5,
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


class SnapshotPlotlyPlot extends Component {
    
    constructor(props) {
        super(props)

        this.layout = {
            title: this.props.title, 
            xaxis: {
                title: this.props.x_label
            },
            yaxis: {
                title: this.props.y_label
            }
        };

    }

    componentDidMount () {
        Plotly.newPlot("snapshot_plot", this.props.data, this.layout);
    }

    componentDidUpdate () {
        Plotly.newPlot("snapshot_plot", this.props.data, this.layout);
    }

    render() {
        
        return (
                <div>
                    <div id="snapshot_plot">
                    </div>
                </div>

        )
    }

}


class SnapShot extends Component {

    constructor(){
        super()
        this.state = {
            voltage: [],
            center : {'longitude': 0, 'latitude': 0},
            voltage_by_distance: [],
            voltage_distribution: [],
            option: {
                value:  'voltage_heatmap'
            },
            line_loading: [],
            xfmr_loading: [],
            max_pu: null,
            min_pu: null,
            max_xfmr_loading: null,
            min_xfmr_loading: null

        };

        fetch(config.base_url + '/map_center')
        .then(response => 
                response.json())
        .then((data)=>{
            this.setState({"center": data})

        })
        .catch(error=>{
            console.log(error);
        });

        fetch(config.base_url + '/snapshots/voltage')
        .then(response => 
                response.json())
        .then((data)=>{
            this.setState({"voltage": data})
            let voltages = data.map((d)=> parseFloat(d.weight))
            this.setState({'max_pu': Math.max(...voltages).toFixed(2)})
            this.setState({'min_pu': Math.min(...voltages).toFixed(2)})

        })
        .catch(error=>{
            console.log(error);
        });

        fetch(config.base_url + '/snapshots/xfmr_loading')
        .then(response => 
                response.json())
        .then((data)=>{
            this.setState({"xfmr_loading": data})
            let loadings = data.map((d)=> parseFloat(d.weight))
            this.setState({'max_xfmr_loading': Math.max(...loadings).toFixed(2)})
            this.setState({'min_xfmr_loading': Math.min(...loadings).toFixed(2)})

        })
        .catch(error=>{
            console.log(error);
        });

        fetch(config.base_url + '/snapshots/voltage-by-distance')
        .then(response => 
                response.json())
        .then((data)=>{
            this.setState({"voltage_by_distance": data})

        })
        .catch(error=>{
            console.log(error);
        });
        
        fetch( config.base_url + '/snapshots/voltage-distribution')
        .then(response => 
                response.json())
        .then((data)=>{
            console.log(data)
            this.setState({"voltage_distribution": data})
            
        })
        .catch(error=>{
            console.log(error);
        });

        fetch(config.base_url + '/snapshots/line_loading')
        .then(response => 
                response.json())
        .then((data)=>{
            this.setState({"line_loading": data})

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
        

        if (this.state.option.value === 'voltage_heatmap'){
            component =<div class="w-3/4 relative border-l">
                        <SnapshotHeatmap data={this.state.voltage} 
                        center={this.state.center}
                        />
                    </div>
                
        }

        else if (this.state.option.value === 'voltage_by_distance') {
            component = <div class="w-3/4">
                <SnapshotPlotlyPlot 
                    data={this.state.voltage_by_distance}
                    name="voltage_by_distance"
                    title="Voltage by distance"
                    x_label="Distance from substation (km)"
                    y_label="Voltage (pu)"
                />
            </div>
        }
        else if (this.state.option.value === 'voltage_distribution') {
            component = <div class="w-3/4">
                 <SnapshotPlotlyPlot 
                 data={this.state.voltage_distribution} 
                 name="voltage_distribution"
                 title="Voltage distribution plot"
                 x_label="Voltage bin (pu)"
                 y_label="Percentage counts"
                 />
            </div>
        }

        else if (this.state.option.value === 'line_loading_heatmap'){
            component = <div class="w-3/4 relative border-l max-h-screen">
                <SnapshotLineLoadingHeatmap 
                line_loading={this.state.line_loading} 
                center={this.state.center}/>
            </div>
            
        }

        else if (this.state.option.value === 'xfmr_loading_heatmap'){
            component =<div class="w-3/4 relative border-l">
                        <SnapshotHeatmap data={this.state.xfmr_loading} 
                        center={this.state.center}
                        />
                    </div>
                
        }

        return (
            <div class="flex">
                <div class="w-1/4 overflow-scroll h-screen">
                    <SnapshotsPageMenu 
                    option={this.state.option}
                    max_pu={this.state.max_pu}
                    min_pu={this.state.min_pu}
                    max_xmfr_loading={this.state.max_xfmr_loading}
                    min_xmfr_loading={this.state.min_xfmr_loading}
                    handleChange={this.handleChange}
                    />
                </div>
                
                {component}


            </div>
        )
    }
    
}

export default SnapShot