import copy
import logging

from django.apps import apps
from django.utils.functional import cached_property
from django_fsm import can_proceed, get_all_FIELD_transitions, has_transition_perm

from .decorators import error_string, state_error_string, transition_error_string
from .utils import update_object

logger = logging.getLogger(__name__)


class CompleteValidation(object):
    PERMISSIONS_CLASS = None

    def __init__(
            self,
            new,
            user=None,
            old=None,
            instance_class=None,
            stateless=False,
            disable_rigid_check=False
    ):
        if old and isinstance(old, dict):
            raise TypeError(
                'if old is transmitted to complete validation '
                'it needs to be a model instance'
            )

        if isinstance(new, dict):
            if not instance_class:
                if old:
                    instance_class = type(old)
                else:
                    try:
                        instance_class = apps.get_model(
                            getattr(self, 'VALIDATION_CLASS')
                        )
                    except LookupError:
                        raise TypeError(
                            'Object transmitted for validation cannot '
                            'be dict if instance_class is not defined'
                        )
            new_id = new.get('id', None) or new.get('pk', None)
            if new_id:
                # let it raise the error if it does not exist
                if old and old.id == new_id:
                    old_instance = old
                else:
                    old_instance = instance_class.objects.get(id=new_id)
                new_instance = instance_class.objects.get(id=new_id)
                update_object(new_instance, new)

            else:
                old_instance = old
                # TODO: instance_class(**new) can't be called like that if
                # models have m2m fields
                # Workaround for now is not to call the validator from the
                # serializer on new instances
                new_instance = copy.deepcopy(old) if old else instance_class(**new)
                if old:
                    update_object(new_instance, new)
            new = new_instance
            old = old_instance

        self.stateless = stateless
        self.new = new
        # TODO: on old for related fields add the _old values in order to check
        # for rigid fields if validator was not called through the view using
        # the viewmixin
        self.old = old
        if not self.stateless:
            self.new_status = self.new.status
            self.old_status = self.old.status if self.old else None
        self.skip_transition = not old
        self.skip_permissions = not user
        self.user = user

        # permissions to be set in each function that is needed, this attribute
        # can change values as auto-update goes through different statuses
        self.permissions = None
        self.disable_rigid_check = disable_rigid_check

    def get_permissions(self, instance):
        if self.PERMISSIONS_CLASS:
            p = self.PERMISSIONS_CLASS(
                user=self.user,
                instance=instance,
                permission_structure=self.new.permission_structure(),
                inbound_check=True)
            return p.get_permissions()
        return None

    def check_transition_conditions(self, transition):
        if not transition:
            return True
        return can_proceed(transition)

    def check_transition_permission(self, transition):
        if not transition:
            return True
        return has_transition_perm(transition, self.user)

    @cached_property
    def transition(self):
        return self._get_fsm_defined_transitions(self.old_status, self.new_status)

    @transition_error_string
    def transitional_validation(self):
        # set old status to get proper transitions
        self.new.status = self.old.status

        # set old instance on instance to make it available to the
        # validation functions
        setattr(self.new, 'old_instance', self.old)
        self.permissions = self.get_permissions(self.new)

        # check conditions and permissions
        conditions_check = self.check_transition_conditions(self.transition)

        if self.skip_permissions:
            permissions_check = True
        else:
            permissions_check = self.check_transition_permission(
                self.transition
            )

        # cleanup
        delattr(self.new, 'old_instance')
        self.permissions = None
        self.new.status = self.new_status
        return conditions_check and permissions_check

    @state_error_string
    def state_valid(self):
        if not self.basic_validation[0]:
            return self.basic_validation

        result = True
        # set old instance on instance to make it available to the
        # validation functions
        setattr(self.new, 'old_instance', self.old)
        self.permissions = self.get_permissions(self.new)

        funct_name = "state_{}_valid".format(self.new_status)
        function = getattr(self, funct_name, None)
        if function:
            result = function(self.new, user=self.user)

        # cleanup
        delattr(self.new, 'old_instance')
        self.permissions = None
        return result

    def _get_fsm_defined_transitions(self, source, target):
        all_transitions = get_all_FIELD_transitions(self.new,
                                                    type(self.new)._meta.get_field('status'))
        for transition in all_transitions:
            if transition.source == source and target in transition.target:
                return getattr(self.new, transition.method.__name__)

    @transition_error_string
    def auto_transition_validation(self, potential_transition):

        result = self.check_transition_conditions(potential_transition)
        return result

    def _first_available_auto_transition(self):

        potential = getattr(self.new.__class__, 'AUTO_TRANSITIONS', {})

        # ptt: Potential Transition To List
        list_of_status_choices = [
            i[0] for i in self.new.__class__._meta.get_field('status').choices
        ]
        pttl = [i for i in potential.get(self.new.status, [])
                if i in list_of_status_choices]

        for potential_transition_to in pttl:
            possible_fsm_transition = self._get_fsm_defined_transitions(
                self.new.status,
                potential_transition_to
            )
            if not possible_fsm_transition:
                template = "transition: {} -> {} is possible since there " \
                           "was no transition defined on the model"
                logger.debug(template.format(self.new.status, potential_transition_to))
            if self.auto_transition_validation(possible_fsm_transition)[0]:
                # get the side effects function if any
                SIDE_EFFECTS_DICT = getattr(type(self.new), 'TRANSITION_SIDE_EFFECTS', {})
                transition_side_effects = SIDE_EFFECTS_DICT.get(potential_transition_to, [])

                return True, potential_transition_to, transition_side_effects
        return None, None, None

    def _make_auto_transition(self):
        valid_available_transition, new_status, auto_update_functions = self._first_available_auto_transition()
        if not valid_available_transition:
            return False
        else:
            originals = self.new.status, self.new_status
            self.new.status = new_status
            self.new_status = new_status

            state_valid = self.state_valid()
            if not state_valid[0]:
                # set stuff back
                self.new.status, self.new_status = originals
                return False

            # if all good run all the autoupdates on that status
            for function in auto_update_functions:
                function(self.new, old_instance=self.old, user=self.user)
            return True

    def make_auto_transitions(self):
        any_transition_made = False

        # disable rigid_check in auto-transitions as they do not apply
        originial_rigid_check_setting = self.disable_rigid_check
        self.disable_rigid_check = True

        while self._make_auto_transition():
            any_transition_made = True

        # reset rigid check:
        self.disable_rigid_check = originial_rigid_check_setting
        return any_transition_made

    @cached_property
    def basic_validation(self):
        '''
        basic set of validations to make sure new state is correct
        :return: True or False
        '''

        setattr(self.new, 'old_instance', self.old)
        self.permissions = self.get_permissions(self.new)
        errors = []
        for validation_function in self.BASIC_VALIDATIONS:
            a = error_string(validation_function)(self.new)
            errors += a[1]
        delattr(self.new, 'old_instance')
        self.permissions = None
        return not len(errors), errors

    def map_errors(self, errors):
        return [self.VALID_ERRORS.get(error, error) for error in errors]

    def _apply_current_side_effects(self):
        # check if there was any transition so far:
        if self.old_status == self.new_status:
            return
        else:
            SIDE_EFFECTS_DICT = getattr(
                self.new.__class__,
                'TRANSITION_SIDE_EFFECTS',
                {}
            )
            transition_side_effects = SIDE_EFFECTS_DICT.get(
                self.new_status,
                []
            )
            for side_effect_function in transition_side_effects:
                side_effect_function(
                    self.new,
                    old_instance=self.old,
                    user=self.user
                )

    @cached_property
    def total_validation(self):
        if not self.basic_validation[0]:
            return False, self.map_errors(self.basic_validation[1])

        if not self.skip_transition and not self.stateless:
            transitional = self.transitional_validation()
            if not transitional[0]:
                return False, self.map_errors(transitional[1])

        if not self.stateless:
            state_valid = self.state_valid()
            if not state_valid[0]:
                return False, self.map_errors(state_valid[1])

            # before checking if any further transitions can be made,
            # if the current instance just transitioned, apply side-effects:
            # TODO.. this needs to be re-written and have a consistent way
            # to include side-effects on both auto-transition/manual transition
            self._apply_current_side_effects()

            if self.make_auto_transitions():
                self.new.save()
        return True, []

    @property
    def is_valid(self):
        return self.total_validation[0]

    @property
    def errors(self):
        return self.total_validation[1]
