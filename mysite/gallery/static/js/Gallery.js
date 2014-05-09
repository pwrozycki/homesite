Gallery = (function () {
    var NUMBER_OF_PRELOADED_ADJACENT_IMAGES = 10;

    var browserTemplate = Handlebars.compile($("#browser-template").html()),
        currentImage = null,
        $browserNotYetLoadedImages,
        json,
        listdirRoot,
        preloads = [],
        imgLoading = null;

    function scrollToImage(imageIndex) {
        var $returnImage = $('.thumbnail-image[data-index=' + imageIndex + ']');
        $(window).scrollTop($returnImage.position().top + $returnImage.height() / 2 - $(window).height() / 2);
    }

    function switchToPreviousImage() {
        showImagePreview(currentImage - 1);
    }

    function switchToNextImage() {
        showImagePreview(currentImage + 1);
    }

    function returnToBrowseMode() {
        preloads = [];
        imgLoading = null;

        $("#preview").hide();
        $("#browser").show();

        removeKeyEventHandlers();
        scrollToImage(currentImage);
    }

    function enterPreviewMode(imageIndex) {
        $("#browser").hide();

        var $preview = $("#preview");
        $preview.find("img").remove();
        $preview.show();

        showImagePreview(imageIndex);
        setKeyEventHandlers();
    }

    function setKeyEventHandlers() {
        $(window).keyup(function (event) {
            // left arrow
            if (event.which == 37) {
                switchToPreviousImage();
                // right arrow
            } else if (event.which == 39) {
                switchToNextImage();
                // up arrow or escape key
            } else if (event.which == 38 || event.which == 27) {
                returnToBrowseMode();
            }
        });
    }

    function removeKeyEventHandlers() {
        $(window).unbind("keyup");
    }

    function setupEventHandlers() {
        $(document).on("click", ".thumbnail-image", function () {
            enterPreviewMode(parseInt($(this).attr('data-index')));
        });

        $(".prevImage").click(function () {
            switchToPreviousImage();
        });

        $(".nextImage").click(function () {
            switchToNextImage();
        });

        $(".browseImage").click(function () {
            returnToBrowseMode();
        });


        $(document).on("click", ".directory-link", function () {
            changeDirectory(listdirRoot + $(this).attr('data-path'));
        });
    }

    function getNextPreloadedImageIndex(number) {
        if (number == 0) {
            return currentImage;
        } else if (number % 2 == 1) {
            return currentImage + (number - 1) / 2 + 1;
        } else {
            return currentImage - number / 2;
        }
    }

    function onLoad(currentImageAtThatTime, number, $img) {
        if (!$("#preview").is(":hidden") || currentImageAtThatTime != currentImage) {
            if (number == 0) {
                var $preview = $("#preview-image");
                $preview.html($img);
                $preview.append($("<span/>"));
            }

            loadNextImage(number + 1);
        }
    }

    function loadNextImage(number) {
        // preload up to 'NOPAI' adjacent images
        if (number > NUMBER_OF_PRELOADED_ADJACENT_IMAGES) {
            return;
        }

        // translate number of adjacent image to index in preloads array
        // 0 -> currentImage; 1 -> currentImage + 1; 2 -> currentImage - 1; 3 -> currentImage + 2 (and so on)
        var realNumber = getNextPreloadedImageIndex(number);

        // start preloading image if index is correct and image isn't already loaded
        if (realNumber >= 0 && realNumber < preloads.length) {
            if (preloads[realNumber].preloadImg == null) {
                preloads[realNumber].preloadImg = $('<img/>', { src: preloads[realNumber].url});
            }

            var $img = preloads[realNumber].preloadImg;

            imgLoading = $img;
            $img.one("load",function () {
                onLoad(currentImage, number, $img);
            }).each(function () {
                if (this.complete) {
                    $(this).load();
                }
            });
        } else {
            // preload next image in order
            loadNextImage(number + 1);
        }
    }

    function showImagePreview(imageIndex) {
        if (imageIndex < 0 || imageIndex >= json.images.length) {
            return;
        }

        // set current image
        currentImage = imageIndex;

        // load current image
        if (preloads.length == 0) {
            $.each(json.images, function (index, element) {
                preloads.push({ index: index, url: element.preview, preloadImg: null });
            });
        }

        // unbind load event for currently loading image
        if (imgLoading != null) {
            imgLoading.unbind("load");
        }

        // start preload for adjacent images
        loadNextImage(0);
    }

    function showVisibleImages() {
        $browserNotYetLoadedImages = $.grep($browserNotYetLoadedImages, function (el) {
            var imgRect = el.getBoundingClientRect();
            if (imgRect.bottom >= 0 && imgRect.top <= window.innerHeight) {
                var $this = $(el);
                $this.attr("src", $this.attr('data-src'));
                return false;
            }
            return true;
        });
    }

    function changeDirectory(directory) {
        return $.getJSON(directory, function (data) {
            json = data;

            /* show browser */
            var $browserDiv = $("#browser");
            $browserDiv.html(browserTemplate(json));
            $browserNotYetLoadedImages = $browserDiv.find("img");
            showVisibleImages();
        });
    }

    return {
        init: function (listDirRoot, startingDirectory) {
            listdirRoot = listDirRoot;

            setupEventHandlers();
            changeDirectory(startingDirectory);
        },
        showVisibleImages: showVisibleImages
    }
})();

$(window).scroll(function () {
    if (!$("#browser").is(":hidden")) {
        Gallery.showVisibleImages();
    }
});