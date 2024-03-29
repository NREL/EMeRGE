/// app.js
import React, { Component } from 'react';
import { Routes, Route} from "react-router-dom";
import {Menu, Header} from './components/menus';
import AssetsPage from './assets/assets';
import SnapShot from './components/snapshots';
import MetricPage from './components/metrics';
import ScenarioPage from './components/scenarios';
// import {axios} from 'axios';


class App extends Component {

  render() {
    return (

      <div>
        <Header />
        <div class="flex">
              <Menu class="w-20"/>
              <div class="w-full">
                <Routes>
                  <Route path='/assets' element={<AssetsPage/>} />
                  <Route path='/snapshots' element={<SnapShot />} />
                  <Route path='/timeseries-metrics' element={<MetricPage />} />
                  <Route path='/scenario-metrics' element={<ScenarioPage />} />
                </Routes>
              </div>
        </div>
        
      </div>
    )
  }
}

export default App;
