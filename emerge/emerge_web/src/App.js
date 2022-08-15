/// app.js
import React, { Component } from 'react';
import { Routes, Route} from "react-router-dom";
import {Menu, Header} from './components/menus';
import AssetsPage from './assets/assets';
import SnapShot from './components/snapshots';
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
                </Routes>
              </div>
        </div>
        
      </div>
    )
  }
}

export default App;
