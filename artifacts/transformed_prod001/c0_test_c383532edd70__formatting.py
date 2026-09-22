class SubscriptionPlanAutoAssignmentRuleBuilderCriterias:
    def __init__(
        self,
        username=None,
        groups=None,
        role=None,
        first=None,
        last=None,
        company=None,
        billing_id=None,
        comment=None,
    ):
        self.Username = username
        self.Groups = groups
        self.Role = role
        self.First = first
        self.Last = last
        self.Company = company
        self.BillingId = billing_id
        self.Comment = comment
