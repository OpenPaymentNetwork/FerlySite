import AppBar from 'material-ui/AppBar';
import ferly_horizontal_logo from './images/ferly_horizontal_logo.svg';
import React, {Component} from 'react';
import Toolbar from 'material-ui/Toolbar';


class Footer extends Component {

  constructor(props) {
    super(props);
    this.wide = window.innerWidth > 768;
  }

  render() {
    const logoProps = {
      width: this.wide ? 225 : 100,
      height: this.wide ? 60 : 35,
    }

    return (
      <AppBar
          position="static"
          color="inherit"
          elevation={0}>
        <Toolbar style={{color: '#1D3A54'}}>
          <img
              src={ferly_horizontal_logo}
              {...logoProps}
              alt="logo" />
          <div style={{flex: '1'}} />
          Copyright © 2018 Ferly, Inc. All rights reserved.
        </Toolbar>
      </AppBar>
    );
  }
}

export default Footer;
