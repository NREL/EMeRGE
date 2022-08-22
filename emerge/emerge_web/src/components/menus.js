import {Link} from "react-router-dom";
import chevronDown from '../icons/chevron-down.svg';
import plug from '../icons/power-plug.svg';
import asset_types from '../assets/asset_types.js';
import assets_logo from '../icons/assets_icon.svg';
import logo from '../icons/logo.svg';


function Header() {
    return (
      <div class="flex items-center py-3 pl-5 text-white shadow-xl bg-sky-600">
              <img src={logo} class="w-14 rounded-md shadow-md p-1"/>
              <div class="">
                <h1 class="text-3xl px-5 font-mono" > EMERGE </h1>
                <p class="px-5 font-mono"> Distribution System Explorer </p>
              </div>
        </div>
    )
  }

function Menu(){
    return (
      <div class="w-32 bg-slate-700 text-white border-r min-h-screen shadow-md">
          <div class=""> 
            
              <div class="flex flex-col py-2 bg-slate-800 border-b items-center hover:cursor-pointer"
                >
                  <Link to="/assets" class="flex flex-col items-center"> 
                    <h1 class="text-lg 2xl:text-xl pb-2"> Assets </h1>
                    <img src={assets_logo} width="40"/>
                  </Link>
                    
                
              </div>
  
              <div class="flex flex-col py-2 border-b items-center hover:cursor-pointer" >
                  
                  <Link to="/snapshots" class="flex flex-col items-center">
                    <h1 class="text-lg 2xl:text-xl pb-2"> Snapshot </h1>
                    <img src={assets_logo} width="40"/>
                  </Link>
              </div>

              <div class="flex flex-col py-2 border-b items-center hover:cursor-pointer" >
                  
                  <Link to="/timeseries-metrics" class="flex flex-col items-center">
                    <h1 class="text-lg 2xl:text-xl pb-2"> Metrics </h1>
                    <img src={assets_logo} width="40"/>
                  </Link>
              </div>
  
          </div>
      </div>
    )
  }
  
function AssetsPageMenu(props){
  
      return (
        <div>
          <div class="flex border-t">
  
              <div class="min-h-screen bg-slate-700 w-full">
                <div >
                  <div class="bg-slate-900 px-5 h-16 flex items-center justify-between 
                    hover:border-2 hover:border-indigo-600 hover:cursor-pointer">
                      <div class="flex">
                        <img src={plug} width="30" class="mr-5"/>
                        <h1 class="text-xl 2xl:text-2xl"> Electrical Layers </h1>
                      </div>
                      <img src={chevronDown} width="30"/>
                  </div>
    
                  <div class="px-10 py-5">
  
                        {
                            asset_types.map( (asset, index) => {
                              return (
                                <div class="flex items-center justify-between mb-5" key={index}>
                                  <div class="flex items-center">
                                    <input class="w-8 h-8 mr-5 bg-slate-700 border-2 border-white text-orange-600 rounded-md" 
                                        type="checkbox" name={asset.variable} value="" checked={props.state[asset.variable]} 
                                        onChange={props.handleCheckbox}/>
                                    <label class="text-base 2xl:text-xl font-bold"> {asset.name} </label>
                                  </div>
                                  <div className={asset.bg_color + " w-5 h-5 rounded-full"}>
                                  </div>
                                </div>
                              )
                            })
                        }
                  </div>
                </div>
              </div>
    
          </div>
        </div>
      )
}

function SnapshotsPageMenu(){
  
    return (
      <div>
        <div class="flex border-t text-white">

            <div class="min-h-screen bg-slate-700 w-full">
              <div >
                <div class="bg-slate-900 px-5 h-16 flex items-center justify-between 
                  hover:border-2 hover:border-indigo-600 hover:cursor-pointer">
                    <div class="flex">
                      <img src={plug} width="30" class="mr-5"/>
                      <h1 class="text-xl 2xl:text-2xl"> Voltage Heatmap </h1>
                    </div>
                    <img src={chevronDown} width="30"/>
                </div>
  
                <div class="px-10 py-5">

                      
                </div>
              </div>
            </div>
  
        </div>
      </div>
    )
}

export {Menu, AssetsPageMenu, Header, SnapshotsPageMenu};