import Ember from 'ember';

var $ = Ember.$;
var $window = $(window);

var THRESHOLD = 200;
var UPDATE_VIEWPORT_STEP = 200;
var FAILURE_LIMIT = 10;

export default Ember.Object.extend({

    elements: null,
    lastUpdateViewport: null,

    rebindEvents: function () {
        $window.unbind("resize");
        $window.unbind("scroll");
        $window.bind("resize", this.tryupdate.bind(this));
        $window.bind("scroll", this.tryupdate.bind(this));
    },

    /**
     * Setup lazy loader, by specifying array of DOM images that should be lazy loaded.
     */
    setImages: function (jqueryRefs) {
        this.rebindEvents();

        this.elements = [];
        this.lastUpdateViewport = null;

        var $this = this;
        jqueryRefs.each(function (index, item) {
            $this.elements.push($(item));
        });

        this.tryupdate();
    },

    /**
     * Show specified element i.e. replace src attribute with value assigned to data-original attribute.
     */
    showElement: function ($element) {
        var imageSrc = $element.attr("src");
        var imageUrl = $element.attr("data-original");

        // only show if image url is specified and hasn't been already assigned
        if (imageUrl && imageSrc !== imageUrl) {
            $("<img />")
                .bind("load", function () {
                    $element.attr("src", imageUrl);
                    $element.loaded = true;
                })
                .attr("src", imageUrl);
        }
    },

    /**
     * Show elements starting with firstElementIndex, increasing or decreasing indices.
     * (Until images end up outside viewport).
     */
    showElements: function (firstElementIndex, step) {
        var counter = 0;

        // iterate downwards or upwards (depending on step value)
        // show images to be loaded, until failure_limit counter is exceeded
        for (var i = firstElementIndex; i >= 0 && i < this.elements.length; i += step) {
            var $element = this.elements[i];

            if (!this.aboveTheTop($element) && !this.leftOfBegin($element) && !this.belowTheFold($element) && !this.rightToFold($element)) {

                // element in viewport - reset counter
                counter = 0;
                this.showElement($element);
            } else {
                // to many failures -> stop iterating
                if (++counter >= FAILURE_LIMIT) {
                    return;
                }
            }
        }
    },

    /**
     * Check if update should be started at all (viewport has been changed significantly).
     */
    tryupdate: function () {
        // Check if viewport change was significant enough to perform update
        // if not return
        if(this.lastUpdateViewport != null &&
            $window.scrollTop() > this.lastUpdateViewport.top - UPDATE_VIEWPORT_STEP &&
            $window.scrollTop() + $window.height() < this.lastUpdateViewport.bottom + UPDATE_VIEWPORT_STEP) {
            return;
        }

        // Update will be executed - store this viewport geometry for later reference
        this.lastUpdateViewport = { top: $window.scrollTop(), bottom: $window.scrollTop() + $window.height() };

        this.update();
    },

    /**
     * Find visible images applying binary search algorithm to detect visible images and show them.
     */
    update: function () {
        if (this.elements.length === 0) {
            // Elements are empty - nothing will be found anyway
            return;
        }

        /* Set initial values - lower and upper indices pointing at beginning and end of array */
        var lowerIndex = 0;
        var upperIndex = this.elements.length - 1;
        var testedIndex = 0;

        /* Binary search algorithm - test image in the middle of range: <lowerIndex, upperIndex>.
         Always look for middle value between lowerIndex and upperIndex */
        while (upperIndex > lowerIndex + 1) {
            testedIndex = lowerIndex + Math.floor((upperIndex - lowerIndex) / 2);
            var testedElement = this.elements[testedIndex];

            // testedIndex appears to be above viewport
            // there is no use testing smaller indices => lowerIndex = testedIndex
            if (this.aboveTheTop(testedElement) ||
                this.leftOfBegin(testedElement)) {
                lowerIndex = testedIndex;

                // testedIndex appears to be below viewport
                // there is no use testing bigger indices => upperIndex = testedIndex
            } else if (this.belowTheFold(testedElement) ||
                this.rightToFold(testedElement)) {
                upperIndex = testedIndex;
            } else {
                break;
            }
        }

        // iterate over images downwards, beginning with testedIndex
        this.showElements(testedIndex, -1);
        // iterate over images upwards, beginning with testedIndex
        this.showElements(testedIndex, 1);
    },


    belowTheFold: function ($element) {
        var fold = (window.innerHeight ? window.innerHeight : $window.height()) + $window.scrollTop();

        return fold <= $element.offset().top - THRESHOLD;
    },

    rightToFold: function ($element) {
        var fold = $window.width() + $window.scrollLeft();

        return fold <= $element.offset().left - THRESHOLD;
    },

    aboveTheTop: function ($element) {
        var fold = $window.scrollTop();

        return fold >= $element.offset().top + THRESHOLD + $element.height();
    },


    leftOfBegin: function ($element) {
        var fold = $window.scrollLeft();

        return fold >= $element.offset().left + THRESHOLD + $element.width();
    }
});