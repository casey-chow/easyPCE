import React from 'react';
import { Provider } from 'react-redux';
import { Router, Route, IndexRoute, browserHistory } from 'react-router';

import Layout from '../pages/Layout';
import store from '../store';
import CourseView from '../pages/CourseView';

import './App.scss';

const App = () => (
    <Provider store={store}>
        <Router history={browserHistory}>
            <Route path="/" component={Layout}>
                <IndexRoute component={CourseView} />
            </Route>
        </Router>
    </Provider>
);

export default App;
