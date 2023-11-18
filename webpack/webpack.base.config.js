const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const BundleTracker = require('webpack-bundle-tracker');
const path = require('path');

const PUBLIC_PATH = process.env.PUBLIC_PATH;
const BUILD_DIR = process.env.BUILD_DIR;

if (!PUBLIC_PATH) throw Error('Missing PUBLIC_PATH in env.');
if (!BUILD_DIR) throw Error('Missing BUILD_DIR in env.');

console.log(`BUILD_DIR=${BUILD_DIR}`)
console.log(`PUBLIC_PATH=${PUBLIC_PATH}`)

module.exports = {
    mode: 'production',
    entry: {
        main: [
            path.join(__dirname, './src/main.js')
        ],
        jquery: [
            path.join(__dirname, './src/jquery.js')
        ],
    },
    output: {
        publicPath: PUBLIC_PATH,
        path: BUILD_DIR,
        filename: '[name].[chunkhash:8].js',
        chunkFilename: "[id]-[chunkhash].js",
    },
    optimization: {
        runtimeChunk: true,
        splitChunks: {


        }
    },
    module: {
        rules: [
            {
                test: /\.(svg|gif|jpg|png|woff|woff2|eot|ttf)$/,
                use: [
                    {
                        loader: 'url-loader',
                        options: {
                            name: 'assets/[name]-[hash:6].[ext]',
                            limit: 10 * 1024, // inline smaller files in css (than 10kB)
                            esModule: false,
                        },
                    },
                ],
            },
            {
                test: /\.(jpg|png|gif|svg)$/,
                loader: 'image-webpack-loader',
                enforce: 'pre',
                options: {
                    bypassOnDebug: true,
                },
            },
            {
                test: /\.css$/i,
                include: path.resolve(__dirname, 'src'),
                use: [
                    MiniCssExtractPlugin.loader,
                    'css-loader',
                    {
                        loader: 'postcss-loader',
                        options: {
                            sourceMap: true,
                        },
                    },
                ],
            },
        ],
    },
    resolve: {
        modules: [
            'node_modules/',
        ],
        unsafeCache: true,
    },
    plugins: [
        new BundleTracker({
            path: BUILD_DIR,
            // https://github.com/django-webpack/webpack-bundle-tracker/issues/108
            filename: path.join(BUILD_DIR, 'webpack-stats.json'),
        }),
        new MiniCssExtractPlugin({
            filename: '[name].[chunkhash:8].css',
            chunkFilename: '[id].[chunkhash:8].css',
        }),
        // new MomentLocalesPlugin({
        //     localesToKeep: ['en', 'cs'],
        // }),
    ],
};
