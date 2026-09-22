def build_autoscale_profile(autoscale_settings):
    from datetime import time
    import json
    from azure.mgmt.monitor.models import AutoscaleProfile
    def _validate_default_profile(default_profile, profile):
        if profile.capacity.default != default_profile.capacity.default or \
                profile.capacity.minimum != default_profile.capacity.minimum or \
                profile.capacity.maximum != default_profile.capacity.maximum:
            from knack.util import CLIError
            raise CLIError('unable to resolve default profile.')
    recurring_profiles_renamed = [x for x in autoscale_settings.profiles if x.recurrence]
    default_profiles = [x for x in autoscale_settings.profiles if not x.recurrence and not x.fixed_date]
    profile_schedule = {
    }
    default_profile = default_profiles[0] if default_profiles else None
    for p in default_profiles:
        _validate_default_profile(default_profile, p)
    for profile in recurring_profiles_renamed:
        try:
            json_name = json.loads(profile.name)
            sched_name = json_name['for']
            end_time = time(hour=profile.recurrence.schedule.hours[0], minute=profile.recurrence.schedule.minutes[0])
            if not default_profile:
                default_profile = AutoscaleProfile(
                    name='default',
                    capacity=profile.capacity,
                    rules=profile.rules
                )
            else:
                _validate_default_profile(default_profile, profile)
            for day in profile.recurrence.schedule.days:
                if day not in profile_schedule:
                    profile_schedule[day] = {}
                if sched_name in profile_schedule[day]:
                    profile_schedule[day][sched_name]['end'] = end_time
                else:
                    profile_schedule[day][sched_name] = {'end': end_time}
        except ValueError:
            sched_name = profile.name
            start_time = time(hour=profile.recurrence.schedule.hours[0], minute=profile.recurrence.schedule.minutes[0])
            for day in profile.recurrence.schedule.days:
                if day not in profile_schedule:
                    profile_schedule[day] = {}
                if sched_name in profile_schedule[day]:
                    profile_schedule[day][sched_name]['start'] = start_time
                    profile_schedule[day][sched_name]['capacity'] = profile.capacity
                    profile_schedule[day][sched_name]['rules'] = profile.rules
                else:
                    profile_schedule[day][sched_name] = {
                        'start': start_time,
                        'capacity': profile.capacity,
                        'rules': profile.rules
                    }
    return default_profile, profile_schedule