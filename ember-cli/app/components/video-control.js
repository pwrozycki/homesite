import Ember from 'ember';

/**
 * Fullscreen video on double click
 */
export default Ember.Component.extend({
    requestFullScreen: function (videoElement) {
        if (videoElement.requestFullscreen) {
            videoElement.requestFullscreen();
        } else if (videoElement.mozRequestFullScreen) {
            videoElement.mozRequestFullScreen();
        } else if (videoElement.webkitRequestFullscreen) {
            videoElement.webkitRequestFullscreen();
        }
    },

    actions: {
        fullscreen: function() {
            var videoElement = Ember.$(this.element).find('video')[0];
            this.requestFullScreen(videoElement);
        }
    }
});