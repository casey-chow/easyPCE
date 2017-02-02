const webpack = require('webpack');
const BundleTracker = require('webpack-bundle-tracker');

const config = require('./common.config.js');

config.devtool = 'source-map';

config.plugins = config.plugins.concat([
    new BundleTracker({ filename: './webpack-stats-prod.json' }),

    // remove debugging code
    new webpack.DefinePlugin({
        'process.env': {
            NODE_ENV: JSON.stringify('production'),
        },
    }),

    // minify
    new webpack.optimize.UglifyJsPlugin({
        compress: {
            warnings: false,
        },
    }),
]);

module.exports = config;
