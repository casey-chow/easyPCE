/* Webpack configuration for a hot-reloading server.
 * To use, run `npm run watch`.
 */
const path = require('path');
const webpack = require('webpack');
const BundleTracker = require('webpack-bundle-tracker');

const config = require('./local.config.js');

config.entry = [
    // WebpackDevServer host and port
    'webpack-dev-server/client?http://0.0.0.0:3000',

    // "only" prevents reload on syntax errors
    'webpack/hot/only-dev-server',

    // app entry point
    './static/js/index',
];

// override django's STATIC_URL for webpack bundles
config.output.publicPath = 'http://localhost:3000/static/bundles/';

// Add HotModuleReplacementPlugin and BundleTracker plugins
config.plugins = config.plugins.concat([
    new webpack.HotModuleReplacementPlugin(),
    new webpack.NoErrorsPlugin(),
    new BundleTracker({ filename: './webpack-stats.json' }),
]);

// add a loader for JSX files with react-hot enabled
config.module.loaders.push({
    // use the following loaders on all .js and .jsx files
    test: /\.jsx?$/,

    // use the react hot loader
    loaders: [
        'react-hot',
        'babel-loader',
    ],

    // include everything in js
    include: path.resolve(__dirname, '../static/js'),
});

module.exports = config;
