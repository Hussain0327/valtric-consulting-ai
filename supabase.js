[
  {
    "table_schema": "public",
    "table_name": "active_plan",
    "table_type": "VIEW",
    "column_name": "user_id",
    "data_type": "uuid",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "active_plan",
    "table_type": "VIEW",
    "column_name": "plan_id",
    "data_type": "text",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "active_plan",
    "table_type": "VIEW",
    "column_name": "monthly_quota",
    "data_type": "integer",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "chunks",
    "table_type": "BASE TABLE",
    "column_name": "id",
    "data_type": "bigint",
    "is_nullable": "NO",
    "column_default": "nextval('chunks_id_seq'::regclass)",
    "constraint_type": "PRIMARY KEY"
  },
  {
    "table_schema": "public",
    "table_name": "chunks",
    "table_type": "BASE TABLE",
    "column_name": "document_id",
    "data_type": "uuid",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": "FOREIGN KEY"
  },
  {
    "table_schema": "public",
    "table_name": "chunks",
    "table_type": "BASE TABLE",
    "column_name": "text",
    "data_type": "text",
    "is_nullable": "NO",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "chunks",
    "table_type": "BASE TABLE",
    "column_name": "span",
    "data_type": "int4range",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "chunks",
    "table_type": "BASE TABLE",
    "column_name": "embedding",
    "data_type": "USER-DEFINED",
    "is_nullable": "NO",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "documents",
    "table_type": "BASE TABLE",
    "column_name": "id",
    "data_type": "uuid",
    "is_nullable": "NO",
    "column_default": "gen_random_uuid()",
    "constraint_type": "PRIMARY KEY"
  },
  {
    "table_schema": "public",
    "table_name": "documents",
    "table_type": "BASE TABLE",
    "column_name": "project_id",
    "data_type": "uuid",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": "FOREIGN KEY"
  },
  {
    "table_schema": "public",
    "table_name": "documents",
    "table_type": "BASE TABLE",
    "column_name": "source",
    "data_type": "text",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "documents",
    "table_type": "BASE TABLE",
    "column_name": "path",
    "data_type": "text",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "documents",
    "table_type": "BASE TABLE",
    "column_name": "meta",
    "data_type": "jsonb",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "documents",
    "table_type": "BASE TABLE",
    "column_name": "created_at",
    "data_type": "timestamp with time zone",
    "is_nullable": "YES",
    "column_default": "now()",
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "evidence",
    "table_type": "BASE TABLE",
    "column_name": "id",
    "data_type": "uuid",
    "is_nullable": "NO",
    "column_default": "gen_random_uuid()",
    "constraint_type": "PRIMARY KEY"
  },
  {
    "table_schema": "public",
    "table_name": "evidence",
    "table_type": "BASE TABLE",
    "column_name": "project_id",
    "data_type": "uuid",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": "FOREIGN KEY"
  },
  {
    "table_schema": "public",
    "table_name": "evidence",
    "table_type": "BASE TABLE",
    "column_name": "chunk_id",
    "data_type": "bigint",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": "FOREIGN KEY"
  },
  {
    "table_schema": "public",
    "table_name": "evidence",
    "table_type": "BASE TABLE",
    "column_name": "label",
    "data_type": "text",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "evidence",
    "table_type": "BASE TABLE",
    "column_name": "created_at",
    "data_type": "timestamp with time zone",
    "is_nullable": "YES",
    "column_default": "now()",
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "members",
    "table_type": "BASE TABLE",
    "column_name": "org_id",
    "data_type": "uuid",
    "is_nullable": "NO",
    "column_default": null,
    "constraint_type": "FOREIGN KEY"
  },
  {
    "table_schema": "public",
    "table_name": "members",
    "table_type": "BASE TABLE",
    "column_name": "org_id",
    "data_type": "uuid",
    "is_nullable": "NO",
    "column_default": null,
    "constraint_type": "PRIMARY KEY"
  },
  {
    "table_schema": "public",
    "table_name": "members",
    "table_type": "BASE TABLE",
    "column_name": "user_id",
    "data_type": "uuid",
    "is_nullable": "NO",
    "column_default": null,
    "constraint_type": "PRIMARY KEY"
  },
  {
    "table_schema": "public",
    "table_name": "members",
    "table_type": "BASE TABLE",
    "column_name": "role",
    "data_type": "text",
    "is_nullable": "NO",
    "column_default": "'member'::text",
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "members",
    "table_type": "BASE TABLE",
    "column_name": "created_at",
    "data_type": "timestamp with time zone",
    "is_nullable": "YES",
    "column_default": "now()",
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "message_usage",
    "table_type": "BASE TABLE",
    "column_name": "id",
    "data_type": "uuid",
    "is_nullable": "NO",
    "column_default": "gen_random_uuid()",
    "constraint_type": "PRIMARY KEY"
  },
  {
    "table_schema": "public",
    "table_name": "message_usage",
    "table_type": "BASE TABLE",
    "column_name": "user_id",
    "data_type": "uuid",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": "FOREIGN KEY"
  },
  {
    "table_schema": "public",
    "table_name": "message_usage",
    "table_type": "BASE TABLE",
    "column_name": "messages_used",
    "data_type": "integer",
    "is_nullable": "NO",
    "column_default": "0",
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "message_usage",
    "table_type": "BASE TABLE",
    "column_name": "messages_limit",
    "data_type": "integer",
    "is_nullable": "NO",
    "column_default": "10",
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "message_usage",
    "table_type": "BASE TABLE",
    "column_name": "reset_date",
    "data_type": "timestamp with time zone",
    "is_nullable": "NO",
    "column_default": "(now() + '1 mon'::interval)",
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "message_usage",
    "table_type": "BASE TABLE",
    "column_name": "created_at",
    "data_type": "timestamp with time zone",
    "is_nullable": "NO",
    "column_default": "now()",
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "message_usage",
    "table_type": "BASE TABLE",
    "column_name": "updated_at",
    "data_type": "timestamp with time zone",
    "is_nullable": "NO",
    "column_default": "now()",
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "metrics",
    "table_type": "BASE TABLE",
    "column_name": "id",
    "data_type": "uuid",
    "is_nullable": "NO",
    "column_default": "gen_random_uuid()",
    "constraint_type": "PRIMARY KEY"
  },
  {
    "table_schema": "public",
    "table_name": "metrics",
    "table_type": "BASE TABLE",
    "column_name": "project_id",
    "data_type": "uuid",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": "FOREIGN KEY"
  },
  {
    "table_schema": "public",
    "table_name": "metrics",
    "table_type": "BASE TABLE",
    "column_name": "name",
    "data_type": "text",
    "is_nullable": "NO",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "metrics",
    "table_type": "BASE TABLE",
    "column_name": "baseline",
    "data_type": "double precision",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "metrics",
    "table_type": "BASE TABLE",
    "column_name": "target",
    "data_type": "double precision",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "metrics",
    "table_type": "BASE TABLE",
    "column_name": "current",
    "data_type": "double precision",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "metrics",
    "table_type": "BASE TABLE",
    "column_name": "source",
    "data_type": "text",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "metrics",
    "table_type": "BASE TABLE",
    "column_name": "updated_at",
    "data_type": "timestamp with time zone",
    "is_nullable": "YES",
    "column_default": "now()",
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "my_orgs",
    "table_type": "VIEW",
    "column_name": "org_id",
    "data_type": "uuid",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "orgs",
    "table_type": "BASE TABLE",
    "column_name": "id",
    "data_type": "uuid",
    "is_nullable": "NO",
    "column_default": "gen_random_uuid()",
    "constraint_type": "PRIMARY KEY"
  },
  {
    "table_schema": "public",
    "table_name": "orgs",
    "table_type": "BASE TABLE",
    "column_name": "name",
    "data_type": "text",
    "is_nullable": "NO",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "orgs",
    "table_type": "BASE TABLE",
    "column_name": "created_at",
    "data_type": "timestamp with time zone",
    "is_nullable": "YES",
    "column_default": "now()",
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "plans",
    "table_type": "BASE TABLE",
    "column_name": "id",
    "data_type": "text",
    "is_nullable": "NO",
    "column_default": null,
    "constraint_type": "PRIMARY KEY"
  },
  {
    "table_schema": "public",
    "table_name": "plans",
    "table_type": "BASE TABLE",
    "column_name": "name",
    "data_type": "text",
    "is_nullable": "NO",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "plans",
    "table_type": "BASE TABLE",
    "column_name": "monthly_quota",
    "data_type": "integer",
    "is_nullable": "NO",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "plans",
    "table_type": "BASE TABLE",
    "column_name": "features",
    "data_type": "jsonb",
    "is_nullable": "YES",
    "column_default": "'{}'::jsonb",
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "projects",
    "table_type": "BASE TABLE",
    "column_name": "id",
    "data_type": "uuid",
    "is_nullable": "NO",
    "column_default": "gen_random_uuid()",
    "constraint_type": "PRIMARY KEY"
  },
  {
    "table_schema": "public",
    "table_name": "projects",
    "table_type": "BASE TABLE",
    "column_name": "org_id",
    "data_type": "uuid",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": "FOREIGN KEY"
  },
  {
    "table_schema": "public",
    "table_name": "projects",
    "table_type": "BASE TABLE",
    "column_name": "name",
    "data_type": "text",
    "is_nullable": "NO",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "projects",
    "table_type": "BASE TABLE",
    "column_name": "tier",
    "data_type": "text",
    "is_nullable": "YES",
    "column_default": "'pro'::text",
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "projects",
    "table_type": "BASE TABLE",
    "column_name": "created_at",
    "data_type": "timestamp with time zone",
    "is_nullable": "YES",
    "column_default": "now()",
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "runs",
    "table_type": "BASE TABLE",
    "column_name": "id",
    "data_type": "uuid",
    "is_nullable": "NO",
    "column_default": "gen_random_uuid()",
    "constraint_type": "PRIMARY KEY"
  },
  {
    "table_schema": "public",
    "table_name": "runs",
    "table_type": "BASE TABLE",
    "column_name": "project_id",
    "data_type": "uuid",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": "FOREIGN KEY"
  },
  {
    "table_schema": "public",
    "table_name": "runs",
    "table_type": "BASE TABLE",
    "column_name": "playbook",
    "data_type": "text",
    "is_nullable": "NO",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "runs",
    "table_type": "BASE TABLE",
    "column_name": "input",
    "data_type": "jsonb",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "runs",
    "table_type": "BASE TABLE",
    "column_name": "output",
    "data_type": "jsonb",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "runs",
    "table_type": "BASE TABLE",
    "column_name": "model",
    "data_type": "text",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "runs",
    "table_type": "BASE TABLE",
    "column_name": "latency_ms",
    "data_type": "integer",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "runs",
    "table_type": "BASE TABLE",
    "column_name": "created_at",
    "data_type": "timestamp with time zone",
    "is_nullable": "YES",
    "column_default": "now()",
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "subscribers",
    "table_type": "BASE TABLE",
    "column_name": "id",
    "data_type": "uuid",
    "is_nullable": "NO",
    "column_default": "gen_random_uuid()",
    "constraint_type": "PRIMARY KEY"
  },
  {
    "table_schema": "public",
    "table_name": "subscribers",
    "table_type": "BASE TABLE",
    "column_name": "user_id",
    "data_type": "uuid",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": "FOREIGN KEY"
  },
  {
    "table_schema": "public",
    "table_name": "subscribers",
    "table_type": "BASE TABLE",
    "column_name": "email",
    "data_type": "text",
    "is_nullable": "NO",
    "column_default": null,
    "constraint_type": "UNIQUE"
  },
  {
    "table_schema": "public",
    "table_name": "subscribers",
    "table_type": "BASE TABLE",
    "column_name": "stripe_customer_id",
    "data_type": "text",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "subscribers",
    "table_type": "BASE TABLE",
    "column_name": "subscribed",
    "data_type": "boolean",
    "is_nullable": "NO",
    "column_default": "false",
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "subscribers",
    "table_type": "BASE TABLE",
    "column_name": "subscription_tier",
    "data_type": "text",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "subscribers",
    "table_type": "BASE TABLE",
    "column_name": "subscription_end",
    "data_type": "timestamp with time zone",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "subscribers",
    "table_type": "BASE TABLE",
    "column_name": "updated_at",
    "data_type": "timestamp with time zone",
    "is_nullable": "NO",
    "column_default": "now()",
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "subscribers",
    "table_type": "BASE TABLE",
    "column_name": "created_at",
    "data_type": "timestamp with time zone",
    "is_nullable": "NO",
    "column_default": "now()",
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "subscriptions",
    "table_type": "BASE TABLE",
    "column_name": "id",
    "data_type": "uuid",
    "is_nullable": "NO",
    "column_default": "gen_random_uuid()",
    "constraint_type": "PRIMARY KEY"
  },
  {
    "table_schema": "public",
    "table_name": "subscriptions",
    "table_type": "BASE TABLE",
    "column_name": "user_id",
    "data_type": "uuid",
    "is_nullable": "NO",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "subscriptions",
    "table_type": "BASE TABLE",
    "column_name": "plan_id",
    "data_type": "text",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": "FOREIGN KEY"
  },
  {
    "table_schema": "public",
    "table_name": "subscriptions",
    "table_type": "BASE TABLE",
    "column_name": "status",
    "data_type": "text",
    "is_nullable": "NO",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "subscriptions",
    "table_type": "BASE TABLE",
    "column_name": "current_period_start",
    "data_type": "timestamp with time zone",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "subscriptions",
    "table_type": "BASE TABLE",
    "column_name": "current_period_end",
    "data_type": "timestamp with time zone",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "subscriptions",
    "table_type": "BASE TABLE",
    "column_name": "stripe_customer_id",
    "data_type": "text",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "subscriptions",
    "table_type": "BASE TABLE",
    "column_name": "stripe_sub_id",
    "data_type": "text",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "subscriptions",
    "table_type": "BASE TABLE",
    "column_name": "created_at",
    "data_type": "timestamp with time zone",
    "is_nullable": "YES",
    "column_default": "now()",
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "usage_counters",
    "table_type": "VIEW",
    "column_name": "user_id",
    "data_type": "uuid",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "usage_counters",
    "table_type": "VIEW",
    "column_name": "kind",
    "data_type": "text",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "usage_counters",
    "table_type": "VIEW",
    "column_name": "month",
    "data_type": "timestamp with time zone",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "usage_counters",
    "table_type": "VIEW",
    "column_name": "used",
    "data_type": "integer",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "usage_events",
    "table_type": "BASE TABLE",
    "column_name": "id",
    "data_type": "bigint",
    "is_nullable": "NO",
    "column_default": "nextval('usage_events_id_seq'::regclass)",
    "constraint_type": "PRIMARY KEY"
  },
  {
    "table_schema": "public",
    "table_name": "usage_events",
    "table_type": "BASE TABLE",
    "column_name": "user_id",
    "data_type": "uuid",
    "is_nullable": "NO",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "usage_events",
    "table_type": "BASE TABLE",
    "column_name": "org_id",
    "data_type": "uuid",
    "is_nullable": "YES",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "usage_events",
    "table_type": "BASE TABLE",
    "column_name": "kind",
    "data_type": "text",
    "is_nullable": "NO",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "usage_events",
    "table_type": "BASE TABLE",
    "column_name": "amount",
    "data_type": "integer",
    "is_nullable": "NO",
    "column_default": null,
    "constraint_type": ""
  },
  {
    "table_schema": "public",
    "table_name": "usage_events",
    "table_type": "BASE TABLE",
    "column_name": "occurred_at",
    "data_type": "timestamp with time zone",
    "is_nullable": "YES",
    "column_default": "now()",
    "constraint_type": ""
  }
]


[
  {
    "table_name": "chunks",
    "constraint_name": "2200_17826_1_not_null",
    "check_clause": "id IS NOT NULL"
  },
  {
    "table_name": "chunks",
    "constraint_name": "2200_17826_3_not_null",
    "check_clause": "text IS NOT NULL"
  },
  {
    "table_name": "chunks",
    "constraint_name": "2200_17826_5_not_null",
    "check_clause": "embedding IS NOT NULL"
  },
  {
    "table_name": "documents",
    "constraint_name": "2200_17811_1_not_null",
    "check_clause": "id IS NOT NULL"
  },
  {
    "table_name": "evidence",
    "constraint_name": "2200_17839_1_not_null",
    "check_clause": "id IS NOT NULL"
  },
  {
    "table_name": "members",
    "constraint_name": "2200_17781_1_not_null",
    "check_clause": "org_id IS NOT NULL"
  },
  {
    "table_name": "members",
    "constraint_name": "2200_17781_2_not_null",
    "check_clause": "user_id IS NOT NULL"
  },
  {
    "table_name": "members",
    "constraint_name": "2200_17781_3_not_null",
    "check_clause": "role IS NOT NULL"
  },
  {
    "table_name": "members",
    "constraint_name": "members_role_check",
    "check_clause": "(role = ANY (ARRAY['owner'::text, 'admin'::text, 'member'::text]))"
  },
  {
    "table_name": "message_usage",
    "constraint_name": "2200_17298_1_not_null",
    "check_clause": "id IS NOT NULL"
  },
  {
    "table_name": "message_usage",
    "constraint_name": "2200_17298_3_not_null",
    "check_clause": "messages_used IS NOT NULL"
  },
  {
    "table_name": "message_usage",
    "constraint_name": "2200_17298_4_not_null",
    "check_clause": "messages_limit IS NOT NULL"
  },
  {
    "table_name": "message_usage",
    "constraint_name": "2200_17298_5_not_null",
    "check_clause": "reset_date IS NOT NULL"
  },
  {
    "table_name": "message_usage",
    "constraint_name": "2200_17298_6_not_null",
    "check_clause": "created_at IS NOT NULL"
  },
  {
    "table_name": "message_usage",
    "constraint_name": "2200_17298_7_not_null",
    "check_clause": "updated_at IS NOT NULL"
  },
  {
    "table_name": "metrics",
    "constraint_name": "2200_17872_1_not_null",
    "check_clause": "id IS NOT NULL"
  },
  {
    "table_name": "metrics",
    "constraint_name": "2200_17872_3_not_null",
    "check_clause": "name IS NOT NULL"
  },
  {
    "table_name": "orgs",
    "constraint_name": "2200_17772_1_not_null",
    "check_clause": "id IS NOT NULL"
  },
  {
    "table_name": "orgs",
    "constraint_name": "2200_17772_2_not_null",
    "check_clause": "name IS NOT NULL"
  },
  {
    "table_name": "plans",
    "constraint_name": "2200_17886_1_not_null",
    "check_clause": "id IS NOT NULL"
  },
  {
    "table_name": "plans",
    "constraint_name": "2200_17886_2_not_null",
    "check_clause": "name IS NOT NULL"
  },
  {
    "table_name": "plans",
    "constraint_name": "2200_17886_3_not_null",
    "check_clause": "monthly_quota IS NOT NULL"
  },
  {
    "table_name": "projects",
    "constraint_name": "2200_17796_1_not_null",
    "check_clause": "id IS NOT NULL"
  },
  {
    "table_name": "projects",
    "constraint_name": "2200_17796_3_not_null",
    "check_clause": "name IS NOT NULL"
  },
  {
    "table_name": "runs",
    "constraint_name": "2200_17858_1_not_null",
    "check_clause": "id IS NOT NULL"
  },
  {
    "table_name": "runs",
    "constraint_name": "2200_17858_3_not_null",
    "check_clause": "playbook IS NOT NULL"
  },
  {
    "table_name": "subscribers",
    "constraint_name": "2200_17280_1_not_null",
    "check_clause": "id IS NOT NULL"
  },
  {
    "table_name": "subscribers",
    "constraint_name": "2200_17280_3_not_null",
    "check_clause": "email IS NOT NULL"
  },
  {
    "table_name": "subscribers",
    "constraint_name": "2200_17280_5_not_null",
    "check_clause": "subscribed IS NOT NULL"
  },
  {
    "table_name": "subscribers",
    "constraint_name": "2200_17280_8_not_null",
    "check_clause": "updated_at IS NOT NULL"
  },
  {
    "table_name": "subscribers",
    "constraint_name": "2200_17280_9_not_null",
    "check_clause": "created_at IS NOT NULL"
  },
  {
    "table_name": "subscriptions",
    "constraint_name": "2200_17894_1_not_null",
    "check_clause": "id IS NOT NULL"
  },
  {
    "table_name": "subscriptions",
    "constraint_name": "2200_17894_2_not_null",
    "check_clause": "user_id IS NOT NULL"
  },
  {
    "table_name": "subscriptions",
    "constraint_name": "2200_17894_4_not_null",
    "check_clause": "status IS NOT NULL"
  },
  {
    "table_name": "subscriptions",
    "constraint_name": "subscriptions_status_check",
    "check_clause": "(status = ANY (ARRAY['active'::text, 'past_due'::text, 'canceled'::text]))"
  },
  {
    "table_name": "usage_events",
    "constraint_name": "2200_17910_1_not_null",
    "check_clause": "id IS NOT NULL"
  },
  {
    "table_name": "usage_events",
    "constraint_name": "2200_17910_2_not_null",
    "check_clause": "user_id IS NOT NULL"
  },
  {
    "table_name": "usage_events",
    "constraint_name": "2200_17910_4_not_null",
    "check_clause": "kind IS NOT NULL"
  },
  {
    "table_name": "usage_events",
    "constraint_name": "2200_17910_5_not_null",
    "check_clause": "amount IS NOT NULL"
  }
]


[
  {
    "table_name": "chunks",
    "column_name": "document_id",
    "foreign_table_name": "documents",
    "foreign_column_name": "id"
  },
  {
    "table_name": "documents",
    "column_name": "project_id",
    "foreign_table_name": "projects",
    "foreign_column_name": "id"
  },
  {
    "table_name": "evidence",
    "column_name": "chunk_id",
    "foreign_table_name": "chunks",
    "foreign_column_name": "id"
  },
  {
    "table_name": "evidence",
    "column_name": "project_id",
    "foreign_table_name": "projects",
    "foreign_column_name": "id"
  },
  {
    "table_name": "members",
    "column_name": "org_id",
    "foreign_table_name": "orgs",
    "foreign_column_name": "id"
  },
  {
    "table_name": "metrics",
    "column_name": "project_id",
    "foreign_table_name": "projects",
    "foreign_column_name": "id"
  },
  {
    "table_name": "projects",
    "column_name": "org_id",
    "foreign_table_name": "orgs",
    "foreign_column_name": "id"
  },
  {
    "table_name": "runs",
    "column_name": "project_id",
    "foreign_table_name": "projects",
    "foreign_column_name": "id"
  },
  {
    "table_name": "subscriptions",
    "column_name": "plan_id",
    "foreign_table_name": "plans",
    "foreign_column_name": "id"
  }
]


[
  {
    "schemaname": "public",
    "tablename": "chunks",
    "policyname": "chunks_rw",
    "permissive": "PERMISSIVE",
    "roles": "{public}",
    "cmd": "ALL",
    "qual": "(document_id IN ( SELECT documents.id\n   FROM documents\n  WHERE (documents.project_id IN ( SELECT projects.id\n           FROM projects\n          WHERE (projects.org_id IN ( SELECT my_orgs.org_id\n                   FROM my_orgs))))))",
    "with_check": "(document_id IN ( SELECT documents.id\n   FROM documents\n  WHERE (documents.project_id IN ( SELECT projects.id\n           FROM projects\n          WHERE (projects.org_id IN ( SELECT my_orgs.org_id\n                   FROM my_orgs))))))"
  },
  {
    "schemaname": "public",
    "tablename": "documents",
    "policyname": "docs_rw",
    "permissive": "PERMISSIVE",
    "roles": "{public}",
    "cmd": "ALL",
    "qual": "(project_id IN ( SELECT projects.id\n   FROM projects\n  WHERE (projects.org_id IN ( SELECT my_orgs.org_id\n           FROM my_orgs))))",
    "with_check": "(project_id IN ( SELECT projects.id\n   FROM projects\n  WHERE (projects.org_id IN ( SELECT my_orgs.org_id\n           FROM my_orgs))))"
  },
  {
    "schemaname": "public",
    "tablename": "evidence",
    "policyname": "evidence_rw",
    "permissive": "PERMISSIVE",
    "roles": "{public}",
    "cmd": "ALL",
    "qual": "(project_id IN ( SELECT projects.id\n   FROM projects\n  WHERE (projects.org_id IN ( SELECT my_orgs.org_id\n           FROM my_orgs))))",
    "with_check": "(project_id IN ( SELECT projects.id\n   FROM projects\n  WHERE (projects.org_id IN ( SELECT my_orgs.org_id\n           FROM my_orgs))))"
  },
  {
    "schemaname": "public",
    "tablename": "members",
    "policyname": "members_rw",
    "permissive": "PERMISSIVE",
    "roles": "{public}",
    "cmd": "ALL",
    "qual": "(user_id = auth.uid())",
    "with_check": "(user_id = auth.uid())"
  },
  {
    "schemaname": "public",
    "tablename": "message_usage",
    "policyname": "insert_own_usage",
    "permissive": "PERMISSIVE",
    "roles": "{public}",
    "cmd": "INSERT",
    "qual": null,
    "with_check": "(user_id = auth.uid())"
  },
  {
    "schemaname": "public",
    "tablename": "message_usage",
    "policyname": "select_own_usage",
    "permissive": "PERMISSIVE",
    "roles": "{public}",
    "cmd": "SELECT",
    "qual": "(user_id = auth.uid())",
    "with_check": null
  },
  {
    "schemaname": "public",
    "tablename": "message_usage",
    "policyname": "update_own_usage",
    "permissive": "PERMISSIVE",
    "roles": "{public}",
    "cmd": "UPDATE",
    "qual": "(user_id = auth.uid())",
    "with_check": null
  },
  {
    "schemaname": "public",
    "tablename": "metrics",
    "policyname": "metrics_rw",
    "permissive": "PERMISSIVE",
    "roles": "{public}",
    "cmd": "ALL",
    "qual": "(project_id IN ( SELECT projects.id\n   FROM projects\n  WHERE (projects.org_id IN ( SELECT my_orgs.org_id\n           FROM my_orgs))))",
    "with_check": "(project_id IN ( SELECT projects.id\n   FROM projects\n  WHERE (projects.org_id IN ( SELECT my_orgs.org_id\n           FROM my_orgs))))"
  },
  {
    "schemaname": "public",
    "tablename": "orgs",
    "policyname": "orgs_insert",
    "permissive": "PERMISSIVE",
    "roles": "{public}",
    "cmd": "INSERT",
    "qual": null,
    "with_check": "(auth.uid() IS NOT NULL)"
  },
  {
    "schemaname": "public",
    "tablename": "orgs",
    "policyname": "orgs_read",
    "permissive": "PERMISSIVE",
    "roles": "{public}",
    "cmd": "SELECT",
    "qual": "(id IN ( SELECT my_orgs.org_id\n   FROM my_orgs))",
    "with_check": null
  },
  {
    "schemaname": "public",
    "tablename": "plans",
    "policyname": "plans_read",
    "permissive": "PERMISSIVE",
    "roles": "{public}",
    "cmd": "SELECT",
    "qual": "true",
    "with_check": null
  },
  {
    "schemaname": "public",
    "tablename": "projects",
    "policyname": "proj_read",
    "permissive": "PERMISSIVE",
    "roles": "{public}",
    "cmd": "SELECT",
    "qual": "(org_id IN ( SELECT my_orgs.org_id\n   FROM my_orgs))",
    "with_check": null
  },
  {
    "schemaname": "public",
    "tablename": "projects",
    "policyname": "proj_write",
    "permissive": "PERMISSIVE",
    "roles": "{public}",
    "cmd": "INSERT",
    "qual": null,
    "with_check": "(org_id IN ( SELECT my_orgs.org_id\n   FROM my_orgs))"
  },
  {
    "schemaname": "public",
    "tablename": "runs",
    "policyname": "runs_rw",
    "permissive": "PERMISSIVE",
    "roles": "{public}",
    "cmd": "ALL",
    "qual": "(project_id IN ( SELECT projects.id\n   FROM projects\n  WHERE (projects.org_id IN ( SELECT my_orgs.org_id\n           FROM my_orgs))))",
    "with_check": "(project_id IN ( SELECT projects.id\n   FROM projects\n  WHERE (projects.org_id IN ( SELECT my_orgs.org_id\n           FROM my_orgs))))"
  },
  {
    "schemaname": "public",
    "tablename": "subscribers",
    "policyname": "insert_subscription",
    "permissive": "PERMISSIVE",
    "roles": "{public}",
    "cmd": "INSERT",
    "qual": null,
    "with_check": "true"
  },
  {
    "schemaname": "public",
    "tablename": "subscribers",
    "policyname": "select_own_subscription",
    "permissive": "PERMISSIVE",
    "roles": "{public}",
    "cmd": "SELECT",
    "qual": "((user_id = auth.uid()) OR (email = auth.email()))",
    "with_check": null
  },
  {
    "schemaname": "public",
    "tablename": "subscribers",
    "policyname": "update_own_subscription",
    "permissive": "PERMISSIVE",
    "roles": "{public}",
    "cmd": "UPDATE",
    "qual": "true",
    "with_check": null
  },
  {
    "schemaname": "public",
    "tablename": "subscriptions",
    "policyname": "subs_rw",
    "permissive": "PERMISSIVE",
    "roles": "{public}",
    "cmd": "ALL",
    "qual": "(user_id = auth.uid())",
    "with_check": "(user_id = auth.uid())"
  },
  {
    "schemaname": "public",
    "tablename": "usage_events",
    "policyname": "usage_rw",
    "permissive": "PERMISSIVE",
    "roles": "{public}",
    "cmd": "ALL",
    "qual": "(user_id = auth.uid())",
    "with_check": "(user_id = auth.uid())"
  }
]

[
  {
    "schemaname": "public",
    "tablename": "chunks",
    "indexname": "chunks_pkey",
    "indexdef": "CREATE UNIQUE INDEX chunks_pkey ON public.chunks USING btree (id)"
  },
  {
    "schemaname": "public",
    "tablename": "chunks",
    "indexname": "idx_chunks_doc",
    "indexdef": "CREATE INDEX idx_chunks_doc ON public.chunks USING btree (document_id)"
  },
  {
    "schemaname": "public",
    "tablename": "chunks",
    "indexname": "idx_chunks_embedding_cosine",
    "indexdef": "CREATE INDEX idx_chunks_embedding_cosine ON public.chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists='100')"
  },
  {
    "schemaname": "public",
    "tablename": "documents",
    "indexname": "documents_pkey",
    "indexdef": "CREATE UNIQUE INDEX documents_pkey ON public.documents USING btree (id)"
  },
  {
    "schemaname": "public",
    "tablename": "documents",
    "indexname": "idx_docs_project",
    "indexdef": "CREATE INDEX idx_docs_project ON public.documents USING btree (project_id)"
  },
  {
    "schemaname": "public",
    "tablename": "evidence",
    "indexname": "evidence_pkey",
    "indexdef": "CREATE UNIQUE INDEX evidence_pkey ON public.evidence USING btree (id)"
  },
  {
    "schemaname": "public",
    "tablename": "evidence",
    "indexname": "idx_evidence_project",
    "indexdef": "CREATE INDEX idx_evidence_project ON public.evidence USING btree (project_id)"
  },
  {
    "schemaname": "public",
    "tablename": "members",
    "indexname": "members_pkey",
    "indexdef": "CREATE UNIQUE INDEX members_pkey ON public.members USING btree (org_id, user_id)"
  },
  {
    "schemaname": "public",
    "tablename": "message_usage",
    "indexname": "message_usage_pkey",
    "indexdef": "CREATE UNIQUE INDEX message_usage_pkey ON public.message_usage USING btree (id)"
  },
  {
    "schemaname": "public",
    "tablename": "metrics",
    "indexname": "idx_metrics_project",
    "indexdef": "CREATE INDEX idx_metrics_project ON public.metrics USING btree (project_id)"
  },
  {
    "schemaname": "public",
    "tablename": "metrics",
    "indexname": "metrics_pkey",
    "indexdef": "CREATE UNIQUE INDEX metrics_pkey ON public.metrics USING btree (id)"
  },
  {
    "schemaname": "public",
    "tablename": "orgs",
    "indexname": "orgs_pkey",
    "indexdef": "CREATE UNIQUE INDEX orgs_pkey ON public.orgs USING btree (id)"
  },
  {
    "schemaname": "public",
    "tablename": "plans",
    "indexname": "plans_pkey",
    "indexdef": "CREATE UNIQUE INDEX plans_pkey ON public.plans USING btree (id)"
  },
  {
    "schemaname": "public",
    "tablename": "projects",
    "indexname": "idx_projects_org",
    "indexdef": "CREATE INDEX idx_projects_org ON public.projects USING btree (org_id)"
  },
  {
    "schemaname": "public",
    "tablename": "projects",
    "indexname": "projects_pkey",
    "indexdef": "CREATE UNIQUE INDEX projects_pkey ON public.projects USING btree (id)"
  },
  {
    "schemaname": "public",
    "tablename": "runs",
    "indexname": "idx_runs_project",
    "indexdef": "CREATE INDEX idx_runs_project ON public.runs USING btree (project_id)"
  },
  {
    "schemaname": "public",
    "tablename": "runs",
    "indexname": "runs_pkey",
    "indexdef": "CREATE UNIQUE INDEX runs_pkey ON public.runs USING btree (id)"
  },
  {
    "schemaname": "public",
    "tablename": "subscribers",
    "indexname": "subscribers_email_key",
    "indexdef": "CREATE UNIQUE INDEX subscribers_email_key ON public.subscribers USING btree (email)"
  },
  {
    "schemaname": "public",
    "tablename": "subscribers",
    "indexname": "subscribers_pkey",
    "indexdef": "CREATE UNIQUE INDEX subscribers_pkey ON public.subscribers USING btree (id)"
  },
  {
    "schemaname": "public",
    "tablename": "subscriptions",
    "indexname": "subscriptions_pkey",
    "indexdef": "CREATE UNIQUE INDEX subscriptions_pkey ON public.subscriptions USING btree (id)"
  },
  {
    "schemaname": "public",
    "tablename": "usage_events",
    "indexname": "usage_events_pkey",
    "indexdef": "CREATE UNIQUE INDEX usage_events_pkey ON public.usage_events USING btree (id)"
  }
]

[
  {
    "table_name": "message_usage",
    "trigger_name": "update_message_usage_updated_at",
    "action_timing": "BEFORE",
    "event_manipulation": "UPDATE",
    "action_statement": "EXECUTE FUNCTION update_updated_at_column()"
  },
  {
    "table_name": "subscribers",
    "trigger_name": "update_subscribers_updated_at",
    "action_timing": "BEFORE",
    "event_manipulation": "UPDATE",
    "action_statement": "EXECUTE FUNCTION update_updated_at_column()"
  }
]

[
  {
    "schema": "public",
    "proname": "array_to_halfvec",
    "args": "integer[], integer, boolean"
  },
  {
    "schema": "public",
    "proname": "array_to_halfvec",
    "args": "numeric[], integer, boolean"
  },
  {
    "schema": "public",
    "proname": "array_to_halfvec",
    "args": "double precision[], integer, boolean"
  },
  {
    "schema": "public",
    "proname": "array_to_halfvec",
    "args": "real[], integer, boolean"
  },
  {
    "schema": "public",
    "proname": "array_to_sparsevec",
    "args": "numeric[], integer, boolean"
  },
  {
    "schema": "public",
    "proname": "array_to_sparsevec",
    "args": "real[], integer, boolean"
  },
  {
    "schema": "public",
    "proname": "array_to_sparsevec",
    "args": "integer[], integer, boolean"
  },
  {
    "schema": "public",
    "proname": "array_to_sparsevec",
    "args": "double precision[], integer, boolean"
  },
  {
    "schema": "public",
    "proname": "array_to_vector",
    "args": "real[], integer, boolean"
  },
  {
    "schema": "public",
    "proname": "array_to_vector",
    "args": "double precision[], integer, boolean"
  },
  {
    "schema": "public",
    "proname": "array_to_vector",
    "args": "numeric[], integer, boolean"
  },
  {
    "schema": "public",
    "proname": "array_to_vector",
    "args": "integer[], integer, boolean"
  },
  {
    "schema": "public",
    "proname": "avg",
    "args": "vector"
  },
  {
    "schema": "public",
    "proname": "avg",
    "args": "halfvec"
  },
  {
    "schema": "public",
    "proname": "binary_quantize",
    "args": "halfvec"
  },
  {
    "schema": "public",
    "proname": "binary_quantize",
    "args": "vector"
  },
  {
    "schema": "public",
    "proname": "cosine_distance",
    "args": "halfvec, halfvec"
  },
  {
    "schema": "public",
    "proname": "cosine_distance",
    "args": "sparsevec, sparsevec"
  },
  {
    "schema": "public",
    "proname": "cosine_distance",
    "args": "vector, vector"
  },
  {
    "schema": "public",
    "proname": "halfvec",
    "args": "halfvec, integer, boolean"
  },
  {
    "schema": "public",
    "proname": "halfvec_accum",
    "args": "double precision[], halfvec"
  },
  {
    "schema": "public",
    "proname": "halfvec_add",
    "args": "halfvec, halfvec"
  },
  {
    "schema": "public",
    "proname": "halfvec_avg",
    "args": "double precision[]"
  },
  {
    "schema": "public",
    "proname": "halfvec_cmp",
    "args": "halfvec, halfvec"
  },
  {
    "schema": "public",
    "proname": "halfvec_combine",
    "args": "double precision[], double precision[]"
  },
  {
    "schema": "public",
    "proname": "halfvec_concat",
    "args": "halfvec, halfvec"
  },
  {
    "schema": "public",
    "proname": "halfvec_eq",
    "args": "halfvec, halfvec"
  },
  {
    "schema": "public",
    "proname": "halfvec_ge",
    "args": "halfvec, halfvec"
  },
  {
    "schema": "public",
    "proname": "halfvec_gt",
    "args": "halfvec, halfvec"
  },
  {
    "schema": "public",
    "proname": "halfvec_in",
    "args": "cstring, oid, integer"
  },
  {
    "schema": "public",
    "proname": "halfvec_l2_squared_distance",
    "args": "halfvec, halfvec"
  },
  {
    "schema": "public",
    "proname": "halfvec_le",
    "args": "halfvec, halfvec"
  },
  {
    "schema": "public",
    "proname": "halfvec_lt",
    "args": "halfvec, halfvec"
  },
  {
    "schema": "public",
    "proname": "halfvec_mul",
    "args": "halfvec, halfvec"
  },
  {
    "schema": "public",
    "proname": "halfvec_ne",
    "args": "halfvec, halfvec"
  },
  {
    "schema": "public",
    "proname": "halfvec_negative_inner_product",
    "args": "halfvec, halfvec"
  },
  {
    "schema": "public",
    "proname": "halfvec_out",
    "args": "halfvec"
  },
  {
    "schema": "public",
    "proname": "halfvec_recv",
    "args": "internal, oid, integer"
  },
  {
    "schema": "public",
    "proname": "halfvec_send",
    "args": "halfvec"
  },
  {
    "schema": "public",
    "proname": "halfvec_spherical_distance",
    "args": "halfvec, halfvec"
  },
  {
    "schema": "public",
    "proname": "halfvec_sub",
    "args": "halfvec, halfvec"
  },
  {
    "schema": "public",
    "proname": "halfvec_to_float4",
    "args": "halfvec, integer, boolean"
  },
  {
    "schema": "public",
    "proname": "halfvec_to_sparsevec",
    "args": "halfvec, integer, boolean"
  },
  {
    "schema": "public",
    "proname": "halfvec_to_vector",
    "args": "halfvec, integer, boolean"
  },
  {
    "schema": "public",
    "proname": "halfvec_typmod_in",
    "args": "cstring[]"
  },
  {
    "schema": "public",
    "proname": "hamming_distance",
    "args": "bit, bit"
  },
  {
    "schema": "public",
    "proname": "hnsw_bit_support",
    "args": "internal"
  },
  {
    "schema": "public",
    "proname": "hnsw_halfvec_support",
    "args": "internal"
  },
  {
    "schema": "public",
    "proname": "hnsw_sparsevec_support",
    "args": "internal"
  },
  {
    "schema": "public",
    "proname": "hnswhandler",
    "args": "internal"
  },
  {
    "schema": "public",
    "proname": "inner_product",
    "args": "vector, vector"
  },
  {
    "schema": "public",
    "proname": "inner_product",
    "args": "halfvec, halfvec"
  },
  {
    "schema": "public",
    "proname": "inner_product",
    "args": "sparsevec, sparsevec"
  },
  {
    "schema": "public",
    "proname": "insert_chunk_arr",
    "args": "p_doc uuid, p_text text, p_start integer, p_end integer, p_vec real[]"
  },
  {
    "schema": "public",
    "proname": "ivfflat_bit_support",
    "args": "internal"
  },
  {
    "schema": "public",
    "proname": "ivfflat_halfvec_support",
    "args": "internal"
  },
  {
    "schema": "public",
    "proname": "ivfflathandler",
    "args": "internal"
  },
  {
    "schema": "public",
    "proname": "jaccard_distance",
    "args": "bit, bit"
  },
  {
    "schema": "public",
    "proname": "l1_distance",
    "args": "vector, vector"
  },
  {
    "schema": "public",
    "proname": "l1_distance",
    "args": "sparsevec, sparsevec"
  },
  {
    "schema": "public",
    "proname": "l1_distance",
    "args": "halfvec, halfvec"
  },
  {
    "schema": "public",
    "proname": "l2_distance",
    "args": "sparsevec, sparsevec"
  },
  {
    "schema": "public",
    "proname": "l2_distance",
    "args": "halfvec, halfvec"
  },
  {
    "schema": "public",
    "proname": "l2_distance",
    "args": "vector, vector"
  },
  {
    "schema": "public",
    "proname": "l2_norm",
    "args": "sparsevec"
  },
  {
    "schema": "public",
    "proname": "l2_norm",
    "args": "halfvec"
  },
  {
    "schema": "public",
    "proname": "l2_normalize",
    "args": "halfvec"
  },
  {
    "schema": "public",
    "proname": "l2_normalize",
    "args": "sparsevec"
  },
  {
    "schema": "public",
    "proname": "l2_normalize",
    "args": "vector"
  },
  {
    "schema": "public",
    "proname": "search_project_chunks_arr",
    "args": "p_project uuid, q real[], k integer"
  },
  {
    "schema": "public",
    "proname": "sparsevec",
    "args": "sparsevec, integer, boolean"
  },
  {
    "schema": "public",
    "proname": "sparsevec_cmp",
    "args": "sparsevec, sparsevec"
  },
  {
    "schema": "public",
    "proname": "sparsevec_eq",
    "args": "sparsevec, sparsevec"
  },
  {
    "schema": "public",
    "proname": "sparsevec_ge",
    "args": "sparsevec, sparsevec"
  },
  {
    "schema": "public",
    "proname": "sparsevec_gt",
    "args": "sparsevec, sparsevec"
  },
  {
    "schema": "public",
    "proname": "sparsevec_in",
    "args": "cstring, oid, integer"
  },
  {
    "schema": "public",
    "proname": "sparsevec_l2_squared_distance",
    "args": "sparsevec, sparsevec"
  },
  {
    "schema": "public",
    "proname": "sparsevec_le",
    "args": "sparsevec, sparsevec"
  },
  {
    "schema": "public",
    "proname": "sparsevec_lt",
    "args": "sparsevec, sparsevec"
  },
  {
    "schema": "public",
    "proname": "sparsevec_ne",
    "args": "sparsevec, sparsevec"
  },
  {
    "schema": "public",
    "proname": "sparsevec_negative_inner_product",
    "args": "sparsevec, sparsevec"
  },
  {
    "schema": "public",
    "proname": "sparsevec_out",
    "args": "sparsevec"
  },
  {
    "schema": "public",
    "proname": "sparsevec_recv",
    "args": "internal, oid, integer"
  },
  {
    "schema": "public",
    "proname": "sparsevec_send",
    "args": "sparsevec"
  },
  {
    "schema": "public",
    "proname": "sparsevec_to_halfvec",
    "args": "sparsevec, integer, boolean"
  },
  {
    "schema": "public",
    "proname": "sparsevec_to_vector",
    "args": "sparsevec, integer, boolean"
  },
  {
    "schema": "public",
    "proname": "sparsevec_typmod_in",
    "args": "cstring[]"
  },
  {
    "schema": "public",
    "proname": "subvector",
    "args": "vector, integer, integer"
  },
  {
    "schema": "public",
    "proname": "subvector",
    "args": "halfvec, integer, integer"
  },
  {
    "schema": "public",
    "proname": "sum",
    "args": "halfvec"
  },
  {
    "schema": "public",
    "proname": "sum",
    "args": "vector"
  },
  {
    "schema": "public",
    "proname": "update_updated_at_column",
    "args": ""
  },
  {
    "schema": "public",
    "proname": "vector",
    "args": "vector, integer, boolean"
  },
  {
    "schema": "public",
    "proname": "vector_accum",
    "args": "double precision[], vector"
  },
  {
    "schema": "public",
    "proname": "vector_add",
    "args": "vector, vector"
  },
  {
    "schema": "public",
    "proname": "vector_avg",
    "args": "double precision[]"
  },
  {
    "schema": "public",
    "proname": "vector_cmp",
    "args": "vector, vector"
  },
  {
    "schema": "public",
    "proname": "vector_combine",
    "args": "double precision[], double precision[]"
  },
  {
    "schema": "public",
    "proname": "vector_concat",
    "args": "vector, vector"
  },
  {
    "schema": "public",
    "proname": "vector_dims",
    "args": "vector"
  },
  {
    "schema": "public",
    "proname": "vector_dims",
    "args": "halfvec"
  },
  {
    "schema": "public",
    "proname": "vector_eq",
    "args": "vector, vector"
  },
  {
    "schema": "public",
    "proname": "vector_ge",
    "args": "vector, vector"
  },
  {
    "schema": "public",
    "proname": "vector_gt",
    "args": "vector, vector"
  },
  {
    "schema": "public",
    "proname": "vector_in",
    "args": "cstring, oid, integer"
  },
  {
    "schema": "public",
    "proname": "vector_l2_squared_distance",
    "args": "vector, vector"
  },
  {
    "schema": "public",
    "proname": "vector_le",
    "args": "vector, vector"
  },
  {
    "schema": "public",
    "proname": "vector_lt",
    "args": "vector, vector"
  },
  {
    "schema": "public",
    "proname": "vector_mul",
    "args": "vector, vector"
  },
  {
    "schema": "public",
    "proname": "vector_ne",
    "args": "vector, vector"
  },
  {
    "schema": "public",
    "proname": "vector_negative_inner_product",
    "args": "vector, vector"
  },
  {
    "schema": "public",
    "proname": "vector_norm",
    "args": "vector"
  },
  {
    "schema": "public",
    "proname": "vector_out",
    "args": "vector"
  },
  {
    "schema": "public",
    "proname": "vector_recv",
    "args": "internal, oid, integer"
  },
  {
    "schema": "public",
    "proname": "vector_send",
    "args": "vector"
  },
  {
    "schema": "public",
    "proname": "vector_spherical_distance",
    "args": "vector, vector"
  },
  {
    "schema": "public",
    "proname": "vector_sub",
    "args": "vector, vector"
  },
  {
    "schema": "public",
    "proname": "vector_to_float4",
    "args": "vector, integer, boolean"
  },
  {
    "schema": "public",
    "proname": "vector_to_halfvec",
    "args": "vector, integer, boolean"
  },
  {
    "schema": "public",
    "proname": "vector_to_sparsevec",
    "args": "vector, integer, boolean"
  },
  {
    "schema": "public",
    "proname": "vector_typmod_in",
    "args": "cstring[]"
  }
]

[
  {
    "table_name": "active_plan",
    "view_definition": " SELECT s.user_id,\n    p.id AS plan_id,\n    p.monthly_quota\n   FROM (subscriptions s\n     JOIN plans p ON ((p.id = s.plan_id)))\n  WHERE ((s.status = 'active'::text) AND ((now() >= COALESCE(s.current_period_start, now())) AND (now() <= COALESCE(s.current_period_end, now()))));"
  },
  {
    "table_name": "my_orgs",
    "view_definition": " SELECT org_id\n   FROM members m\n  WHERE (user_id = auth.uid());"
  },
  {
    "table_name": "usage_counters",
    "view_definition": " SELECT user_id,\n    kind,\n    date_trunc('month'::text, occurred_at) AS month,\n    (sum(amount))::integer AS used\n   FROM usage_events\n  GROUP BY user_id, kind, (date_trunc('month'::text, occurred_at));"
  }
]

[
  {
    "schemaname": "public",
    "tablename": "chunks",
    "tableowner": "postgres"
  },
  {
    "schemaname": "public",
    "tablename": "documents",
    "tableowner": "postgres"
  },
  {
    "schemaname": "public",
    "tablename": "evidence",
    "tableowner": "postgres"
  },
  {
    "schemaname": "public",
    "tablename": "members",
    "tableowner": "postgres"
  },
  {
    "schemaname": "public",
    "tablename": "message_usage",
    "tableowner": "postgres"
  },
  {
    "schemaname": "public",
    "tablename": "metrics",
    "tableowner": "postgres"
  },
  {
    "schemaname": "public",
    "tablename": "orgs",
    "tableowner": "postgres"
  },
  {
    "schemaname": "public",
    "tablename": "plans",
    "tableowner": "postgres"
  },
  {
    "schemaname": "public",
    "tablename": "projects",
    "tableowner": "postgres"
  },
  {
    "schemaname": "public",
    "tablename": "runs",
    "tableowner": "postgres"
  },
  {
    "schemaname": "public",
    "tablename": "subscribers",
    "tableowner": "postgres"
  },
  {
    "schemaname": "public",
    "tablename": "subscriptions",
    "tableowner": "postgres"
  },
  {
    "schemaname": "public",
    "tablename": "usage_events",
    "tableowner": "postgres"
  }
]