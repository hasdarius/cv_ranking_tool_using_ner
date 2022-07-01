from business_rules import run_all
from business_rules.actions import BaseActions, rule_action
from business_rules.fields import FIELD_NUMERIC
from business_rules.variables import BaseVariables, numeric_rule_variable

from utilities.constants import REASONING_PENALIZATION, CONCEPTS_SCORES


class RequiredLabelInfo:
    def __init__(self, label_name, required_values, max_absolute_seniority,
                 max_required_values=9999):
        self.name = label_name
        self.values = required_values
        self.max_absolute_seniority = max_absolute_seniority
        self.loss_value = 0.25
        self.max_required_values = max_required_values
        self.actual_loss_values = 0


class RequiredLabelInfoVariables(BaseVariables):

    def __init__(self, label_info):
        self.label_info = label_info

    @numeric_rule_variable(label='Maximum number of words with a specific label before being penalized')
    def get_max_required_value_for_label(self):
        label_info = self.label_info
        label_info.max_required_values = max(2 * len(label_info.values),
                                             CONCEPTS_SCORES[label_info.max_absolute_seniority][
                                                 'Max ' + label_info.name])
        return label_info.max_required_values


class RequiredLabelInfoActions(BaseActions):

    def __init__(self, label_info):
        self.label_info = label_info

    @rule_action(params={"given_values_length": FIELD_NUMERIC})
    def penalize(self, given_values_length):
        self.label_info.actual_loss_values = (
                                                     self.label_info.max_required_values - given_values_length) * self.label_info.loss_value


def apply_business_rules(max_absolute_seniority, label_name, required_label_values,
                         given_label_values, feedback_list):
    given_label_values_length = len(given_label_values)
    rules = [
        {"conditions":
             {"name": "get_max_required_value_for_label",
              "operator": "less_than",
              "value": given_label_values_length,
              },
         "actions": [
             {"name": "penalize",
              "params": {"given_values_length": given_label_values_length},
              }
         ]}]
    required_label_info = RequiredLabelInfo(label_name, required_label_values,
                                            max_absolute_seniority)
    if run_all(rule_list=rules,
               defined_variables=RequiredLabelInfoVariables(required_label_info),
               defined_actions=RequiredLabelInfoActions(required_label_info),
               stop_on_first_trigger=True
               ):
        feedback_list.append(REASONING_PENALIZATION + "<<" + label_name + ">>.")
    return required_label_info.actual_loss_values
