import csrfutil from '../utils/csrftoken';

export default {
    name: 'get session',
    after: 'store',

    /**
     * setup CSRF: add token passed as cookie to every ajax request
     * get active sessions ->
     */
    initialize: function(container) {
        csrfutil.setupAjaxForCSRF();
        container.lookup('controller:session').getActiveSessions();
    }
};