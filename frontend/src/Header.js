import AppBar from 'material-ui/AppBar';
import Button from 'material-ui/Button';
import ferly_horizontal_logo from './images/ferly_horizontal_logo.svg';
import IconButton from 'material-ui/IconButton';
import Menu, {MenuItem} from 'material-ui/Menu';
import MenuIcon from 'material-ui-icons/Menu';
import React, {Component} from 'react';
import Toolbar from 'material-ui/Toolbar';


class Header extends Component {

  constructor(props) {
    super(props);
    this.wide = window.innerWidth > 768;
    this.state = {
      anchorEl: null,
      link: null,
    }
    this.links = {
      about: {label: 'About', key: 'about'},
      retailers: {label: 'For Merchants', key: 'retailers'},
      consumers: {label: 'For Consumers', key: 'consumers'}
    };
  }

  renderButton(link) {
    const buttonProps = {
      key: link.key,
      onClick: (e) => this.scrollTo(link.key),
    };
    const buttonStyle = {
      textTransform: 'none',
      color: '#1D3A54',
    };
    return <Button style={buttonStyle} {...buttonProps}>{link.label}</Button>;
  }

  renderMenuItem(link) {
    return (
      <MenuItem
          key={link.key}
          style={{color: '#1D3A54'}}
          onClick={(e) => this.setState({link: link.key, anchorEl: null})}>
        {link.label}
      </MenuItem>
    );
  }

  scrollTo(key) {
    const element = document.getElementById(key);
    element.scrollIntoView({behavior: 'smooth', block: 'start'})
  }

  renderLinks() {
    if (this.wide) {
      return (
        <div style={{display: 'flex'}}>
        {
          Object.keys(this.links).map((link) => {
            return this.renderButton(this.links[link]);
          })
        }
        </div>
      );
    } else {
      const {anchorEl} = this.state;
      return (
        <div>
          <IconButton
              onClick={(e) => this.setState({anchorEl: e.currentTarget})}>
            <MenuIcon />
          </IconButton>
          <Menu
              anchorEl={anchorEl}
              transitionDuration={0}
              open={Boolean(anchorEl)}
              onExited={() => this.scrollTo(this.state.link)}
              onClose={() => this.setState({anchorEl: null})}>
            {
              Object.keys(this.links).map((link) => {
                return this.renderMenuItem(this.links[link]);
              })
            }
          </Menu>
        </div>
      );
    }
  }

  render() {
    const logoProps = {
      width: this.wide ? 250 : 125,
      height: this.wide ? 70 : 40,
    }

    return (
      <AppBar color="inherit" elevation={0}>
        <Toolbar style={{color: '#1D3A54', paddingTop: '8px'}}>
          <img
              src={ferly_horizontal_logo}
              {...logoProps}
              alt="logo" />
          <div style={{flex: '1'}} />
          {this.props.home ? this.renderLinks() : null}
        </Toolbar>
      </AppBar>
    );
  }
}

export default Header;
