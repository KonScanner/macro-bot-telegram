create schema if not exists core;

CREATE TABLE core.macro_events (
    hash text not NULL,
    event text,
    importance text,
    timestamp text,
    flag text,
    previous text,
    forecast text,
    actual text,
    process_time TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (hash)
);

ALTER TABLE
    core.macro_events
ALTER COLUMN
    process_time TYPE TIMESTAMP WITH TIME ZONE USING process_time AT TIME ZONE 'UTC';

-- B-trees (defualt)
CREATE INDEX ON core.macro_events (flag);

CREATE INDEX ON core.macro_events (event)
where
    event is not NULL;

create index on core.macro_events(process_time);