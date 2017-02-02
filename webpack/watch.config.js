/* Webpack configuration for a hot-reloading server.
 * To use, run `npm run watch`.
 */
const path = require('path');
const webpack = require('webpack');
const BundleTracker = require('webpack-bundle-tracker');

const config = require('./local.config.js');

config.entry = [
    'react-hot-loader/patch',

    // WebpackDevServer host and port
    'webpack-dev-server/client?http://0.0.0.0:3000',

    // "only" prevents reload on syntax errors
    'webpack/hot/only-dev-server',

    // app entry point
    './static/src/index',
];

config.devServer = {
    hot: true,
    // enable HMR on the server

    contentBase: path.resolve(__dirname, 'dist'),
    // match the output path

    publicPath: '/'
    // match the output `publicPath`
};

// override django's STATIC_URL for webpack bundles
config.output.publicPath = 'http://localhost:3000/static/bundles/';

// Add HotModuleReplacementPlugin and BundleTracker plugins
config.plugins = config.plugins.concat([
    new webpack.HotModuleReplacementPlugin(),
    new webpack.NoEmitOnErrorsPlugin(),
    new BundleTracker({ filename: './webpack-stats.json' }),
]);

module.exports = config;
