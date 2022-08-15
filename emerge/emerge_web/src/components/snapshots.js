import { Component } from "react";
import {SnapshotsPageMenu} from "./menus";
import DeckGL from '@deck.gl/react';
import {HeatmapLayer} from '@deck.gl/aggregation-layers';
// import {ScatterplotLayer} from '@deck.gl/layers';
import {ScreenGridLayer} from '@deck.gl/aggregation-layers';
import {GridCellLayer} from '@deck.gl/layers';
import Plotly from 'plotly.js-dist';
import {Map} from 'react-map-gl';


class VoltageSnapshot extends Component {
  
    constructor(props) {
        super(props)

    }

    render() {

        console.log(this.props.voltage)
        // Set your mapbox access token here
        const MAPBOX_ACCESS_TOKEN = 'pk.eyJ1Ijoia2R1d2FkaSIsImEiOiJjbDR4bGdwMHYwMGtzM2xvMnJ3Z2w5NHJtIn0.sDUtApi8peyjZPy3ASmPWg';

        // Viewport settings
        const INITIAL_VIEW_STATE = {
        longitude: 80.267428,
        latitude: 13.083537,
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
                mapboxAccessToken={MAPBOX_ACCESS_TOKEN} 
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
            'voltage': []
        }

        fetch('http://localhost:8000/snapshots/voltage')
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
        
        fetch('http://localhost:8000/snapshots/voltage-distribution')
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
                    <VoltageSnapshot voltage={this.state.voltage}/>
                </div>

                <div id="myDiv" class="absolute bottom-0 right-0 w-2/4 
                h-48 mr-20 mb-5 opacity-80 shadow-md text-white">
                </div>
            
            </div>
        )
    }
    
}

export default SnapShot