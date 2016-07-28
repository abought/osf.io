import Ember from 'ember';

export function canRemoveContributor(params/*, hash*/) {
    var contributor = params[0];
    var currentUser = params[1];
    var registration = params[2];
    if (currentUser) {
        var currentUserId = currentUser.get('currentUserId') || currentUser.get('id');
        return contributor.id.split('-')[1] === currentUserId && !registration;
    } else {
        return params;
    }

}

export default Ember.Helper.helper(canRemoveContributor);
