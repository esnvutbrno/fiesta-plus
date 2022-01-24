const path = require('path');
const publicPath = process.env.PUBLIC_PATH || 'https://webpack.localhost/';
const buildDir = process.env.BUILD_DIR;

if (!buildDir) throw Error('Missing BUILD_DIR in env.');

console.log('Build dir: ', buildDir);

const BundleTracker = require('webpack-bundle-tracker');

module.exports = {
    optimization: {
        splitChunks: {
            name: 'common',
            chunks: 'all',
        },
        runtimeChunk: {
            name: 'vendor',
        },
    },
    entry: {
        main: path.join(__dirname, './src/main.css'),
        // login: path.join(__dirname, './src/js/pages/Login/login.ts'),
    },
    output: {
        publicPath,
        path: buildDir,
        // TODO: found out about chunkhash/contenthash
        filename: '[name].[fullhash:8].js',
    },
    module: {
        rules: [
            {
                test: /\.(svg|gif|jpg|png|woff|woff2|eot|ttf)$/,
                use: [
                    {
                        loader: 'url-loader',
                        options: {
                            name: 'assets/[name]-[hash:12].[ext]',
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
                use: ['style-loader', 'css-loader', 'postcss-loader'],
            },
        ],
    },
    resolve: {
        modules: [
            // path.resolve(__dirname, './src/'),
            'node_modules/',
        ],
        extensions: ['.js', '.ts'],
        unsafeCache: true,
    },
    plugins: [
        new BundleTracker({
            path: buildDir,
            // https://github.com/django-webpack/webpack-bundle-tracker/issues/108
            filename: path.join(buildDir, 'webpack-stats.json'),
        }),
        // new MiniCssExtractPlugin({
        //     filename: '[name].[hash:8].css',
        //     chunkFilename: '[id].[hash:8].css',
        //     ignoreOrder: true, // vuetify-plugin/loader problem
        // }),
        // new MomentLocalesPlugin({
        //     localesToKeep: ['en', 'cs'],
        // }),
    ],
};
