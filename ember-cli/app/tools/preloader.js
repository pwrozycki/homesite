import Ember from 'ember';

var $ = Ember.$;

export default {
    // TODO: fix after moving from image.js
    setupImagePreloading: function (newImageIndex, sign) {
        var images = this.get('images');

        // Calculate paths of images that should be preloaded
        var newPreviewPaths = new Ember.Set();
        for (var i = 0; Math.abs(i) < 10; i += sign) {
            var preloadIndex = newImageIndex + i;
            if (preloadIndex >= 0 && preloadIndex < images.get('length')) {
                newPreviewPaths.add(images.objectAt(preloadIndex).get('preview'));
            }
        }

        $("#preloads").find("img").each(function (index, item) {
            var previewPath = $(item).attr('src');

            // Remove img objects that should no longer be in preloaded
            // Remove paths from set, if corresponding img object already exists
            if (!newPreviewPaths.contains(previewPath)) {
                $(this).remove();
            } else {
                newPreviewPaths.remove(previewPath);
            }
        });

        var $previewImg = $("#preview-image").find("> img");
        $previewImg.unbind('load');
        $previewImg.bind('load', function () {
            // Add img object if there is no corresponding preload for path
            newPreviewPaths.forEach(function (item) {
                $("#preloads").append($("<img>", { src: item }));
            });
        });
    }
};