CREATE TABLE "public"."alembic_version" (
  "version_num" character varying(32) NOT NULL,
  CONSTRAINT "alembic_version_pkc" PRIMARY KEY (version_num)
);

CREATE TABLE "public"."cell" (
  "id"         uuid                        NOT NULL,
  "value"      double precision            NOT NULL,
  "created_at" timestamp without time zone NOT NULL DEFAULT now(),
  "updated_at" timestamp without time zone NOT NULL DEFAULT now(),
  "sheet_id"   uuid                        NOT NULL,
  CONSTRAINT "cell_pkey" PRIMARY KEY (id)
);

CREATE TABLE "public"."groups" (
  "id"          uuid                        NOT NULL,
  "name"        character varying(50)       NOT NULL,
  "description" character varying(200),
  "created_at"  timestamp without time zone NOT NULL DEFAULT now(),
  "user_id"     uuid                        NOT NULL,
  CONSTRAINT "groups_pkey" PRIMARY KEY (id)
);

CREATE TABLE "public"."sheet" (
  "id"         uuid                        NOT NULL,
  "name"       character varying(50)       NOT NULL,
  "created_at" timestamp without time zone NOT NULL DEFAULT now(),
  "group_id"   uuid                        NOT NULL,
  CONSTRAINT "sheet_pkey" PRIMARY KEY (id)
);

CREATE TABLE "public"."users" (
  "id"       uuid                   NOT NULL,
  "username" character varying(50)  NOT NULL,
  "email"    character varying(100) NOT NULL,
  "password" character varying(100) NOT NULL,
  CONSTRAINT "users_email_key" UNIQUE (email),
  CONSTRAINT "users_pkey" PRIMARY KEY (id)
);

ALTER TABLE "public"."sheet"
  ADD CONSTRAINT "sheet_group_id_fkey" FOREIGN KEY (group_id) REFERENCES public.groups(id);

ALTER TABLE "public"."cell"
  ADD CONSTRAINT "cell_sheet_id_fkey" FOREIGN KEY (sheet_id) REFERENCES public.sheet(id);

ALTER TABLE "public"."groups"
  ADD CONSTRAINT "groups_user_id_fkey" FOREIGN KEY (user_id) REFERENCES public.users(id);

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."alembic_version" TO "anon", "authenticated";

REVOKE ALL ON TABLE "public"."alembic_version" FROM "postgres";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."alembic_version" TO "postgres";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."alembic_version" TO "service_role";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."cell" TO "anon", "authenticated";

REVOKE ALL ON TABLE "public"."cell" FROM "postgres";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."cell" TO "postgres";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."cell" TO "service_role";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."groups" TO "anon", "authenticated";

REVOKE ALL ON TABLE "public"."groups" FROM "postgres";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."groups" TO "postgres";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."groups" TO "service_role";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."sheet" TO "anon", "authenticated";

REVOKE ALL ON TABLE "public"."sheet" FROM "postgres";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."sheet" TO "postgres";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."sheet" TO "service_role";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."users" TO "anon", "authenticated";

REVOKE ALL ON TABLE "public"."users" FROM "postgres";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."users" TO "postgres";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."users" TO "service_role";

