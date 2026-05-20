from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random

from accounts.models import Role, Region, Team, ModuleAccess, EmployeeProfile
from tasks.models import Task
from visits.models import Visit
from activity_logs.models import ActivityLog


class Command(BaseCommand):
    help = 'Seed the database with sample data for all roles and modules'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('\n======================================'))
        self.stdout.write(self.style.MIGRATE_HEADING('  FFMS -- Seeding Database'))
        self.stdout.write(self.style.MIGRATE_HEADING('======================================\n'))

        self._seed_roles()
        self._seed_regions()
        self._seed_teams()
        self._seed_module_access()
        self._seed_users()
        self._seed_tasks()
        self._seed_visits()
        self._seed_activity_logs()
        self._print_credentials()

        self.stdout.write(self.style.SUCCESS('\n[OK] Seed data complete!\n'))

    # ──────────────────────────────────────────────
    # Roles
    # ──────────────────────────────────────────────
    def _seed_roles(self):
        roles_data = [
            ('admin', 'Full system access. Can manage everything.'),
            ('regional_manager', 'Manages tasks and agents within their assigned region.'),
            ('team_lead', 'Leads a team. Can create and assign tasks to team members.'),
            ('field_agent', 'Performs field visits. Can only update their own tasks and visits.'),
            ('auditor', 'Read-only access to logs, reports, and visit outcomes.'),
        ]
        for name, desc in roles_data:
            Role.objects.get_or_create(name=name, defaults={'description': desc})
        self.stdout.write(self.style.SUCCESS(f'  [OK] Roles: {Role.objects.count()} created'))

    # ──────────────────────────────────────────────
    # Regions
    # ──────────────────────────────────────────────
    def _seed_regions(self):
        regions_data = [
            ('North Region', 'NORTH'),
            ('South Region', 'SOUTH'),
            ('West Region', 'WEST'),
        ]
        for name, code in regions_data:
            Region.objects.get_or_create(name=name, defaults={'code': code})
        self.stdout.write(self.style.SUCCESS(f'  [OK] Regions: {Region.objects.count()} created'))

    # ──────────────────────────────────────────────
    # Teams
    # ──────────────────────────────────────────────
    def _seed_teams(self):
        north = Region.objects.get(code='NORTH')
        south = Region.objects.get(code='SOUTH')
        west = Region.objects.get(code='WEST')

        teams_data = [
            ('Team Alpha', north),
            ('Team Beta', north),
            ('Team Gamma', south),
            ('Team Delta', south),
            ('Team Omega', west),
        ]
        for name, region in teams_data:
            Team.objects.get_or_create(name=name, defaults={'region': region})
        self.stdout.write(self.style.SUCCESS(f'  [OK] Teams: {Team.objects.count()} created'))

    # ──────────────────────────────────────────────
    # Module Access (Permissions)
    # ──────────────────────────────────────────────
    def _seed_module_access(self):
        """
        Permission matrix:
        Admin:            tasks=CRUD, visits=CRUD, logs=CRUD, reports=CR, users=CRUD
        Regional Manager: tasks=CRU,  visits=CRU,  logs=R,    reports=CR, users=R
        Team Lead:        tasks=CRU,  visits=CRU,  logs=R,    reports=R,  users=R
        Field Agent:      tasks=R,    visits=RU,   logs=-,    reports=-,  users=-
        Auditor:          tasks=R,    visits=R,     logs=R,    reports=R,  users=-
        """
        permissions = {
            'admin': {
                'tasks':   {'can_create': True,  'can_read': True,  'can_update': True,  'can_delete': True},
                'visits':  {'can_create': True,  'can_read': True,  'can_update': True,  'can_delete': True},
                'logs':    {'can_create': True,  'can_read': True,  'can_update': True,  'can_delete': True},
                'reports': {'can_create': True,  'can_read': True,  'can_update': False, 'can_delete': False},
                'users':   {'can_create': True,  'can_read': True,  'can_update': True,  'can_delete': True},
            },
            'regional_manager': {
                'tasks':   {'can_create': True,  'can_read': True,  'can_update': True,  'can_delete': False},
                'visits':  {'can_create': True,  'can_read': True,  'can_update': True,  'can_delete': False},
                'logs':    {'can_create': False, 'can_read': True,  'can_update': False, 'can_delete': False},
                'reports': {'can_create': True,  'can_read': True,  'can_update': False, 'can_delete': False},
                'users':   {'can_create': False, 'can_read': True,  'can_update': False, 'can_delete': False},
            },
            'team_lead': {
                'tasks':   {'can_create': True,  'can_read': True,  'can_update': True,  'can_delete': False},
                'visits':  {'can_create': True,  'can_read': True,  'can_update': True,  'can_delete': False},
                'logs':    {'can_create': False, 'can_read': True,  'can_update': False, 'can_delete': False},
                'reports': {'can_create': False, 'can_read': True,  'can_update': False, 'can_delete': False},
                'users':   {'can_create': False, 'can_read': True,  'can_update': False, 'can_delete': False},
            },
            'field_agent': {
                'tasks':   {'can_create': False, 'can_read': True,  'can_update': False, 'can_delete': False},
                'visits':  {'can_create': True,  'can_read': True,  'can_update': True,  'can_delete': False},
            },
            'auditor': {
                'tasks':   {'can_create': False, 'can_read': True,  'can_update': False, 'can_delete': False},
                'visits':  {'can_create': False, 'can_read': True,  'can_update': False, 'can_delete': False},
                'logs':    {'can_create': False, 'can_read': True,  'can_update': False, 'can_delete': False},
                'reports': {'can_create': False, 'can_read': True,  'can_update': False, 'can_delete': False},
            },
        }

        count = 0
        for role_name, modules in permissions.items():
            role = Role.objects.get(name=role_name)
            for module_name, perms in modules.items():
                _, created = ModuleAccess.objects.get_or_create(
                    role=role,
                    module_name=module_name,
                    defaults=perms,
                )
                if created:
                    count += 1
        self.stdout.write(self.style.SUCCESS(f'  [OK] Module Access: {ModuleAccess.objects.count()} rows ({count} new)'))

    # ──────────────────────────────────────────────
    # Users + Employee Profiles
    # ──────────────────────────────────────────────
    def _seed_users(self):
        north = Region.objects.get(code='NORTH')
        south = Region.objects.get(code='SOUTH')
        west = Region.objects.get(code='WEST')
        team_alpha = Team.objects.get(name='Team Alpha')
        team_gamma = Team.objects.get(name='Team Gamma')
        team_omega = Team.objects.get(name='Team Omega')

        users_data = [
            # (username, email, password, role_name, team, region, employee_id, phone)
            ('admin_user', 'admin@ffms.com', 'admin123', 'admin', None, None, 'EMP-001', '9000000001'),
            ('rm_north', 'rm.north@ffms.com', 'pass123', 'regional_manager', None, north, 'EMP-002', '9000000002'),
            ('rm_south', 'rm.south@ffms.com', 'pass123', 'regional_manager', None, south, 'EMP-003', '9000000003'),
            ('tl_alpha', 'tl.alpha@ffms.com', 'pass123', 'team_lead', team_alpha, north, 'EMP-004', '9000000004'),
            ('agent_ravi', 'ravi@ffms.com', 'pass123', 'field_agent', team_alpha, north, 'EMP-005', '9000000005'),
            ('agent_priya', 'priya@ffms.com', 'pass123', 'field_agent', team_gamma, south, 'EMP-006', '9000000006'),
            ('auditor_meera', 'meera@ffms.com', 'pass123', 'auditor', None, None, 'EMP-007', '9000000007'),
        ]

        for username, email, password, role_name, team, region, emp_id, phone in users_data:
            user, user_created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': username.replace('_', ' ').title().split()[0],
                    'is_active': True,
                }
            )
            if user_created:
                user.set_password(password)
                user.save()

            role = Role.objects.get(name=role_name)
            EmployeeProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role': role,
                    'team': team,
                    'region': region,
                    'employee_id': emp_id,
                    'phone': phone,
                }
            )

        self.stdout.write(self.style.SUCCESS(f'  [OK] Users: {User.objects.count()} | Profiles: {EmployeeProfile.objects.count()}'))

    # ──────────────────────────────────────────────
    # Tasks
    # ──────────────────────────────────────────────
    def _seed_tasks(self):
        now = timezone.now()
        tl_alpha = EmployeeProfile.objects.get(employee_id='EMP-004')
        rm_north = EmployeeProfile.objects.get(employee_id='EMP-002')
        rm_south = EmployeeProfile.objects.get(employee_id='EMP-003')
        agent_ravi = EmployeeProfile.objects.get(employee_id='EMP-005')
        agent_priya = EmployeeProfile.objects.get(employee_id='EMP-006')

        team_alpha = Team.objects.get(name='Team Alpha')
        team_gamma = Team.objects.get(name='Team Gamma')
        north = Region.objects.get(code='NORTH')
        south = Region.objects.get(code='SOUTH')

        tasks_data = [
            {
                'title': 'Site inspection at Warehouse A',
                'description': 'Perform a detailed inspection of Warehouse A for compliance checks.',
                'created_by': tl_alpha, 'assigned_to': agent_ravi,
                'status': 'assigned', 'priority': 'high',
                'due_date': (now + timedelta(days=2)).date(),
                'team_scope': team_alpha, 'region_scope': north,
            },
            {
                'title': 'Client onboarding visit — Acme Corp',
                'description': 'Visit Acme Corp office to complete onboarding documentation.',
                'created_by': tl_alpha, 'assigned_to': agent_ravi,
                'status': 'in_progress', 'priority': 'medium',
                'due_date': (now + timedelta(days=1)).date(),
                'team_scope': team_alpha, 'region_scope': north,
            },
            {
                'title': 'Equipment delivery verification',
                'description': 'Verify that all ordered equipment has been delivered at Site B.',
                'created_by': rm_north, 'assigned_to': agent_ravi,
                'status': 'completed', 'priority': 'low',
                'due_date': (now - timedelta(days=1)).date(),
                'team_scope': team_alpha, 'region_scope': north,
            },
            {
                'title': 'Customer feedback collection — South Zone',
                'description': 'Collect customer feedback forms from 5 locations in south zone.',
                'created_by': rm_south, 'assigned_to': agent_priya,
                'status': 'assigned', 'priority': 'medium',
                'due_date': (now + timedelta(days=3)).date(),
                'team_scope': team_gamma, 'region_scope': south,
            },
            {
                'title': 'Safety audit — Factory Floor',
                'description': 'Conduct safety audit checklist for factory floor operations.',
                'created_by': rm_south, 'assigned_to': agent_priya,
                'status': 'completed', 'priority': 'high',
                'due_date': (now - timedelta(days=2)).date(),
                'team_scope': team_gamma, 'region_scope': south,
            },
            {
                'title': 'New vendor site assessment',
                'description': 'Assess the new vendor location for quality and compliance standards.',
                'created_by': tl_alpha, 'assigned_to': None,
                'status': 'pending', 'priority': 'medium',
                'due_date': (now + timedelta(days=5)).date(),
                'team_scope': team_alpha, 'region_scope': north,
            },
            {
                'title': 'Quarterly inventory count',
                'description': 'Perform quarterly physical inventory count at all warehouses.',
                'created_by': rm_north, 'assigned_to': None,
                'status': 'pending', 'priority': 'high',
                'due_date': (now + timedelta(days=7)).date(),
                'team_scope': team_alpha, 'region_scope': north,
            },
            {
                'title': 'Follow-up visit — Cancelled contract',
                'description': 'Visit the client who cancelled their contract to understand reasons.',
                'created_by': rm_south, 'assigned_to': agent_priya,
                'status': 'in_progress', 'priority': 'high',
                'due_date': (now + timedelta(days=1)).date(),
                'team_scope': team_gamma, 'region_scope': south,
            },
            {
                'title': 'Training session at branch office',
                'description': 'Conduct product training session for new staff at branch office.',
                'created_by': tl_alpha, 'assigned_to': agent_ravi,
                'status': 'pending', 'priority': 'low',
                'due_date': (now + timedelta(days=10)).date(),
                'team_scope': team_alpha, 'region_scope': north,
            },
            {
                'title': 'Emergency repair request — Site C',
                'description': 'Urgent: Equipment malfunction reported at Site C. Immediate visit needed.',
                'created_by': rm_north, 'assigned_to': agent_ravi,
                'status': 'cancelled', 'priority': 'high',
                'due_date': (now - timedelta(days=3)).date(),
                'team_scope': team_alpha, 'region_scope': north,
            },
        ]

        for task_data in tasks_data:
            Task.objects.get_or_create(
                title=task_data['title'],
                defaults=task_data,
            )
        self.stdout.write(self.style.SUCCESS(f'  [OK] Tasks: {Task.objects.count()} created'))

    # ──────────────────────────────────────────────
    # Visits
    # ──────────────────────────────────────────────
    def _seed_visits(self):
        now = timezone.now()
        agent_ravi = EmployeeProfile.objects.get(employee_id='EMP-005')
        agent_priya = EmployeeProfile.objects.get(employee_id='EMP-006')

        # Visit 1: Completed visit with notes (low risk)
        task1 = Task.objects.get(title='Equipment delivery verification')
        Visit.objects.get_or_create(
            task=task1,
            started_by=agent_ravi,
            defaults={
                'status': 'completed',
                'start_time': now - timedelta(hours=5),
                'end_time': now - timedelta(hours=3),
                'visit_notes': 'All equipment delivered and verified. 15 units received, all in good condition. Signed delivery receipt with warehouse manager.',
                'ai_summary': "Agent reported: 'All equipment delivered and verified. 15 units received, all in good condition.'",
                'ai_recommendation': 'No immediate action needed. Standard 7-day follow-up recommended.',
                'ai_risk_flag': 'low',
            }
        )

        # Visit 2: Completed visit with notes (high risk)
        task2 = Task.objects.get(title='Safety audit — Factory Floor')
        Visit.objects.get_or_create(
            task=task2,
            started_by=agent_priya,
            defaults={
                'status': 'completed',
                'start_time': now - timedelta(days=1, hours=6),
                'end_time': now - timedelta(days=1, hours=2),
                'visit_notes': 'Found multiple safety issues on factory floor. Workers complained about inadequate safety gear. One worker reported an injury last week. Management seemed angry when confronted about the problems.',
                'ai_summary': "Agent reported: 'Found multiple safety issues on factory floor. Workers complained about inadequate safety gear...'",
                'ai_recommendation': 'Immediate escalation required. Notify Team Lead within 24 hours.',
                'ai_risk_flag': 'high',
            }
        )

        # Visit 3: Completed visit (medium risk)
        task3 = Task.objects.get(title='Client onboarding visit — Acme Corp')
        Visit.objects.get_or_create(
            task=task3,
            started_by=agent_ravi,
            defaults={
                'status': 'completed',
                'start_time': now - timedelta(hours=8),
                'end_time': now - timedelta(hours=6),
                'visit_notes': 'Client onboarding partially complete. The client wants to reschedule the final documentation signing due to unavailable key decision makers.',
                'ai_summary': "Agent reported: 'Client onboarding partially complete. The client wants to reschedule the final documentation...'",
                'ai_recommendation': 'Schedule a follow-up visit within 3 business days.',
                'ai_risk_flag': 'medium',
            }
        )

        # Visit 4: Started but not completed
        task4 = Task.objects.get(title='Follow-up visit — Cancelled contract')
        Visit.objects.get_or_create(
            task=task4,
            started_by=agent_priya,
            defaults={
                'status': 'started',
                'start_time': now - timedelta(hours=1),
            }
        )

        # Visit 5: Completed visit (low risk)
        task5 = Task.objects.get(title='Customer feedback collection — South Zone')
        Visit.objects.get_or_create(
            task=task5,
            started_by=agent_priya,
            defaults={
                'status': 'completed',
                'start_time': now - timedelta(days=2, hours=4),
                'end_time': now - timedelta(days=2, hours=1),
                'visit_notes': 'Collected feedback forms from 3 out of 5 locations. Remaining 2 locations were closed for holiday. Will revisit next week.',
                'ai_summary': "Agent reported: 'Collected feedback forms from 3 out of 5 locations. Remaining 2 locations were closed...'",
                'ai_recommendation': 'No immediate action needed. Standard 7-day follow-up recommended.',
                'ai_risk_flag': 'low',
            }
        )

        self.stdout.write(self.style.SUCCESS(f'  [OK] Visits: {Visit.objects.count()} created'))

    # ──────────────────────────────────────────────
    # Activity Logs
    # ──────────────────────────────────────────────
    def _seed_activity_logs(self):
        now = timezone.now()
        admin_user = User.objects.get(username='admin_user')
        tl_user = User.objects.get(username='tl_alpha')
        rm_north_user = User.objects.get(username='rm_north')
        rm_south_user = User.objects.get(username='rm_south')
        agent_ravi_user = User.objects.get(username='agent_ravi')
        agent_priya_user = User.objects.get(username='agent_priya')

        tasks = Task.objects.all()
        visits = Visit.objects.all()

        logs_data = [
            (tl_user, 'created', 'task', tasks[0].id, f'Task "{tasks[0].title}" created by tl_alpha', now - timedelta(days=3)),
            (tl_user, 'assigned', 'task', tasks[0].id, f'Task "{tasks[0].title}" assigned to agent_ravi', now - timedelta(days=3, hours=-1)),
            (rm_north_user, 'created', 'task', tasks[2].id, f'Task "{tasks[2].title}" created by rm_north', now - timedelta(days=2)),
            (rm_north_user, 'assigned', 'task', tasks[2].id, f'Task "{tasks[2].title}" assigned to agent_ravi', now - timedelta(days=2, hours=-1)),
            (rm_south_user, 'created', 'task', tasks[4].id, f'Task "{tasks[4].title}" created by rm_south', now - timedelta(days=2)),
            (agent_ravi_user, 'started', 'visit', visits[0].id if visits.exists() else 1, 'Visit started for "Equipment delivery verification"', now - timedelta(hours=5)),
            (agent_ravi_user, 'completed', 'visit', visits[0].id if visits.exists() else 1, 'Visit completed for "Equipment delivery verification"', now - timedelta(hours=3)),
            (agent_priya_user, 'started', 'visit', visits[1].id if visits.count() > 1 else 1, 'Visit started for "Safety audit — Factory Floor"', now - timedelta(days=1, hours=6)),
            (agent_priya_user, 'completed', 'visit', visits[1].id if visits.count() > 1 else 1, 'Visit completed for "Safety audit — Factory Floor"', now - timedelta(days=1, hours=2)),
            (tl_user, 'status_changed', 'task', tasks[2].id, f'Task "{tasks[2].title}" status changed to Completed', now - timedelta(hours=2)),
            (rm_south_user, 'assigned', 'task', tasks[3].id, f'Task "{tasks[3].title}" assigned to agent_priya', now - timedelta(days=1)),
            (agent_priya_user, 'started', 'visit', visits[3].id if visits.count() > 3 else 1, 'Visit started for "Follow-up visit — Cancelled contract"', now - timedelta(hours=1)),
        ]

        count = 0
        for user, action, entity_type, entity_id, description, timestamp in logs_data:
            _, created = ActivityLog.objects.get_or_create(
                user=user,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                description=description,
                defaults={'timestamp': timestamp},
            )
            if created:
                count += 1
        self.stdout.write(self.style.SUCCESS(f'  [OK] Activity Logs: {ActivityLog.objects.count()} entries ({count} new)'))

    # ──────────────────────────────────────────────
    # Print Credentials
    # ──────────────────────────────────────────────
    def _print_credentials(self):
        self.stdout.write(self.style.MIGRATE_HEADING('\n-- Sample Login Credentials --\n'))
        credentials = [
            ('admin_user', 'admin123', 'Admin', '-', '-'),
            ('rm_north', 'pass123', 'Regional Manager', '-', 'North'),
            ('rm_south', 'pass123', 'Regional Manager', '-', 'South'),
            ('tl_alpha', 'pass123', 'Team Lead', 'Team Alpha', 'North'),
            ('agent_ravi', 'pass123', 'Field Agent', 'Team Alpha', 'North'),
            ('agent_priya', 'pass123', 'Field Agent', 'Team Gamma', 'South'),
            ('auditor_meera', 'pass123', 'Auditor', '-', '-'),
        ]

        header = f"  {'Username':<18} {'Password':<12} {'Role':<20} {'Team':<14} {'Region'}"
        self.stdout.write(header)
        self.stdout.write('  ' + '-' * 80)
        for username, password, role, team, region in credentials:
            self.stdout.write(f"  {username:<18} {password:<12} {role:<20} {team:<14} {region}")
