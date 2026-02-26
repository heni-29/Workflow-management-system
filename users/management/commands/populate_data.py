from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from projects.models import Project
from tasks.models import Task, TaskStatus, TaskPriority
from activities.models import ActivityLog

User = get_user_model()


class Command(BaseCommand):
    help = 'Wipe all existing data and seed with CS undergrad/grad course projects'

    def _due(self, offset_days):
        return date.today() + timedelta(days=offset_days)

    def handle(self, *args, **options):
        # ── 1. Wipe existing data ──────────────────────────────────────
        self.stdout.write('🗑  Clearing existing data...')
        ActivityLog.objects.all().delete()
        Task.objects.all().delete()
        Project.objects.all().delete()
        # Remove non-superuser team members from previous runs
        User.objects.filter(is_superuser=False).exclude(username='djangoadmin').delete()
        self.stdout.write(self.style.SUCCESS('   Done.\n'))

        # ── 2. Admin / owner ──────────────────────────────────────────
        admin = User.objects.filter(username='djangoadmin').first()
        if not admin:
            self.stdout.write(self.style.ERROR(
                'Superuser "djangoadmin" not found. Run create_superuser first.'
            ))
            return

        # ── 3. Team members (students) ─────────────────────────────────
        members_info = [
            ('heni',    'Heni',    'Prajapati', 'heni@cs.edu'),
            ('priya',   'Priya',   'Sharma',    'priya@cs.edu'),
            ('marcus',  'Marcus',  'Chen',      'marcus@cs.edu'),
            ('sofia',   'Sofia',   'Nguyen',    'sofia@cs.edu'),
            ('james',   'James',   'Okafor',    'james@cs.edu'),
            ('leila',   'Leila',   'Hassan',    'leila@cs.edu'),
        ]
        team = {'admin': admin}
        for username, first, last, email in members_info:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'first_name': first, 'last_name': last, 'email': email},
            )
            if created:
                user.set_password('pass1234')
                user.save()
            team[username] = user
        self.stdout.write(self.style.SUCCESS(f'👥  Team ready ({len(team)} members)\n'))

        # ── 4. Projects ────────────────────────────────────────────────
        # Format: name, description, owner_key, [member_keys]
        projects_data = [
            # ── UNDERGRAD ──────────────────────────────────────────────
            {
                'name': 'OS: Custom Unix Shell',
                'description': (
                    'CS 3600 – Operating Systems. Build a POSIX-compatible shell in C supporting '
                    'pipes, I/O redirection, background jobs, signal handling, and a built-in '
                    'command history. Due end of semester.'
                ),
                'owner': 'heni',
                'members': ['heni', 'marcus'],
            },
            {
                'name': 'Algorithms: Graph Shortest-Path Visualiser',
                'description': (
                    'CS 3510 – Design & Analysis of Algorithms. Implement and visually compare '
                    'Dijkstra, Bellman-Ford, and A* on weighted graphs. Interactive web UI shows '
                    'step-by-step exploration. Written in Python + D3.js.'
                ),
                'owner': 'priya',
                'members': ['priya', 'heni', 'sofia'],
            },
            {
                'name': 'Networks: Reliable UDP File Transfer',
                'description': (
                    'CS 3251 – Computer Networking. Implement a stop-and-wait and sliding-window '
                    'protocol on top of UDP in Python to achieve reliable, in-order delivery with '
                    'congestion control. Benchmarked against raw TCP.'
                ),
                'owner': 'marcus',
                'members': ['marcus', 'james'],
            },
            {
                'name': 'Databases: Course Registration System',
                'description': (
                    'CS 4400 – Intro to Database Systems. Full-stack web app for university course '
                    'registration built with Flask, PostgreSQL, and raw SQL (no ORM). Implements '
                    'ER diagram, normalised schema, stored procedures, and transaction isolation.'
                ),
                'owner': 'sofia',
                'members': ['sofia', 'leila', 'priya'],
            },
            {
                'name': 'Computer Architecture: 5-Stage RISC-V Pipeline',
                'description': (
                    'CS 3220 – Computer Architecture. Design and simulate a 5-stage (IF/ID/EX/MEM/WB) '
                    'RISC-V pipeline in SystemVerilog with hazard detection, data forwarding, '
                    'and branch prediction. Tested against the RISC-V test suite.'
                ),
                'owner': 'james',
                'members': ['james', 'marcus', 'heni'],
            },
            {
                'name': 'Software Engineering: Peer Tutoring Platform',
                'description': (
                    'CS 3300 – Software Engineering. Agile team project: RESTful Django + React '
                    'platform where students sign up as tutors or tutees, schedule sessions, and '
                    'leave reviews. Includes CI/CD via GitHub Actions and full test coverage.'
                ),
                'owner': 'leila',
                'members': ['leila', 'sofia', 'priya', 'heni'],
            },
            # ── GRAD ───────────────────────────────────────────────────
            {
                'name': 'Distributed Systems: Raft Consensus',
                'description': (
                    'CS 7210 – Distributed Computing. Implement the Raft consensus algorithm in Go '
                    'from scratch: leader election, log replication, snapshotting, and membership '
                    'changes. Evaluated under network partitions with a Jepsen-inspired test harness.'
                ),
                'owner': 'heni',
                'members': ['heni', 'marcus', 'james'],
            },
            {
                'name': 'ML: Transformer for Code Summarization',
                'description': (
                    'CS 7643 – Deep Learning. Fine-tune a CodeBERT/T5 transformer on the CodeSearchNet '
                    'corpus to generate docstrings from function bodies. Evaluate BLEU/ROUGE/METEOR '
                    'and ablate attention heads. Implemented in PyTorch + HuggingFace.'
                ),
                'owner': 'priya',
                'members': ['priya', 'sofia', 'leila'],
            },
            {
                'name': 'Compilers: LLVM-based Optimising Compiler',
                'description': (
                    'CS 8803 – Compilers. Build a compiler for a statically-typed subset of Python '
                    '(type annotations required) that emits LLVM IR. Implement SSA construction, '
                    'dead-code elimination, loop-invariant code motion, and register allocation.'
                ),
                'owner': 'marcus',
                'members': ['marcus', 'heni'],
            },
            {
                'name': 'Advanced OS: Memory-Safe Kernel Module',
                'description': (
                    'CS 8803 – Advanced Operating Systems. Write a Linux kernel module in Rust '
                    'implementing a per-process memory-safe slab allocator. Benchmark allocation '
                    'latency vs. glibc malloc under multithreaded load.'
                ),
                'owner': 'james',
                'members': ['james', 'sofia', 'heni'],
            },
            {
                'name': 'AI: Multi-Agent Pathfinding Simulator',
                'description': (
                    'CS 6601 – Artificial Intelligence. Implement CBS (Conflict-Based Search) and '
                    'ICTS for optimal multi-agent pathfinding on grid maps. Compare scalability '
                    'with 4–64 agents. Visualised in a real-time Pygame interface.'
                ),
                'owner': 'sofia',
                'members': ['sofia', 'leila', 'priya'],
            },
            {
                'name': 'Systems Security: Kernel Exploit & Mitigation',
                'description': (
                    'CS 6265 – Information Security Lab. Conduct a stack-smashing + ROP-chain exploit '
                    'against a vulnerable kernel module in a VM sandbox, then implement and evaluate '
                    'three mitigations (ASLR, stack canaries, CFI). Written report + demo.'
                ),
                'owner': 'leila',
                'members': ['leila', 'james', 'marcus'],
            },
        ]

        project_objs = {}
        for pd in projects_data:
            owner = team[pd['owner']]
            proj = Project.objects.create(
                name=pd['name'],
                description=pd['description'],
                created_by=owner,
            )
            for m_key in pd['members']:
                proj.members.add(team[m_key])
            project_objs[pd['name']] = proj
            self.stdout.write(self.style.SUCCESS(f'  ✅ {proj.name}'))

        self.stdout.write('')

        # ── 5. Tasks ───────────────────────────────────────────────────
        # (title, status, priority, assignee_key, due_offset_days)
        T, IP, R, D = TaskStatus.TODO, TaskStatus.IN_PROGRESS, TaskStatus.REVIEW, TaskStatus.DONE
        H, M, L = TaskPriority.HIGH, TaskPriority.MEDIUM, TaskPriority.LOW

        tasks_map = {
            'OS: Custom Unix Shell': [
                ('Read & tokenise command input',            D,  H, 'heni',   -30),
                ('Implement pipe operator (|)',              D,  H, 'marcus', -22),
                ('I/O redirection (<, >, >>)',               D,  H, 'heni',   -15),
                ('Background job control (&, fg, bg)',       R,  H, 'marcus',   5),
                ('Signal handling (SIGINT, SIGTSTP)',        IP, M, 'heni',     9),
                ('Built-in command: cd, exit, history',      IP, M, 'marcus',  12),
                ('Command history with up/down arrows',      T,  M, 'heni',    18),
                ('Tab-completion for file paths',            T,  L, 'marcus',  25),
                ('Write comprehensive test suite',           T,  H, 'heni',    20),
                ('Final report & demo recording',            T,  M, 'marcus',  28),
            ],
            'Algorithms: Graph Shortest-Path Visualiser': [
                ('Implement adjacency list graph structure', D,  H, 'priya',  -25),
                ('Dijkstra\'s algorithm (min-heap)',          D,  H, 'heni',   -18),
                ('Bellman-Ford with negative-edge support',  D,  H, 'sofia',  -10),
                ('A* with Euclidean heuristic',              R,  H, 'priya',    4),
                ('D3.js force-directed graph rendering',     IP, M, 'sofia',    8),
                ('Step-by-step animation controls',          IP, M, 'heni',    11),
                ('Upload custom graph via JSON/CSV',         T,  M, 'priya',   16),
                ('Performance comparison table & charts',    T,  M, 'sofia',   20),
                ('Deployed to GitHub Pages',                 T,  L, 'heni',    22),
                ('Write-up: complexity analysis',            T,  H, 'priya',   25),
            ],
            'Networks: Reliable UDP File Transfer': [
                ('Design packet format & header fields',     D,  H, 'marcus', -20),
                ('Implement stop-and-wait protocol',         D,  H, 'james',  -12),
                ('Sliding-window with selective repeat',     D,  H, 'marcus',  -5),
                ('Simulate packet loss & corruption',        R,  H, 'james',    3),
                ('Congestion control (AIMD)',                IP, H, 'marcus',   9),
                ('Multi-file transfer session support',      IP, M, 'james',   13),
                ('Throughput benchmarking vs TCP',           T,  M, 'marcus',  18),
                ('Unit tests for edge cases',                T,  M, 'james',   20),
                ('Lab report with Wireshark captures',       T,  H, 'marcus',  24),
            ],
            'Databases: Course Registration System': [
                ('Draw entity-relationship (ER) diagram',   D,  H, 'sofia',  -28),
                ('Normalise to 3NF schema',                  D,  H, 'leila',  -21),
                ('DDL scripts: tables, indexes, FKs',        D,  H, 'sofia',  -14),
                ('CRUD stored procedures for enrollment',    D,  M, 'priya',   -7),
                ('Flask frontend: student course view',      R,  H, 'leila',    4),
                ('Admin panel: seat limits & waitlists',     IP, H, 'priya',    8),
                ('Transaction isolation for race conditions',IP, H, 'sofia',   11),
                ('Query optimisation & EXPLAIN ANALYSE',     T,  M, 'leila',   17),
                ('Load testing with 500 concurrent users',   T,  M, 'priya',   20),
                ('Final demo: live registration walkthrough',T,  H, 'sofia',   24),
            ],
            'Computer Architecture: 5-Stage RISC-V Pipeline': [
                ('Implement IF stage: instruction fetch',    D,  H, 'james',  -30),
                ('Implement ID stage: register file',        D,  H, 'marcus', -23),
                ('Implement EX stage: ALU & branch logic',   D,  H, 'james',  -16),
                ('Implement MEM stage: data memory',         D,  H, 'heni',    -9),
                ('Implement WB stage: write-back',           R,  H, 'marcus',   2),
                ('Hazard detection unit (data hazards)',      R,  H, 'james',    5),
                ('Data forwarding (bypass) unit',            IP, H, 'heni',     9),
                ('Branch predictor: 2-bit saturating',       IP, M, 'marcus',  12),
                ('Run RISC-V test suite, fix failures',      T,  H, 'james',   16),
                ('Performance report: IPC analysis',         T,  M, 'heni',    20),
            ],
            'Software Engineering: Peer Tutoring Platform': [
                ('Define user stories & acceptance criteria', D, H, 'leila',  -35),
                ('Set up Django REST + React monorepo',       D, H, 'heni',   -28),
                ('User auth: register, login, JWT tokens',   D, H, 'priya',  -21),
                ('Tutor profile & subject-area search',      D, M, 'sofia',  -14),
                ('Session booking & calendar integration',   R, H, 'leila',    5),
                ('Real-time chat (Django Channels/WS)',      IP, H, 'heni',    9),
                ('Rating & review system',                   IP, M, 'priya',  12),
                ('GitHub Actions CI: lint + test + build',   T, M, 'sofia',   16),
                ('Deploy to Render (backend + Postgres)',     T, H, 'leila',   18),
                ('Write technical design document',          T, L, 'priya',   22),
            ],
            'Distributed Systems: Raft Consensus': [
                ('Study Raft paper & design state machine',  D, H, 'heni',   -40),
                ('Leader election & vote request RPC',       D, H, 'marcus', -32),
                ('Log replication: AppendEntries RPC',       D, H, 'james',  -24),
                ('Commit & state machine apply logic',       D, H, 'heni',   -16),
                ('Follower log compaction (snapshotting)',    R, H, 'marcus',   4),
                ('Membership changes: joint consensus',       IP, H, 'james',   9),
                ('Network partition test harness',           IP, H, 'heni',   13),
                ('Jepsen-style linearisability checker',     T, H, 'marcus',  18),
                ('Performance under 3/5/7-node clusters',   T, M, 'james',   22),
                ('Research paper write-up (10 pages)',       T, H, 'heni',   25),
            ],
            'ML: Transformer for Code Summarization': [
                ('Obtain & preprocess CodeSearchNet data',   D, H, 'priya',  -35),
                ('Tokeniser fine-tuning for code syntax',    D, H, 'sofia',  -27),
                ('Baseline: CodeBERT encoder + MLP head',    D, H, 'priya',  -19),
                ('Fine-tune CodeT5 seq2seq model',           D, H, 'leila',  -11),
                ('Implement BLEU/ROUGE/METEOR evaluation',   R, H, 'sofia',    3),
                ('Attention head ablation study',            IP, M, 'priya',   8),
                ('Qualitative error analysis (50 samples)',  IP, M, 'leila',  11),
                ('Hyperparameter sweep (lr, batch, warmup)', T, M, 'sofia',  16),
                ('Write NeurIPS-style paper draft',          T, H, 'priya',  20),
                ('Prepare presentation slides & demo',       T, M, 'leila',  24),
            ],
            'Compilers: LLVM-based Optimising Compiler': [
                ('Lexer & parser for typed-Python subset',   D, H, 'marcus', -38),
                ('AST definition & pretty-printer',          D, H, 'heni',   -30),
                ('Type checker with Hindley-Milner',         D, H, 'marcus', -22),
                ('IR generation: 3-address code → LLVM IR',  D, H, 'heni',  -14),
                ('SSA construction (dominance frontiers)',    R, H, 'marcus',   4),
                ('Dead-code elimination pass',               IP, M, 'heni',    8),
                ('Loop-invariant code motion (LICM)',         IP, H, 'marcus', 12),
                ('Register allocation: graph colouring',     T, H, 'heni',   17),
                ('Run LLVM nightly benchmarks',              T, M, 'marcus',  21),
                ('Final write-up & recorded demo',           T, M, 'heni',   25),
            ],
            'Advanced OS: Memory-Safe Kernel Module': [
                ('Set up Rust kernel dev environment',       D, H, 'james',  -30),
                ('Design slab allocator data structures',    D, H, 'sofia',  -22),
                ('Implement object cache allocation',        D, H, 'james',  -14),
                ('Implement per-CPU partial slab lists',     R, H, 'sofia',    5),
                ('Memory safety audit: unsafe block review', R, H, 'james',    7),
                ('Benchmark: alloc latency (single-thread)', IP, M, 'sofia',  11),
                ('Benchmark: alloc latency (32-thread)',     IP, M, 'james',  14),
                ('Compare vs. glibc malloc & jemalloc',     T, M, 'sofia',   19),
                ('Kernel crash regression tests',            T, H, 'james',   22),
                ('Conference-style report (8 pages)',        T, H, 'sofia',   26),
            ],
            'AI: Multi-Agent Pathfinding Simulator': [
                ('Implement grid map loader (MovingAI)',     D, H, 'sofia',  -28),
                ('Single-agent A* baseline',                 D, H, 'leila',  -21),
                ('CBS (Conflict-Based Search) framework',    D, H, 'sofia',  -13),
                ('ICTS (Increasing Cost Tree Search)',        R, H, 'leila',    4),
                ('Disjoint splitting enhancement for CBS',   IP, H, 'sofia',   8),
                ('Pygame real-time visualiser',              IP, M, 'leila',  12),
                ('Scalability experiments (4–64 agents)',    T, M, 'sofia',   17),
                ('Sub-optimal (bounded) CBS variant',        T, H, 'leila',   20),
                ('Ablation: heuristics comparison',          T, M, 'sofia',   23),
                ('Final report with runtime plots',          T, H, 'leila',   27),
            ],
            'Systems Security: Kernel Exploit & Mitigation': [
                ('Analyse vulnerable kernel module source',  D, H, 'leila',  -25),
                ('Craft stack-smashing exploit (ret2libc)',  D, H, 'james',  -17),
                ('ROP-chain exploit bypassing NX bit',       D, H, 'leila',   -9),
                ('Implement ASLR mitigation & measure',      R, H, 'james',    3),
                ('Stack canary implementation & testing',    R, H, 'leila',    6),
                ('CFI (Control Flow Integrity) prototype',   IP, H, 'james',  10),
                ('Run exploit against each mitigation',      IP, M, 'leila',  14),
                ('Timing & overhead benchmarks',             T, M, 'james',   18),
                ('Threat model & security analysis write-up',T, H, 'leila',  22),
                ('Live demo: exploit → patch walkthrough',   T, H, 'james',   25),
            ],
        }

        total_tasks = 0
        for proj_name, task_list in tasks_map.items():
            proj = project_objs.get(proj_name)
            if not proj:
                continue
            for title, status, priority, assignee_key, due_offset in task_list:
                Task.objects.create(
                    title=title,
                    project=proj,
                    status=status,
                    priority=priority,
                    assignee=team.get(assignee_key, admin),
                    reporter=team.get(proj.created_by.username, admin),
                    due_date=self._due(due_offset),
                )
                total_tasks += 1

        self.stdout.write(self.style.SUCCESS(f'\n📋  Created {total_tasks} tasks\n'))

        # ── 6. Activity logs ───────────────────────────────────────────
        activities = [
            (team['heni'],   'created',   'project', 'Started OS: Custom Unix Shell project'),
            (team['marcus'], 'completed', 'task',    'Finished implementing pipe operator'),
            (team['priya'],  'created',   'project', 'Kicked off Graph Shortest-Path Visualiser'),
            (team['sofia'],  'updated',   'task',    'Moved A* implementation → In Progress'),
            (team['james'],  'created',   'project', 'Started 5-Stage RISC-V Pipeline project'),
            (team['leila'],  'created',   'project', 'Launched Peer Tutoring Platform project'),
            (team['heni'],   'completed', 'task',    'Completed Raft leader election RPC'),
            (team['priya'],  'updated',   'task',    'Fine-tuned CodeT5 model checkpoint saved'),
            (team['marcus'], 'updated',   'task',    'SSA construction pass merged to main'),
            (team['james'],  'completed', 'task',    'ROP-chain exploit successfully demonstrated'),
            (team['sofia'],  'created',   'task',    'Added CBS disjoint splitting task'),
            (team['leila'],  'updated',   'task',    'Session booking feature moved to Review'),
        ]
        for user, verb, target_type, detail_text in activities:
            ActivityLog.objects.create(
                user=user,
                verb=verb,
                target_type=target_type,
                detail={'message': detail_text},
            )

        self.stdout.write(self.style.SUCCESS('✅  CS project data seeded successfully!'))
        self.stdout.write(f'   {len(projects_data)} projects | {total_tasks} tasks | {len(activities)} activity logs\n')
