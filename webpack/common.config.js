const path = require('path');
const webpack = require('webpack');
const BundleTracker = require('webpack-bundle-tracker');

module.exports = {
    // the base directory (absolute path) for resolving the entry option
    context: path.dirname(__dirname),

    devtool: 'cheap-module-eval-source-map',

    // the entry point for the client-side application
    entry: './static/src/index',

    output: {
        // where you want your compiled bundle to be stored
        path: path.resolve(__dirname, '../dist/'),

        // naming convention webpack should use for outputtedfiles
        filename: '[name]-[hash].js',
    },

    plugins: [
        // tells webpack where to store data about your bundles
        new BundleTracker({
            filename: './webpack-stats.json',
        }),

        // makes jQuery available in every module
        new webpack.ProvidePlugin({
            $: 'jquery',
            jQuery: 'jquery',
            'window.jQuery': 'jquery',
        }),
    ],

    module: {
        rules: [
            {
                // use the following loaders on all .js and .jsx files
                test: /\.jsx?$/,

                // do not transpile node_modules
                exclude: /node_modules/,

                // use the babel loader
                use: [
                    'babel-loader',
                ],
            },
            {
                // load scss styles in
                test: /\.scss$/,
                exclude: /node_modules/,
                use: [
                    'style-loader',
                    'css-loader?sourceMap',
                    'sass-loader?sourceMap&sourceComments',
                ]
            },
            {
                // inline base64 URLs for <=8k images, direct URLs for the rest
                test: /\.(png|jpg)$/,
                loader: 'url-loader?limit=8192',
            },
            {
                test: /\.(eot|svg|ttf|woff|woff2)$/,
                loader: 'file-loader?name=public/fonts/[name].[ext]',
            }
        ],
    },

    plugins: [
        new webpack.NamedModulesPlugin(),
        // prints more readable module names in the browser console on HMR updates
        new webpack.ProvidePlugin({
            $: 'jquery',
            jQuery: 'jquery',
        }),
    ],

    resolve: {
        // tells webpack where to look for modules
        modules: ['node_modules'],

        // extensions that should be used to resolve modules
        extensions: ['.js', '.jsx'],

        // do not enforce a .js(x) extension
        enforceExtension: false,
    },

    // create source maps for the bundle
    devtool: 'source-map',
};
