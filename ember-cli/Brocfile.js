/* global require, module */

var EmberApp = require('ember-cli/lib/broccoli/ember-app');

var app = new EmberApp();
var mergeTrees = require('broccoli-merge-trees');
var pickFiles = require('broccoli-static-compiler');

// Use `app.import` to add additional libraries to the generated
// output files.
//
// If you need to use different assets in different
// environments, specify an object as the first parameter. That
// object's keys should be the environment name and the values
// should be the asset to use in that environment.
//
// If the library that you are including contains AMD or ES6
// modules that you would like to import into your application
// please specify an object with the list of modules as keys
// along with the exports of each module as its value.

var jqueryUiImages = pickFiles('bower_components/jquery-ui/themes/smoothness', { srcDir: 'images', destDir: 'assets/images' });

app.import('bower_components/jquery-ui/jquery-ui.min.js');
app.import('bower_components/jquery-ui/themes/smoothness/jquery-ui.min.css');

app.import('bower_components/bootstrap/dist/js/bootstrap.min.js');
app.import('bower_components/bootstrap/dist/css/bootstrap.min.css');

module.exports = mergeTrees([app.toTree(), jqueryUiImages]);
