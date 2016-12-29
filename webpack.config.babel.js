import path from 'path';
import webpack from 'webpack';
import BundleTracker from 'webpack-bundle-tracker';

export default {
    // the base directory (absolute path) for resolving the entry option
    context: __dirname,

    // the entry point for the client-side application
    entry: './static/js/index',

    output: {
        // where you want your compiled bundle to be stored
        path: path.resolve('./static/bundles/'),

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
        loaders: [{
            // use the following loaders on all .js and .jsx files
            test: /\.jsx?$/,

            // do not transpile node_modules
            exclude: ['node_modules'],

            // use the babel loader
            loader: 'babel-loader',

            // specify that we will be dealing with React code
            query: { presets: ['react'] },
        }],
    },

    resolve: {
        // tells webpack where to look for modules
        modulesDirectories: ['node_modules'],

        // extensions that should be used to resolve modules
        extensions: ['', '.js', '.jsx'],
    },

    // create source maps for the bundle
    devtool: 'source-map',
};
