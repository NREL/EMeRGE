import { Component } from "react";
import {SnapshotsPageMenu} from "./menus";
import DeckGL from '@deck.gl/react';
import {HeatmapLayer} from '@deck.gl/aggregation-layers';
import Plotly from 'plotly.js-dist';
import {Map} from 'react-map-gl';
import config from '../config';

class VoltageSnapshot extends Component {
  
    constructor(props) {
        super(props)
    }


    render() {
        // Set your mapbox access token here

        // Viewport settings
        const INITIAL_VIEW_STATE = {
        longitude: this.props.center.longitude,
        latitude: this.props.center.latitude,
        zoom: 15,
        pitch:0,
        bearing: 0
        };

    
        const layers = new HeatmapLayer({id: 'heatmap-layer', 
            data: this.props.voltage,
            getPosition: d => d.coordinates,
            getWeight: d =>d.weight,
            // radiusPixel: 15,
            // aggregation: 'MEAN',
            colorRange: [[1, 152, 189, 255], [73, 227, 206, 255], [216, 254, 181, 255], [254, 237, 177, 255],[254, 173, 84, 255],[209, 55, 78, 255]],
            intensity: 1,
            radiusPixels: 80,
            threshold: 0.5,
            // opacity: 0.6,
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

class SnapShot extends Component {

    constructor(){
        super()
        this.state = {
            voltage: [],
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

        fetch(config.base_url + '/snapshots/voltage')
        .then(response => 
                response.json())
        .then((data)=>{
            this.setState({"voltage": data})

        })
        .catch(error=>{
            console.log(error);
        });

    }

    componentDidMount(){
        
        fetch( config.base_url + '/snapshots/voltage-distribution')
        .then(response => 
                response.json())
        .then((data)=>{
            console.log(data)
            var layout = {barmode: 'group', 
                'plot_bgcolor': '#000000', 
                'paper_bgcolor': '#000000', 
                font: {color: "#ffffff"},
                margin: {
                    t: 0, b: 25, l: 25, r: 0
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
                    <SnapshotsPageMenu />
                </div>
                <div class="w-3/4 relative border-l">
                    <VoltageSnapshot voltage={this.state.voltage} center={this.state.center}/>
                </div>

                <div id="myDiv" class="absolute bottom-0 right-0 w-2/4 
                h-48 mr-20 mb-5 opacity-80 shadow-md text-white">
                </div>
            
            </div>
        )
    }
    
}

export default SnapShot