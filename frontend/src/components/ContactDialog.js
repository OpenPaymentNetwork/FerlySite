import Button from 'material-ui/Button';
import TextField from 'material-ui/TextField';
import React, {Component} from 'react';
import Dialog, {
  DialogActions,
  DialogTitle,
  DialogContentText,
  DialogContent
} from 'material-ui/Dialog';
import { MuiThemeProvider } from 'material-ui/styles';
import {theme} from '../theme';
import {post} from '../fetch';

class ContactDialog extends Component {

  constructor(props) {
    super(props);
    this.state = {
      email: ''
    };
  }

  submit(e) {
    post('create-contact', {'email': this.state.email})
    this.props.close();
  }

  handleChange(e) {
    this.setState({email: e.target.value});
  }

  render() {
    return (
      <Dialog open={this.props.open}>
        <MuiThemeProvider theme={theme}>
          <DialogTitle>Subscribe</DialogTitle>
          <form onSubmit={this.submit.bind(this)} action="">
            <DialogContent>
              <DialogContentText>
                Enter your email address so you can receive important updates.
              </DialogContentText>
              <TextField
                  autoFocus
                  margin="dense"
                  id="name"
                  label="Email Address"
                  onChange={this.handleChange.bind(this)}
                  value={this.state.email}
                  type="email"
                  fullWidth />
            </DialogContent>
            <DialogActions>
              <Button onClick={this.props.close} color="primary">
                Cancel
              </Button>
              <Button type="submit" color="primary">
                Subscribe
              </Button>
            </DialogActions>
          </form>
        </MuiThemeProvider>
      </Dialog>
    );
  }
}

export default ContactDialog;
