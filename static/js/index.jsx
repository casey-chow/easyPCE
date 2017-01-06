import React from 'react';
import { Router, Route, IndexRoute, hashHistory } from "react-router";
import $ from 'jquery';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';

import Layout from "./pages/Layout";
import CourseView from "./pages/CourseView";
import store from "./store"

const container = document.getElementById('container');

ReactDOM.render(
<Provider store ={store}>
    <Router history={hashHistory}>
        <Route path="/" component={Layout}>
            <IndexRoute component={CourseView}></IndexRoute>
        </Route>
    </Router> 
</Provider>, 
container);
