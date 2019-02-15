import ferly_horizontal_logo from './images/ferly_horizontal_logo.svg';
import React, {Component} from 'react';
import {colors} from './Home';
import PrivacyPolicy from './documents/PrivacyPolicy.pdf'
import RefundPolicy from './documents/RefundPolicy.pdf'

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
      <div style={{color: colors.darkBlue}}>
        <img
            src={ferly_horizontal_logo}
            {...logoProps}
            alt="logo" />
        <div style={{marginLeft: this.wide ? 40 : 10}}>
          <div style={{
              display: 'flex',
              justifyContent: 'flex-start',
              textAlign: 'left',
              flexWrap: 'wrap'
            }}>
            <div style={{marginBottom: 10, marginRight: 40}}>
              <h3>Address</h3>
              481 E 1000 S Suite B<br />
              Pleasant Grove, UT 84062
            </div>
            <div style={{marginBottom: 10, marginRight: 40}}>
              <h3>Contact Us</h3>
              801-839-4010<br />
              support@ferly.com
            </div>
            <div style={{marginBottom: 10, marginRight: 40}}>
              <h3>Legal</h3>
              <a href={PrivacyPolicy} target="_blank">
                Privacy Policy
              </a><br />
              <a href={RefundPolicy} target="_blank">
                Cancellation & Refund Policy
              </a>
            </div>
          </div>
          <p style={{fontSize: 12}}>
            Copyright © 2018 Ferly, Inc. All rights reserved.
          </p>
        </div>
      </div>
    );
  }
}

export default Footer;
