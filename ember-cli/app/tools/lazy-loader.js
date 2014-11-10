import Ember from 'ember';

var $ = Ember.$;
var $window = $(window);

var THRESHOLD = 200;
var FAILURE_LIMIT = 10;

export default Ember.Object.extend({

    elements: [],

    rebindEvents: function () {
        $window.unbind("resize");
        $window.unbind("scroll");
        $window.bind("resize", this.update.bind(this));
        $window.bind("scroll", this.update.bind(this));
    },

    setImages: function (jqueryRefs) {
        this.rebindEvents();

        this.elements = [];
        var $this = this;

        jqueryRefs.each(function (index, item) {
            $this.elements.push($(item));
        });

        this.update();
    },

    showElement: function ($element) {
        var imageUrl = $element.attr("data-original");
        if (imageUrl) {
            $("<img />")
                .bind("load", function () {
                    $element.attr("src", imageUrl);
                    $element.loaded = true;
                })
                .attr("src", imageUrl);
        }
    },

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