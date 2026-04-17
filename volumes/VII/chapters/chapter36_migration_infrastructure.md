Chapter 36: Migration Infrastructure

36.1 Migration as Engineering Discipline

System migration represents one of the highest-risk activities in software engineering. Unlike new development where absence of functionality is expected, migrations must preserve existing capabilities while introducing new ones, often across the entire technology stack. The clean room methodology applies particularly well to migration scenarios where the existing system serves as the reference implementation.

Migration strategies divide between big-bang approaches that cut over entire systems at once and incremental approaches that migrate piece by piece. Big-bang migrations concentrate risk into single events, demanding extensive testing and often requiring maintenance freezes. Incremental approaches distribute risk over time but require sophisticated infrastructure to support operation of both old and new systems simultaneously.

The Strangler Fig Pattern provides the dominant incremental migration approach. Named after a tree that gradually envelops and replaces its host, this pattern routes traffic incrementally from legacy to new systems until the legacy system can be retired. This chapter examines the infrastructure required to support such migrations safely.

36.2 Strangler Fig Architecture

The Strangler Fig Pattern relies on routing infrastructure that can direct requests to either legacy or modernized implementations based on configurable rules:

    ┌─────────────────────────────────────────────────────────┐
    │                      Clients                             │
    └──────────────────────┬──────────────────────────────────┘
                           │
            ┌──────────────▼──────────────┐
            │      API Gateway /          │
            │      Load Balancer          │
            │  (Routing Decisions)        │
            └──────────────┬──────────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
      ┌───────▼──────┐    │    ┌──────▼───────┐
      │   Legacy     │    │    │   New        │
      │   System     │◄───┴───►│   System     │
      │              │         │              │
      └──────────────┘         └──────────────┘
              │                       │
              └──────────┬────────────┘
                         │
              ┌──────────▼──────────┐
              │    Shared Data      │
              │    (Eventual        │
              │     Consistency)    │
              └─────────────────────┘

Router responsibilities include:
- Request classification (which system should handle it)
- Traffic percentage allocation (gradual migration)
- Failure handling (fallback to legacy)
- Observability (tracking routing decisions)
- Feature flags (runtime reconfiguration)

36.3 Routing Infrastructure

HTTP-based routing uses API Gateway patterns:

    # Nginx routing configuration
    upstream legacy_backend {
        server legacy-api-1:8080;
        server legacy-api-2:8080;
    }

    upstream modern_backend {
        server modern-api-1:8080;
        server modern-api-2:8080;
    }

    # Router with header-based routing
    map $http_x_api_version $backend {
        default legacy_backend;
        "v2" modern_backend;
        "v1" legacy_backend;
    }

    server {
        listen 80;
        
        location /api/ {
            proxy_pass http://$backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            
            # Circuit breaker for modern backend
            proxy_next_upstream error timeout http_502 http_503;
            proxy_next_upstream_tries 2;
        }
    }

Percentage-based routing for gradual migration:

    # Kong API Gateway configuration
    plugins:
      - name: canary
        config:
          percentage: 10  # 10% to new system
          upstream_fallback: true
          upstream: modern-backend

    # Or with header-based routing for testing
      - name: key-auth
      - name: canary
        config:
          percentage: 0
          upstream_host: modern-backend
          hash: header
          hash_header: x-canary-test

Envoy proxy configuration:

    static_resources:
      listeners:
      - address:
          socket_address:
            address: 0.0.0.0
            port_value: 80
        filter_chains:
        - filters:
          - name: envoy.filters.http.router
            typed_config:
              "@type": type.googleapis.com/envoy.extensions.filters.http.router.v3.Router

      clusters:
      - name: legacy_cluster
        connect_timeout: 5s
        type: STRICT_DNS
        lb_policy: ROUND_ROBIN
        load_assignment:
          cluster_name: legacy_cluster
          endpoints:
          - lb_endpoints:
            - endpoint:
                address:
                  socket_address:
                    address: legacy-svc
                    port_value: 8080

      - name: modern_cluster
        connect_timeout: 5s
        type: STRICT_DNS
        lb_policy: ROUND_ROBIN
        load_assignment:
          cluster_name: modern_cluster
          endpoints:
          - lb_endpoints:
            - endpoint:
                address:
                  socket_address:
                    address: modern-svc
                    port_value: 8080

      # Route configuration with weighted routing
      route_config:
        virtual_hosts:
        - name: api
          domains: ["api.example.com"]
          routes:
          - match:
              prefix: "/"
            route:
              weighted_clusters:
                runtime_key_prefix: routing
                clusters:
                - name: legacy_cluster
                  weight: 90
                - name: modern_cluster
                  weight: 10

36.4 Application-Level Routing

Application routers provide more sophisticated logic:

    from typing import Callable, Optional
    from dataclasses import dataclass
    import random
    import logging

    @dataclass
    class RoutingRule:
        path_pattern: str
        target_system: str
        percentage: int = 100
        predicate: Optional[Callable] = None

    class MigrationRouter:
        def __init__(self):
            self.rules: list[RoutingRule] = []
            self.legacy_client = LegacyClient()
            self.modern_client = ModernClient()
            self.logger = logging.getLogger(__name__)

        def add_rule(self, rule: RoutingRule):
            self.rules.append(rule)

        def route(self, request_path: str, context: dict) -> dict:
            """Route request to appropriate system."""
            rule = self._match_rule(request_path)
            
            if not rule:
                return self._call_legacy(request_path, context)
            
            # Check predicate if defined
            if rule.predicate and not rule.predicate(context):
                return self._call_legacy(request_path, context)
            
            # Percentage-based routing
            if random.randint(1, 100) <= rule.percentage:
                try:
                    return self._call_modern(request_path, context)
                except ModernSystemException:
                    self.logger.warning(
                        f"Modern system failed for {request_path}, falling back"
                    )
                    return self._call_legacy(request_path, context)
            else:
                return self._call_legacy(request_path, context)

        def _match_rule(self, path: str) -> Optional[RoutingRule]:
            for rule in self.rules:
                if path.startswith(rule.path_pattern):
                    return rule
            return None

        def _call_legacy(self, path: str, context: dict) -> dict:
            return self.legacy_client.request(path, context)

        def _call_modern(self, path: str, context: dict) -> dict:
            return self.modern_client.request(path, context)

Usage:

    router = MigrationRouter()
    
    # Migrate user endpoints first, excluding admin features
    router.add_rule(RoutingRule(
        path_pattern="/api/users",
        target_system="modern",
        percentage=25,
        predicate=lambda ctx: not ctx.get('is_admin', False)
    ))
    
    # Read-only endpoints at 50%
    router.add_rule(RoutingRule(
        path_pattern="/api/reports",
        target_system="modern",
        percentage=50
    ))
    
    # Full migration for specific endpoint
    router.add_rule(RoutingRule(
        path_pattern="/api/health",
        target_system="modern",
        percentage=100
    ))

36.5 Data Migration Strategies

Data migration presents distinct challenges from code migration:

Read-Through Pattern:

    class ReadThroughCache:
        def __init__(self, legacy_db, modern_db, migration_status):
            self.legacy = legacy_db
            self.modern = modern_db
            self.status = migration_status

        def get(self, entity_id: str):
            # Try modern first
            if self.status.is_migrated(entity_id):
                result = self.modern.get(entity_id)
                if result:
                    return result
            
            # Fall back to legacy
            result = self.legacy.get(entity_id)
            
            # Backfill to modern
            if result:
                self.modern.put(entity_id, result)
            
            return result

        def put(self, entity_id: str, data: dict):
            # Write to both during migration
            self.legacy.put(entity_id, data)
            self.modern.put(entity_id, data)

Migration Status Tracking:

    from enum import Enum
    import datetime

    class MigrationStatus(Enum):
        PENDING = "pending"
        IN_PROGRESS = "in_progress"
        COMPLETED = "completed"
        FAILED = "failed"

    class MigrationTracker:
        def __init__(self, db):
            self.db = db

        def get_status(self, entity_id: str) -> MigrationStatus:
            row = self.db.query(
                "SELECT status FROM migration_status WHERE entity_id = %s",
                (entity_id,)
            )
            if row:
                return MigrationStatus(row[0])
            return MigrationStatus.PENDING

        def mark_in_progress(self, entity_id: str):
            self.db.execute(
                """INSERT INTO migration_status 
                   (entity_id, status, started_at)
                   VALUES (%s, %s, %s)
                   ON CONFLICT (entity_id) DO UPDATE
                   SET status = EXCLUDED.status,
                       started_at = EXCLUDED.started_at""",
                (entity_id, MigrationStatus.IN_PROGRESS.value, datetime.utcnow())
            )

        def mark_completed(self, entity_id: str, migration_id: str):
            self.db.execute(
                """UPDATE migration_status
                   SET status = %s, completed_at = %s, migration_id = %s
                   WHERE entity_id = %s""",
                (MigrationStatus.COMPLETED.value, datetime.utcnow(), migration_id, entity_id)
            )

36.6 Dual-Write Pattern

Dual-write ensures both systems maintain consistent state:

    class DualWriteRepository:
        def __init__(self, legacy_repo, modern_repo, write_mode='async'):
            self.legacy = legacy_repo
            self.modern = modern_repo
            self.write_mode = write_mode
            self.outbox = []  # For async writes

        def save(self, entity):
            """Save to both repositories."""
            # Always write to legacy (source of truth during migration)
            legacy_result = self.legacy.save(entity)
            
            if self.write_mode == 'sync':
                # Synchronous write to modern
                try:
                    self.modern.save(entity)
                except Exception as e:
                    # Log but don't fail - eventual consistency
                    logger.error(f"Modern write failed: {e}")
            else:
                # Asynchronous via outbox pattern
                self.outbox.append(('modern', 'save', entity))
            
            return legacy_result

        def process_outbox(self):
            """Process pending async writes."""
            while self.outbox:
                target, operation, entity = self.outbox.pop(0)
                try:
                    if target == 'modern' and operation == 'save':
                        self.modern.save(entity)
                except Exception as e:
                    # Re-queue for retry
                    self.outbox.append((target, operation, entity))
                    logger.error(f"Outbox processing failed: {e}")
                    break

    # Background worker
    def outbox_worker(repository, interval=5):
        while True:
            repository.process_outbox()
            time.sleep(interval)

36.7 Change Data Capture (CDC)

CDC captures database changes for synchronization:

Debezium configuration:

    # debezium-connector.json
    {
        "name": "inventory-connector",
        "config": {
            "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
            "database.hostname": "legacy-db",
            "database.port": "5432",
            "database.user": "debezium",
            "database.password": "${secrets:db_password}",
            "database.dbname": "inventory",
            "database.server.name": "legacy",
            "table.include.list": "public.orders,public.customers",
            "plugin.name": "pgoutput",
            "slot.name": "debezium_slot",
            "publication.name": "dbz_publication",
            "transforms": "route",
            "transforms.route.type": "org.apache.kafka.connect.transforms.RegexRouter",
            "transforms.route.regex": "([^.]+)\\.([^.]+)\\.([^.]+)",
            "transforms.route.replacement": "$3"
        }
    }

Kafka consumer for synchronization:

    from confluent_kafka import Consumer, KafkaError
    import json

    class CDCConsumer:
        def __init__(self, bootstrap_servers, group_id, modern_db):
            self.consumer = Consumer({
                'bootstrap.servers': bootstrap_servers,
                'group.id': group_id,
                'auto.offset.reset': 'earliest',
                'enable.auto.commit': False
            })
            self.modern_db = modern_db

        def subscribe(self, topics):
            self.consumer.subscribe(topics)

        def process_messages(self):
            while True:
                msg = self.consumer.poll(timeout=1.0)
                
                if msg is None:
                    continue
                
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        logger.error(msg.error())
                        break
                
                # Parse CDC event
                event = json.loads(msg.value().decode('utf-8'))
                self.apply_change(event)
                
                # Commit offset
                self.consumer.commit(msg)

        def apply_change(self, event: dict):
            """Apply CDC event to modern database."""
            operation = event['op']  # c=create, u=update, d=delete
            table = event['source']['table']
            
            if operation == 'c':
                self.modern_db.insert(table, event['after'])
            elif operation == 'u':
                self.modern_db.update(table, event['after'])
            elif operation == 'd':
                self.modern_db.delete(table, event['before']['id'])

Event transformation:

    def transform_customer_record(event):
        """Transform legacy customer to new format."""
        before = event.get('before', {})
        after = event.get('after', {})
        
        if after:
            after['full_name'] = f"{after['first_name']} {after['last_name']}"
            del after['first_name']
            del after['last_name']
            
            # Convert legacy status codes
            status_mapping = {
                'A': 'active',
                'I': 'inactive',
                'P': 'pending'
            }
            after['status'] = status_mapping.get(
                after.get('status', 'P'), 
                'pending'
            )
        
        return event

36.8 Data Consistency Verification

Consistency checking between systems:

    import hashlib
    import json
    from typing import List, Tuple

    class ConsistencyChecker:
        def __init__(self, legacy_db, modern_db):
            self.legacy = legacy_db
            self.modern = modern_db
            self.discrepancies = []

        def check_entity(self, entity_id: str, table: str) -> bool:
            """Check if entity is consistent between systems."""
            legacy_data = self.legacy.get(table, entity_id)
            modern_data = self.modern.get(table, entity_id)
            
            if legacy_data is None and modern_data is None:
                return True
            
            if legacy_data is None or modern_data is None:
                self.discrepancies.append({
                    'entity_id': entity_id,
                    'table': table,
                    'type': 'missing',
                    'legacy_null': legacy_data is None,
                    'modern_null': modern_data is None
                })
                return False
            
            # Normalize before comparison
            legacy_normalized = self._normalize(legacy_data)
            modern_normalized = self._normalize(modern_data)
            
            if legacy_normalized != modern_normalized:
                self.discrepancies.append({
                    'entity_id': entity_id,
                    'table': table,
                    'type': 'mismatch',
                    'legacy': legacy_normalized,
                    'modern': modern_normalized
                })
                return False
            
            return True

        def _normalize(self, data: dict) -> dict:
            """Normalize data for comparison."""
            # Remove migration-specific fields
            normalized = {k: v for k, v in data.items() 
                        if k not in ['migrated_at', 'migration_id']}
            
            # Sort dict for consistent comparison
            return json.loads(json.dumps(normalized, sort_keys=True))

        def check_batch(self, table: str, batch_size: int = 1000) -> dict:
            """Check consistency for a batch of entities."""
            cursor = self.legacy.get_cursor(table)
            checked = 0
            consistent = 0
            
            while True:
                batch = cursor.fetchmany(batch_size)
                if not batch:
                    break
                
                for row in batch:
                    checked += 1
                    if self.check_entity(row['id'], table):
                        consistent += 1
            
            return {
                'checked': checked,
                'consistent': consistent,
                'discrepancies': len(self.discrepancies),
                'discrepancy_rate': (checked - consistent) / checked if checked > 0 else 0
            }

Checksum-based consistency:

    def compute_table_checksum(db, table: str) -> str:
        """Compute aggregate checksum for table."""
        result = db.execute(f"""
            SELECT MD5(CONCAT_WS(',',
                MD5(CONCAT_WS('|', {','.join(get_columns(table))})),
                COUNT(*)
            )) as checksum
            FROM {table}
        """)
        return result[0]['checksum']

36.9 Feature Flag Integration

Feature flags control migration rollout:

    import hashlib
    from dataclasses import dataclass
    from enum import Enum

    class FlagMode(Enum):
        OFF = "off"
        PERCENTAGE = "percentage"
        TARGETED = "targeted"
        ON = "on"

    @dataclass
    class FlagConfig:
        name: str
        mode: FlagMode
        percentage: int = 0
        targeted_ids: set = None

    class FeatureFlagService:
        def __init__(self, config_store):
            self.config = config_store

        def is_enabled(self, flag_name: str, context: dict) -> bool:
            flag = self.config.get(flag_name)
            
            if flag.mode == FlagMode.OFF:
                return False
            
            if flag.mode == FlagMode.ON:
                return True
            
            if flag.mode == FlagMode.TARGETED:
                entity_id = context.get('entity_id')
                return entity_id in flag.targeted_ids
            
            if flag.mode == FlagMode.PERCENTAGE:
                return self._in_percentage(context, flag.percentage)
            
            return False

        def _in_percentage(self, context: dict, percentage: int) -> bool:
            """Consistent hashing for percentage rollout."""
            user_id = context.get('user_id', '')
            bucket = int(hashlib.md5(user_id.encode()).hexdigest(), 16) % 100
            return bucket < percentage

Integration with router:

    class FeatureFlagRouter(MigrationRouter):
        def __init__(self, flag_service, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.flags = flag_service

        def route(self, request_path: str, context: dict) -> dict:
            flag_name = f"migration_{request_path.replace('/', '_')}"
            
            if self.flags.is_enabled(flag_name, context):
                try:
                    return self._call_modern(request_path, context)
                except Exception:
                    return self._call_legacy(request_path, context)
            
            return self._call_legacy(request_path, context)

UI for flag management:

    # Simple Flask admin for feature flags
    from flask import Flask, request, jsonify

    app = Flask(__name__)

    @app.route('/flags/<name>', methods=['POST'])
    def update_flag(name):
        config = request.json
        
        flag_config = FlagConfig(
            name=name,
            mode=FlagMode(config.get('mode', 'off')),
            percentage=config.get('percentage', 0),
            targeted_ids=set(config.get('targeted_ids', []))
        )
        
        config_store.save(flag_config)
        return jsonify({'status': 'updated', 'flag': name})

    @app.route('/flags/<name>/status', methods=['GET'])
    def get_flag_status(name):
        flag = config_store.get(name)
        return jsonify({
            'name': flag.name,
            'mode': flag.mode.value,
            'percentage': flag.percentage,
            'targeted_count': len(flag.targeted_ids) if flag.targeted_ids else 0
        })

36.10 Shadow Traffic

Shadow traffic routes real requests to new system without affecting users:

    import asyncio
    from typing import Callable

    class ShadowRouter:
        def __init__(self, modern_system, comparison_func: Callable):
            self.modern = modern_system
            self.compare = comparison_func
            self.shadow_results = []

        async def handle_request(self, request):
            # Primary response from legacy
            legacy_response = await call_legacy(request)
            
            # Shadow to modern (async, non-blocking)
            asyncio.create_task(self._shadow_request(request, legacy_response))
            
            return legacy_response

        async def _shadow_request(self, request, expected_response):
            """Send shadow request and compare results."""
            try:
                start = time.time()
                modern_response = await self.modern.handle(request)
                latency = time.time() - start
                
                comparison = self.compare(expected_response, modern_response)
                
                self.shadow_results.append({
                    'request': request,
                    'latency': latency,
                    'match': comparison['match'],
                    'differences': comparison.get('diffs', []),
                    'modern_error': None
                })
            except Exception as e:
                self.shadow_results.append({
                    'request': request,
                    'modern_error': str(e)
                })

    # Response comparison
    def compare_responses(legacy: dict, modern: dict) -> dict:
        diffs = []
        
        # Compare status codes
        if legacy.get('status') != modern.get('status'):
            diffs.append({
                'field': 'status',
                'legacy': legacy.get('status'),
                'modern': modern.get('status')
            })
        
        # Compare response bodies (with normalization)
        legacy_body = normalize(legacy.get('body', {}))
        modern_body = normalize(modern.get('body', {}))
        
        if legacy_body != modern_body:
            diffs.append({
                'field': 'body',
                'legacy': legacy_body,
                'modern': modern_body
            })
        
        return {'match': len(diffs) == 0, 'diffs': diffs}

36.11 Observability for Migrations

Metrics collection during migration:

    from dataclasses import dataclass
    from typing import Dict
    import prometheus_client as prom

    @dataclass
    class MigrationMetrics:
        # Request routing
        requests_total: prom.Counter = prom.Counter(
            'migration_requests_total',
            'Total requests by system',
            ['system', 'endpoint', 'status']
        )
        
        request_duration: prom.Histogram = prom.Histogram(
            'migration_request_duration_seconds',
            'Request latency by system',
            ['system', 'endpoint'],
            buckets=[.005, .01, .025, .05, .1, .25, .5, 1, 2.5, 5]
        )
        
        # Data sync
        sync_lag: prom.Gauge = prom.Gauge(
            'migration_sync_lag_seconds',
            'Data synchronization lag'
        )
        
        sync_errors: prom.Counter = prom.Counter(
            'migration_sync_errors_total',
            'Synchronization errors',
            ['operation', 'table']
        )
        
        consistency_violations: prom.Counter = prom.Counter(
            'migration_consistency_violations_total',
            'Data consistency violations',
            ['table', 'type']
        )
        
        # Migration progress
        migrated_entities: prom.Gauge = prom.Gauge(
            'migration_migrated_entities',
            'Number of migrated entities',
            ['entity_type']
        )
        
        migration_percentage: prom.Gauge = prom.Gauge(
            'migration_percentage',
            'Migration completion percentage',
            ['entity_type']
        )

    class InstrumentedRouter(MigrationRouter):
        def __init__(self, metrics: MigrationMetrics, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.metrics = metrics

        def route(self, request_path: str, context: dict) -> dict:
            system = self._select_system(request_path, context)
            
            with self.metrics.request_duration.labels(
                system=system,
                endpoint=request_path
            ).time():
                try:
                    if system == 'modern':
                        result = self._call_modern(request_path, context)
                    else:
                        result = self._call_legacy(request_path, context)
                    
                    self.metrics.requests_total.labels(
                        system=system,
                        endpoint=request_path,
                        status='success'
                    ).inc()
                    
                    return result
                    
                except Exception as e:
                    self.metrics.requests_total.labels(
                        system=system,
                        endpoint=request_path,
                        status='error'
                    ).inc()
                    raise

Dashboard queries:

    # Grafana dashboard JSON for migration monitoring
    migration_dashboard = {
        "dashboard": {
            "title": "Migration Status",
            "panels": [
                {
                    "title": "Request Distribution",
                    "type": "stat",
                    "targets": [{
                        "expr": "sum(rate(migration_requests_total[5m])) by (system)"
                    }]
                },
                {
                    "title": "Error Rate by System",
                    "type": "timeseries",
                    "targets": [{
                        "expr": "sum(rate(migration_requests_total{status='error'}[5m])) by (system)"
                    }]
                },
                {
                    "title": "Latency Comparison",
                    "type": "timeseries",
                    "targets": [
                        {
                            "expr": "histogram_quantile(0.95, sum(rate(migration_request_duration_seconds_bucket{system='legacy'}[5m])) by (le))",
                            "legendFormat": "Legacy p95"
                        },
                        {
                            "expr": "histogram_quantile(0.95, sum(rate(migration_request_duration_seconds_bucket{system='modern'}[5m])) by (le))",
                            "legendFormat": "Modern p95"
                        }
                    ]
                },
                {
                    "title": "Migration Progress",
                    "type": "gauge",
                    "targets": [{
                        "expr": "migration_percentage"
                    }]
                }
            ]
        }
    }

36.12 Rollback Procedures

Safe rollback capabilities:

    class MigrationRollback:
        def __init__(self, legacy_system, modern_system):
            self.legacy = legacy_system
            self.modern = modern_system
            self.rollout_state = None

        def snapshot_state(self):
            """Capture current migration state."""
            self.rollout_state = {
                'routing_percentages': get_current_routing(),
                'feature_flags': get_flag_states(),
                'timestamp': datetime.utcnow()
            }
            return self.rollout_state

        def execute_rollback(self):
            """Complete rollback to legacy system."""
            logger.critical("Executing full rollback")
            
            # Set all routing to legacy
            set_routing_percentage('modern', 0)
            
            # Disable modern feature flags
            disable_all_modern_flags()
            
            # Verify legacy capacity
            if not self._verify_legacy_capacity():
                raise RollbackError("Legacy system insufficient capacity")
            
            # Drain modern connections
            self._drain_modern_connections(timeout=300)
            
            # Verify no traffic to modern
            if self._check_modern_traffic():
                logger.error("Modern traffic detected after rollback")                
                raise RollbackError("Modern system still receiving traffic")

        def _verify_legacy_capacity(self) -> bool:
            """Ensure legacy can handle full load."""
            metrics = get_legacy_metrics()
            current_capacity = metrics['capacity_percent']
            projected_load = metrics['projected_load_percent']
            
            return current_capacity + projected_load < 80

        def _drain_modern_connections(self, timeout: int):
            """Wait for modern connections to complete."""
            start = time.time()
            while time.time() - start < timeout:
                active = get_active_modern_connections()
                if active == 0:
                    return
                logger.info(f"Waiting for {active} connections")
                time.sleep(5)
            
            raise TimeoutError(f"Connections not drained in {timeout}s")

    # Rollback decision criteria
    class RollbackMonitor:
        def __init__(self, metrics: MigrationMetrics):
            self.metrics = metrics
            self.thresholds = {
                'error_rate': 0.05,      # 5% error rate
                'p95_latency': 2.0,      # 2 seconds
                'consistency_violations': 100
            }

        def should_rollback(self) -> tuple[bool, str]:
            """Evaluate if rollback conditions are met."""
            
            # Check error rate
            modern_error_rate = self._get_error_rate('modern')
            if modern_error_rate > self.thresholds['error_rate']:
                return True, f"Error rate {modern_error_rate:.2%} exceeds threshold"
            
            # Check latency
            modern_p95 = self._get_p95_latency('modern')
            if modern_p95 > self.thresholds['p95_latency']:
                return True, f"p95 latency {modern_p95:.2f}s exceeds threshold"
            
            # Check consistency
            violations = self.metrics.consistency_violations._value.sum()
            if violations > self.thresholds['consistency_violations']:
                return True, f"{violations} consistency violations"
            
            return False, ""

36.13 Testing Migrations

Migration-specific testing strategies:

    import pytest

    class TestMigrationRouting:
        def test_routes_to_legacy_by_default(self, router):
            result = router.route('/api/legacy-endpoint', {})
            assert result.system == 'legacy'

        def test_routes_to_modern_based_on_percentage(self, router):
            # With 50% routing, multiple calls should hit both
            results = {'legacy': 0, 'modern': 0}
            
            for _ in range(1000):
                result = router.route('/api/mixed-endpoint', {})
                results[result.system] += 1
            
            # Should be roughly 50/50 with some variance
            assert 400 < results['modern'] < 600
            assert 400 < results['legacy'] < 600

        def test_fallback_on_modern_failure(self, router):
            router.modern_client.always_fail = True
            router.add_rule(RoutingRule(
                path_pattern='/api/test',
                target_system='modern',
                percentage=100
            ))
            
            result = router.route('/api/test', {})
            assert result.system == 'legacy'  # Fell back

        def test_predicate_routing(self, router):
            router.add_rule(RoutingRule(
                path_pattern='/api/users',
                target_system='modern',
                percentage=100,
                predicate=lambda ctx: ctx.get('beta_user', False)
            ))
            
            # Beta user goes to modern
            result = router.route('/api/users', {'beta_user': True})
            assert result.system == 'modern'
            
            # Regular user goes to legacy
            result = router.route('/api/users', {'beta_user': False})
            assert result.system == 'legacy'

    class TestDataConsistency:
        def test_eventual_consistency(self, dual_write_repo):
            entity = {'id': 'test-1', 'name': 'Test'}
            
            dual_write_repo.save(entity)
            
            # Legacy should have it immediately
            legacy = dual_write_repo.legacy.get('test-1')
            assert legacy is not None
            
            # Modern should have it after outbox processing
            dual_write_repo.process_outbox()
            modern = dual_write_repo.modern.get('test-1')
            assert modern == legacy

        def test_cdc_applies_updates(self, cdc_consumer):
            event = {
                'op': 'u',
                'source': {'table': 'orders'},
                'after': {'id': 'ord-1', 'status': 'shipped'}
            }
            
            cdc_consumer.apply_change(event)
            
            result = cdc_consumer.modern_db.get('orders', 'ord-1')
            assert result['status'] == 'shipped'

36.14 Migration Runbooks

Operational procedures for migrations:

    #!/usr/bin/env python3
    """
    Production Migration Runbook
    
    Phase 2: User Service Migration
    Date: 2024-02-15
    Systems: Legacy Monolith → Modern Microservice
    """

    import argparse
    import sys
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('migration')

    class MigrationRunbook:
        def __init__(self, environment):
            self.env = environment
            self.rollback_point = None

        def pre_flight_checks(self):
            """Verify prerequisites before migration."""
            checks = [
                self._check_legacy_health,
                self._check_modern_health,
                self._check_data_sync_lag,
                self._check_feature_flags,
                self._verify_rollback_procedures,
            ]
            
            for check in checks:
                if not check():
                    raise MigrationError(f"Pre-flight check failed: {check.__name__}")

        def execute_phase_1(self):
            """Phase 1: Enable shadow traffic."""
            logger.info("Phase 1: Enabling shadow traffic")
            
            enable_shadow_traffic('/api/users/*', percentage=100)
            
            # Monitor for 24 hours
            logger.info("Shadow traffic enabled, monitor consistency")

        def execute_phase_2(self):
            """Phase 2: Gradual traffic shift."""
            logger.info("Phase 2: Traffic percentage rollout")
            
            percentages = [5, 10, 25, 50, 75, 100]
            
            for pct in percentages:
                logger.info(f"Increasing traffic to {pct}%")
                set_routing_percentage('modern', pct)
                
                # Wait between increases
                if pct < 100:
                    logger.info(f"Holding at {pct}% for stability check")
                    time.sleep(3600)  # 1 hour
                    
                    if not self._stability_check():
                        logger.error(f"Stability check failed at {pct}%")
                        self.rollback()
                        sys.exit(1)

        def execute_phase_3(self):
            """Phase 3: Legacy drain and decommission."""
            logger.info("Phase 3: Draining legacy traffic")
            
            wait_for_legacy_drain(timeout=86400)  # 24 hours
            
            # Verify no traffic
            assert get_legacy_traffic() == 0, "Legacy still receiving traffic"
            
            # Decommission legacy user service
            scale_down_legacy('user-service')

        def rollback(self):
            """Execute rollback to previous state."""
            logger.critical("Executing rollback")
            
            if self.rollback_point:
                restore_state(self.rollback_point)
            else:
                emergency_rollback()
            
            notify_oncall(team='platform', severity='critical')

        def _check_legacy_health(self) -> bool:
            status = check_health('legacy-service')
            return status == 'healthy'

        def _check_modern_health(self) -> bool:
            status = check_health('modern-service')
            return status == 'healthy'

        def _check_data_sync_lag(self) -> bool:
            lag = get_sync_lag_seconds()
            return lag < 5  # Less than 5 seconds

        def _stability_check(self) -> bool:
            # Check error rates
            error_rate = get_error_rate('modern', window='1h')
            if error_rate > 0.01:
                return False
            
            # Check latency
            p99 = get_p99_latency('modern', window='1h')
            if p99 > 500:  # 500ms
                return False
            
            return True

    if __name__ == '__main__':
        parser = argparse.ArgumentParser(description='Migration Runbook')
        parser.add_argument('phase', choices=['preflight', '1', '2', '3', 'rollback'])
        parser.add_argument('--env', default='production')
        
        args = parser.parse_args()
        
        runbook = MigrationRunbook(args.env)
        
        if args.phase == 'preflight':
            runbook.pre_flight_checks()
        elif args.phase == '1':
            runbook.execute_phase_1()
        elif args.phase == '2':
            runbook.pre_flight_checks()
            runbook.execute_phase_2()
        elif args.phase == '3':
            runbook.execute_phase_3()
        elif args.phase == 'rollback':
            runbook.rollback()

36.15 Migration Best Practices

Successful migrations follow established patterns:

Plan for rollback from the start: Every migration step must be reversible. Maintain the ability to cut back to the legacy system at any point. Test rollback procedures regularly, not just when failures occur.

Automate monitoring: Manual monitoring cannot detect problems quickly enough. Automate metric collection and alerting for both systems. Define clear thresholds for automatic rollback triggers.

Use shadow traffic extensively: Shadow testing reveals problems without user impact. Compare responses between systems for every request type. Build confidence before any user-facing traffic shifts.

Migrate by entity, not by table: Database-level migration often creates inconsistency. Entity-level migration maintains referential integrity. Track migration status per entity for granular progress.

Accept eventual consistency: Perfect consistency during migration is impossible. Design for eventual consistency with bounded staleness. Implement reconciliation processes to detect and fix drift.

Communicate transparently: Stakeholders need visibility into migration progress. Dashboards showing real-time status build confidence. Document decisions and learnings for future migrations.

Start small and expand: Begin with non-critical endpoints or users. Increase migration scope only after stability verification. Reserve full cutover until extensive production validation.

The strangler fig approach, combined with robust routing infrastructure, dual-write patterns, and comprehensive observability, provides a proven framework for safe system migration. Success depends as much on operational discipline and risk management as on technical implementation.
