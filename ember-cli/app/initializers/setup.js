import csrfutil from '../utils/csrftoken';

export default {
    name: 'get session',
    after: 'store',

    /**
     * Perform application initialization.
     */
    initialize: function (container, application) {
        // setup CSRF: add token passed as cookie to every ajax request
        csrfutil.setupAjaxForCSRF();

        // defer readiness until session information is loaded
        application.deferReadiness();
        var sessionController = container.lookup('controller:session');
        sessionController.getActiveSessions().then(function () {
            application.advanceReadiness();
        });

        // inject session into every controller
        container.register('session:main', sessionController, {instantiate: false});
        application.inject('controller', 'session', 'session:main');
    }
};