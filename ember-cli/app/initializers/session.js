export default {
    name: 'get session',
    after: 'store',

    /**
     * Get session controller.
     * Inject it to every controller.
     * Get active session.
     */
    initialize: function (container, application) {
        // inject session into every controller
        var sessionController = container.lookup('controller:session');
        container.register('session:main', sessionController, {instantiate: false});
        application.inject('controller', 'session', 'session:main');

        // get active session
        application.deferReadiness();
        sessionController.getActiveSessions().then(function () {
            application.advanceReadiness();
        });
    }
};