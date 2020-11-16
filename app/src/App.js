import './App.css';
import GoogleBtn from './GoogleBtn';
import React, { Component } from 'react'
import Leaderboard from './leaderboard/Leaderboard'
import Puzzles from './puzzle/Puzzles'
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link
} from "react-router-dom";

class App extends Component {  
  constructor() {
    super()
    this.state = {
      accessToken: '',
    }
  }

  render() {
    const loggedIn = this.state.accessToken !== "";
    return (
      <Router>
        <div className="App" data-testid="app">
          <div className="header">
            <div className="title">Isshoni Sudoku</div>
            {loggedIn && (
              <div className="nav-item">
                <Link to="/mypuzzles">My Puzzles</Link>
              </div>
            )}
            {loggedIn && (
              <div className="nav-item">
                <Link to="/leaderboard">Leaderboard</Link>
              </div>
            )}
            <div className="login-btn" data-testid="login-btn">
              <GoogleBtn onAccessTokenChanged={accessToken => this.setState({accessToken})}/>
            </div>
          </div>
          <div className="page-content">
            {loggedIn ? (
              <Switch>
                <Route path="/mypuzzles">
                  <Puzzles accessToken={this.state.accessToken}/>
                </Route>
                <Route path="/leaderboard">
                  <Leaderboard accessToken={this.state.accessToken}/>
                </Route>
              </Switch>
            ):(
              <div>Please log in!</div>
            )}
          </div>
        </div>
      </Router>
    );
  }
}

export default App;
