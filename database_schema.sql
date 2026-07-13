-- Tameike Sentinel PostgreSQL/PostGIS schema (PoC v0.9)
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TYPE quality_flag AS ENUM ('verified','estimated','incomplete','invalid');
CREATE TYPE alert_level AS ENUM ('normal','info','attention','warning','emergency');

CREATE TABLE organization (
  organization_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  organization_type text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE pond (
  pond_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  source_system text NOT NULL,
  source_record_id text,
  name text NOT NULL,
  former_names text[],
  prefecture_code char(2),
  municipality_code char(5),
  address text,
  location geometry(Point, 4326) NOT NULL,
  coordinate_method text,
  coordinate_accuracy_m numeric,
  status text NOT NULL DEFAULT 'active',
  owner_organization_id uuid REFERENCES organization,
  manager_organization_id uuid REFERENCES organization,
  disaster_priority boolean,
  constructed_year integer,
  dam_height_m numeric,
  crest_length_m numeric,
  total_storage_thousand_m3 numeric,
  full_water_area_km2 numeric,
  quality quality_flag NOT NULL DEFAULT 'incomplete',
  confidence numeric CHECK (confidence BETWEEN 0 AND 1),
  source_payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  valid_from timestamptz,
  valid_to timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX pond_location_gix ON pond USING gist(location);
CREATE INDEX pond_municipality_idx ON pond(municipality_code);

CREATE TABLE pond_geometry (
  geometry_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  pond_id uuid NOT NULL REFERENCES pond ON DELETE CASCADE,
  geometry_type text NOT NULL,
  geom geometry(Geometry, 6677) NOT NULL,
  observed_at timestamptz,
  source text NOT NULL,
  quality quality_flag NOT NULL,
  confidence numeric CHECK (confidence BETWEEN 0 AND 1),
  version integer NOT NULL DEFAULT 1,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX pond_geometry_gix ON pond_geometry USING gist(geom);

CREATE TABLE inspection (
  inspection_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  pond_id uuid NOT NULL REFERENCES pond ON DELETE CASCADE,
  inspection_type text NOT NULL,
  inspected_at timestamptz NOT NULL,
  inspector_organization_id uuid REFERENCES organization,
  weather text,
  water_level_m numeric,
  overall_rating text,
  emergency_action_required boolean,
  source_document_uri text,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE defect (
  defect_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  inspection_id uuid NOT NULL REFERENCES inspection ON DELETE CASCADE,
  component text NOT NULL,
  defect_type text NOT NULL,
  position geometry(PointZ, 6677),
  severity text,
  progression text,
  length_m numeric,
  width_m numeric,
  depth_m numeric,
  evidence_uri text,
  confirmed_by text,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE sensor (
  sensor_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  pond_id uuid NOT NULL REFERENCES pond ON DELETE CASCADE,
  sensor_type text NOT NULL,
  location geometry(Point, 4326),
  unit text,
  sampling_interval_seconds integer,
  installed_at timestamptz,
  calibration_at timestamptz,
  status text NOT NULL DEFAULT 'active'
);

CREATE TABLE observation (
  sensor_id uuid NOT NULL REFERENCES sensor ON DELETE CASCADE,
  observed_at timestamptz NOT NULL,
  value numeric,
  quality quality_flag NOT NULL DEFAULT 'verified',
  battery_percent numeric,
  communication_status text,
  raw_payload jsonb,
  ingested_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY(sensor_id, observed_at)
);
CREATE INDEX observation_time_idx ON observation(observed_at DESC);

CREATE TABLE satellite_asset (
  asset_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  provider text NOT NULL,
  platform text NOT NULL,
  sensor text NOT NULL,
  scene_id text NOT NULL,
  acquired_at timestamptz NOT NULL,
  footprint geometry(Polygon,4326),
  orbit_direction text,
  relative_orbit integer,
  incidence_angle numeric,
  cloud_cover numeric,
  processing_level text,
  uri text NOT NULL,
  checksum text,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE(provider, scene_id)
);
CREATE INDEX satellite_footprint_gix ON satellite_asset USING gist(footprint);

CREATE TABLE analysis_run (
  analysis_run_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  analysis_type text NOT NULL,
  pond_id uuid REFERENCES pond,
  event_id uuid,
  input_manifest jsonb NOT NULL,
  model_name text NOT NULL,
  model_version text NOT NULL,
  code_version text NOT NULL,
  status text NOT NULL,
  started_at timestamptz,
  finished_at timestamptz,
  output_uri text,
  metrics jsonb,
  error_message text,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE simulation_run (
  simulation_run_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  pond_id uuid NOT NULL REFERENCES pond,
  mode text NOT NULL CHECK (mode IN ('surrogate','detailed')),
  simulator_name text NOT NULL,
  simulator_version text NOT NULL,
  input_parameters jsonb NOT NULL,
  input_hash text NOT NULL,
  status text NOT NULL,
  result_summary jsonb,
  result_uri text,
  started_at timestamptz,
  finished_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE risk_assessment (
  risk_assessment_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  pond_id uuid NOT NULL REFERENCES pond,
  assessed_at timestamptz NOT NULL,
  hazard_score numeric,
  vulnerability_score numeric,
  exposure_score numeric,
  anomaly_score numeric,
  uncertainty_score numeric,
  overall_level alert_level NOT NULL,
  evidence jsonb NOT NULL,
  model_version text,
  expires_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX risk_latest_idx ON risk_assessment(pond_id, assessed_at DESC);

CREATE TABLE alert (
  alert_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  pond_id uuid NOT NULL REFERENCES pond,
  risk_assessment_id uuid REFERENCES risk_assessment,
  level alert_level NOT NULL,
  title text NOT NULL,
  message text NOT NULL,
  status text NOT NULL DEFAULT 'proposed',
  proposed_at timestamptz NOT NULL DEFAULT now(),
  approved_at timestamptz,
  approved_by uuid,
  decision_comment text
);

CREATE TABLE report (
  report_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  report_type text NOT NULL,
  event_id uuid,
  status text NOT NULL DEFAULT 'draft',
  content_uri text NOT NULL,
  evidence_manifest jsonb NOT NULL,
  generated_model text,
  generated_at timestamptz,
  approved_at timestamptz,
  approved_by uuid,
  created_at timestamptz NOT NULL DEFAULT now()
);
