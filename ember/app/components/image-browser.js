export default Ember.Component.extend({
    _showVisibleImages: function() {
        for(var i = 0; i < this.$browserNotYetLoadedImages.length; i++) {
            var el = this.$browserNotYetLoadedImages[i];
            /*
            var imgRect = el.getBoundingClientRect();
            if (imgRect.bottom >= 0 && imgRect.top <= window.innerHeight) {
                var $this = $(el);
                $this.attr("src", $this.attr('data-src'));
            }*/
        }
    },

    didInsertElement: function () {
        this.$browserNotYetLoadedImages = $("#browser").find("img");
        this._showVisibleImages();
        var $this = this;
        $(window).scroll(function () {
            $this._showVisibleImages();
        });
    },

    willDestroyElement: function () {
        $(window).unbind("scroll");
    },

    actions: {
        imageClicked: function (image) {
            this.sendAction('imageClicked', image);
        }
    }
});
