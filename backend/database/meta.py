from sqlalchemy import func
from sqlalchemy import Sequence
from sqlalchemy.event import listen
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import DDL
from sqlalchemy.schema import MetaData

# Recommended naming convention used by Alembic, as various different database
# providers will autogenerate vastly different names making migrations more
# difficult. See: http://alembic.zzzcomputing.com/en/latest/naming.html
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)
Base = declarative_base(metadata=metadata)


# Create a skip32 PL/PGSQL function that reorders a sequence,
# maintaining unicity while making it difficult for external users to
# enumerate objects.
# Each table that uses this should use its own key so that
# IDs throughout the database are not very likely to overlap.
# See:
# https://wiki.postgresql.org/wiki/Pseudo_encrypt
# https://wiki.postgresql.org/wiki/Skip32
# http://stackoverflow.com/questions/33760630
# https://dba.stackexchange.com/questions/22512/

func_defs = """
CREATE OR REPLACE FUNCTION skip32(val int4, cr_key bytea, encrypt bool)
RETURNS int4
AS $$
DECLARE
  kstep int;
  k int;
  wl int4;
  wr int4;
  g1 int4;
  g2 int4;
  g3 int4;
  g4 int4;
  g5 int4;
  g6 int4;
  ftable bytea :=
    '\xa3d70983f848f6f4b321157899b1aff9e72d4d8ace4cca2e5295d91e4e3844280adf02a017f1606812b77ac3e9fa3d5396846bbaf2639a197caee5f5f7166aa239b67b0fc193811beeb41aead0912fb855b9da853f41bfe05a58805f660bd89035d5c0a733066569450094566d989b7697fcb2c2b0fedb20e1ebd6e4dd474a1d42ed9e6e493ccd4327d207d4dec7671889cb301f8dc68faac874dcc95d5c31a47088612c9f0d2b8750825464267d0340344b1c73d1c4fd3bccfb7fabe63e5ba5ad04239c145122f02979717eff8c0ee20cefbc72756f37a1ecd38e628b8610e8087711be924f24c532369dcff3a6bbac5e6ca9135725b5e3bda83a0105592a46';
BEGIN
  IF (octet_length(cr_key)!=10) THEN
    RAISE EXCEPTION 'The encryption key must be exactly 10 bytes long.';
  END IF;

  IF (encrypt) THEN
    kstep := 1;
    k := 0;
  ELSE
    kstep := -1;
    k := 23;
  END IF;

  wl := (val & -65536) >> 16;
  wr := val & 65535;

  FOR i IN 0..11 LOOP
    g1 := (wl>>8) & 255;
    g2 := wl & 255;
    g3 := get_byte(ftable, g2 # get_byte(cr_key, (4*k)%10)) # g1;
    g4 := get_byte(ftable, g3 # get_byte(cr_key, (4*k+1)%10)) # g2;
    g5 := get_byte(ftable, g4 # get_byte(cr_key, (4*k+2)%10)) # g3;
    g6 := get_byte(ftable, g5 # get_byte(cr_key, (4*k+3)%10)) # g4;
    wr := wr # (((g5<<8) + g6) # k);
    k := k + kstep;

    g1 := (wr>>8) & 255;
    g2 := wr & 255;
    g3 := get_byte(ftable, g2 # get_byte(cr_key, (4*k)%10)) # g1;
    g4 := get_byte(ftable, g3 # get_byte(cr_key, (4*k+1)%10)) # g2;
    g5 := get_byte(ftable, g4 # get_byte(cr_key, (4*k+2)%10)) # g3;
    g6 := get_byte(ftable, g5 # get_byte(cr_key, (4*k+3)%10)) # g4;
    wl := wl # (((g5<<8) + g6) # k);
    k := k + kstep;
  END LOOP;

  RETURN (wr << 16) | (wl & 65535);

END
$$ immutable strict language plpgsql;


CREATE OR REPLACE FUNCTION random_bytea(p_length in integer)
RETURNS bytea
AS $$
DECLARE
  o bytea := '';
BEGIN
  FOR i IN 1..p_length LOOP
    o := o || decode(
      lpad(to_hex(width_bucket(random(), 0, 1, 256) - 1), 2, '0'), 'hex');
  END LOOP;
  RETURN o;
END
$$ language plpgsql;


CREATE OR REPLACE FUNCTION skip32_hex_seq(val int8, sn character varying)
    returns character varying
AS $$
DECLARE
  ki int8;
  cr_key bytea;
  prefix character varying;
  encrypted int4;
BEGIN
  ki = val >> 31;
  SELECT skip32_key INTO cr_key
    FROM sequence_key
    WHERE seq_name = sn
      AND key_index <= ki
    ORDER BY key_index DESC
    LIMIT 1;
  IF NOT FOUND THEN
    -- Generate and store the needed sequence_key now.
    cr_key = random_bytea(10);
    INSERT INTO sequence_key (seq_name, key_index, skip32_key)
    VALUES (sn, 0, cr_key);
  END IF;
  IF (ki = 0) THEN
    prefix = '';
  ELSE
    prefix = to_hex(ki);
  END IF;
  encrypted = skip32((val & 2147483647)::int4, cr_key, true);
  RETURN prefix || lpad(to_hex(encrypted), 8, '0');
END
$$ language plpgsql;
"""


listen(metadata, 'before_create', DDL(func_defs.replace('%', '%%')))

all_seq_names = set()


def string_sequencer(seq_name):
    all_seq_names.add(seq_name)
    # Use a large increment to ensure fewer than
    # one in a million guessed IDs are valid.
    seq = Sequence(seq_name, metadata=metadata, increment=1047311)
    return func.skip32_hex_seq(seq.next_value(), seq_name)
