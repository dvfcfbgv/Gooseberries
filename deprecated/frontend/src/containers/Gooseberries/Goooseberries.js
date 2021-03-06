import React, { Component } from 'react'
import { Route, Redirect, Switch } from 'react-router-dom'

import Home from './Home/Home'
import Login from './Login/Login'
import Logout from './Logout/Logout'
import Post from './Post/Post'
import Profile from './Profile/Profile'
import Register from './Registration/Register/Register'
import MoreInfo from './Registration/MoreInfo/MoreInfo'
// import Thread from './Thread/Thread'
import Toolbar from '../../components/Navigation/Toolbar/Toolbar'
import RouteListener from '../../hoc/RouteListener/RouteListener'
import { AUTH_TOKEN } from '../../constants'

class Gooseberries extends Component {
	state = {
		auth: false
	}

	componentDidMount() {
		this.handleAuth()
	}

	handleAuth = () => {
		if (localStorage.getItem(AUTH_TOKEN)) this.setState({ auth: true })
		else this.setState({ auth: false })
	}

	handleSideMenu = () => {
		this.setState({ showMenu: !this.state.showMenu })
	}

	render() {
		return (
			<div>
				<Toolbar
					isLoggedIn={this.state.auth}
					handleLogo={this.handleLogo}
					sideButtonClick={this.handleSideMenu}
				/>
				<RouteListener checkAuth={this.handleAuth}>
					<Switch>
						<Route
							path="/home"
							render={routeProps => (
								<Home {...routeProps} showMenu={this.state.showMenu} />
							)}
						/>
						<Route path="/login" component={Login} />
						<Route path="/logout" component={Logout} />
						<Route path="/profile/:userId" component={Profile} />
						<Route path="/register" exact component={Register} />
						<Route path="/register/moreinfo" component={MoreInfo} />
						<Route path="/post/:postId" component={Post} />
						{/* To catch all other undefined routes: */}
						<Route path="/" render={() => <Redirect to="/home" />} />
					</Switch>
				</RouteListener>
			</div>
		)
	}
}

export default Gooseberries
