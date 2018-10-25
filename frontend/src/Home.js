import binoculars from './images/binoculars.png';
import Button from 'material-ui/Button';
import call from './images/phone.png';
import card from './images/card.png';
import chevron from './images/chevron.png';
import construction from './images/construction.png';
import debit from './images/debit.png';
import email from './images/email.png';
import Footer from './Footer';
import gear from './images/gear.png';
import graph from './images/graph.png';
import Header from './Header';
import introBackground from './images/background.png';
import mail from './images/mail.png';
import man from './images/man.png';
import mobile from './images/mobile.png';
import money from './images/money.png';
import phone from './images/iphone.png';
import purse from './images/purse.png';
import React, {Component} from 'react';
import screenshot from './images/screenshot.png';
import share from './images/share.png';
import Tabs, { Tab } from 'material-ui/Tabs';
import {withStyles} from 'material-ui/styles';
import ContactDialog from './components/ContactDialog';

export const colors = {
  'yellow': '#FCD634',
  'darkBlue': '#1D3A54',
  'white': '#E2F3F8',
  'lightBlue': '#65C7C7',
};

const styles = theme => ({
  button: {
    marginTop: '8%',
    backgroundColor: colors.darkBlue,
    color: colors.lightBlue,
  },
});



class Home extends Component {

  constructor(props) {
    super(props);
    this.wide = window.innerWidth > 768;
    this.toggleDialog = this.toggleDialog.bind(this);
    this.state = {
      mTab: 'why',
      cTab: 'features',
      dialogShow: false
    };
  }

  toggleDialog() {
    this.setState({dialogShow: !this.state.dialogShow});
  }

  componentDidMount() {
    setTimeout(this.toggleDialog, 12000);
  }

  scrollTo(target) {
    const element = document.getElementById(target);
    element.scrollIntoView({behavior: 'smooth', block: 'start'})
  }

  renderButton(text, target) {
    return (
      <Button
          variant="raised"
          style={{borderRadius: '18px'}}
          onClick={(e) => this.scrollTo(target)}
          className={this.props.classes.button}>
        {text}
      </Button>
    );
  }

  renderScreenshot() {
    const width = 270;
    return (
      <div style={{display: 'flex', justifyContent: 'center', flexDirection: 'column'}}>
        <div style={{position: 'relative'}}>
          <img src={phone} alt="screenshot" width={width} />
          <img
              src={screenshot}
              alt=""
              width={width - 58}
              style={{position: 'absolute', left: '30px', top: '71px'}} />
        </div>
      </div>
    )
  }

  renderInfo(icon, title, description, small=false) {
    const infoStyle = {
      display: 'flex',
      width: small || !this.wide ? '46%': '50%',
      minWidth: '300px',
      margin: '0 2%'
    }

    return (
      <div style={infoStyle}>
        <img src={icon} height={100} style={{marginTop: '24px'}} alt="" />
        <div style={{
            margin: '0 15px',
            color: colors.darkBlue,
            textAlign: 'left'}}>
          <h4 style={{fontFamily: 'GothamRnd-Med'}}>{title}</h4>
          <p style={{fontSize: '14px'}}>{description}</p>
        </div>
      </div>
    );
  }

  renderConsumerInfo(icon, description) {
    const infoStyle = {
      display: 'flex',
      width: '46%',
      minWidth: '300px',
      margin: '0 2%',
      padding: '20px',
    }

    return (
      <div style={infoStyle}>
        <img src={icon} height={80} style={{marginRight: '20px'}} alt="" />
        <p style={{fontSize: '14px', maxWidth: '260px', textAlign: 'left'}}>
          {description}
        </p>
      </div>
    );
  }

  renderContact(icon, info) {
    return (
      <div style={{margin: '40px', maxWidth: '48%'}}>
        <img src={icon} height={50} style={{marginBottom: '15px'}} alt="" />
        <br />
        {info}
      </div>
    );
  }

  handleMerchantTabChange(e, val) {
    this.setState({mTab: val});
  }

  handleConsumerTabChange(e, val) {
    this.setState({cTab: val});
  }

  renderTab(label, value) {
    const selected = value === this.state.mTab;
    const tabStyle = {
      backgroundColor: selected ? colors.lightBlue : 'white',
      borderRadius: '25px',
      color: selected ? 'white' : colors.lightBlue,
    }
    return (
      <Tab label={label} style={tabStyle} value={value} />
    );
  }

  renderConsumerTab(label, value) {
    const selected = value === this.state.cTab;
    const tabStyle = {
      backgroundColor: selected ? colors.darkBlue : 'transparent',
      borderRadius: '25px',
      color: selected ? colors.lightBlue : colors.darkBlue,
    }
    return (
      <Tab label={label} style={tabStyle} value={value} />
    );
  }

  renderMerchantSection() {
    const tab = this.state.mTab;
    const infoStyle = {
      display: 'flex',
      justifyContent: 'space-around',
      flexWrap: 'wrap',
      paddingTop: '70px',
      textAlign: 'center',
    };

    const sectionStyle = {
      minHeight: '300px',
      width: '100%',
      maxWidth: '96%',
      marginTop: '40px',
      color: colors.darkBlue,
    };

    const modelTableStyle = {
      border: 'solid 2px ' + colors.lightBlue,
      padding: '0 16px',
      borderRadius: '25px 25px 0 0',
    };

    const modelBottomTableStyle = {
      border: 'solid 2px ' + colors.lightBlue,
      borderTop: 0,
      borderRadius: '0 0 25px 25px',
      padding: '12px',
      textAlign: 'left',
      minHeight: '200px',
    };

    const modelStyle = {
      width: this.wide ? '40%' : '100%',
      margin: '15px',
    }

    return (
      <div id='retailers' style={infoStyle}>
        <h2 style={{
            fontFamily: 'GothamRnd-Light',
            width: '100%',
            color: colors.darkBlue
        }}>
          Merchants
        </h2>
        <Tabs
            fullWidth
            value={false}
            scrollable={!this.wide}
            scrollButtons={this.wide ? "off" : "on"}
            onChange={this.handleMerchantTabChange.bind(this)}>
          {this.renderTab("Why Ferly", "why")}
          {this.renderTab("Product Models", "models")}
          {this.renderTab("Features", "features")}
          {this.renderTab("Data", "data")}
        </Tabs>
        <div style={sectionStyle}>
        {tab === 'why' ? (
            <p style={{
                color: colors.lightBlue, maxWidth: '600px', margin: '0 auto'}}>
              Ferly is focused on solving challenges merchants face when
              distributing gift value to consumers. Common challenges Ferly
              helps merchants overcome are cost, lack of brand exposure,
              insufficient data, customized POS systems, inability to
              track gift value ownership and the inability to control the cost
              and exchange of gift value between consumers. Our solution can be
              leveraged by merchants of all sizes at costs lower than
              traditional gift distribution methods.
            </p>) : null}
        {tab === 'models' ? (
            <div style={{maxWidth: '960px', margin: '0 auto'}}>
              <h4 style={{color: colors.lightBlue}}>
                Choose between two integrated product models.
              </h4>
              <div style={{
                display: 'flex',
                flexWrap: 'wrap',
                justifyContent: 'space-around',
                fontFamily: 'GothamRnd-Light',
              }}>
                <div style={modelStyle}>
                  <div style={modelTableStyle}>
                    <h4>Consumer & Marketplace</h4>
                  </div>
                  <div style={modelBottomTableStyle}>
                    Merchants distribute gift value on an end-to-end
                    marketplace maintained by Ferly.<br />
                    <h4 style={{textAlign: 'center'}}>Benefits</h4>
                    <div>
                      Merchant brand exposure<br />
                      Universal consumer experience<br />
                      Quick integration & low maintenance<br />
                    </div>
                  </div>
                </div>
                <div style={modelStyle}>
                  <div style={modelTableStyle}>
                    <h4>Enterprise Integration</h4>
                  </div>
                  <div style={modelBottomTableStyle}>
                    Merchants distribute gift value through an existing
                    application or program integrated with Ferly's API.
                    <h4 style={{textAlign: 'center'}}>Benefits</h4>
                    <div>
                      White label, merchant branded experience<br />
                      Access to consumer analytics<br />
                      Utilize legacy systems<br />
                    </div>
                  </div>
                </div>
              </div>
            </div>
        ) : null}
        {tab === 'features' ? (
          <div style={{
            display: 'flex',
            justifyContent: 'space-around',
            flexWrap: 'wrap',
            maxWidth: '960px', margin: '0 auto',
          }}>
            {this.renderInfo(purse, "Single Access Point",
              "We increase efficiency by providing a single sign on location " +
              "to manage all aspects of your gift distribution program.", true)}
            {this.renderInfo(binoculars, "Increased Brand Exposure",
              "We enhance merchant brand exposure on an online gift " +
              "marketplace, increasing brand affinity with consumers.", true)}
            {this.renderInfo(card, "Debit Network Integration",
              "We ride the debit rail to eliminate merchants' integration " +
              "costs and the amount of plastic in consumers' wallets.", true)}
            {this.renderInfo(man, "Enhanced Security",
              "We follow industry leading security protocols and require " +
              "PIN authentication at POS.", true)}
          </div>
        ) : null}
        {tab === 'data' ?
          (
            <div style={{
              display: 'flex',
              justifyContent: 'space-around',
              flexWrap: 'wrap',
              maxWidth: '960px',
              margin: '0 auto',
            }}>
              {this.renderInfo(graph, "Analytics",
                "We collect various data points, including purchasing habits " +
                "and geolocation information to discover actionable insights.")}
              {this.renderInfo(money, "Total Traceability",
                "We keep track of the logistics so you don't have to, " +
                "including the total gift value purhcased, exchanged, " +
                "redeemed and owned by consumers.")}
              {this.renderInfo(gear, "Personalized Offers",
              "We provide the right data and insights to give consumers what " +
              "they want most through targeted offers.")}
            </div>
        ) : null}
        </div>
      </div>
    );
  }

  renderConsumersSection() {
    const tab = this.state.cTab;
    return (
      <div style={{
          display: 'flex',
          justifyContent: 'space-around',
          maxWidth: '960px',
          margin: '0 auto',
          flexWrap: 'wrap'}}>
        <h2 style={{fontFamily: 'GothamRnd-Light', width: '100%'}}>
          Consumers
        </h2>
         <Tabs
            fullWidth
            value={false}
            onChange={this.handleConsumerTabChange.bind(this)}>
          {this.renderConsumerTab("Features", "features")}
          {this.renderConsumerTab("Download Our App", "app")}
        </Tabs>
        {tab === 'features' ?
          (
            <div style={{
              display: 'flex', justifyContent: 'space-around', flexWrap: 'wrap'
            }}>
              {this.renderConsumerInfo(mobile,
                "Track all gift card balances in a single mobile app.")}
              {this.renderConsumerInfo(debit,
                "Redeem gift value for all merchants with a single card.")}
              {this.renderConsumerInfo(share,
                "Easily share gifts with friends.")}
            </div>
          ) : null}
        {tab === 'app' ?
          (
            <div style={{
              width: '100%',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'start',
              minHeight: '360px',
            }}>
              <img
                  src={construction}
                  width={80}
                  style={{margin: '20px auto'}}
                  alt="" />
              <p style={{maxWidth: '350px', margin: '20px auto'}}>
                Our app is currently under construction. It will be available on
                Apple and Android platforms soon. We appreciate your patience!
              </p>
            </div>
          ) : null}
      </div>
    );
  }



  render() {

    const introHeadStyle = {
      backgroundImage: `url(${introBackground})`,
      backgroundSize: this.wide ? '70% ' + window.innerWidth : '180% 100%',
      height: '600px',
      textAlign: 'center',
      color: colors.darkBlue,
    }

    const headerStyle = {
      lineHeight: '44px',
      fontSize: this.wide ? '34px' : '22px',
      fontFamily: 'GothamRnd-Med',
      marginTop: '100px',
      textAlign: 'left',
      display: 'inline-block',
    };

    const introStyle = {
      maxWidth: '34%',
      minWidth: '260px',
      margin: '20px auto',
    };

    const aboutStyle = {
      minHeight: '680px',
      display: 'flex',
      justifyContent: 'space-around',
      flexWrap: 'wrap',
      margin: '20px auto',
      maxWidth: '960px',
    };

    const descriptionStyle = {
      display: 'flex',
      justifyContent: 'center',
      flexDirection: 'column',
      maxWidth: '300px',
      textAlign: 'center',
    };

    const consumersStyle = {
      minHeight: '500px',
      paddingTop: '70px',
      display: 'flex',
      justifyContent: 'space-around',
      flexWrap: 'wrap',
      textAlign: 'center',
      margin: '60px 0',
      color: colors.darkBlue,
      background: `linear-gradient(${colors.lightBlue}, white)`,
    };

    const contactStyle = {
      minHeight: '350px',
      maxWidth: '960px',
      margin: '0 auto',
      paddingTop: '50px',
      color: colors.darkBlue,
      textAlign: 'center',
    };

    const contactEntriesStyle = {
      display: 'flex',
      justifyContent: 'space-around',
      flexWrap: 'wrap'
    };

    const merchantInfoStyle = {
      backgroundColor: colors.darkBlue,
      minHeight: '300px',
      color: colors.lightBlue,
      textAlign: 'center',
      padding: '60px 15%',
    };

    return (
      <div>
        <ContactDialog open={this.state.dialogShow} close={this.toggleDialog} />
        <Header home />
        <div style={introHeadStyle}>
          <p style={headerStyle}>
            Seamless Consumer Experience<br />
            Endless Opportunities</p>
          <p style={introStyle}>
            Ferly provides a simplified and integrated merchant to consumer
            experience for the purchase, exchange and redemption of gift value.
          </p>
          {this.renderButton("Learn More", "about")}
        </div>
        <div style={aboutStyle}>
          {this.renderScreenshot()}
          <div id='about' style={descriptionStyle}>
            <h2 style={{color: colors.darkBlue}}>About Ferly</h2>
            <p style={{color: colors.lightBlue, margin: '20px 0'}}>
              Our platform captures critical consumer gift card purchase
              information, assigns gift card issuer and holder value, enables
              exchange, leverages existing debit functionality
              for redemption, and streamlines user experience through a
              singular card and mobile app.
            </p>
            <div>
              <img
                onClick={(e) => this.scrollTo('why')}
                src={chevron}
                alt=""
                width={45}
                style={{transform: 'rotate(90deg)', cursor: 'pointer'}} />
            </div>
          </div>
        </div>
        <div  id='why' style={merchantInfoStyle}>
          <h3 style={{fontFamily: 'GothamRnd-Light'}}>
            Why merchants choose our data-centric technology
          </h3>
          <p style={{maxWidth: '260px', display: 'inline-block'}}>
            Ferly allows merchants the tools and flexibility to maintain a
            data-rich gift distribution program that is inexpensive and tailored
            for their brand. Ferly takes the complex world of gift distribution
            and wraps it into a single solution convenient for merchants and
            consumers alike.
          </p>
        </div>
        {this.renderMerchantSection()}
        <div id='consumers' style={consumersStyle}>
          {this.renderConsumersSection()}
        </div>
        <div id='contact' style={contactStyle}>
          <h2>Contact Us</h2>
          <div style={contactEntriesStyle}>
            {this.renderContact(email, "info@ferly.com")}
            {this.renderContact(mail,
              <p>481 E 1000 S Suite B<br />Pleasant Grove, UT 84062-3623</p>)}
            {this.renderContact(call, "801-839-4010")}
          </div>
        </div>
        <Footer />
      </div>
    );
  }
}

export default withStyles(styles)(Home);
