import {Link} from "react-router-dom";
import chevronDown from '../icons/chevron-down.svg';
import plug from '../icons/power-plug.svg';
import asset_types from '../assets/asset_types.js';
import assets_logo from '../icons/assets_icon.svg';
import logo from '../icons/logo.svg';
import { Component } from "react";


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

              <div class="flex flex-col py-2 border-b items-center hover:cursor-pointer" >
                  
                  <Link to="/scenario-metrics" class="flex flex-col items-center">
                    <h1 class="text-lg 2xl:text-xl pb-2"> Scenarios </h1>
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

function ScenarioPageMenu(props){
  return (
    <div class="flex border-t text-white">
      <div class="min-h-screen bg-slate-700 w-full"> 
        <div class="px-10 py-5">
            <h1 class="text-xl font-bold bg-slate-900 rounded-md p-2"> 
              Scenario time series metrics </h1>
        </div>

        <div class="px-10 py-5">

            <div class="flex items-center pb-2">
              <input type="radio" name="value" value="total_energy" defaultChecked={props.option.value==='total_energy'} onChange={props.handleChange}/>
              <h1 class="pl-3 text-xl font-bold text-sky-500"> Substation Energy </h1>
            </div>
            <p> Time series plot of total energy compared across DER scenrios.</p>

            <div class="flex items-center pb-2 pt-5">
              <input type="radio" name="value" value="total_pv_energy" defaultChecked={props.option.value==='total_pv_energy'} onChange={props.handleChange}/>
              <h1 class="pl-3 text-xl font-bold text-sky-500"> PV Energy </h1>
            </div>
            <p> Time series plot of total PV energy compared across DER scenrios.</p>

          
            <div class="flex items-center pb-2 pt-5">
              <input type="radio" name="value" value="system" defaultChecked={props.option.value==='system'} onChange={props.handleChange}/>
              <h1 class="pl-3 text-xl font-bold text-sky-500"> SARDI Metrics </h1>
            </div>
            <p> Time series plot of SARDI metrics compared across DER scenrios.</p>

            <div class="flex items-center pb-2 pt-5">
              <input type="radio" name="value" value="nvri" defaultChecked={props.option.value==='nvri'} onChange={props.handleChange}/>
              <h1 class="pl-3 text-xl font-bold text-sky-500"> NVRI </h1>
            </div>

            <p> Comparing Nodal Voltage Risk Index statistics across DER scenarios.</p>
            
            <div class="flex items-center pb-2 pt-5">
              <input type="radio" name="value" value="llri" defaultChecked={props.option.value==='llri'} onChange={props.handleChange}/>
              <h1 class="pl-3 text-xl font-bold text-sky-500"> LLRI </h1>
            </div>

            <p> Comparing Line Loading Risk Index statistics across DER scenarios.</p>

            <div class="flex items-center pb-2 pt-5">
              <input type="radio" name="value" value="tlri" defaultChecked={props.option.value==='tlri'} onChange={props.handleChange}/>
              <h1 class="pl-3 text-xl font-bold text-sky-500"> TLRI </h1>
            </div>

            <p> Comparing Transformer Loading Risk Index statistics across DER scenarios.</p>


        </div>

      </div>
    </div>
  )
}

function MetricsPageMenu(props){

    return (
      <div>
        <div class="flex border-t text-white">
  
            <div class="min-h-screen bg-slate-700 w-full">
              
              <div class="px-10 py-5">
                <h1 class="text-xl font-bold bg-slate-900 rounded-md p-2"> Time series metrics </h1>
              </div>

              <div>
                <div class="px-10 py-5">
                    <div class="flex items-center pb-2">
                      <input type="radio" name="value" value="system" defaultChecked={props.option.value==='system'} onChange={props.handleChange}/>
                      <h1 class="pl-3 text-xl font-bold text-sky-500"> System level metrics </h1>
                    </div>
                    <p class="italic mb-3"> Single value time series metrics.
                    </p>
                </div>
              </div>
  
              <div >
                <div class="px-10 py-5">
                    <div class="flex items-center pb-2">
                      <input type="radio" name="value" value="nvri" defaultChecked={props.option.value==='nvri'} onChange={props.handleChange}/>
                      <h1 class="pl-3 text-xl font-bold text-sky-500"> NVRI </h1>
                    </div>
                    <p class="italic mb-3 border-b"> Average depth of voltage violation for a node.
                    </p>
  
                    <div class="grid grid-cols-2 2xl:grid-cols-5 gap-x-1 grid">
                    <div class="flex items-center">
                        <div class="w-2 h-2 bg-orange-500 rounded-full"></div>
                        <p class="pl-2 font-bold">0.04</p>
                      </div>
  
                      <div class="flex items-center">
                        <div class="w-4 h-4 bg-orange-500 rounded-full"></div>
                        <p class="pl-2 font-bold">0.08</p>
                      </div>
  
                      <div class="flex items-center">
                        <div class="w-6 h-6 bg-orange-500 rounded-full"></div>
                        <p class="pl-2 font-bold">0.12</p>
                      </div>
  
                      <div class="flex items-center">
                        <div class="w-8 h-8 bg-orange-500 rounded-full"></div>
                        <p class="pl-2 font-bold">0.16</p>
                      </div>
  
                      <div class="flex items-center">
                        <div class="w-10 h-10 bg-orange-500 rounded-full"></div>
                        <p class="pl-2 font-bold">0.2</p>
                      </div>
                      
                    </div>
                    
                      
                </div>
              </div>
  
              <div >
                <div class="px-10 py-5">
                    <div class="flex items-center pb-2">
                      <input type="radio" name="value" value="llri" defaultChecked={props.option.value==='llri'} onChange={props.handleChange}/>
                      <h1 class="pl-3 text-xl font-bold text-sky-500"> LLRI</h1>
                    </div>
                    <p class="italic mb-3 border-b"> Average depth of thermal violation for a line.
                    </p>

                    <div class="flex justify-between font-bold">
                      <h1> 0.0 </h1>
                      <h1> {props.max_llri} </h1>
                    </div>
                    <div class="h-6 w-full bg-gradient-to-r from-[rgb(0,140,255)] to-[rgb(255,140,255)]"></div>
                    
                      
                </div>
              </div>

              <div >
                <div class="px-10 py-5">
                    <div class="flex items-center pb-2">
                      <input type="radio" name="value" value="tlri" defaultChecked={props.option.value==='tlri'} onChange={props.handleChange}/>
                      <h1 class="pl-3 text-xl font-bold text-sky-500"> TLRI</h1>
                    </div>
                    <p class="italic mb-3 border-b"> Average depth of thermal violation for a transformer.
                    </p>
  
                    <div class="grid grid-cols-2 2xl:grid-cols-5 gap-x-1 grid">
                    <div class="flex items-center">
                        <div class="w-2 h-2 bg-orange-500 rounded-full"></div>
                        <p class="pl-2 font-bold">0.04</p>
                      </div>
  
                      <div class="flex items-center">
                        <div class="w-4 h-4 bg-orange-500 rounded-full"></div>
                        <p class="pl-2 font-bold">0.08</p>
                      </div>
  
                      <div class="flex items-center">
                        <div class="w-6 h-6 bg-orange-500 rounded-full"></div>
                        <p class="pl-2 font-bold">0.12</p>
                      </div>
  
                      <div class="flex items-center">
                        <div class="w-8 h-8 bg-orange-500 rounded-full"></div>
                        <p class="pl-2 font-bold">0.16</p>
                      </div>
  
                      <div class="flex items-center">
                        <div class="w-10 h-10 bg-orange-500 rounded-full"></div>
                        <p class="pl-2 font-bold">0.2</p>
                      </div>
                      
                    </div>
                    
                      
                </div>
              </div>

            </div>
  
        </div>
      </div>
    )
  }

export {Menu, AssetsPageMenu, Header, SnapshotsPageMenu, MetricsPageMenu, ScenarioPageMenu};