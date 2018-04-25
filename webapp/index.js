import { Component } from 'preact';
import linkState from 'linkstate';

import './style';
import Sources from './components/sources';
import Topnav from './components/topnav';
import Home from './components/home';


export default class App extends Component {
  constructor() {
    super();

    this.state = {
      nav: {
        home: true,
        passwords: false,
        questions: false
      },
    }
    this.toggleNav = this.toggleNav.bind(this);
  }

  toggleNav(item) {
    let nav = Object.assign({}, ...Object.keys(this.state.nav).map(k => ({[k]: false})));
    this.setState({
      nav: Object.assign({}, nav, {
        [item]: true
      })
    });
  }

	render({}, {nav}) {
		return (<div class="column">
      <Topnav nav={this.state.nav} toggleNav={this.toggleNav} />

      <div class="main-cont">
        { nav.home === true ? <Home /> : null }
        { nav.questions === true ? <Sources /> : null }
      </div>
		</div>);
	}
}
