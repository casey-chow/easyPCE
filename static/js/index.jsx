import React from 'react';
import { Router, Route, IndexRoute, hashHistory } from "react-router";
import $ from 'jquery';
import ReactDOM from 'react-dom';

import Layout from "./pages/Layout";
import CourseView from "./pages/CourseView";

const container = document.getElementById('container');

ReactDOM.render(
    <Router history={hashHistory}>
        <Route path="/" component={Layout}>
            <IndexRoute component={CourseView}></IndexRoute>
        </Route>
    </Router>, 
    container);
