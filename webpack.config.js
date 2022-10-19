const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const { WebpackManifestPlugin } = require('webpack-manifest-plugin');


const frontEndStaticDir = path.resolve(__dirname, 'critiquebrainz/frontend/static');

module.exports = (env, argv) => {
  const isProd = argv.mode == 'production';
  return {
    mode: argv.mode,
    entry: {
      'main': path.resolve(frontEndStaticDir, 'scripts/main.js'),
      'common': path.resolve(frontEndStaticDir, 'scripts/common.js'),
      'leaflet': path.resolve(frontEndStaticDir, 'scripts/leaflet.js'),
      'rating': path.resolve(frontEndStaticDir, 'scripts/rating.js'),
      'spotify': path.resolve(frontEndStaticDir, 'scripts/spotify.js'),
      'wysiwyg-editor': path.resolve(frontEndStaticDir, 'scripts/wysiwyg-editor.js'),
    },
    output: {
      path: path.resolve(frontEndStaticDir, 'build/'),
      filename: isProd ? '[name].[contenthash].js' : '[name].js',
      publicPath: '',
    },
    module: {
      rules: [
      {
        test: /\.(js)$/,
        exclude: /node_modules/,
        use: [
          {
            loader: 'babel-loader'
          }
        ]
      },
      {
        test: /\.less$/,
        use: [
          {
            loader: 'style-loader'
          },
          {
            loader: MiniCssExtractPlugin.loader,
            options: {
              esModule: false,
            },
          },
          {
            loader: 'css-loader',
            options: {
              url: false
            }
          },
          {
            loader: 'less-loader',
            options: {
              lessOptions: {
                relativeUrls: false
              }
            }
          }
        ]
      }
      ]
    },
    plugins: [
      new MiniCssExtractPlugin({
        filename: isProd ? '[name].[contenthash].css' : '[name].css',
        chunkFilename: '[name].[contenthash].css'
      }),
      new WebpackManifestPlugin()
    ]
  }
};
