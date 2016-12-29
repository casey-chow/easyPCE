/* eslint-disable */

// Server to enable React hot code reloading
// http://owaislone.org/blog/webpack-plus-reactjs-and-django/

const webpack = require('webpack');
const WebpackDevServer = require('webpack-dev-server');
const config = require('./webpack/watch.config');

const server = new WebpackDevServer(webpack(config), {
      publicPath: config.output.publicPath,
      hot: true,
      inline: true,
      historyApiFallback: true,
});

server.listen(3000, '0.0.0.0', function (err) {
    if (err) {
        console.log(err);
    }

    console.log('Listening at 0.0.0.0:3000');
});