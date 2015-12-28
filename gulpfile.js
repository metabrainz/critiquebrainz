var gulp = require('gulp'),
	less = require('gulp-less'),
	concat = require('gulp-concat'),
   	uglify = require('gulp-uglify'),
   	minifyCss = require("gulp-minify-css");

gulp.task('less', function() {
	gulp.src('critiquebrainz/frontend/static/css/*.less')
		.pipe(less())
   	  	.pipe(concat('bundle.css'))
   	 	.pipe(minifyCss())
 	    .pipe(gulp.dest('critiquebrainz/frontend/static/build/'))
});

gulp.task('external', function () {
	gulp.src(['critiquebrainz/frontend/static/js/!(bootstrap.min)*.js','critiquebrainz/frontend/static/js/boostrap.min.js'])
		.pipe(concat('bundle.js'))
		.pipe(uglify())
		.pipe(gulp.dest('critiquebrainz/frontend/static/build/'))
});

gulp.task('default', ['less', 'external']);
