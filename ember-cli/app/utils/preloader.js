import Ember from 'ember';

var $ = Ember.$;

export default {
    /**
     * Array that holds jquery <img> references for preloaded images.
     */
    preloadImages: [],

    /**
     * Preload images from images argument, starting with newImageIndex, advancing up (sign == 1)
     * or down (sign == -1).
     */
    setupImagePreloading: function (images, newImageIndex) {
        var self = this;

        var newPreviewPaths = this.getNewPaths(images, newImageIndex);

        this.updatePreloadsArray(newPreviewPaths);

        var $previewImg = $("#preview-image").find("> img");
        $previewImg.unbind('load');
        // fetch preloads AFTER image is loaded.
        $previewImg.bind('load',
            function () {
                newPreviewPaths.forEach(function (item) {
                    self.preloadImages.push($("<img>", { src: item }));
                });
            });
    },

    /**
     * Calculate paths of images that should be preloaded.
     */
    getNewPaths: function (images, newImageIndex) {
        var newPreviewPaths = [];

        // get indices in following order 1, -1, 2, -2, 3, -3 relative to newImageIndex
        for (var i = 0; Math.abs(i) < 10; i += 1) {
            var sign = i%2 === 0 ? 1 : -1;
            var preloadIndex = newImageIndex + (Math.floor(i/2)+1) * sign;

            if (preloadIndex >= 0 && preloadIndex < images.get('length')) {
                newPreviewPaths.push(images.objectAt(preloadIndex).get('preview'));
            }
        }

        return newPreviewPaths;
    },

    /**
     * Update array of preloaded images. Leave only images that exist in newPreviewPaths.
     * Destroy jquery refs for images not in newPreviewPaths.
     */
    updatePreloadsArray: function (newPreviewPaths) {
        this.preloadImages = this.preloadImages.filter(function (item) {
            var previewPath = $(item).attr('src');

            if (!newPreviewPaths.contains(previewPath)) {
                $(item).remove();
                return false;
            } else {
                newPreviewPaths.removeObject(previewPath);
                return true;
            }
        });
    }
};