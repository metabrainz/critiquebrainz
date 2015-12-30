var _ = require('lodash');
var fs = require('fs');
var gulp = require('gulp');
var less = require('gulp-less');
var path = require('path');
var rev = require('gulp-rev');
var source = require('vinyl-source-stream');
var streamify = require('gulp-streamify');
var through2 = require('through2');
var Q = require('q');
var yarb = require('yarb');

const CACHED_BUNDLES = new Map();
const STATIC_DIR = path.resolve(__dirname, '../static');
const BUILD_DIR = path.resolve(STATIC_DIR, 'build');
const STYLES_DIR = path.resolve(STATIC_DIR, 'css');
const SCRIPTS_DIR = path.resolve(STATIC_DIR, 'js');

const revManifestPath = path.resolve(BUILD_DIR, 'rev-manifest.json');
const revManifest = {};

if (fs.existsSync(revManifestPath)) {
  _.assign(revManifest, JSON.parse(fs.readFileSync(revManifestPath)));
}

function writeManifest() {
  fs.writeFileSync(revManifestPath, JSON.stringify(revManifest));
}

function writeResource(stream) {
  var deferred = Q.defer();

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

  var bundle = transformBundle(yarb(path.resolve(SCRIPTS_DIR, resourceName), {
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

  var commonBundle = runYarb('common.js');
  var leafletBundle = runYarb('leaflet.js');
  var logBundle = runYarb('log.js', function (b) {
    b.external(commonBundle);
  });
  var eventBundle = runYarb('event.js', function (b) {
    b.external(leafletBundle);
  });
  var macrosBundle = runYarb('macros.js');
  var reportBundle = runYarb('report.js', function (b) {
    b.external(commonBundle);
  });
  var reviewBaseBundle = runYarb('reviewBase.js', function (b) {
    b.external(commonBundle);
  });
  var revisionBundle = runYarb('revision.js', function (b) {
    b.external(commonBundle);
  });
  var searchIndexBundle = runYarb('searchIndex.js', function (b) {
    b.external(commonBundle);
  });
  var searchSelectorBundle = runYarb('searchSelector.js', function (b) {
    b.external(commonBundle);
  });
  var spotifyBundle = runYarb('spotify.js', function (b) {
    b.external(commonBundle);
  });

  return Q.all([
    writeScript(commonBundle, 'common.js'),
    writeScript(leafletBundle, 'leaflet.js'),
    writeScript(logBundle, 'log.js'),
    writeScript(eventBundle, 'event.js'),
    writeScript(macrosBundle, 'macros.js'),
    writeScript(reportBundle, 'report.js'),
    writeScript(reviewBaseBundle, 'reviewBase.js'),
    writeScript(revisionBundle, 'revision.js'),
    writeScript(searchIndexBundle, 'searchIndex.js'),
    writeScript(searchSelectorBundle, 'searchSelector.js'),
    writeScript(spotifyBundle, 'spotify.js')
  ]).then(writeManifest);
}

gulp.task('styles', buildStyles);
gulp.task('scripts', buildScripts);

gulp.task('default', ['styles', 'scripts']);
