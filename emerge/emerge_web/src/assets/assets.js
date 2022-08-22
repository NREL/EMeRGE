import React, { Component } from 'react';
import DeckGL from '@deck.gl/react';
import {GeoJsonLayer} from '@deck.gl/layers';
import {Map} from 'react-map-gl';
import {AssetsPageMenu} from '../components/menus';

class Assets extends Component {
  
    constructor(props) {
        super(props)
    }

    render() {

        // Set your mapbox access token here
        const MAPBOX_ACCESS_TOKEN = 'pk.eyJ1Ijoia2R1d2FkaSIsImEiOiJjbDR4bGdwMHYwMGtzM2xvMnJ3Z2w5NHJtIn0.sDUtApi8peyjZPy3ASmPWg';

        // Viewport settings
        const INITIAL_VIEW_STATE = {
        longitude: 80.267428,
        latitude: 13.083537,
        zoom: 15,
        pitch: 0,
        bearing: 0
        };

        const node_color_mapper = {
            'buses': [255, 0, 0],
            'transformers': [0,255,0],
            'lines': [255, 255, 255],
            'loads': [63, 81, 181]
        }

        const node_sizes = {
            'buses':2,
            'transformers': 15,
            'lines': 5,
            'loads': 4
        }

        const layers = this.props.asset_data.map((d) => [
        
        // new LineLayer({id: 'line-layer', data1 }),
            new GeoJsonLayer({id: 'geojson-layer', 
            data: d.data,
            filled: true,
            pointType: 'circle',
            getPointRadius: node_sizes[d.type],
            getFillColor: node_color_mapper[d.type],
            getLineColor: node_color_mapper[d.type],
            lineWidthScale: 6
            })
        ]);

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


function AssetMetrics(props){

    return (
      <div>
        <h1 class="text-xl text-orange-500 font-bold mb-2"> {props.title} </h1>

        <div class="grid grid-cols-2">
            {
              props.data.map((d, index) => { return (
                <div class="flex flex-col items-center mb-5 capitalize text-center px-1" key={index}>
                  <h1 class="text-2xl 2xl:text-4xl"> {d.value} </h1>
                  <p class="italic text-sm 2xl:text-md"> {d.metric}</p> 
                </div>
              )
              })
            }
        </div>

      </div>
    )

}



// Data to be used by the LineLayer
class AssetsPage extends Component {

  constructor(){
    super()
    this.state = {
      "asset_data": [],
      "metrics": [],
    }
  }

  handlePageUpdate(page_name) {
    this.setState({"active_page": page_name})
  }

  handleCheckbox = (event) =>{
    // event.preventDefault()
    console.log(event.target.name, event.target.checked)
    this.setState({
      [event.target.name]: event.target.checked
    })


    if(event.target.checked){
      fetch('http://localhost:8000/assets/geojsons/' + event.target.name)
      .then(response => 
            response.json())
      .then((data)=>{
          
        const state_data = this.state.asset_data
        state_data.push(data)
        this.setState({"asset_data": state_data})

      })
      .catch(error=>{
          console.log(error);
      });

      fetch('http://localhost:8000/assets/metrics')
      .then(response => 
            response.json())
      .then((data)=>{
          
        const metrics = this.state.metrics
        const metric_data = data.filter((d)=> { return d.type === event.target.name})
        
        if (metric_data.length !==0 ){
          metrics.push(metric_data[0])
          this.setState({"metrics": metrics})
        }
        

      })
      .catch(error=>{
          console.log(error);
      });



    } else {
      const asset_data = this.state.asset_data.filter((d) => { return d.type !== event.target.name})
      this.setState({"asset_data": asset_data})
      const metrics = this.state.metrics.filter((d) => { return d.type !== event.target.name})
      this.setState({"metrics": metrics})
    }
    // Let's get the data
   
  
  }
  render(){

      return (
        
          <div>
            <div class="flex relative">
              <div class="w-1/4 bg-slate-800 shadow-md text-white"> 
                <AssetsPageMenu handleCheckbox={this.handleCheckbox.bind(this)} state={this.state}/> </div>
              
              <div class="w-3/4 relative border-l"> 
                  <Assets asset_data={this.state.asset_data}/> 
              </div>
    
              <div class="absolute top-10 right-10 text-white w-1/4 2xl:w-1/5 
                  bg-gray-800 shadow-md rounded-md opacity-95 max-h-[32rem] 2xl:max-h-[48rem] overflow-y-scroll">
                {
                  this.state.metrics.map( (metric, index) => {
                    return (
                      <div class="p-10" key={index}>
                          <AssetMetrics title={metric.type} data={metric.data}/>
                      </div>
                    )
                  })
                }
              </div>
            </div>
          </div>
          
      )
    } 
  }

export default AssetsPage;