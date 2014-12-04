import csrfutil from '../utils/csrftoken';

export default {
    name: 'csrf',

    /**
     * Setup CSRF: add token passed as cookie to every ajax request.
     */
    initialize: function (container, application) {
        csrfutil.setupAjaxForCSRF();
    }
};