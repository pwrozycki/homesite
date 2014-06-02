export default Ember.Route.extend({
    model: function () {
        return Ember.$.getJSON('http://localhost:18000/gallery/listdir/Przemek/2013_08_Pireneje' + '?callback=?');
    }
});
