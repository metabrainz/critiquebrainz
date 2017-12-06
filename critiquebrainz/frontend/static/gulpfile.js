let _ = require('lodash');
let fs = require('fs');
let gulp = require('gulp');
let less = require('gulp-less');
let path = require('path');
let rev = require('gulp-rev');
let source = require('vinyl-source-stream');
let streamify = require('gulp-streamify');
let through2 = require('through2');
let Q = require('q');
let yarb = require('yarb');

const CACHED_BUNDLES = new Map();
const STATIC_DIR = path.resolve(__dirname, '../static');
const BUILD_DIR = path.resolve(STATIC_DIR, 'build');
const STYLES_DIR = path.resolve(STATIC_DIR, 'styles');
const SCRIPTS_DIR = path.resolve(STATIC_DIR, 'scripts');

const revManifestPath = path.resolve(BUILD_DIR, 'rev-manifest.json');
const revManifest = {};

if (fs.existsSync(revManifestPath)) {
  _.assign(revManifest, JSON.parse(fs.readFileSync(revManifestPath)));
}

function writeManifest() {
  fs.writeFileSync(revManifestPath, JSON.stringify(revManifest));
}

function writeResource(stream) {
  let deferred = Q.defer();

  stream
    .pipe(streamify(rev()))
    .pipe(gulp.dest(BUILD_DIR))
    .pipe(rev.manifest())
    .pipe(through2.obj(function (chunk, encoding, callback) {
      _.assign(revManifest, JSON.parse(chunk.contents));
      callback();
    }))
    .on('finish', function () {
      deferred.resolve();
    });

  return deferred.promise;
}

function buildStyles() {
  return writeResource(
    gulp.src(path.resolve(STYLES_DIR, '*.less'))
    .pipe(less({
      rootpath: '/static/',
      relativeUrls: true,
      plugins: [
        new (require('less-plugin-clean-css'))({compatibility: 'ie8'})
      ]
    }))
  ).done(writeManifest);
}

function transformBundle(bundle) {
  bundle.transform('babelify');
  bundle.transform('envify', {global: true});
  return bundle;
}

function runYarb(resourceName, callback) {
  if (resourceName in CACHED_BUNDLES) {
    return CACHED_BUNDLES.get(resourceName);
  }

  let bundle = transformBundle(yarb(path.resolve(SCRIPTS_DIR, resourceName), {
    debug: false // disable sourcemaps
  }));

  if (callback) {
    callback(bundle);
  }

  CACHED_BUNDLES.set(resourceName, bundle);
  return bundle;
}

function bundleScripts(b, resourceName) {
  return b.bundle().on('error', console.log).pipe(source(resourceName));
}

function writeScript(b, resourceName) {
  return writeResource(bundleScripts(b, resourceName));
}

function buildScripts() {
  process.env.NODE_ENV = String(process.env.DEVELOPMENT_SERVER) === '1' ? 'development' : 'production';

  let commonBundle = runYarb('common.js');
  let leafletBundle = runYarb('leaflet.js', function (b) {
    b.external(commonBundle);
  });
  let spotifyBundle = runYarb('spotify.js', function (b) {
    b.external(commonBundle);
  });
  let ratingBundle = runYarb('rating.js', function (b) {
    b.external(commonBundle);
  });
  let wysiwygBundle = runYarb('wysiwyg-editor.js', function(b) {
    b.external(commonBundle)
  });

  return Q.all([
    writeScript(commonBundle, 'common.js'),
    writeScript(leafletBundle, 'leaflet.js'),
    writeScript(spotifyBundle, 'spotify.js'),
    writeScript(ratingBundle, 'rating.js'),
    writeScript(wysiwygBundle, 'wysiwyg-editor.js'),
  ]).then(writeManifest);
}

gulp.task('styles', buildStyles);
gulp.task('scripts', buildScripts);

gulp.task('default', ['styles', 'scripts']);
