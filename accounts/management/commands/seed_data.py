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
    help = 'Seed the database with realistic Indian sample data for all roles and modules'

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
                'reports': {'can_create': False, 'can_read': True,  'can_update': False, 'can_delete': False},
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
            # (username, email, password, first_name, last_name, role_name, team, region, employee_id, phone)
            ('admin_user',    'admin@ffms.com',      'admin123', 'Arjun',   'Mehta',     'admin',            None,        None,  'EMP-001', '+91-98100-10001'),
            ('rm_north',      'rm.north@ffms.com',   'pass123',  'Rajesh',  'Kapoor',    'regional_manager', None,        north, 'EMP-002', '+91-98100-20002'),
            ('rm_south',      'rm.south@ffms.com',   'pass123',  'Sunita',  'Iyer',      'regional_manager', None,        south, 'EMP-003', '+91-98400-30003'),
            ('tl_alpha',      'tl.alpha@ffms.com',   'pass123',  'Vikram',  'Sharma',    'team_lead',        team_alpha,  north, 'EMP-004', '+91-98100-40004'),
            ('agent_ravi',    'ravi@ffms.com',        'pass123',  'Ravi',    'Verma',     'field_agent',      team_alpha,  north, 'EMP-005', '+91-98100-50005'),
            ('agent_priya',   'priya@ffms.com',       'pass123',  'Priya',   'Nair',      'field_agent',      team_gamma,  south, 'EMP-006', '+91-98400-60006'),
            ('auditor_meera', 'meera@ffms.com',       'pass123',  'Meera',   'Deshmukh',  'auditor',          None,        None,  'EMP-007', '+91-98200-70007'),
        ]

        for username, email, password, first_name, last_name, role_name, team, region, emp_id, phone in users_data:
            user, user_created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_active': True,
                }
            )
            if user_created:
                user.set_password(password)
                user.save()
            else:
                # Update existing user's names if they were generic
                updated = False
                if user.first_name != first_name:
                    user.first_name = first_name
                    updated = True
                if user.last_name != last_name:
                    user.last_name = last_name
                    updated = True
                if updated:
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
    # Tasks (realistic Indian field operations)
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
            # ── North Region / Team Alpha (Ravi) ──
            {
                'title': 'Site inspection — Reliance Warehouse, Sector 18 Noida',
                'description': 'Conduct a full compliance inspection at the Reliance Jio warehouse in Sector 18, Noida. Verify fire safety equipment, check inventory storage standards, and review the loading dock operations. Report any FSSAI or BIS compliance gaps.',
                'created_by': tl_alpha, 'assigned_to': agent_ravi,
                'status': 'completed', 'priority': 'high',
                'due_date': (now - timedelta(days=2)).date(),
                'team_scope': team_alpha, 'region_scope': north,
            },
            {
                'title': 'Client onboarding — Tata Motors, Manesar Plant',
                'description': 'Visit Tata Motors Manesar plant for new service contract onboarding. Meet with Mr. Suresh Bansal (Plant Manager) to complete KYC documentation, collect signed agreements, and hand over the welcome kit. Ensure all GSTIN and PAN details are verified.',
                'created_by': tl_alpha, 'assigned_to': agent_ravi,
                'status': 'in_progress', 'priority': 'high',
                'due_date': (now + timedelta(days=1)).date(),
                'team_scope': team_alpha, 'region_scope': north,
            },
            {
                'title': 'Equipment delivery verification — Maruti Suzuki, Gurugram',
                'description': 'Verify delivery of 25 industrial air purifier units at Maruti Suzuki service centre in Gurugram. Cross-check serial numbers against PO #MSZ-2026-4891. Get delivery receipt signed by warehouse incharge Mr. Deepak Rawat.',
                'created_by': rm_north, 'assigned_to': agent_ravi,
                'status': 'completed', 'priority': 'medium',
                'due_date': (now - timedelta(days=3)).date(),
                'team_scope': team_alpha, 'region_scope': north,
            },
            {
                'title': 'AMC renewal follow-up — HDFC Bank, Connaught Place',
                'description': 'Follow up with Mr. Ankit Jain (Branch Manager) at HDFC Bank CP branch regarding the Annual Maintenance Contract renewal for 12 ATM machines. Contract expires on 30th June. Carry revised rate card and updated SLA terms.',
                'created_by': tl_alpha, 'assigned_to': agent_ravi,
                'status': 'assigned', 'priority': 'medium',
                'due_date': (now + timedelta(days=4)).date(),
                'team_scope': team_alpha, 'region_scope': north,
            },
            {
                'title': 'New vendor assessment — Balaji Industrial, Faridabad',
                'description': 'Assess Balaji Industrial Solutions at Plot No. 47, Sector 6, Faridabad as a potential vendor for electrical components. Evaluate manufacturing capacity, quality certifications (ISO 9001, BIS), and delivery reliability. Take photos of the facility.',
                'created_by': rm_north, 'assigned_to': None,
                'status': 'pending', 'priority': 'medium',
                'due_date': (now + timedelta(days=6)).date(),
                'team_scope': team_alpha, 'region_scope': north,
            },
            {
                'title': 'Quarterly stock audit — Central Warehouse, Karol Bagh',
                'description': 'Perform Q2 physical inventory count at Central Warehouse, Karol Bagh. Verify stock levels for SKUs in Category A and B against ERP records. Flag any discrepancies exceeding 2%. Coordinate with Mr. Harish Chandra (Store Keeper).',
                'created_by': rm_north, 'assigned_to': agent_ravi,
                'status': 'pending', 'priority': 'high',
                'due_date': (now + timedelta(days=8)).date(),
                'team_scope': team_alpha, 'region_scope': north,
            },
            {
                'title': 'Emergency repair — SBI ATM, Lajpat Nagar',
                'description': 'Urgent: SBI ATM at Lajpat Nagar Central Market reported cash dispenser jamming and screen flickering since morning. Branch code: SBI-LN-042. Contact: Mr. Pankaj Gupta (Branch Ops), Ph: +91-98100-44512.',
                'created_by': rm_north, 'assigned_to': agent_ravi,
                'status': 'cancelled', 'priority': 'high',
                'due_date': (now - timedelta(days=4)).date(),
                'team_scope': team_alpha, 'region_scope': north,
            },
            {
                'title': 'Training session — New CRM rollout, Nehru Place office',
                'description': 'Conduct a 2-hour training session for the sales team at Nehru Place branch office on the new CRM platform. Cover lead management, visit logging, and report generation modules. Carry 15 printed quick-reference guides.',
                'created_by': tl_alpha, 'assigned_to': agent_ravi,
                'status': 'pending', 'priority': 'low',
                'due_date': (now + timedelta(days=12)).date(),
                'team_scope': team_alpha, 'region_scope': north,
            },

            # ── South Region / Team Gamma (Priya) ──
            {
                'title': 'Customer feedback collection — Infosys campus, Electronic City',
                'description': 'Visit Infosys Electronic City campus (Gate 3, Building 7) to collect quarterly customer satisfaction feedback from facility management team. Meet Ms. Kavitha Reddy (Admin Head). Collect filled survey forms and note any verbal complaints.',
                'created_by': rm_south, 'assigned_to': agent_priya,
                'status': 'completed', 'priority': 'medium',
                'due_date': (now - timedelta(days=1)).date(),
                'team_scope': team_gamma, 'region_scope': south,
            },
            {
                'title': 'Safety audit — TVS Motor factory, Hosur',
                'description': 'Conduct comprehensive safety audit at TVS Motor Company factory in Hosur. Check fire extinguisher servicing dates, emergency exit signage, PPE compliance on assembly floor, and first-aid kit inventory. Factory Head: Mr. Venkatesh Murthy.',
                'created_by': rm_south, 'assigned_to': agent_priya,
                'status': 'completed', 'priority': 'high',
                'due_date': (now - timedelta(days=3)).date(),
                'team_scope': team_gamma, 'region_scope': south,
            },
            {
                'title': 'Follow-up — Wipro contract cancellation, Whitefield',
                'description': 'Visit Wipro Whitefield office to understand reasons behind the recent service contract cancellation. Meet Mr. Arun Krishnan (Procurement Head). Attempt to negotiate revised terms and present the updated pricing proposal (Ref: WPR-2026-789).',
                'created_by': rm_south, 'assigned_to': agent_priya,
                'status': 'in_progress', 'priority': 'high',
                'due_date': (now + timedelta(days=1)).date(),
                'team_scope': team_gamma, 'region_scope': south,
            },
            {
                'title': 'New branch setup inspection — Koramangala',
                'description': 'Inspect the new branch office space at 4th Block, Koramangala (above Rameshwaram Cafe). Verify electrical wiring, internet connectivity, CCTV installation, and furniture placement against the approved layout. Landlord: Mr. Srinivas Rao, Ph: +91-98440-88912.',
                'created_by': rm_south, 'assigned_to': agent_priya,
                'status': 'assigned', 'priority': 'medium',
                'due_date': (now + timedelta(days=3)).date(),
                'team_scope': team_gamma, 'region_scope': south,
            },
            {
                'title': 'Vendor payment dispute — Sri Lakshmi Enterprises, Peenya',
                'description': 'Visit Sri Lakshmi Enterprises at Peenya Industrial Area (2nd Stage) to resolve pending payment dispute for invoice #SLE-2026-312 (₹2,47,500). Carry credit note and reconciliation statement. Contact: Mr. Ramesh Gowda.',
                'created_by': rm_south, 'assigned_to': agent_priya,
                'status': 'pending', 'priority': 'high',
                'due_date': (now + timedelta(days=5)).date(),
                'team_scope': team_gamma, 'region_scope': south,
            },
            {
                'title': 'Maintenance check — Manipal Hospital, Old Airport Road',
                'description': 'Quarterly maintenance check of 8 HVAC units installed at Manipal Hospital, Old Airport Road. Verify filter replacement schedule, check refrigerant levels, and test thermostat calibration. Hospital facility contact: Mr. Joseph Thomas.',
                'created_by': rm_south, 'assigned_to': None,
                'status': 'pending', 'priority': 'low',
                'due_date': (now + timedelta(days=10)).date(),
                'team_scope': team_gamma, 'region_scope': south,
            },
        ]

        for task_data in tasks_data:
            Task.objects.get_or_create(
                title=task_data['title'],
                defaults=task_data,
            )
        self.stdout.write(self.style.SUCCESS(f'  [OK] Tasks: {Task.objects.count()} created'))

    # ──────────────────────────────────────────────
    # Visits (with realistic Indian field notes)
    # ──────────────────────────────────────────────
    def _seed_visits(self):
        now = timezone.now()
        agent_ravi = EmployeeProfile.objects.get(employee_id='EMP-005')
        agent_priya = EmployeeProfile.objects.get(employee_id='EMP-006')

        # ── Visit 1: Ravi — Reliance Warehouse Noida (completed, low risk)
        task = Task.objects.filter(title__contains='Reliance Warehouse').first()
        if task:
            Visit.objects.get_or_create(
                task=task,
                started_by=agent_ravi,
                defaults={
                    'status': 'completed',
                    'start_time': now - timedelta(days=2, hours=6),
                    'end_time': now - timedelta(days=2, hours=4),
                    'visit_notes': 'Reached Reliance Jio warehouse at 10:15 AM. Met Mr. Sandeep Tiwari (Site Manager). Fire extinguishers checked — all 18 units serviced within date. Loading dock area clean and organised. Cold storage section maintaining temperature at -18°C as per FSSAI norms. Inventory stacking follows BIS guidelines. No compliance gaps found. Signed off inspection register.',
                    'ai_summary': 'The visit was routine and successful with no major issues reported.',
                    'ai_recommendation': 'Proceed with standard timeline.',
                    'ai_risk_flag': 'low',
                }
            )

        # ── Visit 2: Ravi — Maruti Suzuki Gurugram (completed, low risk)
        task = Task.objects.filter(title__contains='Maruti Suzuki').first()
        if task:
            Visit.objects.get_or_create(
                task=task,
                started_by=agent_ravi,
                defaults={
                    'status': 'completed',
                    'start_time': now - timedelta(days=3, hours=5),
                    'end_time': now - timedelta(days=3, hours=3),
                    'visit_notes': 'Arrived at Maruti Suzuki Gurugram service centre at 11 AM. Met Mr. Deepak Rawat at the warehouse. All 25 air purifier units received — serial numbers cross-checked against PO #MSZ-2026-4891, everything matches. Two units had minor packaging dents but internal product undamaged. Delivery receipt signed and stamped. Warehouse team cooperative throughout.',
                    'ai_summary': 'The visit was routine and successful with no major issues reported.',
                    'ai_recommendation': 'Proceed with standard timeline.',
                    'ai_risk_flag': 'low',
                }
            )

        # ── Visit 3: Ravi — Tata Motors Manesar (completed, medium risk)
        task = Task.objects.filter(title__contains='Tata Motors').first()
        if task:
            Visit.objects.get_or_create(
                task=task,
                started_by=agent_ravi,
                defaults={
                    'status': 'completed',
                    'start_time': now - timedelta(hours=10),
                    'end_time': now - timedelta(hours=7),
                    'visit_notes': 'Visited Tata Motors Manesar plant. Met Mr. Suresh Bansal. KYC documentation partially complete — PAN and GSTIN verified but the authorised signatory Mr. Rohit Mehra was on leave. Mr. Bansal mentioned some confusion regarding the SLA terms for after-hours support. He wants to reschedule the final agreement signing for next Tuesday. Left the welcome kit with reception.',
                    'ai_summary': 'The visit had some minor issues or delays.',
                    'ai_recommendation': 'Follow up within 48 hours to ensure resolution.',
                    'ai_risk_flag': 'medium',
                }
            )

        # ── Visit 4: Priya — Infosys Electronic City (completed, low risk)
        task = Task.objects.filter(title__contains='Infosys').first()
        if task:
            Visit.objects.get_or_create(
                task=task,
                started_by=agent_priya,
                defaults={
                    'status': 'completed',
                    'start_time': now - timedelta(days=1, hours=7),
                    'end_time': now - timedelta(days=1, hours=5),
                    'visit_notes': 'Reached Infosys Electronic City Gate 3 at 9:30 AM. Met Ms. Kavitha Reddy at Building 7 admin office. Collected 42 filled survey forms from facility management team. Overall feedback positive — 85% satisfaction rate mentioned verbally. Minor complaint about response time for weekend AC maintenance requests. Ms. Kavitha requested a dedicated helpline number for urgent issues.',
                    'ai_summary': 'The visit was routine and successful with no major issues reported.',
                    'ai_recommendation': 'Proceed with standard timeline.',
                    'ai_risk_flag': 'low',
                }
            )

        # ── Visit 5: Priya — TVS Motor Hosur (completed, HIGH risk)
        task = Task.objects.filter(title__contains='TVS Motor').first()
        if task:
            Visit.objects.get_or_create(
                task=task,
                started_by=agent_priya,
                defaults={
                    'status': 'completed',
                    'start_time': now - timedelta(days=3, hours=8),
                    'end_time': now - timedelta(days=3, hours=4),
                    'visit_notes': 'Conducted safety audit at TVS Motor Hosur factory. Found 3 out of 12 fire extinguishers past servicing date. Emergency exit on east wing partially blocked by raw material pallets. Two workers on assembly line not wearing safety goggles. Mr. Venkatesh Murthy became angry when these issues were pointed out and refused to sign the non-compliance acknowledgment form. One worker mentioned an unreported hand injury from last Wednesday. PPE stock in storeroom is running critically low.',
                    'ai_summary': 'The visit highlighted severe issues or an extremely dissatisfied customer.',
                    'ai_recommendation': 'Immediate escalation to Regional Manager required.',
                    'ai_risk_flag': 'high',
                }
            )

        # ── Visit 6: Priya — Wipro Whitefield (started, in progress)
        task = Task.objects.filter(title__contains='Wipro').first()
        if task:
            Visit.objects.get_or_create(
                task=task,
                started_by=agent_priya,
                defaults={
                    'status': 'started',
                    'start_time': now - timedelta(hours=2),
                }
            )

        # ── Visit 7: Ravi — SBI ATM Lajpat Nagar (completed before cancellation, medium risk)
        task = Task.objects.filter(title__contains='SBI ATM').first()
        if task:
            Visit.objects.get_or_create(
                task=task,
                started_by=agent_ravi,
                defaults={
                    'status': 'completed',
                    'start_time': now - timedelta(days=4, hours=4),
                    'end_time': now - timedelta(days=4, hours=3),
                    'visit_notes': 'Reached SBI ATM Lajpat Nagar. The cash dispenser issue was already resolved by SBI\'s own maintenance team before I arrived. Mr. Pankaj Gupta confirmed the screen flickering was due to a loose HDMI cable which they fixed internally. He apologised for the late update. No action needed from our side.',
                    'ai_summary': 'The visit was routine and successful with no major issues reported.',
                    'ai_recommendation': 'Proceed with standard timeline.',
                    'ai_risk_flag': 'low',
                }
            )

        self.stdout.write(self.style.SUCCESS(f'  [OK] Visits: {Visit.objects.count()} created'))

    # ──────────────────────────────────────────────
    # Activity Logs
    # ──────────────────────────────────────────────
    def _seed_activity_logs(self):
        now = timezone.now()
        tl_user = User.objects.get(username='tl_alpha')
        rm_north_user = User.objects.get(username='rm_north')
        rm_south_user = User.objects.get(username='rm_south')
        agent_ravi_user = User.objects.get(username='agent_ravi')
        agent_priya_user = User.objects.get(username='agent_priya')

        tasks = list(Task.objects.all().order_by('id'))
        visits = list(Visit.objects.all().order_by('id'))

        if not tasks:
            self.stdout.write(self.style.WARNING('  [SKIP] No tasks found, skipping activity logs'))
            return

        logs_data = []

        # Task creation logs
        for t in tasks:
            creator_user = t.created_by.user
            logs_data.append((
                creator_user, 'created', 'task', t.id,
                f'Task "{t.title[:50]}..." created.',
                t.created_at or now - timedelta(days=5)
            ))

        # Task assignment logs
        for t in tasks:
            if t.assigned_to:
                assigner_user = t.created_by.user
                logs_data.append((
                    assigner_user, 'assigned', 'task', t.id,
                    f'Task assigned to {t.assigned_to.user.first_name} {t.assigned_to.user.last_name}.',
                    (t.created_at or now - timedelta(days=5)) + timedelta(minutes=15)
                ))

        # Visit logs
        for v in visits:
            logs_data.append((
                v.started_by.user, 'started', 'visit', v.id,
                f'Visit started for task #{v.task.id} — {v.task.title[:40]}...',
                v.start_time
            ))
            if v.status == 'completed' and v.end_time:
                logs_data.append((
                    v.started_by.user, 'completed', 'visit', v.id,
                    f'Visit completed for task #{v.task.id}. Risk: {v.ai_risk_flag}.',
                    v.end_time
                ))

        # Status change logs for completed/cancelled tasks
        for t in tasks:
            if t.status in ('completed', 'cancelled'):
                changer = t.created_by.user
                logs_data.append((
                    changer, 'status_changed', 'task', t.id,
                    f'Task status changed to {t.get_status_display()}.',
                    (t.created_at or now - timedelta(days=4)) + timedelta(days=1)
                ))

        count = 0
        for user, action, entity_type, entity_id, description, timestamp in logs_data:
            _, created = ActivityLog.objects.get_or_create(
                user=user,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                description=description,
            )
            if created:
                count += 1
        self.stdout.write(self.style.SUCCESS(f'  [OK] Activity Logs: {ActivityLog.objects.count()} entries ({count} new)'))

    # ──────────────────────────────────────────────
    # Print Credentials
    # ──────────────────────────────────────────────
    def _print_credentials(self):
        self.stdout.write(self.style.MIGRATE_HEADING('\n-- Login Credentials --\n'))
        credentials = [
            ('admin_user',    'admin123', 'Admin',            'Arjun Mehta',     '-',           '-'),
            ('rm_north',      'pass123',  'Regional Manager', 'Rajesh Kapoor',   '-',           'North'),
            ('rm_south',      'pass123',  'Regional Manager', 'Sunita Iyer',     '-',           'South'),
            ('tl_alpha',      'pass123',  'Team Lead',        'Vikram Sharma',   'Team Alpha',  'North'),
            ('agent_ravi',    'pass123',  'Field Agent',      'Ravi Verma',      'Team Alpha',  'North'),
            ('agent_priya',   'pass123',  'Field Agent',      'Priya Nair',      'Team Gamma',  'South'),
            ('auditor_meera', 'pass123',  'Auditor',          'Meera Deshmukh',  '-',           '-'),
        ]

        header = f"  {'Username':<18} {'Password':<12} {'Role':<20} {'Name':<18} {'Team':<14} {'Region'}"
        self.stdout.write(header)
        self.stdout.write('  ' + '-' * 95)
        for username, password, role, name, team, region in credentials:
            self.stdout.write(f"  {username:<18} {password:<12} {role:<20} {name:<18} {team:<14} {region}")
