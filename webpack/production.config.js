const path = require('path');
const webpack = require('webpack');
const BundleTracker = require('webpack-bundle-tracker');

const config = require('./common.config.js');

// export to dist directory during production
config.output.path = path.resolve(__dirname, '../assets/dist');

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

// Add a loader for JSX files
config.module.loaders.push({
    test: /\.jsx?$/,
    exclude: /node_modules/,
    loader: 'babel-loader',
});

module.exports = config;
