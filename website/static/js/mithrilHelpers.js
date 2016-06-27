'use strict';

/* Send with ajax calls to work with api2 */
var apiV2Config = function (options) {
    return function (xhr) {
        xhr.withCredentials = options.withCredentials || true;
        xhr.setRequestHeader('Content-Type', 'application/vnd.api+json;');
        xhr.setRequestHeader('Accept', 'application/vnd.api+json; ext=bulk');
    };
};

module.exports = {
    apiV2Config: apiV2Config
};
