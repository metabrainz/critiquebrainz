const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CleanWebpackPlugin = require('clean-webpack-plugin');
var ManifestPlugin = require('webpack-manifest-plugin');

module.exports = {
  entry: {
    main: path.resolve(__dirname, 'critiquebrainz/frontend/static/scripts/main.js'),
    common: path.resolve(__dirname, 'critiquebrainz/frontend/static/scripts/common.js'),
    leaflet: path.resolve(__dirname, 'critiquebrainz/frontend/static/scripts/leaflet.js'),
    rating: path.resolve(__dirname, 'critiquebrainz/frontend/static/scripts/rating.js'),
    spotify: path.resolve(__dirname, 'critiquebrainz/frontend/static/scripts/spotify.js'),
    "wysiwyg-editor": path.resolve(__dirname, 'critiquebrainz/frontend/static/scripts/wysiwyg-editor.js'),
  },
  output: {
    path: path.resolve(__dirname, 'critiquebrainz/frontend/static/build/'),
    filename: '[name].[hash].js',
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
          loader: "style-loader"
        },
        {
          loader: MiniCssExtractPlugin.loader
        }, 
        {
          loader: "css-loader",
          options: {
            url: false 
          }
        },
        {
          loader: "less-loader",
          options: {
            relativeUrls: false
          }
        }
      ]
    }
    ]
  },
  plugins: [
  new MiniCssExtractPlugin({
    filename: '[name].[hash].css',
    chunkFilename: '[id].css'
  }),
  new CleanWebpackPlugin(),
  new ManifestPlugin()
  ]
};
