import React from 'react';
import { AppContainer } from 'react-hot-loader';

import ReactDOM from 'react-dom';

import 'jquery';
import 'bootstrap';

import '../scss/application.scss';

import App from './components/App';

const container = document.getElementById('container');

const render = (Component) => {
    ReactDOM.render(
        <AppContainer>
            <Component />
        </AppContainer>,
    container);
};

render(App);

// Hot Module Replacement API
if (module.hot) {
  module.hot.accept('./components/App', () => {
    render(App)
  });
}
